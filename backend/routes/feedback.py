"""
Reviews and support messages, the only things students can send us.

What gets stored: exactly what the person typed (trimmed, length-limited)
plus a timestamp and a status. No accounts, cookies, IP addresses or user
agents. Reviews start "pending" and only show on the site once the owner
approves them.

Everything lives in its own SQLite file (FEEDBACK_DB_PATH, default next to
the analytics file). Put it on the same persistent disk as ANALYTICS_DB_PATH,
or reviews and messages are lost on every deploy.

Spam: a honeypot field that people never see (must stay empty) and a minimum
time on the page (elapsed_ms). A bot gets the normal 201 answer and nothing
is stored. Rate limits are kept in memory, keyed on a random id the browser
makes up (not the IP): 3 sends per 10 minutes per browser, 60 per hour overall.
Only sends that pass the checks count, so fixing a typo doesn't use one up.

Admin (same token as /api/admin/stats, in the Authorization header):
  GET  /api/admin/feedback?status=pending|approved|hidden|new|done
  POST /api/admin/reviews/<id>   {"status": "approved" | "hidden" | "pending"}
  POST /api/admin/support/<id>   {"status": "done" | "new"}
"""

import collections
import json
import os
import random
import re
import sqlite3
import threading
import time

from flask import Blueprint, current_app, jsonify, request

from backend.routes import analytics

feedback_bp = Blueprint("feedback", __name__)

MAX_BODY_BYTES = 8 * 1024
MIN_FILL_MS = 1500
COMMENT_MAX = 600
NAME_MAX = 30
MESSAGE_MIN, MESSAGE_MAX = 10, 2000
COURSE_MAX, SECTION_MAX = 20, 10
EMAIL_MAX = 120
DEFAULT_NAME = "A student"
SUPPORT_KINDS = ("broken", "wrong_info", "missing_class", "idea", "other")
REVIEW_STATUSES = ("pending", "approved", "hidden")
SUPPORT_STATUSES = ("new", "done")
ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{8,64}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
LINK_PATTERN = re.compile(r"http|www\.", re.IGNORECASE)
CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b-\x1f\x7f]")   # keeps \t and \n

PER_VISITOR = (3, 10 * 60)   # 3 sends per 10 minutes per browser
OVERALL = (60, 60 * 60)      # 60 sends per hour in total
TOO_MANY = "You've sent a few already. Please try again in a few minutes."

SCHEMA = """
CREATE TABLE IF NOT EXISTS reviews (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at   TEXT NOT NULL,                  -- UTC, 'YYYY-MM-DD HH:MM:SS'
    rating       INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment      TEXT NOT NULL DEFAULT '',
    display_name TEXT NOT NULL DEFAULT '',       -- '' shows as "A student"
    status       TEXT NOT NULL DEFAULT 'pending' -- pending | approved | hidden
);
CREATE TABLE IF NOT EXISTS support_messages (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    kind       TEXT NOT NULL,
    message    TEXT NOT NULL,
    course     TEXT NOT NULL DEFAULT '',
    section    TEXT NOT NULL DEFAULT '',
    email      TEXT NOT NULL DEFAULT '',
    status     TEXT NOT NULL DEFAULT 'new'       -- new | done
);
CREATE INDEX IF NOT EXISTS idx_reviews_status ON reviews(status, id);
CREATE INDEX IF NOT EXISTS idx_support_status ON support_messages(status, id);
"""


def db_path():
    return os.environ.get("FEEDBACK_DB_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(analytics.db_path())), "feedback.db")


def get_connection():
    path = db_path()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(SCHEMA)
    return conn


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())


def error(message, status=400):
    return jsonify({"ok": False, "error": message}), status


# ---------- rate limiting ----------

_lock = threading.Lock()
_sent = {"all": collections.deque(), "by_visitor": collections.defaultdict(collections.deque)}


def reset_rate_limits():
    """For the tests."""
    with _lock:
        _sent["all"].clear()
        _sent["by_visitor"].clear()


def within_rate_limit(visitor_id):
    t = time.time()
    with _lock:
        everyone, mine = _sent["all"], _sent["by_visitor"][visitor_id]
        for queue, window in ((everyone, OVERALL[1]), (mine, PER_VISITOR[1])):
            while queue and queue[0] <= t - window:
                queue.popleft()
        if len(everyone) >= OVERALL[0] or len(mine) >= PER_VISITOR[0]:
            return False
        everyone.append(t)
        mine.append(t)
        return True


# ---------- reading and cleaning the body ----------

class BadRequest(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def read_body():
    if (request.content_length or 0) > MAX_BODY_BYTES:
        raise BadRequest("That's too long to send.", 413)
    if not request.is_json:
        raise BadRequest("Send the form as JSON.")
    raw = request.stream.read(MAX_BODY_BYTES + 1)
    if len(raw) > MAX_BODY_BYTES:
        raise BadRequest("That's too long to send.", 413)
    try:
        body = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        raise BadRequest("Send the form as JSON.")
    if not isinstance(body, dict):
        raise BadRequest("Send the form as JSON.")
    return body


def text(body, key, limit, label):
    """A trimmed string without control characters (newlines kept), at most limit characters."""
    value = body.get(key, "")
    if value is None:
        value = ""
    if not isinstance(value, str):
        raise BadRequest(f"{label} must be text.")
    value = CONTROL_CHARS.sub("", value.replace("\r\n", "\n").replace("\r", "\n")).strip()
    if len(value) > limit:
        raise BadRequest(f"{label} can be at most {limit} characters.")
    return value


def looks_like_a_bot(body):
    """Honeypot filled in, or the form was sent faster than a person could."""
    if body.get("website"):
        return True
    elapsed = body.get("elapsed_ms")
    return not isinstance(elapsed, (int, float)) or isinstance(elapsed, bool) or elapsed < MIN_FILL_MS


def visitor(body):
    value = body.get("visitor_id")
    return value if isinstance(value, str) and ID_PATTERN.match(value) else "unknown"


def save(sql, params):
    try:
        conn = get_connection()
        cur = conn.execute(sql, params)
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id
    except (sqlite3.Error, OSError):
        current_app.logger.exception("could not save feedback to %s", db_path())   # never the text itself
        return None


# ---------- reviews ----------

@feedback_bp.route("/api/reviews", methods=["GET"])
def list_reviews():
    """{"average": 4.6, "count": 12, "reviews": [{rating, comment, name, date}]}, approved only, newest first."""
    try:
        limit = min(max(int(request.args.get("limit", 20)), 1), 50)
        offset = max(int(request.args.get("offset", 0)), 0)
    except ValueError:
        return error("limit and offset must be whole numbers")
    conn = get_connection()
    summary = conn.execute("SELECT COUNT(*), AVG(rating) FROM reviews WHERE status = 'approved'").fetchone()
    rows = conn.execute("""SELECT rating, comment, display_name, created_at FROM reviews WHERE status = 'approved'
                           ORDER BY id DESC LIMIT ? OFFSET ?""", (limit, offset)).fetchall()
    conn.close()
    response = jsonify({
        "average": round(summary[1], 1) if summary[0] else None,
        "count": summary[0],
        "reviews": [{"rating": r["rating"], "comment": r["comment"], "name": r["display_name"] or DEFAULT_NAME,
                     "date": r["created_at"][:10]} for r in rows],
    })
    response.headers["Cache-Control"] = "no-store"
    return response


@feedback_bp.route("/api/reviews", methods=["POST"])
def add_review():
    """{"rating": 1-5, "comment": "...", "name": "...", "website": "", "elapsed_ms": 9000, "visitor_id": "..."}"""
    try:
        body = read_body()
        if looks_like_a_bot(body):
            return jsonify({"ok": True, "status": "pending"}), 201
        rating = body.get("rating")
        if not isinstance(rating, int) or isinstance(rating, bool) or not 1 <= rating <= 5:
            raise BadRequest("Pick a rating from 1 to 5 stars.")
        comment = text(body, "comment", COMMENT_MAX, "Your comment")
        if LINK_PATTERN.search(comment):
            raise BadRequest("Please leave links out of your review.")
        name = text(body, "name", NAME_MAX, "Your name")
    except BadRequest as e:
        return error(str(e), e.status)
    if not within_rate_limit(visitor(body)):   # only sends that would be saved count
        return error(TOO_MANY, 429)
    if save("INSERT INTO reviews (created_at, rating, comment, display_name, status) VALUES (?, ?, ?, ?, 'pending')",
            (now(), rating, comment, name)) is None:
        return error("Could not save your review right now. Please try again later.", 503)
    return jsonify({"ok": True, "status": "pending"}), 201


# ---------- support ----------

@feedback_bp.route("/api/support", methods=["POST"])
def add_support_message():
    """{"kind": "wrong_info", "message": "...", "course": "SOC 101", "section": "5", "email": "", ...} -> {"ref": "S-123"}"""
    try:
        body = read_body()
        if looks_like_a_bot(body):
            return jsonify({"ok": True, "ref": f"S-{random.randint(100, 999)}"}), 201
        kind = body.get("kind")
        if kind not in SUPPORT_KINDS:
            raise BadRequest("Pick what kind of problem it is.")
        message = text(body, "message", MESSAGE_MAX, "Your message")
        if len(message) < MESSAGE_MIN:
            raise BadRequest(f"Please tell us a bit more (at least {MESSAGE_MIN} characters).")
        course = text(body, "course", COURSE_MAX, "Course")
        section = text(body, "section", SECTION_MAX, "Section")
        email = text(body, "email", EMAIL_MAX, "Email")
        if email and not EMAIL_PATTERN.match(email):
            raise BadRequest("That email doesn't look right. You can also leave it empty.")
    except BadRequest as e:
        return error(str(e), e.status)
    if not within_rate_limit(visitor(body)):
        return error(TOO_MANY, 429)
    new_id = save("""INSERT INTO support_messages (created_at, kind, message, course, section, email, status)
                     VALUES (?, ?, ?, ?, ?, ?, 'new')""", (now(), kind, message, course, section, email))
    if new_id is None:
        return error("Could not send your message right now. Please try again later.", 503)
    return jsonify({"ok": True, "ref": f"S-{new_id}"}), 201


# ---------- admin ----------

def admin_check():
    """None when the request may go on, otherwise the response to send."""
    if not os.environ.get("ADMIN_TOKEN"):
        return jsonify({"error": "not found"}), 404
    if not analytics.authorized():
        return jsonify({"error": "unauthorized"}), 401
    return None


@feedback_bp.route("/api/admin/feedback", methods=["GET"])
def admin_feedback():
    """
    Reviews and support messages to look at, newest first (at most 200 of each).
      curl -H "Authorization: Bearer $ADMIN_TOKEN" "https://<site>/api/admin/feedback?status=pending"
    ?status=pending|approved|hidden picks reviews, new|done picks messages; none = both, every status.
    """
    denied = admin_check()
    if denied:
        return denied
    status = request.args.get("status", "")
    if status and status not in REVIEW_STATUSES + SUPPORT_STATUSES:
        return jsonify({"error": "status must be one of " + ", ".join(REVIEW_STATUSES + SUPPORT_STATUSES)}), 400
    conn = get_connection()
    result = {}
    if not status or status in REVIEW_STATUSES:
        where = "WHERE status = ?" if status else ""
        result["reviews"] = [dict(r) for r in conn.execute(
            f"SELECT * FROM reviews {where} ORDER BY id DESC LIMIT 200", (status,) if status else ()).fetchall()]
    if not status or status in SUPPORT_STATUSES:
        where = "WHERE status = ?" if status else ""
        result["support"] = [dict(r) for r in conn.execute(
            f"SELECT * FROM support_messages {where} ORDER BY id DESC LIMIT 200", (status,) if status else ()).fetchall()]
    conn.close()
    response = jsonify(result)
    response.headers["Cache-Control"] = "no-store"
    return response


def set_status(table, item_id, allowed):
    denied = admin_check()
    if denied:
        return denied
    body = request.get_json(silent=True)
    status = body.get("status") if isinstance(body, dict) else None
    if status not in allowed:
        return jsonify({"error": "status must be one of " + ", ".join(allowed)}), 400
    conn = get_connection()
    changed = conn.execute(f"UPDATE {table} SET status = ? WHERE id = ?", (status, item_id)).rowcount
    conn.commit()
    conn.close()
    if not changed:
        return jsonify({"error": "not found"}), 404
    return jsonify({"ok": True, "id": item_id, "status": status})


@feedback_bp.route("/api/admin/reviews/<int:review_id>", methods=["POST"])
def admin_review(review_id):
    """curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json"
            -d '{"status":"approved"}' https://<site>/api/admin/reviews/12"""
    return set_status("reviews", review_id, REVIEW_STATUSES)


@feedback_bp.route("/api/admin/support/<int:message_id>", methods=["POST"])
def admin_support(message_id):
    """curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json"
            -d '{"status":"done"}' https://<site>/api/admin/support/7"""
    return set_status("support_messages", message_id, SUPPORT_STATUSES)

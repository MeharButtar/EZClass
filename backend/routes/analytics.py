"""
Anonymous visit counting, so we can tell how many people use the site.

What gets stored per event: a timestamp, the event name, a random visitor id
and session id made up by the browser (frontend/js/track.js), "mobile" or
"desktop", and a few whitelisted details like which view or GE areas were
picked. No names, emails, IP addresses, cookies, full user agents, or anything
typed into the professor/keyword boxes.

Events go into their own SQLite file (ANALYTICS_DB_PATH), not the class
database, because the class database is rebuilt from CSVs and is read-only in
production. Put ANALYTICS_DB_PATH on a persistent disk or the counts reset on
every deploy (Render's free plan has no disk, so there they always reset).

Settings (read on every request, so they can change without a code change):
  ANALYTICS_ENABLED=0  -> /api/event accepts and drops everything
  ADMIN_TOKEN          -> required to read /api/admin/stats (unset = stats off)
"""

import datetime
import hmac
import json
import os
import re
import sqlite3
import threading
import time

from flask import Blueprint, current_app, jsonify, request

analytics_bp = Blueprint("analytics", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "backend", "sql", "analytics.db")

ALLOWED_EVENTS = {"page_view", "search", "ge_search", "cart_add", "cart_remove", "cart_clear", "conflict_check"}
ALLOWED_PROPS = ("view", "subject", "day", "areas", "results", "has_prof", "has_kw", "cart_size", "conflict_free")
ID_PATTERN = re.compile(r"^[A-Za-z0-9-]{8,64}$")
MAX_BODY_BYTES = 2048
MAX_PROP_CHARS = 40

# Rate limits per minute. Keyed on the visitor id, not the IP: behind the host's
# proxy every request can arrive from the same address. Counts live in memory, so
# each gunicorn worker keeps its own (2 workers = up to double), which is fine
# for keeping junk out.
PER_VISITOR_PER_MINUTE = 120
TOTAL_PER_MINUTE = 3000

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    ts         TEXT NOT NULL,      -- UTC, 'YYYY-MM-DD HH:MM:SS'
    event      TEXT NOT NULL,
    visitor_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    device     TEXT NOT NULL,      -- 'mobile' or 'desktop'
    props      TEXT NOT NULL       -- small JSON object, whitelisted keys only
);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_event ON events(event);
"""


def db_path():
    return os.environ.get("ANALYTICS_DB_PATH") or DEFAULT_DB_PATH


def get_connection():
    # Creating the table on every connection (IF NOT EXISTS, so it's cheap) means a
    # deleted or freshly mounted file just starts over instead of failing until a restart.
    path = db_path()
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    conn = sqlite3.connect(path, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # readers don't block the writer
    conn.executescript(SCHEMA)
    return conn


# ---------- rate limiting ----------

_rate_lock = threading.Lock()
_rate = {"minute": None, "total": 0, "visitors": {}}


def within_rate_limit(visitor_id):
    minute = int(time.time() // 60)
    with _rate_lock:
        if _rate["minute"] != minute:
            _rate.update(minute=minute, total=0, visitors={})
        seen = _rate["visitors"].get(visitor_id, 0)
        if _rate["total"] >= TOTAL_PER_MINUTE or seen >= PER_VISITOR_PER_MINUTE:
            return False
        _rate["total"] += 1
        _rate["visitors"][visitor_id] = seen + 1
        return True


# ---------- POST /api/event ----------

def clean_props(props):
    """Keeps only whitelisted keys with simple values, strings cut to 40 chars."""
    if not isinstance(props, dict):
        return {}
    cleaned = {}
    for key in ALLOWED_PROPS:
        value = props.get(key)
        if isinstance(value, (bool, int)):
            cleaned[key] = value
        elif isinstance(value, str):
            cleaned[key] = value[:MAX_PROP_CHARS]
    return cleaned


def device_type():
    ua = request.headers.get("User-Agent", "")
    return "mobile" if re.search(r"Mobi|Android|iPhone|iPad", ua) else "desktop"


@analytics_bp.route("/api/event", methods=["POST"])
def record_event():
    """
    Body (JSON, sent as text/plain by navigator.sendBeacon):
      {"event": "page_view", "visitor_id": "...", "session_id": "...", "props": {...}}
    Always 204 on success, and also when analytics is switched off.
    """
    if os.environ.get("ANALYTICS_ENABLED", "1") == "0":
        return "", 204

    if (request.content_length or 0) > MAX_BODY_BYTES:
        return "", 413
    raw = request.stream.read(MAX_BODY_BYTES + 1)   # covers bodies sent without a length too
    if len(raw) > MAX_BODY_BYTES:
        return "", 413

    # parse it ourselves: request.get_json() would refuse the text/plain beacons
    try:
        body = json.loads(raw.decode("utf-8"))
    except ValueError:
        return "", 400
    if not isinstance(body, dict):
        return "", 400

    event = body.get("event")
    visitor_id = body.get("visitor_id")
    session_id = body.get("session_id")
    if event not in ALLOWED_EVENTS:
        return "", 400
    for value in (visitor_id, session_id):
        if not isinstance(value, str) or not ID_PATTERN.match(value):
            return "", 400

    if not within_rate_limit(visitor_id):
        return "", 429

    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO events (ts, event, visitor_id, session_id, device, props) VALUES (?, ?, ?, ?, ?, ?)",
            (
                time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
                event, visitor_id, session_id, device_type(),
                json.dumps(clean_props(body.get("props")), separators=(",", ":")),
            ),
        )
        conn.commit()
        conn.close()
    except (sqlite3.Error, OSError):
        # most likely the volume isn't writable; say so in the logs, the page doesn't care
        current_app.logger.exception("could not save analytics event to %s", db_path())
        return "", 503
    return "", 204


# ---------- GET /api/admin/stats ----------

def authorized():
    token = os.environ.get("ADMIN_TOKEN", "")
    given = request.headers.get("Authorization", "")
    return hmac.compare_digest(given.encode("utf-8"), f"Bearer {token}".encode("utf-8"))


@analytics_bp.route("/api/admin/stats", methods=["GET"])
def stats():
    """
    Usage summary for the last ?days=N days (1 to 90, default 14). Dates are UTC.
      curl -H "Authorization: Bearer $ADMIN_TOKEN" https://<site>/api/admin/stats?days=7
    404 when ADMIN_TOKEN isn't set (stats switched off), 401 with a wrong token.
    """
    if not os.environ.get("ADMIN_TOKEN"):
        return jsonify({"error": "not found"}), 404
    if not authorized():
        return jsonify({"error": "unauthorized"}), 401

    try:
        days = min(max(int(request.args.get("days", 14)), 1), 90)
    except ValueError:
        return jsonify({"error": "days must be a whole number"}), 400

    today = datetime.datetime.now(datetime.timezone.utc).date()
    since = (today - datetime.timedelta(days=days - 1)).isoformat()
    week_ago = (today - datetime.timedelta(days=6)).isoformat()

    conn = get_connection()

    def one(sql, *params):
        return conn.execute(sql, params).fetchone()[0]

    def counts(sql, *params):
        # str() because a missing prop comes back as None, and JSON keys must be strings
        return {str(row[0]): row[1] for row in conn.execute(sql, params).fetchall()}

    totals = conn.execute("""
        SELECT COUNT(*) AS events, COUNT(DISTINCT visitor_id) AS visitors,
               COUNT(DISTINCT session_id) AS sessions
        FROM events WHERE ts >= ?""", (since,)).fetchone()

    per_day = [dict(r) for r in conn.execute("""
        SELECT substr(ts, 1, 10) AS date,
               COUNT(DISTINCT visitor_id) AS visitors,
               COUNT(DISTINCT session_id) AS sessions,
               SUM(event = 'page_view') AS page_views,
               COUNT(*) AS events
        FROM events WHERE ts >= ?
        GROUP BY date ORDER BY date""", (since,)).fetchall()]

    # areas are stored as "1B,5C", so split them before counting
    ge_areas = {}
    for (areas,) in conn.execute("""
            SELECT json_extract(props, '$.areas') FROM events
            WHERE event = 'ge_search' AND ts >= ?""", (since,)).fetchall():
        for code in str(areas or "").split(","):
            if code.strip():
                ge_areas[code.strip()] = ge_areas.get(code.strip(), 0) + 1

    conflict_rows = counts("""
        SELECT json_extract(props, '$.conflict_free'), COUNT(*) FROM events
        WHERE event = 'conflict_check' AND ts >= ? GROUP BY 1""", since)

    result = {
        "days": days,
        "since": since,
        "totals": dict(totals),
        "visitors_today": one("SELECT COUNT(DISTINCT visitor_id) FROM events WHERE ts >= ?", today.isoformat()),
        "visitors_7d": one("SELECT COUNT(DISTINCT visitor_id) FROM events WHERE ts >= ?", week_ago),
        "per_day": per_day,
        "by_event": counts("SELECT event, COUNT(*) FROM events WHERE ts >= ? GROUP BY event ORDER BY 2 DESC", since),
        "page_views_by_view": counts("""
            SELECT json_extract(props, '$.view'), COUNT(*) FROM events
            WHERE event = 'page_view' AND ts >= ? GROUP BY 1 ORDER BY 2 DESC""", since),
        "ge_areas": dict(sorted(ge_areas.items(), key=lambda kv: -kv[1])),
        "conflict_checks": {
            "conflict_free": conflict_rows.get("1", 0),     # JSON true comes back as 1
            "conflicts_found": conflict_rows.get("0", 0),
        },
        "devices": counts("""
            SELECT device, COUNT(DISTINCT visitor_id) FROM events
            WHERE ts >= ? GROUP BY device""", since),
    }
    conn.close()
    response = jsonify(result)
    response.headers["Cache-Control"] = "no-store"
    return response

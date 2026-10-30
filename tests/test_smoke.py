"""
Smoke tests for the deployable app: health, first-start database build, GE
filter, conflict check input rules, security headers, and anonymous analytics.

Run from the project root:
    python3 -m unittest discover -s tests -v

Everything runs against throwaway databases in a temp folder, never the real
backend/sql/*.db files.
"""

import contextlib
import io
import json
import os
import sqlite3
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# These must be set before the app is imported: db.py reads EZCLASS_DB_PATH at
# import time, and importing app.py builds the class database.
TMP = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
CLASS_DB = os.path.join(TMP.name, "scheduler.db")
ANALYTICS_DB = os.path.join(TMP.name, "analytics.db")
ADMIN_TOKEN = "test-admin-token"
os.environ["EZCLASS_DB_PATH"] = CLASS_DB
os.environ["ANALYTICS_DB_PATH"] = ANALYTICS_DB
os.environ["ADMIN_TOKEN"] = ADMIN_TOKEN
os.environ.pop("ANALYTICS_ENABLED", None)

with contextlib.redirect_stdout(io.StringIO()):   # the loader prints a line per table
    from backend import app as app_module
from backend.models import db
from backend.models.conflicts import find_conflicts

EXPECTED_CSP = (
    "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
    "script-src 'self'; connect-src 'self'; frame-ancestors 'none'; "
    "base-uri 'self'; form-action 'self'"
)


def class_db_count(sql, *params):
    conn = sqlite3.connect(CLASS_DB)
    try:
        return conn.execute(sql, params).fetchone()[0]
    finally:
        conn.close()


def stored_events(visitor_id):
    if not os.path.exists(ANALYTICS_DB):
        return []
    conn = sqlite3.connect(ANALYTICS_DB)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute("SELECT * FROM events WHERE visitor_id = ?", (visitor_id,))]
    finally:
        conn.close()


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app_module.app.test_client()

    def event(self, visitor_id, event="page_view", props=None, as_text=False, **extra):
        body = {"event": event, "visitor_id": visitor_id, "session_id": "session-1234", "props": props or {}}
        body.update(extra)
        if as_text:   # what navigator.sendBeacon sends
            return self.client.post("/api/event", data=json.dumps(body), content_type="text/plain;charset=UTF-8")
        return self.client.post("/api/event", json=body)


class CoreTests(AppTestCase):
    def test_health_and_home(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {"status": "ok"})

        with self.client.get("/") as res:
            self.assertEqual(res.status_code, 200)
            html = res.get_data(as_text=True)
        self.assertIn("EzClass", html)
        self.assertIn('src="js/track.js"', html)
        self.assertIn('id="track-optout"', html)

    def test_health_reports_broken_database(self):
        with mock.patch.object(app_module, "get_connection", side_effect=sqlite3.OperationalError("gone")):
            res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 503)
        self.assertEqual(res.get_json(), {"status": "error"})

    def test_database_built_on_first_start(self):
        self.assertTrue(os.path.exists(CLASS_DB))
        self.assertEqual(class_db_count("SELECT COUNT(*) FROM sections"), 559)
        self.assertEqual(class_db_count("SELECT COUNT(*) FROM courses"), 145)

    def test_existing_database_is_never_wiped(self):
        conn = sqlite3.connect(CLASS_DB)
        conn.execute("INSERT INTO students (first_name, last_name, email) VALUES ('Keep', 'Me', 'keep@example.com')")
        conn.commit()
        conn.close()
        try:
            db.ensure_database()
            self.assertEqual(class_db_count("SELECT COUNT(*) FROM students WHERE email = 'keep@example.com'"), 1)
        finally:
            conn = sqlite3.connect(CLASS_DB)
            conn.execute("DELETE FROM students WHERE email = 'keep@example.com'")
            conn.commit()
            conn.close()

    def test_ge_filter_and_areas(self):
        areas = self.client.get("/api/ge-areas").get_json()
        self.assertEqual(len(areas["areas"]), 14)
        self.assertEqual(areas["total_sections"], 425)
        self.assertEqual(len(self.client.get("/api/sections?ge=1B").get_json()), 78)
        self.assertEqual(len(self.client.get("/api/sections?ge=1B,5C").get_json()), 132)
        self.assertEqual(len(self.client.get("/api/sections?ge=1B&day=W").get_json()), 65)

    def test_security_headers(self):
        for path in ("/", "/api/health", "/js/app.js", "/api/sections/999999"):
            with self.client.get(path) as res:
                headers = res.headers
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff", path)
            self.assertEqual(headers["X-Frame-Options"], "DENY", path)
            self.assertEqual(headers["Referrer-Policy"], "strict-origin-when-cross-origin", path)
            self.assertEqual(headers["Permissions-Policy"], "geolocation=(), microphone=(), camera=()", path)
            self.assertEqual(headers["Content-Security-Policy"], EXPECTED_CSP, path)


class ConflictCheckTests(AppTestCase):
    def check(self, body=None, **kwargs):
        if body is not None:
            kwargs["json"] = body
        return self.client.post("/api/schedule/check", **kwargs)

    def test_good_input(self):
        conn = db.get_connection()
        sections = [dict(r) for r in conn.execute("SELECT * FROM sections ORDER BY section_id")]
        conn.close()
        a, b = find_conflicts(sections)[0]

        res = self.check({"section_ids": [a["section_id"], b["section_id"]]})
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertFalse(data["conflict_free"])
        self.assertEqual(len(data["conflicts"]), 1)

        res = self.check({"section_ids": [a["section_id"]]})
        self.assertEqual(res.get_json(), {"conflicts": [], "conflict_free": True})

    def test_empty_and_non_json(self):
        for kwargs in ({"json": {"section_ids": []}}, {"json": {}},
                       {"data": "not json", "content_type": "text/plain"}, {}):
            res = self.client.post("/api/schedule/check", **kwargs)
            self.assertEqual(res.status_code, 200, kwargs)
            self.assertEqual(res.get_json(), {"conflicts": [], "conflict_free": True}, kwargs)

    def test_rejected_inputs(self):
        bad_bodies = [
            {"section_ids": ["1; DROP TABLE sections"]},
            {"section_ids": "abc"},
            {"section_ids": [True]},
            {"section_ids": [1.5]},
            {"section_ids": list(range(1, 62))},
            {"section_ids": None},
            {"section_ids": [2**70]},
            [1, 2],
        ]
        for body in bad_bodies:
            res = self.check(body)
            self.assertEqual(res.status_code, 400, body)
            data = res.get_json()
            self.assertIn("error", data)
            self.assertEqual(data["conflicts"], [])
            self.assertIs(data["conflict_free"], False)
        self.assertEqual(class_db_count("SELECT COUNT(*) FROM sections"), 559)

    def test_sixty_ids_is_allowed(self):
        self.assertEqual(self.check({"section_ids": list(range(1, 61))}).status_code, 200)


class AnalyticsTests(AppTestCase):
    def test_events_accepted_json_and_text_plain(self):
        vid = "visitor-accepted"
        self.assertEqual(self.event(vid, props={"view": "ge"}).status_code, 204)
        self.assertEqual(self.event(vid, "ge_search", {"areas": "1B,5C", "results": 132}, as_text=True).status_code, 204)
        rows = stored_events(vid)
        self.assertEqual([r["event"] for r in rows], ["page_view", "ge_search"])
        self.assertEqual(json.loads(rows[1]["props"]), {"areas": "1B,5C", "results": 132})
        self.assertEqual(rows[0]["device"], "desktop")
        self.assertEqual(rows[0]["session_id"], "session-1234")

    def test_device_is_only_mobile_or_desktop(self):
        vid = "visitor-mobile"
        ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Mobile/15E148"
        self.client.post("/api/event", json={"event": "page_view", "visitor_id": vid, "session_id": "session-1234"},
                         headers={"User-Agent": ua})
        row = stored_events(vid)[0]
        self.assertEqual(row["device"], "mobile")
        self.assertNotIn("iPhone", json.dumps(row))

    def test_junk_events_rejected(self):
        vid = "visitor-junk"
        cases = [
            self.event(vid, "delete_everything"),
            self.event("short", "page_view"),
            self.event("bad id with spaces!", "page_view"),
            self.event(vid, "page_view", session_id="x" * 65),
            self.client.post("/api/event", json={"event": "page_view", "visitor_id": 12345678,
                                                 "session_id": "session-1234"}),
            self.client.post("/api/event", data="{not json", content_type="text/plain"),
            self.client.post("/api/event", json=["page_view"]),
        ]
        for res in cases:
            self.assertEqual(res.status_code, 400)
        self.assertEqual(stored_events(vid), [])

    def test_oversized_event_rejected(self):
        vid = "visitor-big"
        res = self.event(vid, "search", {"subject": "x" * 3000})
        self.assertEqual(res.status_code, 413)
        self.assertEqual(stored_events(vid), [])

    def test_typed_text_never_stored(self):
        vid = "visitor-private"
        props = {
            "subject": "CS", "has_prof": True, "has_kw": True, "results": 3,
            "professor": "Nguyen", "q": "secret keyword", "email": "me@sdsu.edu", "name": "Real Name",
            "areas": "A" * 100,
        }
        self.assertEqual(self.event(vid, "search", props).status_code, 204)
        row = stored_events(vid)[0]
        stored = json.loads(row["props"])
        self.assertEqual(set(stored), {"subject", "has_prof", "has_kw", "results", "areas"})
        self.assertEqual(len(stored["areas"]), 40)
        everything = json.dumps(row)
        for secret in ("Nguyen", "secret keyword", "me@sdsu.edu", "Real Name", "127.0.0.1"):
            self.assertNotIn(secret, everything)
        # and there is no column that could hold an IP or user agent
        conn = sqlite3.connect(ANALYTICS_DB)
        columns = [r[1] for r in conn.execute("PRAGMA table_info(events)")]
        conn.close()
        self.assertEqual(columns, ["id", "ts", "event", "visitor_id", "session_id", "device", "props"])

    def test_rate_limit_per_visitor(self):
        vid = "visitor-flood"
        codes = [self.event(vid, "cart_add").status_code for _ in range(121)]
        self.assertEqual(codes[:120], [204] * 120)
        self.assertEqual(codes[120], 429)
        self.assertEqual(self.event("visitor-other", "cart_add").status_code, 204)

    def test_stats_need_token(self):
        self.event("visitor-stats", "conflict_check", {"conflict_free": True})
        self.assertEqual(self.client.get("/api/admin/stats").status_code, 401)
        res = self.client.get("/api/admin/stats", headers={"Authorization": "Bearer wrong"})
        self.assertEqual(res.status_code, 401)

        auth = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
        res = self.client.get("/api/admin/stats?days=7", headers=auth)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        for key in ("totals", "visitors_today", "visitors_7d", "per_day", "by_event",
                    "page_views_by_view", "ge_areas", "conflict_checks", "devices"):
            self.assertIn(key, data)
        self.assertEqual(data["days"], 7)
        self.assertGreaterEqual(data["visitors_today"], 1)
        self.assertGreaterEqual(data["conflict_checks"]["conflict_free"], 1)

        self.assertEqual(self.client.get("/api/admin/stats?days=500", headers=auth).get_json()["days"], 90)
        self.assertEqual(self.client.get("/api/admin/stats?days=0", headers=auth).get_json()["days"], 1)
        self.assertEqual(self.client.get("/api/admin/stats?days=abc", headers=auth).status_code, 400)

    def test_stats_off_without_token(self):
        with mock.patch.dict(os.environ, {"ADMIN_TOKEN": ""}):
            res = self.client.get("/api/admin/stats", headers={"Authorization": "Bearer "})
        self.assertEqual(res.status_code, 404)

    def test_tracking_turned_off(self):
        vid = "visitor-disabled"
        with mock.patch.dict(os.environ, {"ANALYTICS_ENABLED": "0"}):
            self.assertEqual(self.event(vid).status_code, 204)
            self.assertEqual(self.event(vid, "junk_event").status_code, 204)
        self.assertEqual(stored_events(vid), [])


if __name__ == "__main__":
    unittest.main()

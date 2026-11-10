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
FEEDBACK_DB = os.path.join(TMP.name, "feedback.db")
ADMIN_TOKEN = "test-admin-token"
os.environ["EZCLASS_DB_PATH"] = CLASS_DB
os.environ["ANALYTICS_DB_PATH"] = ANALYTICS_DB
os.environ["FEEDBACK_DB_PATH"] = FEEDBACK_DB
os.environ["ADMIN_TOKEN"] = ADMIN_TOKEN
os.environ.pop("ANALYTICS_ENABLED", None)

with contextlib.redirect_stdout(io.StringIO()):   # the loader prints a line per table
    from backend import app as app_module
from backend.models import db
from backend.routes import analytics
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

    def test_every_page_loads_with_shared_header_and_tracking(self):
        # the footer (with the #track-optout link) is built by nav.js, which each page module imports
        for page in ("index", "major", "ge", "search", "schedule", "reviews", "support"):
            with self.client.get(f"/{page}.html") as res:
                self.assertEqual(res.status_code, 200, page)
                html = res.get_data(as_text=True)
            self.assertIn('id="site-header"', html, page)
            self.assertIn('id="site-footer"', html, page)
            self.assertIn('<script type="module" src="js/track.js">', html, page)
            self.assertNotIn("<script>", html, page)          # CSP: no inline scripts
            self.assertNotIn("onclick", html, page)
        with self.client.get("/js/nav.js") as res:
            self.assertIn('id: "track-optout"', res.get_data(as_text=True))

    def test_info_reports_when_class_data_was_updated(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "data_info.json")
            with mock.patch.object(app_module, "DATA_INFO_PATH", path):
                self.assertEqual(self.client.get("/api/info").get_json(), {"data_updated": None})   # no file
                for content, expected in (('{"updated": "2026-11-04"}', "2026-11-04"),
                                          ('{"updated": "<b>soon</b>"}', None),
                                          ('{"updated": 5}', None), ('[1]', None), ("not json", None)):
                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)
                    self.assertEqual(self.client.get("/api/info").get_json(), {"data_updated": expected}, content)

    def test_health_reports_broken_database(self):
        with mock.patch.object(app_module, "get_connection", side_effect=sqlite3.OperationalError("gone")):
            res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 503)
        self.assertEqual(res.get_json(), {"status": "error"})

    def test_database_built_on_first_start(self):
        self.assertTrue(os.path.exists(CLASS_DB))
        # Spring 2027: 2,284 sections in the sheet, plus 9 from the earlier import kept as inactive
        self.assertEqual(class_db_count("SELECT COUNT(*) FROM sections WHERE active = 1"), 2284)
        self.assertEqual(class_db_count("SELECT COUNT(*) FROM sections WHERE active = 0"), 9)
        self.assertEqual(class_db_count("SELECT COUNT(*) FROM section_meetings"), 3203 + 9)   # inactive ones keep theirs
        self.assertEqual(class_db_count("SELECT COUNT(*) FROM courses"), 779)   # 777 offered + 2 with only inactive sections

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
        self.assertEqual(areas["total_sections"], 1275)
        self.assertEqual(len(self.client.get("/api/sections?ge=1B").get_json()), 83)
        self.assertEqual(len(self.client.get("/api/sections?ge=1B,5C").get_json()), 170)
        self.assertEqual(len(self.client.get("/api/sections?ge=1B&day=W").get_json()), 65)

    def test_section_with_no_schedule_yet(self):
        pa = next(s for s in self.client.get("/api/sections?subject=PA").get_json()
                  if s["catalog_num"] == "301" and s["section_number"] == "01")
        self.assertEqual((pa["meetings"], pa["no_schedule"], pa["online_only"], pa["instructors"]), ([], True, False, []))
        self.assertEqual([pa[k] for k in ("days", "start_time", "end_time", "building", "room_number", "seats_total")], [None] * 6)
        # a class that meets every weekday all day still doesn't conflict with it
        busy = next(s for s in self.client.get("/api/sections?subject=CS").get_json() if not s["online_only"] and s["meetings"])
        res = self.client.post("/api/schedule/check", json={"section_ids": [pa["section_id"], busy["section_id"]]})
        self.assertTrue(res.get_json()["conflict_free"])

    def test_online_only_and_hybrid_flags(self):
        sections = self.client.get("/api/sections").get_json()
        self.assertEqual(len(sections), 2284)
        self.assertEqual(sum(s["online_only"] for s in sections), 411)
        self.assertEqual(sum(s["no_schedule"] for s in sections), 108)
        self.assertEqual(sum(1 for s in sections if not s["online_only"] and any(m["online"] for m in s["meetings"])), 151)

    def test_special_topics_section_titles(self):
        music = [s for s in self.client.get("/api/sections?subject=MUSIC").get_json() if s["catalog_num"] == "351"]
        self.assertEqual(len(music), 9)
        self.assertEqual({s["course_title"] for s in music}, {"Music and Culture"})
        self.assertIn("Music and Culture: Hip Hop", {s["section_title"] for s in music})

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
        for kwargs in ({"json": {"section_ids": []}}, {"json": {}}):
            res = self.client.post("/api/schedule/check", **kwargs)
            self.assertEqual(res.status_code, 200, kwargs)
            self.assertEqual(res.get_json(), {"conflicts": [], "conflict_free": True}, kwargs)
        # not JSON, or no body at all: a 400, never "conflict free"
        for kwargs in ({"data": "not json", "content_type": "text/plain"}, {"data": "not json", "content_type": "application/json"}, {}):
            res = self.client.post("/api/schedule/check", **kwargs)
            self.assertEqual(res.status_code, 400, kwargs)
            self.assertIs(res.get_json()["conflict_free"], False)

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
        self.assertEqual(class_db_count("SELECT COUNT(*) FROM sections"), 2293)

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

    def test_reviews_and_support_are_counted(self):
        vid = "visitor-feedback-pages"
        for view in ("reviews", "support"):
            self.assertEqual(self.event(vid, props={"view": view}).status_code, 204)
        self.assertEqual(self.event(vid, "review_submit").status_code, 204)
        self.assertEqual(self.event(vid, "support_submit", {"kind": "wrong_info"}).status_code, 204)
        rows = stored_events(vid)
        self.assertEqual([r["event"] for r in rows], ["page_view", "page_view", "review_submit", "support_submit"])
        self.assertEqual(json.loads(rows[3]["props"]), {"kind": "wrong_info"})
        stats = self.client.get("/api/admin/stats?days=1", headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}).get_json()
        self.assertGreaterEqual(stats["page_views_by_view"].get("reviews", 0), 1)
        self.assertGreaterEqual(stats["page_views_by_view"].get("support", 0), 1)
        self.assertGreaterEqual(stats["by_event"].get("review_submit", 0), 1)
        self.assertGreaterEqual(stats["by_event"].get("support_submit", 0), 1)

    def test_unknown_view_or_kind_is_dropped(self):
        vid = "visitor-unknown-view"
        self.assertEqual(self.event(vid, props={"view": "my email is a@b.c"}).status_code, 204)
        self.assertEqual(self.event(vid, "support_submit", {"kind": "free text here"}).status_code, 204)
        self.assertEqual([json.loads(r["props"]) for r in stored_events(vid)], [{}, {}])

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
        # The limit counts per clock minute. Pin the clock so the 121 requests
        # can't straddle a minute boundary (which resets the count and made
        # this test fail now and then).
        vid = "visitor-flood"
        with mock.patch.object(analytics.time, "time", return_value=1_800_000_000.0):
            codes = [self.event(vid, "cart_add").status_code for _ in range(121)]
            other = self.event("visitor-other", "cart_add").status_code
        self.assertEqual(codes[:120], [204] * 120)
        self.assertEqual(codes[120], 429)
        self.assertEqual(other, 204)

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


class SiteTests(AppTestCase):
    """Clean URLs, the 404 page, gzip, robots.txt / sitemap.xml and the favicon."""

    def test_clean_urls_redirect(self):
        for page in ("search", "major", "ge", "schedule", "reviews", "support"):
            res = self.client.get(f"/{page}")
            self.assertEqual((res.status_code, res.headers["Location"]), (301, f"/{page}.html"), page)
        res = self.client.get("/search?q=cs%20480&day=M")
        self.assertEqual(res.headers["Location"], "/search.html?q=cs%20480&day=M")
        self.assertEqual(self.client.get("/major/").headers["Location"], "/major.html")

    def test_not_found(self):
        for path in ("/nope", "/a/b/c", "/searchh"):
            with self.client.get(path) as res:
                self.assertEqual(res.status_code, 404, path)
                self.assertIn("We couldn't find that page", res.get_data(as_text=True))
        for path in ("/api/anything-unknown", "/api/sections/x"):
            res = self.client.get(path)
            self.assertEqual((res.status_code, res.get_json()), (404, {"error": "not found"}), path)
        self.assertEqual(self.client.get("/api/sections/999999").get_json(), {"error": "section not found"})

    def test_gzip_when_asked(self):
        plain = self.client.get("/api/sections")
        self.assertNotIn("Content-Encoding", plain.headers)
        zipped = self.client.get("/api/sections", headers={"Accept-Encoding": "gzip, deflate, br"})
        self.assertEqual(zipped.headers["Content-Encoding"], "gzip")
        self.assertIn("Accept-Encoding", zipped.headers["Vary"])
        import gzip
        self.assertEqual(gzip.decompress(zipped.data), plain.data)
        self.assertLess(len(zipped.data), len(plain.data) / 5)
        with self.client.get("/css/base.css", headers={"Accept-Encoding": "gzip"}) as css:
            self.assertEqual(css.headers["Content-Encoding"], "gzip")
        tiny = self.client.get("/api/health", headers={"Accept-Encoding": "gzip"})
        self.assertNotIn("Content-Encoding", tiny.headers)          # too small to bother

    def test_robots_sitemap_favicon(self):
        robots = self.client.get("/robots.txt", headers={"X-Forwarded-Proto": "https"}, base_url="http://ezclass.example")
        text = robots.get_data(as_text=True)
        self.assertIn("Disallow: /api/", text)
        self.assertIn("Sitemap: https://ezclass.example/sitemap.xml", text)
        sitemap = self.client.get("/sitemap.xml", headers={"X-Forwarded-Proto": "https"}, base_url="http://ezclass.example")
        self.assertEqual(sitemap.mimetype, "application/xml")
        body = sitemap.get_data(as_text=True)
        for page in ("", "major.html", "ge.html", "search.html", "schedule.html", "reviews.html", "support.html"):
            self.assertIn(f"<loc>https://ezclass.example/{page}</loc>", body)
        self.assertNotIn("/api/", body)
        with mock.patch.dict(os.environ, {"SITE_URL": "https://www.ezclass.app/"}):
            self.assertIn("<loc>https://www.ezclass.app/search.html</loc>", self.client.get("/sitemap.xml").get_data(as_text=True))
        # reached through the old Render address, the links still name the real domain
        old = {"headers": {"X-Forwarded-Proto": "https"}, "base_url": "http://ezclass-old.onrender.example"}
        with mock.patch.dict(os.environ, {"SITE_URL": "https://ezclass.win"}):
            self.assertIn("Sitemap: https://ezclass.win/sitemap.xml", self.client.get("/robots.txt", **old).get_data(as_text=True))
            body = self.client.get("/sitemap.xml", **old).get_data(as_text=True)
            self.assertIn("<loc>https://ezclass.win/</loc>", body)
            self.assertIn("<loc>https://ezclass.win/support.html</loc>", body)
            self.assertNotIn("onrender", body)
        with self.client.get("/favicon.svg") as icon:
            self.assertEqual((icon.status_code, icon.mimetype), (200, "image/svg+xml"))
        self.assertEqual(self.client.get("/favicon.ico").headers["Location"], "/favicon.svg")
        for page in ("index", "major", "ge", "search", "schedule", "reviews", "support"):
            with self.client.get(f"/{page}.html") as res:
                self.assertIn('<link rel="icon" href="favicon.svg"', res.get_data(as_text=True), page)

    def test_bad_day_is_a_400(self):
        for day in ("Q", "Monday", "m", "%"):
            self.assertEqual(self.client.get(f"/api/sections?day={day}").status_code, 400, day)
        self.assertEqual(self.client.get("/api/sections?day=Th").status_code, 200)

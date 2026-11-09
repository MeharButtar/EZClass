"""
Tests for Reviews and Support (backend/routes/feedback.py).

Shares test_smoke's throwaway databases (FEEDBACK_DB_PATH points into its temp folder).
"""

import json
import os
import sqlite3
import unittest
from unittest import mock

from test_smoke import ADMIN_TOKEN, FEEDBACK_DB, AppTestCase

from backend.routes import feedback

AUTH = {"Authorization": f"Bearer {ADMIN_TOKEN}"}


def rows(table):
    conn = sqlite3.connect(FEEDBACK_DB)
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(f"SELECT * FROM {table} ORDER BY id")]
    finally:
        conn.close()


class FeedbackCase(AppTestCase):
    visitor = "visitor-feedback-1"

    def setUp(self):
        super().setUp()
        feedback.reset_rate_limits()
        conn = feedback.get_connection()
        conn.execute("DELETE FROM reviews")
        conn.execute("DELETE FROM support_messages")
        conn.commit()
        conn.close()

    def review(self, **fields):
        body = {"rating": 5, "comment": "Saved me an hour.", "name": "", "website": "", "elapsed_ms": 9000,
                "visitor_id": self.visitor}
        body.update(fields)
        return self.client.post("/api/reviews", json=body)

    def support(self, **fields):
        body = {"kind": "wrong_info", "message": "SOC 101 section 5 meets at 1pm, not noon.", "course": "SOC 101",
                "section": "5", "email": "", "website": "", "elapsed_ms": 9000, "visitor_id": self.visitor}
        body.update(fields)
        return self.client.post("/api/support", json=body)

    def approve(self, review_id, status="approved"):
        return self.client.post(f"/api/admin/reviews/{review_id}", json={"status": status}, headers=AUTH)

    def public(self):
        return self.client.get("/api/reviews").get_json()


class ReviewTests(FeedbackCase):
    def test_new_review_waits_for_approval(self):
        res = self.review(rating=4, comment="  Pretty good\\r\\n  ", name="Sam")
        self.assertEqual(res.status_code, 201)
        self.assertEqual(res.get_json(), {"ok": True, "status": "pending"})
        self.assertEqual(self.public(), {"average": None, "count": 0, "reviews": []})
        stored = rows("reviews")[0]
        self.assertEqual((stored["rating"], stored["display_name"], stored["status"]), (4, "Sam", "pending"))

        self.assertEqual(self.approve(stored["id"]).status_code, 200)
        data = self.public()
        self.assertEqual((data["average"], data["count"]), (4.0, 1))
        self.assertEqual(data["reviews"][0]["name"], "Sam")
        self.assertRegex(data["reviews"][0]["date"], r"^\d{4}-\d{2}-\d{2}$")

        self.visitor = "visitor-feedback-2"
        self.review(rating=5, name="")
        self.approve(rows("reviews")[1]["id"])
        data = self.public()
        self.assertEqual((data["average"], data["count"]), (4.5, 2))
        self.assertEqual([r["name"] for r in data["reviews"]], ["A student", "Sam"])   # newest first

        self.approve(stored["id"], "hidden")
        self.assertEqual(self.public()["count"], 1)

    def test_paging(self):
        conn = feedback.get_connection()
        conn.executemany("INSERT INTO reviews (created_at, rating, comment, display_name, status) VALUES (?, 5, ?, '', 'approved')",
                         [("2026-11-01 10:00:00", f"review {i}") for i in range(25)])
        conn.commit()
        conn.close()
        first = self.client.get("/api/reviews?limit=20&offset=0").get_json()
        second = self.client.get("/api/reviews?limit=20&offset=20").get_json()
        self.assertEqual((len(first["reviews"]), len(second["reviews"]), first["count"]), (20, 5, 25))
        self.assertEqual(first["reviews"][0]["comment"], "review 24")
        self.assertEqual(self.client.get("/api/reviews?limit=x").status_code, 400)

    def test_bad_reviews_are_refused(self):
        for fields in ({"rating": 0}, {"rating": 6}, {"rating": "x"}, {"rating": True}, {"rating": 4.5}, {"rating": None},
                       {"comment": "x" * 601}, {"comment": "see http://spam.example"}, {"comment": "WWW.spam.com"},
                       {"name": "n" * 31}, {"comment": 5}):
            res = self.review(**fields)
            self.assertEqual(res.status_code, 400, fields)
            self.assertIn("error", res.get_json())
        self.assertEqual(rows("reviews"), [])

    def test_limits_are_exact(self):
        self.assertEqual(self.review(comment="x" * 600, name="n" * 30).status_code, 201)

    def test_json_only_and_size_limit(self):
        self.assertEqual(self.client.post("/api/reviews", data="rating=5", content_type="application/x-www-form-urlencoded").status_code, 400)
        self.assertEqual(self.client.post("/api/reviews", data="not json", content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post("/api/reviews", json=[1, 2]).status_code, 400)
        big = json.dumps({"rating": 5, "comment": "x" * 9000})
        self.assertEqual(self.client.post("/api/reviews", data=big, content_type="application/json").status_code, 413)

    def test_control_characters_are_stripped(self):
        self.review(comment="ok\x00\x07 then\nnew line", name="Al\x1bex")
        stored = rows("reviews")[0]
        self.assertEqual((stored["comment"], stored["display_name"]), ("ok then\nnew line", "Alex"))

    def test_html_is_stored_as_plain_text(self):
        self.review(comment="<img src=x onerror=alert(1)>")
        self.approve(rows("reviews")[0]["id"])
        self.assertEqual(self.public()["reviews"][0]["comment"], "<img src=x onerror=alert(1)>")


class SpamTests(FeedbackCase):
    def test_honeypot_and_too_fast_store_nothing(self):
        for fields in ({"website": "http://bot.example"}, {"elapsed_ms": 300}, {"elapsed_ms": "9000"}, {"elapsed_ms": None}):
            self.assertEqual(self.review(**fields).status_code, 201, fields)
            res = self.support(**fields)
            self.assertEqual(res.status_code, 201, fields)
            self.assertTrue(res.get_json()["ref"].startswith("S-"))
        self.assertEqual((rows("reviews"), rows("support_messages")), ([], []))

    def test_three_per_ten_minutes_per_browser(self):
        for _ in range(3):
            self.assertEqual(self.review().status_code, 201)
        res = self.support()
        self.assertEqual(res.status_code, 429)
        self.assertIn("try again", res.get_json()["error"])
        self.visitor = "visitor-feedback-other"
        self.assertEqual(self.review().status_code, 201)          # another browser is fine
        self.assertEqual(len(rows("reviews")), 4)

    def test_mistakes_do_not_use_up_the_limit(self):
        for _ in range(5):
            self.assertEqual(self.review(rating=9).status_code, 400)
        self.assertEqual(self.review().status_code, 201)

    def test_overall_limit(self):
        with mock.patch.object(feedback, "OVERALL", (2, 3600)):
            self.visitor = "visitor-a-12345"
            self.assertEqual(self.review().status_code, 201)
            self.visitor = "visitor-b-12345"
            self.assertEqual(self.review().status_code, 201)
            self.visitor = "visitor-c-12345"
            self.assertEqual(self.review().status_code, 429)

    def test_limit_window_passes(self):
        with mock.patch.object(feedback.time, "time", return_value=1_000_000):
            for _ in range(3):
                self.review()
            self.assertEqual(self.review().status_code, 429)
        with mock.patch.object(feedback.time, "time", return_value=1_000_000 + 601):
            self.assertEqual(self.review().status_code, 201)


class SupportTests(FeedbackCase):
    def test_message_is_stored_with_a_reference(self):
        res = self.support(email="me@example.com")
        self.assertEqual(res.status_code, 201)
        stored = rows("support_messages")[0]
        self.assertEqual(res.get_json(), {"ok": True, "ref": f"S-{stored['id']}"})
        self.assertEqual((stored["kind"], stored["course"], stored["section"], stored["email"], stored["status"]),
                         ("wrong_info", "SOC 101", "5", "me@example.com", "new"))

    def test_bad_messages_are_refused(self):
        for fields in ({"kind": "spam"}, {"kind": None}, {"message": "too short"}, {"message": "x" * 2001},
                       {"email": "not an email"}, {"email": "a@b"}, {"email": ("x" * 115) + "@b.com"},
                       {"course": "c" * 21}, {"section": "s" * 11}):
            self.assertEqual(self.support(**fields).status_code, 400, fields)
        self.assertEqual(rows("support_messages"), [])

    def test_every_kind_is_accepted(self):
        for i, kind in enumerate(feedback.SUPPORT_KINDS):
            self.visitor = f"visitor-kind-{i:04d}"
            self.assertEqual(self.support(kind=kind).status_code, 201, kind)


class PrivacyTests(FeedbackCase):
    def test_no_ip_or_user_agent_anywhere(self):
        self.client.post("/api/reviews", json={"rating": 5, "elapsed_ms": 9000, "visitor_id": self.visitor},
                         headers={"User-Agent": "SecretBrowser/1.0", "X-Forwarded-For": "203.0.113.9"})
        self.support()
        conn = sqlite3.connect(FEEDBACK_DB)
        columns = {t: [r[1] for r in conn.execute(f"PRAGMA table_info({t})")] for t in ("reviews", "support_messages")}
        dump = json.dumps([list(r) for t in columns for r in conn.execute(f"SELECT * FROM {t}")])
        conn.close()
        self.assertEqual(columns["reviews"], ["id", "created_at", "rating", "comment", "display_name", "status"])
        self.assertEqual(columns["support_messages"], ["id", "created_at", "kind", "message", "course", "section", "email", "status"])
        for secret in ("SecretBrowser", "203.0.113.9", "127.0.0.1", self.visitor):
            self.assertNotIn(secret, dump)

    def test_tracking_gets_only_the_event_and_kind(self):
        res = self.event("visitor-track-1", "support_submit", {"kind": "wrong_info", "message": "private text"})
        self.assertEqual(res.status_code, 204)
        self.assertEqual(self.event("visitor-track-1", "review_submit", {"comment": "private"}).status_code, 204)
        from test_smoke import stored_events
        stored = [json.loads(e["props"]) for e in stored_events("visitor-track-1")]
        self.assertEqual(stored, [{"kind": "wrong_info"}, {}])


class AdminTests(FeedbackCase):
    def test_off_without_admin_token(self):
        with mock.patch.dict(os.environ, {"ADMIN_TOKEN": ""}):
            for method, url in (("get", "/api/admin/feedback"), ("post", "/api/admin/reviews/1"), ("post", "/api/admin/support/1")):
                self.assertEqual(getattr(self.client, method)(url, headers=AUTH, json={"status": "done"}).status_code, 404, url)

    def test_wrong_token(self):
        for headers in ({"Authorization": "Bearer nope"}, {}, {"Authorization": ADMIN_TOKEN}):
            self.assertEqual(self.client.get("/api/admin/feedback", headers=headers).status_code, 401)
        self.assertEqual(self.client.get(f"/api/admin/feedback?token={ADMIN_TOKEN}").status_code, 401)   # never in the URL

    def test_list_and_change(self):
        self.review(comment="pending one")
        self.support()
        data = self.client.get("/api/admin/feedback?status=pending", headers=AUTH).get_json()
        self.assertEqual([r["comment"] for r in data["reviews"]], ["pending one"])
        self.assertNotIn("support", data)
        new = self.client.get("/api/admin/feedback?status=new", headers=AUTH).get_json()["support"]
        self.assertEqual(len(new), 1)
        res = self.client.post(f"/api/admin/support/{new[0]['id']}", json={"status": "done"}, headers=AUTH)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.client.get("/api/admin/feedback?status=new", headers=AUTH).get_json()["support"], [])
        both = self.client.get("/api/admin/feedback", headers=AUTH).get_json()
        self.assertEqual((len(both["reviews"]), len(both["support"])), (1, 1))
        self.assertEqual(self.client.get("/api/admin/feedback?status=nope", headers=AUTH).status_code, 400)
        self.assertEqual(self.approve(999999).status_code, 404)
        self.assertEqual(self.approve(rows("reviews")[0]["id"], "deleted").status_code, 400)


if __name__ == "__main__":
    unittest.main()

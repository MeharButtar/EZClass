"""The page and support-kind lists live in more than one place. These tests
fail when they drift apart, so a new page can't be silently dropped from the
stats (the server drops a page name it doesn't know, and the browser reports
an unknown page as "home")."""

import os
import re
import unittest

from backend.routes import analytics, feedback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND = os.path.join(ROOT, "frontend")


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def js_list(source, name):
    match = re.search(rf"const {name} = \[([^\]]*)\]", source)
    if not match:
        raise AssertionError(f"{name} not found")
    return re.findall(r'"([^"]+)"', match.group(1))


class PageListTests(unittest.TestCase):
    def test_track_js_views_match_the_server(self):
        views = js_list(read("frontend", "js", "track.js"), "VIEWS")
        self.assertEqual(len(views), len(set(views)), "VIEWS has a duplicate")
        self.assertEqual(set(views), analytics.ALLOWED_VIEWS)

    def test_every_tracked_page_is_in_the_list(self):
        views = set(js_list(read("frontend", "js", "track.js"), "VIEWS"))
        pages = [f for f in os.listdir(FRONTEND) if f.endswith(".html")]
        self.assertIn("index.html", pages)
        for name in pages:
            html = read("frontend", name)
            if "js/track.js" not in html:
                continue   # the 404 page doesn't count visits
            page = re.search(r'<body[^>]*data-page="([^"]+)"', html)
            self.assertIsNotNone(page, f"{name} has no data-page")
            self.assertIn(page.group(1), views, f"{name} (data-page={page.group(1)}) is missing from VIEWS and ALLOWED_VIEWS")

    def test_support_kinds_match(self):
        self.assertEqual(set(feedback.SUPPORT_KINDS), analytics.ALLOWED_KINDS)
        options = re.findall(r'<option value="([^"]+)"', read("frontend", "support.html"))
        self.assertEqual(set(options), analytics.ALLOWED_KINDS)


if __name__ == "__main__":
    unittest.main()

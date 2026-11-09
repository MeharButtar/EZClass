"""
Tests for the keyword and professor search (backend/search.py, /api/sections?q=).

Shares test_smoke's throwaway database (the Spring 2027 data in data/cleaned).
The acceptance counts are for that data; recompute them if it changes.
"""

import sqlite3
import unittest

from test_smoke import CLASS_DB, AppTestCase

from backend.search import load_courses, match_courses, norm, person_match, tokens


def codes(sections):
    """Course codes in result order, each once: ['CS 150', 'CS 150L']"""
    out = []
    for s in sections:
        code = f"{s['subject']} {s['catalog_num']}"
        if code not in out:
            out.append(code)
    return out


class SearchApiCase(AppTestCase):
    def search(self, q=None, **params):
        if q is not None:
            params["q"] = q
        res = self.client.get("/api/sections", query_string=params)
        self.assertEqual(res.status_code, 200, params)
        return res.get_json()

    def assertFinds(self, q, expected_codes, sections=None, **params):
        found = self.search(q, **params)
        self.assertEqual(codes(found), expected_codes, q)
        if sections is not None:
            self.assertEqual(len(found), sections, q)
        return found


class AcceptanceTests(SearchApiCase):
    """The acceptance table, row by row."""

    def test_exact_code_every_way(self):
        for q in ("CS 480", "cs480", "cs-480", "CS 480 ", "CS  480", " cs 480 ", "CS.480", "CS/480", "cs_480"):
            self.assertFinds(q, ["CS 480"], 2)

    def test_number_alone(self):
        self.assertFinds("480", ["AMIND 480", "CS 480", "GENS 480", "MKTG 480"], 11)
        self.assertFinds("150", ["CCS 150", "CS 150", "CS 150L", "CSP 150", "MATH 150", "SLHS 150"], 22)

    def test_subject_alone_is_that_subject_only(self):
        for q in ("CS", "cs"):
            found = self.search(q)
            self.assertEqual(len(found), 73, q)
            self.assertEqual({s["subject"] for s in found}, {"CS"})
            self.assertEqual(len(codes(found)), 41)
        self.assertFinds("csp", ["CSP 150", "CSP 240", "CSP 300", "CSP 420"], 6)
        math = self.search("math")
        self.assertEqual(len(math), 77)
        self.assertEqual({s["subject"] for s in math}, {"MATH"})
        self.assertEqual(len(codes(math)), 14)

    def test_prefixes(self):
        cs4 = ["CS 420", "CS 450", "CS 460", "CS 470", "CS 480", "CS 496", "CS 497", "CS 498", "CS 499"]
        for q in ("CS 4", "cs4"):
            self.assertFinds(q, cs4, 16)
        self.assertFinds("cs48", ["CS 480"], 2)
        for q in ("CS 150", "cs 15"):
            self.assertFinds(q, ["CS 150", "CS 150L"], 6)
        for q in ("CS150L", "cs 150 l"):
            self.assertFinds(q, ["CS 150L"], 4)
        self.assertFinds("BIOL 211", ["BIOL 211", "BIOL 211L"], 10)
        for q in ("BIOL 211L", "biol 211 l", "biol211l"):
            self.assertFinds(q, ["BIOL 211L"], 9)

    def test_subjects_sdsu_writes_with_spaces(self):
        for q in ("GEN S 147", "gens147"):
            self.assertFinds(q, ["GENS 147"], 2)
        for q in ("P A 301", "pa301"):
            self.assertFinds(q, ["PA 301"], 4)            # not GEOL 301 (title words p..., a...)
        self.assertFinds("POL S 102", ["POLS 102"], 15)
        self.assertFinds("MUSIC 351", ["MUSIC 351"], 9)

    def test_title_words(self):
        self.assertFinds("hip hop", ["MUSIC 351", "RELS 356"], 10)   # MUSIC 351's own section titles
        self.assertFinds("Data Science Python", ["CS 200"], 1)
        for q in ("business & diplomacy", "business and diplomacy"):
            self.assertFinds(q, ["MGT 403"], 1)
        intro = self.search("intro to")
        self.assertEqual(len(intro), 153)
        self.assertEqual(len(codes(intro)), 48)              # every course with an active section
        for s in intro:
            words = norm(f"{s['course_title']} {s['section_title'] or ''}").split()
            self.assertTrue(any(w.startswith("intro") for w in words) and any(w.startswith("to") for w in words), s["course_title"])

    def test_cs_and_a_title_word(self):
        found = self.search("cs data")
        self.assertTrue(found)
        self.assertEqual({s["subject"] for s in found}, {"CS"})
        self.assertTrue(all(any(w.startswith("data") for w in norm(s["course_title"]).split()) for s in found))

    def test_no_keyword_filter(self):
        everything = len(self.search())
        self.assertEqual(everything, 2284)
        for q in ("c", "%", "_", "   ", "", "-", "%_%"):
            self.assertEqual(len(self.search(q)), everything, repr(q))

    def test_hostile_text(self):
        for q in ("'; DROP TABLE courses;--", "<script>alert(1)</script>"):
            self.assertEqual(self.search(q), [], q)
        self.assertEqual(len(self.search()), 2284)            # nothing was dropped


class EveryCourseTests(SearchApiCase):
    def test_every_course_finds_itself_first(self):
        conn = sqlite3.connect(CLASS_DB)
        conn.row_factory = sqlite3.Row
        courses = load_courses(conn)
        offered = [r[0] for r in conn.execute("SELECT DISTINCT course_id FROM sections WHERE active = 1")]
        conn.close()
        order = lambda cid: (courses[cid]["subject"], courses[cid]["num"])
        for cid in offered:
            subj, num = courses[cid]["subject"].upper(), courses[cid]["num"].upper()
            for q in (f"{subj} {num}", f"{subj}{num}", f"{subj}-{num}", f"{subj} {num}".lower(), f"{subj}  {num}"):
                ranks = match_courses(courses, q)
                self.assertIn(cid, ranks, q)
                first = min(ranks, key=lambda c: (ranks[c], *order(c)))
                self.assertEqual(first, cid, q)

    def test_every_course_through_the_api_sample(self):
        """The same thing end to end for a spread of courses (the loop above covers all of them)."""
        conn = sqlite3.connect(CLASS_DB)
        rows = conn.execute("""SELECT DISTINCT c.subject, c.catalog_num FROM courses c JOIN sections s ON s.course_id = c.course_id
                               WHERE s.active = 1 ORDER BY c.subject, c.catalog_num""").fetchall()
        conn.close()
        for subj, num in rows[::20]:
            found = self.search(f"{subj.lower()}-{num.lower()}")
            self.assertEqual(codes(found)[0], f"{subj} {num}")


class TextCleaningTests(SearchApiCase):
    def test_tokens(self):
        self.assertEqual(tokens("cs480"), ["cs", "480"])
        self.assertEqual(tokens("biol211l"), ["biol", "211l"])
        self.assertEqual(tokens("GEN S 147"), ["gen", "s", "147"])
        self.assertEqual(tokens("x" * 5000), ["x" * 100])         # capped at 100 characters

    def test_nbsp_and_tab_are_spaces(self):
        for q in ("CS 480", "CS\t480", "cs 480"):
            self.assertFinds(q, ["CS 480"], 2)

    def test_wildcards_and_huge_text_never_break_it(self):
        self.assertEqual(len(self.search("100%")), len(self.search("100")))
        for q in ("%%", "_x_", "a" * 5000, "%" * 5000, "\x00\x01"):
            res = self.client.get("/api/sections", query_string={"q": q})
            self.assertEqual(res.status_code, 200, q[:10])


class ProfessorTests(SearchApiCase):
    def test_name_in_any_order(self):
        base = self.search(professor="Michael Rapp")
        self.assertTrue(base)
        for typed in ("Rapp, Michael", "rapp michael", "M Rapp", "Michael  Rapp", " MICHAEL RAPP "):
            self.assertEqual([s["section_id"] for s in self.search(professor=typed)], [s["section_id"] for s in base], typed)
        # "Rapp" alone also finds the other Rapp (Devin)
        rapp = self.search(professor="Rapp")
        self.assertLess({s["section_id"] for s in base}, {s["section_id"] for s in rapp})
        self.assertEqual({p["last"] for s in rapp for p in s["instructors"] if p["last"].startswith("Rapp")}, {"Rapp"})

    def test_last_comma_first(self):
        # Valerie Alexandra teaches BA 310 1-4; MIS 180 / 380 are Valerie Novikova's, so not here
        found = self.search(professor="Alexandra, Valerie")
        self.assertEqual(codes(found), ["BA 310"])
        self.assertEqual([s["section_number"] for s in found], ["01", "02", "03", "04"])
        self.assertEqual(codes(self.search(professor="Valerie")), ["BA 310", "MIS 180", "MIS 380"])

    def test_person_match(self):
        self.assertTrue(person_match("Michael", "Rapp", "rapp, m"))
        self.assertFalse(person_match("Michael", "Rapp", "app"))           # start of a name, not the middle
        self.assertFalse(person_match("Michael", "Rapp", "%"))
        self.assertEqual(self.search(professor="%"), [])
        self.assertEqual(self.search(professor="'; DROP TABLE professors;--"), [])


class CombinedFilterTests(SearchApiCase):
    def test_keyword_and_day(self):
        found = self.search("cs", day="T")
        self.assertTrue(found)
        self.assertTrue(all(s["subject"] == "CS" for s in found))
        self.assertTrue(all(any(m["day"] and "T" in m["day"].replace("Th", "") for m in s["meetings"]) for s in found))

    def test_keyword_and_ge(self):
        found = self.search("intro", ge="ALL")
        self.assertTrue(found)
        self.assertTrue(all(s["ge_areas"] for s in found))

    def test_keyword_and_subject_dropdown(self):
        found = self.search("intro to", subject="CS")
        self.assertEqual({s["subject"] for s in found}, {"CS"})
        self.assertIn("CS 200", codes(found))
        self.assertEqual(self.search("480", subject="MATH"), [])

    def test_forgiving_subject_parameter(self):
        gens = self.search(subject="GENS")
        self.assertTrue(gens)
        for typed in ("GEN S", "gens", " Gen-S "):
            self.assertEqual(len(self.search(subject=typed)), len(gens), typed)


if __name__ == "__main__":
    unittest.main()

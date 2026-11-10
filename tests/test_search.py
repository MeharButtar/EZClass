"""
Tests for the keyword and professor search (backend/search.py, /api/sections?q=).

Shares test_smoke's throwaway database (the Spring 2027 data in data/cleaned,
from the official schedule export). The acceptance counts are for that data;
recompute them if it changes.
"""

import sqlite3
import unittest

from test_smoke import CLASS_DB, AppTestCase

from backend.search import class_number_query, load_courses, match_courses, norm, person_match, tokens


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
        self.assertFinds("480", ["AMIND 480", "BIOL 480", "CONE 480", "CS 480", "GENS 480", "HTM 480", "JMS 480",
                                 "MKTG 480", "PH 480", "SOC 480"], 17)
        self.assertFinds("150", ["CCS 150", "CS 150", "CS 150L", "CSP 150", "MATH 150", "MATH 150S", "SLHS 150"], 24)

    def test_subject_alone_is_that_subject_only(self):
        for q in ("CS", "cs"):
            found = self.search(q)
            self.assertEqual(len(found), 54, q)
            self.assertEqual({s["subject"] for s in found}, {"CS"})
            self.assertEqual(len(codes(found)), 35)
        csp = self.search("csp")
        self.assertEqual((len(csp), len(codes(csp))), (93, 46))
        self.assertEqual({s["subject"] for s in csp}, {"CSP"})
        self.assertEqual(codes(csp)[:4], ["CSP 150", "CSP 240", "CSP 300", "CSP 320"])
        math = self.search("math")
        self.assertEqual(len(math), 128)
        self.assertEqual({s["subject"] for s in math}, {"MATH"})
        self.assertEqual(len(codes(math)), 48)

    def test_prefixes(self):
        # CS 470, 496 and 497 aren't offered in Spring 2027; 498 and 499 are thesis / special study (skipped)
        cs4 = ["CS 420", "CS 450", "CS 460", "CS 480"]
        for q in ("CS 4", "cs4"):
            self.assertFinds(q, cs4, 9)
        self.assertFinds("cs48", ["CS 480"], 2)
        for q in ("CS 150", "cs 15"):
            self.assertFinds(q, ["CS 150", "CS 150L"], 3)
        for q in ("CS150L", "cs 150 l"):
            self.assertFinds(q, ["CS 150L"], 2)
        self.assertFinds("BIOL 211", ["BIOL 211", "BIOL 211L"], 19)
        for q in ("BIOL 211L", "biol 211 l", "biol211l"):
            self.assertFinds(q, ["BIOL 211L"], 18)

    def test_subjects_sdsu_writes_with_spaces(self):
        for q in ("GEN S 147", "gens147"):
            self.assertFinds(q, ["GENS 147"], 2)
        for q in ("P A 301", "pa301"):
            self.assertFinds(q, ["PA 301"], 3)            # not GEOL 301 (title words p..., a...)
        self.assertFinds("POL S 102", ["POLS 102"], 15)
        self.assertFinds("MUSIC 351", ["MUSIC 351"], 9)

    def test_title_words(self):
        # MUSIC 351's own section title; DANCE 243 and ENS 138 have a Hip Hop section too (every section
        # of the course comes back). RELS 356 isn't offered in Spring 2027.
        self.assertFinds("hip hop", ["DANCE 243", "ENS 138", "MUSIC 351"], 48)
        self.assertFinds("Data Science Python", ["CS 200"], 2)
        for q in ("business & diplomacy", "business and diplomacy"):
            self.assertFinds(q, ["MGT 403"], 1)
        intro = self.search("intro to")
        self.assertEqual(len(intro), 245)
        self.assertEqual(len(codes(intro)), 69)              # every course with an active section
        # a course matches by its title or any of its sections' own titles (ECL 503 has an "Intro to" topic)
        titles = {}
        for s in intro:
            titles.setdefault(s["course_id"], set()).update([s["course_title"], s["section_title"] or ""])
        for course_titles in titles.values():
            words = norm(" ".join(course_titles)).split()
            self.assertTrue(any(w.startswith("intro") for w in words) and any(w.startswith("to") for w in words), course_titles)

    def test_cs_and_a_title_word(self):
        found = self.search("cs data")
        self.assertTrue(found)
        self.assertEqual({s["subject"] for s in found}, {"CS"})
        self.assertTrue(all(any(w.startswith("data") for w in norm(s["course_title"]).split()) for s in found))

    def test_no_keyword_filter(self):
        everything = len(self.search())
        self.assertEqual(everything, 5520)
        for q in ("c", "%", "_", "   ", "", "-", "%_%"):
            self.assertEqual(len(self.search(q)), everything, repr(q))

    def test_hostile_text(self):
        for q in ("'; DROP TABLE courses;--", "<script>alert(1)</script>"):
            self.assertEqual(self.search(q), [], q)
        self.assertEqual(len(self.search()), 5520)            # nothing was dropped


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
        # Valerie Alexandra teaches BA 310 1-14; MIS 180 / 380 are Valerie Novikova's, so not here
        found = self.search(professor="Alexandra, Valerie")
        self.assertEqual(codes(found), ["BA 310"])
        self.assertEqual([s["section_number"] for s in found], [f"{n:02d}" for n in range(1, 15)])
        self.assertEqual(codes(self.search(professor="Valerie")), ["BA 310", "MIS 180", "MIS 380"])

    def test_person_match(self):
        self.assertTrue(person_match("Michael", "Rapp", "rapp, m"))
        self.assertFalse(person_match("Michael", "Rapp", "app"))           # start of a name, not the middle
        self.assertFalse(person_match("Michael", "Rapp", "%"))
        self.assertEqual(self.search(professor="%"), [])
        self.assertEqual(self.search(professor="'; DROP TABLE professors;--"), [])


class ClassNumberSearchTests(SearchApiCase):
    """A 4 or 5 digit query is a class number, the number students register with."""

    def test_class_number_finds_the_section(self):
        found = self.search("5834")
        self.assertEqual(codes(found), ["CS 150"])
        self.assertEqual((found[0]["class_number"], found[0]["section_number"]), ("5834", "01"))

    def test_the_matching_section_comes_first(self):
        found = self.search("5844")                         # CS 160 section 03
        self.assertEqual(codes(found), ["CS 160"])
        self.assertEqual((found[0]["class_number"], found[0]["section_number"]), ("5844", "03"))
        self.assertGreater(len(found), 1)                   # the other CS 160 sections follow

    def test_hash_and_spaces(self):
        for q in ("#5834", " 5834 ", "# 5834", "#5834 "):
            found = self.search(q)
            self.assertEqual((codes(found), found[0]["class_number"]), (["CS 150"], "5834"), q)
        self.assertEqual(class_number_query("#12095"), "12095")
        for q in ("150", "cs150", "123456", "58 34", "5834a", "##5834"):
            self.assertIsNone(class_number_query(q), q)

    def test_unknown_class_number_is_a_normal_no_result_search(self):
        self.assertEqual(self.search("99999"), [])
        self.assertEqual(self.search("#1001"), [])           # the lowest class number is 1002

    def test_three_digits_are_still_course_numbers(self):
        found = self.search("150")
        self.assertIn("CS 150", codes(found))
        self.assertGreater(len(codes(found)), 1)

    def test_every_section_has_its_class_number(self):
        found = self.search("cs")
        self.assertTrue(all(s["class_number"] and s["class_number"].isdigit() for s in found))


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

"""
Tests for scripts/import_catalog_majors.py, fully offline:
the saved Mechanical Engineering page (tests/fixtures/catalog/me_bs.html),
the saved program listing (tests/fixtures/catalog/programs_listing.html),
major ids, and --promote (only ever on temporary copies of data/majors).
"""

import collections
import contextlib
import csv
import importlib.util
import io
import os
import shutil
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(ROOT, "tests", "fixtures", "catalog")
spec = importlib.util.spec_from_file_location("import_catalog_majors",
                                              os.path.join(ROOT, "scripts", "import_catalog_majors.py"))
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


def read_fixture(name):
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return f.read()


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def codes(rows):
    return [f"{r['subject']} {r['catalog_num']}" for r in rows]


class MechanicalEngineeringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.out = os.path.join(cls.tmp, "staging")
        page = os.path.join(FIXTURES, "me_bs.html")
        with contextlib.redirect_stdout(io.StringIO()):
            programs, cls.report = importer.run([(page, read_fixture("me_bs.html"), None)], cls.out,
                                                os.path.join(cls.tmp, "ids.csv"))
        cls.prog = programs[0]
        cls.majors = read_csv(os.path.join(cls.out, "majors.csv"))
        cls.rows = read_csv(os.path.join(cls.out, "major_requirements.csv"))
        cls.groups = collections.OrderedDict()
        for r in cls.rows:
            cls.groups.setdefault((r["section"], r["group_label"]), []).append(r)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_header(self):
        self.assertEqual(self.majors, [{"major_id": "me_bs", "name": "Mechanical Engineering", "degree": "B.S.",
                                        "college": "", "catalog_year": "2026-2027", "status": "coming_soon"}])
        self.assertEqual(self.prog.poid, "12130")
        self.assertEqual(self.prog.major_code, "09101")

    def test_columns_match_the_live_files(self):
        with open(os.path.join(ROOT, "data", "majors", "major_requirements.csv"), encoding="utf-8") as f:
            live_header = f.readline().strip()
        with open(os.path.join(self.out, "major_requirements.csv"), encoding="utf-8") as f:
            self.assertEqual(f.readline().strip(), live_header)
        self.assertTrue(all(r["major_id"] == "me_bs" for r in self.rows))

    def test_only_course_sections_become_rows(self):
        self.assertEqual(list(dict.fromkeys(r["section"] for r in self.rows)),
                         ["Preparation for the Major", "Major", "Professional Electives"])

    def test_preparation_required(self):
        req = self.groups[("Preparation for the Major", "Required")]
        self.assertEqual(codes(req), ["ME 190", "ME 202", "ME 230", "ME 240", "ME 241", "AE 280", "MATH 150",
                                      "MATH 151", "MATH 252", "PHYS 195", "PHYS 195L", "PHYS 196", "PHYS 196L"])
        self.assertTrue(all(r["rule"] == "required" for r in req))
        self.assertEqual(next(r for r in req if r["catalog_num"] == "190")["title"], "Computer-Aided Design")
        self.assertEqual(next(r for r in req if r["catalog_num"] == "190")["units"], "2")

    def test_preparation_pick_one_groups(self):
        picks = {label: codes(rows) for (section, label), rows in self.groups.items()
                 if section == "Preparation for the Major" and rows[0]["rule"] == "choose"}
        self.assertEqual(picks, {
            "M E 200 / A E 200 (same course, pick 1)": ["ME 200", "AE 200"],
            "M E 220 / A E 220 (same course, pick 1)": ["ME 220", "AE 220"],
            "BIOL 100 or BIOL 101 (pick 1)": ["BIOL 100", "BIOL 101"],
            "CHEM 202 or CHEM 200 (pick 1)": ["CHEM 202", "CHEM 200"],
        })
        for label in picks:
            self.assertTrue(all(r["pick_n"] == "1" for r in self.groups[("Preparation for the Major", label)]))

    def test_or_group(self):
        chem = self.groups[("Preparation for the Major", "CHEM 202 or CHEM 200 (pick 1)")]
        self.assertEqual([r["units"] for r in chem], ["4", "5"])
        self.assertTrue(all("Cross-listed" not in r["note"] for r in chem))

    def test_also_listed_as_pair(self):
        statics = self.groups[("Preparation for the Major", "M E 200 / A E 200 (same course, pick 1)")]
        self.assertEqual({r["note"] for r in statics}, {"Cross-listed. Grade of C or better, no Cr/NC"})
        dynamics = self.groups[("Preparation for the Major", "M E 220 / A E 220 (same course, pick 1)")]
        self.assertEqual({r["note"] for r in dynamics}, {"Cross-listed"})

    def test_grade_note_is_the_standard_text(self):
        math150 = next(r for r in self.rows if codes([r]) == ["MATH 150"])
        self.assertEqual(math150["note"], "Grade of C or better, no Cr/NC")
        self.assertEqual(next(r for r in self.rows if codes([r]) == ["MATH 252"])["note"], "")

    def test_major_required(self):
        req = self.groups[("Major", "Required")]
        self.assertEqual(codes(req), ["ME 304", "ME 314", "ME 330", "ME 340", "ME 350", "ME 360", "ME 430",
                                      "ME 452", "ME 490W", "ME 491", "ME 495", "AE 341"])
        writing = [r for r in self.rows if r["catalog_num"] == "490W"]
        self.assertEqual(len(writing), 1)   # once, in the Major list, not again for the writing block
        self.assertEqual(writing[0]["note"], "Satisfies the Graduation Writing Assessment")

    def test_professional_electives_pool(self):
        mech = self.groups[("Professional Electives", "Mechanical Systems")]
        thermal = self.groups[("Professional Electives", "Thermal Systems")]
        self.assertEqual(codes(mech), ["ME 520", "ME 530", "ME 532", "AE 535", "ME 535", "ME 540", "ME 542",
                                       "ME 543", "ME 544", "ME 570", "ME 580", "ME 582", "ME 585"])
        # 544 and 570 are in both lists on the page: kept once, under the first list
        self.assertEqual(codes(thermal), ["ME 450", "ME 552", "ME 554", "ME 555", "ME 556"])
        for r in mech + thermal:
            self.assertEqual((r["rule"], r["pick_units"]), ("pool", "12"))
            self.assertIn("at least 3 units at the 500-level", r["note"])   # the catalog sentence is kept
        self.assertIn("Cross-listed with M E 535", next(r for r in mech if codes([r]) == ["AE 535"])["note"])
        for num in ("544", "570"):
            row = next(r for r in mech if r["catalog_num"] == num)
            self.assertTrue(row["note"].endswith("Also listed under Thermal Systems"), row["note"])
        self.assertEqual(len([r for r in self.rows if r["section"] == "Professional Electives"]), 18)

    def test_professional_electives_on_review_list(self):
        review = " ".join(self.prog.review)
        self.assertIn("'Professional Electives' (under Major) is a rule in words", review)
        self.assertIn("M E 544 is listed under both 'Mechanical Systems' and 'Thermal Systems'", review)
        self.assertIn("M E 570 is listed under both", review)
        self.assertIn("A E 535 / M E 535", review)

    def test_units_check(self):
        checks = {h: (stated, listed, verdict) for h, stated, listed, verdict in self.prog.units_checks}
        self.assertEqual(checks["Preparation for the Major"][:2], ("48-49", "48-49"))
        self.assertTrue(checks["Preparation for the Major"][2].startswith("inside"))
        self.assertEqual(checks["Major"][:2], ("at least 45", "45"))

    def test_major_notes(self):
        notes = collections.defaultdict(str)
        for heading, text in self.prog.notes:
            notes[heading] += " " + text
        self.assertIn("impacted program", notes["Impacted Program"])
        self.assertIn("GPA of 2.7", notes["Impacted Program"])
        self.assertIn("CHEM 202 (or CHEM 200)", notes["Impacted Program"])
        self.assertIn("300-400+", notes["Major Restriction for Registration"])
        self.assertIn("Area 2/5", notes["General Education"])
        self.assertIn("Area 4", notes["General Education"])
        self.assertIn("master plan", notes["Master Plan"])
        self.assertIn("M E 490W", notes["Graduation Writing Assessment Requirement"])

    def test_report(self):
        self.assertIn("| 1 | 51 | 1 |", self.report)
        self.assertIn("### Review list", self.report)
        self.assertIn("**Impacted Program**", self.report)
        with open(os.path.join(self.out, "REPORT.md"), encoding="utf-8") as f:
            self.assertEqual(f.read(), self.report)


class HelperTests(unittest.TestCase):
    def test_split_title(self):
        self.assertEqual(importer.split_title("Mechanical Engineering, B.S."), ("Mechanical Engineering", "B.S.", True))
        self.assertEqual(importer.split_title("Business Administration, Emphasis in Marketing, B.S."),
                         ("Business Administration, Emphasis in Marketing", "B.S.", True))
        self.assertEqual(importer.split_title("Dance, B.F.A.")[1], "B.F.A.")
        self.assertEqual(importer.split_title("Music, Jazz Studies Specialization, B.M.")[1], "B.M.")
        self.assertEqual(importer.split_title("Business Administration, M.B.A.")[1], "")   # a master's
        name, degree, plain = importer.split_title("Nursing, B.S. - Second Bachelor’s Degree")
        self.assertEqual((name, degree, plain), ("Nursing, Second Bachelor’s Degree", "B.S.", False))

    def test_h3_list_asking_for_fewer_units_is_its_own_pool_section(self):
        course = ('<li class="acalog-course"><span><a href="#">{0}&nbsp;-&nbsp;Course {0}</a> '
                  '<strong>Units:</strong> <strong>3</strong></span></li>')
        page = ('<!-- saved from url=(0)https://catalog.sdsu.edu/preview_program.php?catoid=12&poid=1 -->'
                '<h1 id="acalog-page-title">Example, B.A.</h1>'
                '<div class="acalog-core"><h2>Major</h2><ul>' + course.format("EX 300") + '</ul></div>'
                '<div class="acalog-core"><h3>Electives</h3><p>(6 units)</p><ul>'
                + "".join(course.format(f"EX {n}") for n in (400, 410, 420)) + '</ul></div>')
        prog = importer.parse_program(page)
        self.assertEqual([(r["section"], r["group_label"], r["rule"], r["pick_units"], r["_code"]) for r in prog.rows], [
            ("Major", "Required", "required", "", "EX 300"),
            ("Electives", "Electives", "pool", "6", "EX 400"),
            ("Electives", "Electives", "pool", "6", "EX 410"),
            ("Electives", "Electives", "pool", "6", "EX 420"),
        ])
        self.assertTrue(any("own section 'Electives'" in x for x in prog.review))

    def test_propose_id(self):
        self.assertEqual(importer.propose_id("Civil Engineering", "B.S."), "ce_bs")
        self.assertEqual(importer.propose_id("Civil Engineering", "B.S.", full=True), "civil_engineering_bs")
        self.assertEqual(importer.propose_id("Business Administration, Emphasis in Accounting", "B.S."),
                         "ba_accounting_bs")
        self.assertEqual(importer.propose_id("History", "B.A."), "history_ba")

    def test_existing_ids_are_reused_and_never_changed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "ids.csv")
            ids = {"11952": {"poid": "11952", "major_id": "civil_bs", "name": "Civil Engineering", "degree": "B.S."}}
            importer.write_ids(ids, path)
            progs = []
            for poid, name in [("11952", "Civil Engineering"), ("11968", "Computer Engineering"), ("12130", "x")]:
                p = importer.Program("")
                p.poid, p.name, p.degree = poid, name, "B.S."
                progs.append(p)
            log = []
            importer.assign_ids(progs, importer.read_ids(path), log)
            self.assertEqual([p.major_id for p in progs], ["civil_bs", "ce_bs", "me_bs"])
            # a second program whose short id is taken gets the spelled-out one, and the collision is logged
            other = importer.Program("")
            other.poid, other.name, other.degree = "99999", "Chemical Engineering", "B.S."
            importer.assign_ids([other], {p.poid: {"poid": p.poid, "major_id": p.major_id} for p in progs}, log)
            self.assertEqual(other.major_id, "chemical_engineering_bs")
            self.assertTrue(any("collision" in line for line in log))


class DiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.programs, cls.counts = importer.discover(read_fixture("programs_listing.html"))
        cls.titles = [p["title"] for p in cls.programs]

    def test_counts(self):
        self.assertEqual(self.counts["programs"], 653)
        self.assertEqual(self.counts["roadmap"], 184)
        self.assertEqual(len(self.programs), 188)
        self.assertEqual(len({p["poid"] for p in self.programs}), 188)

    def test_about_80_major_names(self):
        names = {t.split(",")[0].strip() for t in self.titles}
        self.assertTrue(70 <= len(names) <= 90, len(names))

    def test_skipped_types(self):
        for title in self.titles:
            self.assertIsNotNone(importer.BACHELOR.search(title), title)
            for bad in ("M.A.", "M.S.", "M.B.A.", "Ph.D.", "Minor", "4+1", "BS/MS", "BA/MS", "Roadmap", "Undeclared"):
                self.assertNotIn(bad, title)

    def test_known_programs_present(self):
        poids = {p["poid"] for p in self.programs}
        self.assertLessEqual(set(importer.KNOWN_IDS), poids)
        self.assertIn("Mechanical Engineering, B.S.", self.titles)
        self.assertIn("Business Administration, Emphasis in Marketing, B.S.", self.titles)

    def test_special_programs_flagged(self):
        self.assertEqual(sum(p["special"] for p in self.programs), 11)

    def test_urls(self):
        me = next(p for p in self.programs if p["poid"] == "12130")
        self.assertEqual(me["url"], "https://catalog.sdsu.edu/preview_program.php?catoid=12&poid=12130")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "urls.txt")
            importer.write_urls(self.programs, path)
            self.assertEqual(importer.read_urls(path), [p["url"] for p in self.programs])

    def test_ids_for_every_program_are_unique(self):
        progs = []
        for p in self.programs:
            prog = importer.Program("")
            prog.poid, prog.name, prog.degree = p["poid"], p["name"], p["degree"]
            progs.append(prog)
        importer.assign_ids(progs, collections.OrderedDict(), [])
        ids = [p.major_id for p in progs]
        self.assertEqual(len(set(ids)), 188)
        self.assertTrue(all(importer.re.fullmatch(r"[a-z0-9_]+", i) for i in ids))
        for poid, known in importer.KNOWN_IDS.items():
            self.assertEqual(next(p.major_id for p in progs if p.poid == poid), known)


class PromoteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.live = os.path.join(self.tmp, "majors")
        shutil.copytree(os.path.join(ROOT, "data", "majors"), self.live,
                        ignore=shutil.ignore_patterns("staging"))
        self.staging = os.path.join(self.tmp, "staging")
        with contextlib.redirect_stdout(io.StringIO()):
            importer.run([("me_bs.html", read_fixture("me_bs.html"), None)], self.staging,
                         os.path.join(self.tmp, "ids.csv"))
        # a staged copy of a live major, to prove promote refuses it
        rows = read_csv(os.path.join(self.staging, "major_requirements.csv"))
        importer.write_csv(os.path.join(self.staging, "major_requirements.csv"), importer.REQ_FIELDS,
                           rows + [dict(rows[0], major_id="cs_bs")])
        majors = read_csv(os.path.join(self.staging, "majors.csv"))
        importer.write_csv(os.path.join(self.staging, "majors.csv"), importer.MAJOR_FIELDS,
                           majors + [dict(majors[0], major_id="cs_bs")])

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def live_files(self):
        return (read_csv(os.path.join(self.live, "majors.csv")),
                read_csv(os.path.join(self.live, "major_requirements.csv")))

    def test_refuses_a_live_major(self):
        before = self.live_files()
        with self.assertRaises(SystemExit) as err:
            importer.promote("cs_bs", self.staging, self.live)
        self.assertIn("Refusing", str(err.exception))
        self.assertEqual(self.live_files(), before)

    def test_fills_the_empty_placeholder_once(self):
        majors_before, rows_before = self.live_files()
        n, placeholder = importer.promote("me_bs", self.staging, self.live)
        self.assertTrue(placeholder)
        majors, rows = self.live_files()
        self.assertEqual(len(majors), len(majors_before))   # replaced in place, not added
        me = next(m for m in majors if m["major_id"] == "me_bs")
        self.assertEqual(me, {"major_id": "me_bs", "name": "Mechanical Engineering", "degree": "B.S.",
                              "college": "", "catalog_year": "2026-2027", "status": "coming_soon"})
        self.assertEqual(len(rows), len(rows_before) + n)
        self.assertEqual(rows[: len(rows_before)], rows_before)   # the live majors' rows are untouched
        self.assertEqual([m for m in majors if m["major_id"] != "me_bs"],
                         [m for m in majors_before if m["major_id"] != "me_bs"])
        # now it has rows, so a second promote is refused
        with self.assertRaises(SystemExit):
            importer.promote("me_bs", self.staging, self.live)

    def test_never_sets_live(self):
        importer.promote("me_bs", self.staging, self.live)
        majors, _ = self.live_files()
        self.assertEqual(next(m for m in majors if m["major_id"] == "me_bs")["status"], "coming_soon")


if __name__ == "__main__":
    unittest.main()

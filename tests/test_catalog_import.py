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
            "ME 200 / AE 200 (same course, pick 1)": ["ME 200", "AE 200"],
            "ME 220 / AE 220 (same course, pick 1)": ["ME 220", "AE 220"],
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
        statics = self.groups[("Preparation for the Major", "ME 200 / AE 200 (same course, pick 1)")]
        self.assertEqual({r["note"] for r in statics}, {"Cross-listed. Grade of C or better, no Cr/NC"})
        dynamics = self.groups[("Preparation for the Major", "ME 220 / AE 220 (same course, pick 1)")]
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
            self.assertNotIn("500-level", r["note"])   # the rule sentence is the section note, not on each row
        self.assertEqual(next(r for r in mech if codes([r]) == ["AE 535"])["note"], "Cross-listed with ME 535")
        for num in ("544", "570"):
            row = next(r for r in mech if r["catalog_num"] == num)
            self.assertTrue(row["note"].endswith("Also listed under Thermal Systems"), row["note"])
        self.assertEqual(len([r for r in self.rows if r["section"] == "Professional Electives"
                              and r["rule"] == "pool"]), 18)

    def test_section_note_row(self):
        notes = [r for r in self.rows if r["rule"] == "note"]
        self.assertEqual([(r["section"], r["group_label"], r["subject"], r["catalog_num"]) for r in notes],
                         [("Professional Electives", "", "", "")])
        self.assertIn("at least 3 units at the 500-level", notes[0]["note"])   # the catalog sentence, once
        first = next(i for i, r in enumerate(self.rows) if r["section"] == "Professional Electives")
        self.assertEqual(self.rows[first]["rule"], "note")   # at the top of its section

    def test_professional_electives_on_review_list(self):
        review = " ".join(self.prog.review)
        self.assertIn("'Professional Electives' (under Major) is a rule in words", review)
        self.assertIn("M E 544 is listed under both 'Mechanical Systems' and 'Thermal Systems'", review)
        self.assertIn("M E 570 is listed under both", review)
        self.assertIn("AE 535 / ME 535", review)

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
        self.assertIn("| 1 | 52 | 1 |", self.report)   # 51 courses + 1 note row
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

    def test_shortened_schedule_titles(self):
        for short, full in [("Intro to Eng Materials", "Introduction to Engineering Materials"),
                            ("Engr Design:Mech Compon", "Engineering Design: Mechanical Components"),
                            ("Mech & Thermal Sys Lab", "Mechanical and Thermal Systems Laboratory"),
                            ("Applicatns Thermodynamics", "Applications of Thermodynamics")]:
            self.assertTrue(importer.is_abbreviation(short, full), short)
        for short, full in [("Senior Projects II", "Engineering Design: Senior Project"),
                            ("Enrgy& Thrm Sys Anal/Dsgn", "Thermal Systems Analysis and Design"),
                            ("Data Structures", "Computer Organization")]:
            self.assertFalse(importer.is_abbreviation(short, full), short)

    def test_propose_id(self):
        pid = importer.propose_id
        self.assertEqual(pid("Civil Engineering", "B.S."), "civil_engineering_bs")
        self.assertEqual(pid("Aerospace Engineering", "B.S."), "aerospace_engineering_bs")
        self.assertEqual(pid("Business Administration, Emphasis in Accounting", "B.S."), "ba_accounting_bs")
        self.assertEqual(pid("History", "B.A."), "history_ba")
        self.assertEqual(pid("Brazilian Studies", "B.A."), "brazilian_studies_ba")
        self.assertEqual(pid("Music, Music Education Specialization", "B.M."), "music_education_bm")
        self.assertEqual(pid("Biology, Emphasis in Marine Biology", "B.S."), "biology_marine_bs")
        self.assertEqual(pid("Public Health, Emphasis in Environmental Health", "B.S."),
                         "public_health_environmental_health_bs")        # only the whole base is dropped
        self.assertEqual(pid("Foods and Nutrition", "B.S."), "foods_nutrition_bs")
        self.assertEqual(pid("Television, Film and New Media, Emphasis in Production", "B.S."),
                         "television_film_new_media_production_bs")
        self.assertEqual(pid("Chemistry, Emphasis in Biochemistry, and Certificate of the American Chemical Society",
                             "B.S."), "chemistry_biochemistry_american_chemical_society_bs")
        self.assertEqual(pid("Biology, in Preparation for the Single Subject Teaching Credential "
                             "in Science/Biological Sciences", "B.S."), "biology_credential_bs")
        long = pid("International Security and Conflict Resolution, Specialization in Environment in the Global "
                   "System and Very Long Words Here", "B.A.")
        self.assertLessEqual(len(long), importer.MAX_ID_LEN)
        self.assertTrue(long.startswith("international_security_conflict_resolution_environment") and long.endswith("_ba"))

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
            # civil_bs is kept as saved, me_bs is a known live id, the new one is in full words
            self.assertEqual([p.major_id for p in progs], ["civil_bs", "computer_engineering_bs", "me_bs"])
            # an id that is already taken is never handed out again
            other = importer.Program("")
            other.poid, other.name, other.degree = "99999", "Computer Engineering", "B.S."
            saved = {p.poid: {"poid": p.poid, "major_id": p.major_id, "name": p.name} for p in progs}
            importer.assign_ids([other], saved, log)
            self.assertEqual(other.major_id, "computer_engineering_bs_2")
            self.assertTrue(any("collision" in line for line in log))

    def test_every_id_fits_the_api_and_the_page(self):
        """ba_management_human_resource_management_bs (42 characters) was refused by the old 40-character limit."""
        api = importlib.util.spec_from_file_location("majors_routes", os.path.join(ROOT, "backend", "routes", "majors.py"))
        with open(api.origin, encoding="utf-8") as f:
            api_pattern = importer.re.search(r'MAJOR_ID_PATTERN = re\.compile\(r"([^"]+)"\)', f.read()).group(1)
        with open(os.path.join(ROOT, "frontend", "js", "store.js"), encoding="utf-8") as f:
            page_patterns = set(importer.re.findall(r"/(\^\[a-z0-9_\]\{1,\d+\}\$)/", f.read()))
        self.assertEqual(len(page_patterns), 1)
        ids = [r["major_id"] for r in read_csv(os.path.join(ROOT, "data", "majors", "majors.csv"))]
        ids += [r["major_id"] for r in importer.read_ids().values()]
        for mid in ids:
            self.assertRegex(mid, api_pattern)
            self.assertRegex(mid, page_patterns.copy().pop())
            self.assertLessEqual(len(mid), importer.MAX_ID_LEN)


class FetcherTests(unittest.TestCase):
    def robots(self, lines):
        parser = importer.urllib.robotparser.RobotFileParser()
        parser.parse(lines)
        return parser

    def test_follows_crawl_delay_and_disallow(self):
        fetcher = importer.Fetcher(robots=self.robots(
            ["User-agent: *", "Disallow: /search_advanced.php", "crawl-delay: 120"]))
        self.assertTrue(fetcher.allowed("https://catalog.sdsu.edu/preview_program.php?catoid=12&poid=12130"))
        self.assertEqual(fetcher.delay, 120)
        self.assertFalse(fetcher.allowed("https://catalog.sdsu.edu/search_advanced.php?catoid=12"))

    def test_disallowed_page_is_never_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            fetcher = importer.Fetcher(cache_dir=tmp, robots=self.robots(["User-agent: *", "Disallow: /"]))
            with self.assertRaises(SystemExit) as err:
                fetcher.get("https://catalog.sdsu.edu/content.php?catoid=12&navoid=1153", "listing.html")
            self.assertIn("robots.txt does not allow", str(err.exception))
            self.assertEqual(os.listdir(tmp), [])

    def test_saved_page_is_reused_without_a_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "page.html"), "w", encoding="utf-8") as f:
                f.write("saved")
            fetcher = importer.Fetcher(cache_dir=tmp, robots=self.robots(["User-agent: *", "Disallow: /"]))
            self.assertEqual(fetcher.get("https://catalog.sdsu.edu/x", "page.html"), "saved")

    def test_bot_challenge_page_is_recognized(self):
        challenge = ('<script src="https://x.token.awswaf.com/challenge.js"></script><script>'
                     'AwsWafIntegration.getToken()</script><noscript>we need to verify that you\'re not a robot.</noscript>')
        self.assertTrue(importer.is_bot_challenge(challenge))
        self.assertFalse(importer.is_bot_challenge(read_fixture("programs_listing.html")))
        self.assertFalse(importer.is_bot_challenge(read_fixture("me_bs.html")))

    def test_user_agent_is_generic(self):
        self.assertEqual(importer.USER_AGENT, "EzClass-catalog-reader")


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
        self.assertTrue(all(len(i) <= importer.MAX_ID_LEN for i in ids))
        self.assertTrue(all(importer.re.fullmatch(r"[a-z0-9_]+", i) for i in ids))
        for poid, known in importer.KNOWN_IDS.items():
            self.assertEqual(next(p.major_id for p in progs if p.poid == poid), known)


class BatchTests(unittest.TestCase):
    """--html-dir on hand-saved pages: matched by what is inside them, checked against a batch list."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.ids = os.path.join(self.tmp, "ids.csv")
        importer.write_ids({"12130": {"poid": "12130", "major_id": "me_bs", "name": "Mechanical Engineering",
                                      "degree": "B.S."}}, self.ids)
        self.expect = [("Mechanical Engineering", "B.S.", "https://catalog.sdsu.edu/preview_program.php?catoid=12&poid=12130"),
                       ("Civil Engineering", "B.S.", "https://catalog.sdsu.edu/preview_program.php?catoid=12&poid=11952")]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def stage(self, pages):
        with contextlib.redirect_stdout(io.StringIO()):
            return importer.run(pages, os.path.join(self.tmp, "out"), self.ids, self.expect)

    def test_matched_by_content_not_file_name(self):
        programs, report = self.stage([("Program__Civil_Engineering.html", read_fixture("me_bs.html"), None)])
        self.assertEqual([p.major_id for p in programs], ["me_bs"])
        self.assertIn("## Batch check: 1 of 2 pages found", report)
        self.assertIn("| 1 | Mechanical Engineering, B.S. | `me_bs` | found |", report)
        self.assertIn("| 2 | Civil Engineering, B.S. | `` | **missing** |", report)

    def test_page_without_a_poid_is_matched_by_its_title(self):
        page = read_fixture("me_bs.html").replace("poid=12130", "poid=x")   # no usable program id left
        programs, report = self.stage([("page.html", page, None)])
        self.assertEqual([(p.poid, p.major_id) for p in programs], [("12130", "me_bs")])
        self.assertIn("matched by its title to poid 12130", report)

    def test_title_that_does_not_match_the_listing_is_flagged(self):
        importer.write_ids({"12130": {"poid": "12130", "major_id": "me_bs", "name": "Civil Engineering",
                                      "degree": "B.S."}}, self.ids)
        programs, _ = self.stage([("page.html", read_fixture("me_bs.html"), None)])
        self.assertTrue(any("differs from the listing" in x for x in programs[0].review))

    def test_bot_check_page_is_skipped(self):
        challenge = "<html><script>AwsWafIntegration.getToken()</script></html>"
        programs, report = self.stage([("blocked.html", challenge, None),
                                       ("me.html", read_fixture("me_bs.html"), None)])
        self.assertEqual(len(programs), 1)
        self.assertIn("a saved bot-check page", report)

    def test_coverage_lists_required_courses_with_sections(self):
        cov = importer.coverage(MechanicalEngineeringTests.prog if hasattr(MechanicalEngineeringTests, "prog")
                                else self.stage([("me.html", read_fixture("me_bs.html"), None)])[0][0],
                                {("MATH", "150"): {"sections": 4, "units": 4, "scheduled": 4}})
        have, missing = cov["required"]
        self.assertEqual(have, [("MATH 150", 4)])
        self.assertIn("M E 190", missing)

    def test_read_expect(self):
        path = os.path.join(ROOT, "scripts", "catalog_batch1_urls.txt")
        batch = importer.read_expect(path)
        self.assertEqual(len(batch), 12)
        self.assertEqual(len({url for _, _, url in batch}), 12)
        ids = importer.read_ids()
        self.assertTrue(all((importer.re.search(r"poid=(\d+)", url).group(1)) in ids for _, _, url in batch))


class PromoteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.live = os.path.join(self.tmp, "majors")
        shutil.copytree(os.path.join(ROOT, "data", "majors"), self.live,
                        ignore=shutil.ignore_patterns("staging"))
        # me_bs as the empty coming_soon placeholder it was before it was promoted (no rows, no degree)
        majors = read_csv(os.path.join(self.live, "majors.csv"))
        importer.write_csv_ending(os.path.join(self.live, "majors.csv"), importer.MAJOR_FIELDS, [
            dict(m, degree="", status="coming_soon") if m["major_id"] == "me_bs" else m for m in majors])
        rows = read_csv(os.path.join(self.live, "major_requirements.csv"))
        importer.write_csv_ending(os.path.join(self.live, "major_requirements.csv"), importer.REQ_FIELDS,
                                  [r for r in rows if r["major_id"] != "me_bs"])
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

class RuleTextTests(unittest.TestCase):
    """Rule sentences seen on the batch 1 pages (Business and engineering), on small made-up pages."""
    COURSE = ('<li class="acalog-course"><span><a href="#">{0}&nbsp;-&nbsp;Course {0}</a> '
              '<strong>Units:</strong> <strong>{1}</strong>{2}</span></li>')
    OR = '<li class="acalog-adhoc"><p>or</p></li>'
    SEP = '<li class="acalog-adhoc"><p>&#160;</p></li>'
    TEXT = '<li><p>{0}</p></li>'

    def course(self, name, units=3, extra=""):
        return self.COURSE.format(name, units, extra)

    def page(self, *blocks):
        body = "".join(f'<div class="acalog-core"><{tag}>{heading}</{tag}>{paras}<ul>{items}</ul></div>'
                       for tag, heading, paras, items in blocks)
        return importer.parse_program('<h1 id="acalog-page-title">Example, B.S.</h1>' + body)

    def test_units_selected_from_list_is_a_pool_in_its_own_section(self):
        prog = self.page(
            ("h2", "Major", "<p>A C (2.0) average or better is required in the courses stipulated here for the "
                            "major. 9 upper division units to include:</p>", self.course("EX 300")),
            ("h3", "Upper Division Major Electives", "<p>6 units selected from:</p>",
             self.course("EX 400") + self.SEP + self.course("EX 404") + self.OR + self.course("EY 405")
             + self.SEP + self.course("EX 410")))
        pool = [r for r in prog.rows if r["rule"] == "pool"]
        self.assertEqual([r["_code"] for r in pool], ["EX 400", "EX 404", "EY 405", "EX 410"])
        self.assertEqual({(r["section"], r["group_label"], r["pick_units"]) for r in pool},
                         {("Upper Division Major Electives", "Upper Division Major Electives", "6")})
        self.assertEqual(next(r for r in pool if r["_code"] == "EX 404")["note"], "Or EY 405")
        self.assertEqual(next(r for r in pool if r["_code"] == "EX 400")["note"], "")   # the counter says it
        self.assertIn(("Major", "A C (2.0) average or better is required in the courses stipulated here for the major."),
                      prog.notes)
        self.assertEqual(prog.units_checks[0][1:], ("9", "9", "inside"))

    def test_subject_range_rule_is_an_open_row(self):
        prog = self.page(
            ("h2", "Major", "<p>3 upper division units to include:</p>", self.course("ACCTG 331")),
            ("h3", "Upper Division Accountancy Electives",
             "<p>6 units of upper division Accounting (ACCTG) courses, excluding ACCTG 325 and ACCTG 326</p>", ""),
            ("h3", "Note", "<p>A “C” (2.0) average or better is required in the courses stipulated here.</p>", ""))
        opened = [r for r in prog.rows if r["rule"] == "open"]
        self.assertEqual([(r["section"], r["group_label"], r["subject"], r["num_min"], r["num_max"], r["pick_units"])
                          for r in opened],
                         [("Upper Division Accountancy Electives", "Any ACCTG 300-599 course", "ACCTG", "300", "599", "6")])
        self.assertIn("excluding ACCTG 325 and ACCTG 326", opened[0]["note"])
        self.assertEqual(opened[0]["exclude"], "ACCTG 325|ACCTG 326")
        self.assertTrue(any("ACCTG 325, ACCTG 326 left out" in x for x in prog.review))
        self.assertFalse(any("'Note'" in x for x in prog.review))     # a Note block is a major note, not a rule

    def test_open_rule_written_inside_a_list(self):
        prog = self.page(("h2", "Major", "", self.course("FIN 321") + self.TEXT.format("and")
                          + self.TEXT.format("Nine units of 300- to 500-level finance courses. Units: 9")))
        opened = [r for r in prog.rows if r["rule"] == "open"]
        self.assertEqual([(r["section"], r["subject"], r["num_min"], r["num_max"], r["pick_units"]) for r in opened],
                         [("Major", "FIN", "300", "599", "9")])
        self.assertTrue(any("read from the department name" in x for x in prog.review))
        self.assertFalse(any("text between courses" in x for x in prog.review))

    def test_select_at_least_one_is_a_pick_one_group(self):
        prog = self.page(("h2", "Engineering Science Elective", "<p>Select at least one of the following courses:</p>",
                          self.course("EX 240") + self.course("EX 204") + self.course("EX 350")))
        self.assertEqual([(r["group_label"], r["rule"], r["pick_n"], r["note"]) for r in prog.rows], [
            ("", "note", "", "Select at least one of the following courses"),   # once, for the section
            ("Engineering Science Elective (pick 1)", "choose", "1", ""),
            ("Engineering Science Elective (pick 1)", "choose", "1", ""),
            ("Engineering Science Elective (pick 1)", "choose", "1", ""),
        ])

    def test_pool_text_is_the_section_note(self):
        prog = self.page(
            ("h2", "Major", "", self.course("EX 300")),
            ("h3", "Upper Division Major Electives", "<p>14 units selected from:</p><p>(6 units may be taken outside "
                                                     "the college by department chair approval)</p>",
             self.course("EX 400", 3, " *") + self.course("EX 410") + self.course("EX 420")
             + self.TEXT.format("* If EX 400 counted for the core, pick a different course.")))
        rows = [r for r in prog.rows if r["section"] == "Upper Division Major Electives"]
        self.assertEqual([(r["rule"], r["note"]) for r in rows], [
            ("note", "(6 units may be taken outside the college by department chair approval)"),
            ("pool", "If EX 400 counted for the core, pick a different course"),   # course-specific: stays
            ("pool", ""), ("pool", ""),
        ])

    def test_rule_sentences_are_kept_and_blurbs_left_out(self):
        prog = self.page(
            ("h2", "Graduation Writing Assessment Requirement",
             "<p>Complete EX 495W with a grade of C (2.0) or better.</p>", ""),
            ("h2", "Major", "<p>Students may pursue pathways. Please visit the department website. "
                            "A C (2.0) average or better is required in the courses stipulated here for the major. "
                            "EX 490 may only be taken after completion of both EX 470 and EX 480. "
                            "EX 491, 492, or 493 may only be taken after completion of EX 371. "
                            "Students intending to pursue the certificate should refer to its requirements.</p>",
             self.course("EX 371") + self.course("EX 490") + self.course("EX 491") + self.course("EX 493")
             + self.course("EX 495W")),
            ("h3", "Note", "<p>A “C” (2.0) average or better is required in the courses stipulated here for the "
                           "major.</p>", ""))
        notes = {r["_code"]: r["note"] for r in prog.rows if r["rule"] != "note"}
        self.assertEqual(notes["EX 490"], "EX 490 may only be taken after completion of both EX 470 and EX 480")
        self.assertEqual(notes["EX 491"], "EX 491, 492, or 493 may only be taken after completion of EX 371")
        self.assertEqual(notes["EX 493"], notes["EX 491"])
        self.assertEqual(notes["EX 371"], "")
        self.assertEqual(notes["EX 495W"], "Satisfies the Graduation Writing Assessment")   # named only in the text
        self.assertEqual([(r["section"], r["note"]) for r in prog.rows if r["rule"] == "note"],
                         [("Major", "A C (2.0) average or better is required in the courses stipulated here for the "
                                    "major")])                                       # once, though written twice
        left_out = " ".join(text for _, text in prog.notes)
        self.assertIn("Please visit the department website", left_out)              # blurbs: report only
        self.assertIn("should refer to its requirements", left_out)

    def groups_of(self, prog):
        out = collections.OrderedDict()
        for r in prog.rows:
            out.setdefault((r["section"], r["group_label"], r["rule"], r["pick_n"], r["pick_units"]), []).append(r["_code"])
        return out

    def test_headings_that_are_the_rule(self):
        prog = self.page(
            ("h2", "Preparation for the Major", "", self.course("EX 100")),
            ("h3", "One of the Following", "", self.course("EX 115") + self.course("EX 119")),
            ("h2", "Major", "<p>A minimum of 18 upper division units to include</p>", self.course("EX 300")),
            ("h3", "A Minimum of 9 Upper Division Units to Include", "", self.course("EX 310") + self.course("EX 320")),
            ("h3", "At Least One Course Selected From", "", self.course("EX 330") + self.course("EX 340")),
            ("h3", "Six Units Selected from", "", self.course("EX 510") + self.course("EX 520") + self.course("EX 530")))
        self.assertEqual(list(self.groups_of(prog).items()), [
            (("Preparation for the Major", "Required", "required", "", ""), ["EX 100"]),
            (("Preparation for the Major", "One of the Following (pick 1)", "choose", "1", ""), ["EX 115", "EX 119"]),
            (("Major", "Required", "required", "", ""), ["EX 300", "EX 310", "EX 320"]),
            (("Major", "At Least One Course Selected From (pick 1)", "choose", "1", ""), ["EX 330", "EX 340"]),
            (("Major Electives", "Major Electives", "pool", "", "6"), ["EX 510", "EX 520", "EX 530"]),
        ])
        self.assertEqual(prog.units_checks[-1][1:3], ("at least 18", "18"))

    def test_emphasis_wrapper_is_read_one_level_up(self):
        prog = self.page(
            ("h2", "Emphasis in Bioengineering", "<p>This program requires 120 units.</p>", ""),
            ("h3", "Preparation for the Major", "<p>(3 units)</p>", self.course("EX 100")),
            ("h3", "Graduation Writing Assessment Requirement", "<p>Complete EX 490W with a grade of C (2.0).</p>", ""),
            ("h3", "Major", "<p>A minimum of 6 upper division units to include:</p>", self.course("EX 300")
             + self.course("EX 490W")),
            ("h4", "Professional Electives", "<p>Three units of additional coursework may be selected from EX 499 "
                                             "(3 units), EX 570, EX 580, and other 400-level courses.</p>", ""))
        self.assertEqual(list(self.groups_of(prog)), [
            ("Preparation for the Major", "Required", "required", "", ""), ("Major", "Required", "required", "", ""),
            ("Professional Electives", "", "note", "", ""),          # the rule sentence, once
            ("Professional Electives", "Professional Electives", "pool", "", "3")])
        pool = [r for r in prog.rows if r["rule"] == "pool"]
        self.assertEqual([(r["_code"], r["units"]) for r in pool], [("EX 499", "3"), ("EX 570", ""), ("EX 580", "")])
        self.assertEqual(next(r for r in prog.rows if r["_code"] == "EX 490W")["note"], importer.GWAR_NOTE)
        self.assertEqual([c[1:3] for c in prog.units_checks], [("3", "3"), ("at least 6", "9")])

    def test_units_per_named_group_and_pick_one_per_group(self):
        prog = self.page(
            ("h2", "Major", "", self.course("EX 300")),
            ("h3", "Three Units Selected From", "<p>Three units from Technical elective A and one unit from "
                                                 "Technical elective B.</p>", ""),
            ("h4", "Technical Elective A", "", self.course("EX 520") + self.course("EX 521")),
            ("h4", "Technical Elective B", "", self.course("EX 499", 1)),
            ("h3", "Breadth", "<p>All majors must complete three courses; one course selected from Groups I and II:</p>",
             ""),
            ("h4", "Group I", "", self.course("EX 340") + self.OR + self.course("EX 344")),
            ("h4", "Group II", "", self.course("EX 351") + self.course("EX 352")),
            ("h4", "Group III", "<p>Satisfied by major core courses.</p>", ""))
        groups = self.groups_of(prog)
        self.assertIn(("Technical Elective A", "Technical Elective A", "pool", "", "3"), groups)
        self.assertIn(("Technical Elective B", "Technical Elective B", "pool", "", "1"), groups)
        self.assertEqual(groups[("Breadth", "Group I (pick 1)", "choose", "1", "")], ["EX 340", "EX 344"])
        self.assertEqual(groups[("Breadth", "Group II (pick 1)", "choose", "1", "")], ["EX 351", "EX 352"])
        breadth = next(r for r in prog.rows if r["section"] == "Breadth" and r["rule"] == "note")["note"]
        self.assertTrue(breadth.startswith("All majors must complete three courses"))   # the rule first
        self.assertIn("Group III: Satisfied by major core courses", breadth)
        self.assertFalse(any("encoded as one pool" in x for x in prog.review))

    def test_a_list_under_a_pool_joins_it(self):
        prog = self.page(
            ("h2", "Major", "", self.course("EX 300")),
            ("h3", "Electives", "<p>18 units selected from:</p>", self.course("EX 421") + self.course("EX 422")),
            ("h4", "3 units may also be selected from:", "", self.course("EX 371") + self.course("EX 415")),
            ("h3", "Capstone", "", self.course("EX 495")))
        groups = self.groups_of(prog)
        self.assertEqual(groups[("Electives", "Electives", "pool", "", "18")], ["EX 421", "EX 422"])
        self.assertEqual(groups[("Electives", "3 units may also be selected from", "pool", "", "18")],
                         ["EX 371", "EX 415"])
        self.assertEqual({r["note"] for r in prog.rows if r["_code"] in ("EX 371", "EX 415")},
                         {"3 units may also be selected from"})
        self.assertIn(("Major", "Capstone", "required", "", ""), groups)            # the pool ends with its level

    def test_whole_prep_list_is_a_pool_and_recommended_is_not_required(self):
        prog = self.page(
            ("h2", "Preparation for the Major", "<p>(9 units) General Education Oral Communication requirement "
                                                "(3 units) and 6 units selected from:</p>",
             self.course("EX 160") + self.course("EX 201") + self.course("EX 204")),
            ("h3", "Recommended", "", self.course("EX 197") + self.course("EX 197L", 1)),
            ("h2", "Language Requirement", "<p>Competency is required in one language other than English.</p>", ""))
        self.assertEqual(list(self.groups_of(prog)), [
            ("Preparation for the Major", "", "note", "", ""),
            ("Preparation for the Major", "Choose from these courses", "pool", "", "6"),
            ("Language Requirement", "", "note", "", "")])
        notes = {r["section"]: r["note"] for r in prog.rows if r["rule"] == "note"}
        self.assertIn("Recommended (not required): EX 197, EX 197L", notes["Preparation for the Major"])
        self.assertEqual(notes["Language Requirement"], "Competency is required in one language other than English")

    def test_open_rules_in_words_and_pairs_of_courses(self):
        prog = self.page(
            ("h2", "Preparation for the Major", "", self.course("EX 200") + self.SEP + self.course("BIOL 203")
             + self.TEXT.format("and") + self.course("BIOL 203L", 1) + self.OR + self.course("BIOL 204")
             + self.TEXT.format("and") + self.course("BIOL 204L", 1)),
            ("h2", "Major", "<p>A minimum of 24 upper division units in chemistry to include</p>",
             self.course("CHEM 410A") + self.TEXT.format("Seven units of electives in chemistry")),
            ("h3", "Upper Division Major Electives", "<p>An additional 5-6 elective units selected from 300- to "
                                                     "500-level Psychology courses to satisfy the 31 units required."
                                                     "</p>", ""),
            ("h3", "Professional Electives", "<p>9 units selected from upper division psychology courses.</p>", ""),
            ("h4", "Area One", "", self.course("PSY 480")))
        groups = self.groups_of(prog)
        self.assertEqual(groups[("Preparation for the Major", "BIOL 203 and BIOL 203L, or BIOL 204 and BIOL 204L",
                                 "choose", "2", "4")], ["BIOL 203", "BIOL 203L", "BIOL 204", "BIOL 204L"])
        prep = [r for r in prog.rows if r["section"] == "Preparation for the Major"]
        self.assertEqual(importer.listed_units(prep), (7, 7))   # EX 200 (3) + one pair (4), not 3 + 2
        opened = [(r["section"], r["subject"], r["num_min"], r["num_max"], r["pick_units"]) for r in prog.rows
                  if r["rule"] == "open"]
        self.assertEqual(opened, [("Major", "CHEM", "300", "599", "7"),
                                  ("Upper Division Major Electives", "PSY", "300", "599", "5-6")])
        self.assertIn(("Professional Electives", "Area One", "pool", "", "9"), groups)   # lists follow: not open

    def test_competency_sequences_writing_course_and_ge_units(self):
        """Communication, B.A.: Prep '(9 units)' is 3 GE units with no course plus 6 from a list; the math
        competency is all of one statistics sequence; the writing course is outside the major's lists."""
        prog = self.page(
            ("h2", "Preparation for the Major", "<p>(9 units) General Education Oral Communication requirement "
                                                "(3 units) and 6 units selected from:</p>",
             self.course("EX 160") + self.course("EX 201") + self.course("EX 204")),
            ("h2", "Mathematics Competency Requirement",
             "<p>Competency in mathematics is generally satisfied by completing three semesters of college "
             "mathematics. or Students interested in a statistics sequence may choose from one of the following two "
             "statistics sequences approved for the major.</p>",
             self.course("STAT 250") + self.course("STAT 350A") + self.course("STAT 350B") + self.OR
             + self.TEXT.format("(highly recommended)") + self.course("SOC 201", 3, " *") + self.course("SOC 406", 3, " *")
             + self.course("SOC 407", 3, " *")),
            ("h3", "Note", "<p>*Additional prerequisites required.</p>", ""),
            ("h2", "Graduation Writing Assessment Requirement",
             "<p>Complete RWS 305W or PSFA 305W (recommended) and earn a grade of C (2.0) or better.</p>",
             self.course("RWS 305W") + self.OR + self.course("PSFA 305W", 3, " (Recommended)")),
            ("h2", "Major", "<p>A minimum of 6 upper division units to include:</p>",
             self.course("EX 300") + self.course("EX 350")))
        groups = self.groups_of(prog)
        seq = "STAT 250, STAT 350A and STAT 350B, or SOC 201, SOC 406 and SOC 407"
        self.assertEqual(groups[("Mathematics Competency Requirement", seq, "choose", "3", "0")],
                         ["STAT 250", "STAT 350A", "STAT 350B", "SOC 201", "SOC 406", "SOC 407"])
        notes = {r["_code"]: r["note"] for r in prog.rows if r["rule"] != "note"}
        self.assertEqual(notes["STAT 250"], "")
        self.assertEqual(notes["SOC 406"], "Highly recommended sequence. Additional prerequisites required")
        section_notes = {r["section"]: r["note"] for r in prog.rows if r["rule"] == "note"}
        self.assertIn("three semesters of college mathematics", section_notes["Mathematics Competency Requirement"])
        self.assertIn("Take all the courses of one sequence", section_notes["Mathematics Competency Requirement"])
        self.assertEqual(groups[("Graduation Writing Assessment Requirement", "RWS 305W or PSFA 305W (pick 1)",
                                 "choose", "1", "0")], ["RWS 305W", "PSFA 305W"])
        self.assertEqual(notes["PSFA 305W"], "Grade of C or better. Recommended")
        checks = {h: (s, l, v) for h, s, l, v in prog.units_checks}
        self.assertEqual(checks["Preparation for the Major"][:2], ("9", "6"))
        self.assertTrue(checks["Preparation for the Major"][2].startswith("short by 3: a General Education"))
        self.assertEqual(checks["Major"][:2], ("at least 6", "6"))   # the competency and writing units are not in it

    def test_grade_text_and_footnote_right_under_a_course(self):
        prog = self.page(("h2", "Preparation for the Major", "",
                          self.course("EX 200", 3, " (must be completed with a grade of C (2.0) or better) "
                                                   "(cannot be taken for credit/no credit (Cr/NC))")
                          + self.course("EX 280", 4) + self.TEXT.format("° A statistics course from another "
                                                                         "department will be accepted.")
                          + self.course("EX 319", 3, " Must be completed with a grade of C (2. 0) or higher better.")))
        notes = {r["_code"]: r["note"] for r in prog.rows}
        self.assertEqual(notes, {"EX 200": "Grade of C or better, no Cr/NC",
                                 "EX 280": "A statistics course from another department will be accepted",
                                 "EX 319": "Grade of C or better"})

    def open_groups(self, prog):
        out = collections.OrderedDict()
        for r in prog.rows:
            if r["rule"] == "open":
                out.setdefault((r["section"], r["group_label"]), []).append(
                    (r["subject"], r["catalog_num"], r["num_min"], r["num_max"], r["exclude"], r["pick_n"],
                     r["pick_units"]))
        return out

    def test_list_plus_any_level_course_is_one_open_group(self):
        """Chem Biochem: '8 units selected from:' a list and 'Any 500-level chemistry course'."""
        prog = self.page(
            ("h2", "Major", "", self.course("CHEM 410A")),
            ("h3", "Upper Division Major Electives", "<p>8 units selected from:</p>",
             self.course("CHEM 496") + self.course("BIOL 350") + self.course("CHEM 520")
             + self.TEXT.format("Any 500-level chemistry course")))
        self.assertEqual(self.open_groups(prog), {("Upper Division Major Electives", "Upper Division Major Electives"): [
            ("CHEM", "", "500", "599", "", "", "8"),
            ("CHEM", "496", "", "", "", "", ""), ("BIOL", "350", "", "", "", "", "")]})   # CHEM 520 is in the range

    def test_range_with_extra_courses_and_a_cap(self):
        """Political Science: any upper division POL S except 390W, plus up to 3 units from a list."""
        prog = self.page(("h2", "Major Electives",
                          "<p>The major requires 12 units of major electives, which may come from any SDSU "
                          "upper-division political science courses (except POL S 390W ).</p>"
                          "<p>Students may optionally take up to three units toward the 12 units of major electives "
                          "from one of:</p>", self.course("AFRAS 321") + self.course("WGSS 375")))
        groups = self.open_groups(prog)
        [(key, rows)] = groups.items()
        self.assertEqual(rows, [("POLS", "", "300", "599", "POLS 390W", "", "12"),
                                ("AFRAS", "321", "", "", "", "", ""), ("WGSS", "375", "", "", "", "", "")])
        first = next(r for r in prog.rows if r["rule"] == "open")
        self.assertIn("up to three units", first["note"])                      # the cap, under the group

    def test_electives_excluding_a_list(self):
        prog = self.page(
            ("h2", "Major", "<p>A minimum of 9 upper division units to include</p>", self.course("MATH 320")),
            ("h4", "Six Units of Electives in Computer Science, Mathematics, or Statistics", "<p>Excluding:</p>",
             self.course("MATH 303") + self.course("MATH 312")))
        self.assertEqual(list(self.open_groups(prog).values()),
                         [[("MATH|CS|STAT", "", "300", "599", "MATH 303|MATH 312", "", "6")]])
        self.assertEqual(prog.units_checks[0][1:3], ("at least 9", "9"))

    def test_groups_with_their_own_units_and_the_rest_open(self):
        """Journalism: 15 units of JMS or LDT; at least 3 and at least 6 units from two lists."""
        prog = self.page(
            ("h2", "Major", "<p>A minimum of 18 upper division units to include:</p>", self.course("JMS 300")),
            ("h3", "And 15 Units of Upper Division Coursework", "<p>Fifteen units of upper division coursework in "
                                                                "either journalism and media studies or learning design "
                                                                "and technology.</p>", ""),
            ("h4", "Critical Courses", "<p>At least three units must be taken from the following list of courses.</p>",
             self.course("JMS 416") + self.course("JMS 450")),
            ("h4", "Skills Courses", "<p>At least six units must be taken from the following list of courses.</p>",
             self.course("JMS 415") + self.course("JMS 418")))
        groups = self.groups_of(prog)
        self.assertIn(("Critical Courses", "Critical Courses", "pool", "", "3"), groups)
        self.assertIn(("Skills Courses", "Skills Courses", "pool", "", "6"), groups)
        self.assertEqual(list(self.open_groups(prog).values()), [[("JMS|LDT", "", "300", "599", "", "", "6")]])
        self.assertEqual(prog.units_checks[-1][1:3], ("at least 18", "18"))

    def test_single_subject_electives_in_words(self):
        prog = self.page(
            ("h2", "Major", "<p>Complete 18 units of core requirements listed below and 12 units of upper division "
                            "sociology electives. (30 units)</p>",
             self.course("SOC 301") + self.course("SOC 401") + self.course("SOC 403") + self.course("SOC 406")
             + self.course("SOC 433") + self.course("SOC 450")),
            ("h3", "Upper Division Major Electives", "<p>18 additional units of upper division Economics (ECON) "
                                                     "electives.</p>", ""))
        self.assertEqual(list(self.open_groups(prog).values()),
                         [[("SOC", "", "300", "599", "", "", "12")], [("ECON", "", "300", "599", "", "", "18")]])
        self.assertEqual(len([r for r in prog.rows if r["rule"] == "required"]), 6)   # the core stays required
        self.assertEqual(prog.units_checks[0][1:3], ("30", "48"))

    def test_more_pick_and_pool_wordings(self):
        prog = self.page(
            ("h2", "Preparation for the Major", "", self.course("ECON 101")),
            ("h3", "Calculus", "<p>One course (3-4 units) selected from:</p>",
             self.course("MATH 120") + self.course("MATH 124", 4)),
            ("h3", "And One Course Selected From", "", self.course("CS 150") + self.TEXT.format("and")
             + self.course("CS 150L", 1) + self.SEP + self.OR + self.course("CS 200", 4) + self.OR + self.course("STAT 200")),
            ("h2", "Major", "", self.course("CFD 335")),
            ("h3", "And Two Units from", "", self.course("CFD 378A", 1) + self.course("CFD 378B", 1)),
            ("h3", "Electives", "<p>6 units selected with the approval of the advisor from:</p>",
             self.course("FN 407") + self.course("FN 409")),
            ("h3", "Variable Unit Courses", "<p>Courses listed below may be applied to the major with department "
                                            "approval.</p>", self.course("ECON 496")),
            ("h3", "Maximum Units", "<p>Maximum nine units of ECON 496 may be substituted.</p>", ""))
        groups = self.groups_of(prog)
        self.assertIn(("Preparation for the Major", "Calculus (pick 1)", "choose", "1", ""), groups)
        self.assertEqual(groups[("Preparation for the Major", "CS 150 and CS 150L, or CS 200, or STAT 200", "choose",
                                 "1", "3")], ["CS 150", "CS 150L", "CS 200", "STAT 200"])
        self.assertIn(("Major Electives", "Major Electives", "pool", "", "2"), groups)       # 'And Two Units from'
        self.assertIn(("Electives", "Electives", "pool", "", "6"), groups)
        self.assertFalse(any(r["_code"] == "ECON 496" for r in prog.rows))                  # approval only: a note
        notes = " ".join(r["note"] for r in prog.rows if r["rule"] == "note")
        self.assertIn("ECON 496", notes)
        self.assertIn("Maximum nine units", notes)

    def test_pick_labels_use_the_app_codes(self):
        prog = self.page(("h2", "Preparation for the Major", "",
                          self.course("CIV E 160") + self.OR + self.course("STAT 250")))
        self.assertEqual({r["group_label"] for r in prog.rows}, {"CIVE 160 or STAT 250 (pick 1)"})

    def test_grade_rules_and_footnotes(self):
        prog = self.page(
            ("h2", "Preparation for the Major", "<p>(7 units)</p><p>These courses cannot be taken for credit/no "
                                                "credit (Cr/NC).</p>",
             self.course("EX 100", 1) + self.course("EX 200", 3, " must be completed with a grade C- (1.7) or better.")
             + self.course("EX 210", 3, " must be completed with a grade of C (2.0) or better.")),
            ("h2", "Major", "", self.course("EX 363", 3, " *") + self.TEXT.format("*No design component.")))
        notes = {r["_code"]: r["note"] for r in prog.rows}
        self.assertEqual(notes, {"EX 100": "No Cr/NC", "EX 200": "Grade of C- or better, no Cr/NC",
                                 "EX 210": "Grade of C or better, no Cr/NC", "EX 363": "No design component"})
        self.assertEqual(prog.review, [])

    def test_lab_electives_are_their_own_pool(self):
        prog = self.page(
            ("h2", "Major", "<p>A minimum of 10 upper division units to include the following courses.</p>",
             self.course("EX 300", 2) + self.course("EX 310", 3)),
            ("h3", "Professional Electives", "<p>3 units selected from upper division example courses with no more "
                                             "than 3 units from other subjects or approved upper division courses "
                                             "from other departments. Example laboratory electives: 2 units selected "
                                             "from any non-required example laboratory courses.</p>", ""),
            ("h4", "Area One", "", self.course("EX 480") + self.course("EX 380L", 1)),
            ("h4", "Area Two", "", self.course("EY 502") + self.course("EX 430L", 1)))
        pools = {(r["section"], r["group_label"], r["pick_units"], r["_code"], r["note"]) for r in prog.rows
                 if r["rule"] == "pool"}
        limit = "No more than 3 units from other subjects or approved courses from other departments"
        self.assertEqual([(r["section"], r["note"]) for r in prog.rows if r["rule"] == "note"],
                         [("Professional Electives", limit)])
        self.assertEqual(pools, {
            ("Professional Electives", "Area One", "3", "EX 480", ""),
            ("Professional Electives", "Area Two", "3", "EY 502", ""),
            ("Laboratory Electives", "Laboratory Electives", "2", "EX 380L", ""),
            ("Laboratory Electives", "Laboratory Electives", "2", "EX 430L", ""),
        })
        self.assertEqual(prog.units_checks[0][1:], ("at least 10", "10", "inside"))
        self.assertFalse(any("encoded as one pool" in x for x in prog.review))

    def test_business_grade_paragraph(self):
        prog = self.page(("h2", "Preparation for the Major",
                          "<p>These prerequisite courses may not be taken Cr/NC; the minimum grade in each class is C "
                          "(2.0). Additional progress requirements must be met before a student is admitted to the "
                          "upper division major.</p><p>Complete with a grade of C (2.0) or better:</p>",
                          self.course("EX 201") + self.SEP + self.course("EX 119") + self.OR
                          + self.course("EY 201", 3, " But not both.")))
        self.assertEqual({r["note"] for r in prog.rows if r["rule"] != "note"}, {"Grade of C or better, no Cr/NC"})
        self.assertEqual([r["note"] for r in prog.rows if r["rule"] == "note"],   # a rule: kept, once
                         ["Additional progress requirements must be met before a student is admitted to the upper "
                          "division major"])
        self.assertEqual(prog.review, [])



if __name__ == "__main__":
    unittest.main()

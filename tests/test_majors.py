"""
Tests for the majors data: the loader (subject normalization, courses with no
sections, adding majors to an older database), GET /api/majors, the
requirement tree, the /api/courses lookup for open rules, the new
/api/sections filters, and the major_select / plan_create analytics events.

Shares test_smoke's throwaway databases: the app can only be imported once per
run, and test_smoke sets the paths before it does.
"""

import contextlib
import io
import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from unittest import mock

from test_smoke import ADMIN_TOKEN, CLASS_DB, AppTestCase, stored_events

from backend.models import db
from backend.routes import majors as majors_routes


@contextlib.contextmanager
def scratch_db(drop_majors=False):
    """A copy of the test class database that db.py and the routes use while the block runs."""
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        path = os.path.join(tmp, "copy.db")
        shutil.copy(CLASS_DB, path)
        if drop_majors:
            conn = sqlite3.connect(path)
            conn.executescript("DROP TABLE major_requirements; DROP TABLE majors;")
            conn.close()
        with mock.patch.object(db, "DB_PATH", path), contextlib.redirect_stdout(io.StringIO()):
            yield path


MAJORS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "majors")


def csv_rows(name):
    """The rows of data/majors/<name>: what the loader must bring in, whatever majors are live."""
    import csv
    with open(os.path.join(MAJORS_DIR, name), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def count(path, sql, *params):
    conn = sqlite3.connect(path)
    try:
        return conn.execute(sql, params).fetchone()[0]
    finally:
        conn.close()


def write_csv(folder, name, text):
    with open(os.path.join(folder, name), "w", encoding="utf-8", newline="") as f:
        f.write(text)


class LoaderTests(unittest.TestCase):
    def test_normalize_subject(self):
        self.assertEqual(db.normalize_subject("POL S"), "POLS")
        self.assertEqual(db.normalize_subject(" b a "), "BA")
        self.assertEqual(db.normalize_subject("AFRAS"), "AFRAS")

    def test_real_majors_loaded_on_first_start(self):
        self.assertEqual(count(CLASS_DB, "SELECT COUNT(*) FROM majors"), len(csv_rows("majors.csv")))
        self.assertEqual(count(CLASS_DB, "SELECT COUNT(*) FROM major_requirements"),
                         len(csv_rows("major_requirements.csv")))
        self.assertEqual(count(CLASS_DB, "SELECT COUNT(*) FROM major_requirements WHERE subject LIKE '% %'"), 0)
        # catalog numbers stay text
        self.assertEqual(count(CLASS_DB, "SELECT COUNT(*) FROM major_requirements WHERE catalog_num = '150L'"), 1)

    def test_spaces_normalized_and_unmatched_course_still_loads(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder, scratch_db() as path:
            write_csv(folder, "majors.csv", "major_id,name,degree,college,catalog_year,status\n"
                                            "test_ma,Test Major,B.A.,,2026-2027,live\n")
            write_csv(folder, "major_requirements.csv",
                      "major_id,section,group_label,rule,pick_n,pick_units,subject,catalog_num,num_min,num_max,title,units,note\n"
                      "test_ma,Preparation for the Major,Required,required,,,POL S,102,,,Gov,3,\n"
                      "test_ma,Preparation for the Major,Required,required,,,zz z,999,,,Made Up,3,\n"
                      "test_ma,Electives,Business,open,,6,b a|acctg,,400,599,,,\n"
                      "nope,Major,Required,required,,,CS,150,,,Unknown major row,3,\n")
            db.load_majors(folder)
            conn = sqlite3.connect(path)
            rows = conn.execute("SELECT subject, catalog_num FROM major_requirements ORDER BY id").fetchall()
            conn.close()
            self.assertEqual(rows, [("POLS", "102"), ("ZZZ", "999"), ("BA|ACCTG", None)])

            tree = self.client_get("/api/majors/test_ma/requirements").get_json()
            courses = tree["sections"][0]["groups"][0]["courses"]
            self.assertTrue(courses[0]["has_sections"])           # POL S 102 matched POLS 102
            self.assertEqual(courses[1]["code"], "ZZZ 999")         # no such course, still listed
            self.assertFalse(courses[1]["has_sections"])
            self.assertEqual(courses[1]["section_count"], 0)

    def test_exclude_list_and_section_note_rows(self):
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as folder, scratch_db():
            write_csv(folder, "majors.csv", "major_id,name,degree,college,catalog_year,status\n"
                                            "test_ac,Test Accounting,B.S.,,2026-2027,live\n")
            write_csv(folder, "major_requirements.csv",
                      "major_id,section,group_label,rule,pick_n,pick_units,subject,catalog_num,num_min,num_max,"
                      "exclude,title,units,note\n"
                      "test_ac,Major,Required,required,,,ACCTG,331,,,,Intermediate,3,\n"
                      "test_ac,Electives,,note,,,,,,,,,,Six units outside the college need approval\n"
                      "test_ac,Electives,Any ACCTG 300-599 course,open,,6,ACCTG,,300,599,acctg 325|CIV E 160,,,"
                      "\"6 units of ACCTG, excluding ACCTG 325\"\n")
            db.load_majors(folder)
            tree = self.client_get("/api/majors/test_ac/requirements").get_json()
            electives = tree["sections"][1]
            self.assertEqual(tree["sections"][0]["note"], None)
            self.assertEqual(electives["note"], "Six units outside the college need approval")   # once, on the section
            self.assertEqual([g["label"] for g in electives["groups"]], ["Any ACCTG 300-599 course"])  # no note group
            self.assertEqual(electives["groups"][0]["open"],
                             {"subjects": ["ACCTG"], "min": 300, "max": 599, "exclude": ["ACCTG 325", "CIVE 160"]})

    def test_database_from_before_the_exclude_column_gets_majors_reloaded(self):
        with scratch_db() as path:
            conn = sqlite3.connect(path)
            columns = [r[1] for r in conn.execute("PRAGMA table_info(major_requirements)") if r[1] != "exclude"]
            conn.executescript(f"""
                CREATE TABLE old_reqs AS SELECT {', '.join(columns)} FROM major_requirements;
                DROP TABLE major_requirements;
                ALTER TABLE old_reqs RENAME TO major_requirements;
                INSERT INTO students (first_name, last_name) VALUES ('Keep', 'Me');""")
            conn.commit()
            conn.close()
            self.assertTrue(db.majors_need_upgrade())
            db.ensure_database()
            self.assertFalse(db.majors_need_upgrade())
            self.assertEqual(count(path, "SELECT COUNT(*) FROM major_requirements"),
                             len(csv_rows("major_requirements.csv")))
            self.assertEqual(count(path, "SELECT COUNT(*) FROM students WHERE first_name = 'Keep'"), 1)
            self.assertEqual(count(path, "SELECT exclude FROM major_requirements WHERE major_id = 'ba_accounting_bs' "
                                         "AND rule = 'open'"), "ACCTG 325|ACCTG 326")

    def test_missing_majors_folder_is_not_an_error(self):
        with scratch_db(drop_majors=True):
            db.load_majors(os.path.join(CLASS_DB, "no-such-folder"))
            self.assertEqual(self.client_get("/api/majors").get_json(), [])
            self.assertEqual(self.client_get("/api/majors/cs_bs/requirements").status_code, 404)

    def test_older_database_gets_majors_without_losing_sections(self):
        with scratch_db(drop_majors=True) as path:
            conn = sqlite3.connect(path)
            conn.execute("INSERT INTO students (first_name, last_name) VALUES ('Keep', 'Me')")
            conn.commit()
            conn.close()
            db.ensure_database()
            self.assertEqual(count(path, "SELECT COUNT(*) FROM majors"), len(csv_rows("majors.csv")))
            self.assertEqual(count(path, "SELECT COUNT(*) FROM sections"), 7813)
            self.assertEqual(count(path, "SELECT COUNT(*) FROM students WHERE first_name = 'Keep'"), 1)
            db.ensure_database()   # second start: nothing doubles
            self.assertEqual(count(path, "SELECT COUNT(*) FROM major_requirements"),
                             len(csv_rows("major_requirements.csv")))

    def client_get(self, url):
        from test_smoke import app_module
        return app_module.app.test_client().get(url)


class MajorsApiTests(AppTestCase):
    def tree(self, major_id):
        res = self.client.get(f"/api/majors/{major_id}/requirements")
        self.assertEqual(res.status_code, 200)
        return res.get_json()

    @staticmethod
    def group(tree, label):
        for section in tree["sections"]:
            for group in section["groups"]:
                if group["label"] == label:
                    return group
        raise AssertionError(f"no group {label!r}")

    def test_list_majors(self):
        majors = self.client.get("/api/majors").get_json()
        self.assertEqual(len(majors), len(csv_rows("majors.csv")))
        self.assertEqual(set(majors[0]), {"major_id", "name", "degree", "status"})
        by_id = {m["major_id"]: m for m in majors}
        self.assertEqual(by_id["cs_bs"]["status"], "live")
        self.assertEqual({k: m["status"] for k, m in by_id.items()},
                         {m["major_id"]: m["status"] for m in csv_rows("majors.csv")})

    def test_cs_tree(self):
        tree = self.tree("cs_bs")
        self.assertEqual(tree["major"]["name"], "Computer Science")
        self.assertEqual([s["name"] for s in tree["sections"]][:2], ["Preparation for the Major", "Major"])
        prep = self.group(tree, "Required")
        self.assertEqual(prep["rule"], "required")
        self.assertEqual(prep["note"], "Grade of C or better, no Cr/NC")   # shared note moved to the group
        codes = {c["code"]: c for c in prep["courses"]}
        self.assertTrue(codes["CS 150"]["has_sections"])
        self.assertGreater(codes["CS 150"]["section_count"], 0)
        self.assertIsNotNone(codes["CS 150"]["course_id"])
        self.assertTrue(codes["PHYS 195"]["has_sections"])
        self.assertEqual(codes["STAT 250"]["ge_areas"], ["2"])
        total = sum(len(g["courses"]) for s in tree["sections"] for g in s["groups"])
        self.assertEqual(total, 57)
        self.assertEqual(tree["sections"][2]["pool_units"], "18")
        self.assertEqual(self.group(tree, "A. Computer Systems")["rule"], "pool")

    def test_psychology_open_rule(self):
        group = self.group(self.tree("psych_ba"), "Any 300-500 level Psychology course")
        self.assertEqual(group["rule"], "open")
        self.assertEqual(group["open"], {"subjects": ["PSY"], "min": 300, "max": 599, "exclude": []})
        self.assertEqual(group["courses"], [])
        self.assertIn("31 upper division", group["note"])

    def test_business_choose_groups_and_open_subjects(self):
        tree = self.tree("ba_general_bs")
        stats = self.group(tree, "Statistics (pick 1, not both)")
        self.assertEqual((stats["rule"], stats["pick_n"], len(stats["courses"])), ("choose", 1, 2))
        electives = self.group(tree, "400-500 level Fowler College of Business courses")
        self.assertEqual(electives["open"]["subjects"], ["ACCTG", "BA", "FIN", "MGT", "MIS", "MKTG"])

    def test_criminal_justice_practicum_and_two_open_rules(self):
        tree = self.tree("crim_justice")
        practicum = self.group(tree, "Practicum (pick 1)")
        self.assertEqual((practicum["pick_n"], len(practicum["courses"])), (1, 6))
        self.assertEqual(self.group(tree, "Criminal justice specific electives")["open"]["subjects"], ["CJ"])
        pa = self.group(tree, "Public administration electives (pick 2)")
        self.assertEqual((pa["pick_n"], pa["open"]["subjects"]), (2, ["PA"]))
        codes = {c["code"]: c for c in self.group(tree, "Required")["courses"]}
        self.assertTrue(codes["POLS 102"]["has_sections"])

    def test_kinesiology_clinic_choice_and_ens(self):
        tree = self.tree("kin_prept")
        clinic = self.group(tree, "Clinic (pick 1, not both)")
        self.assertEqual([c["code"] for c in clinic["courses"]], ["ENS 437A", "ENS 437B"])
        self.assertEqual(clinic["pick_n"], 1)
        self.assertTrue(clinic["courses"][0]["has_sections"])
        self.assertFalse(clinic["courses"][1]["has_sections"])             # ENS 437B: not offered, still listed
        self.assertIsNone(clinic["courses"][1]["course_id"])
        codes = {c["code"]: c for c in self.group(tree, "Required")["courses"]}
        self.assertTrue(codes["BIOL 211L"]["has_sections"])
        self.assertEqual(codes["SOC 101"]["ge_areas"], ["4"])

    def test_accounting_open_rule_excludes_and_section_notes(self):
        tree = self.tree("ba_accounting_bs")
        group = self.group(tree, "Any ACCTG 300-599 course")
        self.assertEqual(group["open"]["exclude"], ["ACCTG 325", "ACCTG 326"])
        me = self.tree("me_bs")
        electives = next(s for s in me["sections"] if s["name"] == "Professional Electives")
        self.assertIn("at least 3 units at the 500-level", electives["note"])
        for g in electives["groups"]:
            self.assertIsNone(g["note"])
            self.assertTrue(all("500-level" not in (c["note"] or "") for c in g["courses"]))
        self.assertEqual(self.group(me, "CHEM 202 or CHEM 200 (pick 1)")["rule"], "choose")
        self.assertEqual(self.group(self.tree("civil_engineering_bs"), "CIVE 160 or STAT 250 (pick 1)")["pick_n"], 1)

    def test_unknown_and_bad_major_ids(self):
        for major_id in ("no_such_major", "Bad-Id!", "x" * 41, "CS_BS"):
            res = self.client.get(f"/api/majors/{major_id}/requirements")
            self.assertEqual(res.status_code, 404, major_id)
            self.assertIn("error", res.get_json())


class CoursesApiTests(AppTestCase):
    def courses(self, query, status=200):
        res = self.client.get(f"/api/courses?{query}")
        self.assertEqual(res.status_code, status, query)
        return res.get_json()

    def test_open_rule_lookup(self):
        data = self.courses("subject=PSY&min=300&max=599")
        self.assertFalse(data["truncated"])
        for c in data["courses"]:
            self.assertEqual(c["subject"], "PSY")
            self.assertTrue(300 <= int("".join(ch for ch in c["catalog_num"] if ch.isdigit())) <= 599)
        offered = self.courses("subject=PSY&min=300&max=599&has_sections=1")["courses"]
        self.assertTrue(all(c["has_sections"] for c in offered))

    def test_several_subjects_and_spaces(self):
        data = self.courses("subject=cs|MATH&min=100&max=199&has_sections=1")
        self.assertEqual({c["subject"] for c in data["courses"]}, {"CS", "MATH"})
        self.assertIn("CS 150L", [c["code"] for c in data["courses"]])     # 150L counts as 150
        self.assertEqual(self.courses("subject=POL%20S")["courses"][0]["subject"], "POLS")

    def test_empty_result(self):
        self.assertEqual(self.courses("subject=ZZZ"), {"courses": [], "truncated": False})
        self.assertEqual(self.courses("subject=CJ&min=900&max=999&has_sections=1")["courses"], [])

    def test_result_cap(self):
        with mock.patch.object(majors_routes, "MAX_COURSES", 2):
            data = self.courses("subject=CS")
        self.assertEqual(len(data["courses"]), 2)
        self.assertTrue(data["truncated"])

    def test_bad_input(self):
        for query in ("", "subject=", "subject=PSY;DROP", "subject=PSY&min=abc", "subject=PSY&min=-1",
                      "subject=PSY&min=500&max=300", "subject=PSY&max=99999",
                      "subject=" + "|".join(["CS"] * 13), "subject=TOOLONGCODE"):
            self.assertIn("error", self.courses(query, status=400))


class SectionFilterTests(AppTestCase):
    def test_course_id_and_ids_filters(self):
        tree = self.client.get("/api/majors/cs_bs/requirements").get_json()
        cs150 = next(c for c in tree["sections"][0]["groups"][0]["courses"] if c["code"] == "CS 150")
        sections = self.client.get(f"/api/sections?course_id={cs150['course_id']}").get_json()
        self.assertEqual(len(sections), cs150["section_count"])
        self.assertTrue(all(s["catalog_num"] == "150" for s in sections))

        # two active sections; 1 is a retired id from the old workbook and 999999 never existed
        conn = sqlite3.connect(CLASS_DB)
        wanted = sorted(r[0] for r in conn.execute("SELECT section_id FROM sections WHERE class_number IN ('5834', '5843')"))
        conn.close()
        picked = self.client.get(f"/api/sections?ids=1,{wanted[0]},{wanted[1]},999999").get_json()
        self.assertEqual(sorted(s["section_id"] for s in picked), wanted)

    def test_professor_last_name_for_ratemyprofessors(self):
        sections = self.client.get("/api/sections?professor=Kraft").get_json()
        self.assertTrue(sections)
        for s in sections:
            self.assertTrue(s["professor_name"].endswith(s["professor_last"]))
            self.assertEqual(s["professor_last"], "Kraft")
        # multi-word last names come through whole
        geer = self.client.get("/api/sections?professor=Van%20Der%20Geer").get_json()
        if geer:
            self.assertEqual(geer[0]["professor_last"], "Van Der Geer")

    def test_bad_id_lists(self):
        for query in ("ids=abc", "ids=1,x", "ids=", "course_id=1;2", "ids=" + ",".join(["1"] * 201)):
            res = self.client.get(f"/api/sections?{query}")
            self.assertEqual(res.status_code, 400, query)


class MajorAnalyticsTests(AppTestCase):
    def test_major_select_and_plan_create(self):
        vid = "visitor-majors"
        self.assertEqual(self.event(vid, "major_select", {"major": "cs_bs"}).status_code, 204)
        self.assertEqual(self.event(vid, "major_select", {"major": "m" * 60}).status_code, 204)
        self.assertEqual(self.event(vid, "plan_create", {"cart_size": 0}).status_code, 204)
        rows = stored_events(vid)
        self.assertEqual([r["event"] for r in rows], ["major_select", "major_select", "plan_create"])
        self.assertEqual(json.loads(rows[1]["props"])["major"], "m" * 40)

        stats = self.client.get("/api/admin/stats", headers={"Authorization": f"Bearer {ADMIN_TOKEN}"}).get_json()
        self.assertGreaterEqual(stats["majors"]["cs_bs"], 1)

class CoverageReportTests(unittest.TestCase):
    """scripts/coverage_report.py: an open rule counts neither its excluded courses nor the major's required ones."""

    def test_open_rule_leaves_out_excluded_and_required_courses(self):
        import importlib.util
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location("coverage_report", os.path.join(root, "scripts", "coverage_report.py"))
        report = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(report)
        base = {"pick_n": "", "pick_units": "", "subject": "", "catalog_num": "", "num_min": "", "num_max": "",
                "exclude": "", "title": "", "units": "3", "note": ""}
        rows = [
            dict(base, major_id="t", section="Major", group_label="Required", rule="required", subject="ACCTG",
                 catalog_num="331"),
            dict(base, major_id="t", section="Electives", group_label="", rule="note", note="A section note"),
            dict(base, major_id="t", section="Electives", group_label="Any ACCTG 300-599 course", rule="open",
                 pick_units="6", subject="ACCTG", num_min="300", num_max="599", exclude="ACCTG 325|ACCTG 326"),
        ]
        files = {("data", "majors", "majors.csv"): [{"major_id": "t", "name": "T", "status": "live"}],
                 ("data", "majors", "major_requirements.csv"): rows}
        offered = {(s, n): {"units": 3, "sections": 1, "scheduled": 1}
                   for s, n in [("ACCTG", "325"), ("ACCTG", "326"), ("ACCTG", "331"), ("ACCTG", "409")]}
        with mock.patch.object(report, "read", lambda *path: files[path]):
            lines, _ = report.major_report(offered)
        text = "\n".join(lines)
        # only ACCTG 409 counts: 325/326 are excluded and 331 is already required
        self.assertIn("any ACCTG 300-599 needs 1 course(s) / 6 units, 1 offered (3 units)", text)


if __name__ == "__main__":
    unittest.main()

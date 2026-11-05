"""
Tests for data/import_real_data.py: section ids must stay the same from one
import to the next, because students' saved plans remember sections by id.
"""

import contextlib
import csv
import datetime
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("import_real_data", os.path.join(ROOT, "data", "import_real_data.py"))
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)


def row(subject, catalog, section, term="Spring 2027"):
    """A row as validate() leaves it."""
    return {"subject": subject, "catalog_num": catalog, "course_title": f"{subject} {catalog}", "units": "3",
            "section_number": section, "term": term, "days": "MW", "start_time": "09:00", "end_time": "10:15",
            "capacity": "40", "professor_first": "", "professor_last": "", "building": "", "room_number": ""}


def save(out_dir, rows, known=None, highest=0):
    """Builds tables like main() and writes the courses and sections CSVs; returns {key: id}."""
    _, _, courses, sections = importer.build_tables(rows, known, highest)
    with contextlib.redirect_stdout(io.StringIO()):
        importer.write(os.path.join(out_dir, "courses.csv"),
                       ["course_id", "subject", "catalog_num", "title", "units", "description"],
                       [{"course_id": v[0], "subject": k[0], "catalog_num": k[1], "title": v[1], "units": v[2], "description": ""}
                        for k, v in courses.items()])
        importer.write(os.path.join(out_dir, "sections.csv"),
                       ["section_id", "course_id", "professor_id", "room_id", "section_number", "term",
                        "days", "start_time", "end_time", "capacity"], sections)
    return {(r["subject"], r["catalog_num"], r["section_number"]): s["section_id"] for r, s in zip(rows, sections)}


def raw_row(first, last, n=2):
    """A row as read from the sheet, before validate()."""
    return {"_row": n, "term": "Spring 2027", "subject": "CS", "catalog_num": "150", "course_title": "Intro",
            "units": "3", "section_number": "1", "days": "MW", "start_time": "09:00", "end_time": "10:15",
            "professor_first": first, "professor_last": last, "building": "P", "room_number": "144", "capacity": "40"}


class ProfessorNameTests(unittest.TestCase):
    def test_placeholder_names_mean_no_professor(self):
        for first, last in (("To be", "Announced"), ("TBA", ""), ("Staff", ""), ("tba", "tba")):
            good, errors = importer.validate([raw_row(first, last)])
            self.assertEqual(errors, [], (first, last))
            self.assertEqual((good[0]["professor_first"], good[0]["professor_last"]), ("", ""), (first, last))

    def test_real_names_are_kept(self):
        good, errors = importer.validate([raw_row("Patricia", "Kraft")])
        self.assertEqual((good[0]["professor_first"], good[0]["professor_last"]), ("Patricia", "Kraft"))


class StableIdTests(unittest.TestCase):
    def test_first_import_numbers_from_one(self):
        with tempfile.TemporaryDirectory() as out:
            self.assertEqual(importer.previous_section_ids(out), ({}, 0))
            ids = save(out, [row("CS", "150", "01"), row("CS", "150", "02"), row("MATH", "150", "01")])
            self.assertEqual(sorted(ids.values()), [1, 2, 3])

    def test_ids_survive_reordering_inserts_and_removals(self):
        with tempfile.TemporaryDirectory() as out:
            first = save(out, [row("CS", "150", "01"), row("CS", "150", "02"), row("MATH", "150", "01")])
            known, highest = importer.previous_section_ids(out)
            self.assertEqual(highest, 3)
            # a new row on top, CS 150-02 deleted, the rest moved around
            second = save(out, [row("PSY", "101", "01"), row("MATH", "150", "01"), row("CS", "150", "01")], known, highest)
            self.assertEqual(second[("CS", "150", "01")], first[("CS", "150", "01")])
            self.assertEqual(second[("MATH", "150", "01")], first[("MATH", "150", "01")])
            self.assertEqual(second[("PSY", "101", "01")], 4)               # new: after the highest id ever used
            self.assertNotIn(first[("CS", "150", "02")], second.values())    # a removed id is not reused

            # a third import still remembers the highest id, even though id 2 is gone
            known, highest = importer.previous_section_ids(out)
            third = save(out, [row("CS", "150", "01"), row("BIOL", "100", "01")], known, highest)
            self.assertEqual(third[("BIOL", "100", "01")], 5)

    def test_same_section_in_another_term_is_a_different_section(self):
        with tempfile.TemporaryDirectory() as out:
            save(out, [row("CS", "150", "01")])
            known, highest = importer.previous_section_ids(out)
            ids = save(out, [row("CS", "150", "01", term="Fall 2027")], known, highest)
            self.assertEqual(ids[("CS", "150", "01")], 2)

    def test_key_ignores_spaces_and_case_in_subject(self):
        self.assertEqual(importer.section_key("POL S", "102", "01", "Spring 2027"),
                         importer.section_key("pols", " 102 ", "01", "Spring 2027"))



class DataDateTests(unittest.TestCase):
    def test_import_records_todays_date_for_the_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            sheet = os.path.join(tmp, "rows.csv")
            fields = [k for k in raw_row("Patricia", "Kraft") if k != "_row"]
            with open(sheet, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                w.writerow({k: v for k, v in raw_row("Patricia", "Kraft").items() if k != "_row"})
            out = os.path.join(tmp, "cleaned")
            with mock.patch.object(importer, "OUT_DIR", out),                  mock.patch.object(importer, "previous_section_ids", return_value=({}, 0)),                  mock.patch.object(sys, "argv", ["import_real_data.py", sheet]),                  contextlib.redirect_stdout(io.StringIO()):
                importer.main()
            with open(os.path.join(out, "data_info.json"), encoding="utf-8") as f:
                self.assertEqual(json.load(f), {"updated": datetime.date.today().isoformat()})


if __name__ == "__main__":
    unittest.main()

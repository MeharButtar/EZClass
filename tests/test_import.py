"""
Tests for data/import_real_data.py: section ids must stay the same from one
import to the next, because students' saved plans remember sections by id.
"""

import contextlib
import importlib.util
import io
import os
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()

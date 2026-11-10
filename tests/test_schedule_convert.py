"""
Tests for data/convert_sdsu_schedule.py, the official schedule export ->
Sections format converter.

tests/fixtures/schedule/schedule_sample.xlsx holds 50 real rows of the
Spring 2027 export (picked by Class Nbr, one or two per hard case) plus 4
made-up rows with class numbers 99001 to 99004 for cases the real file
doesn't have. tests/fixtures/schedule/cleaned/ is a tiny "current EzClass
data" to compare with (titles, full first names, known rooms).
"""

import csv
import importlib.util
import os
import random
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


conv = load("convert_sdsu_schedule", os.path.join("data", "convert_sdsu_schedule.py"))
importer = load("import_real_data", os.path.join("data", "import_real_data.py"))

FIXTURES = os.path.join(ROOT, "tests", "fixtures", "schedule")
SAMPLE = os.path.join(FIXTURES, "schedule_sample.xlsx")
CLEANED = os.path.join(FIXTURES, "cleaned")
NOWHERE = os.path.join(FIXTURES, "no-such-folder")


def convert(path=SAMPLE):
    return conv.convert(path, cleaned_dir=CLEANED, majors_dir=NOWHERE, ge_dir=NOWHERE)


def sample_rows():
    import openpyxl
    wb = openpyxl.load_workbook(SAMPLE, read_only=True)
    rows = [list(r) for r in wb.worksheets[0].iter_rows(values_only=True)]
    wb.close()
    return rows


def write_xlsx(path, rows):
    import openpyxl
    book = openpyxl.Workbook()
    for r in rows:
        book.active.append(r)
    book.save(path)


FIELDS = ["term", "subject", "catalog", "title", "units", "section", "days", "start", "end",
          "first", "last", "building", "room", "seats", "class_number"]


class SampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.term, cls.table, cls.report = convert()
        cls.rows = {r[-1]: dict(zip(FIELDS, r)) for r in cls.table}

    def row(self, class_number):
        self.assertIn(class_number, self.rows, f"class {class_number} is not in the output")
        return self.rows[class_number]

    def meeting(self, class_number):
        r = self.row(class_number)
        return (r["days"], r["start"], r["end"], r["building"], r["room"])

    # ---- the numbers ----
    def test_term_and_counts_add_up(self):
        self.assertEqual(self.term, "Spring 2027")
        self.assertIn("Rows read:            54  (the title line says 54: matches)", self.report)
        self.assertIn("(adds up)", self.report)
        self.assertEqual(len(self.table), 32)

    def test_header_matches_the_importer(self):
        keys = [importer.header_key(h) for h in conv.OUT_HEADER]
        self.assertEqual(keys, importer.COLUMNS + importer.OPTIONAL_COLUMNS)

    # ---- section 5: the mapping ----
    def test_cs_150_sec_01(self):
        r = self.row("5834")
        self.assertEqual((r["subject"], r["catalog"], r["section"], r["units"], r["seats"]), ("CS", "150", "01", "3", "60"))
        self.assertEqual(self.meeting("5834"), ("TTh", "09:30", "10:45", "P", "144"))
        self.assertEqual((r["first"], r["last"]), ("Patricia", "Kraft"))          # full name from professors.csv
        self.assertEqual(r["title"], "Introductory Computer Programming")      # the current EzClass title

    def test_cs_160_sec_01(self):
        self.assertEqual(self.meeting("5843"), ("MW", "14:00", "15:15", "LH", "343"))
        self.assertEqual(self.row("5843")["title"], "Int Computer Programming")   # new course: the export's title

    def test_subject_spaces_and_catalog_padding(self):
        self.assertEqual(self.row("2610")["subject"], "NAVS")                  # 'NAV S'
        self.assertEqual(self.row("2482")["subject"], "MSE")                   # 'M S E'
        self.assertNotIn("11529", self.rows)                                   # ENGR '  16' is Global campus only

    def test_saturday(self):
        self.assertEqual(self.row("8047")["days"], "Sa")

    def test_parts_taken_together_get_the_course_total(self):
        # ACCTG 201: a 1.5-unit LED part and a 1.5-unit LLC part with the same Associated Class
        self.assertEqual((self.row("3807")["units"], self.row("3808")["units"]), ("3", "3"))
        self.assertIn("course made of parts: each part gets its group's total units: 1", self.report)
        self.assertEqual(self.row("5834")["units"], "3")                      # one part only: as listed

    def test_placeholder_seats_are_blank(self):
        self.assertEqual(self.row("11636")["seats"], "")    # 0
        self.assertEqual(self.row("99004")["seats"], "")    # 999

    def test_other_campuses_are_skipped_and_counted(self):
        self.assertNotIn("10713", self.rows)                # IVC
        self.assertIn("campus GLBL: 1", self.report)
        self.assertIn("campus IVC: 1", self.report)

    # ---- section 6: meetings and online ----
    def test_live_online_stays_timed(self):
        self.assertEqual(self.meeting("8906"), ("TTh", "17:30", "18:45", "ONLINE", ""))

    def test_asyn_is_an_online_part(self):
        self.assertEqual(self.meeting("9902"), ("ONLINE", "", "", "", ""))

    def test_a_time_that_comes_with_asyn_is_dropped_and_reported(self):
        self.assertEqual(self.meeting("99004"), ("ONLINE", "", "", "", ""))
        self.assertIn("time with pattern ASYN dropped: 1", self.report)

    def test_facility_online_with_no_time_is_an_online_part(self):
        self.assertEqual(self.meeting("5366"), ("MW / ONLINE", "10:00 / ", "10:50 / ", "SH / ", "109 / "))

    def test_hybrid_keeps_both_parts(self):
        self.assertEqual(self.meeting("5837"), ("M / ONLINE", "17:30 / ", "18:45 / ", "SSW / ", "2522 / "))
        self.assertEqual((self.row("5837")["first"], self.row("5837")["last"]), ("", ""))   # no instructor listed

    def test_arranged_in_person_has_no_schedule(self):
        self.assertEqual(self.meeting("2148"), ("", "", "", "", ""))           # music lesson, kept
        self.assertEqual(self.meeting("9118"), ("", "", "", "", ""))           # ARRSDSU
        self.assertIn("in-person arranged section -> no schedule (Time not listed yet)", self.report)

    def test_arranged_in_a_hybrid_section_is_online(self):
        self.assertEqual(self.meeting("8793"), ("ONLINE", "", "", "", ""))

    def test_arranged_part_next_to_a_timed_one_is_dropped(self):
        self.assertEqual(self.meeting("11238"), ("T", "18:00", "19:40", "SH", "324"))
        self.assertIn("part dropped next to a timed meeting (arranged)", self.report)

    def test_pattern_without_times_is_reported_not_guessed(self):
        self.assertEqual(self.meeting("6095"), ("MW", "12:00", "13:15", "PG", "242"))
        self.assertIn("pattern but no times (part dropped, not guessed): 1", self.report)
        self.assertIn("AE 310 sec 01 (class 6095): F", self.report)

    # ---- rooms ----
    def test_rooms_split(self):
        self.assertEqual(self.meeting("7847")[3:], ("SHW", "237"))             # SHW, not SH + W237
        self.assertEqual(self.meeting("10550")[3:], ("LLA", "2203"))           # unknown building: letters, digits

    def test_codes_that_do_not_split_stay_whole(self):
        self.assertEqual(self.meeting("4477")[3:], ("AQUAPLEX", ""))
        self.assertEqual(self.meeting("12266")[3:], ("39-110", ""))
        self.assertIn("39-110, AQUAPLEX", self.report)

    def test_off_campus(self):
        self.assertEqual(self.meeting("11865")[3:], ("Off campus", ""))

    # ---- people ----
    def test_two_instructors(self):
        r = self.row("10550")
        self.assertEqual((r["first"], r["last"]), ("K. / S.", "Kennelly / Roldan"))

    def test_ambiguous_initial_uses_the_initial(self):
        r = self.row("5180")
        self.assertEqual((r["first"], r["last"]), ("A.", "Brown"))
        self.assertIn("A Brown: Ajani Brown, Alison Brown", self.report)

    def test_all_caps_last_name_is_title_cased(self):
        self.assertEqual(self.row("2610")["last"], "Karnes")

    def test_instructor_on_only_some_meetings_is_reported(self):
        self.assertIn("GEOG 101 sec 01 (class 3866)", self.report)

    # ---- titles ----
    def test_special_topics_keep_their_own_titles(self):
        self.assertEqual(self.row("4691")["title"], "Mus&Cult: Hip Hop")
        self.assertEqual(self.row("8081")["title"], "Mus&Cult: The Beatles")

    def test_current_title_kept_for_a_known_course(self):
        self.assertEqual(self.row("9902")["title"], "Politics, Power, and Asian America")

    # ---- duplicate keys ----
    def test_lowest_class_number_wins_a_duplicate_key(self):
        self.assertIn("8866", self.rows)
        self.assertNotIn("12138", self.rows)
        self.assertNotIn("12192", self.rows)
        self.assertIn("GEOL 502 sec 01: class 12138 skipped, 8866 kept", self.report)

    # ---- section 6c: thesis and individual study ----
    def test_thesis_kinds_are_skipped(self):
        for nbr in ("1057", "2025", "3137", "9514", "3347", "1081", "3659", "6385"):
            self.assertNotIn(nbr, self.rows, nbr)
        self.assertIn("thesis or individual study: 8", self.report)

    def test_kept_even_without_a_time(self):
        for nbr in ("99001", "99002", "99003", "11122", "2482", "2148"):
            self.assertIn(nbr, self.rows, nbr)


class ThesisRuleTests(unittest.TestCase):
    def skip(self, title, catalog="500", component="SUP", timed=False):
        return conv.is_thesis_like(component, title, catalog, timed)

    def test_skipped_titles(self):
        for title in ("Thesis", "Thesis or Project", "Thesis Extension", "Thesis or Proj Extension", "Senior Thesis",
                      "Undergrad Honors Thesis", "Thesis Research", "Doctoral Dissertation", "Special Study",
                      "Special Studies", "Doctoral Special Study", "Honors Special Study", "Research",
                      "Doctoral Research", "Independent Research", "Undergraduate Research", "Directed Study",
                      "Directed Readings Thea", "Comprehensive Exam", "Comp Exam Extension",
                      "Investigation and Report", "Investigation & Report"):
            self.assertTrue(self.skip(title), title)

    def test_kept_titles(self):
        for title in ("Intro to Research Methods", "Marketing Research", "Internship", "Orientation Practicum",
                      "Per St Jazz Inst", "Perfrm Stdy: Strings", "DNP Project/Clinical Practice"):
            self.assertFalse(self.skip(title), title)

    def test_a_real_day_and_time_always_stays(self):
        self.assertFalse(self.skip("Special Study", timed=True))

    def test_other_components_stay(self):
        self.assertFalse(self.skip("Thesis", component="LEC"))

    def test_number_ending_in_97_98_99_is_a_second_opinion(self):
        self.assertTrue(self.skip("Research Crim Justice", catalog="797"))
        self.assertTrue(self.skip("Project", catalog="798"))
        for title in ("Internship", "Clinical Practicum", "Fieldwork", "Student Teaching", "Community Service",
                      "Senior Project", "At Clerkship II"):
            self.assertFalse(self.skip(title, catalog="499"), title)
        self.assertFalse(self.skip("Research Crim Justice", catalog="796"))


class SmallRuleTests(unittest.TestCase):
    def test_term_name(self):
        self.assertEqual(conv.term_name("2273"), "Spring 2027")
        self.assertEqual(conv.term_name("2275"), "Summer 2027")
        self.assertEqual(conv.term_name("2287"), "Fall 2028")
        for bad in ("2279", "273", "Spring"):
            with self.assertRaises(ValueError):
                conv.term_name(bad)

    def test_days(self):
        self.assertEqual(conv.days_of("TR"), "TTh")
        self.assertEqual(conv.days_of("MWF"), "MWF")
        self.assertEqual(conv.days_of("MTWR"), "MTWTh")
        self.assertEqual(conv.days_of("S"), "Sa")
        with self.assertRaises(ValueError):
            conv.days_of("MX")

    def test_clock(self):
        self.assertEqual(conv.clock("06:00 PM"), "18:00")
        self.assertEqual(conv.clock("9:30 AM"), "09:30")
        self.assertEqual(conv.clock("12:00 PM"), "12:00")
        self.assertEqual(conv.clock("12:30 AM"), "00:30")
        self.assertEqual(conv.clock("18:00"), "18:00")
        self.assertIsNone(conv.clock("TBA"))

    def test_room_split(self):
        rooms = conv.Rooms([{"building": b, "room_number": r} for b, r in
                            [("SH", "100"), ("SHW", "237"), ("RDNY", "AUD"), ("GMCS", "214"), ("ONLINE", "")]])
        self.assertEqual(rooms.split("GMCS428"), ("GMCS", "428", True))
        self.assertEqual(rooms.split("RDNYAUD"), ("RDNY", "AUD", True))
        self.assertEqual(rooms.split("SHW237"), ("SHW", "237", True))
        self.assertEqual(rooms.split("SH222D"), ("SH", "222D", True))
        self.assertEqual(rooms.split("M119A"), ("M", "119A", True))
        self.assertEqual(rooms.split("ARTN512B"), ("ARTN", "512B", True))
        self.assertEqual(rooms.split("PSYANNX"), ("PSYANNX", "", False))
        self.assertEqual(rooms.split("39-105"), ("39-105", "", False))

    def test_group_units(self):
        self.assertEqual(conv.group_units({"LED": {"1.5"}, "LLC": {"1.5"}}), "3")
        self.assertEqual(conv.group_units({"LLC": {"3"}, "LED": {"1"}, "LAB": {"1"}}), "5")
        self.assertEqual(conv.group_units({"LEC": {"3.5"}, "CPO": {"2.5"}}), "6")
        self.assertEqual(conv.group_units({"LEC": {"3"}, "LAB": {"0"}}), "3")
        self.assertEqual(conv.group_units({"LED": {"2", "3"}, "ACT": {"1"}}), "4")   # a part with two values: the largest
        self.assertIsNone(conv.group_units({"LEC": {"3"}}))                         # one part: nothing to add
        self.assertIsNone(conv.group_units({"LEC": {"3"}, "LAB": {"1-2"}}))          # not a number: left alone
        self.assertEqual(conv.number_text("5.0"), "5")
        self.assertIsNone(conv.number_text("1-4"))

    def test_title_case_only_all_caps(self):
        self.assertEqual(conv.title_case_caps("RICHARDSON"), "Richardson")
        self.assertEqual(conv.title_case_caps("De La Pena"), "De La Pena")
        self.assertEqual(conv.title_case_caps("Alameen-Shavers"), "Alameen-Shavers")


class WholeFileTests(unittest.TestCase):
    def test_same_input_same_output_even_shuffled(self):
        first = conv.csv_text(convert()[1])
        self.assertEqual(first, conv.csv_text(convert()[1]))
        rows = sample_rows()
        body = rows[2:]
        random.Random(7).shuffle(body)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "shuffled.xlsx")
            write_xlsx(path, rows[:2] + body)
            self.assertEqual(first, conv.csv_text(convert(path)[1]))

    def test_header_row_is_found_not_assumed(self):
        rows = sample_rows()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "moved.xlsx")
            write_xlsx(path, [rows[0], ["exported by someone"]] + rows[1:])
            self.assertEqual(len(convert(path)[1]), 32)

    def test_two_terms_stop(self):
        rows = sample_rows()
        term = rows[1].index("Term")
        rows[2][term] = "2277"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "two_terms.xlsx")
            write_xlsx(path, rows)
            with self.assertRaises(SystemExit) as stop:
                convert(path)
            self.assertIn("exactly one term", str(stop.exception))

    def test_unknown_day_letter_stops(self):
        rows = sample_rows()
        pattern = rows[1].index("Standard Meeting Pattern")
        nbr = rows[1].index("Class Nbr")
        row = next(r for r in rows[2:] if int(r[nbr]) == 5834)
        row[pattern] = "TX"
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "bad_day.xlsx")
            write_xlsx(path, rows)
            with self.assertRaises(SystemExit) as stop:
                convert(path)
            self.assertIn("letter 'X'", str(stop.exception))

    def test_the_output_imports_cleanly(self):
        _, table, _ = convert()
        with tempfile.TemporaryDirectory() as tmp:
            sheet = os.path.join(tmp, "sections.csv")
            with open(sheet, "w", encoding="utf-8", newline="") as f:
                f.write(conv.csv_text(table))
            text, skipped = importer.run(sheet, out_dir=tmp, report_path=None)
            self.assertEqual(skipped, 0, text)
            with open(os.path.join(tmp, "sections.csv"), newline="", encoding="utf-8") as f:
                sections = {s["class_number"]: s for s in csv.DictReader(f)}
            with open(os.path.join(tmp, "section_meetings.csv"), newline="", encoding="utf-8") as f:
                meetings = {}
                for m in csv.DictReader(f):
                    meetings.setdefault(m["section_id"], []).append(m)
            self.assertEqual(len(sections), 32)
            lab = meetings[sections["5837"]["section_id"]]                     # hybrid: timed + online
            self.assertEqual([(m["day_code"], m["building"], m["is_online"]) for m in lab],
                             [("M", "SSW", "0"), ("", "ONLINE", "1")])
            live = meetings[sections["8906"]["section_id"]]                    # live online: timed, building ONLINE
            self.assertEqual([(m["day_code"], m["start_min"], m["building"], m["is_online"]) for m in live],
                             [("TTh", "1050", "ONLINE", "0")])
            self.assertNotIn(sections["2148"]["section_id"], meetings)         # arranged: no meetings
            self.assertEqual(sections["3807"]["seats_total"], "45")


if __name__ == "__main__":
    unittest.main()

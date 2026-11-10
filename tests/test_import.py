"""
Tests for data/import_real_data.py: the slash rules (several meetings,
instructors and seat numbers in one row), online and hybrid sections, stable
ids from one import to the next, and the real Spring 2027 sheet
(tests/fixtures/spring2027_sections.xlsx is a copy of its Sections sheet).
"""

import csv
import datetime
import importlib.util
import json
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("import_real_data", os.path.join(ROOT, "data", "import_real_data.py"))
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)

from backend.models.conflicts import find_conflicts  # noqa: E402

FIXTURE = os.path.join(ROOT, "tests", "fixtures", "spring2027_sections.xlsx")


def rec(row=3, **cells):
    """A sheet row as read_rows() gives it (all text), CS 150 section 1 unless changed."""
    base = {"term": "Spring 2027", "subject": "CS", "catalog_num": "150", "course_title": "Intro", "units": "3",
            "section_number": "1", "days": "MW", "start_time": "09:00", "end_time": "10:15",
            "professor_first": "Patricia", "professor_last": "Kraft", "building": "GMCS", "room_number": "214",
            "seats": "40"}
    base.update(cells)
    base["_row"] = row
    return base


def parse(**cells):
    report = importer.Report()
    return importer.parse_row(rec(**cells), report), report


def problem(**cells):
    """The reason parse_row refuses the row (fails the test if it doesn't)."""
    try:
        importer.parse_row(rec(**cells), importer.Report())
    except importer.RowProblem as e:
        return str(e)
    raise AssertionError(f"row was accepted: {cells}")


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_table(out_dir, name):
    with open(os.path.join(out_dir, f"{name}.csv"), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_sheet(path, rows):
    """A CSV sheet (the importer reads CSV like the workbook) from rec()-style dicts."""
    fields = [c for c in importer.COLUMNS]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Term", "Subject", "Course Number", "Course Title", "Units", "Section", "Days", "Start Time",
                    "End Time", "Professor First Name", "Professor Last Name", "Building", "Room Number", "Seats"])
        for r in rows:
            w.writerow([r[c] for c in fields])


def run(sheet_rows, out_dir):
    """Imports rec()-style rows on top of out_dir. Returns (report text, skipped, sections by key)."""
    sheet = os.path.join(out_dir, "sheet.csv")
    write_sheet(sheet, sheet_rows)
    text, skipped = importer.run(sheet, out_dir=out_dir, report_path=None)
    courses = {r["course_id"]: (r["subject"], r["catalog_num"]) for r in read_table(out_dir, "courses")}
    sections = {(*courses[s["course_id"]], s["section_number"], s["term"]): s for s in read_table(out_dir, "sections")}
    return text, skipped, sections


# ---------- 1. days ----------

class DayTests(unittest.TestCase):
    def test_day_patterns(self):
        for days, tokens in (("TWTh", ["T", "W", "Th"]), ("MTWTh", ["M", "T", "W", "Th"]),
                             ("MWThF", ["M", "W", "Th", "F"]), ("TTh", ["T", "Th"]), ("MWF", ["M", "W", "F"]),
                             ("SaSu", ["Sa", "Su"])):
            self.assertEqual(importer.day_tokens(days), tokens, days)
            s, _ = parse(days=days)
            self.assertEqual(s["meetings"][0]["day_code"], days)

    def test_unknown_days_skip_the_row(self):
        self.assertIn("not understood", problem(days="MX"))
        self.assertIn("not understood", problem(days="Tu"))

    def test_online_any_case(self):
        for days in ("ONLINE", "online", "Online"):
            s, report = parse(days=days, start_time="", end_time="", building="ONLINE", room_number="")
            self.assertEqual(s["meetings"], [{"day_code": "", "start_min": None, "end_min": None,
                                              "building": "ONLINE", "room": "", "is_online": 1}], days)
            self.assertEqual(dict(report.normalized), {}, days)

    def test_async_and_friends_become_online_and_are_logged(self):
        for days in ("ASYNC", "ASYNCHRONOUS", "ARRANGED", "TBA"):
            s, report = parse(days=days, start_time="", end_time="", building=days, room_number="")
            self.assertEqual(s["meetings"][0]["is_online"], 1)
            self.assertEqual(s["meetings"][0]["building"], "ONLINE")
            self.assertEqual(report.normalized[f"{days} -> ONLINE (Days)"], [3])
            self.assertEqual(report.normalized[f"{days} -> ONLINE (Building)"], [3])

    def test_times(self):
        s, _ = parse(start_time="9:30", end_time="10:45")
        self.assertEqual((s["meetings"][0]["start_min"], s["meetings"][0]["end_min"]), (570, 645))
        self.assertIn("ends before it starts", problem(start_time="10:00", end_time="09:00"))
        self.assertIn("needs a start and end time", problem(start_time="", end_time=""))
        self.assertIn("is ONLINE but has a time", problem(days="MW / ONLINE", start_time="09:00 / 10:00", end_time="10:00 / 11:00"))


# ---------- 2. slash alignment ----------

class SlashTests(unittest.TestCase):
    def test_one_part_applies_to_every_meeting(self):
        s, _ = parse(days="MW / F", start_time="13:00", end_time="13:50", building="LH", room_number="256")
        self.assertEqual([(m["day_code"], m["start_min"], m["building"], m["room"]) for m in s["meetings"]],
                         [("MW", 780, "LH", "256"), ("F", 780, "LH", "256")])

    def test_one_part_per_meeting(self):
        s, _ = parse(days="MW / MW", start_time="13:00 / 12:00", end_time="13:50 / 12:50",
                     building="LH / GMCS", room_number="256 / 333")
        self.assertEqual([(m["day_code"], m["start_min"], m["end_min"], m["building"], m["room"]) for m in s["meetings"]],
                         [("MW", 780, 830, "LH", "256"), ("MW", 720, 770, "GMCS", "333")])

    def test_empty_parts_for_the_online_meeting(self):
        s, _ = parse(days="TTh / ONLINE", start_time="09:30 / ", end_time="10:45 / ",
                     building="GMCS / ONLINE", room_number="333 / ")
        self.assertEqual(s["meetings"][0], {"day_code": "TTh", "start_min": 570, "end_min": 645,
                                            "building": "GMCS", "room": "333", "is_online": 0})
        self.assertEqual(s["meetings"][1]["is_online"], 1)
        self.assertIsNone(s["meetings"][1]["start_min"])

    def test_a_shared_time_does_not_land_on_the_online_meeting(self):
        s, _ = parse(days="TTh / ONLINE", start_time="09:30", end_time="10:45", building="GMCS", room_number="333")
        self.assertEqual(s["meetings"][0]["start_min"], 570)
        self.assertEqual((s["meetings"][1]["is_online"], s["meetings"][1]["start_min"], s["meetings"][1]["building"]),
                         (1, None, "ONLINE"))

    def test_mismatched_counts_skip_only_that_row(self):
        self.assertIn("Start has 2 parts but Days has 3", problem(days="M / W / F", start_time="09:00 / 10:00"))
        self.assertIn("Room has 3 parts but Days has 2", problem(days="M / W", room_number="1 / 2 / 3"))
        with tempfile.TemporaryDirectory() as tmp:
            text, skipped, sections = run([rec(3), rec(4, section_number="2", days="M / W", start_time="09:00 / 10:00 / 11:00"),
                                           rec(5, section_number="3")], tmp)
            self.assertEqual(skipped, 1)
            self.assertIn("row 3: Start has 3 parts but Days has 2", text)   # a CSV sheet starts on row 2
            self.assertEqual(sorted(k[2] for k in sections), ["01", "03"])


# ---------- 3. seats ----------

class SeatTests(unittest.TestCase):
    def test_seats(self):
        for typed, text, total in (("180 / 45", "180 / 45", 45), ("40", "40", 40), ("", "", None), ("100/25", "100/25", 25)):
            s, _ = parse(seats=typed)
            self.assertEqual((s["seats_text"], s["seats_total"]), (text, total), typed)

    def test_squished_seats_are_reported_not_split(self):
        s, report = parse(seats="18045")
        self.assertEqual((s["seats_text"], s["seats_total"]), ("18045", None))
        self.assertEqual(report.warnings["seats over 999 (two numbers without a slash?)"], [(3, "18045")])

    def test_seats_must_be_numbers(self):
        self.assertIn("whole numbers", problem(seats="forty"))


# ---------- 4. instructors ----------

class InstructorTests(unittest.TestCase):
    def test_two_people_on_one_section(self):
        s, _ = parse(professor_first="Diana / Rachel", professor_last="Carson / Cuesta")
        self.assertEqual(s["instructors"], [("Diana", "Carson"), ("Rachel", "Cuesta")])

    def test_same_person_twice_is_listed_once(self):
        s, _ = parse(professor_first="Diana / diana", professor_last="Carson / CARSON")
        self.assertEqual(s["instructors"], [("Diana", "Carson")])

    def test_empty_and_placeholder_names_mean_no_instructor(self):
        for first, last in (("", ""), (" / ", " / "), ("To be", "Announced"), ("TBA", ""), ("Staff", "")):
            s, _ = parse(professor_first=first, professor_last=last)
            self.assertEqual(s["instructors"], [], (first, last))

    def test_an_empty_part_next_to_a_real_one(self):
        s, _ = parse(professor_first="Diana / ", professor_last="Carson / ")
        self.assertEqual(s["instructors"], [("Diana", "Carson")])

    def test_never_a_person_called_slash(self):
        s, _ = parse(professor_first="/", professor_last="/")
        self.assertEqual(s["instructors"], [])

    def test_mismatched_name_parts_skip_the_row(self):
        self.assertIn("First Name has 2 parts but Last Name has 1", problem(professor_first="Diana / Rachel", professor_last="Carson"))
        self.assertIn("both a first and a last name", problem(professor_first="Diana", professor_last=""))


# ---------- 5. online-only and hybrid ----------

def meeting(day, start=None, end=None):
    online = day == "ONLINE"
    return {"day_code": "" if online else day, "start_min": start, "end_min": end, "is_online": int(online)}


class OnlineAndHybridConflictTests(unittest.TestCase):
    def test_online_only_never_conflicts(self):
        online = {"section_id": 1, "meetings": [meeting("ONLINE")]}
        lecture = {"section_id": 2, "meetings": [meeting("MW", 540, 615)]}
        self.assertEqual(find_conflicts([online, lecture]), [])

    def test_hybrid_conflicts_only_through_its_timed_meetings(self):
        hybrid = {"section_id": 1, "meetings": [meeting("TTh", 570, 645), meeting("ONLINE")]}
        same_time_other_days = {"section_id": 2, "meetings": [meeting("MW", 570, 645)]}
        overlapping = {"section_id": 3, "meetings": [meeting("Th", 600, 700)]}
        self.assertEqual(find_conflicts([hybrid, same_time_other_days]), [])
        self.assertEqual(len(find_conflicts([hybrid, overlapping])), 1)

    def test_second_meeting_can_conflict_and_own_meetings_never_do(self):
        soc = {"section_id": 1, "meetings": [meeting("MW", 780, 830), meeting("MW", 720, 770)]}
        self.assertEqual(find_conflicts([soc]), [])
        at_noon = {"section_id": 2, "meetings": [meeting("M", 720, 795)]}
        self.assertEqual(len(find_conflicts([soc, at_noon])), 1)

    def test_online_only_rows_are_imported(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, skipped, sections = run([rec(3, days="ONLINE", start_time="", end_time="", building="ONLINE", room_number="")], tmp)
            self.assertEqual(skipped, 0)
            s = sections[("CS", "150", "01", "Spring 2027")]
            self.assertEqual((s["days"], s["start_time"], s["active"]), ("", "", "1"))
            self.assertEqual(read_table(tmp, "section_meetings")[0]["is_online"], "1")
            self.assertEqual(read_table(tmp, "rooms"), [])   # ONLINE is not a room


# ---------- 3b. no schedule entered yet ----------

NO_SCHEDULE = dict(days="", start_time="", end_time="", building="", room_number="",
                   professor_first="", professor_last="", seats="")


class NoScheduleTests(unittest.TestCase):
    def test_all_meeting_columns_empty_means_no_meetings(self):
        s, report = parse(**NO_SCHEDULE)
        self.assertEqual((s["meetings"], s["instructors"], s["seats_text"], s["seats_total"]), ([], [], "", None))
        self.assertEqual((dict(report.warnings), report.skipped), ({}, []))

    def test_professor_and_seats_are_still_read(self):
        s, _ = parse(**{**NO_SCHEDULE, "professor_first": "Diana", "professor_last": "Carson", "seats": "30"})
        self.assertEqual((s["meetings"], s["instructors"], s["seats_total"]), ([], [("Diana", "Carson")], 30))

    def test_days_empty_but_something_else_filled_is_skipped(self):
        for column in ("start_time", "end_time", "building", "room_number"):
            self.assertIn("Days is empty but", problem(**{**NO_SCHEDULE, column: "1"}), column)

    def test_imported_without_meetings_rooms_or_conflicts(self):
        with tempfile.TemporaryDirectory() as tmp:
            text, skipped, sections = run([rec(3, subject="PA", catalog_num="301", **NO_SCHEDULE)], tmp)
            self.assertEqual(skipped, 0)
            s = sections[("PA", "301", "01", "Spring 2027")]
            self.assertEqual((s["days"], s["start_time"], s["seats_total"], s["active"]), ("", "", "", "1"))
            self.assertEqual((read_table(tmp, "section_meetings"), read_table(tmp, "rooms")), ([], []))
            self.assertIn("No schedule yet:           1", text)
            self.assertIn("Online-only sections:      0", text)
        nothing = {"section_id": 1, "meetings": []}
        self.assertEqual(find_conflicts([nothing, {"section_id": 2, "meetings": [meeting("MW", 0, 1439)]}]), [])

    def test_typing_the_schedule_in_later_updates_the_same_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, first = run([rec(3, subject="PA", catalog_num="301", **NO_SCHEDULE)], tmp)
            text, _, second = run([rec(3, subject="PA", catalog_num="301")], tmp)
            key = ("PA", "301", "01", "Spring 2027")
            self.assertEqual(first[key]["section_id"], second[key]["section_id"])
            self.assertIn("updated:                 1", text)


# ---------- special topics: a title per section ----------

class SectionTitleTests(unittest.TestCase):
    def test_special_topics_sections_keep_their_own_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [rec(3, subject="MUSIC", catalog_num="351", section_number="1", course_title="Music and Culture: Hip Hop"),
                    rec(4, subject="MUSIC", catalog_num="351", section_number="2", course_title="Music and Culture: Jazz")]
            text, _, sections = run(rows, tmp)
            self.assertEqual([sections[("MUSIC", "351", n, "Spring 2027")]["section_title"] for n in ("01", "02")],
                             ["Music and Culture: Hip Hop", "Music and Culture: Jazz"])
            self.assertEqual(read_table(tmp, "courses")[0]["title"], "Music and Culture")
            self.assertNotIn("two titles", text)

    def test_any_other_course_with_two_titles_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [rec(3, section_number="1"), rec(4, section_number="2", course_title="Intro to Programming")]
            text, _, sections = run(rows, tmp)
            self.assertIn("two titles or unit values for one course: 1", text)
            self.assertEqual(sections[("CS", "150", "02", "Spring 2027")]["section_title"], "Intro to Programming")   # as typed

    def test_shared_title(self):
        self.assertEqual(importer.shared_title(["Music and Culture: Hip Hop", "Music and Culture: Jazz"]), "Music and Culture")
        self.assertEqual(importer.shared_title(["Music and Cultures", "Music and Culture: Jazz"]), "Music and")
        self.assertEqual(importer.shared_title(["Jazz", "Rock"]), "Jazz")


# ---------- stable ids ----------

class StableIdTests(unittest.TestCase):
    def test_ids_survive_reordering_and_removed_sections_go_inactive(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b, c = rec(3, section_number="1"), rec(4, section_number="2"), rec(5, subject="MATH", catalog_num="150")
            _, _, first = run([a, b, c], tmp)
            ids = {k: s["section_id"] for k, s in first.items()}
            d = rec(3, subject="PSY", catalog_num="101")
            text, _, second = run([d, c, a], tmp)              # b removed, d new, order changed
            for key in (("CS", "150", "01", "Spring 2027"), ("MATH", "150", "01", "Spring 2027")):
                self.assertEqual(second[key]["section_id"], ids[key])
            gone = second[("CS", "150", "02", "Spring 2027")]
            self.assertEqual((gone["section_id"], gone["active"]), (ids[("CS", "150", "02", "Spring 2027")], "0"))
            self.assertEqual(second[("PSY", "101", "01", "Spring 2027")]["section_id"], "4")   # never reuses 2
            self.assertIn("CS 150 section 02", text)
            _, _, third = run([d, c, a, b], tmp)               # it comes back with the same id
            self.assertEqual(third[("CS", "150", "02", "Spring 2027")]["active"], "1")
            self.assertEqual(third[("CS", "150", "02", "Spring 2027")]["section_id"], ids[("CS", "150", "02", "Spring 2027")])

    def test_blank_section_gets_the_next_number_and_keeps_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [rec(3, section_number="1"), rec(4, section_number="2"), rec(5, section_number="", days="F")]
            text, _, first = run(rows, tmp)
            self.assertIn(("CS", "150", "03", "Spring 2027"), first)
            self.assertIn("row 4: CS 150 section 03", text)
            _, _, second = run(rows, tmp)
            self.assertEqual(first[("CS", "150", "03", "Spring 2027")]["section_id"], second[("CS", "150", "03", "Spring 2027")]["section_id"])

    def test_old_one_meeting_files_keep_their_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "courses.csv"), "w", newline="", encoding="utf-8") as f:
                f.write("course_id,subject,catalog_num,title,units,description\n7,CS,150,Intro,3,\n")
            with open(os.path.join(tmp, "professors.csv"), "w", newline="", encoding="utf-8") as f:
                f.write("professor_id,first_name,last_name,email,department\n9,Patricia,Kraft,,Unknown\n")
            with open(os.path.join(tmp, "rooms.csv"), "w", newline="", encoding="utf-8") as f:
                f.write("room_id,building,room_number,capacity\n5,GMCS,214,\n")
            with open(os.path.join(tmp, "sections.csv"), "w", newline="", encoding="utf-8") as f:
                f.write("section_id,course_id,professor_id,room_id,section_number,term,days,start_time,end_time,capacity\n"
                        "42,7,9,5,01,Spring 2027,MW,09:00,10:15,40\n")
            text, _, sections = run([rec(3)], tmp)
            s = sections[("CS", "150", "01", "Spring 2027")]
            self.assertEqual((s["section_id"], s["course_id"], s["professor_id"], s["room_id"]), ("42", "7", "9", "5"))
            self.assertIn("unchanged:               1", text)

    def test_same_section_in_another_term_is_a_different_section(self):
        self.assertNotEqual(importer.section_key("CS", "150", "01", "Fall 2026"),
                            importer.section_key("CS", "150", "01", "Spring 2027"))
        self.assertEqual(importer.section_key("POL S", "101", "01", "Fall 2026"),
                         importer.section_key("pols", "101", "01", "Fall 2026"))


# ---------- class numbers and --retire-existing ----------

def run_numbered(sheet_rows, out_dir, retire=False):
    """Like run(), with a 15th Class Number column (rec(class_number=...)). Returns (text, skipped, rows, codes)."""
    sheet = os.path.join(out_dir, "sheet.csv")
    with open(sheet, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Term", "Subject", "Course Number", "Course Title", "Units", "Section", "Days", "Start Time",
                    "End Time", "Professor First Name", "Professor Last Name", "Building", "Room Number", "Seats",
                    "Class Number (registration)"])
        for r in sheet_rows:
            w.writerow([r[c] for c in importer.COLUMNS] + [r.get("class_number", "")])
    text, skipped = importer.run(sheet, out_dir=out_dir, report_path=None, retire_existing=retire)
    courses = {r["course_id"]: f"{r['subject']} {r['catalog_num']}" for r in read_table(out_dir, "courses")}
    rows = read_table(out_dir, "sections")
    return text, skipped, rows, {s["section_id"]: courses[s["course_id"]] for s in rows}


def by_number(rows):
    return {s["class_number"]: s for s in rows if s["class_number"]}


class ClassNumberTests(unittest.TestCase):
    def test_stored_and_carried_into_sections_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            text, skipped, rows, _ = run_numbered([rec(3, class_number="5834"), rec(4, section_number="2", class_number="12095")], tmp)
            self.assertEqual(skipped, 0)
            self.assertEqual(sorted(by_number(rows)), ["12095", "5834"])
            self.assertIn("With a class number:       2", text)

    def test_a_file_without_the_column_imports_as_before(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, skipped, sections = run([rec(3), rec(4, section_number="2")], tmp)
            self.assertEqual(skipped, 0)
            self.assertEqual({s["class_number"] for s in sections.values()}, {""})
            self.assertEqual({s["retired"] for s in sections.values()}, {"0"})

    def test_class_number_must_be_digits(self):
        self.assertIn("digits only", problem(class_number="58A4"))

    def test_a_class_number_is_never_given_to_two_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            text, skipped, rows, _ = run_numbered([rec(3, class_number="5834"), rec(4, section_number="2", class_number="5834")], tmp)
            self.assertEqual(skipped, 1)
            self.assertIn("row 3: CS 150 section 02 has class number 5834, already used by row 2", text)   # CSV rows start at 2
            self.assertEqual(len([s for s in rows if s["class_number"] == "5834"]), 1)

    def test_rows_without_one_are_reported_when_others_have_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            text, _, _, _ = run_numbered([rec(3, class_number="5834"), rec(4, section_number="2")], tmp)
            self.assertIn("no class number (other rows have one): 1", text)
            self.assertIn("row 3: CS 150 section 02", text)

    def test_a_renumbered_section_keeps_its_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, first, _ = run_numbered([rec(3, section_number="1", class_number="5834"),
                                           rec(4, section_number="2", class_number="5835")], tmp)
            ids = {n: s["section_id"] for n, s in by_number(first).items()}
            # the export renumbered them: 5834 is now section 02 and 5835 section 03
            text, _, second, _ = run_numbered([rec(3, section_number="2", class_number="5834"),
                                               rec(4, section_number="3", class_number="5835")], tmp)
            now = by_number(second)
            self.assertEqual((now["5834"]["section_id"], now["5834"]["section_number"]), (ids["5834"], "02"))
            self.assertEqual((now["5835"]["section_id"], now["5835"]["section_number"]), (ids["5835"], "03"))
            self.assertEqual(len(second), 2)                          # nothing new, nothing gone
            self.assertIn("same class number, new section number (id kept): 2", text)

    def test_same_section_number_with_a_different_class_number_is_a_different_class(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, first, _ = run_numbered([rec(3, class_number="5834")], tmp)
            old_id = first[0]["section_id"]
            _, _, second, _ = run_numbered([rec(3, class_number="7777")], tmp)
            now = by_number(second)
            self.assertNotEqual(now["7777"]["section_id"], old_id)
            self.assertEqual((now["5834"]["section_id"], now["5834"]["active"]), (old_id, "0"))

    def test_old_rule_fallback_for_a_file_without_the_column(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, _, first, _ = run_numbered([rec(3, class_number="5834")], tmp)
            _, _, second = run([rec(3, days="TTh")], tmp)
            s = second[("CS", "150", "01", "Spring 2027")]
            self.assertEqual((s["section_id"], s["active"], s["days"]), (first[0]["section_id"], "1", "TTh"))

    def test_running_twice_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = [rec(3, class_number="5834"), rec(4, section_number="2", class_number="5835"),
                    rec(5, subject="MATH", catalog_num="150", class_number="12095")]
            run_numbered(rows, tmp)
            before = {n: read_text(os.path.join(tmp, f"{n}.csv")) for n in importer.TABLE_FIELDS}
            text, _, _, _ = run_numbered(rows, tmp)
            self.assertEqual(before, {n: read_text(os.path.join(tmp, f"{n}.csv")) for n in importer.TABLE_FIELDS})
            self.assertIn("unchanged:               3", text)


class RetireExistingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        # the old data: CS 150 sections 01 and 02, MATH 150 section 01, no class numbers
        _, _, self.old, _ = run_numbered([rec(3, section_number="1"), rec(4, section_number="2"),
                                          rec(5, subject="MATH", catalog_num="150")], self.dir)
        self.old_ids = {s["section_id"] for s in self.old}
        self.old_courses = {r["course_id"]: (r["subject"], r["catalog_num"]) for r in read_table(self.dir, "courses")}

    def tearDown(self):
        self.tmp.cleanup()

    def new_file(self):
        return [rec(3, section_number="1", class_number="5834", days="TTh"),    # same subject, number, section
                rec(4, subject="PSY", catalog_num="101", class_number="9001")]

    def test_a_new_row_with_an_old_key_gets_a_new_id(self):
        text, skipped, rows, codes = run_numbered(self.new_file(), self.dir, retire=True)
        self.assertEqual(skipped, 0)
        new = by_number(rows)
        self.assertNotIn(new["5834"]["section_id"], self.old_ids)
        self.assertNotIn(new["9001"]["section_id"], self.old_ids)
        self.assertEqual(codes[new["5834"]["section_id"]], "CS 150")
        self.assertIn("Retired now:               3", text)

    def test_old_rows_are_kept_inactive_with_their_ids(self):
        _, _, rows, _ = run_numbered(self.new_file(), self.dir, retire=True)
        old = {s["section_id"]: s for s in rows if s["section_id"] in self.old_ids}
        self.assertEqual(set(old), self.old_ids)
        self.assertEqual({(s["active"], s["retired"]) for s in old.values()}, {("0", "1")})
        # courses kept their ids, even MATH 150 that has no section now
        courses = {(r["subject"], r["catalog_num"]): r["course_id"] for r in read_table(self.dir, "courses")}
        for cid, key in self.old_courses.items():
            self.assertEqual(courses[key], cid)

    def test_the_next_run_without_the_flag_changes_nothing(self):
        run_numbered(self.new_file(), self.dir, retire=True)
        before = {n: read_text(os.path.join(self.dir, f"{n}.csv")) for n in importer.TABLE_FIELDS}
        text, _, _, _ = run_numbered(self.new_file(), self.dir)
        self.assertEqual(before, {n: read_text(os.path.join(self.dir, f"{n}.csv")) for n in importer.TABLE_FIELDS})
        self.assertIn("Retired earlier:           3", text)

    def test_retired_sections_never_match_later_even_by_the_old_rule(self):
        run_numbered(self.new_file(), self.dir, retire=True)
        # a later file without class numbers that has CS 150 section 02 (only the retired one has that key)
        _, _, rows, _ = run_numbered([rec(3, section_number="2")], self.dir)
        live = [s for s in rows if s["active"] == "1"]
        self.assertEqual(len(live), 1)
        self.assertNotIn(live[0]["section_id"], self.old_ids)

    def test_without_the_flag_nothing_is_retired(self):
        text, _, rows, _ = run_numbered([rec(3, section_number="1")], self.dir)
        self.assertNotIn("Retired", text)
        self.assertEqual({s["retired"] for s in rows}, {"0"})
        kept = [s for s in rows if s["active"] == "1"]
        self.assertEqual(len(kept), 1)
        self.assertIn(kept[0]["section_id"], self.old_ids)       # the old rule still applies


# ---------- 6-9. the real Spring 2027 sheet ----------

class RealSheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = cls.tmp.name
        cls.first, cls.first_skipped = importer.run(FIXTURE, out_dir=cls.out, report_path=os.path.join(cls.out, "r1.txt"))
        cls.files = {n: read_text(os.path.join(cls.out, f"{n}.csv")) for n in importer.TABLE_FIELDS}
        cls.second, cls.second_skipped = importer.run(FIXTURE, out_dir=cls.out, report_path=os.path.join(cls.out, "r2.txt"))
        courses = {r["course_id"]: r for r in read_table(cls.out, "courses")}
        cls.people = {r["professor_id"]: r for r in read_table(cls.out, "professors")}
        cls.meetings, cls.instructors = {}, {}
        for m in read_table(cls.out, "section_meetings"):
            cls.meetings.setdefault(m["section_id"], []).append(m)
        for i in read_table(cls.out, "section_instructors"):
            cls.instructors.setdefault(i["section_id"], []).append(i)
        cls.sections = read_table(cls.out, "sections")
        cls.by_key = {(courses[s["course_id"]]["subject"], courses[s["course_id"]]["catalog_num"], s["section_number"]): s
                      for s in cls.sections}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def meet(self, key):
        return [(m["day_code"], m["start_min"], m["end_min"], m["building"], m["room"], m["is_online"])
                for m in self.meetings[self.by_key[key]["section_id"]]]

    def names(self, key):
        return [f"{self.people[i['professor_id']]['first_name']} {self.people[i['professor_id']]['last_name']}"
                for i in self.instructors.get(self.by_key[key]["section_id"], [])]

    def test_totals_match_the_sheet(self):
        self.assertEqual(self.first_skipped, 0)
        self.assertEqual(len(self.sections), 2284)
        self.assertEqual(len(read_table(self.out, "courses")), 777)
        self.assertEqual(sum(len(v) for v in self.meetings.values()), 3203)
        counts = {0: sum(1 for s in self.sections if s["section_id"] not in self.meetings)}
        for ms in self.meetings.values():
            counts[len(ms)] = counts.get(len(ms), 0) + 1
        self.assertEqual(counts, {0: 108, 1: 1439, 2: 447, 3: 290})
        timed = {sid: [m for m in ms if m["is_online"] == "0"] for sid, ms in self.meetings.items()}
        self.assertEqual(sum(1 for t in timed.values() if not t), 411)                                  # online only
        self.assertEqual(sum(1 for sid, t in timed.items() if t and len(t) < len(self.meetings[sid])), 151)   # hybrid
        self.assertEqual(sum(1 for s in self.sections if "/" in s["seats_text"]), 244)
        self.assertEqual(sum(1 for v in self.instructors.values() if len(v) > 1), 165)
        self.assertEqual(sum(1 for s in self.sections if s["section_id"] not in self.instructors), 511)
        self.assertEqual(sum(1 for s in self.sections if s["seats_total"] == ""), 269)
        self.assertEqual(len(self.people), 652)
        for line in ("Rows read:                 2284", "Meetings written:          3203", "Online-only sections:      411",
                     "Hybrid sections:           151", "No schedule yet:           108", "Seats with slashes:        244",
                     "Skipped rows:              0"):
            self.assertIn(line, self.first)

    def test_soc_101_section_6(self):
        self.assertEqual(self.meet(("SOC", "101", "06")),
                         [("W", "780", "830", "LH", "256", "0"), ("MW", "720", "770", "GMCS", "333", "0")])
        s = self.by_key[("SOC", "101", "06")]
        self.assertEqual((s["seats_text"], s["seats_total"]), ("30 / 180", "30"))

    def test_cs_200_section_1(self):
        self.assertEqual(self.meet(("CS", "200", "01")),
                         [("MW", "840", "915", "LH", "439", "0"), ("Th", "510", "640", "GMCS", "425", "0")])
        self.assertEqual(self.by_key[("CS", "200", "01")]["seats_total"], "48")

    def test_pa_301_has_no_schedule_yet(self):
        s = self.by_key[("PA", "301", "01")]
        self.assertNotIn(s["section_id"], self.meetings)
        self.assertNotIn(s["section_id"], self.instructors)
        self.assertEqual((s["days"], s["seats_total"], s["active"]), ("", "", "1"))

    def test_music_351_sections_have_their_own_titles(self):
        titles = [s["section_title"] for k, s in self.by_key.items() if k[:2] == ("MUSIC", "351")]
        self.assertEqual(len(titles), 9)
        self.assertTrue(all(t.startswith("Music and Culture: ") for t in titles), titles)
        self.assertGreater(len(set(titles)), 1)   # some topics run in more than one section
        self.assertNotIn("two titles", self.first)

    def test_one_time_two_rooms(self):
        self.assertEqual(self.meet(("POLS", "201", "01")),
                         [("TTh", "840", "915", "SH", "101", "0"), ("TTh", "840", "915", "HH", "218", "0")])

    def test_live_online_class_at_a_set_time_is_timed(self):
        self.assertEqual(self.meet(("GENS", "420", "01")), [("W", "960", "1120", "ONLINE", "", "0")])

    def test_tfm_270_section_1(self):
        s = self.by_key[("TFM", "270", "01")]
        self.assertEqual((s["seats_text"], s["seats_total"]), ("100 / 25", "25"))
        self.assertEqual([(d, b, r) for d, _, _, b, r, _ in self.meet(("TFM", "270", "01"))], [("W", "BT", "161"), ("MF", "COM", "206")])

    def test_psy_407_at_southwestern_college(self):
        self.assertEqual(self.meet(("PSY", "407", "01")), [("TTh", "840", "915", "Southwestern College", "", "0")])

    def test_gens_420_two_instructors(self):
        self.assertTrue(any(len(self.names(k)) == 2 for k in self.by_key if k[:2] == ("GENS", "420")))
        self.assertEqual(self.names(("GENS", "420", "01")), ["Diana Carson", "Rachel Cuesta"])

    def test_chem_100_two_meetings(self):
        self.assertEqual(len(self.meet(("CHEM", "100", "01"))), 2)

    def test_rooms_keep_leading_zeros(self):
        rooms = {r["room_number"] for r in read_table(self.out, "rooms")}
        self.assertIn("060", rooms)
        self.assertIn("003", rooms)

    def test_second_run_changes_nothing(self):
        self.assertEqual(self.second_skipped, 0)
        for line in ("created:                 0", "updated:                 0", "unchanged:               2284",
                     "no longer in the sheet:  0", "Files changed:             no"):
            self.assertIn(line, self.second)
        for name, text in self.files.items():
            self.assertEqual(read_text(os.path.join(self.out, f"{name}.csv")), text, name)

    def test_import_records_todays_date(self):
        with open(os.path.join(self.out, "data_info.json"), encoding="utf-8") as f:
            self.assertEqual(json.load(f), {"updated": datetime.date.today().isoformat()})


if __name__ == "__main__":
    unittest.main()

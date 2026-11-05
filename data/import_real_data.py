"""
Turns the team's filled-in workbook (sheet "Sections") into the CSV files the
database loads, so nobody has to deal with ids.

Usage (from the project root):
    python3 data/import_real_data.py path/to/EzClass_Data_Template.xlsx
    python3 data/import_real_data.py my_rows.csv          # a CSV also works

Only the Sections sheet is read, columns A to N, data from row 3 (row 2 is
the gray example row). Output goes to data/cleaned/:
    professors.csv, rooms.csv, courses.csv, sections.csv,
    section_meetings.csv, section_instructors.csv, data_info.json
and the run's report to data/import_report.txt. Then load them with:
    python3 backend/models/db.py data/cleaned

One row is one section a student picks. A section can meet more than once
(lecture + lab), written with " / " between the parts:
  - Days, Start, End, Building, Room: one part per meeting, or one part that
    applies to every timed meeting. "ONLINE" in Days is a meeting with no
    day, time or room.
  - Professor First / Last Name: one part per component (not per meeting),
    zipped into people. A section lists every person once.
  - Seats: one number per component. The section's seat count is the
    smallest, since a student needs a seat in every part.
  - Days, Start, End, Building and Room all empty: a section whose schedule
    isn't entered yet. It is imported with no meetings ("Time not listed yet").
A course has one title, except special-topics courses (SPECIAL_TOPICS below)
where every section has its own. Any other course with two titles is
reported (each section still keeps the title typed in its row).
A row whose parts don't line up is skipped (with its row number); the rest
still import, and the script exits with status 1 at the end.

Ids stay the same between imports, because students' saved plans remember
sections by id. Always import on top of the current data/cleaned/ files:
  - a section is the same section when subject, course number, section and
    term match. A blank Section cell (new rows go at the bottom) gets the next
    unused number for that course, or the number it got last time if the
    row's meetings, people and seats are the same.
  - a section that is no longer in the sheet is kept with active = 0, so its
    id is never handed to a different class (and it comes back if the row does).
  - courses, professors and rooms keep their ids too.
Running it twice on the same file changes nothing.

The importer never "fixes" a day, time, room or name. Anything odd is
reported; the team fixes the workbook.
"""

import collections
import csv
import datetime
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(BASE, "data", "cleaned")
REPORT_PATH = os.path.join(BASE, "data", "import_report.txt")

COLUMNS = ["term", "subject", "catalog_num", "course_title", "units",
           "section_number", "days", "start_time", "end_time",
           "professor_first", "professor_last", "building", "room_number",
           "seats"]
# Headers in the workbook are friendly ("Course Number (e.g. 150)"). Only the
# part before the first " (" is used to find the column, so the hint text can
# change. The old code-style names still work too.
FRIENDLY = {
    "term": "term", "subject": "subject", "course number": "catalog_num",
    "course title": "course_title", "units": "units", "section": "section_number",
    "days": "days", "start time": "start_time", "end time": "end_time",
    "professor first name": "professor_first", "professor last name": "professor_last",
    "building": "building", "room number": "room_number", "seats": "seats", "capacity": "seats",
}

SPLIT = re.compile(r"\s*/\s*")
DAY_TOKEN = re.compile(r"Th|Sa|Su|M|T|W|F")
ONLINE = "ONLINE"
# Days / Building values that mean "no set day, time or room"
NO_SET_TIME = {"ONLINE", "ASYNC", "ASYNCHRONOUS", "ARRANGED", "TBA"}
NOT_A_PROFESSOR = {"to be announced", "to be", "tba", "tbd", "staff", "instructor", "tba tba", "staff staff"}
MAX_SEATS = 999   # more than this is probably two numbers typed without the slash
MEETING_COLUMNS = ("days", "start_time", "end_time", "building", "room_number")
# special-topics courses: each section has its own title ("Music and Culture: Hip Hop")
SPECIAL_TOPICS = {("MUSIC", "351")}


def header_key(text):
    base = text.split(" (")[0].strip().lower()
    return FRIENDLY.get(base, text.strip())


class RowProblem(Exception):
    """The row can't be imported as it is; the message says why."""


class Report:
    """Everything the run noticed, grouped, with sheet row numbers."""

    def __init__(self):
        self.skipped = []                                     # (row, reason)
        self.warnings = collections.defaultdict(list)         # kind -> [(row, detail)]
        self.normalized = collections.defaultdict(list)       # kind -> [row]

    def warn(self, kind, row, detail=""):
        self.warnings[kind].append((row, detail))

    def normalize(self, kind, row):
        self.normalized[kind].append(row)


# ---------- reading ----------

def cell_text(value, column, row, report):
    """A cell as text. Numbers typed into text columns keep their digits."""
    if value is None:
        return ""
    if isinstance(value, datetime.time):
        return f"{value.hour:02d}:{value.minute:02d}"
    if isinstance(value, datetime.datetime):
        return f"{value.hour:02d}:{value.minute:02d}"
    if isinstance(value, float) and value == int(value):
        value = int(value)
    if isinstance(value, int) and column in ("building", "room_number", "catalog_num"):
        report.warn(f"{column} stored as a number (leading zeros may be lost)", row, str(value))
    return str(value).strip()


def read_rows(path, report):
    """List of dicts keyed by COLUMNS (all text) plus "_row", the sheet row number."""
    if path.lower().endswith(".xlsx"):
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        ws = wb["Sections"]
        table = list(ws.iter_rows(min_row=1, max_col=len(COLUMNS), values_only=True))
        header, first_data = table[0], 3         # row 2 is the gray example row
    else:
        with open(path, newline="", encoding="utf-8-sig") as f:
            table = list(csv.reader(f))
        header, first_data = table[0], 2
    header = [header_key(str(h)) if h is not None else "" for h in header]
    missing = [c for c in COLUMNS if c not in header]
    if missing:
        sys.exit(f"Missing column(s) in the sheet header: {', '.join(missing)}")
    rows = []
    for i, values in enumerate(table[first_data - 1:], start=first_data):
        rec = {h: cell_text(v, h, i, report) for h, v in zip(header, values) if h in COLUMNS}
        if not any(rec.get(c) for c in COLUMNS):
            continue                                       # blank row
        if rec.get("term", "").upper().startswith("EXAMPLE"):
            continue                                       # an example row
        rec["_row"] = i
        rows.append(rec)
    return rows


# ---------- one row ----------

def parts(text):
    """'09:30 / ' -> ['09:30', '']. An empty cell is one empty part."""
    return SPLIT.split(text.strip()) if text.strip() else [""]


def to_minutes(text):
    """'09:30' or '9:30' -> 570. None if it isn't a time."""
    m = re.fullmatch(r"(\d{1,2}):(\d{2})(?::\d{2})?", text.strip())
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    return h * 60 + mi if h <= 23 and mi <= 59 else None


def day_tokens(text):
    """'TTh' -> ['T', 'Th']; None if any letter isn't a day (M T W Th F Sa Su)."""
    tokens = DAY_TOKEN.findall(text)
    return tokens if tokens and "".join(tokens) == text else None


def per_meeting(column, values, n):
    """One part for every meeting, or one part per meeting."""
    if len(values) == 1:
        return values * n
    if len(values) == n:
        return values
    raise RowProblem(f"{column} has {len(values)} parts but Days has {n}")


def parse_meetings(rec, report):
    row = rec["_row"]
    if not any(rec[c] for c in MEETING_COLUMNS):
        return []                 # schedule not entered yet; the team fills it in later
    if not rec["days"]:
        raise RowProblem("Days is empty but Start, End, Building or Room has a value")
    days = parts(rec["days"])
    n = len(days)
    starts, ends = parts(rec["start_time"]), parts(rec["end_time"])
    buildings, rooms = parts(rec["building"]), parts(rec["room_number"])
    # one part shared by several meetings applies to the timed ones; online meetings have no time or room
    shared = {"Start": len(starts) == 1 < n, "End": len(ends) == 1 < n,
              "Building": len(buildings) == 1 < n, "Room": len(rooms) == 1 < n}
    starts, ends = per_meeting("Start", starts, n), per_meeting("End", ends, n)
    buildings, rooms = per_meeting("Building", buildings, n), per_meeting("Room", rooms, n)

    meetings = []
    for i, (day, start, end, building, room) in enumerate(zip(days, starts, ends, buildings, rooms)):
        label = f"meeting {i + 1}" if n > 1 else "the meeting"
        day = day.replace(" ", "")
        if day.upper() in NO_SET_TIME:
            if day.upper() != ONLINE:
                report.normalize(f"{day} -> ONLINE (Days)", row)
            if (start or end) and not (shared["Start"] and shared["End"]):
                raise RowProblem(f"{label} is ONLINE but has a time ({start}-{end})")
            if building.upper() in NO_SET_TIME and building.upper() != ONLINE:
                report.normalize(f"{building} -> ONLINE (Building)", row)
            elif building and building.upper() != ONLINE and not shared["Building"]:
                report.warn("online meeting with a building", row, f"{label}: {building}")
            meetings.append({"day_code": "", "start_min": None, "end_min": None,
                             "building": ONLINE, "room": "", "is_online": 1})
            continue
        if not day:
            raise RowProblem(f"{label} has no days")
        if day_tokens(day) is None:
            raise RowProblem(f"{label}: days '{day}' not understood (use M T W Th F Sa Su, like MWF or TTh)")
        start_min, end_min = to_minutes(start), to_minutes(end)
        if start_min is None or end_min is None:
            raise RowProblem(f"{label} ({day}) needs a start and end time like 14:30 (got '{start}' to '{end}')")
        if start_min >= end_min:
            raise RowProblem(f"{label} ({day}) ends before it starts ({start}-{end})")
        if building.upper() in NO_SET_TIME:
            # a live online class at a set time: on the calendar, no room on campus
            if building.upper() != ONLINE:
                report.normalize(f"{building} -> ONLINE (Building)", row)
            report.warn("set day and time but Building ONLINE (live online class?)", row, f"{label}: {day} {start}-{end}")
            building = ONLINE
        elif not building:
            report.warn("timed meeting with no building", row, f"{label}: {day} {start}-{end}")
        meetings.append({"day_code": day, "start_min": start_min, "end_min": end_min,
                         "building": building, "room": room, "is_online": 0})
    return meetings


def parse_instructors(rec, report):
    """[(first, last), ...] without repeats (same name in any case = same person)."""
    row = rec["_row"]
    firsts, lasts = parts(rec["professor_first"]), parts(rec["professor_last"])
    if len(firsts) != len(lasts):
        raise RowProblem(f"Professor First Name has {len(firsts)} parts but Last Name has {len(lasts)}")
    people, seen = [], set()
    for first, last in zip(firsts, lasts):
        if not first and not last:
            continue
        if f"{first} {last}".strip().lower() in NOT_A_PROFESSOR:
            report.normalize("placeholder professor name -> no professor", row)
            continue
        if not (first and last):
            raise RowProblem(f"professor '{first or last}' needs both a first and a last name")
        key = (first.casefold(), last.casefold())
        if key not in seen:
            seen.add(key)
            people.append((first, last))
    return people


def parse_seats(rec, report):
    """(text as typed, smallest part as a number or None)."""
    text = rec["seats"]
    if not text:
        return "", None
    numbers = []
    for part in parts(text):
        if not part:
            continue
        if not part.isdigit():
            raise RowProblem(f"Seats '{text}' must be whole numbers separated by ' / '")
        numbers.append(int(part))
    if any(n > MAX_SEATS for n in numbers):
        report.warn(f"seats over {MAX_SEATS} (two numbers without a slash?)", rec["_row"], text)
        return text, None
    if "/" in text:
        report.normalize("seats with slashes (smallest part used)", rec["_row"])
    return text, (min(numbers) if numbers else None)


def parse_row(rec, report):
    """One sheet row -> one section dict. Raises RowProblem if it can't be imported."""
    for col, label in (("term", "Term"), ("subject", "Subject"), ("catalog_num", "Course Number"),
                       ("course_title", "Course Title"), ("units", "Units")):
        if not rec.get(col):
            raise RowProblem(f"{label} is empty")
    if not rec["units"].isdigit():
        raise RowProblem(f"Units '{rec['units']}' must be a whole number")
    number = rec["section_number"]
    if number and not number.isdigit():
        raise RowProblem(f"Section '{number}' must be a number")
    seats_text, seats_total = parse_seats(rec, report)
    return {
        "_row": rec["_row"],
        "term": rec["term"],
        "subject": "".join(rec["subject"].split()).upper(),
        "catalog_num": "".join(rec["catalog_num"].split()).upper(),
        "title": rec["course_title"],
        "units": int(rec["units"]),
        "section_number": number.zfill(2) if number else "",
        "meetings": parse_meetings(rec, report),
        "instructors": parse_instructors(rec, report),
        "seats_text": seats_text,
        "seats_total": seats_total,
    }


# ---------- the last import ----------

def section_key(subject, catalog_num, section_number, term):
    """What makes a section the same section from one import to the next."""
    return ("".join(str(subject).split()).upper(), str(catalog_num).strip().upper(),
            str(section_number).strip(), str(term).strip())


def read_csv(path):
    if not os.path.exists(path):
        return None
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def content(meetings, instructors, seats_text, title=""):
    """What a section is, apart from its id: compared to tell 'unchanged' from 'updated'."""
    return (tuple((m["day_code"], m["start_min"], m["end_min"], m["building"], m["room"], m["is_online"])
                  for m in meetings),
            tuple(instructors), seats_text, title)


def _int(value):
    return int(value) if str(value or "").strip().lstrip("-").isdigit() else None


def load_previous(out_dir=OUT_DIR):
    """
    The ids and contents from the current data/cleaned files. Works with the
    older one-meeting format too (no section_meetings.csv yet), so the first
    import in the new format keeps every id.
    """
    prev = {"courses": {}, "professors": {}, "rooms": {}, "sections": {}, "highest": 0,
            "course_highest": 0, "prof_highest": 0, "room_highest": 0}
    courses = read_csv(os.path.join(out_dir, "courses.csv"))
    sections = read_csv(os.path.join(out_dir, "sections.csv"))
    if not courses or sections is None:
        return prev
    by_course_id = {}
    for c in courses:
        cid = int(c["course_id"])
        key = ("".join(c["subject"].split()).upper(), c["catalog_num"].strip().upper())
        prev["courses"][key] = {"id": cid, "title": c["title"], "units": c["units"], "row": c}
        by_course_id[c["course_id"]] = key
        prev["course_highest"] = max(prev["course_highest"], cid)
    names = {}
    for p in read_csv(os.path.join(out_dir, "professors.csv")) or []:
        pid = int(p["professor_id"])
        prev["professors"][(p["first_name"].casefold(), p["last_name"].casefold())] = pid
        names[p["professor_id"]] = (p["first_name"], p["last_name"])
        prev["prof_highest"] = max(prev["prof_highest"], pid)
    rooms = {}
    for r in read_csv(os.path.join(out_dir, "rooms.csv")) or []:
        rid = int(r["room_id"])
        prev["rooms"][(r["building"], r["room_number"])] = rid
        rooms[r["room_id"]] = (r["building"], r["room_number"])
        prev["room_highest"] = max(prev["room_highest"], rid)

    meetings = collections.defaultdict(list)
    for m in read_csv(os.path.join(out_dir, "section_meetings.csv")) or []:
        meetings[m["section_id"]].append((int(m["idx"]), {
            "day_code": m["day_code"], "start_min": _int(m["start_min"]), "end_min": _int(m["end_min"]),
            "building": m["building"], "room": m["room"], "is_online": int(m["is_online"] or 0)}))
    people = collections.defaultdict(list)
    for si in read_csv(os.path.join(out_dir, "section_instructors.csv")) or []:
        if si["professor_id"] in names:
            people[si["section_id"]].append((int(si["idx"]), names[si["professor_id"]]))

    for s in sections:
        sid = int(s["section_id"])
        prev["highest"] = max(prev["highest"], sid)
        if s["course_id"] not in by_course_id:
            continue
        subject, catalog = by_course_id[s["course_id"]]
        key = section_key(subject, catalog, s["section_number"], s["term"])
        if s["section_id"] in meetings:
            mlist = [m for _, m in sorted(meetings[s["section_id"]], key=lambda x: x[0])]
        elif s.get("days"):                               # older one-meeting format
            building, room = rooms.get(s.get("room_id") or "", ("", ""))
            mlist = [{"day_code": s["days"], "start_min": _minutes_or_none(s["start_time"]),
                      "end_min": _minutes_or_none(s["end_time"]), "building": building, "room": room, "is_online": 0}]
        else:
            mlist = []
        if s["section_id"] in people:
            plist = [p for _, p in sorted(people[s["section_id"]])]
        else:
            plist = [names[s["professor_id"]]] if s.get("professor_id") in names else []
        seats_text = s.get("seats_text", s.get("capacity", "")) or ""
        prev["sections"][key] = {"id": sid, "active": s.get("active", "1") != "0", "row": s, "meetings": mlist,
                                 "content": content(mlist, plist, seats_text, s.get("section_title", ""))}
    return prev


def _minutes_or_none(text):
    return to_minutes(text) if text else None


# ---------- building the tables ----------

def hhmm(minutes):
    return "" if minutes is None else f"{minutes // 60:02d}:{minutes % 60:02d}"


class IdMap:
    """Ids that stay the same: known keys keep theirs, new keys count up from the highest."""

    def __init__(self, known, highest):
        self.known, self.next, self.used = dict(known), highest, {}

    def get(self, key):
        if key not in self.used:
            if key in self.known:
                self.used[key] = self.known[key]
            else:
                self.next += 1
                self.used[key] = self.next
        return self.used[key]


def assign_section_numbers(sections, prev, report):
    """Fills in blank Section cells (see the module docstring)."""
    taken = collections.defaultdict(set)      # (term, subject, catalog) -> numbers used anywhere
    for s in sections:
        if s["section_number"]:
            taken[(s["term"], s["subject"], s["catalog_num"])].add(int(s["section_number"]))
    claimed = {section_key(s["subject"], s["catalog_num"], s["section_number"], s["term"])
               for s in sections if s["section_number"]}
    leftovers = collections.defaultdict(list)  # earlier sections no filled-in row claims
    for key, p in prev["sections"].items():
        subject, catalog, number, term = key
        if number.isdigit():
            taken[(term, subject, catalog)].add(int(number))
        if key not in claimed:
            leftovers[(term, subject, catalog)].append((number, p["content"]))
    for s in sections:
        if s["section_number"]:
            continue
        course = (s["term"], s["subject"], s["catalog_num"])
        mine = content(s["meetings"], s["instructors"], s["seats_text"],
                       s["title"] if (s["subject"], s["catalog_num"]) in SPECIAL_TOPICS else "")
        match = next((i for i, (_, c) in enumerate(leftovers[course]) if c == mine), None)
        if match is not None:
            s["section_number"] = leftovers[course].pop(match)[0]
        else:
            number = max(taken[course], default=0) + 1
            taken[course].add(number)
            s["section_number"] = str(number).zfill(2)
        report.warn("Section was blank, number filled in (type it into the sheet)", s["_row"],
                    f"{s['subject']} {s['catalog_num']} section {s['section_number']}")


def shared_title(titles):
    """'Music and Culture: Hip Hop', 'Music and Culture: Jazz' -> 'Music and Culture' (whole words only)."""
    prefix = os.path.commonprefix(titles)
    if any(len(t) > len(prefix) and t[len(prefix)].isalnum() for t in titles):
        prefix = prefix.rsplit(" ", 1)[0] if " " in prefix else ""   # don't cut a word in half
    return prefix.rstrip(" :-–—") or titles[0]


def build_tables(sections, prev, report):
    """The CSV rows for every table, plus counts for the report."""
    terms = {s["term"] for s in sections}
    course_ids = IdMap({k: v["id"] for k, v in prev["courses"].items()}, prev["course_highest"])
    prof_ids = IdMap(prev["professors"], prev["prof_highest"])
    room_ids = IdMap(prev["rooms"], prev["room_highest"])
    section_ids = IdMap({k: v["id"] for k, v in prev["sections"].items()}, prev["highest"])

    courses, course_seen = {}, {}
    professors, rooms = {}, {}
    # a special-topics course is called by what its sections' titles share
    topics = collections.defaultdict(list)
    for s in sections:
        if (s["subject"], s["catalog_num"]) in SPECIAL_TOPICS:
            topics[(s["subject"], s["catalog_num"])].append(s["title"])
    topic_titles = {k: shared_title(v) for k, v in topics.items()}
    out_sections, out_meetings, out_instructors = [], [], []
    counts = collections.Counter()

    for s in sections:
        ckey = (s["subject"], s["catalog_num"])
        cid = course_ids.get(ckey)
        if ckey not in courses:
            courses[ckey] = {"course_id": cid, "subject": s["subject"], "catalog_num": s["catalog_num"],
                             "title": topic_titles.get(ckey, s["title"]), "units": s["units"], "description": ""}
            course_seen[ckey] = s["_row"]
            old = prev["courses"].get(ckey)
            title_changed = old and old["title"] != s["title"] and ckey not in SPECIAL_TOPICS
            if old and (title_changed or str(old["units"]) != str(s["units"])):
                report.warn("course title or units changed since the last import", s["_row"],
                            f"{s['subject']} {s['catalog_num']}: '{old['title']}' {old['units']} -> '{s['title']}' {s['units']}")
        elif courses[ckey]["units"] != s["units"] or (courses[ckey]["title"] != s["title"] and ckey not in SPECIAL_TOPICS):
            report.warn("two titles or unit values for one course", s["_row"],
                        f"{s['subject']} {s['catalog_num']}: row {course_seen[ckey]} says "
                        f"'{courses[ckey]['title']}' {courses[ckey]['units']}, this row '{s['title']}' {s['units']}")
        # a section keeps its own title when it isn't the course's (always, for special topics)
        own_title = s["title"] if ckey in SPECIAL_TOPICS or s["title"] != courses[ckey]["title"] else ""
        counts["own_title"] += bool(own_title)

        key = section_key(s["subject"], s["catalog_num"], s["section_number"], s["term"])
        sid = section_ids.get(key)
        before = prev["sections"].get(key)
        mine = content(s["meetings"], s["instructors"], s["seats_text"], own_title)
        if before is None:
            counts["created"] += 1
        elif before["content"] == mine and before["active"]:
            counts["unchanged"] += 1
        else:
            counts["updated"] += 1

        people = []
        for i, (first, last) in enumerate(s["instructors"]):
            pkey = (first.casefold(), last.casefold())
            pid = prof_ids.get(pkey)
            professors.setdefault(pkey, {"professor_id": pid, "first_name": first, "last_name": last,
                                         "email": "", "department": "Unknown"})
            people.append(pid)
            out_instructors.append({"section_id": sid, "professor_id": pid, "idx": i})

        first_timed = next((m for m in s["meetings"] if not m["is_online"]), None)
        first_room = ""
        for i, m in enumerate(s["meetings"]):
            out_meetings.append({"section_id": sid, "idx": i, "day_code": m["day_code"],
                                 "start_min": "" if m["start_min"] is None else m["start_min"],
                                 "end_min": "" if m["end_min"] is None else m["end_min"],
                                 "building": m["building"], "room": m["room"], "is_online": m["is_online"]})
            if not m["is_online"] and m["building"]:
                rkey = (m["building"], m["room"])
                rid = room_ids.get(rkey)
                rooms.setdefault(rkey, {"room_id": rid, "building": m["building"], "room_number": m["room"], "capacity": ""})
                if m is first_timed:
                    first_room = rid

        counts["meetings"] += len(s["meetings"])
        if not s["meetings"]:
            counts["no_schedule"] += 1
        elif first_timed is None:
            counts["online_only"] += 1
        elif any(m["is_online"] for m in s["meetings"]):
            counts["hybrid"] += 1
        # the older one-meeting columns, from the first timed meeting, so older code keeps working
        out_sections.append({
            "section_id": sid, "course_id": cid,
            "professor_id": people[0] if people else "", "room_id": first_room,
            "section_number": s["section_number"], "term": s["term"],
            "days": first_timed["day_code"] if first_timed else "",
            "start_time": hhmm(first_timed["start_min"]) if first_timed else "",
            "end_time": hhmm(first_timed["end_min"]) if first_timed else "",
            "capacity": "" if s["seats_total"] is None else s["seats_total"],
            "seats_text": s["seats_text"],
            "seats_total": "" if s["seats_total"] is None else s["seats_total"],
            "active": 1,
            "section_title": own_title,
        })

    # sections from the last import that aren't in the sheet: kept, marked inactive
    in_sheet = {section_key(s["subject"], s["catalog_num"], s["section_number"], s["term"]) for s in sections}
    gone = []
    for key, p in sorted(prev["sections"].items(), key=lambda kv: kv[1]["id"]):
        if key in in_sheet:
            continue
        row = p["row"]
        ckey = key[:2]
        if ckey not in courses:          # keep its course so the key is still known next time
            c = prev["courses"][ckey]["row"]
            courses[ckey] = {"course_id": int(c["course_id"]), "subject": c["subject"], "catalog_num": c["catalog_num"],
                             "title": c["title"], "units": c["units"], "description": c.get("description", "")}
        if key[3] not in terms:
            counts["other_terms"] += 1
        elif p["active"]:
            gone.append(f"{key[0]} {key[1]} section {key[2]} (id {p['id']})")
        else:
            counts["still_inactive"] += 1
        out_sections.append({
            "section_id": p["id"], "course_id": courses[ckey]["course_id"], "professor_id": "", "room_id": "",
            "section_number": key[2], "term": key[3], "days": row.get("days", ""),
            "start_time": row.get("start_time", ""), "end_time": row.get("end_time", ""),
            "capacity": row.get("capacity", ""), "seats_text": row.get("seats_text", row.get("capacity", "")) or "",
            "seats_total": row.get("seats_total", row.get("capacity", "")) or "",
            # other terms aren't this sheet's business: they keep whatever they had
            "active": 0 if key[3] in terms else (1 if p["active"] else 0),
            "section_title": row.get("section_title", ""),
        })
        for i, m in enumerate(p["meetings"]):   # its meetings are kept as they were
            out_meetings.append({"section_id": p["id"], "idx": i, "day_code": m["day_code"],
                                 "start_min": "" if m["start_min"] is None else m["start_min"],
                                 "end_min": "" if m["end_min"] is None else m["end_min"],
                                 "building": m["building"], "room": m["room"], "is_online": m["is_online"]})
    counts["professors_created"] = sum(1 for k in professors if k not in prev["professors"])
    counts["courses"] = len({(s["subject"], s["catalog_num"]) for s in sections})
    return {
        "professors": sorted(professors.values(), key=lambda r: r["professor_id"]),
        "rooms": sorted(rooms.values(), key=lambda r: r["room_id"]),
        "courses": sorted(courses.values(), key=lambda r: r["course_id"]),
        "sections": out_sections,
        "section_meetings": out_meetings,
        "section_instructors": out_instructors,
    }, counts, gone


TABLE_FIELDS = {
    "professors": ["professor_id", "first_name", "last_name", "email", "department"],
    "rooms": ["room_id", "building", "room_number", "capacity"],
    "courses": ["course_id", "subject", "catalog_num", "title", "units", "description"],
    "sections": ["section_id", "course_id", "professor_id", "room_id", "section_number", "term",
                 "days", "start_time", "end_time", "capacity", "seats_text", "seats_total", "active", "section_title"],
    "section_meetings": ["section_id", "idx", "day_code", "start_min", "end_min", "building", "room", "is_online"],
    "section_instructors": ["section_id", "professor_id", "idx"],
}


def csv_text(fields, rows):
    import io
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def write_tables(tables, out_dir=OUT_DIR):
    """Writes every CSV. Returns True if any file's contents changed."""
    os.makedirs(out_dir, exist_ok=True)
    changed = False
    for name, fields in TABLE_FIELDS.items():
        path = os.path.join(out_dir, f"{name}.csv")
        text = csv_text(fields, tables[name])
        try:
            # git on Windows may have checked the file out with \r\n; that isn't a change
            with open(path, encoding="utf-8", newline="") as f:
                same = f.read().replace("\r\n", "\n") == text
        except OSError:
            same = False
        if not same:
            changed = True
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(text)
    if changed or not os.path.exists(os.path.join(out_dir, "data_info.json")):
        # the site shows this as "Class data last updated ..."
        with open(os.path.join(out_dir, "data_info.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump({"updated": datetime.date.today().isoformat()}, f)
            f.write("\n")
    return changed


# ---------- the report ----------

def rows_text(rows, limit=40):
    rows = sorted(set(rows))
    text = ", ".join(str(r) for r in rows[:limit])
    return text + (f" ... and {len(rows) - limit} more" if len(rows) > limit else "")


def report_text(source, rows_read, sections, counts, gone, report, changed):
    multi_seat = sum(1 for s in sections if "/" in s["seats_text"])
    lines = [
        f"EzClass import of {os.path.basename(source)}",
        "",
        f"Rows read:                 {rows_read}",
        f"Sections imported:         {len(sections)}  (courses: {counts['courses']})",
        f"  created:                 {counts['created']}",
        f"  updated:                 {counts['updated']}",
        f"  unchanged:               {counts['unchanged']}",
        f"  no longer in the sheet:  {len(gone)}  (kept, marked inactive)",
        f"  still inactive:          {counts['still_inactive']}  (gone before this run too)",
        *([f"  other terms, untouched:  {counts['other_terms']}"] if counts["other_terms"] else []),
        f"Meetings written:          {counts['meetings']}",
        f"Online-only sections:      {counts['online_only']}",
        f"Hybrid sections:           {counts['hybrid']}  (some meetings online)",
        f"No schedule yet:           {counts['no_schedule']}  (no days, times or rooms entered)",
        f"Sections with own title:   {counts['own_title']}  (special topics: "
        f"{', '.join(' '.join(k) for k in sorted(SPECIAL_TOPICS))})",
        f"Instructors created:       {counts['professors_created']}",
        f"Seats with slashes:        {multi_seat}",
        f"Sections with no seats:    {sum(1 for s in sections if s['seats_total'] is None)}",
        f"Skipped rows:              {len(report.skipped)}",
        f"Files changed:             {'yes' if changed else 'no, data/cleaned is already up to date'}",
    ]
    lines += ["", "Normalizations applied:"]
    lines += [f"  {kind}: {len(rows)} (rows {rows_text(rows)})" for kind, rows in sorted(report.normalized.items())] or ["  none"]
    lines += ["", "Warnings:"]
    if not report.warnings:
        lines.append("  none")
    for kind, items in sorted(report.warnings.items()):
        lines.append(f"  {kind}: {len(items)}")
        lines += [f"    row {row}: {detail}" if detail else f"    row {row}" for row, detail in sorted(items)]
    lines += ["", "Skipped rows (fix them in the sheet, then run again):"]
    lines += [f"  row {row}: {reason}" for row, reason in sorted(report.skipped)] or ["  none"]
    lines += ["", "No longer in the sheet (marked inactive; they come back if the row does):"]
    lines += [f"  {g}" for g in gone] or ["  none"]
    return "\n".join(lines) + "\n"


def run(source, out_dir=OUT_DIR, report_path=REPORT_PATH):
    """The whole import. Returns (report text, number of skipped rows)."""
    report = Report()
    rows = read_rows(source, report)
    sections, seen = [], {}
    for rec in rows:
        try:
            s = parse_row(rec, report)
        except RowProblem as problem:
            report.skipped.append((rec["_row"], str(problem)))
            continue
        if s["section_number"]:
            key = section_key(s["subject"], s["catalog_num"], s["section_number"], s["term"])
            if key in seen:
                report.skipped.append((rec["_row"], f"same course and section as row {seen[key]} "
                                                    f"({s['subject']} {s['catalog_num']} section {s['section_number']})"))
                continue
            seen[key] = rec["_row"]
        sections.append(s)
    prev = load_previous(out_dir)
    assign_section_numbers(sections, prev, report)
    tables, counts, gone = build_tables(sections, prev, report)
    changed = write_tables(tables, out_dir)
    text = report_text(source, len(rows), sections, counts, gone, report, changed)
    if report_path:
        with open(report_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    return text, len(report.skipped)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]   # --skip-problems is the default now
    if len(args) != 1:
        sys.exit(__doc__)
    text, skipped = run(args[0])
    print(text)
    print(f"Report saved to {os.path.relpath(REPORT_PATH, BASE)}")
    print("Next: python3 backend/models/db.py data/cleaned")
    if skipped:
        sys.exit(1)


if __name__ == "__main__":
    main()

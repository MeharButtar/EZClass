"""
Turns SDSU's official class schedule export (PeopleSoft "Sched of Classes",
one .xlsx sheet) into the Sections format data/import_real_data.py reads.

Usage (from the project root):
    python3 data/convert_sdsu_schedule.py data/source/SD_CLASS_SCHEDULE_RPT_PUBLIC_204541634.xlsx

Writes:
    data/source/<term>_sections.csv     e.g. spring2027_sections.csv
    data/schedule_convert_report.txt    what was kept, skipped and decided
Then:
    python3 data/import_real_data.py data/source/spring2027_sections.csv

The export has one row per instructor times meeting. One output row is one
Class Nbr (a section of one component). Same input, same output, byte for
byte: rows, meetings and people are written in a fixed order.

What it decides (every case is counted in the report, nothing is dropped
without a line there):
  - main campus (SDSU) only, status A only; thesis and individual study
    sections are skipped (is_thesis_like below)
  - meeting pattern letters M T W R F S become M T W Th F Sa; 06:00 PM -> 18:00
  - Facility ONLINE with a day and time stays a timed meeting in building
    ONLINE (a live online class); ONLINE or ASYN with no time is an online part
  - ARR (arranged) in an in-person section means no schedule ("Time not listed
    yet"); in an online or hybrid section it is an online part
  - GMCS428 -> building GMCS, room 428 (longest building code already known
    first); codes that don't split stay whole; OFFCSDSU -> "Off campus"
  - people: the full name from data/cleaned/professors.csv when the last name
    and first initial match exactly one person, else "L." + last name
  - titles: the current EzClass title when the course already exists, else
    the export's (a course with several titles keeps each section's own)
  - seats 0 or 999 are placeholders and left blank
  - two Class Nbrs with the same subject, number, section and term: the
    lowest is kept (the importer can't keep them apart)
Another export with different headers only needs SOURCE_COLUMNS changed.
"""

import collections
import csv
import datetime
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED_DIR = os.path.join(BASE, "data", "cleaned")
MAJORS_DIR = os.path.join(BASE, "data", "majors")
GE_DIR = os.path.join(BASE, "data", "ge")
OUT_DIR = os.path.join(BASE, "data", "source")
REPORT_PATH = os.path.join(BASE, "data", "schedule_convert_report.txt")

# our name -> the export's column header. Change only this for another export.
SOURCE_COLUMNS = {
    "campus": "Campus",
    "term": "Term",
    "session": "Session",
    "career": "Career",
    "class_nbr": "Class Nbr",
    "subject": "Subject",
    "catalog": "Catalog Nbr",
    "title": "Title",
    "section": "Class Section",
    "component": "Component",
    "units": "Component Units",
    "facility": "Facility ID",
    "start": "Meeting Start",
    "end": "Meeting End",
    "pattern": "Standard Meeting Pattern",
    "last": "Last Name",
    "initials": "Initials",
    "status": "Class Status",
    "capacity": "Enrollment Capacity",
    "mode": "Instruction Mode",
}
HEADER_MARK = "class_nbr"          # the header row is the first row with this column in it

KEEP_CAMPUS = {"SDSU"}
KEEP_STATUS = {"A"}
SEASONS = {"3": "Spring", "5": "Summer", "7": "Fall"}
DAY_LETTERS = {"M": "M", "T": "T", "W": "W", "R": "Th", "F": "F", "S": "Sa"}
NO_DAY_PATTERNS = {"", "ARR", "ASYN"}
ONLINE_MODES = {"ON", "HY", "OE"}  # online, hybrid, OE (online, all with Facility ONLINE): an arranged part is online
ONLINE_FACILITY = "ONLINE"
OFF_CAMPUS = {"OFFCSDSU": "Off campus"}
ARRANGED_FACILITY = {"ARRSDSU"}    # room arranged: follows the arranged rule
PLACEHOLDER_SEATS = {0, 999}
LOOK_AT_SEATS = 500
NOT_A_PERSON = {"STAFF", "TBA", "TBD"}

# the importer's Sections columns (its friendly headers), plus the optional class number
OUT_HEADER = ["Term", "Subject", "Course Number", "Course Title", "Units", "Section", "Days", "Start Time",
              "End Time", "Professor First Name", "Professor Last Name", "Building", "Room Number", "Seats",
              "Class Number"]

# ---------- thesis and individual study (skipped) ----------

THESIS_COMPONENTS = {"SUP", "NNT"}
_SKIP_TITLE = re.compile(r"""
      \bthes(is|es)?\b                                      # Thesis, Thesis or Proj Ext, Senior Thesis
    | \bdissert                                             # Doctoral Dissertation
    | \b(spec(ial)?|spcl|sp)\.?\s*stud(y|ies)?\b            # Special Study, Spec Studies
    | ^\s*(doctoral|doct?|independent|indep|ind|undergrad(uate)?|ugrd|graduate|grad)?\.?\s*research\s*$
    | \b(individual|indiv|independent|indep|ind|directed|dir)\.?\s*(study|studies|stdy|readings?|rdgs?)\b
    | \bcomp(rehensive|re|r)?\.?\s*exam                     # Comprehensive Exam (and Extension)
    | \binvestig\w*\.?\s*(and|&)\s*(report|rpt)\b           # Investigation and Report
""", re.I | re.X)
# kept on purpose even with no time; also overrules the "ends in 97, 98, 99" second opinion
_KEEP_TITLE = re.compile(r"""
      intern | practicum | prac\b | clinical | clin\b | field\s*(work|exp|study|placement) | fieldwork
    | student\s*teach | supervised\s*teach | sup\w*\s*teach | community\s*serv
    | senior\s*proj | (doctoral|dnp)\s*proj | \bper\s*st | perfrm | clerkship
""", re.I | re.X)


def is_thesis_like(component, title, catalog, timed):
    """True for a thesis / individual study section that students don't schedule (see 6c of the task)."""
    if component not in THESIS_COMPONENTS or timed:
        return False
    if _SKIP_TITLE.search(title):
        return True
    digits = re.match(r"\d+", catalog)
    return bool(digits and digits.group()[-2:] in ("97", "98", "99") and not _KEEP_TITLE.search(title))


# ---------- reading ----------

def text(value):
    """A cell as text: 3.0 -> '3', a time -> '18:00', None -> ''."""
    if value is None:
        return ""
    if isinstance(value, (datetime.datetime, datetime.time)):
        return f"{value.hour:02d}:{value.minute:02d}"
    if isinstance(value, float) and value == int(value):
        value = int(value)
    return str(value).strip()


def read_export(path):
    """(rows as dicts keyed by our names with '_row', the row count the title line promises or None)."""
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.worksheets[0]
    table = [[c for c in row] for row in ws.iter_rows(values_only=True)]
    wb.close()
    wanted = {v: k for k, v in SOURCE_COLUMNS.items()}
    header_at = next((i for i, row in enumerate(table[:20])
                      if SOURCE_COLUMNS[HEADER_MARK] in [text(c) for c in row]), None)
    if header_at is None:
        sys.exit(f"No header row with '{SOURCE_COLUMNS[HEADER_MARK]}' in the first 20 rows of {path}")
    header = [wanted.get(text(c)) for c in table[header_at]]
    missing = [v for k, v in SOURCE_COLUMNS.items() if k not in header]
    if missing:
        sys.exit(f"Missing column(s) in the export header: {', '.join(missing)}")
    promised = None
    for row in table[:header_at]:
        numbers = [text(c) for c in row if text(c).isdigit()]
        if numbers:
            promised = int(numbers[-1])
    rows = []
    for i, values in enumerate(table[header_at + 1:], start=header_at + 2):
        raw = {}
        for key, value in zip(header, values):
            if key:
                # padding inside a value matters only at the ends ("  16"); keep the raw text for times
                raw[key] = text(value)
        if not any(raw.values()):
            continue
        raw["_row"] = i
        rows.append(raw)
    return rows, promised


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------- small rules ----------

def term_name(code):
    """'2273' -> 'Spring 2027'. Raises ValueError for anything else."""
    m = re.fullmatch(r"2(\d\d)(\d)", code)
    if not m or m.group(2) not in SEASONS:
        raise ValueError(f"term '{code}' is not 2 + two-digit year + 3/5/7")
    return f"{SEASONS[m.group(2)]} {2000 + int(m.group(1))}"


def squish(value):
    return "".join(value.split()).upper()


def days_of(pattern):
    """'TR' -> 'TTh', 'MWF' -> 'MWF'. Raises ValueError on an unknown letter."""
    out = []
    for letter in pattern:
        if letter not in DAY_LETTERS:
            raise ValueError(f"meeting pattern '{pattern}' has the letter '{letter}'")
        out.append(DAY_LETTERS[letter])
    return "".join(out)


def clock(value):
    """'06:00 PM' -> '18:00', '9:30 AM' -> '09:30', '18:00' -> '18:00'. None if it isn't a time."""
    value = value.strip().upper()
    m = re.fullmatch(r"(\d{1,2}):(\d{2})(?::\d{2})?\s*([AP]M)?", value)
    if not m:
        return None
    h, mi, half = int(m.group(1)), int(m.group(2)), m.group(3)
    if half:
        if not 1 <= h <= 12:
            return None
        h = h % 12 + (12 if half == "PM" else 0)
    return f"{h:02d}:{mi:02d}" if h <= 23 and mi <= 59 else None


def title_case_caps(name):
    """'RICHARDSON' -> 'Richardson'; 'De La Pena' and 'McDonald' stay as they are."""
    return name.title() if name.isupper() else name


class Rooms:
    """Splits glued facility codes using the buildings already in rooms.csv."""

    ROOM = re.compile(r"\d+[A-Z]?")
    GLUED = re.compile(r"([A-Z]+)(\d+[A-Z]?)")

    def __init__(self, rooms_rows):
        self.pairs = {(r["building"], r["room_number"]) for r in rooms_rows}
        self.buildings = sorted({b for b, _ in self.pairs if b and b.isupper() and b != ONLINE_FACILITY},
                                key=len, reverse=True)

    def split(self, code):
        """'GMCS428' -> ('GMCS', '428', True); '39-110' -> ('39-110', '', False)."""
        code = squish(code)
        for b in self.buildings:                       # longest known code first
            rest = code[len(b):]
            if code.startswith(b) and rest and (self.ROOM.fullmatch(rest) or (b, rest) in self.pairs):
                return b, rest, True
        m = self.GLUED.fullmatch(code)
        if m:
            return m.group(1), m.group(2), True
        return code, "", False


# ---------- the conversion ----------

class Notes:
    """Counts and examples for the report."""

    def __init__(self):
        self.count = collections.Counter()
        self.examples = collections.defaultdict(list)

    def add(self, kind, example="", n=1):
        self.count[kind] += n
        if example and example not in self.examples[kind]:
            self.examples[kind].append(example)


def convert(path, cleaned_dir=CLEANED_DIR, majors_dir=MAJORS_DIR, ge_dir=GE_DIR):
    """-> (term name, output rows as lists, report text). Exits with a message on a problem it must not guess."""
    rows, promised = read_export(path)
    notes = Notes()
    rooms = Rooms(read_csv(os.path.join(cleaned_dir, "rooms.csv")))
    courses_now = {(squish(c["subject"]), c["catalog_num"].strip().upper()): c["title"]
                   for c in read_csv(os.path.join(cleaned_dir, "courses.csv"))}
    people_now = collections.defaultdict(list)
    for p in read_csv(os.path.join(cleaned_dir, "professors.csv")):
        if p["first_name"] and p["last_name"]:
            people_now[(p["last_name"].upper(), p["first_name"][0].upper())].append((p["first_name"], p["last_name"]))

    # ---- terms ----
    terms = sorted({r["term"] for r in rows if r["term"]})
    if len(terms) != 1:
        sys.exit(f"The export must have exactly one term, it has: {', '.join(terms) or 'none'}")
    try:
        term = term_name(terms[0])
    except ValueError as e:
        sys.exit(f"Unknown term: {e}")

    # ---- group by Class Nbr ----
    groups = collections.OrderedDict()
    for r in rows:
        groups.setdefault(r["class_nbr"], []).append(r)
    campus_sections = collections.Counter(g[0]["campus"] for g in groups.values())
    campus_rows = collections.Counter(r["campus"] for r in rows)

    kept, skipped = [], collections.Counter()
    skipped_rows = collections.Counter()
    for nbr, group in groups.items():
        first = group[0]
        if first["campus"] not in KEEP_CAMPUS:
            skipped[f"campus {first['campus'] or '(blank)'}"] += 1
            skipped_rows[f"campus {first['campus'] or '(blank)'}"] += len(group)
            continue
        if first["status"] not in KEEP_STATUS:
            skipped[f"class status {first['status'] or '(blank)'}"] += 1
            skipped_rows[f"class status {first['status'] or '(blank)'}"] += len(group)
            continue
        kept.append((nbr, group))

    sections = []
    for nbr, group in kept:
        s = build_section(nbr, group, term, rooms, people_now, notes)
        sections.append(s)

    # ---- thesis and individual study ----
    thesis_skipped, no_time_kept = [], []
    out = []
    for s in sections:
        if is_thesis_like(s["component"], s["title_export"], s["catalog"], s["timed"]):
            thesis_skipped.append(s)
        else:
            out.append(s)
            if not s["timed"]:
                no_time_kept.append(s)
    for s in thesis_skipped:
        skipped_rows["thesis or individual study"] += s["rows"]
    skipped["thesis or individual study"] = len(thesis_skipped)

    # ---- duplicate keys: the importer can't keep two Class Nbrs with one section number apart ----
    by_key = collections.defaultdict(list)
    for s in out:
        by_key[(s["subject"], s["catalog"], s["section"])].append(s)
    duplicates = []
    for key, items in by_key.items():
        if len(items) > 1:
            items.sort(key=lambda s: int(s["class_nbr"]))
            for extra in items[1:]:
                duplicates.append((extra, items[0]))
    drop = {id(extra) for extra, _ in duplicates}
    for extra, _ in duplicates:
        skipped_rows["same subject, number and section as a lower Class Nbr"] += extra["rows"]
    skipped["same subject, number and section as a lower Class Nbr"] = len(duplicates)
    out = [s for s in out if id(s) not in drop]

    # ---- titles ----
    export_titles = collections.defaultdict(set)
    for s in out:
        export_titles[(s["subject"], s["catalog"])].add(s["title_export"])
    title_counts = collections.Counter()
    for s in out:
        ckey = (s["subject"], s["catalog"])
        if len(export_titles[ckey]) > 1:
            s["title"] = s["title_export"]
            title_counts["several titles, each section keeps its own"] += 1
            notes.add("course with several titles in the export (each section keeps its own)",
                      f"{s['subject']} {s['catalog']}")
        elif ckey in courses_now:
            s["title"] = courses_now[ckey]
            title_counts["current EzClass title kept"] += 1
            if courses_now[ckey] != s["title_export"]:
                notes.add("current title kept instead of the export's short one",
                          f"{s['subject']} {s['catalog']}: '{s['title_export']}' -> '{courses_now[ckey]}'")
        else:
            s["title"] = s["title_export"]
            title_counts["new course, export title"] += 1

    out.sort(key=sort_key)
    table = [[term, s["subject"], s["catalog"], s["title"], s["units"], s["section"],
              *s["schedule"], s["first"], s["last"], s["building"], s["room"], s["seats"], s["class_nbr"]]
             for s in out]

    context = dict(path=path, rows=rows, promised=promised, groups=groups, campus_sections=campus_sections,
                   campus_rows=campus_rows, skipped=skipped, skipped_rows=skipped_rows, sections=sections, out=out,
                   thesis_skipped=thesis_skipped, no_time_kept=no_time_kept, duplicates=duplicates,
                   title_counts=title_counts, courses_now=courses_now, rooms=rooms, notes=notes, term=term,
                   majors_dir=majors_dir, ge_dir=ge_dir)
    return term, table, report_text(context)


def sort_key(s):
    m = re.match(r"(\d*)(.*)", s["catalog"])
    return (s["subject"], int(m.group(1) or 0), m.group(2), s["section"], int(s["class_nbr"]))


def same_for_section(group, field, nbr, notes):
    """A section-level value; if the rows disagree the first is used and it's reported."""
    values = [r[field] for r in group]
    if len(set(values)) > 1:
        notes.add(f"rows of one Class Nbr disagree on {SOURCE_COLUMNS[field]} (first used)",
                  f"class {nbr}: {', '.join(sorted(set(values)))}")
    return values[0]


def build_section(nbr, group, term, rooms, people_now, notes):
    """One Class Nbr's rows -> one section dict (with its schedule columns ready to write)."""
    get = lambda field: same_for_section(group, field, nbr, notes)   # noqa: E731
    subject, catalog = squish(get("subject")), get("catalog").strip().upper()
    code = f"{subject} {catalog}"
    section = get("section").strip()
    mode = get("mode").strip().upper()
    label = f"{code} sec {section} (class {nbr})"
    if not nbr.isdigit():
        sys.exit(f"Class Nbr '{nbr}' is not a number (row {group[0]['_row']})")
    if " " in get("subject").strip():
        notes.add("subject spaces removed", f"'{get('subject').strip()}' -> {subject}")
    if get("catalog") != catalog:
        notes.add("course number padding or case cleaned", f"'{get('catalog')}' -> {catalog}")

    # ---- units ----
    units = get("units")
    if re.fullmatch(r"\d+\.0+", units):
        units = units.split(".")[0]
    if not re.fullmatch(r"\d+(\.\d+)?", units):
        notes.add("units not a number (the importer will skip the row)", f"{label}: '{units}'")
    elif not units.isdigit():
        notes.add("half units (kept as they are)", f"{label}: {units}")
    elif int(units) == 0:
        notes.add("0 units", label)
    elif int(units) > 6:
        notes.add("over 6 units", f"{label}: {units}")

    # ---- seats ----
    seats = get("capacity")
    if re.fullmatch(r"\d+\.0+", seats):
        seats = seats.split(".")[0]
    if seats.isdigit():
        n = int(seats)
        if n in PLACEHOLDER_SEATS:
            notes.add(f"seats {n} (placeholder, left blank)", label)
            seats = ""
        else:
            if n >= LOOK_AT_SEATS:
                notes.add(f"seats {LOOK_AT_SEATS} or more (kept, please glance)", f"{label}: {n}")
            if n == 99:
                notes.add("seats 99 (kept, could be a placeholder)", label)
    elif seats:
        notes.add("seats not a number (left blank)", f"{label}: '{seats}'")
        seats = ""

    # ---- meetings ----
    distinct = []
    for r in group:
        m = (r["pattern"].strip().upper(), r["start"].strip(), r["end"].strip(), squish(r["facility"]))
        if m not in distinct:
            distinct.append(m)
    timed, online, dropped = [], [], []
    for pattern, start, end, facility in distinct:
        has_time = bool(start or end)
        if pattern in NO_DAY_PATTERNS:
            if has_time:
                notes.add(f"time with pattern {pattern or '(blank)'} dropped", f"{label}: {start}-{end}")
            if pattern == "ASYN" or facility == ONLINE_FACILITY:
                online.append(True)
                if pattern == "ASYN":
                    notes.add("ASYN -> online part", label)
                else:
                    notes.add("Facility ONLINE, no time -> online part", label)
            elif pattern == "ARR" or facility in ARRANGED_FACILITY:
                if mode in ONLINE_MODES:
                    online.append(True)
                    notes.add(f"arranged in an {mode} section -> online part", label)
                else:
                    dropped.append("arranged")
                    notes.add("arranged in an in-person section (no schedule part)", label)
            elif facility:
                dropped.append("room, no day or time")
                notes.add("room but no day or time (part dropped)", f"{label}: {facility}")
            else:
                dropped.append("empty")
            continue
        try:
            days = days_of(pattern)
        except ValueError as e:
            sys.exit(f"Stopped: {e} (row {group[0]['_row']}, {label}). Add it to DAY_LETTERS if it is a real day.")
        t0, t1 = clock(start), clock(end)
        if not (t0 and t1):
            dropped.append("pattern but no time")
            notes.add("pattern but no times (part dropped, not guessed)", f"{label}: {pattern} '{start}'-'{end}'")
            continue
        if facility == ONLINE_FACILITY:
            building, room = ONLINE_FACILITY, ""
            notes.add("live online: day and time, Facility ONLINE", f"{label}: {days} {t0}-{t1}")
        elif facility in OFF_CAMPUS:
            building, room = OFF_CAMPUS[facility], ""
            notes.add(f"{facility} -> '{OFF_CAMPUS[facility]}'", label)
        elif facility in ARRANGED_FACILITY or not facility:
            building, room = "", ""
            notes.add("timed meeting with no room", f"{label}: {days} {t0}-{t1} '{facility}'")
        else:
            building, room, clean = rooms.split(facility)
            if not clean:
                notes.add("facility code that doesn't split (kept whole as the building)", facility)
            elif (building, room) not in rooms.pairs:
                notes.add("room not in rooms.csv yet", f"{building} {room}")
            if building not in {b for b, _ in rooms.pairs}:
                notes.add("building not in rooms.csv yet", building)
        timed.append((days, t0, t1, building, room))
    if timed and dropped:
        for why in dropped:
            notes.add(f"part dropped next to a timed meeting ({why})", label)
    if not timed and not online:
        if "arranged" in dropped:
            notes.add("in-person arranged section -> no schedule (Time not listed yet)", label)
        elif dropped:
            notes.add("no usable meeting -> no schedule", f"{label}: {', '.join(sorted(set(dropped)))}")
    if mode == "HY":
        notes.add("hybrid sections" + (" with a timed and an online part" if timed and online
                                       else " (no online part listed)" if timed else " (online parts only)"), label)
    if len(timed) + (1 if online else 0) > 1:
        notes.add("sections with two or more meetings", label)

    day_order = {d: i for i, d in enumerate(["M", "T", "W", "Th", "F", "Sa", "Su"])}
    first_day = lambda d: day_order[re.match(r"Th|Sa|Su|M|T|W|F", d).group()]   # noqa: E731
    timed.sort(key=lambda m: (first_day(m[0]), m[1], m[2], m[3], m[4]))
    meetings = timed + ([("ONLINE", "", "", "", "")] if online else [])
    if meetings:
        cols = list(zip(*meetings))
        schedule = [" / ".join(c) for c in cols[:3]]
        building, room = " / ".join(cols[3]), " / ".join(cols[4])
    else:
        schedule, building, room = ["", "", ""], "", ""

    # ---- people ----
    people, seen = [], set()
    for r in group:
        last, initials = r["last"].strip(), r["initials"].strip().rstrip(".")
        if not last and not initials:
            continue
        if last.upper() in NOT_A_PERSON:
            notes.add("placeholder instructor (left out)", f"{label}: {last}")
            continue
        key = (last.upper(), initials[:1].upper())
        if key in seen:
            continue
        seen.add(key)
        matches = people_now.get(key, []) if initials else []
        if len(set(matches)) == 1:
            people.append(matches[0])
            notes.add("instructor matched to a current full name", f"{initials} {last} -> {matches[0][0]} {matches[0][1]}")
        else:
            if len(set(matches)) > 1:
                notes.add("instructor initial matches more than one current person (initial used)",
                          f"{initials} {last}: {', '.join(sorted(f'{a} {b}' for a, b in set(matches)))}")
            elif last.isupper():
                notes.add("all-caps last name title-cased", f"{last} -> {title_case_caps(last)}")
            if not initials:
                notes.add("instructor with no initial (left out, the importer needs a first name)", f"{label}: {last}")
                continue
            people.append((f"{initials[0].upper()}.", title_case_caps(last)))
            notes.add("new instructor, initial used as the first name", f"{initials[0].upper()}. {title_case_caps(last)}")
    people.sort(key=lambda p: (p[1].casefold(), p[0].casefold()))
    if not people:
        notes.add("no instructor listed", label)
    by_meeting = collections.defaultdict(set)
    for r in group:
        by_meeting[(r["pattern"], r["start"], r["end"], r["facility"])].add((r["last"].upper(), r["initials"][:1].upper()))
    if len(by_meeting) > 1 and len({frozenset(v) for v in by_meeting.values()}) > 1:
        notes.add("instructor listed on only some meetings (the importer lists each person once per section)", label)
    if len(people) > 1:
        notes.add("two or more instructors", label)

    return {
        "class_nbr": nbr, "subject": subject, "catalog": catalog, "section": section, "units": units,
        "title_export": get("title").strip(), "component": get("component").strip().upper(),
        "career": get("career").strip().upper(), "mode": mode, "session": get("session").strip(),
        "schedule": schedule, "building": building, "room": room, "seats": seats,
        "first": " / ".join(p[0] for p in people), "last": " / ".join(p[1] for p in people),
        "timed": bool(timed), "timed_count": len(timed), "online": bool(online), "rows": len(group),
    }


# ---------- the report ----------

def examples(items, n=5):
    items = list(items)
    shown = "; ".join(items[:n])
    return shown + (f"; ... ({len(items) - n} more)" if len(items) > n else "")


def wrap(words, per_line=10, indent="    "):
    words = sorted(words)
    return [indent + ", ".join(words[i:i + per_line]) for i in range(0, len(words), per_line)]


def needed_courses(majors_dir, ge_dir):
    """(subject, number) -> where it's needed ('major M-E', 'GE 3A')."""
    need = collections.defaultdict(set)
    for r in read_csv(os.path.join(majors_dir, "major_requirements.csv")):
        if (r.get("catalog_num") or "").strip():
            for subj in (r.get("subject") or "").split("|"):
                need[(squish(subj), r["catalog_num"].strip().upper())].add(f"major {r['major_id']}")
    for r in read_csv(os.path.join(ge_dir, "ge_courses.csv")):
        need[(squish(r["subject"]), r["catalog_num"].strip().upper())].add(f"GE {r['area_code']}")
    return need


def report_text(c):
    notes, out = c["notes"], c["out"]
    rows_used = sum(s["rows"] for s in out)
    rows_skipped = sum(c["skipped_rows"].values())
    lines = [f"EzClass schedule conversion of {os.path.basename(c['path'])}", f"Term: {c['term']}", ""]
    w = lines.append
    w("== The numbers")
    w(f"Rows read:            {len(c['rows'])}" + (
        f"  (the title line says {c['promised']}: {'matches' if c['promised'] == len(c['rows']) else 'DOES NOT MATCH'})"
        if c["promised"] is not None else "  (no row count on the title line)"))
    w(f"  rows used:          {rows_used}")
    w(f"  rows skipped:       {rows_skipped}")
    for why, n in sorted(c["skipped_rows"].items()):
        w(f"    {why}: {n} rows")
    w(f"  check: {rows_used} + {rows_skipped} = {rows_used + rows_skipped}"
      f" {'(adds up)' if rows_used + rows_skipped == len(c['rows']) else '(DOES NOT ADD UP)'}")
    w(f"Sections in the file: {len(c['groups'])}  ("
      + ", ".join(f"{k or '(blank)'} {v}" for k, v in sorted(c["campus_sections"].items())) + ")")
    w(f"Sections skipped:     {sum(c['skipped'].values())}")
    for why, n in sorted(c["skipped"].items()):
        w(f"    {why}: {n}")
    courses = {(s["subject"], s["catalog"]) for s in out}
    w(f"Sections written:     {len(out)}  (courses {len(courses)}, subjects {len({s['subject'] for s in out})})")
    careers = collections.Counter(s["career"] for s in out)
    w("  by career:          " + ", ".join(f"{k or '(blank)'} {v}" for k, v in sorted(careers.items())))
    w(f"  new courses:        {len(courses - set(c['courses_now']))}  (already in EzClass: {len(courses & set(c['courses_now']))})")
    old_courses = set(c["courses_now"])
    w(f"  EzClass courses with no section in this file: {len(old_courses - courses)}")
    timed_count = sum(s["timed_count"] for s in out)
    online_count = sum(1 for s in out if s["online"])
    w(f"Meetings written:     {timed_count + online_count}  (timed {timed_count}, online parts {online_count})")
    w(f"  no schedule:        {sum(1 for s in out if not s['schedule'][0])}  (shown as 'Time not listed yet')")
    people = {(f, l) for s in out for f, l in zip(s["first"].split(" / "), s["last"].split(" / ")) if l}
    w(f"People written:       {len(people)}  (sections with no instructor: {sum(1 for s in out if not s['last'])})")
    numbers = [s["class_nbr"] for s in out]
    w(f"Class numbers:        {len(numbers)} ({len(set(numbers))} unique; "
      f"{sum(1 for n in numbers if len(n) == 4)} with 4 digits, {sum(1 for n in numbers if len(n) == 5)} with 5)")
    modes = collections.Counter(s["mode"] for s in out)
    w("Instruction modes:    " + ", ".join(f"{k or '(blank)'} {v}" for k, v in sorted(modes.items())))
    sessions = collections.Counter(s["session"] for s in out)
    w("Sessions:             " + ", ".join(f"{k or '(blank)'} {v}" for k, v in sorted(sessions.items())))
    comps = collections.Counter(s["component"] for s in out)
    w("Components:           " + ", ".join(f"{k or '(blank)'} {v}" for k, v in sorted(comps.items())))
    multi = collections.defaultdict(set)
    for s in out:
        multi[(s["subject"], s["catalog"])].add(s["component"])
    w(f"Courses with two or more components (e.g. lecture + lab as separate sections): "
      f"{sum(1 for v in multi.values() if len(v) > 1)}")
    w("")

    w("== Every rule applied (count, up to 5 examples)")
    for kind in sorted(notes.count):
        w(f"  {kind}: {notes.count[kind]}")
        if notes.examples[kind] and kind not in LONG_LISTS:
            w(f"      {examples(notes.examples[kind])}")
    w("")
    w("Titles:")
    for kind, n in sorted(c["title_counts"].items()):
        w(f"  {kind}: {n} sections")
    w("")

    w("== Needs a look")
    w("")
    w("Thesis and individual study, skipped (by title):")
    by_title = collections.Counter(s["title_export"] for s in c["thesis_skipped"])
    for title, n in by_title.most_common(25):
        w(f"  {n:4}  {title}")
    if len(by_title) > 25:
        w(f"  and one section each (or two): ")
        lines.extend(wrap([f"{t} ({n})" for t, n in by_title.most_common()[25:]], per_line=5))
    w("")
    arranged = [s for s in c["no_time_kept"] if not s["online"]]
    online_only = [s for s in c["no_time_kept"] if s["online"]]
    w(f"Kept on purpose with no day or time: {len(c['no_time_kept'])} sections")
    w(f"  {len(online_only)} are online with no set time (normal online classes).")
    w(f"  {len(arranged)} are arranged or not listed (shown as 'Time not listed yet'). Top 40 titles, say yes or no per group:")
    for title, n in collections.Counter(s["title_export"] for s in arranged).most_common(40):
        w(f"  {n:4}  {title}")
    w("")
    gone_courses = {(s["subject"], s["catalog"]) for s in c["thesis_skipped"]} - courses
    need = needed_courses(c["majors_dir"], c["ge_dir"])
    w(f"Courses that disappear completely because of the thesis filter: {len(gone_courses)}")
    needed = sorted((k, sorted(need[k])) for k in gone_courses if k in need)
    w(f"  of those, needed by a major or a GE list (they will show as 'not offered'): {len(needed)}")
    for (subj, num), where in needed[:30]:
        w(f"    {subj} {num}: {', '.join(where)}")
    if len(needed) > 30:
        w(f"    ... and {len(needed) - 30} more")
    w("")
    if c["duplicates"]:
        w("Same subject, number and section with two Class Nbrs (the lowest is kept, the others skipped):")
        for extra, keep in c["duplicates"][:30]:
            w(f"  {extra['subject']} {extra['catalog']} sec {extra['section']}: class {extra['class_nbr']} skipped, "
              f"{keep['class_nbr']} kept")
        w("")
    for kind in LONG_LISTS:
        if notes.examples.get(kind):
            w(f"{kind} ({len(notes.examples[kind])} different, {notes.count[kind]} meetings or sections):")
            lines.extend(wrap(notes.examples[kind]))
            w("")
    return "\n".join(lines).rstrip() + "\n"


LONG_LISTS = ("building not in rooms.csv yet", "room not in rooms.csv yet",
              "facility code that doesn't split (kept whole as the building)",
              "instructor initial matches more than one current person (initial used)",
              "seats 500 or more (kept, please glance)")


def csv_text(table):
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(OUT_HEADER)
    writer.writerows(table)
    return buf.getvalue()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    term, table, report = convert(args[0])
    os.makedirs(OUT_DIR, exist_ok=True)
    season, year = term.split()
    out_path = os.path.join(OUT_DIR, f"{season.lower()}{year}_sections.csv")
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(csv_text(table))
    with open(REPORT_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(report)
    print(report)
    print(f"Wrote {os.path.relpath(out_path, BASE)} ({len(table)} sections) and {os.path.relpath(REPORT_PATH, BASE)}")
    print(f"Next: python3 data/import_real_data.py {os.path.relpath(out_path, BASE).replace(os.sep, '/')}")


if __name__ == "__main__":
    main()

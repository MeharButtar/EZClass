"""
Conflict-detection logic: given two sections, do they overlap in a way
that means a student can't take both?

A section can meet more than once (lecture + lab, or a timed part and an
online part). Two sections conflict if some timed meeting of one and some
timed meeting of the other:
  1. share at least one day, AND
  2. have time ranges that overlap (back to back is fine).
Online meetings have no time, so they never conflict, and meetings of the
same section never conflict with each other.

Day patterns in the data look like 'MW', 'TTh', 'MWF', 'TR'. We break
each pattern into individual day letters/tokens so 'TTh' and 'TR' (both
meaning Tuesday/Thursday depending on how someone typed it) are handled
consistently, and so 'MW' vs 'MWF' correctly shares Monday and Wednesday.
"""

# Map every way a day might show up in raw data to one canonical token.
DAY_TOKENS = {
    "M": "Mon", "Mon": "Mon",
    "T": "Tue", "Tu": "Tue", "Tue": "Tue",
    "W": "Wed", "Wed": "Wed",
    "Th": "Thu", "R": "Thu", "Thu": "Thu",
    "F": "Fri", "Fri": "Fri",
    "Sa": "Sat", "Sat": "Sat",
    "Su": "Sun", "Sun": "Sun",
}


def parse_days(day_string):
    """
    Turns a day-pattern string like 'MWF' or 'TTh' or 'TR' into a set of
    canonical day tokens, e.g. {'Mon', 'Wed', 'Fri'}.

    This is intentionally a small hand-rolled parser rather than a
    single-character split, because 'Th' is two characters representing
    one day, and naive splitting would misread 'TTh' as T, T, h.
    """
    days = set()
    i = 0
    s = (day_string or "").strip()
    while i < len(s):
        # try two-character tokens first (Th, Tu, Sa, Su) before
        # falling back to a single character
        two = s[i:i + 2]
        if two in DAY_TOKENS:
            days.add(DAY_TOKENS[two])
            i += 2
            continue
        one = s[i]
        if one in DAY_TOKENS:
            days.add(DAY_TOKENS[one])
            i += 1
            continue
        # unrecognized character, skip it rather than crash on bad data
        i += 1
    return days


def time_to_minutes(t):
    """'14:30' -> 870"""
    h, m = map(int, t.split(":"))
    return h * 60 + m


def timed_meetings(section):
    """
    The meetings with a day and a time, as (days set, start_min, end_min).
    Uses section["meetings"] (dicts with day_code, start_min, end_min,
    is_online) when present, otherwise the older one-meeting columns
    days / start_time / end_time.
    """
    meetings = section.get("meetings") if hasattr(section, "get") else None
    if meetings is None:
        if not (section["days"] and section["start_time"] and section["end_time"]):
            return []
        return [(parse_days(section["days"]), time_to_minutes(section["start_time"]),
                 time_to_minutes(section["end_time"]))]
    return [(parse_days(m["day_code"]), m["start_min"], m["end_min"]) for m in meetings
            if not m["is_online"] and m["day_code"] and m["start_min"] is not None and m["end_min"] is not None]


def sections_conflict(section_a, section_b):
    """
    section_a, section_b: dicts with 'section_id' and either 'meetings' or
    the older 'days', 'start_time', 'end_time' keys (a sqlite3.Row works for
    the older shape). Returns True if the two sections cannot both be taken.
    """
    if section_a["section_id"] == section_b["section_id"]:
        return False
    for days_a, start_a, end_a in timed_meetings(section_a):
        for days_b, start_b, end_b in timed_meetings(section_b):
            if days_a & days_b and start_a < end_b and start_b < end_a:
                return True
    return False


def find_conflicts(sections):
    """
    Given a list of sections (e.g. everything a student has selected so
    far), returns a list of (section_a, section_b) pairs that conflict.
    """
    conflicts = []
    for i in range(len(sections)):
        for j in range(i + 1, len(sections)):
            if sections_conflict(sections[i], sections[j]):
                conflicts.append((sections[i], sections[j]))
    return conflicts

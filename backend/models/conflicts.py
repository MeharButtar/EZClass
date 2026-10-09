"""
Conflict-detection logic: given two sections, do they overlap in a way
that means a student can't take both?

Two sections conflict if:
  1. They share at least one day in common, AND
  2. Their time ranges overlap.

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
    s = day_string.strip()
    while i < len(s):
        # try two-character tokens first (Th, Tu, Mo, We, Fr) before
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


def times_overlap(start1, end1, start2, end2):
    s1, e1 = time_to_minutes(start1), time_to_minutes(end1)
    s2, e2 = time_to_minutes(start2), time_to_minutes(end2)
    # standard interval overlap check: NOT (one ends before the other starts)
    return s1 < e2 and s2 < e1


def sections_conflict(section_a, section_b):
    """
    section_a, section_b: dict-like with 'days', 'start_time', 'end_time'
    keys (works directly with sqlite3.Row or a plain dict).
    Returns True if the two sections cannot both be taken.
    """
    if section_a["section_id"] == section_b["section_id"]:
        return False

    days_a = parse_days(section_a["days"])
    days_b = parse_days(section_b["days"])
    shared_days = days_a & days_b
    if not shared_days:
        return False

    return times_overlap(
        section_a["start_time"], section_a["end_time"],
        section_b["start_time"], section_b["end_time"],
    )


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

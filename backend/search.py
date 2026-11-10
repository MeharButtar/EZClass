"""
The keyword and professor matching behind /api/sections?q= and &professor=.

Plain Python on purpose: the typed text is never put into SQL (not even as a
LIKE pattern, so % and _ are just characters), and the rules are easy to
test. The routes turn the matches into a list of ids and filter with
parameterized "IN (?, ?, ...)".

Keyword rules (see tests/test_search.py):
  - spaces, dashes, dots, slashes, case and accents never matter: "CS 480",
    "cs480", "CS-480" are the same, and "GEN S 147" finds GENS 147 (squished)
  - a code or the start of one: "CS 4" -> CS 4xx, "150" -> every 150..., "CS 150"
    -> CS 150 then CS 150L
  - a subject alone is that subject only ("CS" never matches "physiCS" or CSP)
  - otherwise every typed word must start the subject, the number or a word
    of the title (special-topics section titles included); & means "and"
  - typing a number makes it a code search: word matches are dropped when a
    code matches
  - one character, or only punctuation, is no keyword at all
  - 4 or 5 digits alone ("5834", "#12095", " 5834 ") is a class number, the
    number students register with: that section's course comes back, the
    section first. Course numbers have at most 3 digits, so "150" is still a
    course search. An unknown class number falls back to the rules above.
"""

import os
import re
import threading
import unicodedata

MAX_Q = 100

_cache = {"key": None, "courses": None, "numbers": None}
CLASS_NUMBER = re.compile(r"\d{4,5}")
_cache_lock = threading.Lock()


def norm(text):
    """lowercase, accents dropped, & -> and, every run of non-letters/digits -> one space."""
    t = unicodedata.normalize("NFKD", str(text or "")).encode("ascii", "ignore").decode()
    t = t.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def tokens(q):
    """'cs480' -> ['cs', '480'], 'biol211l' -> ['biol', '211l'], 'intro to' -> ['intro', 'to']"""
    t = re.sub(r"([a-z])(?=\d)", r"\1 ", norm(str(q or "")[:MAX_Q]))
    return t.split()


def load_courses(conn):
    """course_id -> what the matcher needs (subject, number, code, title words)."""
    courses = {}
    for r in conn.execute("""SELECT c.course_id, c.subject, c.catalog_num, c.title,
                                    (SELECT GROUP_CONCAT(DISTINCT s.section_title) FROM sections s
                                      WHERE s.course_id = c.course_id AND s.active = 1) AS section_titles
                             FROM courses c"""):
        subj, num = r["subject"].lower(), r["catalog_num"].lower()
        courses[r["course_id"]] = dict(subject=subj, num=num, key=subj + num,
                                       words=norm(f"{r['title']} {r['section_titles'] or ''}").split())
    return courses


def load_class_numbers(conn):
    """class number ('5834') -> (course_id, section_id), active sections only."""
    return {r["class_number"]: (r["course_id"], r["section_id"]) for r in conn.execute(
        "SELECT class_number, course_id, section_id FROM sections WHERE active = 1 AND class_number IS NOT NULL")}


def _index(conn, db_path):
    """Both lookups, cached until the database file changes (a re-import rewrites it)."""
    try:
        stamp = os.stat(db_path).st_mtime_ns
    except OSError:
        stamp = None
    key = (db_path, stamp)
    with _cache_lock:
        if _cache["key"] != key or stamp is None:
            _cache["courses"] = load_courses(conn)
            _cache["numbers"] = load_class_numbers(conn)
            _cache["key"] = key
        return _cache


def get_course_index(conn, db_path):
    """load_courses, cached."""
    return _index(conn, db_path)["courses"]


def class_number_query(q):
    """'5834', '#5834', ' # 12095 ' -> the digits; anything else -> None."""
    text = str(q or "")[:MAX_Q].strip()
    text = text[1:].strip() if text.startswith("#") else text
    return text if CLASS_NUMBER.fullmatch(text) else None


def match_class_number(conn, db_path, q):
    """(course_id, section_id) of the active section with that class number, or None."""
    number = class_number_query(q)
    return _index(conn, db_path)["numbers"].get(number) if number else None


def match_courses(courses, q):
    """
    -> {course_id: rank}, or None when there is no keyword to apply.
    rank 0 = exact code ("CS 480"), 1 = subject or code/number prefix
    ("CS", "CS 4", "150", CS 150L for "CS 150"), 2 = title words.
    """
    toks = tokens(q)
    if not toks or len("".join(toks)) < 2:
        return None                                  # empty, only punctuation, or one character
    squished = "".join(toks)
    has_digit = any(ch.isdigit() for ch in squished)
    subjects = {c["subject"] for c in courses.values()}
    out = {}
    for cid, c in courses.items():
        subj, num = c["subject"], c["num"]

        def code_tok(t):
            return t == subj or (t[0].isdigit() and num.startswith(t))

        rank = None
        if squished == c["key"]:
            rank = 0                                  # cs480, cs 480, CS-480, gen s 147 -> gens147
        elif squished.isalpha() and squished in subjects:
            rank = 1 if subj == squished else None    # "cs" -> subject CS only
        elif has_digit and c["key"].startswith(squished):
            rank = 1                                  # cs48, cs4 -> CS 48x, CS 4xx
        elif all(code_tok(t) for t in toks):
            rank = 1                                  # "cs 4", "150"
        elif all(code_tok(t) or any(w.startswith(t) for w in c["words"]) for t in toks):
            rank = 2                                  # every word starts the subject, number or a title word
        if rank is not None:
            out[cid] = rank
    if has_digit and any(r <= 1 for r in out.values()):
        return {k: r for k, r in out.items() if r <= 1}   # a number makes it a code search
    return out


def person_match(first, last, q):
    """Every typed word must start the first or the last name: 'Rapp, Michael', 'M Rapp', 'rapp'."""
    toks = norm(str(q or "")[:MAX_Q]).split()
    names = norm(f"{first} {last}").split()
    return bool(toks) and all(any(n.startswith(t) for n in names) for t in toks)

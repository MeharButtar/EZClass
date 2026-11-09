"""
Routes for searching/filtering course sections.

A section can meet more than once (lecture + lab, or a timed part and an
online part) and can have more than one instructor. Every section comes
back with:
  meetings     -> [{day, start, end, building, room, online}] in the sheet's order
  instructors  -> [{name, first, last}], each person once
  online_only  -> true when it has meetings and none has a set day and time
  no_schedule  -> true when no meetings are entered yet ("Time not listed yet")
  section_title -> the section's own title (special topics), else null
The older flat fields (days, start_time, end_time, building, room_number,
professor_name, capacity) are still there, filled from the first timed
meeting and the first instructor (all null for a section with no schedule).
Sections no longer in the sheet (active = 0) never come back.
"""

import re

from flask import Blueprint, jsonify, request

from backend.models.conflicts import DAY_TOKENS, parse_days
from backend.models.db import DB_PATH, get_connection
from backend.search import get_course_index, match_courses, person_match

sections_bp = Blueprint("sections", __name__)

MAX_ID_LIST = 200


def id_list(value):
    """'1,2,3' -> [1, 2, 3]. None if anything isn't a plain number or the list is too long."""
    parts = [p.strip() for p in value.split(",") if p.strip()]
    if not parts or len(parts) > MAX_ID_LIST or not all(p.isdigit() and len(p) <= 9 for p in parts):
        return None
    return [int(p) for p in parts]


def hhmm(minutes):
    return None if minutes is None else f"{minutes // 60:02d}:{minutes % 60:02d}"


def _in_chunks(conn, sql, ids):
    """Runs sql (with one {marks} slot) for the ids, a few hundred at a time (SQLite caps parameters)."""
    rows = []
    for i in range(0, len(ids), 500):
        part = ids[i:i + 500]
        rows += conn.execute(sql.format(marks=",".join("?" * len(part))), part).fetchall()
    return rows


def meetings_by_section(conn, section_ids):
    """section_id -> its meetings (dicts with day_code, start_min, end_min, building, room, is_online)."""
    out = {}
    for r in _in_chunks(conn, """
            SELECT section_id, idx, day_code, start_min, end_min, building, room, is_online
            FROM section_meetings WHERE section_id IN ({marks}) ORDER BY section_id, idx""", list(section_ids)):
        out.setdefault(r["section_id"], []).append(dict(r))
    return out


def instructors_by_section(conn, section_ids):
    """section_id -> [{name, first, last}] in the sheet's order."""
    out = {}
    for r in _in_chunks(conn, """
            SELECT i.section_id, p.first_name, p.last_name
            FROM section_instructors i JOIN professors p ON p.professor_id = i.professor_id
            WHERE i.section_id IN ({marks}) ORDER BY i.section_id, i.idx""", list(section_ids)):
        out.setdefault(r["section_id"], []).append(
            {"name": f"{r['first_name']} {r['last_name']}", "first": r["first_name"], "last": r["last_name"]})
    return out


def meeting_to_dict(m):
    online = bool(m["is_online"])
    return {
        "day": "" if online else (m["day_code"] or ""),
        "start": None if online else hhmm(m["start_min"]),
        "end": None if online else hhmm(m["end_min"]),
        "building": m["building"] or "",
        "room": m["room"] or "",
        "online": online,
    }


def is_timed(m):
    return not m["online"] and bool(m["day"]) and m["start"] is not None and m["end"] is not None


def section_to_dict(row, meetings, instructors):
    meetings = [meeting_to_dict(m) for m in meetings]
    first_timed = next((m for m in meetings if is_timed(m)), None)
    first = instructors[0] if instructors else None
    no_schedule = not meetings
    return {
        "section_id": row["section_id"],
        "course_id": row["course_id"],
        "subject": row["subject"],
        "catalog_num": row["catalog_num"],
        "course_title": row["title"],
        "units": row["units"],
        "section_number": row["section_number"],
        "section_title": row["section_title"] or None,
        "term": row["term"],
        "meetings": meetings,
        "instructors": instructors,
        "online_only": not no_schedule and first_timed is None,
        "no_schedule": no_schedule,
        "seats_text": row["seats_text"] or "",
        "seats_total": row["seats_total"],
        # the older one-meeting fields, from the first timed meeting and the first instructor
        "professor_name": first["name"] if first else None,
        "professor_last": first["last"] if first else None,   # for the RateMyProfessors link
        "days": first_timed["day"] if first_timed else (None if no_schedule else ""),
        "start_time": first_timed["start"] if first_timed else None,
        "end_time": first_timed["end"] if first_timed else None,
        "building": first_timed["building"] if first_timed else (meetings[0]["building"] if meetings else None),
        "room_number": first_timed["room"] if first_timed else (None if no_schedule else ""),
        "capacity": row["seats_total"],
        # GE info: list of area codes like ["3A"], plus the three tags
        "ge_areas": row["ge_areas"].split(",") if row["ge_areas"] else [],
        "cultural_diversity": bool(row["cultural_diversity"]),
        "ethnic_studies_grad": bool(row["ethnic_studies_grad"]),
        "american_inst": bool(row["american_inst"]),
    }


def sections_to_dicts(conn, rows):
    ids = [r["section_id"] for r in rows]
    meetings = meetings_by_section(conn, ids)
    people = instructors_by_section(conn, ids)
    return [section_to_dict(r, meetings.get(r["section_id"], []), people.get(r["section_id"], [])) for r in rows]


BASE_QUERY = """
    SELECT
        s.section_id, s.course_id, s.section_number, s.term, s.seats_text, s.seats_total, s.section_title,
        c.subject, c.catalog_num, c.title, c.units,
        (SELECT GROUP_CONCAT(g.area_code, ',') FROM course_ge g
          WHERE g.subject = c.subject AND g.catalog_num = c.catalog_num) AS ge_areas,
        (SELECT MAX(g.cultural_diversity) FROM course_ge g
          WHERE g.subject = c.subject AND g.catalog_num = c.catalog_num) AS cultural_diversity,
        (SELECT MAX(g.ethnic_studies_grad) FROM course_ge g
          WHERE g.subject = c.subject AND g.catalog_num = c.catalog_num) AS ethnic_studies_grad,
        (SELECT MAX(g.american_inst) FROM course_ge g
          WHERE g.subject = c.subject AND g.catalog_num = c.catalog_num) AS american_inst
    FROM sections s
    JOIN courses c ON s.course_id = c.course_id
    WHERE s.active = 1
"""


@sections_bp.route("/api/sections", methods=["GET"])
def search_sections():
    """
    Search/filter sections.

    Query params (all optional):
      subject   -> exact match, e.g. ?subject=CS ("GEN S" and "gens" work too)
      professor -> every typed word starts an instructor's first or last name
                   ("Rapp", "Rapp, Michael", "M Rapp")
      day       -> a single day letter/token that some timed meeting must
                   fall on, e.g. ?day=M (online-only sections never match)
      q         -> course code or title words: "CS 480", "cs4", "GEN S 147",
                   "data science" (see backend/search.py). Exact codes come
                   first, then code prefixes, then title matches.
      ge        -> GE area codes, comma separated, e.g. ?ge=3A,3B. Use ge=ALL
                   for any GE area. A section matches if its course counts for
                   ANY of the areas listed.
      cultural_diversity / ethnic_studies / american_inst -> set to 1 to only
                   show courses with that GE tag
      course_id -> one or more course ids, comma separated (all sections of
                   the courses a major needs, in one request)
      ids       -> one or more section ids, comma separated (the student's plan)
    course_id and ids take at most 200 numbers each; anything else is a 400.
    """
    query = BASE_QUERY
    conditions = []
    params = []

    for arg, column in (("course_id", "s.course_id"), ("ids", "s.section_id")):
        value = request.args.get(arg)
        if value is None:
            continue
        numbers = id_list(value)
        if numbers is None:
            return jsonify({"error": f"{arg} must be up to {MAX_ID_LIST} comma separated numbers"}), 400
        conditions.append(f"{column} IN ({','.join('?' * len(numbers))})")
        params.extend(numbers)

    subject = re.sub(r"[^A-Za-z0-9]", "", request.args.get("subject") or "").upper()
    if subject:
        conditions.append("c.subject = ?")
        params.append(subject)

    day = request.args.get("day")   # filtered below with parse_days, not LIKE

    conn = get_connection()
    # the typed text is matched in Python (backend/search.py), never put into SQL
    professor = request.args.get("professor")
    if professor and professor.strip():
        people = [r["professor_id"] for r in conn.execute("SELECT professor_id, first_name, last_name FROM professors")
                  if person_match(r["first_name"], r["last_name"], professor)]
        if not people:
            conn.close()
            return jsonify([])
        conditions.append("EXISTS (SELECT 1 FROM section_instructors i WHERE i.section_id = s.section_id "
                          f"AND i.professor_id IN ({','.join('?' * len(people))}))")
        params.extend(people)

    q = request.args.get("q")
    ranks = match_courses(get_course_index(conn, DB_PATH), q) if q else None
    if ranks is not None:
        if not ranks:
            conn.close()
            return jsonify([])
        conditions.append(f"s.course_id IN ({','.join('?' * len(ranks))})")
        params.extend(ranks)

    ge = request.args.get("ge")
    if ge:
        if ge.upper() == "ALL":
            conditions.append("EXISTS (SELECT 1 FROM course_ge g "
                              "WHERE g.subject = c.subject AND g.catalog_num = c.catalog_num)")
        else:
            codes = [c.strip().upper() for c in ge.split(",") if c.strip()]
            marks = ",".join(["?"] * len(codes))
            conditions.append("EXISTS (SELECT 1 FROM course_ge g "
                              "WHERE g.subject = c.subject AND g.catalog_num = c.catalog_num "
                              f"AND g.area_code IN ({marks}))")
            params.extend(codes)

    # tag filters (each needs some GE row for the course with that tag set)
    for arg, column in (("cultural_diversity", "cultural_diversity"),
                        ("ethnic_studies", "ethnic_studies_grad"),
                        ("american_inst", "american_inst")):
        if request.args.get(arg) == "1":
            conditions.append("EXISTS (SELECT 1 FROM course_ge g "
                              "WHERE g.subject = c.subject AND g.catalog_num = c.catalog_num "
                              f"AND g.{column} = 1)")

    if conditions:
        query += " AND " + " AND ".join(conditions)
    query += " ORDER BY c.subject, c.catalog_num, s.section_number"

    rows = conn.execute(query, params).fetchall()
    if ranks:
        # exact code first, then code prefixes, then title matches (stable: keeps subject, number, section)
        rows = sorted(rows, key=lambda r: ranks.get(r["course_id"], 0))
    result = sections_to_dicts(conn, rows)
    conn.close()

    if day:
        # 'T' must mean Tuesday only (not Thursday), so use the same parser
        # the conflict check uses instead of a text LIKE.
        wanted = DAY_TOKENS.get(day)
        if wanted:
            result = [s for s in result if any(is_timed(m) and wanted in parse_days(m["day"]) for m in s["meetings"])]
    return jsonify(result)


@sections_bp.route("/api/sections/<int:section_id>", methods=["GET"])
def get_section(section_id):
    conn = get_connection()
    rows = conn.execute(BASE_QUERY + " AND s.section_id = ?", (section_id,)).fetchall()
    result = sections_to_dicts(conn, rows)
    conn.close()
    if not result:
        return jsonify({"error": "section not found"}), 404
    return jsonify(result[0])


@sections_bp.route("/api/subjects", methods=["GET"])
def list_subjects():
    """The subjects that have sections this term, for the Search filter dropdown."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT DISTINCT c.subject FROM courses c
        WHERE EXISTS (SELECT 1 FROM sections s WHERE s.course_id = c.course_id AND s.active = 1)
        ORDER BY c.subject""").fetchall()
    conn.close()
    return jsonify([r["subject"] for r in rows])


@sections_bp.route("/api/ge-areas", methods=["GET"])
def list_ge_areas():
    """
    Every GE area with how many sections we currently have for it. Used to
    build the GE Scheduler filter buttons. Also returns the total number of
    distinct GE sections (for the "All GE" button).
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT a.area_code, a.name, a.grp, a.sort_order,
               COUNT(DISTINCT s.section_id) AS section_count
        FROM ge_areas a
        LEFT JOIN course_ge g ON g.area_code = a.area_code
        LEFT JOIN courses c ON c.subject = g.subject AND c.catalog_num = g.catalog_num
        LEFT JOIN sections s ON s.course_id = c.course_id AND s.active = 1
        GROUP BY a.area_code, a.name, a.grp, a.sort_order
        ORDER BY a.sort_order
    """).fetchall()
    total = conn.execute("""
        SELECT COUNT(DISTINCT s.section_id)
        FROM sections s
        JOIN courses c ON c.course_id = s.course_id
        WHERE s.active = 1 AND EXISTS (SELECT 1 FROM course_ge g
                      WHERE g.subject = c.subject AND g.catalog_num = c.catalog_num)
    """).fetchone()[0]
    conn.close()
    return jsonify({
        "total_sections": total,
        "areas": [dict(r) for r in rows],
    })

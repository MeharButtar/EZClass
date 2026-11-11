"""
Routes for majors: the list for the "What's your major?" prompt, the full
requirement tree for one major, and a course lookup for "open" rules like
"any PSY 300-599".

Requirement courses are matched to our class data by subject + catalog number.
Plenty of required courses have no sections in our data yet; they still come
back (has_sections false) so the student always sees the whole list.
"""

import re
import sqlite3

from flask import Blueprint, jsonify, request

from backend.models.db import get_connection, normalize_subject

majors_bp = Blueprint("majors", __name__)

MAJOR_ID_PATTERN = re.compile(r"^[a-z0-9_]{1,40}$")
SUBJECT_PATTERN = re.compile(r"^[A-Z]{1,8}$")
MAX_SUBJECTS = 12
MAX_COURSES = 200


def course_key(subject, catalog_num):
    return (normalize_subject(subject), str(catalog_num or "").strip().upper())


def course_lookup(conn):
    """(subject, catalog_num) -> course row with its section count, for every course we have."""
    rows = conn.execute("""
        SELECT c.course_id, c.subject, c.catalog_num, c.title, c.units,
               COUNT(s.section_id) AS section_count
        FROM courses c LEFT JOIN sections s ON s.course_id = c.course_id AND s.active = 1
        GROUP BY c.course_id
    """).fetchall()
    return {course_key(r["subject"], r["catalog_num"]): r for r in rows}


def ge_lookup(conn):
    """(subject, catalog_num) -> sorted list of GE area codes the course counts for."""
    areas = {}
    for r in conn.execute("SELECT subject, catalog_num, area_code FROM course_ge ORDER BY area_code"):
        areas.setdefault(course_key(r["subject"], r["catalog_num"]), []).append(r["area_code"])
    return areas


def course_to_dict(subject, catalog_num, courses, ge, title=None, units=None):
    match = courses.get(course_key(subject, catalog_num))
    return {
        "code": f"{subject} {catalog_num}",
        "subject": subject,
        "catalog_num": catalog_num,
        "title": title or (match["title"] if match else None),
        "units": units or (str(match["units"]) if match else None),
        "course_id": match["course_id"] if match else None,
        "section_count": match["section_count"] if match else 0,
        "has_sections": bool(match and match["section_count"]),
        "ge_areas": ge.get(course_key(subject, catalog_num), []),
    }


@majors_bp.route("/api/majors", methods=["GET"])
def list_majors():
    """Every major in data/majors/majors.csv, coming_soon ones included (the UI shows them disabled)."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT major_id, name, degree, status FROM majors ORDER BY name").fetchall()
    except sqlite3.OperationalError:
        rows = []   # database built before majors existed
    finally:
        conn.close()
    return jsonify([dict(r) for r in rows])


@majors_bp.route("/api/majors/<major_id>/requirements", methods=["GET"])
def major_requirements(major_id):
    """
    The requirement tree for one major:
      {"major": {...}, "sections": [{"name", "pool_units", "note", "groups": [
          {"label", "rule", "pick_n", "pick_units", "note", "open", "courses": [...]}]}]}
    "open" is {"subjects": [...], "min": 300, "max": 599, "exclude": ["ACCTG 325"]} for
    rules without a course list; the frontend fetches those courses from /api/courses
    and leaves out the excluded ones and the ones the major already requires.
    A "note" row is the section's note. A note shared by every course in a group
    is moved up to the group.
    """
    if not MAJOR_ID_PATTERN.match(major_id):
        return jsonify({"error": "major not found"}), 404
    conn = get_connection()
    try:
        major = conn.execute(
            "SELECT major_id, name, degree, catalog_year, status FROM majors WHERE major_id = ?", (major_id,)
        ).fetchone()
        if major is None:
            return jsonify({"error": "major not found"}), 404
        rows = conn.execute(
            "SELECT * FROM major_requirements WHERE major_id = ? ORDER BY id", (major_id,)
        ).fetchall()
        courses = course_lookup(conn)
        ge = ge_lookup(conn)
    except sqlite3.OperationalError:
        return jsonify({"error": "major not found"}), 404
    finally:
        conn.close()

    sections, groups = [], {}
    for r in rows:
        if not sections or sections[-1]["name"] != r["section"]:
            sections.append({"name": r["section"], "pool_units": None, "note": None, "groups": []})
        section = sections[-1]
        if r["rule"] == "note":       # a note for the whole section, shown once under its heading
            if r["note"]:
                section["note"] = f"{section['note']} {r['note']}" if section["note"] else r["note"]
            continue
        key = (r["section"], r["group_label"])
        group = groups.get(key)
        if group is None:
            group = {
                "label": r["group_label"], "rule": r["rule"], "pick_n": r["pick_n"],
                "pick_units": r["pick_units"], "note": None, "open": None,
                "courses": [], "_notes": [],
            }
            groups[key] = group
            section["groups"].append(group)
        if r["rule"] == "pool" and r["pick_units"]:
            section["pool_units"] = r["pick_units"]
        if r["rule"] == "open":
            group["open"] = {
                "subjects": [s for s in (r["subject"] or "").split("|") if s],
                "min": r["num_min"], "max": r["num_max"],
                "exclude": [c for c in (r["exclude"] or "").split("|") if c],
            }
            group["_notes"].append(r["note"])
            continue
        course = course_to_dict(r["subject"], r["catalog_num"], courses, ge, r["title"], r["units"])
        course["note"] = r["note"]
        group["courses"].append(course)
        group["_notes"].append(r["note"])

    for group in groups.values():
        notes = group.pop("_notes")
        if notes and len(set(notes)) == 1:
            group["note"] = notes[0]
            for course in group["courses"]:
                course["note"] = None

    return jsonify({"major": dict(major), "sections": sections})


@majors_bp.route("/api/courses", methods=["GET"])
def find_courses():
    """
    Course lookup for "open" rules.
      subject      -> required, one code or several joined by | (e.g. ACCTG|BA|FIN)
      min, max     -> catalog number range, compared on the number part (150L counts as 150)
      has_sections -> 1 to only return courses with sections in our data
    Returns {"courses": [...], "truncated": bool}, at most 200 courses.
    """
    raw = request.args.get("subject", "")
    subjects = [normalize_subject(s) for s in raw.split("|") if s.strip()]
    if not subjects or len(subjects) > MAX_SUBJECTS or not all(SUBJECT_PATTERN.match(s) for s in subjects):
        return jsonify({"error": "subject must be one or more course subject codes, like PSY or ACCTG|BA"}), 400

    bounds = []
    for name, default in (("min", 0), ("max", 9999)):
        value = request.args.get(name, "").strip()
        if value and not (value.isdigit() and len(value) <= 4):
            return jsonify({"error": f"{name} must be a whole number from 0 to 9999"}), 400
        bounds.append(int(value) if value else default)
    low, high = bounds
    if low > high:
        return jsonify({"error": "min must not be larger than max"}), 400

    only_offered = request.args.get("has_sections") == "1"
    marks = ",".join("?" * len(subjects))
    sql = f"""
        SELECT c.course_id, c.subject, c.catalog_num, c.title, c.units,
               COUNT(s.section_id) AS section_count
        FROM courses c LEFT JOIN sections s ON s.course_id = c.course_id AND s.active = 1
        WHERE c.subject IN ({marks}) AND CAST(c.catalog_num AS INTEGER) BETWEEN ? AND ?
        GROUP BY c.course_id
        {"HAVING COUNT(s.section_id) > 0" if only_offered else ""}
        ORDER BY c.subject, CAST(c.catalog_num AS INTEGER), c.catalog_num
        LIMIT ?
    """
    conn = get_connection()
    try:
        rows = conn.execute(sql, [*subjects, low, high, MAX_COURSES + 1]).fetchall()
        ge = ge_lookup(conn)
    finally:
        conn.close()

    courses = {course_key(r["subject"], r["catalog_num"]): r for r in rows}
    result = [course_to_dict(r["subject"], r["catalog_num"], courses, ge) for r in rows[:MAX_COURSES]]
    return jsonify({"courses": result, "truncated": len(rows) > MAX_COURSES})

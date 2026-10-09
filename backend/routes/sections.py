"""
Routes for searching/filtering course sections.
"""

from flask import Blueprint, jsonify, request

from backend.models.db import get_connection

sections_bp = Blueprint("sections", __name__)


def section_to_dict(row):
    return {
        "section_id": row["section_id"],
        "course_id": row["course_id"],
        "subject": row["subject"],
        "catalog_num": row["catalog_num"],
        "course_title": row["title"],
        "units": row["units"],
        "section_number": row["section_number"],
        "professor_name": row["professor_name"],
        "days": row["days"],
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "building": row["building"],
        "room_number": row["room_number"],
        "capacity": row["capacity"],
    }


BASE_QUERY = """
    SELECT
        s.section_id, s.course_id, s.section_number, s.days,
        s.start_time, s.end_time, s.capacity,
        c.subject, c.catalog_num, c.title, c.units,
        (p.first_name || ' ' || p.last_name) AS professor_name,
        r.building, r.room_number
    FROM sections s
    JOIN courses c ON s.course_id = c.course_id
    LEFT JOIN professors p ON s.professor_id = p.professor_id
    LEFT JOIN rooms r ON s.room_id = r.room_id
"""


@sections_bp.route("/api/sections", methods=["GET"])
def search_sections():
    """
    Search/filter sections.

    Query params (all optional):
      subject   -> exact match, e.g. ?subject=CS
      professor -> partial match on professor name
      day       -> a single day letter/token that must appear in the
                   section's day pattern, e.g. ?day=M
      q         -> free-text search across course title and catalog number
    """
    conn = get_connection()
    query = BASE_QUERY
    conditions = []
    params = []

    subject = request.args.get("subject")
    if subject:
        conditions.append("c.subject = ?")
        params.append(subject.upper())

    professor = request.args.get("professor")
    if professor:
        conditions.append("professor_name LIKE ?")
        params.append(f"%{professor}%")

    day = request.args.get("day")
    if day:
        conditions.append("s.days LIKE ?")
        params.append(f"%{day}%")

    q = request.args.get("q")
    if q:
        conditions.append("(c.title LIKE ? OR c.catalog_num LIKE ?)")
        params.append(f"%{q}%")
        params.append(f"%{q}%")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY c.subject, c.catalog_num, s.section_number"

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([section_to_dict(r) for r in rows])


@sections_bp.route("/api/sections/<int:section_id>", methods=["GET"])
def get_section(section_id):
    conn = get_connection()
    row = conn.execute(BASE_QUERY + " WHERE s.section_id = ?", (section_id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({"error": "section not found"}), 404
    return jsonify(section_to_dict(row))


@sections_bp.route("/api/subjects", methods=["GET"])
def list_subjects():
    """Returns the distinct list of subjects, for populating a filter dropdown."""
    conn = get_connection()
    rows = conn.execute("SELECT DISTINCT subject FROM courses ORDER BY subject").fetchall()
    conn.close()
    return jsonify([r["subject"] for r in rows])

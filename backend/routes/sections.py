"""
Routes for searching/filtering course sections.
"""

from flask import Blueprint, jsonify, request

from backend.models.conflicts import DAY_TOKENS, parse_days
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
        # GE info: list of area codes like ["3A"], plus the three tags
        "ge_areas": row["ge_areas"].split(",") if row["ge_areas"] else [],
        "cultural_diversity": bool(row["cultural_diversity"]),
        "ethnic_studies_grad": bool(row["ethnic_studies_grad"]),
        "american_inst": bool(row["american_inst"]),
    }


BASE_QUERY = """
    SELECT
        s.section_id, s.course_id, s.section_number, s.days,
        s.start_time, s.end_time, s.capacity,
        c.subject, c.catalog_num, c.title, c.units,
        (p.first_name || ' ' || p.last_name) AS professor_name,
        r.building, r.room_number,
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
      ge        -> GE area codes, comma separated, e.g. ?ge=3A,3B. Use ge=ALL
                   for any GE area. A section matches if its course counts for
                   ANY of the areas listed.
      cultural_diversity / ethnic_studies / american_inst -> set to 1 to only
                   show courses with that GE tag
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

    day = request.args.get("day")   # filtered below with parse_days, not LIKE

    q = request.args.get("q")
    if q:
        conditions.append("(c.title LIKE ? OR c.catalog_num LIKE ?)")
        params.append(f"%{q}%")
        params.append(f"%{q}%")

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
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY c.subject, c.catalog_num, s.section_number"

    rows = conn.execute(query, params).fetchall()
    conn.close()

    if day:
        # 'T' must mean Tuesday only (not Thursday), so use the same parser
        # the conflict check uses instead of a text LIKE.
        wanted = DAY_TOKENS.get(day)
        if wanted:
            rows = [r for r in rows if wanted in parse_days(r["days"])]
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
        LEFT JOIN sections s ON s.course_id = c.course_id
        GROUP BY a.area_code, a.name, a.grp, a.sort_order
        ORDER BY a.sort_order
    """).fetchall()
    total = conn.execute("""
        SELECT COUNT(DISTINCT s.section_id)
        FROM sections s
        JOIN courses c ON c.course_id = s.course_id
        WHERE EXISTS (SELECT 1 FROM course_ge g
                      WHERE g.subject = c.subject AND g.catalog_num = c.catalog_num)
    """).fetchone()[0]
    conn.close()
    return jsonify({
        "total_sections": total,
        "areas": [dict(r) for r in rows],
    })

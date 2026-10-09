"""
Route for checking a proposed set of sections for scheduling conflicts.
This is the "build my schedule" feature: the frontend sends a list of
section_ids the user has picked, and this route reports back whether any
of them conflict with each other.
"""

from flask import Blueprint, jsonify, request

from backend.models.conflicts import find_conflicts
from backend.models.db import get_connection

schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.route("/api/schedule/check", methods=["POST"])
def check_schedule():
    """
    Expects JSON body: {"section_ids": [1, 2, 3]}
    Returns: {"conflicts": [{"section_a": {...}, "section_b": {...}}, ...]}
    An empty "conflicts" list means the schedule is conflict-free.
    """
    body = request.get_json(silent=True) or {}
    section_ids = body.get("section_ids", [])

    if not section_ids:
        return jsonify({"conflicts": []})

    conn = get_connection()
    placeholders = ",".join(["?"] * len(section_ids))
    rows = conn.execute(
        f"SELECT * FROM sections WHERE section_id IN ({placeholders})",
        section_ids,
    ).fetchall()
    conn.close()

    sections = [dict(r) for r in rows]
    conflict_pairs = find_conflicts(sections)

    return jsonify({
        "conflicts": [
            {"section_a": a, "section_b": b} for a, b in conflict_pairs
        ],
        "conflict_free": len(conflict_pairs) == 0,
    })

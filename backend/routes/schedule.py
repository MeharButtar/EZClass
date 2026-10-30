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

MAX_SECTIONS = 60   # far more than anyone takes in a term; keeps the query small


def bad_request(message):
    return jsonify({"error": message, "conflicts": [], "conflict_free": False}), 400


@schedule_bp.route("/api/schedule/check", methods=["POST"])
def check_schedule():
    """
    Expects JSON body: {"section_ids": [1, 2, 3]}
    Returns: {"conflicts": [{"section_a": {...}, "section_b": {...}}, ...],
              "conflict_free": true/false}
    An empty "conflicts" list means the schedule is conflict-free.
    Anything other than a list of up to 60 whole numbers gets a 400.
    """
    body = request.get_json(silent=True)
    if body is None:
        body = {}   # no body, or not JSON at all: nothing to check
    if not isinstance(body, dict):
        return bad_request("body must be a JSON object")

    section_ids = body.get("section_ids", [])
    if not isinstance(section_ids, list):
        return bad_request("section_ids must be a list")
    if len(section_ids) > MAX_SECTIONS:
        return bad_request(f"at most {MAX_SECTIONS} sections can be checked at once")
    # bool is a subclass of int in Python, so True would sneak through without the extra check.
    # The range check stops huge numbers that SQLite can't store (it would raise, a 500).
    if not all(isinstance(i, int) and not isinstance(i, bool) and 0 <= i < 2**63 for i in section_ids):
        return bad_request("section_ids must be whole numbers")

    if not section_ids:
        return jsonify({"conflicts": [], "conflict_free": True})

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

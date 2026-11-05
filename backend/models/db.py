"""
Database connection + load helpers.

Local dev uses SQLite (zero setup, same SQL you'll run in MySQL Workbench
later). To move to real MySQL, only this file needs to change: swap
sqlite3 for a MySQL driver (e.g. mysql-connector-python or PyMySQL) and
update DB_PATH -> connection credentials. The schema.sql file is already
written to be portable (see notes at its bottom).
"""

import csv
import os
import sqlite3

try:
    import fcntl   # Linux/macOS only; on Windows we just skip the lock
except ImportError:
    fcntl = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# EZCLASS_DB_PATH lets a host (or the tests) put the database somewhere else
DB_PATH = os.path.abspath(os.environ.get("EZCLASS_DB_PATH") or os.path.join(BASE_DIR, "backend", "sql", "scheduler.db"))
SCHEMA_PATH = os.path.join(BASE_DIR, "backend", "sql", "schema.sql")
PLACEHOLDER_DIR = os.path.join(BASE_DIR, "data", "placeholder")
CLEANED_DIR = os.path.join(BASE_DIR, "data", "cleaned")
GE_DIR = os.path.join(BASE_DIR, "data", "ge")
MAJORS_DIR = os.path.join(BASE_DIR, "data", "majors")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema():
    """(Re)creates all tables from schema.sql. Wipes existing data."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Schema created at {DB_PATH}")


def normalize_subject(subject):
    """'POL S' -> 'POLS', 'b a' -> 'BA'. Subject codes are compared in this form everywhere."""
    return "".join(str(subject or "").split()).upper()


def load_csv_into_table(conn, csv_path, table_name):
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            print(f"  {table_name}: no rows in {csv_path}, skipping")
            return
        columns = list(rows[0].keys())
        placeholders = ", ".join(["?"] * len(columns))
        col_list = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})"
        # Subject codes may arrive with spaces ("POL S"); store them the way the
        # majors data writes them ("POLS") so subject + catalog_num matches.
        if "subject" in columns:
            for row in rows:
                row["subject"] = normalize_subject(row["subject"])
        # blank cells become NULL (e.g. a section with no professor yet)
        conn.executemany(sql, [tuple(None if v == "" else v for v in row.values()) for row in rows])
        print(f"  {table_name}: loaded {len(rows)} rows")


def load_csvs(data_dir=PLACEHOLDER_DIR):
    """
    Loads professors, rooms, courses, sections, students CSVs (in that
    order, since sections has foreign keys into the other four) from
    data_dir into the database. Point this at data/cleaned/ once real
    data is ready, using the same column names as the placeholder CSVs.
    """
    conn = get_connection()
    order = ["professors", "rooms", "courses", "sections", "section_meetings", "section_instructors", "students"]
    print(f"Loading CSVs from {data_dir}")
    for table in order:
        csv_path = os.path.join(data_dir, f"{table}.csv")
        if os.path.exists(csv_path):
            load_csv_into_table(conn, csv_path, table)
        else:
            print(f"  {table}: {csv_path} not found, skipping")
    conn.commit()
    conn.close()


def load_ge(ge_dir=GE_DIR):
    """
    Loads the General Education tables: ge_areas.csv (the list of areas) and
    ge_courses.csv (which course counts for which area) into ge_areas and
    course_ge. Same GE data no matter which class data you loaded.
    """
    conn = get_connection()
    print(f"Loading GE data from {ge_dir}")
    for csv_name, table in [("ge_areas.csv", "ge_areas"), ("ge_courses.csv", "course_ge")]:
        csv_path = os.path.join(ge_dir, csv_name)
        if os.path.exists(csv_path):
            load_csv_into_table(conn, csv_path, table)
        else:
            print(f"  {table}: {csv_path} not found, skipping")
    conn.commit()
    conn.close()


def schema_block(name):
    """One marked block of schema.sql (between "-- name:begin" and "-- name:end")."""
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        text = f.read()
    return text.split(f"-- {name}:begin", 1)[1].split(f"-- {name}:end", 1)[0]


def majors_schema():
    """Just the majors tables from schema.sql."""
    return schema_block("majors")


# columns sections gained with section_meetings; older databases get them added
NEW_SECTION_COLUMNS = [("seats_text", "TEXT"), ("seats_total", "INTEGER"), ("active", "INTEGER NOT NULL DEFAULT 1"),
                       ("section_title", "TEXT")]


def _minutes(text):
    """'14:30' -> 870, anything else -> None"""
    try:
        h, m = str(text).strip().split(":")[:2]
        return int(h) * 60 + int(m)
    except (ValueError, AttributeError):
        return None


def sections_need_upgrade():
    """True if the database predates section_meetings (or is missing a new column)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        try:
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            if not {"section_meetings", "section_instructors"} <= tables:
                return True
            columns = {r[1] for r in conn.execute("PRAGMA table_info(sections)")}
            return not all(name in columns for name, _ in NEW_SECTION_COLUMNS)
        finally:
            conn.close()
    except sqlite3.Error:
        return False


def upgrade_sections():
    """
    Brings sections data in the older one-meeting shape up to date, without
    dropping or changing anything that's there. Safe to run any number of
    times:
      - adds section_meetings / section_instructors and the new sections columns
      - a section with no meetings gets meeting 0 from its days/start/end/room
      - a section with no instructors gets its professor_id
      - seats come from capacity where they're missing
    """
    conn = get_connection()
    conn.executescript(schema_block("meetings"))
    columns = {r[1] for r in conn.execute("PRAGMA table_info(sections)")}
    for name, decl in NEW_SECTION_COLUMNS:
        if name not in columns:
            conn.execute(f"ALTER TABLE sections ADD COLUMN {name} {decl}")
    conn.execute("""UPDATE sections SET seats_total = capacity, seats_text = CAST(capacity AS TEXT)
                    WHERE seats_total IS NULL AND (seats_text IS NULL OR seats_text = '') AND capacity IS NOT NULL""")
    rows = conn.execute("""
        SELECT s.section_id, s.days, s.start_time, s.end_time, r.building, r.room_number
        FROM sections s LEFT JOIN rooms r ON r.room_id = s.room_id
        WHERE s.days IS NOT NULL AND s.days != ''
          AND NOT EXISTS (SELECT 1 FROM section_meetings m WHERE m.section_id = s.section_id)""").fetchall()
    conn.executemany(
        """INSERT INTO section_meetings (section_id, idx, day_code, start_min, end_min, building, room, is_online)
           VALUES (?, 0, ?, ?, ?, ?, ?, 0)""",
        [(r["section_id"], r["days"], _minutes(r["start_time"]), _minutes(r["end_time"]), r["building"], r["room_number"])
         for r in rows])
    added = conn.execute("""
        INSERT INTO section_instructors (section_id, professor_id, idx)
        SELECT s.section_id, s.professor_id, 0 FROM sections s
        WHERE s.professor_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM section_instructors i WHERE i.section_id = s.section_id)""").rowcount
    conn.commit()
    conn.close()
    if rows or added:
        print(f"  upgraded: {len(rows)} sections got meetings, {added} got instructors")


def _int_or_none(value):
    value = (value or "").strip()
    return int(value) if value.isdigit() else None


def load_majors(majors_dir=MAJORS_DIR):
    """
    Loads majors.csv and major_requirements.csv into the majors tables.
    Subject codes are normalized ("B A" -> "BA", and each code in an open rule's
    "ACCTG|BA" list). A required course with no sections in our data still
    loads; it just shows as not offered. A missing folder is not an error.
    """
    majors_csv = os.path.join(majors_dir, "majors.csv")
    reqs_csv = os.path.join(majors_dir, "major_requirements.csv")
    if not os.path.exists(majors_csv):
        print(f"  majors: {majors_csv} not found, skipping")
        return
    conn = get_connection()
    conn.executescript(majors_schema())
    # only ever called on a full rebuild or when majors is empty, so this clears
    # nothing but a half-finished earlier load
    conn.execute("DELETE FROM major_requirements")
    conn.execute("DELETE FROM majors")
    with open(majors_csv, newline="", encoding="utf-8") as f:
        majors = [r for r in csv.DictReader(f) if (r.get("major_id") or "").strip()]
    conn.executemany(
        "INSERT INTO majors (major_id, name, degree, college, catalog_year, status) VALUES (?, ?, ?, ?, ?, ?)",
        [(m["major_id"].strip(), m["name"].strip(), m.get("degree") or None, m.get("college") or None,
          m.get("catalog_year") or None, (m.get("status") or "live").strip()) for m in majors],
    )
    print(f"  majors: loaded {len(majors)} rows")

    known = {m["major_id"].strip() for m in majors}
    rows = []
    if os.path.exists(reqs_csv):
        with open(reqs_csv, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if (r.get("major_id") or "").strip() not in known:
                    print(f"  major_requirements: skipping row for unknown major {r.get('major_id')!r}")
                    continue
                subject = "|".join(normalize_subject(s) for s in (r.get("subject") or "").split("|") if s.strip())
                rows.append((
                    r["major_id"].strip(), r["section"].strip(), r["group_label"].strip(), r["rule"].strip().lower(),
                    _int_or_none(r.get("pick_n")), (r.get("pick_units") or "").strip() or None,
                    subject or None, (r.get("catalog_num") or "").strip().upper() or None,
                    _int_or_none(r.get("num_min")), _int_or_none(r.get("num_max")),
                    (r.get("title") or "").strip() or None, (r.get("units") or "").strip() or None,
                    (r.get("note") or "").strip() or None,
                ))
    conn.executemany(
        """INSERT INTO major_requirements (major_id, section, group_label, rule, pick_n, pick_units,
           subject, catalog_num, num_min, num_max, title, units, note)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", rows)
    print(f"  major_requirements: loaded {len(rows)} rows")
    conn.commit()
    conn.close()


def majors_loaded():
    """True if the majors table exists and has rows."""
    try:
        conn = sqlite3.connect(DB_PATH)
        try:
            return conn.execute("SELECT COUNT(*) FROM majors").fetchone()[0] > 0
        finally:
            conn.close()
    except sqlite3.Error:
        return False


def database_has_data():
    """True if the database file exists and has at least one section."""
    if not os.path.exists(DB_PATH):
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        try:
            return conn.execute("SELECT COUNT(*) FROM sections").fetchone()[0] > 0
        finally:
            conn.close()
    except sqlite3.Error:
        return False   # no sections table yet, or not a database at all


def build_database(data_dir):
    """Wipes and reloads everything: schema, class CSVs from data_dir, GE data."""
    init_schema()
    load_csvs(data_dir)
    upgrade_sections()   # one-meeting CSVs (the placeholder data) get their meetings here
    load_ge()
    load_majors()


def ensure_database():
    """
    Builds the database on first start (fresh clone, fresh container) so the
    app works without a manual db.py step. Never wipes a database that
    already has sections in it. Uses data/cleaned if it exists, otherwise
    data/placeholder. A database built before majors existed gets just the
    majors tables added.

    Several gunicorn workers import the app at the same moment, so the build
    happens under a file lock and we check again once we hold it: the first
    worker builds, the others wait and then see the data is there.
    """
    if (database_has_data() and (majors_loaded() or not os.path.isdir(MAJORS_DIR))
            and not sections_need_upgrade()):
        return
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH + ".lock", "w") as lock:
        if fcntl:
            fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            if database_has_data():
                if not majors_loaded() and os.path.isdir(MAJORS_DIR):
                    print(f"Adding majors to {DB_PATH}")
                    load_majors()
                if sections_need_upgrade():
                    print(f"Adding section meetings to {DB_PATH}")
                    upgrade_sections()
                return
            data_dir = CLEANED_DIR if os.path.isdir(CLEANED_DIR) else PLACEHOLDER_DIR
            print(f"No class data in {DB_PATH}, building it from {data_dir}")
            build_database(data_dir)
        finally:
            if fcntl:
                fcntl.flock(lock, fcntl.LOCK_UN)


if __name__ == "__main__":
    import sys
    # python3 backend/models/db.py            -> placeholder data
    # python3 backend/models/db.py data/cleaned -> real data from the template
    # python -m backend.models.db data/cleaned   -> same thing, as a module (Dockerfile)
    data_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else PLACEHOLDER_DIR
    build_database(data_dir)
    print("\nDatabase ready.")

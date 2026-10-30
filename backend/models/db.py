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


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema():
    """(Re)creates all tables from schema.sql. Wipes existing data."""
    conn = get_connection()
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print(f"Schema created at {DB_PATH}")


def load_csv_into_table(conn, csv_path, table_name):
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            print(f"  {table_name}: no rows in {csv_path}, skipping")
            return
        columns = rows[0].keys()
        placeholders = ", ".join(["?"] * len(columns))
        col_list = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({col_list}) VALUES ({placeholders})"
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
    order = ["professors", "rooms", "courses", "sections", "students"]
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
    load_ge()


def ensure_database():
    """
    Builds the database on first start (fresh clone, fresh container) so the
    app works without a manual db.py step. Never touches a database that
    already has sections in it. Uses data/cleaned if it exists, otherwise
    data/placeholder.

    Several gunicorn workers import the app at the same moment, so the build
    happens under a file lock and we check again once we hold it: the first
    worker builds, the others wait and then see the data is there.
    """
    if database_has_data():
        return
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH + ".lock", "w") as lock:
        if fcntl:
            fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            if database_has_data():
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

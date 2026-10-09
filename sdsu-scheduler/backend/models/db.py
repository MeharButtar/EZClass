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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "backend", "sql", "scheduler.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "backend", "sql", "schema.sql")
PLACEHOLDER_DIR = os.path.join(BASE_DIR, "data", "placeholder")


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


if __name__ == "__main__":
    import sys
    # python3 backend/models/db.py            -> placeholder data
    # python3 backend/models/db.py data/cleaned -> real data from the template
    data_dir = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else PLACEHOLDER_DIR
    init_schema()
    load_csvs(data_dir)
    print("\nDatabase ready.")

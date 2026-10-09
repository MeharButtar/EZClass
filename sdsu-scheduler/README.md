# SDSU Class Scheduler — CS514 Final Project

Phase 1 of the project: a fully working scheduler running on synthetic
placeholder data. Real SDSU data gets swapped in later without changing
any code, just the CSV files it imports from.

## What's actually working right now

- A real database (SQLite for local dev, same SQL style as MySQL) with
  Courses, Sections, Professors, Rooms, Students, and Enrollments
- 52 placeholder sections across 5 subjects (CS, MATH, PHYS, ENGL, HIST),
  including 4 sections that deliberately overlap in time so conflict
  detection has something real to catch
- A Flask backend with working routes: search/filter sections, get one
  section, list subjects, and check a set of sections for conflicts
- A basic frontend: search by subject/day/professor/keyword, add
  sections to "My Schedule", and check for conflicts with one click
- Conflict-detection logic that correctly parses day patterns (MW, TTh,
  MWF, TR, etc.) and catches time overlaps

## How to run it

```bash
# from the project root
pip install -r requirements.txt --break-system-packages   # if needed

# (re)build the database from schema + placeholder CSVs
python3 backend/models/db.py

# start the server
python3 backend/app.py
```

Then open **http://localhost:5000** in a browser. That's it, one server,
frontend and backend both served from it.

## Project layout

```
sdsu-scheduler/
├── backend/
│   ├── app.py                  # Flask entry point, run this
│   ├── routes/
│   │   ├── sections.py         # search/filter/list section routes
│   │   └── schedule.py         # conflict-check route
│   ├── models/
│   │   ├── db.py                # DB connection + CSV loader
│   │   └── conflicts.py         # conflict-detection logic (has its own tests, see below)
│   └── sql/
│       └── schema.sql           # CREATE TABLE statements (portable to MySQL)
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/app.js                 # all frontend logic, fetch() calls to the backend
├── data/
│   ├── placeholder/              # generate_placeholder_data.py + its output CSVs
│   ├── raw/                      # put real SDSU downloads here (untouched)
│   └── cleaned/                  # put reshaped real data here (matches placeholder CSV columns)
├── docs/                         # ER diagram, notes go here
└── requirements.txt
```

## Regenerating placeholder data

```bash
cd data/placeholder
python3 generate_placeholder_data.py
```

This overwrites the CSVs with a fresh (but reproducible, seeded) batch.
Edit the constants at the top of the script (subjects, names, counts) if
you want a different mix.

## Adding real data (the easy way)

1. Open `data/template/EzClass_Data_Template.xlsx` and read the Instructions sheet.
2. Fill in the **Sections** sheet, one row per section. No ids needed.
3. Check it and build the CSVs: `python3 data/import_real_data.py data/template/EzClass_Data_Template.xlsx`
   (it lists any row with a problem so you can fix it).
4. Load it: `python3 backend/models/db.py data/cleaned`
5. Start the app as usual. To go back to placeholder data, run `python3 backend/models/db.py`.

## Moving to real data later (manual version)

1. Download the SDSU public class schedule export (Excel) for the term.
2. Reshape it into `data/cleaned/courses.csv`, `sections.csv`, etc., using
   the exact same column names as the placeholder CSVs (open one to see
   the format).
3. Instructor names need separate lookup since the public export doesn't
   include them, see the project doc for the plan on scoping this down
   to a handful of departments.
4. Run `python3 backend/models/db.py` again, but change
   `load_csvs(PLACEHOLDER_DIR)` to `load_csvs(<path to data/cleaned>)`
   in the `if __name__ == "__main__":` block at the bottom of `db.py`.

## Moving from SQLite to real MySQL

Only `backend/models/db.py` needs to change:
- Swap `import sqlite3` for a MySQL driver (`mysql-connector-python` or
  `PyMySQL`)
- Replace `get_connection()` with a MySQL connection using your
  Workbench credentials
- `schema.sql` already has MySQL notes at the bottom (mainly:
  `AUTOINCREMENT` → `AUTO_INCREMENT`)

Everything else (routes, conflict logic, frontend) stays exactly the same,
since they only ever talk to `get_connection()`, not to SQLite directly.

## Testing conflict detection

The 4 placeholder sections with `section_number` starting with `C`
(C49-C52 in the generated data) are deliberately overlapping pairs.
Selecting all 4 in the UI and clicking "Check for Conflicts" should
report exactly 2 conflicts. This was verified while building this: see
`backend/models/conflicts.py` for the logic itself if you want to extend
it (e.g. handling back-to-back classes with no gap, or cross-listed
sections).

## What's NOT done yet (see the project doc for full scope/roles/obstacles)

- Real SDSU data import
- Student accounts / login / saved schedules
- Deployment (Railway or similar)
- Frontend styling polish (current CSS is functional, not final)

## AI usage

See AI_USAGE.md for where AI helped and what the team added.

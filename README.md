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
pip install -r requirements-dev.txt --break-system-packages   # if needed

# (re)build the database from schema + the real class CSVs
python3 backend/models/db.py data/cleaned

# start the server
python3 backend/app.py
```

Then open **http://localhost:5000** in a browser. That's it, one server,
frontend and backend both served from it.

- `requirements.txt` is what the live site needs (Flask, gunicorn).
  `requirements-dev.txt` adds `openpyxl`, which only the Excel importer uses.
- If the database is missing or empty, the app builds it by itself on start
  (from `data/cleaned`). It never wipes a database that already has classes in it.
- Debug mode is off unless you set `FLASK_DEBUG=1`. The port comes from `PORT` (default 5000).

## Project layout

```
sdsu-scheduler/
├── backend/
│   ├── app.py                  # Flask entry point, run this
│   ├── routes/
│   │   ├── sections.py         # search/filter/list section routes
│   │   ├── schedule.py         # conflict-check route
│   │   └── analytics.py        # anonymous visit counting + admin stats
│   ├── models/
│   │   ├── db.py                # DB connection + CSV loader
│   │   └── conflicts.py         # conflict-detection logic (has its own tests, see below)
│   └── sql/
│       └── schema.sql           # CREATE TABLE statements (portable to MySQL)
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── app.js                # all frontend logic, fetch() calls to the backend
│       └── track.js              # anonymous visit counting (watches the page, app.js untouched)
├── data/
│   ├── placeholder/              # generate_placeholder_data.py + its output CSVs
│   ├── raw/                      # put real SDSU downloads here (untouched)
│   └── cleaned/                  # put reshaped real data here (matches placeholder CSV columns)
├── docs/                         # ER diagram, notes go here
├── tests/test_smoke.py           # smoke tests: python3 -m unittest discover -s tests -v
├── Dockerfile                    # production image (gunicorn)
├── .env.example                  # every setting the app reads
├── requirements.txt              # what production needs
└── requirements-dev.txt          # + openpyxl for the Excel importer
```

## Regenerating placeholder data

```bash
cd data/placeholder
python3 generate_placeholder_data.py
```

This overwrites the CSVs with a fresh (but reproducible, seeded) batch.
Edit the constants at the top of the script (subjects, names, counts) if
you want a different mix.

## GE Scheduler

The site has a home page, a Search view, and a GE Scheduler view, with a cart on
the right that stays put across views. The GE Scheduler filters classes by GE
area (1A, 1B, 1C, 2, 3A, 3B, 4, 5A to 5C, 6, and the upper-division Explorations)
and by the cultural diversity, Ethnic Studies and American Institutions tags.

- GE data lives in `data/ge/`. `ge_courses.csv` was built from the SDSU catalog's
  General Education page with `python3 data/ge/parse_ge_guide.py <saved page.txt>`.
- `python3 backend/models/db.py data/cleaned` loads your classes AND the GE tables.
- A class only shows up under a GE area if its subject and course number are in
  `ge_courses.csv`, so there is nothing extra to fill in when adding classes.

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

## Deploying it

The app ships as one Docker image: Flask behind gunicorn, with the class
database built into the image. Any host that runs a Dockerfile and sets `PORT`
works the same way (Render, Fly, AWS App Runner / ECS).

### Run the production image locally

```bash
docker build -t ezclass .
docker run --rm -p 8000:8000 \
  -e ADMIN_TOKEN=pick-a-long-random-string \
  -e ANALYTICS_DB_PATH=/data/analytics.db \
  -v ezclass-data:/data \
  ezclass
```

Open http://localhost:8000. `.env.example` lists every setting; copy it to
`.env` and use `docker run --env-file .env ...` instead of the `-e` flags.
Make a token with `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`.

### Render

1. Push the branch to GitHub (Render deploys from the repo).
2. On render.com: **New → Web Service**, connect GitHub, pick the **EZClass** repo
   and the branch to deploy.
3. Language: **Docker** (Render picks this up from the `Dockerfile`). Leave the
   build and start commands empty; the Dockerfile has them. Render sets `PORT`
   and the image's start command already listens on it.
4. Instance type: **Free** is fine for the class project.
5. **Environment**: add `ADMIN_TOKEN` (long random string). Optionally
   `ANALYTICS_ENABLED=0` to switch counting off.
6. Under **Advanced**, set **Health Check Path** to `/api/health` (it returns 503
   if the class database can't be read).
7. Create the service. The URL is shown at the top, like `https://ezclass.onrender.com`.
   Every push to that branch redeploys.

**Visit counts reset on free hosting.** Render's free web services have no
persistent disk: the container's files are thrown away on every deploy and
restart, and a free service also goes to sleep after about 15 minutes with no
visitors (the next visit takes a minute or so to wake it). So `analytics.db`
starts empty again regularly. Treat the free-plan stats as "since the last
restart", and read them with `curl` before you push a change if you want to
keep the numbers. The class data is not affected: it's baked into the image.

To keep counts across deploys, move to a paid instance, add a **Disk** with
mount path `/data`, and set `ANALYTICS_DB_PATH=/data/analytics.db`. If
`/api/event` then returns 503 and the logs say "could not save analytics
event", the disk isn't writable by the image's non-root user (uid 1000).

### Reading the visit stats

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" "https://<your-domain>/api/admin/stats?days=14"
```

`days` can be 1 to 90. You get totals, visitors today and in the last 7 days,
a per-day list, counts per event, page views per view, the most picked GE areas,
conflict check outcomes, and mobile vs desktop. Dates are UTC. Without
`ADMIN_TOKEN` set, the stats URL returns 404.

### What is tracked (and what isn't)

`frontend/js/track.js` sends small anonymous events: page views (home, search,
GE), searches (subject, day, result count, and only *whether* the professor or
keyword box was used), GE searches (areas picked, result count), cart adds,
removes and clears (cart size), and conflict checks (conflict free or not).
Each event carries a random visitor id (localStorage) and session id
(sessionStorage), and the server records "mobile" or "desktop".

Never stored: names, emails, IP addresses, cookies, full user agents, or text
typed into the search boxes. The production access log also leaves out IPs,
user agents and query strings. Counting is off for browsers that send Do Not
Track or Global Privacy Control, and anyone can turn it off with the link in the
footer. Events go to their own SQLite file, separate from the class data.

Set `ANALYTICS_ENABLED=0` to switch counting off completely (`/api/event` then
accepts and drops everything).

### Running the tests

```bash
python3 -m unittest discover -s tests -v
```

They use throwaway databases in a temp folder, so they never touch your local
`scheduler.db` or `analytics.db`.

### Before adding accounts

Logins and saved schedules will need a hosted database (Render Postgres, a
MySQL host, AWS RDS, etc.) that survives redeploys. A SQLite file inside the
container gets wiped on every deploy, so it only works for the read-only class
data and (with a volume) the visit counts.

## What's NOT done yet (see the project doc for full scope/roles/obstacles)

- Student accounts / login / saved schedules (needs a hosted database first, see above)
- Weekly calendar view of the cart
- Major Prep and Prereqs pages (shown as "coming soon")
- Actually putting the site live (the Docker image is ready, see "Deploying it")
- Frontend styling polish (current CSS is functional, not final)

## AI usage

See AI_USAGE.md for where AI helped and what the team added.

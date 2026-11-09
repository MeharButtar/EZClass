# EzClass, a class scheduler built around your major (CS514 Final Project)

A student picks their major and instantly sees every class it requires, with
this term's sections under each one. They add sections to a plan, see the week
on a calendar as they go, check GE areas their major already covers, and keep
up to three plans (A, B, C). Everything they pick stays in their own browser.

## What's working right now

- **Home** (`index.html`): a landing page with a short animated week.
- **My Major** (`major.html`), the main feature: pick a major from the prompt
  and see every requirement grouped as the catalog does (Preparation for the
  Major, Major, Electives). Each course shows its sections, or is greyed out as
  "not offered or not in our data yet". "I took this" marks completed courses;
  progress counters show which groups are done.
- **GE Scheduler** (`ge.html`): one block per GE area (14), with an area strip to
  jump between them, a day filter and the CD / ES / AI tags. Areas that a course
  from your major already covers are marked "Covered by your major".
- **Search** (`search.html`): subject, day, professor and keyword search,
  as you type. The keyword box takes a course code any way it's written
  (`CS 480`, `cs480`, `GEN S 147`, `BIOL 211L`), the start of one (`CS 4`,
  `150`), a subject alone (`CS`, never "physiCS"), or the start of title words
  (`data science`, `hip hop` finds MUSIC 351's own section titles). The
  professor box takes a name in any order (`Rapp, Michael`, `M Rapp`). The
  rules live in `backend/search.py` and the GE page uses the same search.
- For classes in their plan, students can save the RateMyProfessors rating
  (and difficulty) they looked up, on My Schedule or from the calendar card.
  Scores are kept per professor in the browser only, and show next to that
  professor's name on every page.
- Professor names everywhere link to a RateMyProfessors search (new tab), and
  section rows show their GE areas and the CD / ES / AI tags. A cart saved by
  the first version comes back as Plan A, and old `/#ge` and `/#search` links
  open the new pages.
- **Reviews** (`reviews.html`) and **Support** (`support.html`): students can
  rate the site and report a wrong class time, a missing class or a bug. No
  accounts; reviews show only after the owner approves them (see "Reviews and
  support messages" below). Both are in the top bar on every page; on phones
  they sit under "More" in the bottom tab bar (and in the home page header).
- **My Schedule** (`schedule.html`): plan tabs (A, B, C) with rename, duplicate,
  delete and undo, the full-size week, a stats strip (units, hours, days on
  campus, gaps) and the conflict check. Two or more sections of one course
  are allowed (backups); the calendar says so and units count the course once.
- On My Major, GE and Search the week calendar is docked on the right (a "My
  week" sheet on phones). Pointing at a section draws a dashed preview on it,
  which turns red if it would overlap something already in the plan.
- Real class data for Spring 2027: 2,284 sections of 777 courses in 87
  subjects, GE data (750 course links) and five launch majors. A section can
  meet more than once (lecture + lab, or a timed part and an online part) and
  have more than one professor: each timed meeting gets its own block on the
  calendar, hybrid sections say "+ online part", and the 411 online-only
  sections are listed under "Online / no set time" instead of on the grid
  (they never count as overlapping). 108 sections (the PA and 400-599 business
  courses) have no days or times entered yet: they show "Time not listed yet"
  in the same list and can still be added to a plan. Required courses with no
  sections show as not offered.

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
│   │   ├── sections.py         # search/filter sections, subjects, GE areas
│   │   ├── majors.py           # majors, requirement tree, course lookup for open rules
│   │   ├── schedule.py         # conflict-check route
│   │   └── analytics.py        # anonymous visit counting + admin stats
│   ├── models/
│   │   ├── db.py                # DB connection + CSV loader
│   │   └── conflicts.py         # conflict-detection logic (has its own tests, see below)
│   └── sql/
│       └── schema.sql           # CREATE TABLE statements (portable to MySQL)
├── frontend/                     # plain HTML/CSS/JS, ES modules, no build step
│   ├── index.html, major.html, ge.html, search.html, schedule.html
│   ├── css/base.css              # design tokens (light/dark) and all components
│   └── js/
│       ├── config.js             # school name, term, catalog year, report link: the only school-specific file
│       ├── store.js              # plans, major, taken courses (the only code using localStorage)
│       ├── api.js, plan.js       # fetch helpers; the active plan as section objects
│       ├── nav.js                # the shared header and footer
│       ├── majorPrompt.js        # the "What's your major?" dialog
│       ├── calendar.js, dock.js  # week grid with ghost preview; docked calendar / phone sheet
│       ├── sections.js           # section rows and course cards
│       ├── time.js, stats.js     # day/time rules (same as conflicts.py); week stats
│       ├── ui.js, hero.js        # small DOM helpers; the home page animation
│       ├── track.js              # anonymous visit counting
│       └── pages/                # one module per page
├── data/
│   ├── majors/                   # majors.csv + major_requirements.csv (see "Majors data")
│   ├── ge/                       # GE areas and which course counts for which area
│   ├── placeholder/              # generate_placeholder_data.py + its output CSVs
│   ├── raw/                      # put real SDSU downloads here (untouched)
│   ├── import_real_data.py       # workbook -> data/cleaned (see "Adding real data")
│   ├── import_report.txt         # what the last import did (counts, warnings, skipped rows)
│   └── cleaned/                  # the class data the app loads, written by the importer
├── scripts/
│   └── coverage_report.py        # which required / GE courses have no sections this term
├── docs/                         # ER diagram, notes go here
├── tests/                        # python3 -m unittest discover -s tests -v
│   └── fixtures/                 # spring2027_sections.xlsx: the Sections sheet the import tests use
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

## GE data

- GE data lives in `data/ge/`. `ge_courses.csv` was built from the SDSU catalog's
  General Education page with `python3 data/ge/parse_ge_guide.py <saved page.txt>`.
- `python3 backend/models/db.py data/cleaned` loads your classes, the GE tables
  and the majors.
- A class only shows up under a GE area if its subject and course number are in
  `ge_courses.csv`, so there is nothing extra to fill in when adding classes.

## Majors data

Majors live in two CSV files in `data/majors/`. The loader reads them on every
full build, and the app adds them by itself to an older database that has
classes but no majors yet.

**`majors.csv`**, one row per major:

| Column | Meaning |
| --- | --- |
| `major_id` | Short id used in links: lowercase letters, digits and `_` (e.g. `cs_bs`, so `major.html?major=cs_bs`) |
| `name`, `degree` | What the student sees ("Computer Science", "B.S.") |
| `college` | Kept for reference only, never shown (some are unverified) |
| `catalog_year` | e.g. `2026-2027` |
| `status` | `live`, or `coming_soon` to list it in the prompt without letting anyone pick it |

**`major_requirements.csv`**, one row per course in a requirement group (or one
row for an `open` rule). Rows show up in file order.

| Column | Meaning |
| --- | --- |
| `major_id` | Which major the row belongs to |
| `section` | Heading, e.g. `Preparation for the Major`, `Major`, `Upper Division Major Electives` |
| `group_label` | Group name under the heading, e.g. `Required`, `Statistics (pick 1)` |
| `rule` | How the group is satisfied, see below |
| `pick_n` | `choose`: how many courses to pick. `open`: how many courses (optional) |
| `pick_units` | `pool` and `open`: units needed, can be a range like `14-15` |
| `subject`, `catalog_num` | The course, e.g. `CS` and `150L`. Spaces in subjects are removed (`POL S` becomes `POLS`). For `open` rules `subject` can list several codes separated by `\|`, like `ACCTG\|BA\|FIN` |
| `num_min`, `num_max` | `open` rules: the catalog number range, e.g. 300 to 599 |
| `title`, `units` | Shown on the course card (`units` can be `1-4`) |
| `note` | Shown under the group (or under the course, if the courses in a group have different notes) |

What each `rule` means:

- `required`: every course in the group is needed.
- `choose`: pick `pick_n` of the courses listed ("Pick 1 of 6").
- `pool`: electives where the whole heading needs `pick_units` units across all
  of its pool groups (Computer Science's 18 elective units from areas A to D).
- `open`: no list, a rule like "any PSY 300 to 599". The page asks
  `/api/courses?subject=PSY&min=300&max=599&has_sections=1` for the matching
  courses that have sections this term, and shows the group's note.

Courses are matched to class data by subject plus catalog number, so the same
course can appear in several majors, and a required course without sections in
our data still shows (greyed). A course counts toward its group when the
student marks it as taken or has one of its sections in the active plan.

**Adding a new major needs no code change:** add a row to `majors.csv`, add its
requirement rows to `major_requirements.csv`, and rebuild the database with
`python3 backend/models/db.py data/cleaned` (or delete `backend/sql/scheduler.db`
and start the app). Keep `status` as `coming_soon` until the rows are checked.

## Adding real data (the easy way)

1. Fill in the **Sections** sheet of the team's workbook
   (`data/template/EzClass_Data_Template_2_CLEANED.xlsx`), one row per section a
   student picks (columns A to N, data from row 3; row 2 is the gray example).
   No ids needed. Only the Sections sheet is read. Never remove a row because
   it looks like its neighbor: identical-looking rows are real sections.
2. Import it: `python3 data/import_real_data.py data/template/EzClass_Data_Template_2_CLEANED.xlsx`.
   It prints a report (also saved to `data/import_report.txt`): sections created,
   updated and unchanged, meetings, online-only and hybrid counts, anything it
   normalized, warnings with sheet row numbers, and skipped rows. A row whose
   parts don't line up is skipped and the rest still import; the script then
   exits with status 1. Fix those rows in the workbook and run it again.
3. Load it: `python3 backend/models/db.py data/cleaned`
4. Check what's missing: `python3 scripts/coverage_report.py` lists, for every
   live major and GE area, the courses with no sections this term.
5. Start the app as usual. To go back to placeholder data, run `python3 backend/models/db.py`.

The importer never "fixes" a day, time, room or name; it reports anything odd
so the team can fix the workbook.

**Several meetings, professors or seat numbers in one row.** Parts go in the
same cell with ` / ` between them:

- **Days, Start Time, End Time, Building, Room Number**: one part per meeting,
  in the same order as Days, or a single part that applies to every timed
  meeting. Parts can be empty. `MW / MW`, `13:00 / 12:00`, `13:50 / 12:50`,
  `LH / GMCS`, `256 / 333` is a lecture in LH 256 and a second meeting in
  GMCS 333. Days use `M T W Th F Sa Su` with no spaces (`MWF`, `TTh`, `MTWTh`).
- **ONLINE** in Days is a meeting with no day, time or room (Start and End
  empty, Building `ONLINE`). `ASYNC`, `ASYNCHRONOUS`, `ARRANGED` and `TBA` are
  read as ONLINE and listed in the report. `TTh / ONLINE` with times
  `09:30 / ` is a hybrid section. A section with no timed meeting is online only.
  A real day and time with Building `ONLINE` is a live online class: it is on
  the calendar and in the conflict check, with "Online" as the place.
- **No schedule yet**: Days, Start, End, Building and Room all empty. The
  section is imported with no meetings and shows "Time not listed yet" (never
  on the calendar, never a conflict). Type the days and times into the same row
  later, keeping its Section number, and the next import updates that section.
  Days empty while Start, End, Building or Room has a value is a mistake: that
  row is skipped and reported.
- **Professor First / Last Name**: one part per component (lecture, lab), not
  per meeting; both columns need the same number of parts. Each person is
  listed once per section (same name in any capitalization = same person).
  "TBA", "Staff" and "To be Announced" mean no professor.
- **Seats**: one number per component, like `180 / 45`. The site shows the
  smallest (a student needs a seat in every part) and keeps the text. Blank
  means "Seats unknown". A number over 999 (two numbers typed without the
  slash) is reported and not used.
- **Course Title**: one title per course. Special-topics courses (MUSIC 351,
  listed in `SPECIAL_TOPICS` in the importer) are the exception: each section
  keeps its own title ("Music and Culture: Hip Hop"), shown on its row, and
  the course is called by the part they share ("Music and Culture"). Any other
  course with two titles or two unit values is reported.

The tables: `sections` has one row per section, with `seats_text`,
`seats_total`, `active` and `section_title`; `section_meetings` one row per meeting
(`day_code`, `start_min`, `end_min` in minutes after midnight, `building`,
`room`, `is_online`); `section_instructors` links sections to professors. The
older one-meeting columns on `sections` (days, start_time, end_time,
professor_id, room_id, capacity) are still filled from the first timed meeting
and the first professor. A database built before meetings existed gets the new
tables on its next start, filled from those columns, without losing anything.

The importer also writes `data/cleaned/data_info.json` with today's date. The
site shows it in the footer and on My Schedule ("Class data last updated Nov 4,
2026"), so commit it with the CSVs. If you change the CSVs some other way, update
the date in that file by hand (format `YYYY-MM-DD`). `GET /api/info` returns it.

Section ids stay the same from one import to the next: a section that is still
in the sheet (same subject, course number, section and term) keeps the id it
had in the last `data/cleaned/sections.csv`, even if its row moved. This
matters because students' saved plans remember sections by id. Always import
on top of the current `data/cleaned/` files (don't delete them first).
Courses, professors and rooms keep their ids too.

- **New rows go at the bottom with Section left blank.** The importer gives
  them the next unused number for that course and lists it in the report;
  type that number into the sheet.
- **A section that is no longer in the sheet** is kept with `active = 0`: it
  disappears from the site (and from students' plans, with a short notice),
  but its id is never given to a different class, and it comes back if the row
  does. The report lists these under "No longer in the sheet".
- **Running the importer again on the same file changes nothing** (the report
  says `unchanged`, and the files and the "last updated" date stay the same).

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
mount path `/data`, and set `ANALYTICS_DB_PATH=/data/analytics.db`, or later move the counts to an
external database. **Set `FEEDBACK_DB_PATH=/data/feedback.db` too**: reviews and
support messages live in that file, and without the disk they are wiped on
every deploy. Put **only** these two files on the disk: leave
`EZCLASS_DB_PATH` unset. The app never overwrites a class database that already
has classes in it, so a class database on the disk would keep the first import
forever and ignore every later data update. Left alone, it's rebuilt from the
CSVs in the repo on each deploy. (A service with a disk can't do zero-downtime
deploys, so the site is down for a minute or so while each deploy goes out.) If
`/api/event` then returns 503 and the logs say "could not save analytics
event", the disk isn't writable by the image's non-root user (uid 1000).

### Before you share it with students

- Problem reports go to the Support page (`support.html`), linked from the
  footer, My Schedule, every course card and the calendar's class card (filled
  in with the course and section). `reportProblemUrl` in
  `frontend/js/config.js` can point them somewhere else instead.
- Set `ADMIN_TOKEN` and `FEEDBACK_DB_PATH` on the persistent disk (see above),
  then check new reviews and messages now and then (next section).
- Check `termName` and `catalogYear` in `config.js` match the data.
- Import the latest data so the "last updated" date is current.
- The site tells students to confirm every class in `registrationSite`
  (WebPortal) before registering; keep that.

### Reading the visit stats

```bash
curl -H "Authorization: Bearer $ADMIN_TOKEN" "https://<your-domain>/api/admin/stats?days=14"
```

`days` can be 1 to 90. You get totals, visitors today and in the last 7 days,
a per-day list, counts per event, page views per page, how often each major was
picked, the most picked GE areas, conflict check outcomes, and mobile vs desktop. Dates are UTC. Without
`ADMIN_TOKEN` set, the stats URL returns 404.

### Search engines and links

`/robots.txt` and `/sitemap.xml` are made by the app from the address it's
served at (set `SITE_URL` to pin it, e.g. once you have your own domain): the
sitemap lists the home page, My Major, GE, Search, My Schedule, Reviews and
Support, and robots.txt keeps crawlers out of `/api/`. Short links work too:
`/search`, `/major`, `/ge`, `/schedule`, `/reviews` and `/support` redirect to
the pages (keeping `?q=...`), and Search keeps its filters in the address, so
`/search?q=cs%20480` is a shareable link. Unknown addresses get a friendly
404 page; unknown `/api/` addresses get a JSON 404. Text and JSON answers are
gzipped for browsers that accept it (the full section list goes from 1.6 MB
to under 100 KB).

### Reviews and support messages

Students can leave a review (`reviews.html`: 1 to 5 stars, an optional comment
and name) or send a message (`support.html`: something broken, wrong class
info, a missing class, an idea, with an optional email for a reply). There
are no accounts; only what they type is kept, with a timestamp, in its own
SQLite file (`FEEDBACK_DB_PATH`). No IP address or user agent is stored.

Reviews start **pending** and only show on the site after you approve them.
Nothing is ever pre-filled: with no approved reviews the page says "No reviews
yet. Be the first."

```bash
# reviews waiting for a look (status: pending, approved, hidden) or new messages (new, done)
curl -H "Authorization: Bearer $ADMIN_TOKEN" "https://<your-domain>/api/admin/feedback?status=pending"
curl -H "Authorization: Bearer $ADMIN_TOKEN" "https://<your-domain>/api/admin/feedback?status=new"

# approve (or hide) review 12, mark message 7 done
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"status":"approved"}' https://<your-domain>/api/admin/reviews/12
curl -X POST -H "Authorization: Bearer $ADMIN_TOKEN" -H "Content-Type: application/json" \
  -d '{"status":"done"}' https://<your-domain>/api/admin/support/7
```

Like the stats, these return 404 when `ADMIN_TOKEN` isn't set and 401 with a
wrong token; the token only ever goes in the header. Spam protection: a hidden
field only bots fill in, a minimum time on the page, links refused in reviews,
and at most 3 sends per 10 minutes per browser (60 an hour overall).

### What is tracked (and what isn't)

`frontend/js/track.js` sends small anonymous events: page views (home, major,
GE, search, schedule), which major was picked (`major_select`), searches
(subject, day, result count, and only *whether* the professor or keyword box was
used), GE searches (area jumped to or filters changed, result count), plan adds,
removes and clears (`cart_add`, `cart_remove`, `cart_clear`, with the plan
size), new plans (`plan_create`), and conflict checks (conflict free or not).
Pages report these through an `ezclass:action` event; track.js never reads the
page itself, so typed text can't reach it.
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

- Student accounts / login / plans saved on a server (needs a hosted database
  first, see above). Plans live in the browser for now.
- Auto-build ("Build my schedule" from ticked courses), .ics export, print view,
  comparing plans side by side, share links and busy times (next round)
- More majors (Business Marketing and Mechanical Engineering are listed as coming soon)
- Sections for many required courses (data entry is still in progress)

## AI usage

See AI_USAGE.md for where AI helped and what the team added.

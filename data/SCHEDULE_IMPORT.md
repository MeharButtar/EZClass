# Loading the class schedule

EzClass's class data comes from SDSU's official schedule export (PeopleSoft "Sched of Classes", one .xlsx sheet). Two scripts turn it into the files the site loads:

1. `data/convert_sdsu_schedule.py` turns the export into the **Sections format** (below).
2. `data/import_real_data.py` turns a Sections file into `data/cleaned/`, keeping every id stable.

Never edit `data/cleaned/` by hand. Only the importer writes it.

## Refreshing the data (a new export)

1. Save the export in `data/source/`. The `.xlsx` is never committed; `.gitignore` keeps it out.
2. Convert it:

   PowerShell:
   ```powershell
   python data\convert_sdsu_schedule.py data\source\SD_CLASS_SCHEDULE_RPT_PUBLIC_204541634.xlsx
   ```
   bash:
   ```bash
   python3 data/convert_sdsu_schedule.py data/source/SD_CLASS_SCHEDULE_RPT_PUBLIC_204541634.xlsx
   ```
   This writes `data/source/<term>_sections.csv` (for example `spring2027_sections.csv`) and `data/schedule_convert_report.txt`.
3. Read the report. The numbers come first, then "Needs a look". Check that "Rows read" adds up and that nothing in "Needs a look" is a surprise.
4. Import it on top of the current data:

   PowerShell:
   ```powershell
   python data\import_real_data.py data\source\spring2027_sections.csv
   python backend\models\db.py data\cleaned
   ```
   bash:
   ```bash
   python3 data/import_real_data.py data/source/spring2027_sections.csv
   python3 backend/models/db.py data/cleaned
   ```
   Read `data/import_report.txt` too. Running the importer a second time must say "Files changed: no".
5. Run the tests: `python -m unittest discover -s tests` (PowerShell) or `python3 -m unittest discover -s tests` (bash).
6. Commit the CSV, both reports and `data/cleaned/`. Merging to `main` publishes it (about a minute of downtime).

`--retire-existing` is a one-time option. It was used once, for the first official import (Spring 2027), because the old hand-typed workbook's section numbers were wrong. It marks every section already in `data/cleaned/` as retired: the old rows and ids stay, but no new row can ever match them. **Don't use it for a normal refresh.** A normal refresh keeps ids by class number, so students' saved plans keep working.

## The Sections format (the contract)

One row is one section a student picks. A CSV has its header on row 1. The importer finds each column by the text before the first ` (`, so `Course Number (e.g. 150)` and `Course Number` both work.

| Column | Meaning | Example |
| --- | --- | --- |
| Term | The term | `Spring 2027` |
| Subject | Subject code, spaces are removed | `CS`, `POLS` |
| Course Number | Catalog number with any letter suffix | `150`, `150L`, `305W` |
| Course Title | The course title | `Introductory Computer Programming` |
| Units | Whole number | `3` |
| Section | Section number, text (leading zero kept) | `01` |
| Days | One part per meeting: `M T W Th F Sa Su` run together, or `ONLINE` for a part with no day or time | `TTh`, `MW / ONLINE` |
| Start Time | 24-hour `HH:MM`, one per meeting (empty for an online part) | `09:30`, `17:30 / ` |
| End Time | Same as Start | `10:45` |
| Professor First Name | One part per person | `Patricia`, `L.` |
| Professor Last Name | One part per person, lined up with the first names | `Kraft` |
| Building | One part per meeting. `ONLINE` with a day and time is a live online class | `GMCS`, `ONLINE` |
| Room Number | One part per meeting, text | `214`, `AUD` |
| Seats | One number (or one per component, ` / `); blank = unknown | `60` |
| Class Number (optional) | The official number students register with; unique per term | `5834` |

Rules:

- **` / ` separates parts.** Days, Start, End, Building and Room have one part per meeting, or one part that applies to every timed meeting. Professor first and last names have one part per person.
- **All of Days, Start, End, Building and Room empty** means the schedule isn't listed. The section imports with no meetings, and the site shows "Time not listed yet".
- **Class Number** keeps a section's id even when its section number changes in the next export. Without it, a section is matched by subject + course number + section + term.
- A row that doesn't fit is skipped with its row number in `data/import_report.txt`. The rest still import.

Another school's data only needs a small adapter that writes this format, as `convert_sdsu_schedule.py` does for PeopleSoft. The export's column names are in one dictionary, `SOURCE_COLUMNS`, at the top of the converter. If a new export only renames columns, change that dictionary and nothing else.

## What the converter decides, and what it leaves to people

The converter decides these. Each one is counted in the report, with examples:

- **Main campus only** (`SDSU`), status `A` only. Global Campus and Imperial Valley are counted and skipped.
- **Thesis and individual study sections are skipped:** a `SUP` or `NNT` component with no day and time, and a thesis, dissertation, special study, research, directed study, comprehensive exam or "investigation and report" title. A number ending in 97, 98 or 99 counts too, unless the title is an internship, practicum, clinical, fieldwork, teaching, community service, senior project or private lesson.
- **Days:** `R` is Thursday and `S` is Saturday. An unknown letter stops the run.
- **Times:** `06:00 PM` becomes `18:00`.
- **`ONLINE` with a day and time** is a live online class (building `ONLINE`). `ASYN`, or `ONLINE` with no time, is an online part. A hybrid keeps both its timed and online parts.
- **`ARR` (arranged):** in an in-person section it means no schedule ("Time not listed yet"). In an online or hybrid section it's an online part.
- **Rooms:** `GMCS428` is split into `GMCS` + `428`, trying the longest building code already in `rooms.csv` first. `OFFCSDSU` becomes `Off campus`. A code that doesn't split stays whole as the building.
- **People:** the export has a last name and one initial. When exactly one current EzClass professor matches, their full name is used. Otherwise it's the initial and the last name (`L. Smith`).
- **Titles:** the current EzClass title for a course we already have, the export's short title for a new one. A course with several titles in the export (special topics) keeps each section's own.
- **Seats:** `0` and `999` are placeholders and left blank.
- **Two class numbers with the same subject, number and section:** the lowest is kept.

The report lists these for a person to check, and never guesses at them:

- facility codes that don't split, and new buildings and rooms
- professors whose initial matches more than one person
- seat counts of 500 or more
- sections whose pattern has no times
- the kept sections with no day or time (lessons, internships, placements)
- courses that disappear completely, and whether a major or GE list needs them

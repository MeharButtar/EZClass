# EzClass: script that reads SDSU catalog pages and builds major requirements

Read this whole file first. Work on a new branch called `major-import`, started from the latest `main` (`git checkout main && git pull && git checkout -b major-import`). Do not merge to `main`. Push the branch and tell Mehar. If anything here conflicts with the repo, stop and say so.

## 1. Goal

EzClass has 5 live majors (CS, Psychology, General Business, Criminal Justice, Kinesiology Pre-PT) and 2 "coming soon" placeholders with no requirements (Business Marketing `ba_marketing_bs`, Mechanical Engineering `me_bs`). Mehar wants every undergraduate major from the 2026-2027 SDSU catalog, without copying pages by hand.

Build a script that reads each major's catalog page and writes requirement rows in the exact format the app already loads. The script only produces **staging files and a review report**. A human checks them before anything goes live.

## 2. What the pages look like (checked on the saved Mechanical Engineering page)

The catalog is the "Modern Campus Catalog" (Acalog) site, for example `https://catalog.sdsu.edu/preview_program.php?catoid=12&poid=12130`. `catoid=12` is the 2026-2027 catalog (the listing page in section 3b confirms it).

* The title is an `h1`, like "Mechanical Engineering, B.S." A line below it has "(Major Code: 09101) (Academic Plan Code: 447001BSS)".
* Each block is a `div.acalog-core`. `h2` is a section ("Preparation for the Major", "General Education", "Major"). `h3` is a sub-heading inside it ("Professional Electives", "Mechanical Systems", "Thermal Systems"). A `p` under a heading holds the rule in words, and may include a units total like "(48-49 units)".
* A course is `li.acalog-course`: a link with text `M E 190 - Computer-Aided Design` (non-breaking spaces around the dash), then `<strong>Units:</strong> <strong>2</strong>`, then optional trailing note text.
* Between courses, `li.acalog-adhoc` items hold `<p>or</p>`, `<p>also listed as</p>` or an empty `&nbsp;`.
* Catalog subjects have spaces (`M E`, `A E`, `GEN S`, `POL S`).

Pages differ between majors (emphases, options, "Recommended" lists, extra paragraphs). Do not assume every page looks like this one.

## 3. The format to write (do not change the schema)

Read the "Majors data" section of `README.md`. It is the source of truth, and `backend/models/db.py` (`load_majors`) loads it. Summary:

* `majors.csv`: `major_id, name, degree, college, catalog_year, status`.
* `major_requirements.csv`: `major_id, section, group_label, rule, pick_n, pick_units, subject, catalog_num, num_min, num_max, title, units, note`.
* Rules: `required` (all), `choose` (pick `pick_n`), `pool` (units needed across all pool groups under one heading), `open` (a subject list and number range, such as `PSY` 300 to 599).
* Subjects have spaces removed (`M E` becomes `ME`). Catalog numbers are uppercase (`150L`, `490W`).

Mapping rules:

1. **Name and degree** come from the `h1`: "Mechanical Engineering, B.S." gives name `Mechanical Engineering`, degree `B.S.`. For emphases the existing rows use "Business Administration, Emphasis in Marketing". Match that. Keep the existing ids `me_bs` and `ba_marketing_bs`. New ids follow the pattern `<short>_<degree>` in lowercase, such as `ce_bs`. `catalog_year` is `2026-2027`. Leave `college` blank. **`status` is always `coming_soon`** (README: keep it until the rows are checked).
2. **Sections:** `section` is the `h2` text for course-bearing blocks. An `h3` becomes `group_label`.
3. **Plain list of courses:** `rule=required`, `group_label=Required`.
4. **Courses separated by "or":** one `choose` group with `pick_n=1`, labeled like `BIOL 100 or BIOL 101 (pick 1)`.
5. **Courses separated by "also listed as"** (cross-listed, one real course): also a `choose` group with `pick_n=1`, labeled like `M E 200 / A E 200 (same course, pick 1)`, with the note "Cross-listed".
6. **Elective lists with a units rule:** `pool` with `pick_units`, one `group_label` per sub-heading. A rule like "any 400 or 500 level M E course" is an `open` row (subject plus `num_min` and `num_max`).
7. **Notes:** the standard text "must be completed with a grade of C (2.0) or better. These courses cannot be taken for credit/no credit (Cr/NC)" becomes exactly `Grade of C or better, no Cr/NC` (same as the existing rows). Any other trailing text is kept as the note.
8. **Titles and units:** the title is the link text after the dash. Units are kept as written, including ranges like `1-4`.
9. **Do not make rows for:** General Education, Graduation Writing Assessment, Master Plan, Impacted Program, Major Restriction, advising text. Put them in the report as "major notes" for a human (the app has no field for them yet, so do not add one). If a course appears in both the Graduation Writing block and the Major list (like M E 490W), keep one row in the Major list and add the note "Satisfies the Graduation Writing Assessment".
10. **Anything you cannot map with confidence** (rules in words, "students may substitute", multi-part unit rules): write the closest rows, copy the full catalog sentence into `note`, and put it on the review list. Never guess silently.

## 3b. Finding every major (the program listing page)

Mehar found the page that lists every program in the 2026-2027 catalog: `https://catalog.sdsu.edu/content.php?catoid=12&navoid=1153` ("Programs by Campus Location"). Each bullet links to that program's catalog page.

* **`--discover`** fetches that page (one request), reads every program link, and writes `scripts/catalog_urls.txt` (name, degree, URL). Save the raw page in `data/catalog_html/`.
* The page lists 653 programs, in groups ("Offered at SDSU San Diego and SDSU Imperial Valley", "Only offered at SDSU San Diego", and so on). No program repeats in the saved copy, but still dedupe by `poid`.
* **Keep only bachelor's degrees:** the name contains `B.A.`, `B.S.`, `B.M.` or `B.F.A.`. Careful: `M.B.A.` is a master's. The saved copy gives **188 programs across about 80 distinct major names**.
* **Skip:** minors, certificates, credentials, master's, doctoral, the three combined "4+1" degrees (BS/MS or BA/MS), and "Undeclared".
* Many majors are several pages, because each emphasis is its own page (Business Administration has 10, International Business has 16). Each one is its own `major_id`.
* The listing ends with a "Roadmap" section (184 links like "Aerospace Engineering, B.S. - Roadmap"). Those are degree roadmaps, not requirement pages. **Do not read them in this task.** They may be used later for course order.
* Process these 11 variants like any other program, but put each on the review list because of credential-prep or special rules: Biology B.S. (Single Subject credential prep), Chemistry B.A. (credential prep), Child Development (ITEP), Classics (Honors), English and Comparative Literature (credential prep), Mathematics B.A. (credential prep), Social Science (credential prep), Spanish (credential prep), Nursing B.S. Second Bachelor's Degree, Nursing Registered Nurse B.S., Nursing Registered Nurse B.S. Second Bachelor's Degree.
* **`major_id`s are used in links** (`major.html?major=...`), so they must never change once published. Generate them once into `scripts/catalog_major_ids.csv` (lowercase letters, digits and `_`, all unique), keep the 7 existing ids, reuse the file on every rerun, and report collisions. Never regenerate them silently.
* Discovery must find the 7 programs the app already knows: Computer Science, Psychology, Business General Business, Criminal Justice, Kinesiology Prephysical Therapy, Mechanical Engineering, and Business Marketing.
* Mehar will save the listing page as `tests/fixtures/catalog/programs_listing.html`. Test discovery on it offline: 188 bachelor's programs, none of the skipped types, and the 7 known programs present.

## 4. Script and commands

Create `scripts/import_catalog_majors.py`. Use only the standard library (`html.parser`) or add BeautifulSoup to `requirements-dev.txt` only. The production image must not change.

```
python3 scripts/import_catalog_majors.py --urls scripts/catalog_urls.txt --out data/majors/staging
python3 scripts/import_catalog_majors.py --html-dir data/catalog_html --out data/majors/staging
python3 scripts/import_catalog_majors.py --promote me_bs
```

* `--urls`: a text file with one catalog program URL per line (Mehar fills it in). `--discover` (section 3b) builds this file from the catalog's program listing page. A hand-made list works too.
* `--html-dir`: works fully offline on pages saved by hand. This is also the fallback if automated access is not allowed.
* `--promote <major_id>`: copies one reviewed staged major into the live `data/majors/majors.csv` and `major_requirements.csv`, with status `coming_soon`. It must refuse if that `major_id` already exists in the live files, so the 5 live majors can never be overwritten.
* Staging output: `data/majors/staging/majors.csv`, `data/majors/staging/major_requirements.csv` and `data/majors/staging/REPORT.md`.

## 5. Being polite to the website

* Public pages only. No logins.
* Read the site's `robots.txt` and terms first. If automated access is not allowed, do not crawl. Tell Mehar and use `--html-dir`.
* At most 1 request per second. Save every downloaded page to `data/catalog_html/` and reuse it on reruns.
* Use a generic user agent such as `EzClass-catalog-reader`. Never put Mehar's name or email in it.
* Stop and report on 403 or 429 errors. Do not retry in a loop.

## 6. The report (`REPORT.md`)

For each major: id, name, degree, number of rows, the "major notes" text, and a **review list** of every group the script was not sure about. Also check and print:

1. **Units check:** compare the "(48-49 units)" style totals on the page with the units of the listed courses (taking the lower and upper value for "or" groups). Report mismatches. This is advisory and can be wrong for elective rules.
2. **Coverage:** list courses that have no sections in `data/cleaned`. Reuse the logic in `scripts/coverage_report.py` (it reads the CSVs directly).
3. **Title differences** between the catalog and the class data.
4. A summary table at the top: majors processed, rows, majors with open review items.

## 7. Test fixture: Mechanical Engineering

Mehar will copy the saved page into `tests/fixtures/catalog/me_bs.html` (the file is named `Program__Mechanical_Engineering__B.S._-_San_Diego_State_University.html`). Write `tests/test_catalog_import.py` using it, with no network. From my reading of the page, the result should be about this. Compute it yourself from the HTML and tell Mehar if you disagree.

* Header: name `Mechanical Engineering`, degree `B.S.`, id `me_bs`, `2026-2027`, `coming_soon`.
* **Preparation for the Major** (page says 48-49 units): 13 required rows (M E 190, 202, 230, 240, 241; A E 280; MATH 150, 151, 252; PHYS 195, 195L, 196, 196L). Four pick-1 groups: M E 200 / A E 200, M E 220 / A E 220, BIOL 100 or 101, CHEM 202 or 200. The units check should land inside 48-49.
* **Major:** 12 required rows (M E 304, 314, 330, 340, 350, 360, 430, 452, 490W, 491, 495; A E 341). M E 490W carries the Graduation Writing note.
* **Professional Electives:** Mechanical Systems and Thermal Systems lists as pool rows. The page says 6 units from one area (at least 3 at the 500 level) plus 6 units from any 400 or 500 level M E course. Encode it as best you can and **put it on the review list**. M E 544 and 570 appear in both areas.
* Major notes in the report: impacted program (M E 200 or A E 200, CHEM 202 or 200, MATH 150, 151, PHYS 195, 196 with a C or better, 2.7 GPA), restriction on 300-400+ courses until cleared, GE Areas 2/5 and 4 covered by the major, master plan.
* Also test: an "or" group, an "also listed as" pair, and that `--promote` refuses an id that already exists.

## 8. Order of work

1. Parser and the Mechanical Engineering test. Show Mehar the report.
2. The first batch, Mehar's priority list: the other Business emphases (Marketing, Accounting, Finance, Entrepreneurship, Financial Services, Human Resource Management, Information Systems, Management, Real Estate), Computer Engineering, Electrical Engineering, Civil Engineering.
3. All 188 bachelor's programs that discovery finds, once the first batches look right, in groups of about 20 so the review stays manageable. Skip master's, doctoral, credentials, certificates, minors, 4+1 degrees and "Undeclared".

## 9. Do not

* Do not change the schema, `data/cleaned`, the class importer or the 5 live majors.
* Do not set any status to `live`.
* Do not put secrets, tokens or Mehar's email in code, logs, the report or the user agent.
* Do not merge to `main`.

When done, run `python3 -m unittest discover -s tests -v` (all existing tests must still pass), push the branch, and send Mehar a short summary: what the script does, the Mechanical Engineering report, what you could not read, and the exact commands to run it.

## 10. Decisions after the Mechanical Engineering review (2026-11-09)

These override sections 3 and 7 where they differ. The script's docstring repeats them.

1. **Electives rule in words** (M E Professional Electives: "6 units from one area, at least 3 at the 500 level, and 6 more from the 400- or 500-level M E courses listed below"): one pool for the whole total (12 units for M E), with the full catalog sentence in `note`, on the review list. No `open` row, because the catalog limits the second 6 units to the listed courses. When the rule gives no single total, `pick_units` is the h2 total minus the h2's other rows (M E: 45 - 33 = 12).
2. **An electives pool is always its own section**, for every major, never part of the h2 above it. The app shows a pool's unit counter on its section heading, so a pool inside "Major" would put "x of 12 units" on the whole Major block. Two cases: an h3 with a rule in words and no courses becomes the section, and the h3 lists after it are its pool groups ("Professional Electives" with "Mechanical Systems" and "Thermal Systems"); an h3 list asking for fewer units than it lists becomes its own section.
3. **A course in more than one pool group of one section** (M E 544 and 570): one row, under the first group, with the note "Also listed under <other group>", on the review list. The app's pool counter is not changed for now.
4. **`--promote` and the placeholders:** an id that exists live is refused, except an empty `coming_soon` placeholder (a majors row with no requirement rows, like `me_bs` and `ba_marketing_bs`). That row is filled in place with the staged name and degree, `college` is kept, and `status` stays `coming_soon`. The 5 live majors can never be overwritten.
5. **Crawl speed:** catalog.sdsu.edu's robots.txt (checked 2026-11-09) allows `content.php` and `preview_program.php` but sets `crawl-delay: 120` for every user agent. The script follows the crawl-delay, which is stricter than section 5's 1 request per second: one page every 2 minutes, about 6 hours for all 188 programs. The catalog has no terms-of-use page; it links only to the SDSU Digital Privacy Statement, which says nothing about automated access.

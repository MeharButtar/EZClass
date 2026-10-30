# AI Usage Disclosure (CS 514 Final Project, Phase 1)

This follows the course AI policy: say where AI was used, how the team modified
or extended it, and be ready to explain and defend every part.

## Summary

We used Claude (Anthropic) on this project. Mehar Buttar directed that work.
Claude wrote first drafts of the code, the technical document, and the
presentation, working from Mehar's requirements and feedback. Mehar used those
drafts as a first base, changed and extended the code as needed, tested it, wrote
the final presentation and scripts, and has reviewed all of the code and can
explain how it works. The class data was
gathered and cleaned by the team, not by AI.

## Where AI (Claude) was used

| Part | What Claude did | What Mehar did |
| --- | --- | --- |
| backend/sql/schema.sql | Drafted the eight-table schema, including the GE tables | Gave the requirements, chose the design, reviewed and adjusted it |
| backend/models/conflicts.py | Drafted the day-pattern parsing and time-overlap logic | Reviewed, tested, and adjusted it |
| backend/models/db.py | Drafted the SQLite connection and CSV loader | Reviewed and adjusted it |
| backend/routes/*.py, backend/app.py | Drafted the Flask search, GE, and conflict-check routes | Reviewed, tested, and adjusted them |
| data/import_real_data.py | Drafted the Excel-to-CSV importer | Reviewed and used it to load the real data |
| data/ge/parse_ge_guide.py | Drafted the GE list parser | Reviewed it and checked the output against the catalog |
| frontend/ (HTML, CSS, JS) | Drafted the pages, the GE area picker, the cart, and the combined filters | Directed the layout and behavior (GE area groups, filters that apply together) and tested it in the browser |
| Deployment and visit tracking (Dockerfile, app settings, backend/routes/analytics.py, frontend/js/track.js, tests/test_smoke.py) | Drafted the Docker setup, production settings and security headers, the anonymous visit counting on both ends, and the smoke tests | Set the requirements and privacy rules, directs the work, and reviews and tests it |
| Debugging | Helped find and fix bugs (for example, the 1B button showing every GE class) | Reported the problems and checked the fixes |
| data/placeholder/generate_placeholder_data.py | Wrote the placeholder data generator | Used it for early testing |
| README.md, this file, the technical document, the slides, the presentation script | Drafted them | Revised them and made the final versions |

Claude also helped plan the project scope, the stack, and the team task split.

## What the team changed or added

| Name | What they did |
| --- | --- |
| Mehar Buttar | Led the project. Code, technical document, and the final presentation and scripts, built from Claude's first drafts and revised by Mehar. Reviewed and tested the code |
| Matthew Chung | Gathered and cleaned the class data |
| Malaika Malik | Finished the team site that Mehar started (with Michelle) |
| Michelle Khaliqi | Finished the team site that Mehar started (with Malaika) |
| Sharifullah Sharifi | Drafted early presentation scripts (Mehar wrote the final versions) |
| Noor Hamdard | Drafted early presentation scripts (Mehar wrote the final versions) |

## What we verified ourselves

- Ran the app locally and used the Search page, the GE Scheduler, and the cart in the browser.
- Loaded the real data: 559 sections from 145 courses.
- Checked the GE filters against counts we could confirm: 425 GE sections total, 78 in area 1B, and 65 in 1B on Wednesdays.
- Checked that the area filter and the day filter apply together.
- Checked the conflict check on overlapping classes, back-to-back classes (not a conflict), and the same time on different days (not a conflict).

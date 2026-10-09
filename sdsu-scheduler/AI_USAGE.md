# AI Usage Disclosure (CS 514 Final Project, Phase 1 Draft)

This follows the course AI policy: say where AI was used, how the team modified
or extended it, and be ready to explain and defend every part.

## Where AI (Claude) was used

| Part | AI role |
| --- | --- |
| backend/sql/schema.sql | Drafted the six-table schema from Mehar's requirements |
| data/placeholder/generate_placeholder_data.py | Wrote the placeholder data generator |
| backend/models/db.py | Wrote the SQLite connection and CSV loader |
| backend/models/conflicts.py | Wrote day-pattern parsing and time-overlap logic |
| backend/routes/*.py, backend/app.py | Wrote the Flask search and conflict-check routes |
| frontend/ (HTML, CSS, JS) | Wrote the search page, schedule list, and professor links |
| README.md, this file, the slides, the technical PDF | Drafted for the team to edit |

AI also helped plan the project scope, stack, and team task split.

## What the team changed or added

Fill this in with work you actually did, one line each, with your name and the
file. Examples of what counts: new SQL queries, real data you entered, new
filters, CSS changes, tests you wrote, indexes you added with before/after timings.

| Name | File(s) | What I did |
| --- | --- | --- |
| Mehar Buttar | [fill in] | [fill in] |
| [Name] | [fill in] | [fill in] |
| [Name] | [fill in] | [fill in] |
| [Name] | [fill in] | [fill in] |
| [Name] | [fill in] | [fill in] |
| [Name] | [fill in] | [fill in] |

## What we verified ourselves

[List what you ran and checked, for example: ran the app locally, selected the
four overlapping placeholder sections and confirmed two conflicts are reported.]

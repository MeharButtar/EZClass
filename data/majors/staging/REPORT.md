# Catalog import report (2026-2027)

Staging only: nothing here is live. Every major is `coming_soon`. Check each one against its catalog page, then promote it with `python3 scripts/import_catalog_majors.py --promote <major_id>`.

| Majors processed | Requirement rows | Majors with open review items |
| --- | --- | --- |
| 1 | 51 | 1 |

| major_id | Name | Degree | Rows | Review items |
| --- | --- | --- | --- | --- |
| `me_bs` | Mechanical Engineering | B.S. | 51 | 5 |

## Mechanical Engineering, B.S. (`me_bs`)

- Source: `tests/fixtures/catalog/me_bs.html`, poid 12130, major code 09101
- Rows: 51

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 13: M E 190, M E 202, M E 230, M E 240, M E 241, A E 280, MATH 150, MATH 151, MATH 252, PHYS 195, PHYS 195L, PHYS 196, PHYS 196L |
| Preparation for the Major | M E 200 / A E 200 (same course, pick 1) | choose 1 | 2: M E 200, A E 200 |
| Preparation for the Major | M E 220 / A E 220 (same course, pick 1) | choose 1 | 2: M E 220, A E 220 |
| Preparation for the Major | BIOL 100 or BIOL 101 (pick 1) | choose 1 | 2: BIOL 100, BIOL 101 |
| Preparation for the Major | CHEM 202 or CHEM 200 (pick 1) | choose 1 | 2: CHEM 202, CHEM 200 |
| Major | Required | required | 12: M E 304, M E 314, M E 330, M E 340, M E 350, M E 360, M E 430, M E 452, M E 490W, M E 491, M E 495, A E 341 |
| Professional Electives | Mechanical Systems | pool, 12 units | 13: M E 520, M E 530, M E 532, A E 535, M E 535, M E 540, M E 542, M E 543, M E 544, M E 570, M E 580, M E 582, M E 585 |
| Professional Electives | Thermal Systems | pool, 12 units | 5: M E 450, M E 552, M E 554, M E 555, M E 556 |

### Review list

- [ ] 'Professional Electives' (under Major) is a rule in words, encoded as one pool; check it. Catalog: "6 units of coursework to be selected from one of either mechanical systems or thermal systems areas, with at least 3 units at the 500-level; and 6 units of additional coursework selected from any of the 400- or 500-level mechanical engineering courses listed below. Students may select professional electives from other departments, with departmental approval."
- [ ] A E 535 / M E 535 (same course, pick 1) in the 'Mechanical Systems' pool: kept as pool rows with a note (a pick-1 group inside a units pool would be counted on its own).
- [ ] 'Professional Electives': pool set to 12 units, worked out from the Major total minus its other courses.
- [ ] M E 544 is listed under both 'Mechanical Systems' and 'Thermal Systems' in 'Professional Electives': kept once, under 'Mechanical Systems', with an "Also listed under" note.
- [ ] M E 570 is listed under both 'Mechanical Systems' and 'Thermal Systems' in 'Professional Electives': kept once, under 'Mechanical Systems', with an "Also listed under" note.

### Units check (advisory)

- Preparation for the Major: page says 48-49 units, listed courses give 48-49: **inside**
- Major: page says at least 45 units, listed courses give 45: **inside (elective units were worked out from this total)**

### Major notes (no rows made; for a human)

- **Program description**
  - All students in Mechanical Engineering pursue a common program of basic sciences, engineering, and mechanical engineering fundamentals. Students are provided with the opportunity to select a pattern of study to satisfy their areas of interest. This pattern of study is indicated in the sequence known as “professional electives” and may be selected from available courses in controls, energy conversion, fluid mechanics, heat transfer, machine design, materials, mechanics, thermodynamics, vibrations, and other areas.
  - Students must complete all upper division courses in the major within seven years prior to graduation. Students who will have completed any of those courses more than seven years before the projected date of graduation must contact the department chair for information about ways to certify knowledge of current course content.
  - All candidates for a bachelor’s degree must complete the graduation requirements outlined in the “Graduation Requirements” section of this catalog.
- **Impacted Program**
  - The Mechanical Engineering major is an impacted program. To be admitted to the major, students must meet the following impaction criteria:
  - a. Complete with a grade of C (2.0) or better: M E 200 [or A E 200]; CHEM 202 (or CHEM 200); MATH 150, MATH 151; PHYS 195, PHYS 196. These courses cannot be taken for credit/no credit (Cr/NC);
  - b. Have an overall cumulative GPA of 2.7.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Major Restriction for Registration**
  - You must be in the Major (cleared impaction requirements) in order to take the upper level (300-400+) courses. M E 350 is also open to Environmental Engineering students who are in major status (cleared impaction requirements).
- **General Education**
  - Engineering majors automatically satisfy Area 2/5. Mathematical Concepts and Quantitative Reasoning or Physical and Biological Sciences and Area 4. Social and Behavioral Explorations GE areas by completion of the major.
- **Graduation Writing Assessment Requirement**
  - Complete M E 490W with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements. Courses listed: M E 490W.
- **Master Plan**
  - The master plan provides an advising record and a roadmap toward graduation for mechanical engineering majors. The master plan must be filed electronically with the department advisors (https://mechanical.sdsu.edu/undergraduate/advising). All students transferring from another institution are required to file the master plan at the time of transfer. Current SDSU students are required to file the master plan as part of their course requirements in M E 190 . Students are encouraged to seek the guidance of their advisors when completing the master plan. If there is any change to the course sequence listed in the master plan that is already on file, it must be updated and refiled. All students must have an updated master plan on file in the department prior to enrollment in M E 350 and M E 490W . All course substitutions must be approved by the department chair prior to enrolling in the course.

### Coverage (sections in data/cleaned)

- Required courses: 25 of 25 have sections
  - with sections: M E 190 (12), M E 202 (4), M E 230 (8), M E 240 (2), M E 241 (6), A E 280 (3), MATH 150 (12), MATH 151 (20), MATH 252 (13), PHYS 195 (2), PHYS 195L (17), PHYS 196 (1), PHYS 196L (10), M E 304 (3), M E 314 (2), M E 330 (8), M E 340 (6), M E 350 (3), M E 360 (2), M E 430 (2), M E 452 (3), M E 490W (4), M E 491 (8), M E 495 (4), A E 341 (9)
- Pick-n group courses: 8 of 8 have sections
  - with sections: M E 200 (3), A E 200 (3), M E 220 (5), A E 220 (1), BIOL 100 (4), BIOL 101 (1), CHEM 202 (11), CHEM 200 (49)
- Elective pool courses: 7 of 18 have sections
  - with sections: A E 535 (1), M E 544 (1), M E 570 (2), M E 582 (1), M E 450 (1), M E 555 (1), M E 556 (1)
  - no sections: M E 520, M E 530, M E 532, M E 535, M E 540, M E 542, M E 543, M E 580, M E 585, M E 552, M E 554

### Title differences (catalog vs class data)

- M E 491: catalog "Engineering Design: Senior Project", class data "Senior Projects II"
- A E 535: catalog "Mechanics of Composite Structures", class data "Mech of Composites Struct"
- M E 555: catalog "Thermal Systems Analysis and Design", class data "Enrgy& Thrm Sys Anal/Dsgn"
- 14 more only shortened in the class data (not a real difference): M E 202, M E 240, CHEM 202, M E 314, M E 340, M E 452, M E 490W, M E 495, A E 341, M E 544, M E 570, M E 582, M E 450, M E 556

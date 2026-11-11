# Catalog import report (2026-2027)

Staging only: nothing here is live. Every major is `coming_soon`. Check each one against its catalog page, then promote it with `python3 scripts/import_catalog_majors.py --promote <major_id>`.

| Majors processed | Requirement rows | Majors with open review items |
| --- | --- | --- |
| 13 | 505 | 13 |

## Batch check: 12 of 12 pages found

| # | Program | major_id | Page |
| --- | --- | --- | --- |
| 1 | Business Administration, Emphasis in Marketing, B.S. | `ba_marketing_bs` | found |
| 2 | Business Administration, Emphasis in Accounting, B.S. | `ba_accounting_bs` | found |
| 3 | Business Administration, Emphasis in Finance, B.S. | `ba_finance_bs` | found |
| 4 | Business Administration, Management, Specialization in Entrepreneurship, B.S. | `ba_management_entrepreneurship_bs` | found |
| 5 | Business Administration, Emphasis in Financial Services, B.S. | `ba_financial_services_bs` | found |
| 6 | Business Administration, Management, Specialization in Human Resource Management, B.S. | `ba_management_human_resource_management_bs` | found |
| 7 | Business Administration, Emphasis in Information Systems, B.S. | `ba_information_systems_bs` | found |
| 8 | Business Administration, Emphasis in Management, B.S. | `ba_management_bs` | found |
| 9 | Business Administration, Emphasis in Real Estate, B.S. | `ba_real_estate_bs` | found |
| 10 | Computer Engineering, B.S. | `computer_engineering_bs` | found |
| 11 | Electrical Engineering, B.S. | `electrical_engineering_bs` | found |
| 12 | Civil Engineering, B.S. | `civil_engineering_bs` | found |

## Run notes

- data/catalog_html/Program_ Business Administration, Emphasis in Management, B.S. - San Diego State University.html: no program id in the page; matched by its title to poid 12112

| major_id | Name | Degree | Rows | Review items |
| --- | --- | --- | --- | --- |
| `me_bs` | Mechanical Engineering | B.S. | 52 | 5 |
| `ba_accounting_bs` | Business Administration, Emphasis in Accounting | B.S. | 25 | 2 |
| `ba_finance_bs` | Business Administration, Emphasis in Finance | B.S. | 23 | 2 |
| `ba_financial_services_bs` | Business Administration, Emphasis in Financial Services | B.S. | 40 | 3 |
| `ba_information_systems_bs` | Business Administration, Emphasis in Information Systems | B.S. | 34 | 1 |
| `ba_management_bs` | Business Administration, Emphasis in Management | B.S. | 42 | 1 |
| `ba_marketing_bs` | Business Administration, Emphasis in Marketing | B.S. | 49 | 4 |
| `ba_real_estate_bs` | Business Administration, Emphasis in Real Estate | B.S. | 23 | 1 |
| `ba_management_entrepreneurship_bs` | Business Administration, Management, Specialization in Entrepreneurship | B.S. | 32 | 1 |
| `ba_management_human_resource_management_bs` | Business Administration, Management, Specialization in Human Resource Management | B.S. | 30 | 1 |
| `civil_engineering_bs` | Civil Engineering | B.S. | 55 | 2 |
| `computer_engineering_bs` | Computer Engineering | B.S. | 45 | 2 |
| `electrical_engineering_bs` | Electrical Engineering | B.S. | 55 | 3 |

## Mechanical Engineering, B.S. (`me_bs`)

- Source: `tests/fixtures/catalog/me_bs.html`, poid 12130, major code 09101
- Rows: 52

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 13: M E 190, M E 202, M E 230, M E 240, M E 241, A E 280, MATH 150, MATH 151, MATH 252, PHYS 195, PHYS 195L, PHYS 196, PHYS 196L |
| Preparation for the Major | ME 200 / AE 200 (same course, pick 1) | choose 1 | 2: M E 200, A E 200 |
| Preparation for the Major | ME 220 / AE 220 (same course, pick 1) | choose 1 | 2: M E 220, A E 220 |
| Preparation for the Major | BIOL 100 or BIOL 101 (pick 1) | choose 1 | 2: BIOL 100, BIOL 101 |
| Preparation for the Major | CHEM 202 or CHEM 200 (pick 1) | choose 1 | 2: CHEM 202, CHEM 200 |
| Major | Required | required | 12: M E 304, M E 314, M E 330, M E 340, M E 350, M E 360, M E 430, M E 452, M E 490W, M E 491, M E 495, A E 341 |
| Professional Electives | Mechanical Systems | pool, 12 units | 13: M E 520, M E 530, M E 532, A E 535, M E 535, M E 540, M E 542, M E 543, M E 544, M E 570, M E 580, M E 582, M E 585 |
| Professional Electives | Thermal Systems | pool, 12 units | 5: M E 450, M E 552, M E 554, M E 555, M E 556 |

### Section notes (shown once under the heading)

- **Professional Electives**: 6 units of coursework to be selected from one of either mechanical systems or thermal systems areas, with at least 3 units at the 500-level; and 6 units of additional coursework selected from any of the 400- or 500-level mechanical engineering courses listed below. Students may select professional electives from other departments, with departmental approval

### Review list

- [ ] 'Professional Electives' (under Major) is a rule in words, encoded as one pool; check it. Catalog: "6 units of coursework to be selected from one of either mechanical systems or thermal systems areas, with at least 3 units at the 500-level; and 6 units of additional coursework selected from any of the 400- or 500-level mechanical engineering courses listed below. Students may select professional electives from other departments, with departmental approval."
- [ ] AE 535 / ME 535 (same course, pick 1) in the 'Mechanical Systems' pool: kept as pool rows with a note (a pick-1 group inside a units pool would be counted on its own).
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

## Business Administration, Emphasis in Accounting, B.S. (`ba_accounting_bs`)

- Source: `data/catalog_html/Program_ Business Administration, Emphasis in Accounting, B.S. - San Diego State University.html`, poid 11880, major code 05021
- Rows: 25

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 7: ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MIS 180, MATH 120 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 15: ACCTG 331, ACCTG 332, ACCTG 333, ACCTG 334, ACCTG 390W, ACCTG 431, ACCTG 530, ACCTG 532, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370, MIS 301 |
| Upper Division Accountancy Electives | Any ACCTG 300-599 course | open, 6 units | 1: Any ACCTG 300-599 course |

### Section notes (shown once under the heading)

- none

### Review list

- [ ] 'Any ACCTG 300-599 course' in Upper Division Accountancy Electives: "6 units of upper division Accounting (ACCTG) courses, excluding ACCTG 325 and ACCTG 326" encoded as an open rule (ACCTG 300-599, 6 units); check it.
- [ ] 'Any ACCTG 300-599 course': ACCTG 325, ACCTG 326 left out of its list (exclude column), from "excluding ACCTG 325 and ACCTG 326".

### Units check (advisory)

- Preparation for the Major: page says 24 units, listed courses give 24: **inside**
- Major: page says 47 units, listed courses give 47: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a bachelor’s degree must complete the graduation requirements listed in the section of this catalog on “Graduation Requirements.”
  - Students in the Fowler College of Business may declare only one emphasis under the Business Administration major and may not double major in International Business.
  - A minor is not required for the Business Administration major with an emphasis in Accounting. Students may declare only one minor within the Fowler College of Business.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Preparation for the Major**
  - Additional progress requirements must be met before a student is admitted to an upper division major.
- **Graduation Writing Assessment Requirement**
  - Complete ACCTG 390W and earn a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements. Courses listed: ACCTG 390W.
- **Major**
  - A “C” (2.0) average or better is required in the courses stipulated here for the major.

### Coverage (sections in data/cleaned)

- Required courses: 22 of 22 have sections
  - with sections: ACCTG 201 (11), ACCTG 202 (12), ECON 101 (6), ECON 102 (6), FIN 240 (9), MIS 180 (20), MATH 120 (5), ACCTG 331 (3), ACCTG 332 (4), ACCTG 333 (5), ACCTG 334 (6), ACCTG 390W (5), ACCTG 431 (5), ACCTG 530 (4), ACCTG 532 (4), B A 305 (8), B A 310 (14), B A 323 (13), B A 350 (14), B A 360 (11), B A 370 (16), MIS 301 (7)
- Pick-n group courses: 2 of 2 have sections
  - with sections: STAT 119 (5), ECON 201 (4)
- Open rule 'Any ACCTG 300-599 course' (without excluded and already-required courses): 5 courses with sections: ACCTG 409, ACCTG 503, ACCTG 505, ACCTG 508, ACCTG 596

### Title differences (catalog vs class data)

- none
- 4 more only shortened in the class data (not a real difference): ACCTG 332, ACCTG 333, ACCTG 334, ACCTG 390W

## Business Administration, Emphasis in Finance, B.S. (`ba_finance_bs`)

- Source: `data/catalog_html/Program_ Business Administration, Emphasis in Finance, B.S. - San Diego State University.html`, poid 12008, major code 05041
- Rows: 23

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: FIN 240, ACCTG 201, ACCTG 202, ECON 101, ECON 102, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 12: FIN 321, FIN 325, FIN 327, FIN 423, ACCTG 326, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370 |
| Major | Any FIN 300-599 course | open, 9 units | 1: Any FIN 300-599 course |

### Section notes (shown once under the heading)

- none

### Review list

- [ ] 'Any FIN 300-599 course' in Major: "Nine units of 300- to 500-level finance courses." encoded as an open rule (FIN 300-599, 9 units); check it.
- [ ] 'Any FIN 300-599 course': the page names no subject code; FIN was read from the department name. Check it.

### Units check (advisory)

- Preparation for the Major: page says 27 units, listed courses give 27: **inside**
- Major: page says 41 units, listed courses give 41: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a bachelor’s degree must complete the graduation requirements listed in the section of this catalog on “Graduation Requirements.”
  - Students in the Fowler College of Business may declare only one emphasis under the Business Administration major and may not double major in International Business.
  - A minor is not required for the Business Administration major with an emphasis in Finance. Students may declare only one minor within the Fowler College of Business.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Preparation for the Major**
  - Additional progress requirements must be met before a student is admitted to an upper division major.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - A C (2.0) average or better is required in the courses stipulated here for the major.
  - A “C” (2.0) average or better is required in the courses stipulated here for the major.

### Coverage (sections in data/cleaned)

- Required courses: 20 of 20 have sections
  - with sections: FIN 240 (9), ACCTG 201 (11), ACCTG 202 (12), ECON 101 (6), ECON 102 (6), MIS 180 (20), MATH 120 (5), RWS 290 (31), FIN 321 (6), FIN 325 (5), FIN 327 (6), FIN 423 (7), ACCTG 326 (10), B A 300 (18), B A 305 (8), B A 310 (14), B A 323 (13), B A 350 (14), B A 360 (11), B A 370 (16)
- Pick-n group courses: 2 of 2 have sections
  - with sections: STAT 119 (5), ECON 201 (4)
- Open rule 'Any FIN 300-599 course' (without excluded and already-required courses): 18 courses with sections: FIN 326, FIN 328, FIN 329, FIN 331, FIN 334, FIN 335, FIN 336, FIN 421, FIN 422, FIN 427, FIN 431, FIN 433, FIN 435, FIN 437, FIN 522, FIN 585, FIN 589, FIN 590

### Title differences (catalog vs class data)

- none

## Business Administration, Emphasis in Financial Services, B.S. (`ba_financial_services_bs`)

- Source: `data/catalog_html/Program_ Business Administration, Emphasis in Financial Services, B.S. - San Diego State University.html`, poid 12009, major code 05043
- Rows: 40

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: FIN 240, ACCTG 201, ACCTG 202, ECON 101, ECON 102, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 10: FIN 327, FIN 331, FIN 589, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370 |
| Major | FIN 334 or FIN 522 (pick 1) | choose 1 | 2: FIN 334, FIN 522 |
| Major | FIN 433 or ACCTG 503 (pick 1) | choose 1 | 2: FIN 433, ACCTG 503 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 9-10 units | 16: FIN 326, FIN 335, FIN 336, FIN 421, FIN 422, FIN 427, FIN 431, FIN 435, FIN 436, FIN 585, FIN 590, ACCTG 326, ECON 320, ECON 422, ECON 490, MKTG 377 |

### Section notes (shown once under the heading)

- none

### Review list

- [ ] Text under 'Major' kept as a major note, not on its courses: "Students intending to pursue the Personal Financial Planning Certificate should refer to the certificate requirements when choosing their elective courses."
- [ ] ECON 320 or ECON 422 (pick 1) in the 'Upper Division Major Electives' pool: kept as pool rows with a note (a pick-1 group inside a units pool would be counted on its own).
- [ ] 'Upper Division Major Electives' (under Major) asks for 9-10 units of its list: encoded as a pool in its own section 'Upper Division Major Electives', check it.

### Units check (advisory)

- Preparation for the Major: page says 27 units, listed courses give 27: **inside**
- Major: page says 39-40 units, listed courses give 39-40: **inside**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - Students in the Fowler College of Business may declare only one emphasis under the Business Administration major and may not double major in International Business.
  - A minor is not required for the Business Administration major with an emphasis in Financial Services. Students may declare only one minor within the Fowler College of Business.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Preparation for the Major**
  - Additional progress requirements must be met before a student is admitted to the upper division major.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - A grade point average of C (2.0) or better is required in the courses stipulated here for the major.
  - Students intending to pursue the Personal Financial Planning Certificate should refer to the certificate requirements when choosing their elective courses.

### Coverage (sections in data/cleaned)

- Required courses: 18 of 18 have sections
  - with sections: FIN 240 (9), ACCTG 201 (11), ACCTG 202 (12), ECON 101 (6), ECON 102 (6), MIS 180 (20), MATH 120 (5), RWS 290 (31), FIN 327 (6), FIN 331 (5), FIN 589 (1), B A 300 (18), B A 305 (8), B A 310 (14), B A 323 (13), B A 350 (14), B A 360 (11), B A 370 (16)
- Pick-n group courses: 6 of 6 have sections
  - with sections: STAT 119 (5), ECON 201 (4), FIN 334 (4), FIN 522 (1), FIN 433 (1), ACCTG 503 (3)
- Elective pool courses: 15 of 16 have sections
  - with sections: FIN 326 (1), FIN 335 (7), FIN 336 (1), FIN 421 (1), FIN 422 (1), FIN 427 (1), FIN 431 (1), FIN 435 (1), FIN 585 (1), FIN 590 (1), ACCTG 326 (10), ECON 320 (3), ECON 422 (1), ECON 490 (1), MKTG 377 (5)
  - no sections: FIN 436

### Title differences (catalog vs class data)

- none
- 4 more only shortened in the class data (not a real difference): FIN 334, ACCTG 503, FIN 336, ECON 320

## Business Administration, Emphasis in Information Systems, B.S. (`ba_information_systems_bs`)

- Source: `data/catalog_html/Program_ Business Administration, Emphasis in Information Systems, B.S. - San Diego State University.html`, poid 12117, major code 07021
- Rows: 34

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: MIS 180, ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 13: MIS 301, MIS 306, MIS 315, MIS 380, MIS 383, MIS 460, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 12 units | 11: MIS 305, MIS 396W, MIS 401, MIS 420, MIS 425, MIS 429, MIS 455, MIS 481, MIS 495, MIS 515, MIS 585 |

### Section notes (shown once under the heading)

- none

### Review list

- [ ] 'Upper Division Major Electives' (under Major) asks for 12 units of its list: encoded as a pool in its own section 'Upper Division Major Electives', check it.

### Units check (advisory)

- Preparation for the Major: page says 27 units, listed courses give 27: **inside**
- Major: page says 45 units, listed courses give 45: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a bachelor’s degree must complete the graduation requirements listed in the section of this catalog on “Graduation Requirements.”
  - Students in the Fowler College of Business may declare only one emphasis under the Business Administration major and may not double major in International Business.
  - A minor is not required for the Business Administration major with an emphasis in Information Systems. Students may declare only one minor within the Fowler College of Business.
  - Students must complete all upper division courses in the major within seven years prior to graduation. Students who will have completed any of those courses more than seven years before the projected date of graduation must contact the department chair for information about ways to certify knowledge of current course content.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Preparation for the Major**
  - Additional progress requirements must be met before a student is admitted to the upper division major.
- **Graduation Writing Assessment Requirement**
  - Complete one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - A C (2.0) average or better is required in the courses stipulated here for the major.

### Coverage (sections in data/cleaned)

- Required courses: 21 of 21 have sections
  - with sections: MIS 180 (20), ACCTG 201 (11), ACCTG 202 (12), ECON 101 (6), ECON 102 (6), FIN 240 (9), MATH 120 (5), RWS 290 (31), MIS 301 (7), MIS 306 (5), MIS 315 (6), MIS 380 (4), MIS 383 (4), MIS 460 (3), B A 300 (18), B A 305 (8), B A 310 (14), B A 323 (13), B A 350 (14), B A 360 (11), B A 370 (16)
- Pick-n group courses: 2 of 2 have sections
  - with sections: STAT 119 (5), ECON 201 (4)
- Elective pool courses: 9 of 11 have sections
  - with sections: MIS 305 (3), MIS 401 (1), MIS 420 (1), MIS 425 (2), MIS 455 (1), MIS 481 (2), MIS 495 (1), MIS 515 (2), MIS 585 (2)
  - no sections: MIS 396W, MIS 429

### Title differences (catalog vs class data)

- MIS 495: catalog "Management Information Systems Internship", class data "MIS Internship"
- 2 more only shortened in the class data (not a real difference): MIS 383, MIS 305

## Business Administration, Emphasis in Management, B.S. (`ba_management_bs`)

- Source: `data/catalog_html/Program_ Business Administration, Emphasis in Management, B.S. - San Diego State University.html`, poid 12112, major code 05061
- Rows: 42

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 14: MGT 352, MGT 357, MGT 358, MGT 401, MGT 444, MGT 475, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370, MGT 405 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 6 units | 18: B A 404, MGT 353, MGT 403, MGT 420, MGT 422, MGT 452, MGT 455, MGT 459, MGT 460, MGT 461, MGT 462, MGT 463, MGT 464, MGT 466, MGT 467, MGT 468, MGT 483, MIS 301 |

### Section notes (shown once under the heading)

- none

### Review list

- [ ] 'Upper Division Major Electives' (under Major) asks for 6 units of its list: encoded as a pool in its own section 'Upper Division Major Electives', check it.

### Units check (advisory)

- Preparation for the Major: page says 27 units, listed courses give 27: **inside**
- Major: page says 42 units, listed courses give 42: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a bachelor’s degree must complete the graduation requirements listed in the section of this catalog on “Graduation Requirements.”
  - Students in the Fowler College of Business may declare only one emphasis under the Business Administration major and may not double major in International Business.
  - A minor is not required for the Business Administration major with an emphasis in Management. Students may declare only one minor within the Fowler College of Business.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Preparation for the Major**
  - Additional progress requirements must be met before a student is admitted to the upper division major.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - A C (2.0) average or better is required in the courses stipulated here for the major.

### Coverage (sections in data/cleaned)

- Required courses: 22 of 22 have sections
  - with sections: ACCTG 201 (11), ACCTG 202 (12), ECON 101 (6), ECON 102 (6), FIN 240 (9), MIS 180 (20), MATH 120 (5), RWS 290 (31), MGT 352 (4), MGT 357 (3), MGT 358 (6), MGT 401 (3), MGT 444 (6), MGT 475 (6), B A 300 (18), B A 305 (8), B A 310 (14), B A 323 (13), B A 350 (14), B A 360 (11), B A 370 (16), MGT 405 (13)
- Pick-n group courses: 2 of 2 have sections
  - with sections: STAT 119 (5), ECON 201 (4)
- Elective pool courses: 13 of 18 have sections
  - with sections: MGT 353 (2), MGT 403 (1), MGT 420 (2), MGT 422 (1), MGT 452 (1), MGT 455 (1), MGT 460 (2), MGT 461 (1), MGT 462 (1), MGT 464 (1), MGT 466 (1), MGT 468 (1), MIS 301 (7)
  - no sections: B A 404, MGT 459, MGT 463, MGT 467, MGT 483

### Title differences (catalog vs class data)

- none

## Business Administration, Emphasis in Marketing, B.S. (`ba_marketing_bs`)

- Source: `data/catalog_html/Program_ Business Administration, Emphasis in Marketing, B.S. - San Diego State University.html`, poid 12120, major code 05091
- Rows: 49

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 9: B A 300, MIS 301, MKTG 305, B A 310, B A 323, B A 350, B A 360, B A 370, MKTG 371 |
| Major | MKTG 470 or MKTG 480 (pick 1) | choose 1 | 2: MKTG 470, MKTG 480 |
| Major | MKTG 490 or MKTG 491 or MKTG 492 or MKTG 493 or MKTG 494 (pick 1) | choose 1 | 5: MKTG 490, MKTG 491, MKTG 492, MKTG 493, MKTG 494 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 14 units | 22: MKTG 306, MKTG 372, MKTG 373, MKTG 376, MKTG 377, MKTG 380, MKTG 381, MKTG 402, MKTG 470, MKTG 473, MKTG 474, MKTG 476, MKTG 477, MKTG 478, MKTG 480, MKTG 495, MKTG 496, MKTG 498, MKTG 499, B A 404, MGT 405, MIS 305 |

### Section notes (shown once under the heading)

- **Upper Division Major Electives**: (6 units may be taken outside the Fowler College of Business by department chair approval)

### Review list

- [ ] Text under 'Major' kept as a major note, not on its courses: "Marketing students may pursue various career objectives supported by pathways. These pathways include Brand Management, Customer Experience Management, Integrated Marketing Communications, Marketing Analytics and Intelligence, Professional Selling and Sales Leadership, Strategic Marketing Management, or Sustainable Marketing Management. Please visit the Marketing Department Website https://business.sdsu.edu/undergrad/marketing for specific pathway coursework options. MKTG 490 may only be taken after completion of both MKTG 470 and MKTG 480. MKTG 491, 492, 493, or 494 may only be taken after completion of MKTG 371 and either MKTG 470 or MKTG 480."
- [ ] 'Upper Division Major Electives': rule text kept as the section note, check it: "(6 units may be taken outside the Fowler College of Business by department chair approval)"
- [ ] BA 404 or MGT 405 (pick 1) in the 'Upper Division Major Electives' pool: kept as pool rows with a note (a pick-1 group inside a units pool would be counted on its own).
- [ ] 'Upper Division Major Electives' (under Major) asks for 14 units of its list: encoded as a pool in its own section 'Upper Division Major Electives', check it.

### Units check (advisory)

- Preparation for the Major: page says 27 units, listed courses give 27: **inside**
- Major: page says 44 units, listed courses give 44: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a bachelor’s degree must complete the graduation requirements listed in the section of this catalog on “Graduation Requirements.”
  - Within the Business Administration major, students may declare only one emphasis. Double majoring in International Business is not permitted for students in the Fowler College of Business.
  - A minor is not required for the Business Administration major. Students may declare only one minor within the Fowler College of Business.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Preparation for the Major**
  - Additional progress requirements must be met before a student is admitted to the upper division major.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - A C (2.0) average or better is required in the courses stipulated here for the major.
  - Marketing students may pursue various career objectives supported by pathways.
  - These pathways include Brand Management, Customer Experience Management, Integrated Marketing Communications, Marketing Analytics and Intelligence, Professional Selling and Sales Leadership, Strategic Marketing Management, or Sustainable Marketing Management.
  - Please visit the Marketing Department Website https://business.sdsu.edu/undergrad/marketing for specific pathway coursework options.
  - MKTG 490 may only be taken after completion of both MKTG 470 and MKTG 480.
  - MKTG 491, 492, 493, or 494 may only be taken after completion of MKTG 371 and either MKTG 470 or MKTG 480.

### Coverage (sections in data/cleaned)

- Required courses: 17 of 17 have sections
  - with sections: ACCTG 201 (11), ACCTG 202 (12), ECON 101 (6), ECON 102 (6), FIN 240 (9), MIS 180 (20), MATH 120 (5), RWS 290 (31), B A 300 (18), MIS 301 (7), MKTG 305 (11), B A 310 (14), B A 323 (13), B A 350 (14), B A 360 (11), B A 370 (16), MKTG 371 (6)
- Pick-n group courses: 8 of 9 have sections
  - with sections: STAT 119 (5), ECON 201 (4), MKTG 470 (3), MKTG 480 (6), MKTG 491 (1), MKTG 492 (3), MKTG 493 (1), MKTG 494 (5)
  - no sections: MKTG 490
- Elective pool courses: 12 of 20 have sections
  - with sections: MKTG 372 (2), MKTG 373 (3), MKTG 376 (2), MKTG 377 (5), MKTG 380 (2), MKTG 381 (2), MKTG 402 (1), MKTG 473 (2), MKTG 476 (2), MKTG 478 (2), MGT 405 (13), MIS 305 (3)
  - no sections: MKTG 306, MKTG 474, MKTG 477, MKTG 495, MKTG 496, MKTG 498, MKTG 499, B A 404

### Title differences (catalog vs class data)

- none
- 4 more only shortened in the class data (not a real difference): MKTG 305, MKTG 380, MKTG 381, MIS 305

## Business Administration, Emphasis in Real Estate, B.S. (`ba_real_estate_bs`)

- Source: `data/catalog_html/Program_ Business Administration, Emphasis in Real Estate, B.S. - San Diego State University.html`, poid 12010, major code 05111
- Rows: 23

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: FIN 240, ACCTG 201, ACCTG 202, ECON 101, ECON 102, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 12: FIN 331, FIN 333, FIN 431, FIN 433, FIN 435, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370 |
| Upper Division Major Electives | Any FIN 300-599 course | open, 9 units | 1: Any FIN 300-599 course |

### Section notes (shown once under the heading)

- none

### Review list

- [ ] 'Any FIN 300-599 course' in Upper Division Major Electives: "9 units selected from Finance (FIN) courses numbered 300-599" encoded as an open rule (FIN 300-599, 9 units); check it.

### Units check (advisory)

- Preparation for the Major: page says 27 units, listed courses give 27: **inside**
- Major: page says 39 units, listed courses give 39: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a bachelor’s degree must complete the graduation requirements listed in the section of this catalog on “Graduation Requirements.”
  - Students in the Fowler College of Business may declare only one emphasis under the Business Administration major and may not double major in International Business.
  - A minor is not required for the Business Administration major with an emphasis in Real Estate. Students may declare only one minor within the Fowler College of Business.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Preparation for the Major**
  - Additional progress requirements must be met before a student is admitted to the upper division major.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - A C (2.0) average or better is required in the courses stipulated here for the major.

### Coverage (sections in data/cleaned)

- Required courses: 19 of 20 have sections
  - with sections: FIN 240 (9), ACCTG 201 (11), ACCTG 202 (12), ECON 101 (6), ECON 102 (6), MIS 180 (20), MATH 120 (5), RWS 290 (31), FIN 331 (5), FIN 431 (1), FIN 433 (1), FIN 435 (1), B A 300 (18), B A 305 (8), B A 310 (14), B A 323 (13), B A 350 (14), B A 360 (11), B A 370 (16)
  - no sections: FIN 333
- Pick-n group courses: 2 of 2 have sections
  - with sections: STAT 119 (5), ECON 201 (4)
- Open rule 'Any FIN 300-599 course' (without excluded and already-required courses): 18 courses with sections: FIN 321, FIN 325, FIN 326, FIN 327, FIN 328, FIN 329, FIN 334, FIN 335, FIN 336, FIN 421, FIN 422, FIN 423, FIN 427, FIN 437, FIN 522, FIN 585, FIN 589, FIN 590

### Title differences (catalog vs class data)

- none

## Business Administration, Management, Specialization in Entrepreneurship, B.S. (`ba_management_entrepreneurship_bs`)

- Source: `data/catalog_html/Program_ Business Administration, Management, Specialization in Entrepreneurship, B.S. - San Diego State University.html`, poid 12113
- Rows: 32

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 14: MGT 358, MGT 401, MGT 420, MGT 444, MGT 460, MGT 475, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370, MGT 405 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 6 units | 8: MGT 353, MGT 422, MGT 452, MGT 455, MGT 459, MGT 470, JMS 480, MIS 301 |

### Section notes (shown once under the heading)

- none

### Review list

- [ ] 'Upper Division Major Electives' (under Major) asks for 6 units of its list: encoded as a pool in its own section 'Upper Division Major Electives', check it.

### Units check (advisory)

- Preparation for the Major: page says 27 units, listed courses give 27: **inside**
- Major: page says 42 units, listed courses give 42: **inside**

### Major notes (no rows made; for a human)

- **(Academic Plan Code: 222564BSS)**
  - All candidates for a bachelor’s degree must complete the graduation requirements listed in the section of this catalog on “Graduation Requirements.”
  - Students in the Fowler College of Business may declare only one emphasis under the Business Administration major and may not double major in International Business.
  - A minor is not required for the Business Administration major with a specialization in Entrepreneurship. Students may declare only one minor within the Fowler College of Business.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Preparation for the Major**
  - Additional progress requirements must be met before a student is admitted to the upper division major.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - A C (2.0) average or better is required in the courses stipulated here for the major.

### Coverage (sections in data/cleaned)

- Required courses: 22 of 22 have sections
  - with sections: ACCTG 201 (11), ACCTG 202 (12), ECON 101 (6), ECON 102 (6), FIN 240 (9), MIS 180 (20), MATH 120 (5), RWS 290 (31), MGT 358 (6), MGT 401 (3), MGT 420 (2), MGT 444 (6), MGT 460 (2), MGT 475 (6), B A 300 (18), B A 305 (8), B A 310 (14), B A 323 (13), B A 350 (14), B A 360 (11), B A 370 (16), MGT 405 (13)
- Pick-n group courses: 2 of 2 have sections
  - with sections: STAT 119 (5), ECON 201 (4)
- Elective pool courses: 7 of 8 have sections
  - with sections: MGT 353 (2), MGT 422 (1), MGT 452 (1), MGT 455 (1), MGT 470 (1), JMS 480 (1), MIS 301 (7)
  - no sections: MGT 459

### Title differences (catalog vs class data)

- none

## Business Administration, Management, Specialization in Human Resource Management, B.S. (`ba_management_human_resource_management_bs`)

- Source: `data/catalog_html/Program_ Business Administration, Management, Specialization in Human Resource Management, B.S. - San Diego State University.html`, poid 12114
- Rows: 30

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 14: MGT 352, MGT 401, MGT 444, MGT 461, MGT 462, MGT 475, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370, MGT 405 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 6 units | 6: MGT 463, MGT 464, MGT 466, MGT 467, MGT 468, MIS 301 |

### Section notes (shown once under the heading)

- none

### Review list

- [ ] 'Upper Division Major Electives' (under Major) asks for 6 units of its list: encoded as a pool in its own section 'Upper Division Major Electives', check it.

### Units check (advisory)

- Preparation for the Major: page says 27 units, listed courses give 27: **inside**
- Major: page says 42 units, listed courses give 42: **inside**

### Major notes (no rows made; for a human)

- **(Academic Plan Code: 222563BSS)**
  - All candidates for a bachelor’s degree must complete the graduation requirements listed in the section of this catalog on “Graduation Requirements.”
  - Students in the Fowler College of Business may declare only one emphasis under the Business Administration major and may not double major in International Business.
  - A minor is not required for the Business Administration major with a specialization in Human Resource Management. Students may declare only one minor within the Fowler College of Business.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Preparation for the Major**
  - Additional progress requirements must be met before a student is admitted to the upper division major.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - A C (2.0) average or better is required in the courses stipulated here for the major.

### Coverage (sections in data/cleaned)

- Required courses: 22 of 22 have sections
  - with sections: ACCTG 201 (11), ACCTG 202 (12), ECON 101 (6), ECON 102 (6), FIN 240 (9), MIS 180 (20), MATH 120 (5), RWS 290 (31), MGT 352 (4), MGT 401 (3), MGT 444 (6), MGT 461 (1), MGT 462 (1), MGT 475 (6), B A 300 (18), B A 305 (8), B A 310 (14), B A 323 (13), B A 350 (14), B A 360 (11), B A 370 (16), MGT 405 (13)
- Pick-n group courses: 2 of 2 have sections
  - with sections: STAT 119 (5), ECON 201 (4)
- Elective pool courses: 4 of 6 have sections
  - with sections: MGT 464 (1), MGT 466 (1), MGT 468 (1), MIS 301 (7)
  - no sections: MGT 463, MGT 467

### Title differences (catalog vs class data)

- none

## Civil Engineering, B.S. (`civil_engineering_bs`)

- Source: `data/catalog_html/Program_ Civil Engineering, B.S. - San Diego State University.html`, poid 11952, major code 09081
- Rows: 55

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 13: CIV E 100, CIV E 121, CIV E 218, CIV E 220, CIV E 225, A E 280, CON E 101, MATH 150, MATH 151, MATH 252, PHYS 195, PHYS 195L, PHYS 196 |
| Preparation for the Major | CIVE 160 or STAT 250 (pick 1) | choose 1 | 2: CIV E 160, STAT 250 |
| Preparation for the Major | BIOL 100 or BIOL 101 (pick 1) | choose 1 | 2: BIOL 100, BIOL 101 |
| Preparation for the Major | CHEM 202 or CHEM 200 (pick 1) | choose 1 | 2: CHEM 202, CHEM 200 |
| Engineering Science Elective | Engineering Science Elective (pick 1) | choose 1 | 3: CON E 240, E E 204, M E 350 |
| Major | Required | required | 12: CIV E 302, CIV E 321, CIV E 401, CIV E 421, CIV E 444, CIV E 462, CIV E 463, CIV E 481, CIV E 495W, A E 340, CON E 330, ENV E 355 |
| Major | CIVE 301 or ME 304 (pick 1) | choose 1 | 2: CIV E 301, M E 304 |
| Professional Electives | Water | pool, 15 units | 2: CIV E 445, CIV E 530 |
| Professional Electives | Transportation | pool, 15 units | 2: CIV E 482, CIV E 580 |
| Professional Electives | Environmental | pool, 15 units | 4: ENV E 363, ENV E 445, ENV E 556, ENV E 558 |
| Professional Electives | Structural | pool, 15 units | 4: CIV E 521, CIV E 523, CIV E 525, CIV E 528 |
| Professional Electives | Geotechnical | pool, 15 units | 1: CIV E 465 |
| Professional Electives | Construction | pool, 15 units | 4: CON E 401, CON E 479, CON E 480, CON E 520 |

### Section notes (shown once under the heading)

- **Engineering Science Elective**: Select at least one of the following courses
- **Professional Electives**: 15 units of elective credit. Course choices must consist of at least one course from at least four of the six areas to include ten units of designated design courses

### Review list

- [ ] 'Engineering Science Elective (pick 1)' in Engineering Science Elective: read as pick 1 of 3; check it.
- [ ] 'Professional Electives' (under Major) is a rule in words, encoded as one pool; check it. Catalog: "15 units of elective credit. Course choices must consist of at least one course from at least four of the six areas to include ten units of designated design courses."

### Units check (advisory)

- Preparation for the Major: page says 48 units, listed courses give 48-49: **overlaps**
- Major: page says at least 48 units, listed courses give 48: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - This program requires 126 units to include general education. In addition, the total number of units specified in each elective category represents the minimum requirement.
- **Impacted Program**
  - The Civil Engineering major is an impacted program. To be admitted to the Civil Engineering major, students must meet the following impaction criteria:
  - Complete with a grade of C (2.0) or better: CIV E 225; CHEM 202 (or CHEM 200); MATH 150, MATH 151; PHYS 195, PHYS 196. These courses cannot be taken for credit/no credit (Cr/NC);
  - Have an overall cumulative GPA of 2.7 or higher.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Major Restriction for Registration**
  - You must be in the Civil, Construction, Environmental Engineering or Construction Management major (cleared impaction requirements) in order to take the upper level (300-400+) courses. This rule does not apply for CIV E 301.
- **General Education**
  - Engineering majors automatically satisfy Area 2/5. Mathematical Concepts and Quantitative Reasoning or Physical and Biological Sciences and Area 4. Social and Behavioral Explorations GE areas by completion of the major.
- **Graduation Writing Assessment Requirement**
  - Complete CIV E 495W with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Master Plan**
  - A master plan of elective courses must be approved by the undergraduate advisor as soon as the civil engineering major is declared. Students are required to see their undergraduate advisor prior to registration each semester.

### Coverage (sections in data/cleaned)

- Required courses: 23 of 25 have sections
  - with sections: CIV E 121 (8), CIV E 218 (6), CIV E 225 (2), A E 280 (3), CON E 101 (1), MATH 150 (12), MATH 151 (20), MATH 252 (13), PHYS 195 (2), PHYS 195L (17), PHYS 196 (1), CIV E 302 (5), CIV E 321 (1), CIV E 401 (2), CIV E 421 (1), CIV E 444 (4), CIV E 462 (2), CIV E 463 (3), CIV E 481 (2), CIV E 495W (4), A E 340 (2), CON E 330 (2), ENV E 355 (2)
  - no sections: CIV E 100, CIV E 220
- Pick-n group courses: 11 of 11 have sections
  - with sections: CIV E 160 (1), STAT 250 (8), BIOL 100 (4), BIOL 101 (1), CHEM 202 (11), CHEM 200 (49), CON E 240 (2), E E 204 (1), M E 350 (3), CIV E 301 (3), M E 304 (3)
- Elective pool courses: 13 of 17 have sections
  - with sections: CIV E 445 (2), CIV E 530 (2), CIV E 482 (2), ENV E 363 (3), ENV E 445 (1), ENV E 556 (1), ENV E 558 (1), CIV E 523 (1), CIV E 465 (2), CON E 401 (3), CON E 479 (2), CON E 480 (1), CON E 520 (1)
  - no sections: CIV E 580, CIV E 521, CIV E 525, CIV E 528

### Title differences (catalog vs class data)

- none
- 21 more only shortened in the class data (not a real difference): CIV E 121, CIV E 218, CIV E 225, CIV E 160, CHEM 202, CON E 240, E E 204, CIV E 302, CIV E 401, CIV E 421, CIV E 481, CON E 330, CIV E 301, ENV E 363, ENV E 445, ENV E 558, CIV E 523, CIV E 465, CON E 401, CON E 480, CON E 520

## Computer Engineering, B.S. (`computer_engineering_bs`)

- Source: `data/catalog_html/Program_ Computer Engineering, B.S. - San Diego State University.html`, poid 11968, major code 09094
- Rows: 45

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 14: COMPE 101, COMPE 160, COMPE 260, COMPE 270, COMPE 271, E E 200, E E 210, MATH 150, MATH 151, MATH 245, MATH 254, PHYS 195, PHYS 196, PHYS 196L |
| Preparation for the Major | BIOL 100 or BIOL 101 (pick 1) | choose 1 | 2: BIOL 100, BIOL 101 |
| Major | Required | required | 13: COMPE 361, COMPE 375, COMPE 470, COMPE 470L, COMPE 475, COMPE 491W, COMPE 493, COMPE 560, E E 300, E E 310, E E 330, E E 330L, E E 410 |
| Upper Division Major Electives | Computer Networks | pool, 15 units | 4: COMPE 561, COMPE 565, E E 458, E E 558 |
| Upper Division Major Electives | Embedded Systems | pool, 15 units | 3: COMPE 525, COMPE 571, E E 420 |
| Upper Division Major Electives | Machine Learning and Scientific Computing | pool, 15 units | 3: COMPE 510, E E 450, E E 533 |
| Upper Division Major Electives | VLSI Systems | pool, 15 units | 5: COMPE 570, COMPE 572, E E 430, E E 503, E E 530 |

### Section notes (shown once under the heading)

- **Upper Division Major Electives**: (15 units) Five upper division major elective courses from the following list in 4 concentration areas

### Review list

- [ ] Text under 'Major' kept as a major note, not on its courses: "After enrollment in Computer Engineering at SDSU, the Computer Engineering major must take all upper division computer science and engineering courses at SDSU unless prior approval is obtained from the department."
- [ ] 'Upper Division Major Electives' (under Major) is a rule in words, encoded as one pool; check it. Catalog: "(15 units) Five upper division major elective courses from the following list in 4 concentration areas."

### Units check (advisory)

- Preparation for the Major: page says 43 units, listed courses give 43: **inside**
- Major: page says at least 50 units, listed courses give 50: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
- **Impacted Program**
  - The Computer Engineering major is an impacted program. To be admitted to the major, students must meet the following impaction criteria:
  - a. Complete with a grade of C (2.0) or better: E E 210; COMPE 160; MATH 150, MATH 151; PHYS 195, PHYS 196. These courses cannot be taken for credit/no credit (Cr/NC);
  - b. Have an overall cumulative GPA of 2.70.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Major Restriction for Registration**
  - You must be in the Electrical or Computer Engineering major (cleared impaction requirements) in order to take the upper level (300-400+) courses.
- **General Education**
  - Engineering majors automatically satisfy Area 2/5. Mathematical Concepts and Quantitative Reasoning or Physical and Biological Sciences and Area 4. Social and Behavioral Explorations GE areas by completion of the major.
- **Graduation Writing Assessment Requirement**
  - Complete COMPE 491W with a grade of C (2.0) or better to satisfy the Graduation Writing Assessment Requirement. See Graduation Requirements section for a complete listing of requirements. Courses listed: COMPE 491W.
- **Major**
  - After enrollment in Computer Engineering at SDSU, the Computer Engineering major must take all upper division computer science and engineering courses at SDSU unless prior approval is obtained from the department.
- **Master Plan**
  - The master plan provides an advising record and a roadmap toward graduation for computer engineering majors. The master plan must be filed electronically with the department advisors (https://csse.sdsu.edu/advising/advising). All students transferring from another institution are required to file the master plan at the time of transfer. Current SDSU students are required to file the master plan as part of their course requirements in COMPE 101. Students are encouraged to seek the guidance of their advisors when completing the master plan. If there is any change to the course sequence listed in the master plan that is already on file, it must be updated and refiled. All students must have an updated master plan on file in the department prior to enrollment in E E 410 and COMPE 491W . All course substitutions must be approved by the department chair prior to enrolling in the course.

### Coverage (sections in data/cleaned)

- Required courses: 25 of 27 have sections
  - with sections: COMPE 101 (1), COMPE 160 (4), COMPE 260 (1), COMPE 270 (1), COMPE 271 (1), E E 200 (2), E E 210 (2), MATH 150 (12), MATH 151 (20), MATH 245 (1), MATH 254 (1), PHYS 195 (2), PHYS 196 (1), PHYS 196L (10), COMPE 361 (1), COMPE 375 (5), COMPE 470 (1), COMPE 470L (2), COMPE 475 (1), COMPE 491W (2), E E 300 (1), E E 310 (1), E E 330 (1), E E 330L (6), E E 410 (1)
  - no sections: COMPE 493, COMPE 560
- Pick-n group courses: 2 of 2 have sections
  - with sections: BIOL 100 (4), BIOL 101 (1)
- Elective pool courses: 11 of 15 have sections
  - with sections: COMPE 561 (1), COMPE 565 (1), E E 458 (1), COMPE 525 (1), COMPE 571 (1), E E 420 (1), E E 450 (1), E E 533 (1), COMPE 572 (1), E E 430 (1), E E 530 (1)
  - no sections: E E 558, COMPE 510, COMPE 570, E E 503

### Title differences (catalog vs class data)

- COMPE 260: catalog "Data Structures and Object-Oriented Programming in C++", class data "Data Structures OOP C++"
- E E 530: catalog "Analog Integrated Circuit Design", class data "Analog Integrated Ckt Des"
- 12 more only shortened in the class data (not a real difference): COMPE 101, COMPE 160, E E 200, COMPE 375, E E 300, E E 330, E E 330L, COMPE 561, COMPE 565, E E 458, COMPE 571, E E 430

## Electrical Engineering, B.S. (`electrical_engineering_bs`)

- Source: `data/catalog_html/Program_ Electrical Engineering, B.S. - San Diego State University.html`, poid 11987, major code 09091
- Rows: 55

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 14: E E 101, E E 200, E E 210, COMPE 160, COMPE 270, COMPE 271, MATH 150, MATH 151, MATH 252, MATH 254, PHYS 195, PHYS 195L, PHYS 196, PHYS 196L |
| Preparation for the Major | BIOL 100 or BIOL 101 (pick 1) | choose 1 | 2: BIOL 100, BIOL 101 |
| Major | Required | required | 14: E E 300, E E 310, E E 330, E E 330L, E E 340, E E 380, E E 410, E E 420, E E 430, E E 440, E E 450, E E 491W, E E 493, COMPE 375 |
| Professional Electives | Computer Engineering | pool, 9 units | 5: COMPE 470, COMPE 475, COMPE 560, COMPE 565, COMPE 572 |
| Professional Electives | Electromagnetics | pool, 9 units | 2: E E 455, E E 540 |
| Professional Electives | Power and Controls | pool, 9 units | 6: E E 480, E E 483, E E 522, E E 581, E E 584, E E 586 |
| Professional Electives | Electronics | pool, 9 units | 4: E E 502, E E 503, E E 530, E E 533 |
| Professional Electives | Communications and Digital Signal Processing | pool, 9 units | 2: E E 458, E E 558 |
| Laboratory Electives | Laboratory Electives | pool, 2 units | 5: E E 380L, E E 420L, E E 584L, E E 430L, E E 458L |

### Section notes (shown once under the heading)

- **Professional Electives**: No more than 3 units from computer engineering or approved courses from other departments

### Review list

- [ ] BIOL 100 or BIOL 101 (pick 1) in Preparation for the Major: the 'or' sits next to other courses with no break, so it may cover more than one course. Check the catalog page.
- [ ] 'Professional Electives': split in two as the page states: 'Professional Electives' (9 units, 19 courses) and 'Laboratory Electives' (2 units, the 5 lab courses).
- [ ] 'Professional Electives': the app cannot count "No more than 3 units from computer engineering or approved courses from other departments"; it is the section note.

### Units check (advisory)

- Preparation for the Major: page says 42 units, listed courses give 42: **inside**
- Major: page says at least 51 units, listed courses give 51: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
- **Impacted Program**
  - The Electrical Engineering major is an impacted program. To be admitted to the major, students must meet the following impaction criteria:
  - a. Complete with a grade of C (2.0) or better: E E 210; COMPE 160; MATH 150, MATH 151; PHYS 195, PHYS 196. These courses cannot be taken for credit/no credit (Cr/NC);
  - b. Have an overall cumulative GPA of 2.7.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Major Restriction for Registration**
  - You must be in the Electrical or Computer Engineering major (cleared impaction requirements) in order to take the upper level (300-400+) courses.
- **General Education**
  - Engineering majors automatically satisfy Area 2/5. Mathematical Concepts and Quantitative Reasoning or Physical and Biological Sciences and Area 4. Social and Behavioral Explorations GE areas by completion of the major.
- **Graduation Writing Assessment Requirement**
  - Complete E E 491W and with a grade of C (2.0) or better to satisfy the Graduation Writing Assessment Requirement. See Graduation Requirements section for a complete listing of requirements. Courses listed: E E 491W.
- **Master Plan**
  - The master plan provides an advising record and a roadmap toward graduation for electrical engineering majors. The master plan must be filed electronically with the department advisors (https://csse.sdsu.edu/advising/advising). All students transferring from another institution are required to file the master plan at the time of transfer. Current SDSU students are required to file the master plan as part of their course requirements in E E 101. Students are encouraged to seek the guidance of their advisors when completing the master plan. If there is any change to the course sequence listed in the master plan that is already on file, it must be updated and refiled. All students must have an updated master plan on file in the department prior to enrollment in E E 410 and E E 491W . All course substitutions must be approved by the department chair prior to enrolling in the course.

### Coverage (sections in data/cleaned)

- Required courses: 27 of 28 have sections
  - with sections: E E 101 (1), E E 200 (2), E E 210 (2), COMPE 160 (4), COMPE 270 (1), COMPE 271 (1), MATH 150 (12), MATH 151 (20), MATH 252 (13), MATH 254 (1), PHYS 195 (2), PHYS 195L (17), PHYS 196 (1), PHYS 196L (10), E E 300 (1), E E 310 (1), E E 330 (1), E E 330L (6), E E 340 (1), E E 380 (1), E E 410 (1), E E 420 (1), E E 430 (1), E E 440 (1), E E 450 (1), E E 491W (2), COMPE 375 (5)
  - no sections: E E 493
- Pick-n group courses: 2 of 2 have sections
  - with sections: BIOL 100 (4), BIOL 101 (1)
- Elective pool courses: 14 of 24 have sections
  - with sections: COMPE 470 (1), COMPE 475 (1), COMPE 565 (1), COMPE 572 (1), E E 455 (1), E E 483 (1), E E 502 (2), E E 530 (1), E E 533 (1), E E 458 (1), E E 380L (3), E E 420L (1), E E 430L (2), E E 458L (1)
  - no sections: COMPE 560, E E 540, E E 480, E E 522, E E 581, E E 584, E E 586, E E 503, E E 558, E E 584L

### Title differences (catalog vs class data)

- E E 530: catalog "Analog Integrated Circuit Design", class data "Analog Integrated Ckt Des"
- E E 458L: catalog "Communications and Digital Signal Processing Laboratory", class data "Communication & Dsp Lab"
- 17 more only shortened in the class data (not a real difference): E E 101, E E 200, COMPE 160, E E 300, E E 330, E E 330L, E E 340, E E 380, E E 430, COMPE 375, COMPE 565, E E 483, E E 502, E E 458, E E 380L, E E 420L, E E 430L

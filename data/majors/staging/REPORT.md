# Catalog import report (2026-2027)

Staging only: nothing here is live. Every major is `coming_soon`. Check each one against its catalog page, then promote it with `python3 scripts/import_catalog_majors.py --promote <major_id>`.

| Majors processed | Requirement rows | Majors with open review items |
| --- | --- | --- |
| 33 | 1270 | 33 |

## Batch check: 20 of 20 pages found

| # | Program | major_id | Page |
| --- | --- | --- | --- |
| 1 | Aerospace Engineering, B.S. | `aerospace_engineering_bs` | found |
| 2 | Construction Engineering, B.S. | `construction_engineering_bs` | found |
| 3 | Environmental Engineering, B.S. | `environmental_engineering_bs` | found |
| 4 | Mechanical Engineering, Emphasis in Bioengineering, B.S. | `mechanical_engineering_bioengineering_bs` | found |
| 5 | Psychology, Emphasis in Industrial and Organizational Psychology, B.A. | `psychology_industrial_organizational_ba` | found |
| 6 | Psychology, Emphasis in Neuroscience, B.A. | `psychology_neuroscience_ba` | found |
| 7 | Kinesiology, Emphasis in Exercise Science Generalist, B.S. | `kinesiology_exercise_science_generalist_bs` | found |
| 8 | Kinesiology, Emphasis in Fitness Specialist, B.S. | `kinesiology_fitness_specialist_bs` | found |
| 9 | Communication, B.A. | `communication_ba` | found |
| 10 | Health Communication, B.S. | `health_communication_bs` | found |
| 11 | Biology, B.A. | `biology_ba` | found |
| 12 | Biology, B.S. | `biology_bs` | found |
| 13 | Biology, Emphasis in Cellular and Molecular Biology, B.S. | `biology_cellular_molecular_bs` | found |
| 14 | Biology, Emphasis in Ecology, B.S. | `biology_ecology_bs` | found |
| 15 | Biology, Emphasis in Evolutionary Biology, B.S. | `biology_evolutionary_bs` | found |
| 16 | Biology, Emphasis in Marine Biology, B.S. | `biology_marine_bs` | found |
| 17 | Biology, Emphasis in Zoology, B.S. | `biology_zoology_bs` | found |
| 18 | Chemistry, B.A. | `chemistry_ba` | found |
| 19 | Chemistry, and Certificate of the American Chemical Society, B.S. | `chemistry_american_chemical_society_bs` | found |
| 20 | Chemistry, Emphasis in Biochemistry, and Certificate of the American Chemical Society, B.S. | `chemistry_biochemistry_american_chemical_society_bs` | found |

## Run notes

- data/catalog_html/Program_ Business Administration, Emphasis in Management, B.S. - San Diego State University.html: no program id in the page; matched by its title to poid 12112
- data/catalog_html/Program_ Chemistry, Emphasis in Biochemistry, B.S. and Certificate of the American Chemical Society - San Diego State University.html: no program id in the page; matched by its title to poid 11938
- data/catalog_html/Program_ Construction Engineering, B.S. - San Diego State University.html: no program id in the page; matched by its title to poid 11972
- data/catalog_html/Program_ Environmental Engineering, B.S. - San Diego State University.html: no program id in the page; matched by its title to poid 11997
- data/catalog_html/Program_ Kinesiology, Emphasis in Exercise Science Generalist, B.S. - San Diego State University.html: no program id in the page; matched by its title to poid 12004
- data/catalog_html/Program_ Kinesiology, Emphasis in Fitness Specialist, B.S. - San Diego State University.html: no program id in the page; matched by its title to poid 12005

| major_id | Name | Degree | Rows | Review items |
| --- | --- | --- | --- | --- |
| `me_bs` | Mechanical Engineering | B.S. | 52 | 5 |
| `aerospace_engineering_bs` | Aerospace Engineering | B.S. | 47 | 4 |
| `biology_ba` | Biology | B.A. | 26 | 10 |
| `biology_bs` | Biology | B.S. | 26 | 10 |
| `biology_cellular_molecular_bs` | Biology, Emphasis in Cellular and Molecular Biology | B.S. | 54 | 11 |
| `biology_ecology_bs` | Biology, Emphasis in Ecology | B.S. | 46 | 11 |
| `biology_evolutionary_bs` | Biology, Emphasis in Evolutionary Biology | B.S. | 44 | 10 |
| `biology_marine_bs` | Biology, Emphasis in Marine Biology | B.S. | 35 | 10 |
| `biology_zoology_bs` | Biology, Emphasis in Zoology | B.S. | 40 | 9 |
| `ba_accounting_bs` | Business Administration, Emphasis in Accounting | B.S. | 27 | 2 |
| `ba_finance_bs` | Business Administration, Emphasis in Finance | B.S. | 25 | 2 |
| `ba_financial_services_bs` | Business Administration, Emphasis in Financial Services | B.S. | 42 | 3 |
| `ba_information_systems_bs` | Business Administration, Emphasis in Information Systems | B.S. | 36 | 1 |
| `ba_management_bs` | Business Administration, Emphasis in Management | B.S. | 44 | 1 |
| `ba_marketing_bs` | Business Administration, Emphasis in Marketing | B.S. | 51 | 6 |
| `ba_real_estate_bs` | Business Administration, Emphasis in Real Estate | B.S. | 25 | 1 |
| `ba_management_entrepreneurship_bs` | Business Administration, Management, Specialization in Entrepreneurship | B.S. | 34 | 1 |
| `ba_management_human_resource_management_bs` | Business Administration, Management, Specialization in Human Resource Management | B.S. | 32 | 1 |
| `chemistry_ba` | Chemistry | B.A. | 24 | 4 |
| `chemistry_american_chemical_society_bs` | Chemistry, and Certificate of the American Chemical Society | B.S. | 26 | 6 |
| `chemistry_biochemistry_american_chemical_society_bs` | Chemistry, Emphasis in Biochemistry, and Certificate of the American Chemical Society | B.S. | 39 | 6 |
| `civil_engineering_bs` | Civil Engineering | B.S. | 55 | 2 |
| `communication_ba` | Communication | B.A. | 49 | 10 |
| `computer_engineering_bs` | Computer Engineering | B.S. | 46 | 2 |
| `construction_engineering_bs` | Construction Engineering | B.S. | 46 | 5 |
| `electrical_engineering_bs` | Electrical Engineering | B.S. | 55 | 3 |
| `environmental_engineering_bs` | Environmental Engineering | B.S. | 40 | 1 |
| `health_communication_bs` | Health Communication | B.S. | 41 | 8 |
| `kinesiology_exercise_science_generalist_bs` | Kinesiology, Emphasis in Exercise Science Generalist | B.S. | 29 | 4 |
| `kinesiology_fitness_specialist_bs` | Kinesiology, Emphasis in Fitness Specialist | B.S. | 37 | 2 |
| `mechanical_engineering_bioengineering_bs` | Mechanical Engineering, Emphasis in Bioengineering | B.S. | 40 | 2 |
| `psychology_industrial_organizational_ba` | Psychology, Emphasis in Industrial and Organizational Psychology | B.A. | 27 | 8 |
| `psychology_neuroscience_ba` | Psychology, Emphasis in Neuroscience | B.A. | 30 | 9 |

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

## Aerospace Engineering, B.S. (`aerospace_engineering_bs`)

- Source: `data/catalog_html/Program_ Aerospace Engineering, B.S. - San Diego State University.html`, poid 11888, major code 09021
- Rows: 47

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 11: A E 123, A E 260, A E 280, E E 204, MATH 150, MATH 151, MATH 252, M E 190, PHYS 195, PHYS 195L, PHYS 196 |
| Preparation for the Major | AE 200 / ME 200 (same course, pick 1) | choose 1 | 2: A E 200, M E 200 |
| Preparation for the Major | AE 220 / ME 220 (same course, pick 1) | choose 1 | 2: A E 220, M E 220 |
| Preparation for the Major | BIOL 100 or BIOL 101 (pick 1) | choose 1 | 2: BIOL 100, BIOL 101 |
| Preparation for the Major | CHEM 202 or CHEM 200 (pick 1) | choose 1 | 2: CHEM 202, CHEM 200 |
| Major | Required | required | 15: A E 301, A E 302, A E 303, A E 310, A E 320, A E 331, A E 340, A E 341, A E 403W, A E 410, A E 430, A E 440, A E 460A, A E 460B, CIV E 302 |
| Major | CIVE 301 or ME 304 (pick 1) | choose 1 | 2: CIV E 301, M E 304 |
| Major Electives | Major Electives | pool, 6 units | 10: A E 510, A E 515, A E 520, A E 530, A E 535, M E 535, A E 540, A E 546, A E 550, A E 596 |

### Section notes (shown once under the heading)

- **Major Electives**: Other electives may be substituted with consent of the advisor and department chair

### Review list

- [ ] CIVE 301 or ME 304 (pick 1) in Major: the 'or' sits next to other courses with no break, so it may cover more than one course. Check the catalog page.
- [ ] 'Major Electives': rule text kept as the section note, check it: "Other electives may be substituted with consent of the advisor and department chair."
- [ ] AE 535 / ME 535 (same course, pick 1) in the 'Major Electives' pool: kept as pool rows with a note (a pick-1 group inside a units pool would be counted on its own).
- [ ] 'Major Electives' (under Major) asks for 6 units of its list: encoded as a pool in its own section 'Major Electives', check it.

### Units check (advisory)

- Preparation for the Major: page says 44 units, listed courses give 44-45: **overlaps**
- Major: page says at least 49 units, listed courses give 49: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - Students majoring in Aerospace Engineering must include in their program a sequence of fundamental courses. In addition, the students have the opportunity to satisfy their particular areas of interest by selecting a pattern of study indicated in the sequence below. This pattern includes typical aerospace engineering topics, such as aerospace vehicle design, structural analysis, aerodynamics, and propulsion.
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
- **Impacted Program**
  - The Aerospace Engineering major is an impacted program. To be admitted to the major, students must meet the following impaction criteria:
  - Complete with a grade of C (2.0) or better: A E 200 [or M E 200]; CHEM 202 (or CHEM 200); MATH 150, MATH 151; PHYS 195, PHYS 196. These courses cannot be taken for credit/no credit (Cr/NC);
  - Have an overall cumulative GPA of 2.7.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Major Restriction for Registration**
  - You must be in the Major (cleared impaction requirements) in order to take the upper level (300-400+) courses. This rule does not apply for the courses A E 340 and A E 341.
- **General Education**
  - Engineering majors automatically satisfy Area 2/5. Mathematical Concepts and Quantitative Reasoning or Physical and Biological Sciences and Area 4. Social and Behavioral Explorations GE areas by completion of the major.
- **Graduation Writing Assessment Requirement**
  - Complete A E 403W with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Master Plan**
  - The master plan must be reviewed each semester with the major advisor before registration. All course substitutions must be approved by the department chair. The master plan provides an advising record for aerospace engineering majors and should be initiated by the student with their major advisor during the second semester of the first year. All students must have a master plan on file in the department prior to enrollment in: Courses listed: A E 301, A E 310.

### Coverage (sections in data/cleaned)

- Required courses: 25 of 26 have sections
  - with sections: A E 123 (1), A E 260 (1), A E 280 (3), E E 204 (1), MATH 150 (12), MATH 151 (20), MATH 252 (13), M E 190 (12), PHYS 195 (2), PHYS 195L (17), PHYS 196 (1), A E 301 (1), A E 302 (1), A E 303 (4), A E 310 (1), A E 320 (1), A E 331 (1), A E 340 (2), A E 341 (9), A E 403W (4), A E 410 (1), A E 430 (1), A E 440 (1), A E 460B (2), CIV E 302 (5)
  - no sections: A E 460A
- Pick-n group courses: 10 of 10 have sections
  - with sections: A E 200 (3), M E 200 (3), A E 220 (1), M E 220 (5), BIOL 100 (4), BIOL 101 (1), CHEM 202 (11), CHEM 200 (49), CIV E 301 (3), M E 304 (3)
- Elective pool courses: 5 of 10 have sections
  - with sections: A E 510 (1), A E 520 (1), A E 530 (1), A E 535 (1), A E 596 (1)
  - no sections: A E 515, M E 535, A E 540, A E 546, A E 550

### Title differences (catalog vs class data)

- A E 535: catalog "Mechanics of Composite Structures", class data "Mech of Composites Struct"
- 15 more only shortened in the class data (not a real difference): A E 260, E E 204, CHEM 202, A E 310, A E 341, A E 403W, A E 410, A E 430, A E 440, A E 460B, CIV E 302, CIV E 301, A E 510, A E 520, A E 596

## Biology, B.A. (`biology_ba`)

- Source: `data/catalog_html/Program_ Biology, B.A. - San Diego State University.html`, poid 11918, major code 04011
- Rows: 26

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 10: BIOL 203, BIOL 203L, BIOL 204, BIOL 204L, BIOL 215, CHEM 200, CHEM 201, CHEM 232, CHEM 232L, MATH 124 |
| Major | Required | required | 10: PHYS 180A, PHYS 180B, PHYS 182A, PHYS 182B, BIOL 351, BIOL 352, BIOL 354, BIOL 366, BIOL 366L, CHEM 365 |
| Major | At Least One Course Selected From (pick 1) | choose 1 | 3: BIOL 350, BIOL 459, BIOL 462 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Students must have a cumulative GPA of 2.80 or better to be admitted to the major
- **Major**: All courses not included below must have specific approval of the department. This approval must be filed with the Office of the Registrar. Upper Division Major Electives: Upper division major elective courses include all upper division biology courses numbered 350 and above (except BIOL 497 and BIOL 495 ), and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , CHEM 560 ). Laboratory Course Requirement: A minimum of two upper division major elective courses must be biology laboratory courses
- **Language Requirement**: Competency (successfully completing the third college semester or fifth college quarter) is required in one language other than English to fulfill this requirement

### Review list

- [ ] 'Preparation for the Major': rule text kept as the section note: "Students must have a cumulative GPA of 2.80 or better to be admitted to the major."
- [ ] 'Language Requirement' has no courses; shown as a section with only its note: "Competency (successfully completing the third college semester or fifth college quarter) is required in one language other than English to fulfill this requirement."
- [ ] 'Major': rule text kept as the section note: "All courses not included below must have specific approval of the department."
- [ ] 'Major': rule text kept as the section note: "This approval must be filed with the Office of the Registrar."
- [ ] Text under 'Major' left out (no rule in it; in the report only): "All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval."
- [ ] 'At Least One Course Selected From (pick 1)' in Major: read as pick 1 of 3; check it.
- [ ] Text under 'Upper Division Major Electives' kept as the 'Major' section note: "Upper division major elective courses include all upper division biology courses numbered 350 and above (except BIOL 497 and BIOL 495 ), and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , CHEM 560 )."
- [ ] Text under 'Laboratory Course Requirement' kept as the 'Major' section note: "A minimum of two upper division major elective courses must be biology laboratory courses."
- [ ] Text under 'Laboratory Course Requirement' left out (no rule in it; in the report only): "One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement."
- [ ] Units check for Major: page says 32, listed courses add up to 28-29.

### Units check (advisory)

- Preparation for the Major: page says 29 units, listed courses give 29: **inside**
- Major: page says 32 units, listed courses give 28-29: **MISMATCH**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - A minor is not required with this major.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Graduation Writing Assessment Requirement**
  - Complete one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval.
- **Major: Upper Division Major Electives**
  - Upper division major elective courses include all upper division biology courses numbered 350 and above (except BIOL 497 and BIOL 495 ), and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , CHEM 560 ).
- **Major: Laboratory Course Requirement**
  - A minimum of two upper division major elective courses must be biology laboratory courses.
  - One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement.
- **Time Limitation**
  - All courses for the major must be completed within seven years of the granting of the undergraduate degree. Exceptions for individual courses must be approved by the department and be filed with the Office of the Registrar.

### Coverage (sections in data/cleaned)

- Required courses: 20 of 20 have sections
  - with sections: BIOL 203 (2), BIOL 203L (22), BIOL 204 (4), BIOL 204L (16), BIOL 215 (11), CHEM 200 (49), CHEM 201 (19), CHEM 232 (1), CHEM 232L (14), MATH 124 (9), PHYS 180A (1), PHYS 180B (1), PHYS 182A (16), PHYS 182B (9), BIOL 351 (11), BIOL 352 (9), BIOL 354 (1), BIOL 366 (1), BIOL 366L (6), CHEM 365 (1)
- Pick-n group courses: 1 of 3 have sections
  - with sections: BIOL 350 (8)
  - no sections: BIOL 459, BIOL 462

### Title differences (catalog vs class data)

- none
- 5 more only shortened in the class data (not a real difference): BIOL 204, BIOL 204L, CHEM 232L, BIOL 354, CHEM 365

## Biology, B.S. (`biology_bs`)

- Source: `data/catalog_html/Program_ Biology, B.S. - San Diego State University.html`, poid 11919, major code 04011
- Rows: 26

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 10: BIOL 203, BIOL 203L, BIOL 204, BIOL 204L, BIOL 215, CHEM 200, CHEM 201, CHEM 232, CHEM 232L, MATH 124 |
| Major | Required | required | 10: PHYS 180A, PHYS 180B, PHYS 182A, PHYS 182B, BIOL 351, BIOL 352, BIOL 354, BIOL 366, BIOL 366L, CHEM 365 |
| Major | At Least One Course Selected From (pick 1) | choose 1 | 3: BIOL 350, BIOL 459, BIOL 462 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Students must have a cumulative GPA of 2.80 or better to be admitted to the major
- **Major**: All courses not included below must have specific approval of the department. This approval must be filed with the Office of the Registrar
- **Upper Division Major Electives**: Laboratory Course Requirement: A minimum of two upper division major elective courses must be biology laboratory courses

### Review list

- [ ] 'Preparation for the Major': rule text kept as the section note: "Students must have a cumulative GPA of 2.80 or better to be admitted to the major."
- [ ] 'Major': rule text kept as the section note: "All courses not included below must have specific approval of the department."
- [ ] 'Major': rule text kept as the section note: "This approval must be filed with the Office of the Registrar."
- [ ] Text under 'Major' left out (no rule in it; in the report only): "All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval."
- [ ] 'At Least One Course Selected From (pick 1)' in Major: read as pick 1 of 3; check it.
- [ ] 'Upper Division Major Electives' (under Major) is a rule in words, encoded as one pool; check it. Catalog: "Upper division major elective courses include all upper division biology courses numbered 350 and above; BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , CHEM 560 )."
- [ ] Text under 'Laboratory Course Requirement' kept as the 'Upper Division Major Electives' section note: "A minimum of two upper division major elective courses must be biology laboratory courses."
- [ ] Text under 'Laboratory Course Requirement' left out (no rule in it; in the report only): "One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement."
- [ ] 'Upper Division Major Electives' has a rule but no course lists followed it: Upper division major elective courses include all upper division biology courses numbered 350 and above; BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , CHEM 560 ).
- [ ] Units check for Major: page says 44, listed courses add up to 28-29.

### Units check (advisory)

- Preparation for the Major: page says 29 units, listed courses give 29: **inside**
- Major: page says 44 units, listed courses give 28-29: **MISMATCH**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - A minor is not required with this major.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Graduation Writing Assessment Requirement**
  - Complete one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval.
- **Major: Laboratory Course Requirement**
  - A minimum of two upper division major elective courses must be biology laboratory courses.
  - One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement.
- **Time Limitation**
  - All courses for the major must be completed within seven years of the granting of the undergraduate degree. Exceptions for individual courses must be approved by the department and be filed with the Office of the Registrar.

### Coverage (sections in data/cleaned)

- Required courses: 20 of 20 have sections
  - with sections: BIOL 203 (2), BIOL 203L (22), BIOL 204 (4), BIOL 204L (16), BIOL 215 (11), CHEM 200 (49), CHEM 201 (19), CHEM 232 (1), CHEM 232L (14), MATH 124 (9), PHYS 180A (1), PHYS 180B (1), PHYS 182A (16), PHYS 182B (9), BIOL 351 (11), BIOL 352 (9), BIOL 354 (1), BIOL 366 (1), BIOL 366L (6), CHEM 365 (1)
- Pick-n group courses: 1 of 3 have sections
  - with sections: BIOL 350 (8)
  - no sections: BIOL 459, BIOL 462

### Title differences (catalog vs class data)

- none
- 5 more only shortened in the class data (not a real difference): BIOL 204, BIOL 204L, CHEM 232L, BIOL 354, CHEM 365

## Biology, Emphasis in Cellular and Molecular Biology, B.S. (`biology_cellular_molecular_bs`)

- Source: `data/catalog_html/Program_ Biology, Emphasis in Cellular and Molecular Biology, B.S. - San Diego State University.html`, poid 11920, major code 04011
- Rows: 54

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 10: BIOL 203, BIOL 203L, BIOL 204, BIOL 204L, BIOL 215, CHEM 200, CHEM 201, CHEM 232, CHEM 232L, MATH 124 |
| Major | Required | required | 11: PHYS 180A, PHYS 180B, PHYS 182A, PHYS 182B, BIOL 351, BIOL 352, BIOL 354, BIOL 366, BIOL 366L, BIOL 567, CHEM 365 |
| Major | At Least One Course Selected From (pick 1) | choose 1 | 3: BIOL 350, BIOL 459, BIOL 462 |
| Major | Upper Division Major Electives (pick 2) | choose 2 | 28: BIOL 350, BIOL 464, BIOL 480, BIOL 510, BIOL 528, BIOL 549, BIOL 554, BIOL 556, BIOL 557, BIOL 562, BIOL 564, BIOL 565, BIOL 567L, BIOL 568, BIOMI 568, BIOL 570, BIOL 575, BIOL 576, BIOL 584, BIOL 485, BIOL 585, BIOL 589, BIOL 590, CHEM 432, BIOL 496, CHEM 496, BIOL 596, CHEM 596 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Students must have a cumulative GPA of 2.80 or better to be admitted to the major
- **Major**: All courses not included below must have specific approval of the department. This approval must be filed with the Office of the Registrar. Laboratory Course Requirement: A minimum of two upper division major elective courses must be biology laboratory courses. Other electives include all biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 ). Prior approval from the Biology advisor is required to allow the following courses to fulfill required elective coursework. (BIOL 496, BIOL 596, CHEM 496, CHEM 498, CHEM 499, CHEM 596)

### Review list

- [ ] 'Preparation for the Major': rule text kept as the section note: "Students must have a cumulative GPA of 2.80 or better to be admitted to the major."
- [ ] 'Major': rule text kept as the section note: "All courses not included below must have specific approval of the department."
- [ ] 'Major': rule text kept as the section note: "This approval must be filed with the Office of the Registrar."
- [ ] Text under 'Major' left out (no rule in it; in the report only): "All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval."
- [ ] 'At Least One Course Selected From (pick 1)' in Major: read as pick 1 of 3; check it.
- [ ] 'Upper Division Major Electives (pick 2)' in Major: read as pick 2, its or / also-listed-as pairs kept with a note; check it.
- [ ] Text under 'Laboratory Course Requirement' kept as the 'Major' section note: "A minimum of two upper division major elective courses must be biology laboratory courses."
- [ ] Text under 'Laboratory Course Requirement' left out (no rule in it; in the report only): "One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement."
- [ ] Text under 'Note' kept as the 'Major' section note: "Other electives include all biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 )."
- [ ] 'Approval of the Emphasis': courses that count only with approval, not a requirement: a section note (BIOL 496, BIOL 596, CHEM 496, CHEM 498, CHEM 499, CHEM 596).
- [ ] Units check for Major: page says 44, listed courses add up to 34-41.

### Units check (advisory)

- Preparation for the Major: page says 29 units, listed courses give 29: **inside**
- Major: page says 44 units, listed courses give 34-41: **MISMATCH**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - A minor is not required with this major.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Graduation Writing Assessment Requirement**
  - Complete one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval.
- **Major: Laboratory Course Requirement**
  - A minimum of two upper division major elective courses must be biology laboratory courses.
  - One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement.
- **Major: Note**
  - Other electives include all biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 ).
- **Time Limitation**
  - All courses for the major must be completed within seven years of the granting of the undergraduate degree. Exceptions for individual courses must be approved by the department advisor and be filed with the Office of the Registrar.

### Coverage (sections in data/cleaned)

- Required courses: 21 of 21 have sections
  - with sections: BIOL 203 (2), BIOL 203L (22), BIOL 204 (4), BIOL 204L (16), BIOL 215 (11), CHEM 200 (49), CHEM 201 (19), CHEM 232 (1), CHEM 232L (14), MATH 124 (9), PHYS 180A (1), PHYS 180B (1), PHYS 182A (16), PHYS 182B (9), BIOL 351 (11), BIOL 352 (9), BIOL 354 (1), BIOL 366 (1), BIOL 366L (6), BIOL 567 (1), CHEM 365 (1)
- Pick-n group courses: 12 of 30 have sections
  - with sections: BIOL 350 (8), BIOL 480 (1), BIOL 554 (1), BIOL 564 (2), BIOL 567L (2), BIOL 570 (1), BIOL 576 (1), BIOL 584 (1), BIOL 485 (1), CHEM 432 (1), BIOL 596 (1), CHEM 596 (1)
  - no sections: BIOL 459, BIOL 462, BIOL 464, BIOL 510, BIOL 528, BIOL 549, BIOL 556, BIOL 557, BIOL 562, BIOL 565, BIOL 568, BIOMI 568, BIOL 575, BIOL 585, BIOL 589, BIOL 590, BIOL 496, CHEM 496

### Title differences (catalog vs class data)

- BIOL 596: catalog "Special Topics in Biology", class data "Biol Systems Engineering"
- 9 more only shortened in the class data (not a real difference): BIOL 204, BIOL 204L, CHEM 232L, BIOL 354, BIOL 567, CHEM 365, BIOL 564, BIOL 567L, CHEM 596

## Biology, Emphasis in Ecology, B.S. (`biology_ecology_bs`)

- Source: `data/catalog_html/Program_ Biology, Emphasis in Ecology, B.S. - San Diego State University.html`, poid 11921, major code 04011
- Rows: 46

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 10: BIOL 203, BIOL 203L, BIOL 204, BIOL 204L, BIOL 215, CHEM 200, CHEM 201, CHEM 232, CHEM 232L, MATH 124 |
| Major | Required | required | 11: PHYS 180A, PHYS 180B, PHYS 182A, PHYS 182B, BIOL 351, BIOL 352, BIOL 354, BIOL 358, BIOL 366, BIOL 366L, CHEM 365 |
| Major | At Least One Course Selected From (pick 1) | choose 1 | 3: BIOL 350, BIOL 459, BIOL 462 |
| Major | Upper Division Major Electives (pick 2) | choose 2 | 20: BIOL 509, BIOL 512, BIOL 514, BIOL 516A, BIOL 516B, BIOL 517, BIOL 518, BIOL 526, BIOL 527, BIOL 528, BIOL 535, BIOL 540, BIOL 542, BIOL 544, ENV S 544, BIOL 560, BIOL 562, BIOL 578, BIOL 496, BIOL 596 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Students must have a cumulative GPA of 2.80 or better to be admitted to the major
- **Major**: This approval must be filed with the Office of the Registrar. Laboratory Course Requirement: A minimum of two upper division major elective courses must be biology laboratory courses. Other upper division major electives include all biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 ). Prior approval from the Biology advisor is required to allow the following courses to fulfill required elective coursework. (BIOL 496, BIOL 596)

### Review list

- [ ] 'Preparation for the Major': rule text kept as the section note: "Students must have a cumulative GPA of 2.80 or better to be admitted to the major."
- [ ] Text under 'Preparation for the Major' left out (no rule in it; in the report only): "A computer programming course (e.g. CS 150 and CS 150L ) is recommended."
- [ ] 'Major': rule text kept as the section note: "This approval must be filed with the Office of the Registrar."
- [ ] Text under 'Major' left out (no rule in it; in the report only): "All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval."
- [ ] 'At Least One Course Selected From (pick 1)' in Major: read as pick 1 of 3; check it.
- [ ] 'Upper Division Major Electives (pick 2)' in Major: read as pick 2 of 20; check it.
- [ ] Text under 'Laboratory Course Requirement' kept as the 'Major' section note: "A minimum of two upper division major elective courses must be biology laboratory courses."
- [ ] Text under 'Laboratory Course Requirement' left out (no rule in it; in the report only): "One three-unit semester of BIOL 597 or BIOL 497 (but not both) may fulfill one laboratory requirement."
- [ ] Text under 'Note' kept as the 'Major' section note: "Other upper division major electives include all biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 )."
- [ ] 'Approval of the Emphasis': courses that count only with approval, not a requirement: a section note (BIOL 496, BIOL 596).
- [ ] Units check for Major: page says 44, listed courses add up to 32-39.

### Units check (advisory)

- Preparation for the Major: page says 29 units, listed courses give 29: **inside**
- Major: page says 44 units, listed courses give 32-39: **MISMATCH**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - A minor is not required with this major.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Preparation for the Major**
  - A computer programming course (e.g.
  - CS 150 and CS 150L ) is recommended.
- **Graduation Writing Assessment Requirement**
  - Complete one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval.
- **Major: Laboratory Course Requirement**
  - A minimum of two upper division major elective courses must be biology laboratory courses.
  - One three-unit semester of BIOL 597 or BIOL 497 (but not both) may fulfill one laboratory requirement.
- **Major: Note**
  - Other upper division major electives include all biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 ).
- **Time Limitation**
  - All courses for the major must be completed within seven years of the granting of the undergraduate degree. Exceptions for individual courses must be approved by the department advisor and be filed with the Office of the Registrar.

### Coverage (sections in data/cleaned)

- Required courses: 21 of 21 have sections
  - with sections: BIOL 203 (2), BIOL 203L (22), BIOL 204 (4), BIOL 204L (16), BIOL 215 (11), CHEM 200 (49), CHEM 201 (19), CHEM 232 (1), CHEM 232L (14), MATH 124 (9), PHYS 180A (1), PHYS 180B (1), PHYS 182A (16), PHYS 182B (9), BIOL 351 (11), BIOL 352 (9), BIOL 354 (1), BIOL 358 (6), BIOL 366 (1), BIOL 366L (6), CHEM 365 (1)
- Pick-n group courses: 8 of 23 have sections
  - with sections: BIOL 350 (8), BIOL 512 (2), BIOL 517 (2), BIOL 526 (2), BIOL 535 (2), BIOL 544 (1), ENV S 544 (1), BIOL 596 (1)
  - no sections: BIOL 459, BIOL 462, BIOL 509, BIOL 514, BIOL 516A, BIOL 516B, BIOL 518, BIOL 527, BIOL 528, BIOL 540, BIOL 542, BIOL 560, BIOL 562, BIOL 578, BIOL 496

### Title differences (catalog vs class data)

- BIOL 526: catalog "Terrestrial Arthropod Biology", class data "Terrestrial Arthropods"
- BIOL 596: catalog "Special Topics in Biology", class data "Biol Systems Engineering"
- 8 more only shortened in the class data (not a real difference): BIOL 204, BIOL 204L, CHEM 232L, BIOL 354, CHEM 365, BIOL 512, BIOL 544, ENV S 544

## Biology, Emphasis in Evolutionary Biology, B.S. (`biology_evolutionary_bs`)

- Source: `data/catalog_html/Program_ Biology, Emphasis in Evolutionary Biology, B.S. - San Diego State University.html`, poid 11922, major code 4011
- Rows: 44

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 10: BIOL 203, BIOL 203L, BIOL 204, BIOL 204L, BIOL 215, CHEM 200, CHEM 201, CHEM 232, CHEM 232L, MATH 124 |
| Major | Required | required | 11: PHYS 180A, PHYS 180B, PHYS 182A, PHYS 182B, BIOL 351, BIOL 352, BIOL 354, BIOL 366, BIOL 366L, BIOL 509, CHEM 365 |
| Major | At Least One Course Selected From (pick 1) | choose 1 | 3: BIOL 350, BIOL 459, BIOL 462 |
| Major | Upper Division Major Electives (pick 2) | choose 2 | 18: BIOL 459, BIOL 510, BIOL 512, BIOL 515, BIOL 518, BIOL 523, BIOL 524, BIOL 525, BIOL 526, BIOL 527, BIOL 528, BIOL 530, BIOL 531, BIOL 568, BIOMI 568, BIOL 576, BIOL 496, BIOL 596 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Students must have a cumulative GPA of 2.80 or better to be admitted to the major
- **Major**: This approval must be filed with the Office of the Registrar. Laboratory Course Requirement: A minimum of two upper division elective courses must be biology laboratory courses. Other electives include all biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 ). Prior approval from the Biology advisor is required to allow the following courses to fulfill required elective coursework. (BIOL 597, BIOL 496, BIOL 497, BIOL 596)

### Review list

- [ ] 'Preparation for the Major': rule text kept as the section note: "Students must have a cumulative GPA of 2.80 or better to be admitted to the major."
- [ ] 'Major': rule text kept as the section note: "This approval must be filed with the Office of the Registrar."
- [ ] Text under 'Major' left out (no rule in it; in the report only): "All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval."
- [ ] 'At Least One Course Selected From (pick 1)' in Major: read as pick 1 of 3; check it.
- [ ] 'Upper Division Major Electives (pick 2)' in Major: read as pick 2 of 18; check it.
- [ ] Text under 'Laboratory Course Requirement' kept as the 'Major' section note: "A minimum of two upper division elective courses must be biology laboratory courses."
- [ ] Text under 'Laboratory Course Requirement' left out (no rule in it; in the report only): "One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement."
- [ ] Text under 'Note' kept as the 'Major' section note: "Other electives include all biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 )."
- [ ] 'Approval of the Emphasis': courses that count only with approval, not a requirement: a section note (BIOL 597, BIOL 496, BIOL 497, BIOL 596).
- [ ] Units check for Major: page says 44, listed courses add up to 33-40.

### Units check (advisory)

- Preparation for the Major: page says 29 units, listed courses give 29: **inside**
- Major: page says 44 units, listed courses give 33-40: **MISMATCH**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - A minor is not required with this major.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Graduation Writing Assessment Requirement**
  - Complete one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval.
- **Major: Laboratory Course Requirement**
  - A minimum of two upper division elective courses must be biology laboratory courses.
  - One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement.
- **Major: Note**
  - Other electives include all biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 ).
- **Time Limitation**
  - All courses for the major must be completed within seven years of the granting of the undergraduate degree. Exceptions for individual courses must be approved by the department advisor and be filed with the Office of the Registrar.

### Coverage (sections in data/cleaned)

- Required courses: 20 of 21 have sections
  - with sections: BIOL 203 (2), BIOL 203L (22), BIOL 204 (4), BIOL 204L (16), BIOL 215 (11), CHEM 200 (49), CHEM 201 (19), CHEM 232 (1), CHEM 232L (14), MATH 124 (9), PHYS 180A (1), PHYS 180B (1), PHYS 182A (16), PHYS 182B (9), BIOL 351 (11), BIOL 352 (9), BIOL 354 (1), BIOL 366 (1), BIOL 366L (6), CHEM 365 (1)
  - no sections: BIOL 509
- Pick-n group courses: 8 of 20 have sections
  - with sections: BIOL 350 (8), BIOL 512 (2), BIOL 523 (3), BIOL 524 (2), BIOL 526 (2), BIOL 530 (2), BIOL 576 (1), BIOL 596 (1)
  - no sections: BIOL 459, BIOL 462, BIOL 510, BIOL 515, BIOL 518, BIOL 525, BIOL 527, BIOL 528, BIOL 531, BIOL 568, BIOMI 568, BIOL 496

### Title differences (catalog vs class data)

- BIOL 526: catalog "Terrestrial Arthropod Biology", class data "Terrestrial Arthropods"
- BIOL 596: catalog "Special Topics in Biology", class data "Biol Systems Engineering"
- 6 more only shortened in the class data (not a real difference): BIOL 204, BIOL 204L, CHEM 232L, BIOL 354, CHEM 365, BIOL 512

## Biology, Emphasis in Marine Biology, B.S. (`biology_marine_bs`)

- Source: `data/catalog_html/Program_ Biology, Emphasis in Marine Biology, B.S. - San Diego State University.html`, poid 11923, major code 04011
- Rows: 35

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 10: BIOL 203, BIOL 203L, BIOL 204, BIOL 204L, BIOL 215, CHEM 200, CHEM 201, CHEM 232, CHEM 232L, MATH 124 |
| Major | Required | required | 10: PHYS 180A, PHYS 180B, PHYS 182A, PHYS 182B, BIOL 351, BIOL 352, BIOL 354, BIOL 366, BIOL 366L, CHEM 365 |
| Major | At Least One Course Selected From (pick 1) | choose 1 | 3: BIOL 350, BIOL 459, BIOL 462 |
| Major | Upper Division Major Electives (pick 2) | choose 2 | 10: BIOL 512, BIOL 514, BIOL 515, BIOL 516A, BIOL 516B, BIOL 517, BIOL 518, BIOL 542, BIOL 496, BIOL 596 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Students must have a cumulative GPA of 2.80 or better to be admitted to the major
- **Major**: This approval must be filed with the Office of the Registrar. Laboratory Course Requirement: A minimum of two upper division major elective courses must be biology laboratory courses. The remaining units must be selected from biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 ). Prior approval from the Biology advisor is required to allow the following courses to fulfill required elective coursework. (BIOL 597, BIOL 496, BIOL 497, BIOL 596)

### Review list

- [ ] 'Preparation for the Major': rule text kept as the section note: "Students must have a cumulative GPA of 2.80 or better to be admitted to the major."
- [ ] 'Major': rule text kept as the section note: "This approval must be filed with the Office of the Registrar."
- [ ] Text under 'Major' left out (no rule in it; in the report only): "All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval."
- [ ] 'At Least One Course Selected From (pick 1)' in Major: read as pick 1 of 3; check it.
- [ ] 'Upper Division Major Electives (pick 2)' in Major: read as pick 2 of 10; check it.
- [ ] Text under 'Laboratory Course Requirement' kept as the 'Major' section note: "A minimum of two upper division major elective courses must be biology laboratory courses."
- [ ] Text under 'Laboratory Course Requirement' left out (no rule in it; in the report only): "One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement."
- [ ] Text under 'Note' kept as the 'Major' section note: "The remaining units must be selected from biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 )."
- [ ] 'Approval of the Emphasis': courses that count only with approval, not a requirement: a section note (BIOL 597, BIOL 496, BIOL 497, BIOL 596).
- [ ] Units check for Major: page says 44, listed courses add up to 30-37.

### Units check (advisory)

- Preparation for the Major: page says 29 units, listed courses give 29: **inside**
- Major: page says 44 units, listed courses give 30-37: **MISMATCH**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - A minor is not required with this major.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Graduation Writing Assessment Requirement**
  - Complete one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval.
- **Major: Laboratory Course Requirement**
  - A minimum of two upper division major elective courses must be biology laboratory courses.
  - One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement.
- **Major: Note**
  - The remaining units must be selected from biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 ).
- **Time Limitation**
  - All courses for the major must be completed within seven years of the granting of the undergraduate degree. Exceptions for individual courses must be approved by the department advisor and be filed with the Office of the Registrar.

### Coverage (sections in data/cleaned)

- Required courses: 20 of 20 have sections
  - with sections: BIOL 203 (2), BIOL 203L (22), BIOL 204 (4), BIOL 204L (16), BIOL 215 (11), CHEM 200 (49), CHEM 201 (19), CHEM 232 (1), CHEM 232L (14), MATH 124 (9), PHYS 180A (1), PHYS 180B (1), PHYS 182A (16), PHYS 182B (9), BIOL 351 (11), BIOL 352 (9), BIOL 354 (1), BIOL 366 (1), BIOL 366L (6), CHEM 365 (1)
- Pick-n group courses: 4 of 13 have sections
  - with sections: BIOL 350 (8), BIOL 512 (2), BIOL 517 (2), BIOL 596 (1)
  - no sections: BIOL 459, BIOL 462, BIOL 514, BIOL 515, BIOL 516A, BIOL 516B, BIOL 518, BIOL 542, BIOL 496

### Title differences (catalog vs class data)

- BIOL 596: catalog "Special Topics in Biology", class data "Biol Systems Engineering"
- 6 more only shortened in the class data (not a real difference): BIOL 204, BIOL 204L, CHEM 232L, BIOL 354, CHEM 365, BIOL 512

## Biology, Emphasis in Zoology, B.S. (`biology_zoology_bs`)

- Source: `data/catalog_html/Program_ Biology, Emphasis in Zoology, B.S. - San Diego State University.html`, poid 11924
- Rows: 40

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 10: BIOL 203, BIOL 203L, BIOL 204, BIOL 204L, BIOL 215, CHEM 200, CHEM 201, CHEM 232, CHEM 232L, MATH 124 |
| Major | Required | required | 11: PHYS 180A, PHYS 180B, PHYS 182A, PHYS 182B, BIOL 351, BIOL 352, BIOL 354, BIOL 366, BIOL 366L, BIOL 462, CHEM 365 |
| Major | Upper Division Major Electives (pick 2) | choose 2 | 17: BIOL 509, BIOL 510, BIOL 512, BIOL 515, BIOL 516A, BIOL 518, BIOL 523, BIOL 524, BIOL 525, BIOL 526, BIOL 527, BIOL 540, BIOL 542, BIOL 560, BIOL 576, BIOL 496, BIOL 596 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Students must have a cumulative GPA of 2.80 or better to be admitted to the major
- **Major**: This approval must be filed with the Office of the Registrar. Laboratory Course Requirement: A minimum of two upper division major elective courses must be biology laboratory courses. The remaining units must be selected from biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 ). Prior approval from the Biology advisor is required to allow the following courses to fulfill required elective coursework. (BIOL 597, BIOL 496, BIOL 497, BIOL 596)

### Review list

- [ ] 'Preparation for the Major': rule text kept as the section note: "Students must have a cumulative GPA of 2.80 or better to be admitted to the major."
- [ ] 'Major': rule text kept as the section note: "This approval must be filed with the Office of the Registrar."
- [ ] Text under 'Major' left out (no rule in it; in the report only): "All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval."
- [ ] 'Upper Division Major Electives (pick 2)' in Major: read as pick 2 of 17; check it.
- [ ] Text under 'Laboratory Course Requirement' kept as the 'Major' section note: "A minimum of two upper division major elective courses must be biology laboratory courses."
- [ ] Text under 'Laboratory Course Requirement' left out (no rule in it; in the report only): "One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement."
- [ ] Text under 'Note' kept as the 'Major' section note: "The remaining units must be selected from biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 )."
- [ ] 'Approval of the Emphasis': courses that count only with approval, not a requirement: a section note (BIOL 597, BIOL 496, BIOL 497, BIOL 596).
- [ ] Units check for Major: page says 44, listed courses add up to 30-36.

### Units check (advisory)

- Preparation for the Major: page says 29 units, listed courses give 29: **inside**
- Major: page says 44 units, listed courses give 30-36: **MISMATCH**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - A minor is not required with this major.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major**
  - All upper division transfer courses in biology will calculate in the major GPA but will not fulfill any major requirements without specific department approval.
- **Major: Laboratory Course Requirement**
  - A minimum of two upper division major elective courses must be biology laboratory courses.
  - One three-unit semester of BIOL 597 or BIOL 497 may fulfill one laboratory requirement.
- **Major: Note**
  - The remaining units must be selected from biology courses numbered 350 and above (except BIOL 452 ); BIOL 597 , BIOL 497 , BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300 , CHEM 308 , CHEM 497 , CHEM 499 , and CHEM 560 ).
- **Time Limitation**
  - All courses for the major must be completed within seven years of the granting of the undergraduate degree. Exceptions for individual courses must be approved by the department advisor and be filed with the Office of the Registrar.

### Coverage (sections in data/cleaned)

- Required courses: 20 of 21 have sections
  - with sections: BIOL 203 (2), BIOL 203L (22), BIOL 204 (4), BIOL 204L (16), BIOL 215 (11), CHEM 200 (49), CHEM 201 (19), CHEM 232 (1), CHEM 232L (14), MATH 124 (9), PHYS 180A (1), PHYS 180B (1), PHYS 182A (16), PHYS 182B (9), BIOL 351 (11), BIOL 352 (9), BIOL 354 (1), BIOL 366 (1), BIOL 366L (6), CHEM 365 (1)
  - no sections: BIOL 462
- Pick-n group courses: 6 of 17 have sections
  - with sections: BIOL 512 (2), BIOL 523 (3), BIOL 524 (2), BIOL 526 (2), BIOL 576 (1), BIOL 596 (1)
  - no sections: BIOL 509, BIOL 510, BIOL 515, BIOL 516A, BIOL 518, BIOL 525, BIOL 527, BIOL 540, BIOL 542, BIOL 560, BIOL 496

### Title differences (catalog vs class data)

- BIOL 526: catalog "Terrestrial Arthropod Biology", class data "Terrestrial Arthropods"
- BIOL 596: catalog "Special Topics in Biology", class data "Biol Systems Engineering"
- 6 more only shortened in the class data (not a real difference): BIOL 204, BIOL 204L, CHEM 232L, BIOL 354, CHEM 365, BIOL 512

## Business Administration, Emphasis in Accounting, B.S. (`ba_accounting_bs`)

- Source: `data/catalog_html/Program_ Business Administration, Emphasis in Accounting, B.S. - San Diego State University.html`, poid 11880, major code 05021
- Rows: 27

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 7: ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MIS 180, MATH 120 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 15: ACCTG 331, ACCTG 332, ACCTG 333, ACCTG 334, ACCTG 390W, ACCTG 431, ACCTG 530, ACCTG 532, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370, MIS 301 |
| Upper Division Accountancy Electives | Any ACCTG 300-599 course | open, 6 units | 1: Any ACCTG 300-599 course |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Additional progress requirements must be met before a student is admitted to an upper division major
- **Major**: A “C” (2.0) average or better is required in the courses stipulated here for the major

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
- Rows: 25

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: FIN 240, ACCTG 201, ACCTG 202, ECON 101, ECON 102, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 12: FIN 321, FIN 325, FIN 327, FIN 423, ACCTG 326, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370 |
| Major | Any FIN 300-599 course | open, 9 units | 1: Any FIN 300-599 course |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Additional progress requirements must be met before a student is admitted to an upper division major
- **Major**: A C (2.0) average or better is required in the courses stipulated here for the major

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
- Rows: 42

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

- **Preparation for the Major**: Additional progress requirements must be met before a student is admitted to the upper division major
- **Major**: A grade point average of C (2.0) or better is required in the courses stipulated here for the major

### Review list

- [ ] Text under 'Major' left out (no rule in it; in the report only): "Students intending to pursue the Personal Financial Planning Certificate should refer to the certificate requirements when choosing their elective courses."
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
- Rows: 36

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: MIS 180, ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 13: MIS 301, MIS 306, MIS 315, MIS 380, MIS 383, MIS 460, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 12 units | 11: MIS 305, MIS 396W, MIS 401, MIS 420, MIS 425, MIS 429, MIS 455, MIS 481, MIS 495, MIS 515, MIS 585 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Additional progress requirements must be met before a student is admitted to the upper division major
- **Major**: A C (2.0) average or better is required in the courses stipulated here for the major

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
- Rows: 44

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 14: MGT 352, MGT 357, MGT 358, MGT 401, MGT 444, MGT 475, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370, MGT 405 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 6 units | 18: B A 404, MGT 353, MGT 403, MGT 420, MGT 422, MGT 452, MGT 455, MGT 459, MGT 460, MGT 461, MGT 462, MGT 463, MGT 464, MGT 466, MGT 467, MGT 468, MGT 483, MIS 301 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Additional progress requirements must be met before a student is admitted to the upper division major
- **Major**: A C (2.0) average or better is required in the courses stipulated here for the major

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
- Rows: 51

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

- **Preparation for the Major**: Additional progress requirements must be met before a student is admitted to the upper division major
- **Major**: A C (2.0) average or better is required in the courses stipulated here for the major
- **Upper Division Major Electives**: (6 units may be taken outside the Fowler College of Business by department chair approval)

### Review list

- [ ] Text under 'Major' left out (no rule in it; in the report only): "Marketing students may pursue various career objectives supported by pathways. These pathways include Brand Management, Customer Experience Management, Integrated Marketing Communications, Marketing Analytics and Intelligence, Professional Selling and Sales Leadership, Strategic Marketing Management, or Sustainable Marketing Management. Please visit the Marketing Department Website https://business.sdsu.edu/undergrad/marketing for specific pathway coursework options."
- [ ] 'Upper Division Major Electives': rule text kept as the section note, check it: "(6 units may be taken outside the Fowler College of Business by department chair approval)"
- [ ] BA 404 or MGT 405 (pick 1) in the 'Upper Division Major Electives' pool: kept as pool rows with a note (a pick-1 group inside a units pool would be counted on its own).
- [ ] 'Upper Division Major Electives' (under Major) asks for 14 units of its list: encoded as a pool in its own section 'Upper Division Major Electives', check it.
- [ ] "MKTG 490 may only be taken after completion of both MKTG 470 and MKTG 480." put on MKTG 490.
- [ ] "MKTG 491, 492, 493, or 494 may only be taken after completion of MKTG 371 and either MKTG 470 or MKTG 480." put on MKTG 491, MKTG 492, MKTG 493, MKTG 494.

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
- Rows: 25

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: FIN 240, ACCTG 201, ACCTG 202, ECON 101, ECON 102, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 12: FIN 331, FIN 333, FIN 431, FIN 433, FIN 435, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370 |
| Upper Division Major Electives | Any FIN 300-599 course | open, 9 units | 1: Any FIN 300-599 course |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Additional progress requirements must be met before a student is admitted to the upper division major
- **Major**: A C (2.0) average or better is required in the courses stipulated here for the major

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
- Rows: 34

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 14: MGT 358, MGT 401, MGT 420, MGT 444, MGT 460, MGT 475, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370, MGT 405 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 6 units | 8: MGT 353, MGT 422, MGT 452, MGT 455, MGT 459, MGT 470, JMS 480, MIS 301 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Additional progress requirements must be met before a student is admitted to the upper division major
- **Major**: A C (2.0) average or better is required in the courses stipulated here for the major

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
- Rows: 32

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 8: ACCTG 201, ACCTG 202, ECON 101, ECON 102, FIN 240, MIS 180, MATH 120, RWS 290 |
| Preparation for the Major | STAT 119 or ECON 201 (pick 1) | choose 1 | 2: STAT 119, ECON 201 |
| Major | Required | required | 14: MGT 352, MGT 401, MGT 444, MGT 461, MGT 462, MGT 475, B A 300, B A 305, B A 310, B A 323, B A 350, B A 360, B A 370, MGT 405 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 6 units | 6: MGT 463, MGT 464, MGT 466, MGT 467, MGT 468, MIS 301 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Additional progress requirements must be met before a student is admitted to the upper division major
- **Major**: A C (2.0) average or better is required in the courses stipulated here for the major

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

## Chemistry, B.A. (`chemistry_ba`)

- Source: `data/catalog_html/Program_ Chemistry, B.A. - San Diego State University.html`, poid 11940, major code 19051
- Rows: 24

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 14: CHEM 200, CHEM 201, CHEM 232, CHEM 232L, CHEM 251, BIOL 203, BIOL 203L, MATH 150, MATH 151, MATH 252, PHYS 195, PHYS 195L, PHYS 196, PHYS 196L |
| Major | Required | required | 7: CHEM 410A, CHEM 410B, CHEM 417, CHEM 432, CHEM 432L, CHEM 457, CHEM 550 |
| Major | Any CHEM 300-599 course | open, 7 units | 1: Any CHEM 300-599 course |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Recommended (not required): PHYS 197, PHYS 197L
- **Language Requirement**: Competency (successfully completing the third college semester or fifth college quarter) is required in one language other than English to fulfill the graduation requirement. Refer to section of this catalog on “Graduation Requirements .”

### Review list

- [ ] 'Recommended' list under 'Preparation for the Major' is not required: no rows, a section note (PHYS 197, PHYS 197L).
- [ ] 'Language Requirement' has no courses; shown as a section with only its note: "Competency (successfully completing the third college semester or fifth college quarter) is required in one language other than English to fulfill the graduation requirement. Refer to section of this catalog on “Graduation Requirements .”"
- [ ] 'Any CHEM 300-599 course' in Major: "Seven units of electives in chemistry" encoded as an open rule (CHEM 300-599, 7 units); check it.
- [ ] 'Any CHEM 300-599 course': the page names no subject code; CHEM was read from the department name. Check it.

### Units check (advisory)

- Preparation for the Major: page says 43 units, listed courses give 43: **inside**
- Major: page says at least 24 units, listed courses give 24: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major: Note**
  - CHEM 560 is recommended for all premedical students.
- **Minor**
  - A minor in biology is expected for preprofessional students.

### Coverage (sections in data/cleaned)

- Required courses: 21 of 21 have sections
  - with sections: CHEM 200 (49), CHEM 201 (19), CHEM 232 (1), CHEM 232L (14), CHEM 251 (4), BIOL 203 (2), BIOL 203L (22), MATH 150 (12), MATH 151 (20), MATH 252 (13), PHYS 195 (2), PHYS 195L (17), PHYS 196 (1), PHYS 196L (10), CHEM 410A (3), CHEM 410B (1), CHEM 417 (2), CHEM 432 (1), CHEM 432L (7), CHEM 457 (1), CHEM 550 (1)
- Open rule 'Any CHEM 300-599 course' (without excluded and already-required courses): 11 courses with sections: CHEM 300, CHEM 365, CHEM 413, CHEM 427, CHEM 498, CHEM 520B, CHEM 560, CHEM 562, CHEM 564, CHEM 567, CHEM 596

### Title differences (catalog vs class data)

- none
- 5 more only shortened in the class data (not a real difference): CHEM 232L, CHEM 417, CHEM 432L, CHEM 457, CHEM 550

## Chemistry, and Certificate of the American Chemical Society, B.S. (`chemistry_american_chemical_society_bs`)

- Source: `data/catalog_html/Program_ Chemistry, B.S. and Certificate of the American Chemical Society - San Diego State University.html`, poid 11937, major code 19051
- Rows: 26

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 12: CHEM 200, CHEM 201, CHEM 232, CHEM 232L, CHEM 251, MATH 150, MATH 151, MATH 252, PHYS 195, PHYS 195L, PHYS 196, PHYS 196L |
| Major | Required | required | 12: CHEM 410A, CHEM 410B, CHEM 417, CHEM 427, CHEM 432, CHEM 432L, CHEM 457, CHEM 520A, CHEM 520B, CHEM 550, CHEM 560, CHEM 498 |
| Major | Any CHEM 300-599 course | open, 7 units | 1: Any CHEM 300-599 course |

### Section notes (shown once under the heading)

- **Preparation for the Major**: If CHEM 251 and MATH 252 were not completed prior to matriculation, it must be completed at SDSU. Recommended (not required): PHYS 197, PHYS 197L

### Review list

- [ ] Name 'Chemistry, and Certificate of the American Chemical Society' was built from an unusual title 'Chemistry, B.S. and Certificate of the American Chemical Society'; check it.
- [ ] 'Preparation for the Major': rule text kept as the section note: "If CHEM 251 and MATH 252 were not completed prior to matriculation, it must be completed at SDSU."
- [ ] Text under 'Preparation for the Major' left out (no rule in it; in the report only): "Students completing the California Community College Associate in Science in Chemistry for Transfer (AS-T) will satisfy preparation for the major."
- [ ] 'Recommended' list under 'Preparation for the Major' is not required: no rows, a section note (PHYS 197, PHYS 197L).
- [ ] 'Any CHEM 300-599 course' in Major: "Seven units of upper division electives in chemistry" encoded as an open rule (CHEM 300-599, 7 units); check it.
- [ ] 'Any CHEM 300-599 course': the page names no subject code; CHEM was read from the department name. Check it.

### Units check (advisory)

- Preparation for the Major: page says 39 units, listed courses give 39: **inside**
- Major: page says at least 36 units, listed courses give 36-38: **inside**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - All candidates for a Bachelor of Science degree must complete the graduation requirements listed in the section of this catalog on “Graduation Requirements .”
  - A minor is not required with this major.
- **Preparation for the Major**
  - Students completing the California Community College Associate in Science in Chemistry for Transfer (AS-T) will satisfy preparation for the major.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major: Note**
  - Six of the seven units may be in related subjects with the approval of the department.

### Coverage (sections in data/cleaned)

- Required courses: 23 of 24 have sections
  - with sections: CHEM 200 (49), CHEM 201 (19), CHEM 232 (1), CHEM 232L (14), CHEM 251 (4), MATH 150 (12), MATH 151 (20), MATH 252 (13), PHYS 195 (2), PHYS 195L (17), PHYS 196 (1), PHYS 196L (10), CHEM 410A (3), CHEM 410B (1), CHEM 417 (2), CHEM 427 (3), CHEM 432 (1), CHEM 432L (7), CHEM 457 (1), CHEM 520B (1), CHEM 550 (1), CHEM 560 (1), CHEM 498 (1)
  - no sections: CHEM 520A
- Open rule 'Any CHEM 300-599 course' (without excluded and already-required courses): 7 courses with sections: CHEM 300, CHEM 365, CHEM 413, CHEM 562, CHEM 564, CHEM 567, CHEM 596

### Title differences (catalog vs class data)

- none
- 6 more only shortened in the class data (not a real difference): CHEM 232L, CHEM 417, CHEM 427, CHEM 432L, CHEM 457, CHEM 550

## Chemistry, Emphasis in Biochemistry, and Certificate of the American Chemical Society, B.S. (`chemistry_biochemistry_american_chemical_society_bs`)

- Source: `data/catalog_html/Program_ Chemistry, Emphasis in Biochemistry, B.S. and Certificate of the American Chemical Society - San Diego State University.html`, poid 11938
- Rows: 39

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 12: CHEM 200, CHEM 201, CHEM 232, CHEM 232L, CHEM 251, MATH 150, MATH 151, MATH 252, PHYS 195, PHYS 195L, PHYS 196, PHYS 196L |
| Preparation for the Major | BIOL 203 and BIOL 203L, or BIOL 204 and BIOL 204L | choose 2 | 4: BIOL 203, BIOL 203L, BIOL 204, BIOL 204L |
| Major | Required | required | 8: CHEM 410A, CHEM 410B, CHEM 432, CHEM 432L, CHEM 457, CHEM 550, CHEM 560, CHEM 567 |
| Major | Senior Project | required | 1: CHEM 498 |
| Advanced Biochemistry Core | Advanced Biochemistry Core | pool, 6 units | 3: CHEM 562, CHEM 563, CHEM 564 |
| Upper Division Major Electives | Upper Division Major Electives | pool, 8 units | 9: CHEM 496, CHEM 497, CHEM 498, BIOL 350, BIOL 352, BIOL 485, BIOL 549, BIOL 570, BIOL 590 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Recommended (not required): PHYS 197, PHYS 197L
- **Upper Division Major Electives**: Any 500-level chemistry course

### Review list

- [ ] Name 'Chemistry, Emphasis in Biochemistry, and Certificate of the American Chemical Society' was built from an unusual title 'Chemistry, Emphasis in Biochemistry, B.S. and Certificate of the American Chemical Society'; check it.
- [ ] 'BIOL 203 and BIOL 203L, or BIOL 204 and BIOL 204L' in Preparation for the Major: a choice between pairs, encoded as pick 2 with a note; the app cannot stop a student mixing the pairs. Check it.
- [ ] 'Recommended' list under 'Preparation for the Major' is not required: no rows, a section note (PHYS 197, PHYS 197L).
- [ ] 'Advanced Biochemistry Core' (under Major) asks for 6 units of its list: encoded as a pool in its own section 'Advanced Biochemistry Core', check it.
- [ ] 'Upper Division Major Electives' in Major: text between courses that was not read as a rule: "Any 500-level chemistry course"
- [ ] 'Upper Division Major Electives' (under Major) asks for 8 units of its list: encoded as a pool in its own section 'Upper Division Major Electives', check it.

### Units check (advisory)

- Preparation for the Major: page says 43 units, listed courses give 41-45: **overlaps**
- Major: page says at least 36 units, listed courses give 36-38: **inside**

### Major notes (no rows made; for a human)

- **(Academic Plan Code: 772609BSS)**
  - All candidates for a bachelor’s degree must complete the graduation requirements listed in the section of this catalog on “Graduation Requirements.”
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Note**
  - The addition of CHEM 417 , CHEM 427 , and CHEM 520A qualifies this program for ACS certification.

### Coverage (sections in data/cleaned)

- Required courses: 21 of 21 have sections
  - with sections: CHEM 200 (49), CHEM 201 (19), CHEM 232 (1), CHEM 232L (14), CHEM 251 (4), MATH 150 (12), MATH 151 (20), MATH 252 (13), PHYS 195 (2), PHYS 195L (17), PHYS 196 (1), PHYS 196L (10), CHEM 410A (3), CHEM 410B (1), CHEM 432 (1), CHEM 432L (7), CHEM 457 (1), CHEM 550 (1), CHEM 560 (1), CHEM 567 (2), CHEM 498 (1)
- Pick-n group courses: 4 of 4 have sections
  - with sections: BIOL 203 (2), BIOL 203L (22), BIOL 204 (4), BIOL 204L (16)
- Elective pool courses: 6 of 11 have sections
  - with sections: CHEM 562 (1), CHEM 564 (1), BIOL 350 (8), BIOL 352 (9), BIOL 485 (1), BIOL 570 (1)
  - no sections: CHEM 563, CHEM 496, CHEM 497, BIOL 549, BIOL 590

### Title differences (catalog vs class data)

- none
- 7 more only shortened in the class data (not a real difference): CHEM 232L, BIOL 204, BIOL 204L, CHEM 432L, CHEM 457, CHEM 550, CHEM 564

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

## Communication, B.A. (`communication_ba`)

- Source: `data/catalog_html/Program_ Communication, B.A. - San Diego State University.html`, poid 11960, major code 15061
- Rows: 49

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Choose from these courses | pool, 6 units | 4: COMM 160, COMM 201, COMM 204, COMM 245 |
| Mathematics Competency Requirement | Required | required | 6: STAT 250, STAT 350A, STAT 350B, SOC 201, SOC 406, SOC 407 |
| Major | Required | required | 2: COMM 300, COMM 350 |
| Major | Communication Capstone | required | 1: COMM 495 |
| Conceptualizing Communication | Conceptualizing Communication | pool, 9 units | 6: COMM 321, COMM 371, COMM 415, COMM 450, COMM 470, COMM 492 |
| Investigating Communication | Investigating Communication | pool, 6 units | 5: COMM 407, COMM 420, COMM 441, COMM 462, COMM 465 |
| Communication Electives | Communication Electives | pool, 12 units | 15: COMM 301, COMM 307, COMM 406, COMM 444, COMM 445, COMM 446, COMM 452, COMM 482, COMM 485, COMM 490, COMM 496, COMM 499, COMM 508, COMM 540, COMM 555 |
| Communication Electives | Health Communication Electives | pool, 12 units | 8: COMM 421, COMM 422, COMM 423, COMM 424, COMM 425, COMM 426, COMM 427, COMM 428 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: (9 units) General Education Oral Communication requirement (3 units) and 6 units selected from:
- **Mathematics Competency Requirement**: Competency in mathematics is generally satisfied by completing three semesters of college mathematics

### Review list

- [ ] 'Required': rule text kept as the section note, check it: "(9 units) General Education Oral Communication requirement (3 units) and 6 units selected from:"
- [ ] 'Preparation for the Major' asks for 6 units of its list: the whole list is a 6-unit pool, check it.
- [ ] 'Mathematics Competency Requirement': rule text kept as the section note: "Competency in mathematics is generally satisfied by completing three semesters of college mathematics."
- [ ] Text under 'Mathematics Competency Requirement' left out (no rule in it; in the report only): "Refer to the “General Education Requirements” section of this catalog for a list of approved Area 2. Mathematical Concepts and Quantitative Reasoning courses. or Students interested in a statistics sequence may choose from one of the following two statistics sequences approved for the Communication major."
- [ ] 'Required' in Mathematics Competency Requirement: text between courses that was not read as a rule: "(highly recommended)"
- [ ] 'Conceptualizing Communication' (under Major) asks for 9 units of its list: encoded as a pool in its own section 'Conceptualizing Communication', check it.
- [ ] 'Investigating Communication' (under Major) asks for 6 units of its list: encoded as a pool in its own section 'Investigating Communication', check it.
- [ ] 'Communication Electives' (under Major) asks for 12 units of its list: encoded as a pool in its own section 'Communication Electives', check it.
- [ ] 'Health Communication Electives' (a list under the 'Communication Electives' pool) joined that pool (12 units) with the note "Additional Communication Electives can be selected from the following list, with no more than 9 units selected from:"; check it.
- [ ] 'Communication Capstone' in Major: rule text kept as the note, check the group: "(3 units) Must be taken after completion of at least 90 units to include 6 units in Conceptualizing Communication and 6 units in Investigating Communication."

### Units check (advisory)

- Major: page says at least 36 units, listed courses give 36: **inside**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - Lower division preparation for the major courses may be satisfied by comparable courses in community colleges or other institutions with which the university has articulation agreements.
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - A minor is not required with this major but is strongly recommended.
- **Impacted Program**
  - The Communication major is an impacted program. To be admitted to the major, students must meet the following criteria:
  - a. Complete with a grade of C (2.0) or better in General Education Oral Communication and a grade of C (2.0) or better in 6 units selected from: COMM 160, COMM 201, COMM 204, COMM 245. These courses cannot be taken for credit/no credit (Cr/NC);
  - b. Have a minimum cumulative GPA of 2.75.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Mathematics Competency Requirement**
  - Refer to the “General Education Requirements” section of this catalog for a list of approved Area 2.
  - Mathematical Concepts and Quantitative Reasoning courses. or Students interested in a statistics sequence may choose from one of the following two statistics sequences approved for the Communication major.
- **Graduation Writing Assessment Requirement**
  - Complete RWS 305W or PSFA 305W (recommended) and earn a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements. Courses listed: RWS 305W, PSFA 305W.
  - PSFA 305W is listed for the GWAR but not in the major lists.
  - RWS 305W is listed for the GWAR but not in the major lists.

### Coverage (sections in data/cleaned)

- Required courses: 7 of 9 have sections
  - with sections: STAT 250 (8), STAT 350B (1), SOC 201 (7), SOC 407 (1), COMM 300 (4), COMM 350 (4), COMM 495 (6)
  - no sections: STAT 350A, SOC 406
- Elective pool courses: 31 of 38 have sections
  - with sections: COMM 160 (3), COMM 201 (1), COMM 204 (1), COMM 245 (2), COMM 321 (4), COMM 371 (7), COMM 415 (1), COMM 450 (1), COMM 470 (1), COMM 492 (1), COMM 407 (2), COMM 420 (1), COMM 441 (1), COMM 462 (1), COMM 465 (2), COMM 301 (1), COMM 307 (4), COMM 406 (1), COMM 445 (3), COMM 452 (2), COMM 482 (1), COMM 485 (2), COMM 490 (1), COMM 496 (1), COMM 508 (1), COMM 540 (1), COMM 555 (1), COMM 422 (1), COMM 426 (1), COMM 427 (1), COMM 428 (1)
  - no sections: COMM 444, COMM 446, COMM 499, COMM 421, COMM 423, COMM 424, COMM 425

### Title differences (catalog vs class data)

- COMM 496: catalog "Experimental Topics", class data "GlobalBordersComm"
- COMM 427: catalog "Health Communication and Cultural Communities", class data "HealthComm/CulturalCommunities"
- 16 more only shortened in the class data (not a real difference): COMM 201, SOC 407, COMM 495, COMM 407, COMM 420, COMM 441, COMM 462, COMM 465, COMM 301, COMM 307, COMM 406, COMM 540, COMM 555, COMM 422, COMM 426, COMM 428

## Computer Engineering, B.S. (`computer_engineering_bs`)

- Source: `data/catalog_html/Program_ Computer Engineering, B.S. - San Diego State University.html`, poid 11968, major code 09094
- Rows: 46

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

- **Major**: After enrollment in Computer Engineering at SDSU, the Computer Engineering major must take all upper division computer science and engineering courses at SDSU unless prior approval is obtained from the department
- **Upper Division Major Electives**: (15 units) Five upper division major elective courses from the following list in 4 concentration areas

### Review list

- [ ] 'Major': rule text kept as the section note: "After enrollment in Computer Engineering at SDSU, the Computer Engineering major must take all upper division computer science and engineering courses at SDSU unless prior approval is obtained from the department."
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

## Construction Engineering, B.S. (`construction_engineering_bs`)

- Source: `data/catalog_html/Program_ Construction Engineering, B.S. - San Diego State University.html`, poid 11972, major code 09254
- Rows: 46

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 15: CON E 101, CON E 201, CON E 280, CIV E 218, CIV E 225, ECON 102, GEOL 100, GEOL 101, MATH 150, MATH 151, PHIL 101, PHYS 195, PHYS 195L, PHYS 196, PHYS 196L |
| Preparation for the Major | CONE 215 or CIVE 121 (pick 1) | choose 1 | 2: CON E 215, CIV E 121 |
| Preparation for the Major | BIOL 100 or BIOL 101 (pick 1) | choose 1 | 2: BIOL 100, BIOL 101 |
| Preparation for the Major | CHEM 202 or CHEM 200 (pick 1) | choose 1 | 2: CHEM 202, CHEM 200 |
| Preparation for the Major | CIVE 160 or STAT 250 (pick 1) | choose 1 | 2: CIV E 160, STAT 250 |
| Major | Required | required | 15: CON E 301, CON E 312, CON E 320, CON E 330, CON E 340, CON E 401, CON E 479, CON E 480, CON E 590, CIV E 301, CIV E 302, CIV E 321, CIV E 462, CIV E 463, CIV E 495W |
| Technical Elective A | Technical Elective A | pool, 3 units | 6: CON E 520, CIV E 421, CIV E 465, CIV E 523, CIV E 525, CIV E 528 |
| Technical Elective B | Technical Elective B | pool, 1 units | 1: CON E 499 |

### Section notes (shown once under the heading)

- **Technical Elective A**: Three units from Technical elective A and one unit from Technical elective B

### Review list

- [ ] CONE 215 or CIVE 121 (pick 1) in Preparation for the Major: the 'or' sits next to other courses with no break, so it may cover more than one course. Check the catalog page.
- [ ] BIOL 100 or BIOL 101 (pick 1) in Preparation for the Major: the 'or' sits next to other courses with no break, so it may cover more than one course. Check the catalog page.
- [ ] CHEM 202 or CHEM 200 (pick 1) in Preparation for the Major: the 'or' sits next to other courses with no break, so it may cover more than one course. Check the catalog page.
- [ ] CIVE 160 or STAT 250 (pick 1) in Preparation for the Major: the 'or' sits next to other courses with no break, so it may cover more than one course. Check the catalog page.
- [ ] 'Three Units Selected From': "Three units from Technical elective A and one unit from Technical elective B." read as separate pools: 'Technical Elective A' 3 units, 'Technical Elective B' 1 units.

### Units check (advisory)

- Preparation for the Major: page says 54 units, listed courses give 54-55: **overlaps**
- Major: page says at least 45 units, listed courses give 45: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - The program below describes 120 units required for the degree. Each course specifically listed in the program is required. In addition, the number of units specified in each elective category represents a minimum requirement.
  - The Construction Engineering major is an impacted program. To be admitted to the Construction Engineering major, students must meet the following impaction criteria:
  - Complete with a grade of C (2.0) or better: CIV E 225; CHEM 202 (or CHEM 200); MATH 150, MATH 151; PHYS 195, PHYS 196. These courses cannot be taken for credit/no credit (Cr/NC);
  - Have an overall cumulative GPA of 2.7.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Major Restriction for Registration**
  - You must be in the Civil, Construction, Environmental Engineering or Construction Management Major (cleared impaction requirements) in order to take the upper level (300-400+) courses.
- **General Education**
  - Engineering majors automatically satisfy Area 2/5. Mathematical Concepts and Quantitative Reasoning or Physical and Biological Sciences and Area 4. Social and Behavioral Explorations GE areas by completion of the major.
- **Graduation Writing Assessment Requirement**
  - Complete CIV E 495W with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.

### Coverage (sections in data/cleaned)

- Required courses: 27 of 30 have sections
  - with sections: CON E 101 (1), CON E 201 (1), CON E 280 (2), CIV E 218 (6), CIV E 225 (2), ECON 102 (6), GEOL 100 (2), GEOL 101 (11), MATH 150 (12), MATH 151 (20), PHIL 101 (3), PHYS 195 (2), PHYS 195L (17), PHYS 196 (1), PHYS 196L (10), CON E 330 (2), CON E 340 (1), CON E 401 (3), CON E 479 (2), CON E 480 (1), CON E 590 (1), CIV E 301 (3), CIV E 302 (5), CIV E 321 (1), CIV E 462 (2), CIV E 463 (3), CIV E 495W (4)
  - no sections: CON E 301, CON E 312, CON E 320
- Pick-n group courses: 8 of 8 have sections
  - with sections: CON E 215 (2), CIV E 121 (8), BIOL 100 (4), BIOL 101 (1), CHEM 202 (11), CHEM 200 (49), CIV E 160 (1), STAT 250 (8)
- Elective pool courses: 4 of 7 have sections
  - with sections: CON E 520 (1), CIV E 421 (1), CIV E 465 (2), CIV E 523 (1)
  - no sections: CIV E 525, CIV E 528, CON E 499

### Title differences (catalog vs class data)

- none
- 18 more only shortened in the class data (not a real difference): CON E 201, CIV E 218, CIV E 225, CON E 215, CIV E 121, CHEM 202, CIV E 160, CON E 330, CON E 340, CON E 401, CON E 480, CON E 590, CIV E 301, CIV E 302, CON E 520, CIV E 421, CIV E 465, CIV E 523

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

## Environmental Engineering, B.S. (`environmental_engineering_bs`)

- Source: `data/catalog_html/Program_ Environmental Engineering, B.S. - San Diego State University.html`, poid 11997, major code 09221
- Rows: 40

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 15: ENV E 101, A E 280, BIOL 204, BIOL 204L, CHEM 130, CIV E 121, CIV E 220, CIV E 225, MATH 150, MATH 151, MATH 252, PHYS 195, PHYS 195L, PHYS 196, ENV E 200 |
| Preparation for the Major | CHEM 202 or CHEM 200 (pick 1) | choose 1 | 2: CHEM 202, CHEM 200 |
| Preparation for the Major | CIVE 160 or STAT 250 (pick 1) | choose 1 | 2: CIV E 160, STAT 250 |
| Major | Required | required | 13: ENV E 355, ENV E 356, ENV E 363, ENV E 445, ENV E 554, ENV E 556, ENV E 558, A E 340, CIV E 444, CIV E 462, CIV E 495W, CON E 330, M E 350 |
| Three Units of Professional Electives | Three Units of Professional Electives | pool, 3 units | 8: ENV E 499, ENV E 555, CIV E 445, CIV E 530, CIV E 531, CIV E 545, GEOG 570, GEOL 530 |

### Section notes (shown once under the heading)

- none

### Review list

- [ ] 'Three Units of Professional Electives' (under Major) asks for 3 units of its list: encoded as a pool in its own section 'Three Units of Professional Electives', check it.

### Units check (advisory)

- Preparation for the Major: page says 51 units, listed courses give 51-52: **overlaps**
- Major: page says at least 42 units, listed courses give 42: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - This program requires 120 units to include general education. In addition, the total number of units specified in each elective category represents a minimum requirement.
  - All students in environmental engineering pursue a common program of study in basic sciences, engineering, and environmental engineering fundamentals and design. The program allows three units of “professional electives” which can be selected from available courses in environmental chemistry, environmental microbiology, water resources, and other areas.
- **Impacted Program**
  - The Environmental Engineering major is an impacted program. To be admitted to the Environmental Engineering major, students must meet the following impaction criteria:
  - Complete with a grade of C (2.0) or better: CIV E 225; CHEM 202 (or CHEM 200); MATH 150, MATH 151; PHYS 195, PHYS 196. These courses cannot be taken for credit/no credit (Cr/NC);
  - Have an overall cumulative GPA of 2.7 or higher.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Major Restriction for Registration**
  - You must be in the Civil or Environmental Engineering Majors (cleared impaction requirements) in order to take the upper level (300-400+) courses.
- **General Education**
  - Engineering majors automatically satisfy Area 2/5. Mathematical Concepts and Quantitative Reasoning or Physical and Biological Sciences and Area 4. Social and Behavioral Explorations GE areas by completion of the major.
- **Graduation Writing Assessment Requirement**
  - Complete CIV E 495W with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.

### Coverage (sections in data/cleaned)

- Required courses: 27 of 28 have sections
  - with sections: ENV E 101 (2), A E 280 (3), BIOL 204 (4), BIOL 204L (16), CHEM 130 (1), CIV E 121 (8), CIV E 225 (2), MATH 150 (12), MATH 151 (20), MATH 252 (13), PHYS 195 (2), PHYS 195L (17), PHYS 196 (1), ENV E 200 (1), ENV E 355 (2), ENV E 356 (1), ENV E 363 (3), ENV E 445 (1), ENV E 554 (1), ENV E 556 (1), ENV E 558 (1), A E 340 (2), CIV E 444 (4), CIV E 462 (2), CIV E 495W (4), CON E 330 (2), M E 350 (3)
  - no sections: CIV E 220
- Pick-n group courses: 4 of 4 have sections
  - with sections: CHEM 202 (11), CHEM 200 (49), CIV E 160 (1), STAT 250 (8)
- Elective pool courses: 3 of 8 have sections
  - with sections: CIV E 445 (2), CIV E 530 (2), GEOG 570 (2)
  - no sections: ENV E 499, ENV E 555, CIV E 531, CIV E 545, GEOL 530

### Title differences (catalog vs class data)

- none
- 16 more only shortened in the class data (not a real difference): ENV E 101, BIOL 204, BIOL 204L, CHEM 130, CIV E 121, CIV E 225, ENV E 200, CHEM 202, CIV E 160, ENV E 356, ENV E 363, ENV E 445, ENV E 554, ENV E 558, CON E 330, GEOG 570

## Health Communication, B.S. (`health_communication_bs`)

- Source: `data/catalog_html/Program_ Health Communication, B.S. - San Diego State University.html`, poid 11961, major code 06013
- Rows: 41

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Choose from these courses | pool, 6 units | 4: COMM 160, COMM 201, COMM 204, COMM 245 |
| Major | Required | required | 3: COMM 300, COMM 321, COMM 350 |
| Major | Health Communication Capstone | required | 1: COMM 495 |
| Investigating Communication | Investigating Communication | pool, 6 units | 5: COMM 407, COMM 420, COMM 441, COMM 462, COMM 465 |
| Health Communication Electives | Health Communication Electives | pool, 18 units | 12: COMM 421, COMM 422, COMM 423, COMM 424, COMM 425, COMM 426, COMM 427, COMM 428, COMM 444, COMM 485, COMM 490, COMM 540 |
| Health Communication Electives | 3 units may also be selected from | pool, 18 units | 6: COMM 371, COMM 415, COMM 445, COMM 492, COMM 499, COMM 555 |
| Health-Related Preparation Courses | Health-Related Preparation Courses | pool, 6 units | 9: GERO 360, GERO 370, HHS 350, NURS 350, PHIL 330, P A 340, P H 353, P H 362, SWORK 430 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: General Education Oral Communication requirement (3 units) and 6 units selected from:

### Review list

- [ ] 'Required': rule text kept as the section note, check it: "General Education Oral Communication requirement (3 units) and 6 units selected from:"
- [ ] 'Preparation for the Major' asks for 6 units of its list: the whole list is a 6-unit pool, check it.
- [ ] 'Investigating Communication' (under Major) asks for 6 units of its list: encoded as a pool in its own section 'Investigating Communication', check it.
- [ ] 'Health Communication Electives' (under Major) asks for 18 units of its list: encoded as a pool in its own section 'Health Communication Electives', check it.
- [ ] '3 units may also be selected from:' (a list under the 'Health Communication Electives' pool) joined that pool (18 units) with the note "3 units may also be selected from"; check it.
- [ ] 'Health-Related Preparation Courses' (under Major) asks for 6 units of its list: encoded as a pool in its own section 'Health-Related Preparation Courses', check it.
- [ ] 'Health Communication Capstone' in Major: rule text kept as the note, check the group: "Must be taken after completion of at least 90 units to include 6 units in Investigating Communication and 6 units in Health Communication Electives."
- [ ] Units check for Preparation for the Major: page says 9, listed courses add up to 6.

### Units check (advisory)

- Preparation for the Major: page says 9 units, listed courses give 6: **MISMATCH**
- Major: page says at least 42 units, listed courses give 42: **inside**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - Lower division preparation for the major courses may be satisfied by comparable courses in community colleges or other institutions with which the university has articulation agreements.
  - A minor is not required with this major but is strongly recommended.
- **Impacted Program**
  - The Health Communication major is an impacted program. To be admitted to the major, students must meet the following criteria:
  - a. Complete with a grade of C (2.0) or better in General Education Oral Communication and a grade of C (2.0) or better in 6 units selected from: COMM 160, COMM 201, COMM 204, COMM 245. These courses cannot be taken for credit/no credit (Cr/NC);
  - b. Have a minimum cumulative GPA of 2.75.
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements. Recommended: RWS 305W or PSFA 305W
  - PSFA 305W is listed for the GWAR but not in the major lists.
  - RWS 305W is listed for the GWAR but not in the major lists.

### Coverage (sections in data/cleaned)

- Required courses: 4 of 4 have sections
  - with sections: COMM 300 (4), COMM 321 (4), COMM 350 (4), COMM 495 (6)
- Elective pool courses: 30 of 36 have sections
  - with sections: COMM 160 (3), COMM 201 (1), COMM 204 (1), COMM 245 (2), COMM 407 (2), COMM 420 (1), COMM 441 (1), COMM 462 (1), COMM 465 (2), COMM 422 (1), COMM 426 (1), COMM 427 (1), COMM 428 (1), COMM 485 (2), COMM 490 (1), COMM 540 (1), COMM 371 (7), COMM 415 (1), COMM 445 (3), COMM 492 (1), COMM 555 (1), GERO 360 (1), GERO 370 (1), HHS 350 (2), NURS 350 (2), PHIL 330 (1), P A 340 (2), P H 353 (1), P H 362 (1), SWORK 430 (1)
  - no sections: COMM 421, COMM 423, COMM 424, COMM 425, COMM 444, COMM 499

### Title differences (catalog vs class data)

- COMM 427: catalog "Health Communication and Cultural Communities", class data "HealthComm/CulturalCommunities"
- HHS 350: catalog "Applied International Health and Human Services", class data "International Experience"
- 13 more only shortened in the class data (not a real difference): COMM 201, COMM 495, COMM 407, COMM 420, COMM 441, COMM 462, COMM 465, COMM 422, COMM 426, COMM 428, COMM 540, COMM 555, SWORK 430

## Kinesiology, Emphasis in Exercise Science Generalist, B.S. (`kinesiology_exercise_science_generalist_bs`)

- Source: `data/catalog_html/Program_ Kinesiology, Emphasis in Exercise Science Generalist, B.S. - San Diego State University.html`, poid 12004, major code 08351
- Rows: 29

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 1: ENS 265 |
| Preparation for the Major | CHEM 100 or CHEM 102 or CHEM 200 (pick 1) | choose 1 | 3: CHEM 100, CHEM 102, CHEM 200 |
| Preparation for the Major | Statistics (pick 1) | choose 1 | 5: BIOL 215, ECON 201, PSY 280, SOC 201, STAT 119 |
| Major | Required | required | 14: ENS 303, ENS 304, ENS 304L, ENS 305, ENS 307, ENS 308, ENS 322, ENS 332, ENS 333, ENS 340, ENS 433, ENS 434, HHS 350, FN 313 |
| Major | ENS 437A or ENS 437B (pick 1) | choose 1 | 2: ENS 437A, ENS 437B |
| Upper Division Major Elective | Upper Division Major Elective | pool, 3 units | 3: ENS 318, ENS 330, ENS 331 |

### Section notes (shown once under the heading)

- **Preparation for the Major**: Students must complete the following courses as part of the TMC or at SDSU:

### Review list

- [ ] 'Preparation for the Major': rule text kept as the section note: "Students must complete the following courses as part of the TMC or at SDSU:"
- [ ] Text under 'Preparation for the Major' left out (no rule in it; in the report only): "The emphasis in Exercise Science Generalist is open only to students who have completed the California Community College Associate in Arts in Kinesiology for Transfer (AA-T) degree completing the Transfer Model Curriculum (TMC) for Kinesiology."
- [ ] 'Statistics (pick 1)' in Preparation for the Major: read as pick 1 of 5; check it.
- [ ] 'Upper Division Major Elective' (under Major) asks for 3 units of its list: encoded as a pool in its own section 'Upper Division Major Elective', check it.

### Units check (advisory)

- Preparation for the Major: page says 9-10 units, listed courses give 9-11: **overlaps**
- Major: page says at least 43 units, listed courses give 43: **inside**

### Major notes (no rows made; for a human)

- **Associate Degree for Transfer (ADT) Major**
  - All candidates for a bachelor’s degree must complete the requirements outlined in the “Graduation Requirements” section of this catalog.
  - Preparation for the Major courses cannot be taken for credit/no credit (Cr/NC). ENS 200 and BIOL 212 must be completed with a grade of C (2.0) or better.
- **Open only to AA-T/TMC for Kinesiology**
  - Students must complete the major requirements in effect at the time they were admitted to the premajor at SDSU, provided they maintain continuous enrollment.
- **Preparation for the Major**
  - The emphasis in Exercise Science Generalist is open only to students who have completed the California Community College Associate in Arts in Kinesiology for Transfer (AA-T) degree completing the Transfer Model Curriculum (TMC) for Kinesiology.
- **Graduation Writing Assessment Requirement**
  - Complete one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major: Recommended**
  - COMM 321 is recommended, if needed, for students to complete their 60 unit requirement at SDSU.

### Coverage (sections in data/cleaned)

- Required courses: 15 of 15 have sections
  - with sections: ENS 265 (2), ENS 303 (2), ENS 304 (2), ENS 304L (16), ENS 305 (2), ENS 307 (2), ENS 308 (1), ENS 322 (6), ENS 332 (1), ENS 333 (1), ENS 340 (6), ENS 433 (1), ENS 434 (3), HHS 350 (2), FN 313 (2)
- Pick-n group courses: 8 of 10 have sections
  - with sections: CHEM 100 (11), CHEM 200 (49), BIOL 215 (11), ECON 201 (4), PSY 280 (22), SOC 201 (7), STAT 119 (5), ENS 437A (16)
  - no sections: CHEM 102, ENS 437B
- Elective pool courses: 3 of 3 have sections
  - with sections: ENS 318 (1), ENS 330 (2), ENS 331 (5)

### Title differences (catalog vs class data)

- HHS 350: catalog "Applied International Health and Human Services", class data "International Experience"
- 3 more only shortened in the class data (not a real difference): ENS 322, ENS 340, ENS 433

## Kinesiology, Emphasis in Fitness Specialist, B.S. (`kinesiology_fitness_specialist_bs`)

- Source: `data/catalog_html/Program_ Kinesiology, Emphasis in Fitness Specialist, B.S. - San Diego State University.html`, poid 12005, major code 08351
- Rows: 37

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 13: ENS 200, ENS 265, ENS 265L, BIOL 100, BIOL 100L, BIOL 212, CHEM 100, COMM 103, GERO 101, FN 201, PHYS 180A, PSY 101, SOC 101 |
| Preparation for the Major | One of the Following (pick 1) | choose 1 | 5: BIOL 215, ECON 201, PSY 280, SOC 201, STAT 119 |
| Major | Required | required | 17: ENS 303, ENS 304, ENS 304L, ENS 305, ENS 306, ENS 307, ENS 322, ENS 332, ENS 333, ENS 340, ENS 410, ENS 433, ENS 434, ENS 438, ENS 439, ENS 440, BIOL 336 |
| Major | ENS 437A or ENS 437B (pick 1) | choose 1 | 2: ENS 437A, ENS 437B |

### Section notes (shown once under the heading)

- none

### Review list

- [ ] 'One of the Following (pick 1)' in Preparation for the Major: read as pick 1 of 5; check it.
- [ ] ENS 437A or ENS 437B (pick 1) in Major: the 'or' sits next to other courses with no break, so it may cover more than one course. Check the catalog page.

### Units check (advisory)

- Preparation for the Major: page says 39 units, listed courses give 39-40: **overlaps**
- Major: page says at least 48 units, listed courses give 48: **inside**

### Major notes (no rows made; for a human)

- **Program description**
  - All candidates for a degree in applied arts and sciences must complete the requirements listed in the section of this catalog on “Graduation Requirements .”
  - Preparation for the Major courses cannot be taken for credit/no credit (Cr/NC). ENS 200 and BIOL 212 must be completed with a grade of C (2.0) or better.
- **Graduation Writing Assessment Requirement**
  - Complete one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Recommended**
  - Students should take HHS 350 , ENS 318 , or ENS 330 to satisfy the General Education requirement in IV.B.

### Coverage (sections in data/cleaned)

- Required courses: 28 of 30 have sections
  - with sections: ENS 200 (1), ENS 265 (2), ENS 265L (3), BIOL 100 (4), BIOL 100L (26), BIOL 212 (18), CHEM 100 (11), COMM 103 (98), FN 201 (1), PHYS 180A (1), PSY 101 (2), SOC 101 (11), ENS 303 (2), ENS 304 (2), ENS 304L (16), ENS 305 (2), ENS 306 (1), ENS 307 (2), ENS 322 (6), ENS 332 (1), ENS 333 (1), ENS 340 (6), ENS 433 (1), ENS 434 (3), ENS 438 (1), ENS 439 (2), ENS 440 (2), BIOL 336 (1)
  - no sections: GERO 101, ENS 410
- Pick-n group courses: 6 of 7 have sections
  - with sections: BIOL 215 (11), ECON 201 (4), PSY 280 (22), SOC 201 (7), STAT 119 (5), ENS 437A (16)
  - no sections: ENS 437B

### Title differences (catalog vs class data)

- none
- 6 more only shortened in the class data (not a real difference): ENS 265L, ENS 322, ENS 340, ENS 433, ENS 439, ENS 440

## Mechanical Engineering, Emphasis in Bioengineering, B.S. (`mechanical_engineering_bioengineering_bs`)

- Source: `data/catalog_html/Program_ Mechanical Engineering, Emphasis in Bioengineering, B.S. - San Diego State University.html`, poid 12131, major code 09101
- Rows: 40

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 14: M E 190, M E 202, M E 230, M E 240, M E 241, A E 280, BIOL 203, MATH 150, MATH 151, MATH 252, PHYS 195, PHYS 195L, PHYS 196, PHYS 196L |
| Preparation for the Major | ME 200 / AE 200 (same course, pick 1) | choose 1 | 2: M E 200, A E 200 |
| Preparation for the Major | ME 220 / AE 220 (same course, pick 1) | choose 1 | 2: M E 220, A E 220 |
| Preparation for the Major | CHEM 202 or CHEM 200 (pick 1) | choose 1 | 2: CHEM 202, CHEM 200 |
| Major | Required | required | 13: M E 304, M E 314, M E 330, M E 340, M E 350, M E 360, M E 430, M E 452, M E 490W, M E 491, A E 341, BIOL 336, BIOL 436 |
| Professional Electives | Professional Electives | pool, 9 units | 6: M E 499, M E 570, M E 580, M E 582, M E 585, E E 503 |

### Section notes (shown once under the heading)

- **Professional Electives**: Nine units of additional coursework may be selected from M E 499 (3 units), M E 570 , M E 580 , M E 582 , M E 585 , E E 503 , and other 400- or 500-level courses in the bioengineering area with prior departmental approval, with at least six of the nine units at the 500-level

### Review list

- [ ] 'Professional Electives' (under Major) is a rule in words, encoded as one pool; check it. Catalog: "Nine units of additional coursework may be selected from M E 499 (3 units), M E 570 , M E 580 , M E 582 , M E 585 , E E 503 , and other 400- or 500-level courses in the bioengineering area with prior departmental approval, with at least six of the nine units at the 500-level."
- [ ] 'Professional Electives': no lists follow, so the 6 courses named in the rule are a 9-unit pool; titles and units come from the class data. Check it: "Nine units of additional coursework may be selected from M E 499 (3 units), M E 570 , M E 580 , M E 582 , M E 585 , E E 503 , and other 400- or 500-level courses in the bioengineering area with prior departmental approval, with at least six of the nine units at the 500-level."

### Units check (advisory)

- Preparation for the Major: page says 48-49 units, listed courses give 48-49: **inside**
- Major: page says at least 45 units, listed courses give 45: **inside**

### Major notes (no rows made; for a human)

- **Emphasis in Bioengineering**
  - This program requires 120 units to include general education. In addition, the total number of units specified in each elective category represents a minimum requirement.
- **General Education**
  - Engineering majors automatically satisfy Area 2/5. Mathematical Concepts and Quantitative Reasoning or Physical and Biological Sciences and Area 4. Social and Behavioral Explorations GE areas by completion of the major.
- **Graduation Writing Assessment Requirement**
  - Complete M E 490W with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.

### Coverage (sections in data/cleaned)

- Required courses: 27 of 27 have sections
  - with sections: M E 190 (12), M E 202 (4), M E 230 (8), M E 240 (2), M E 241 (6), A E 280 (3), BIOL 203 (2), MATH 150 (12), MATH 151 (20), MATH 252 (13), PHYS 195 (2), PHYS 195L (17), PHYS 196 (1), PHYS 196L (10), M E 304 (3), M E 314 (2), M E 330 (8), M E 340 (6), M E 350 (3), M E 360 (2), M E 430 (2), M E 452 (3), M E 490W (4), M E 491 (8), A E 341 (9), BIOL 336 (1), BIOL 436 (10)
- Pick-n group courses: 6 of 6 have sections
  - with sections: M E 200 (3), A E 200 (3), M E 220 (5), A E 220 (1), CHEM 202 (11), CHEM 200 (49)
- Elective pool courses: 2 of 6 have sections
  - with sections: M E 570 (2), M E 582 (1)
  - no sections: M E 499, M E 580, M E 585, E E 503

### Title differences (catalog vs class data)

- M E 491: catalog "Engineering Design: Senior Project", class data "Senior Projects II"
- M E 570: catalog "", class data "Eng Sensor Tech"
- M E 582: catalog "", class data "Intro to Nanobiotechnolgy"
- 8 more only shortened in the class data (not a real difference): M E 202, M E 240, CHEM 202, M E 314, M E 340, M E 452, M E 490W, A E 341

## Psychology, Emphasis in Industrial and Organizational Psychology, B.A. (`psychology_industrial_organizational_ba`)

- Source: `data/catalog_html/Program_ Psychology, Emphasis in Industrial and Organizational Psychology, B.A. - San Diego State University.html`, poid 12168
- Rows: 27

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 6: PSY 101, PSY 201, PSY 211, PSY 230, PSY 260, PSY 280 |
| Major | Required | required | 4: PSY 319, PSY 370, PSY 420, PSY 421 |
| Major | PSY 301 or PSY 410 (pick 1) | choose 1 | 2: PSY 301, PSY 410 |
| Breadth | Group I (pick 1) | choose 1 | 2: PSY 340, PSY 344 |
| Breadth | Group III (pick 1) | choose 1 | 5: PSY 331, PSY 332, PSY 333, PSY 350, PSY 407 |
| Breadth | Group IV (pick 1) | choose 1 | 5: PSY 360, PSY 361, PSY 362, PSY 380, PSY 388 |
| Upper Division Major Electives | Any PSY 300-599 course | open, 5-6 units | 1: Any PSY 300-599 course |

### Section notes (shown once under the heading)

- **Major**: Methods: All majors must complete PSY 301 or PSY 410 (or both) with a grade of B (3.0) or better. Methods: To enroll in these courses, students must have earned at least a B (3.0) in PSY 280 or an equivalent course
- **Breadth**: All majors must complete three courses or 9 units; one course selected from Groups I, III, and IV:. Group II: Satisfied by emphasis core courses

### Review list

- [ ] Text under 'Methods' kept as the 'Major' section note: "All majors must complete PSY 301 or PSY 410 (or both) with a grade of B (3.0) or better. To enroll in these courses, students must have earned at least a B (3.0) in PSY 280 or an equivalent course."
- [ ] Text under 'Methods' left out (no rule in it; in the report only): "PSY 301 is appropriate for most psychology majors, including those entering the workforce after graduation, exploring career options, or pursuing graduate study in related fields such as counseling. Students planning to pursue research-focused graduate programs in psychology should take PSY 370 and PSY 410 as early as possible. Students who would like additional preparation in statistics or computer skills may benefit from taking PSY 301 before PSY 370 or PSY 410."
- [ ] Text under 'Group II' kept as the 'Breadth' section note: "Satisfied by emphasis core courses."
- [ ] 'Breadth': "All majors must complete three courses or 9 units; one course selected from Groups I, III, and IV:" read as pick 1 in each group.
- [ ] 'Any PSY 300-599 course' in Upper Division Major Electives: "An additional 5-6 elective units selected from 300- to 500-level Psychology courses and WGSS 325 * to satisfy the 31 units required for the Psychology major." encoded as an open rule (PSY 300-599, 5-6 units); check it.
- [ ] 'Any PSY 300-599 course': the page names no subject code; PSY was read from the department name. Check it.
- [ ] Footnote '* WGSS 325 for SDSU Imperial Valley students only.' has no course marked '*'; kept as a major note.
- [ ] Units check for Major: page says at least 31, listed courses add up to 30-32.

### Units check (advisory)

- Preparation for the Major: page says 17 units, listed courses give 17: **inside**
- Major: page says at least 31 units, listed courses give 30-32: **MISMATCH**

### Major notes (no rows made; for a human)

- **Program description**
  - (Academic Plan Code: 778312BALS) (Academic Plan Code: 778312BALI - SDSU Imperial Valley)
  - Also Offered at SDSU Imperial Valley
  - This emphasis offers students an opportunity to complete a four-course sequence (within the scope of a bachelor’s degree in Psychology) that will enhance their competitiveness in the job market and for admission to graduate programs in Industrial and Organizational (I/O) Psychology or related fields. Students will learn about theories, research, and practice in industrial and organizational psychology. Advanced courses will provide opportunities to complete applied projects and written assignments.
  - All candidates for a bachelor’s degree must complete the graduation requirements outlined in the “Graduation Requirements” section of this catalog.
  - A minor is not required for this major. However, depending on career goals, students may wish to consider minors in areas such as biology, business, public administration, recreation, social work, statistics, and others.
- **Impacted Program**
  - The Psychology, Emphasis in Industrial and Organizational Psychology major is an impacted program. To be admitted to the major, students must meet the following criteria:
  - a. Complete with a grade of C (2.0) or better: PSY 101, PSY 211, PSY 230, PSY 260. Complete with a grade of B (3.0) or better: PSY 280. These courses cannot be taken for credit/no credit (Cr/NC). Complete PSY 201 with a grade of Cr (Credit);
  - b. Have a minimum cumulative GPA of 2.5.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See “Graduation Requirements ” section for a complete listing of requirements.
- **Major: Methods**
  - All majors must complete PSY 301 or PSY 410 (or both) with a grade of B (3.0) or better.
  - PSY 301 is appropriate for most psychology majors, including those entering the workforce after graduation, exploring career options, or pursuing graduate study in related fields such as counseling.
  - Students planning to pursue research-focused graduate programs in psychology should take PSY 370 and PSY 410 as early as possible.
  - To enroll in these courses, students must have earned at least a B (3.0) in PSY 280 or an equivalent course.
  - Students who would like additional preparation in statistics or computer skills may benefit from taking PSY 301 before PSY 370 or PSY 410.
- **Major: Group II**
  - Satisfied by emphasis core courses.
- **Recommendations for Psychology Electives**
  - (no text)
- **Recommendations for Psychology Electives: Employment with the B.A.**
  - Electives should be selected in accord with general career goals. Students interested in health and human services may take courses that focus on psychological health and well-being or issues related to child development. Those interested in business may take courses that focus on industrial, organizational and consumer issues or that emphasize computer skills, measurement, data analysis, or some combination of these.
- **Recommendations for Psychology Electives: Masters Programs in Counseling**
  - At SDSU, a Master of Science degree in Counseling is offered by the College of Education and a Master of Social Work degree is offered by the College of Health and Human Services. For these programs students have considerable latitude in the selection of psychology electives, but it is important to develop an appropriate profile of volunteer or work experience.
- **Recommendations for Psychology Electives: Graduate Programs in Psychology**
  - Most masters or doctoral programs in psychology require students to have strong research profiles. SDSU psychology majors can accomplish this by completing PSY 370 , PSY 410 , and becoming involved as early as possible in faculty-sponsored research.
- **Footnotes**
  - * WGSS 325 for SDSU Imperial Valley students only.

### Coverage (sections in data/cleaned)

- Required courses: 10 of 10 have sections
  - with sections: PSY 101 (2), PSY 201 (1), PSY 211 (1), PSY 230 (2), PSY 260 (1), PSY 280 (22), PSY 319 (1), PSY 370 (1), PSY 420 (1), PSY 421 (1)
- Pick-n group courses: 12 of 14 have sections
  - with sections: PSY 301 (20), PSY 410 (2), PSY 340 (2), PSY 344 (1), PSY 331 (1), PSY 332 (1), PSY 333 (1), PSY 350 (3), PSY 407 (1), PSY 360 (1), PSY 380 (1), PSY 388 (1)
  - no sections: PSY 361, PSY 362
- Open rule 'Any PSY 300-599 course' (without excluded and already-required courses): 25 courses with sections: PSY 301, PSY 331, PSY 332, PSY 333, PSY 340, PSY 344, PSY 345, PSY 350, PSY 351, PSY 353, PSY 356, PSY 360, PSY 365, PSY 380, PSY 388, PSY 407, PSY 410, PSY 442, PSY 452, PSY 470, PSY 491, PSY 494, PSY 495, PSY 497, PSY 568

### Title differences (catalog vs class data)

- PSY 420: catalog "Advanced Topics in Industrial Psychology", class data "Workplace Training"
- PSY 421: catalog "Advanced Topics in Organizational Psychology", class data "Worker Stress and Well-Being"

## Psychology, Emphasis in Neuroscience, B.A. (`psychology_neuroscience_ba`)

- Source: `data/catalog_html/Program_ Psychology, Emphasis in Neuroscience, B.A. - San Diego State University.html`, poid 12544, major code 20011
- Rows: 30

### Groups

| Section | Group | Rule | Courses |
| --- | --- | --- | --- |
| Preparation for the Major | Required | required | 6: PSY 101, PSY 201, PSY 211, PSY 230, PSY 260, PSY 280 |
| Major | PSY 301 or PSY 410 (pick 1) | choose 1 | 2: PSY 301, PSY 410 |
| Neuroscience Core | Neuroscience Core | choose 1 | 2: PSY 360, PSY 362 |
| Neuroscience Core Electives | Neuroscience Core Electives | pool, 9 units | 7: PSY 360, PSY 361, PSY 362, PSY 365, PSY 561, PSY 568, PSY 569 |
| Breadth | Group I (pick 1) | choose 1 | 2: PSY 340, PSY 344 |
| Breadth | Group II (pick 1) | choose 1 | 3: PSY 319, PSY 351, PSY 370 |
| Breadth | Group III (pick 1) | choose 1 | 5: PSY 331, PSY 332, PSY 333, PSY 350, PSY 407 |
| Upper Division Major Electives | Any PSY 300-599 course | open, 5-6 units | 1: Any PSY 300-599 course |

### Section notes (shown once under the heading)

- **Major**: Methods: All majors must complete PSY 301 or PSY 410 (or both). Methods: To enroll in these courses, students must have earned at least a B (3.0) in PSY 280 or an equivalent course
- **Breadth**: All majors must complete three courses or 9 units; one course selected from Groups I, II, and III:. Group IV: Satisfied by major core courses

### Review list

- [ ] Text under 'Methods' kept as the 'Major' section note: "All majors must complete PSY 301 or PSY 410 (or both). To enroll in these courses, students must have earned at least a B (3.0) in PSY 280 or an equivalent course."
- [ ] Text under 'Methods' left out (no rule in it; in the report only): "PSY 301 is appropriate for most psychology majors, including those entering the workforce after graduation, exploring career options, or pursuing graduate study in related fields such as counseling. Students planning to pursue doctoral programs in psychology are encouraged to take PSY 410. Students who would like additional preparation in statistics or computer skills may benefit from taking PSY 301 before PSY 410."
- [ ] 'Neuroscience Core' asks for 3 units of one 'or' list (PSY 360 or PSY 362 (pick 1)): read as pick 1; check it.
- [ ] 'Neuroscience Core Electives' (under Major) asks for 9 units of its list: encoded as a pool in its own section 'Neuroscience Core Electives', check it.
- [ ] Text under 'Group IV' kept as the 'Breadth' section note: "Satisfied by major core courses."
- [ ] 'Breadth': "All majors must complete three courses or 9 units; one course selected from Groups I, II, and III:" read as pick 1 in each group.
- [ ] 'Any PSY 300-599 course' in Upper Division Major Electives: "An additional 5-6 elective units selected from 300- to 500-level Psychology courses to satisfy the 31 units required for the Psychology major." encoded as an open rule (PSY 300-599, 5-6 units); check it.
- [ ] 'Any PSY 300-599 course': the page names no subject code; PSY was read from the department name. Check it.
- [ ] Units check for Major: page says at least 31, listed courses add up to 30-32.

### Units check (advisory)

- Preparation for the Major: page says 17 units, listed courses give 17: **inside**
- Major: page says at least 31 units, listed courses give 30-32: **MISMATCH**

### Major notes (no rows made; for a human)

- **Program description**
  - This emphasis offers students an opportunity to complete a four-course sequence (within the scope of a bachelor’s degree in Psychology) that will help them on the job market in research assistant and coordinator positions in neuroscience and related fields as well be more competitive for admission to graduate programs in Neuropsychology and Neuroscience areas. Students will learn about theories, research, and practice in neuroscience. Advanced courses will provide students with opportunities to complete projects and written assignments.
  - All candidates for a bachelor’s degree must complete the graduation requirements outlined in the “Graduation Requirements” section of this catalog.
  - A minor is not required for this major. However, depending on career goals, students may wish to consider minors in areas such as biology, chemistry, gerontology; speech, language, and hearing sciences, and others.
- **Impacted Program**
  - The Psychology, Emphasis in Neuroscience major is an impacted program. To be admitted to the major, students must meet the following criteria:
  - a. Complete with a grade of C (2.0) or better: PSY 101, PSY 230, PSY 280. Complete with a grade of B (3.0) or better: PSY 211, PSY 260. These courses cannot be taken for credit/no credit (Cr/NC). Complete PSY 201 with a grade of Cr (Credit);
  - b. Have a minimum cumulative GPA of 3.0.
  - To complete the major, students must fulfill the degree requirements for the major described in the catalog in effect at the time they are accepted into the premajor at SDSU (assuming continuous enrollment).
- **Graduation Writing Assessment Requirement**
  - Completing one of the approved upper division writing courses (W) with a grade of C (2.0) or better. See Graduation Requirements for a complete listing of requirements.
- **Major: Methods**
  - All majors must complete PSY 301 or PSY 410 (or both).
  - PSY 301 is appropriate for most psychology majors, including those entering the workforce after graduation, exploring career options, or pursuing graduate study in related fields such as counseling.
  - Students planning to pursue doctoral programs in psychology are encouraged to take PSY 410.
  - To enroll in these courses, students must have earned at least a B (3.0) in PSY 280 or an equivalent course.
  - Students who would like additional preparation in statistics or computer skills may benefit from taking PSY 301 before PSY 410.
- **Major: Group IV**
  - Satisfied by major core courses.

### Coverage (sections in data/cleaned)

- Required courses: 6 of 6 have sections
  - with sections: PSY 101 (2), PSY 201 (1), PSY 211 (1), PSY 230 (2), PSY 260 (1), PSY 280 (22)
- Pick-n group courses: 13 of 14 have sections
  - with sections: PSY 301 (20), PSY 410 (2), PSY 360 (1), PSY 340 (2), PSY 344 (1), PSY 319 (1), PSY 351 (2), PSY 370 (1), PSY 331 (1), PSY 332 (1), PSY 333 (1), PSY 350 (3), PSY 407 (1)
  - no sections: PSY 362
- Elective pool courses: 2 of 5 have sections
  - with sections: PSY 365 (1), PSY 568 (2)
  - no sections: PSY 361, PSY 561, PSY 569
- Open rule 'Any PSY 300-599 course' (without excluded and already-required courses): 29 courses with sections: PSY 301, PSY 319, PSY 331, PSY 332, PSY 333, PSY 340, PSY 344, PSY 345, PSY 350, PSY 351, PSY 353, PSY 356, PSY 360, PSY 365, PSY 370, PSY 380, PSY 388, PSY 407, PSY 410, PSY 420, PSY 421, PSY 442, PSY 452, PSY 470, PSY 491, PSY 494, PSY 495, PSY 497, PSY 568

### Title differences (catalog vs class data)

- none

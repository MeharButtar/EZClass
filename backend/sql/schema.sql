-- SDSU Class Scheduler — Database Schema (Phase 1)
-- Written to run on SQLite for local dev; syntax is portable to MySQL with
-- minor tweaks (see notes at the bottom).

DROP TABLE IF EXISTS major_requirements;
DROP TABLE IF EXISTS majors;
DROP TABLE IF EXISTS course_ge;
DROP TABLE IF EXISTS ge_areas;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS section_instructors;
DROP TABLE IF EXISTS section_meetings;
DROP TABLE IF EXISTS sections;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS professors;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS students;

-- Departments/subjects are just a text code on Courses (e.g. 'CS', 'MATH')
-- for Phase 1. A separate Departments table is a natural Phase 3 addition.

CREATE TABLE professors (
    professor_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    email        TEXT,
    department   TEXT NOT NULL
);

-- One row per (building, room) a class meets in. ONLINE is not a room. The
-- room can be blank (a class at another campus, "Southwestern College").
CREATE TABLE rooms (
    room_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    building    TEXT NOT NULL,
    room_number TEXT,                 -- text: keeps leading zeros ('060')
    capacity    INTEGER
);

CREATE TABLE courses (
    course_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    subject      TEXT NOT NULL,       -- e.g. 'CS'
    catalog_num  TEXT NOT NULL,       -- e.g. '514'
    title        TEXT NOT NULL,
    units        INTEGER NOT NULL,
    description  TEXT,
    UNIQUE (subject, catalog_num)
);

-- General Education areas (1A, 1B, 3A ... plus the upper-division Explorations).
CREATE TABLE ge_areas (
    area_code  TEXT PRIMARY KEY,      -- e.g. '3A', 'E3'
    name       TEXT NOT NULL,         -- e.g. 'Arts'
    grp        TEXT NOT NULL,         -- heading it shows under
    sort_order INTEGER NOT NULL
);

-- Which course counts for which GE area. A course can count for more than one
-- area, so this is a many-to-many link between courses and ge_areas.
-- It is keyed by subject + catalog number (not course_id) on purpose: the GE
-- list covers every course SDSU approves, including ones we have no sections
-- for yet. Built by data/ge/parse_ge_guide.py from the catalog's GE page.
CREATE TABLE course_ge (
    course_ge_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    subject             TEXT NOT NULL,
    catalog_num         TEXT NOT NULL,
    title               TEXT,
    units               TEXT,
    area_code           TEXT NOT NULL,
    cultural_diversity  INTEGER NOT NULL DEFAULT 0,   -- the * tag
    ethnic_studies_grad INTEGER NOT NULL DEFAULT 0,   -- also meets the Ethnic Studies graduation requirement
    american_inst       INTEGER NOT NULL DEFAULT 0,   -- [AI] also meets American Institutions
    FOREIGN KEY (area_code) REFERENCES ge_areas(area_code),
    UNIQUE (subject, catalog_num, area_code)
);

-- One row per section a student picks. When it meets lives in section_meetings
-- and who teaches it in section_instructors. professor_id, room_id, days,
-- start_time, end_time and capacity are the older one-meeting columns, kept
-- filled from the first timed meeting (blank for an online-only section).
CREATE TABLE sections (
    section_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id      INTEGER NOT NULL,
    professor_id   INTEGER,           -- first instructor
    room_id        INTEGER,           -- room of the first timed meeting
    section_number TEXT NOT NULL,     -- e.g. '01', '02'
    term           TEXT NOT NULL,     -- e.g. 'Fall 2026'
    days           TEXT,              -- e.g. 'MW', 'TTh', 'MWF'
    start_time     TEXT,              -- 24h 'HH:MM', e.g. '14:00'
    end_time       TEXT,              -- 24h 'HH:MM'
    capacity       INTEGER,           -- same as seats_total
    seats_text     TEXT,              -- as typed: '180 / 45' (seats per component)
    seats_total    INTEGER,           -- smallest part; NULL = unknown
    active         INTEGER NOT NULL DEFAULT 1,   -- 0 = no longer in the sheet (id kept, never reused)
    section_title  TEXT,              -- this section's own title (special topics), else NULL
    class_number   TEXT,              -- official class number students register with ('5834'), else NULL
    retired        INTEGER NOT NULL DEFAULT 0,   -- 1 = retired by import_real_data.py --retire-existing (never matched again)
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (professor_id) REFERENCES professors(professor_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
);

CREATE TABLE students (
    student_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    email       TEXT UNIQUE,
    major       TEXT
);

-- Junction table: many-to-many between students and sections
CREATE TABLE enrollments (
    enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    INTEGER NOT NULL,
    section_id    INTEGER NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    UNIQUE (student_id, section_id)
);

-- meetings:begin
-- When a section meets: one row per meeting (lecture, lab, online part), in
-- the sheet's order. Online meetings have no day, time or room. A section
-- whose schedule isn't entered yet has no rows here. "IF NOT
-- EXISTS" so db.py can add these tables to an older database (see
-- upgrade_sections), filling them from the one-meeting columns.
CREATE TABLE IF NOT EXISTS section_meetings (
    section_id INTEGER NOT NULL,
    idx        INTEGER NOT NULL,      -- 0, 1, 2 in the sheet's order
    day_code   TEXT,                  -- 'MW', 'TTh'; NULL when online
    start_min  INTEGER,               -- minutes after midnight (570 = 9:30); NULL when online
    end_min    INTEGER,
    building   TEXT,                  -- 'GMCS', 'ONLINE', 'Southwestern College'
    room       TEXT,                  -- text: '060'
    is_online  INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (section_id, idx),
    FOREIGN KEY (section_id) REFERENCES sections(section_id)
);

-- Who teaches a section (often more than one person: lecture + lab).
CREATE TABLE IF NOT EXISTS section_instructors (
    section_id   INTEGER NOT NULL,
    professor_id INTEGER NOT NULL,
    idx          INTEGER NOT NULL DEFAULT 0,   -- order in the sheet
    PRIMARY KEY (section_id, professor_id),
    FOREIGN KEY (section_id) REFERENCES sections(section_id),
    FOREIGN KEY (professor_id) REFERENCES professors(professor_id)
);
CREATE INDEX IF NOT EXISTS idx_section_instructors_professor ON section_instructors(professor_id);
-- meetings:end

-- majors:begin
-- Majors and what each one requires, loaded from data/majors/*.csv. "IF NOT
-- EXISTS" so db.py can add just this block to an older database that already
-- has class data (see ensure_database), without dropping anything.
CREATE TABLE IF NOT EXISTS majors (
    major_id     TEXT PRIMARY KEY,    -- e.g. 'cs_bs', used in URLs
    name         TEXT NOT NULL,
    degree       TEXT,                -- e.g. 'B.S.'
    college      TEXT,                -- not shown anywhere (partly unverified)
    catalog_year TEXT,
    status       TEXT NOT NULL DEFAULT 'live'   -- 'live' or 'coming_soon'
);

-- One row per course in a requirement group, or one row per "open" rule.
-- Matched to courses by subject + catalog_num (never by course_id): many
-- required courses have no sections in our data yet and must still show.
CREATE TABLE IF NOT EXISTS major_requirements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,   -- keeps the CSV order
    major_id    TEXT NOT NULL,
    section     TEXT NOT NULL,        -- 'Preparation for the Major', 'Major', ...
    group_label TEXT NOT NULL,        -- 'Required', 'Statistics (pick 1)', ...
    rule        TEXT NOT NULL,        -- required | choose | pool | open
    pick_n      INTEGER,              -- choose: how many courses; open: how many courses (optional)
    pick_units  TEXT,                 -- pool/open: units needed, can be a range like '14-15'
    subject     TEXT,                 -- normalized ('POLS'); open rules may list 'ACCTG|BA|FIN'
    catalog_num TEXT,                 -- text on purpose: '150L', '437A'
    num_min     INTEGER,              -- open rules: lowest catalog number
    num_max     INTEGER,              -- open rules: highest catalog number
    title       TEXT,
    units       TEXT,                 -- text: can be '1-4'
    note        TEXT,
    FOREIGN KEY (major_id) REFERENCES majors(major_id)
);
CREATE INDEX IF NOT EXISTS idx_major_requirements_major ON major_requirements(major_id);
CREATE INDEX IF NOT EXISTS idx_major_requirements_course ON major_requirements(subject, catalog_num);
-- majors:end

CREATE INDEX idx_courses_subject ON courses(subject);
CREATE INDEX idx_sections_course ON sections(course_id);
CREATE INDEX idx_sections_professor ON sections(professor_id);
CREATE INDEX idx_course_ge_course ON course_ge(subject, catalog_num);
CREATE INDEX idx_course_ge_area ON course_ge(area_code);

-- ---------------------------------------------------------------------
-- MySQL notes (for when the team moves this into Workbench):
--   - Replace "INTEGER PRIMARY KEY AUTOINCREMENT" with
--     "INT AUTO_INCREMENT PRIMARY KEY" and column type INT.
--   - TEXT stays TEXT/VARCHAR(n) as appropriate (e.g. VARCHAR(100)).
--   - Everything else (FOREIGN KEY, UNIQUE, INDEX) is valid MySQL as-is.
-- ---------------------------------------------------------------------

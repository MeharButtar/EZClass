-- SDSU Class Scheduler — Database Schema (Phase 1)
-- Written to run on SQLite for local dev; syntax is portable to MySQL with
-- minor tweaks (see notes at the bottom).

DROP TABLE IF EXISTS enrollments;
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

CREATE TABLE rooms (
    room_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    building    TEXT NOT NULL,
    room_number TEXT NOT NULL,
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

CREATE TABLE sections (
    section_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id      INTEGER NOT NULL,
    professor_id   INTEGER,
    room_id        INTEGER,
    section_number TEXT NOT NULL,     -- e.g. '01', '02'
    term           TEXT NOT NULL,     -- e.g. 'Fall 2026'
    days           TEXT NOT NULL,     -- e.g. 'MW', 'TTh', 'MWF'
    start_time     TEXT NOT NULL,     -- 24h 'HH:MM', e.g. '14:00'
    end_time       TEXT NOT NULL,     -- 24h 'HH:MM'
    capacity       INTEGER,
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

CREATE INDEX idx_courses_subject ON courses(subject);
CREATE INDEX idx_sections_course ON sections(course_id);
CREATE INDEX idx_sections_professor ON sections(professor_id);

-- ---------------------------------------------------------------------
-- MySQL notes (for when the team moves this into Workbench):
--   - Replace "INTEGER PRIMARY KEY AUTOINCREMENT" with
--     "INT AUTO_INCREMENT PRIMARY KEY" and column type INT.
--   - TEXT stays TEXT/VARCHAR(n) as appropriate (e.g. VARCHAR(100)).
--   - Everything else (FOREIGN KEY, UNIQUE, INDEX) is valid MySQL as-is.
-- ---------------------------------------------------------------------

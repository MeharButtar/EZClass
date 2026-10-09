"""
Generates synthetic placeholder data for the SDSU Class Scheduler.

Why this exists: the team doesn't need to wait on real scraped/downloaded
SDSU data to start building and testing the app. This script creates fake
but realistic-looking courses, sections, professors, rooms, and students,
including deliberately overlapping sections so conflict-detection logic
can actually be tested.

Run it with:
    python3 generate_placeholder_data.py

It writes CSVs to this same folder: professors.csv, rooms.csv, courses.csv,
sections.csv, students.csv. Those get imported the same way real data will
be (see backend/models/db.py load_csvs(), or MySQL Workbench's import
wizard later).
"""

import csv
import random

random.seed(42)  # reproducible output

SUBJECTS = ["CS", "MATH", "PHYS", "ENGL", "HIST"]

FIRST_NAMES = ["Alex", "Jordan", "Sam", "Taylor", "Morgan", "Casey", "Riley",
               "Jamie", "Drew", "Avery", "Quinn", "Reese"]
LAST_NAMES = ["Nguyen", "Garcia", "Smith", "Patel", "Kim", "Johnson", "Lopez",
              "Chen", "Brown", "Martinez", "Davis", "Wilson"]

BUILDINGS = ["GMCS", "SSE", "PSFA", "EBA", "LOVE"]

DAY_PATTERNS = ["MW", "TTh", "MWF", "TR"]

COURSE_TITLES = {
    "CS": ["Intro to Programming", "Data Structures", "Operating Systems",
           "Database Theory and Implementation", "Networks and Distributed Systems",
           "Intro to AI", "Wireless Networks", "Adv Programming Languages",
           "Software Engineering", "Computer Architecture"],
    "MATH": ["Calculus I", "Calculus II", "Discrete Mathematics",
             "Linear Algebra", "Probability and Statistics"],
    "PHYS": ["Physics for Engineers I", "Physics for Engineers II",
             "Modern Physics"],
    "ENGL": ["Rhetoric and Writing", "American Literature", "Technical Writing"],
    "HIST": ["World History I", "U.S. History", "History of Science"],
}


def make_professors(n=15):
    rows = []
    used_names = set()
    for i in range(1, n + 1):
        while True:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            if (first, last) not in used_names:
                used_names.add((first, last))
                break
        dept = random.choice(SUBJECTS)
        email = f"{first.lower()}.{last.lower()}@sdsu.edu"
        rows.append({
            "professor_id": i,
            "first_name": first,
            "last_name": last,
            "email": email,
            "department": dept,
        })
    return rows


def make_rooms(n=10):
    rows = []
    for i in range(1, n + 1):
        rows.append({
            "room_id": i,
            "building": random.choice(BUILDINGS),
            "room_number": str(random.randint(100, 499)),
            "capacity": random.choice([30, 40, 60, 100, 150]),
        })
    return rows


def make_courses():
    rows = []
    course_id = 1
    for subject, titles in COURSE_TITLES.items():
        for idx, title in enumerate(titles):
            catalog_num = str(100 + idx * 50 + random.randint(0, 9))
            rows.append({
                "course_id": course_id,
                "subject": subject,
                "catalog_num": catalog_num,
                "title": title,
                "units": random.choice([3, 3, 3, 4]),
                "description": f"Placeholder description for {subject} {catalog_num}: {title}.",
            })
            course_id += 1
    return rows


def time_to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m


def make_sections(courses, professors, rooms, sections_per_course=2):
    rows = []
    section_id = 1
    profs_by_dept = {}
    for p in professors:
        profs_by_dept.setdefault(p["department"], []).append(p)

    start_hours = [8, 9, 10, 11, 12, 13, 14, 15, 16]

    for course in courses:
        dept_profs = profs_by_dept.get(course["subject"]) or professors
        for sec_num in range(1, sections_per_course + 1):
            prof = random.choice(dept_profs)
            room = random.choice(rooms)
            start_h = random.choice(start_hours)
            start_time = f"{start_h:02d}:00"
            end_time = f"{start_h + 1:02d}:15" if random.random() < 0.5 else f"{start_h + 1:02d}:50"
            rows.append({
                "section_id": section_id,
                "course_id": course["course_id"],
                "professor_id": prof["professor_id"],
                "room_id": room["room_id"],
                "section_number": f"{sec_num:02d}",
                "term": "Fall 2026",
                "days": random.choice(DAY_PATTERNS),
                "start_time": start_time,
                "end_time": end_time,
                "capacity": room["capacity"],
            })
            section_id += 1

    # Deliberately add a handful of sections that overlap in time and days,
    # so conflict-detection logic has real overlapping cases to catch.
    conflict_course = courses[0]
    conflict_room = rooms[0]
    conflict_prof = professors[0]
    overlap_pairs = [
        ("MW", "10:00", "11:15"),
        ("MW", "10:30", "11:45"),   # overlaps with the row above
        ("TTh", "13:00", "14:15"),
        ("TTh", "13:30", "14:45"),  # overlaps with the row above
    ]
    for days, start, end in overlap_pairs:
        rows.append({
            "section_id": section_id,
            "course_id": conflict_course["course_id"],
            "professor_id": conflict_prof["professor_id"],
            "room_id": conflict_room["room_id"],
            "section_number": f"C{section_id}",
            "term": "Fall 2026",
            "days": days,
            "start_time": start,
            "end_time": end,
            "capacity": conflict_room["capacity"],
        })
        section_id += 1

    return rows


def make_students(n=25, sections=None):
    rows = []
    used_names = set()
    for i in range(1, n + 1):
        while True:
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            if (first, last, i) not in used_names:
                used_names.add((first, last, i))
                break
        email = f"{first.lower()}.{last.lower()}{i}@sdsu.edu"
        rows.append({
            "student_id": i,
            "first_name": first,
            "last_name": last,
            "email": email,
            "major": random.choice(SUBJECTS),
        })
    return rows


def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows -> {path}")


if __name__ == "__main__":
    import os
    out_dir = os.path.dirname(os.path.abspath(__file__))

    professors = make_professors()
    rooms = make_rooms()
    courses = make_courses()
    sections = make_sections(courses, professors, rooms)
    students = make_students()

    write_csv(os.path.join(out_dir, "professors.csv"), professors,
              ["professor_id", "first_name", "last_name", "email", "department"])
    write_csv(os.path.join(out_dir, "rooms.csv"), rooms,
              ["room_id", "building", "room_number", "capacity"])
    write_csv(os.path.join(out_dir, "courses.csv"), courses,
              ["course_id", "subject", "catalog_num", "title", "units", "description"])
    write_csv(os.path.join(out_dir, "sections.csv"), sections,
              ["section_id", "course_id", "professor_id", "room_id", "section_number",
               "term", "days", "start_time", "end_time", "capacity"])
    write_csv(os.path.join(out_dir, "students.csv"), students,
              ["student_id", "first_name", "last_name", "email", "major"])

    print("\nDone. 4 deliberately overlapping sections were added at the end "
          "of sections.csv (section_ids near the top of the range) to test "
          "conflict detection.")

"""
Turns the SDSU catalog's "General Education Requirements" page (saved as a
text file) into data/ge/ge_courses.csv, one row per course per GE area.

Usage (from the project root):
    python3 data/ge/parse_ge_guide.py path/to/ge_guide.txt

Output columns:
    subject, catalog_num, title, units, area_code,
    cultural_diversity, ethnic_studies_grad, american_inst

Area codes: 1A 1B 1C 2 3A 3B 4 5A 5B 5C 6 (lower division)
            E2/5 E3 E4 (upper-division Explorations)
Tags in the catalog: * = cultural diversity, the sideways-hourglass symbol =
Ethnic Studies graduation requirement, [AI] = also counts for American
Institutions. "also listed as X" lines (cross-listed courses) get their own
rows so searching either course code finds the GE area.

Subjects have spaces removed (POL S -> POLS) to match data/import_real_data.py.
"""

import csv
import os
import re
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ge_courses.csv")
FIELDS = ["subject", "catalog_num", "title", "units", "area_code",
          "cultural_diversity", "ethnic_studies_grad", "american_inst"]

COURSE = re.compile(r"^([A-Z]+(?: [A-Z]+)?) (\d{1,3}[A-Z]?) - (.+?) Units: (\d+(?:\.\d+)?)(.*)$")
ALSO = re.compile(r"^also listed as (.+?)\s*$")
CODE = re.compile(r"^([A-Z]+(?: [A-Z]+)?) (\d{1,3}[A-Z]?)$")


def main(path):
    lines = [l.rstrip("\n").strip() for l in open(path, encoding="utf-8-sig")]
    start = max(i for i, l in enumerate(lines) if l == "General Education Areas and Courses")  # the menu at the top has the same text
    end = max(i for i, l in enumerate(lines) if l.startswith("IX. Ethnic Studies Graduation Requirement"))

    rows, area, explore, last = [], None, False, None
    for l in lines[start:end]:
        m = re.match(r"^Area (\d)\. .*\((\d+) units\)$", l)
        if m and not explore:
            area = m.group(1)
            continue
        if l == "Explorations of Human Experience":
            explore = True
            continue
        if explore:
            if l.startswith("Area 2 or 5."):
                area = "E2/5"; continue
            if re.match(r"^Area 3\. ", l):
                area = "E3"; continue
            if re.match(r"^Area 4\. ", l):
                area = "E4"; continue
        m = re.match(r"^([1-5][A-C])\. ", l)
        if m:
            area = m.group(1)
            continue

        m = COURSE.match(l)
        if m and area:
            tags = m.group(5)
            last = {
                "subject": m.group(1).replace(" ", ""),
                "catalog_num": m.group(2),
                "title": m.group(3).strip(),
                "units": m.group(4),
                "area_code": area,
                "cultural_diversity": int("*" in tags),
                "ethnic_studies_grad": int("⌘" in tags),
                "american_inst": int("[AI]" in tags),
            }
            rows.append(last)
            continue
        m = ALSO.match(l)
        if m and last:
            for part in re.split(r",| and ", m.group(1)):
                c = CODE.match(part.strip())
                if c:
                    twin = dict(last)
                    twin["subject"] = c.group(1).replace(" ", "")
                    twin["catalog_num"] = c.group(2)
                    rows.append(twin)

    # drop exact duplicates (same course in the same area)
    seen, out = set(), []
    for r in rows:
        k = (r["subject"], r["catalog_num"], r["area_code"])
        if k not in seen:
            seen.add(k)
            out.append(r)

    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(out)
    print(f"wrote {len(out)} rows -> {OUT}")
    from collections import Counter
    for code, n in sorted(Counter(r["area_code"] for r in out).items()):
        print(f"  {code:5} {n}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

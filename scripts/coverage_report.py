"""
Which required or listed courses have no sections this term?

For every live major (data/majors) and every GE area (data/ge), compares what
the major or area lists with the sections in data/cleaned (active ones only).
Reads the CSVs directly, so it works without building the database.

Usage (from the project root):
    python3 scripts/coverage_report.py

Rules (the "rule" column of major_requirements.csv):
  required -> every course must have sections
  choose   -> at least pick_n of the group's courses must have sections
  pool     -> the offered courses of the pool (all pool groups in one part of
              the major together) must add up to pick_units
  open     -> some course in the subject list and number range must have
              sections (pick_n / pick_units when given)

A course whose sections have no days or times entered yet still counts as
offered (students can add it); the report lists those as "no times yet".
"""

import collections
import csv
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLEANED = os.path.join(ROOT, "data", "cleaned")

# gaps the team already knows about: shown, but marked as known
KNOWN = {
    "BA 404": "not offered this term",
    "ENS 437B": "not offered this term",
    "ISCOR 450": "not offered this term",
    "ACCTG": "ACCTG 400-599 courses are not in the sheet yet",
}


def read(*path):
    with open(os.path.join(ROOT, *path), newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def norm(subject):
    return "".join(str(subject or "").split()).upper()


def number(catalog):
    m = re.match(r"\d+", catalog or "")
    return int(m.group()) if m else None


def units_low(text):
    """'3' -> 3, '1-4' -> 1, '' -> 0"""
    m = re.match(r"\d+", str(text or ""))
    return int(m.group()) if m else 0


def offered_courses():
    """(subject, catalog) -> {"units", "sections", "scheduled"} for courses with active sections.
    scheduled counts the sections that have days and times (or an online part) entered."""
    courses = {r["course_id"]: r for r in read("data", "cleaned", "courses.csv")}
    path = os.path.join(CLEANED, "section_meetings.csv")
    with_meetings = {m["section_id"] for m in read("data", "cleaned", "section_meetings.csv")} if os.path.exists(path) else None
    counts, scheduled = collections.Counter(), collections.Counter()
    for s in read("data", "cleaned", "sections.csv"):
        if s.get("active", "1") != "0":
            counts[s["course_id"]] += 1
            scheduled[s["course_id"]] += with_meetings is None or s["section_id"] in with_meetings
    return {(norm(c["subject"]), c["catalog_num"].strip().upper()):
            {"units": units_low(c["units"]), "sections": counts[cid], "scheduled": scheduled[cid]}
            for cid, c in courses.items() if counts[cid]}


def no_times(keys, offered):
    """The offered courses among keys whose sections all have no days or times yet."""
    return sorted(f"{k[0]} {k[1]}" for k in keys if k in offered and not offered[k]["scheduled"])


def known(code):
    note = KNOWN.get(code) or KNOWN.get(code.split()[0])
    return f"  [known: {note}]" if note else ""


def major_report(offered):
    majors = [m for m in read("data", "majors", "majors.csv") if (m.get("status") or "live").strip() == "live"]
    rows = read("data", "majors", "major_requirements.csv")
    lines, problems = [], 0
    for major in majors:
        mid = major["major_id"].strip()
        groups = collections.OrderedDict()
        for r in rows:
            if r["major_id"].strip() == mid:
                groups.setdefault((r["section"].strip(), r["group_label"].strip(), r["rule"].strip().lower()), []).append(r)
        out = []
        pools = collections.defaultdict(list)       # part of the major -> its pool rows
        for (part, label, rule), items in groups.items():
            codes = [f"{norm(r['subject'])} {r['catalog_num'].strip().upper()}" for r in items if r.get("catalog_num")]
            missing = [c for c in codes if tuple(c.split()) not in offered]
            waiting = no_times([tuple(c.split()) for c in codes], offered)
            if waiting and rule != "pool":
                out.append(f"  no times yet in '{label}' ({len(waiting)}): {', '.join(waiting)}")
            if rule == "required":
                out += [f"  MISSING   {c}  ({part} / {label}){known(c)}" for c in missing]
            elif rule == "choose":
                need = int(items[0]["pick_n"] or 1)
                have = len(codes) - len(missing)
                if have < need:
                    out.append(f"  SHORT     {label}: needs {need}, {have} offered  ({part})")
                if missing:
                    out.append(f"  not offered in '{label}' (pick {need}, {have} of {len(codes)} offered): "
                               + ", ".join(c + known(c).replace("  ", " ") for c in missing))
            elif rule == "pool":
                pools[part] += items
            elif rule == "open":
                for r in items:
                    subjects = [norm(s) for s in (r["subject"] or "").split("|") if s.strip()]
                    low, high = int(r["num_min"] or 0), int(r["num_max"] or 9999)
                    matches = [k for k in offered if k[0] in subjects and number(k[1]) is not None and low <= number(k[1]) <= high]
                    need_n = int(r["pick_n"]) if (r.get("pick_n") or "").strip() else 1
                    need_units = units_low(r.get("pick_units"))
                    have_units = sum(offered[k]["units"] for k in matches)
                    rule_text = f"{'|'.join(subjects)} {low}-{high}"
                    if len(matches) < need_n or have_units < need_units:
                        out.append(f"  SHORT     {label}: any {rule_text} needs {need_n} course(s)"
                                   + (f" / {need_units} units" if need_units else "")
                                   + f", {len(matches)} offered ({have_units} units)  ({part})"
                                   + next((known(s) for s in subjects if known(s)), ""))
                    waiting = no_times(matches, offered)
                    if waiting:
                        out.append(f"  no times yet in '{label}' ({len(waiting)} of {len(matches)} offered {rule_text}): "
                                   + ", ".join(waiting))
                    for s in subjects:
                        if not any(k[0] == s for k in offered):
                            out.append(f"  NOTHING   subject {s} has no sections at all ({label}){known(s)}")
        for part, items in pools.items():
            need = units_low(items[0]["pick_units"])
            codes = [(f"{norm(r['subject'])} {r['catalog_num'].strip().upper()}", units_low(r["units"])) for r in items]
            have = sum(u for c, u in codes if tuple(c.split()) in offered)
            missing = [c for c, _ in codes if tuple(c.split()) not in offered]
            if have < need:
                out.append(f"  SHORT     pool '{part}': needs {need} units, {have} offered")
            waiting = no_times([tuple(c.split()) for c, _ in codes], offered)
            if waiting:
                out.append(f"  no times yet in pool '{part}' ({len(waiting)}): {', '.join(waiting)}")
            if missing:
                out.append(f"  not offered in pool '{part}' ({have} of {sum(u for _, u in codes)} units offered): "
                           + ", ".join(c + known(c).replace("  ", " ") for c in missing))
        problems += sum(1 for line in out if line.lstrip().startswith(("MISSING", "SHORT", "NOTHING"))
                        and "[known:" not in line)
        lines.append(f"{major['name'].strip()} ({mid})")
        lines += out or ["  everything has sections"]
        lines.append("")
    return lines, problems


def ge_report(offered):
    areas = read("data", "ge", "ge_areas.csv")
    listed = collections.defaultdict(list)
    for r in read("data", "ge", "ge_courses.csv"):
        listed[r["area_code"]].append(f"{norm(r['subject'])} {r['catalog_num'].strip().upper()}")
    lines = []
    for a in sorted(areas, key=lambda a: int(a["sort_order"])):
        codes = sorted(set(listed[a["area_code"]]))
        missing = [c for c in codes if tuple(c.split()) not in offered]
        sections = sum(offered[tuple(c.split())]["sections"] for c in codes if tuple(c.split()) in offered)
        flag = "  <-- NO SECTIONS" if codes and len(missing) == len(codes) else ""
        lines.append(f"GE {a['area_code']} {a['name']}: {len(codes) - len(missing)} of {len(codes)} listed courses offered, "
                     f"{sections} sections{flag}")
        if missing:
            lines.append("  zero sections: " + ", ".join(missing))
    return lines


def main():
    offered = offered_courses()
    print(f"Courses with sections this term: {len(offered)}\n")
    print("=== Majors (live) ===\n")
    lines, problems = major_report(offered)
    print("\n".join(lines))
    print("=== GE areas ===\n")
    print("\n".join(ge_report(offered)))
    print(f"\nNew gaps in the majors (not in the known list): {problems}")


if __name__ == "__main__":
    main()

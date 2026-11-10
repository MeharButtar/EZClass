"""
Reads SDSU catalog program pages (Acalog / "Modern Campus Catalog") and writes
major requirement rows in the format data/majors already uses, plus a review
report. It only writes staging files; a person checks them before anything
goes live (see "Majors data" in README.md).

Usage (from the project root):
    python3 scripts/import_catalog_majors.py --discover
        reads the "Programs by Campus Location" page (one request, or a saved
        copy with --listing-html) and writes scripts/catalog_urls.txt with
        every bachelor's program
    python3 scripts/import_catalog_majors.py --urls scripts/catalog_urls.txt --out data/majors/staging
        downloads each program page (cached in data/catalog_html/) and stages it
    python3 scripts/import_catalog_majors.py --html-dir data/catalog_html --out data/majors/staging
        works fully offline on saved pages
    python3 scripts/import_catalog_majors.py --promote me_bs
        copies one reviewed staged major into data/majors (status coming_soon)

Staging output: majors.csv, major_requirements.csv and REPORT.md in --out.

major_ids are used in links, so they never change once made: they live in
scripts/catalog_major_ids.csv (poid -> major_id) and every run reuses it.
Only the standard library is used, so the production image does not change.

How a page becomes rows (decided with Mehar after the Mechanical Engineering review):
  - section is the h2 text, and an h3 list under it is a group (group_label).
  - An electives pool is always its own section, never part of the h2 above it,
    because the app puts a pool's unit counter on its section heading. Two cases:
      * an h3 with a rule in words and no courses ("Professional Electives"):
        it becomes the section, and the h3 lists after it are its pool groups;
      * an h3 list asking for fewer units than it lists: the h3 becomes the section.
  - A rule the app cannot express ("6 units from one area, at least 3 at the 500
    level") becomes one pool for the whole total, with the full catalog sentence
    as the note, and goes on the review list. When the rule gives no single
    total, pick_units is what the h2 total leaves after its other rows.
  - A course in more than one pool group of one section keeps one row (the
    first), with "Also listed under <other group>", and goes on the review list.
  - "or" makes a pick-1 group; "also listed as" makes a pick-1 group noted
    "Cross-listed" (inside a pool the pair stays as pool rows, noted).
  - General Education, Graduation Writing, Master Plan, Impacted Program, Major
    Restriction and advising text make no rows; they go to the report as major notes.
"""

import argparse
import collections
import csv
import html
import importlib.util
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE_DIR = os.path.join(ROOT, "data", "majors")
STAGING_DIR = os.path.join(LIVE_DIR, "staging")
CACHE_DIR = os.path.join(ROOT, "data", "catalog_html")
IDS_FILE = os.path.join(ROOT, "scripts", "catalog_major_ids.csv")
URLS_FILE = os.path.join(ROOT, "scripts", "catalog_urls.txt")

CATALOG_ID = "12"
CATALOG_YEAR = "2026-2027"
SITE = "https://catalog.sdsu.edu"
LISTING_URL = f"{SITE}/content.php?catoid={CATALOG_ID}&navoid=1153"
USER_AGENT = "EzClass-catalog-reader"
SECONDS_BETWEEN_REQUESTS = 1.0

MAJOR_FIELDS = ["major_id", "name", "degree", "college", "catalog_year", "status"]
REQ_FIELDS = ["major_id", "section", "group_label", "rule", "pick_n", "pick_units", "subject", "catalog_num",
              "num_min", "num_max", "title", "units", "note"]

# the 7 majors the app already has, by catalog program id (poid); these ids never change
KNOWN_IDS = {
    "11969": "cs_bs",            # Computer Science, B.S.
    "12498": "psych_ba",         # Psychology, B.A.
    "11935": "ba_general_bs",    # Business Administration, Emphasis in General Business, B.S.
    "12120": "ba_marketing_bs",  # Business Administration, Emphasis in Marketing, B.S.
    "11974": "crim_justice",     # Criminal Justice, B.S.
    "12006": "kin_prept",        # Kinesiology, Emphasis in Prephysical Therapy, B.S.
    "12130": "me_bs",            # Mechanical Engineering, B.S.
}

BACHELOR = re.compile(r"(?<![A-Za-z.])(B\.F\.A\.|B\.A\.|B\.S\.|B\.M\.)")
COMBINED = re.compile(r"4\+1|\bB[AS]/M[AS]\b")
# credential prep and other special programs: processed, but always reviewed
SPECIAL = re.compile(r"Credential|\bITEP\b|Honors|Second Bachelor|Registered Nurse", re.I)

# h2 blocks that are not course requirements: their text goes to the report as major notes
NOTE_BLOCKS = re.compile(r"general education|graduation writing|master plan|impacted|major restriction|advising"
                         r"|roadmap", re.I)
GWAR_BLOCK = re.compile(r"graduation writing", re.I)

GRADE_C = re.compile(r"must be completed with a grade of C \(2\.0\) or better\.?\s*These courses cannot be taken "
                     r"for credit/no credit \(Cr/NC\)\.?", re.I)
GRADE_C_NOTE = "Grade of C or better, no Cr/NC"
GWAR_NOTE = "Satisfies the Graduation Writing Assessment"
CROSS_NOTE = "Cross-listed"

COURSE_TEXT = re.compile(r"^([A-Z][A-Z ]*?)\s+(\d{1,3}[A-Z]{0,3})\s+-\s+(.+)$")
UNITS_ONLY = re.compile(r"^\(?\s*(\d+)(?:\s*[-–]\s*(\d+))?\s+units?\s*\)?\.?$", re.I)
UNITS_MINIMUM = re.compile(r"^(?:a\s+)?minimum of\s+(\d+)\s+(?:upper[- ]division\s+)?units?(?:\s+to include)?:?$", re.I)
UNIT_AMOUNT = re.compile(r"\b(\d+)(?:\s*[-–]\s*(\d+))?\s+units?\b", re.I)


def clean(text):
    """Non-breaking spaces to spaces, runs of whitespace to one space."""
    return re.sub(r"\s+", " ", html.unescape(text or "").replace("\xa0", " ")).strip()


def subject_key(subject):
    """'M E' -> 'ME' (the app's form)"""
    return "".join(subject.split()).upper()


def code(subject, catalog_num):
    return f"{subject} {catalog_num}"


# ---------- a small HTML tree (html.parser only) ----------

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Node:
    def __init__(self, tag, attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs or {}), parent, []

    def classes(self):
        return set((self.attrs.get("class") or "").split())

    def text(self):
        return clean("".join(c if isinstance(c, str) else c.text_raw() for c in self.children))

    def text_raw(self):
        return "".join(c if isinstance(c, str) else c.text_raw() for c in self.children)

    def walk(self, stop=None):
        """Every descendant element in document order; does not go inside nodes where stop(node) is true."""
        for c in self.children:
            if isinstance(c, Node):
                yield c
                if not (stop and stop(c)):
                    yield from c.walk(stop)

    def find(self, pred):
        return next((n for n in self.walk() if pred(n)), None)


class TreeBuilder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root")
        self.current = self.root
        self.comments = []

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.current.children.append(Node(tag, attrs, self.current))

    def handle_endtag(self, tag):
        node = self.current
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:          # a stray end tag is ignored
            self.current = node.parent

    def handle_data(self, data):
        self.current.children.append(data)

    def handle_comment(self, data):
        self.comments.append(data)


def parse_html(text):
    builder = TreeBuilder()
    builder.feed(text)
    builder.close()
    return builder.root, builder.comments


def is_core(node):
    return node.tag == "div" and "acalog-core" in node.classes()


# ---------- program pages ----------

def split_title(title):
    """'Business Administration, Emphasis in Marketing, B.S.' -> ('Business Administration, Emphasis in Marketing', 'B.S.', ok)
    ok is False when the degree is not at the end, so the name is a best effort."""
    title = clean(title)
    m = BACHELOR.search(title)
    if not m:
        return title, "", False
    degree = m.group(1)
    if title.endswith(", " + degree):
        return title[: -len(", " + degree)].strip(), degree, True
    name = (title[: m.start()] + title[m.end():])
    name = re.sub(r"\s*,\s*(?:-\s*)?,?\s*", ", ", name)
    name = re.sub(r"\s+-\s*$|^\s*-\s+", "", name)
    name = re.sub(r"\s+,", ",", re.sub(r"\s{2,}", " ", name)).strip(" ,-")
    name = re.sub(r",?\s*with the$", "", name)     # 'Social Science, in Preparation ..., with the B.A.'
    return name, degree, False


def find_poid(text, comments, url=None):
    for source in [url or ""] + [c for c in comments if "saved from url" in c]:
        m = re.search(r"[?&]poid=(\d+)", source)
        if m:
            return m.group(1), re.search(r"[?&]catoid=(\d+)", source).group(1) if "catoid=" in source else None
    m = re.search(r'rel="canonical"[^>]*href="[^"]*poid=(\d+)', text)
    if m:
        return m.group(1), None
    counts = collections.Counter(re.findall(r"preview_program\.php\?catoid=\d+&(?:amp;)?poid=(\d+)[^\"']*returnto", text))
    return (counts.most_common(1)[0][0], None) if counts else (None, None)


def parse_course(li):
    """li.acalog-course -> dict(subject, catalog_num, title, units, extra) or None."""
    link = li.find(lambda n: n.tag == "a")
    if not link:
        return None
    m = COURSE_TEXT.match(link.text())
    if not m:
        return None
    subject, num, title = m.group(1).strip(), m.group(2).upper(), m.group(3).strip()
    full = li.text()
    after = full[full.find(link.text()) + len(link.text()):] if link.text() in full else ""
    units, extra = "", after.strip()
    um = re.match(r"\s*Units:\s*(\d+(?:\s*[-–]\s*\d+)?(?:\s+or\s+\d+)?)\s*(.*)$", after, re.S)
    if um:
        units = re.sub(r"\s*[-–]\s*", "-", um.group(1)).strip()
        extra = um.group(2).strip()
    return {"subject": subject, "catalog_num": num, "title": title, "units": units, "extra": extra}


def read_blocks(root):
    """Every div.acalog-core in order: heading level and text, own paragraphs, own list items."""
    blocks = []
    for core in (n for n in root.walk() if is_core(n)):
        own = list(core.walk(stop=lambda n: is_core(n) or n.tag == "li"))
        heading = next((n for n in own if n.tag in ("h2", "h3", "h4", "h5")), None)
        items = []
        for li in (n for n in core.walk(stop=is_core) if n.tag == "li"):
            cls = li.classes()
            if "acalog-course" in cls:
                course = parse_course(li)
                items.append(("course", course) if course else ("text", li.text()))
            elif "acalog-adhoc" in cls:
                t = li.text().strip().lower()
                items.append(("or", None) if t == "or" else ("also", None) if t == "also listed as"
                             else ("sep", None) if not t else ("text", li.text()))
            else:
                items.append(("text", li.text()))
        blocks.append({
            "level": int(heading.tag[1]) if heading else 0,
            "heading": heading.text() if heading else "",
            "paras": [p.text() for p in own if p.tag == "p" and p.text()],
            "items": items,
        })
    return blocks


def description_notes(root):
    """The program description above the requirement blocks, as (heading, text) pairs."""
    box = root.find(lambda n: n.tag == "div" and "program_description" in n.classes())
    if not box:
        return []
    notes, heading = [], "Program description"
    for node in box.walk(stop=lambda n: n.tag in ("p", "h2", "h3", "h4", "h5", "li")):
        text = node.text()
        if not text or node.tag not in ("p", "h2", "h3", "h4", "h5", "li"):
            continue
        if text.startswith("(Major Code") or "Roadmap" in text and node.find(lambda n: n.tag == "a"):
            continue
        strong_only = node.tag == "p" and len([c for c in node.children if isinstance(c, Node) or c.strip()]) == 1 \
            and isinstance(node.children[0] if node.children else None, Node) and node.children[0].tag in ("strong", "b") \
            and len(text) < 80
        if node.tag.startswith("h") or strong_only:
            heading = text
            continue
        notes.append((heading, text))
    return notes


def units_range(text):
    """'3' -> (3, 3), '1-4' -> (1, 4), '3 or 4' -> (3, 4), '' -> (0, 0)"""
    nums = [int(n) for n in re.findall(r"\d+", text or "")]
    return (min(nums), max(nums)) if nums else (0, 0)


def stated_units(paragraph):
    """'(48-49 units)' -> (48, 49, 'exact'); 'A minimum of 45 upper division units to include:' -> (45, None, 'minimum')"""
    m = UNITS_ONLY.match(paragraph)
    if m:
        low = int(m.group(1))
        return low, int(m.group(2) or low), "exact"
    m = UNITS_MINIMUM.match(paragraph)
    if m:
        return int(m.group(1)), None, "minimum"
    return None


def course_note(course, gwar_codes):
    parts = []
    extra = course["extra"]
    if GRADE_C.search(extra):
        parts.append(GRADE_C_NOTE)
        extra = clean(GRADE_C.sub("", extra))
    if extra:
        parts.append(extra)
    if code(course["subject"], course["catalog_num"]) in gwar_codes:
        parts.append(GWAR_NOTE)
    return parts


def join_note(parts):
    out = []
    for p in parts:
        p = p.strip().rstrip(".")
        if p and p not in out:
            out.append(p)
    return ". ".join(out)


def chains(items):
    """Course items joined by 'or' / 'also listed as' into chains.
    Returns [(courses, joiners, loose)] where loose is True when an 'or' chain
    touches a neighbouring course with no blank separator (the 'or' might cover several courses)."""
    out, i = [], 0
    while i < len(items):
        kind, value = items[i]
        if kind != "course":
            i += 1
            continue
        courses, joiners = [value], []
        j = i + 1
        while j + 1 < len(items) and items[j][0] in ("or", "also") and items[j + 1][0] == "course":
            joiners.append(items[j][0])
            courses.append(items[j + 1][1])
            j += 2
        loose = False
        if "or" in joiners:
            before = items[i - 1][0] if i > 0 else "sep"
            after = items[j][0] if j < len(items) else "sep"
            loose = before == "course" or after == "course"
        out.append((courses, joiners, loose, i))
        i = j
    return out


def chain_label(courses, joiners):
    names = [code(c["subject"], c["catalog_num"]) for c in courses]
    if set(joiners) == {"also"}:
        return " / ".join(names) + " (same course, pick 1)"
    if set(joiners) == {"or"}:
        return " or ".join(names) + " (pick 1)"
    text = names[0]
    for joiner, name in zip(joiners, names[1:]):
        text += (" or " if joiner == "or" else " / ") + name
    return text + " (pick 1)"


class Program:
    def __init__(self, source):
        self.source = source
        self.poid = self.catoid = None
        self.title = self.name = self.degree = ""
        self.major_code = ""
        self.major_id = ""
        self.rows = []
        self.notes = []          # (heading, text)
        self.review = []         # sentences for a human
        self.units_checks = []   # (heading, stated text, listed text, verdict)
        self.derived = set()     # h2 headings whose pool units were worked out from the h2 total
        self.special = False

    def flag(self, text):
        if text not in self.review:
            self.review.append(text)


def parse_program(text, source="", url=None):
    root, comments = parse_html(text)
    prog = Program(source)
    prog.poid, prog.catoid = find_poid(text, comments, url)
    h1 = root.find(lambda n: n.tag == "h1" and n.attrs.get("id") == "acalog-page-title") or root.find(lambda n: n.tag == "h1")
    prog.title = h1.text() if h1 else ""
    prog.name, prog.degree, plain = split_title(prog.title)
    if not prog.degree:
        prog.flag(f"No bachelor's degree in the page title '{prog.title}'.")
    elif not plain:
        prog.flag(f"Name '{prog.name}' was built from an unusual title '{prog.title}'; check it.")
    if prog.catoid and prog.catoid != CATALOG_ID:
        prog.flag(f"Page is from catalog catoid={prog.catoid}, not {CATALOG_ID} ({CATALOG_YEAR}).")
    m = re.search(r"Major Code:\s*([\w-]+)", text)
    prog.major_code = m.group(1) if m else ""
    prog.special = bool(SPECIAL.search(prog.title))
    if prog.special:
        prog.flag("Credential-prep or special program: check every group against the catalog page.")
    prog.notes = description_notes(root)
    map_blocks(prog, read_blocks(root))
    return prog


def map_blocks(prog, blocks):
    gwar_codes = set()
    for b in blocks:
        if b["level"] == 2 and GWAR_BLOCK.search(b["heading"]):
            gwar_codes |= {code(v["subject"], v["catalog_num"]) for k, v in b["items"] if k == "course"}
    used_codes = set()

    h2 = None                 # current h2 heading
    h2_is_note = False
    parent = None             # an h3 with a rule but no courses: the following h3 lists are its groups
    totals = collections.OrderedDict()   # h2 -> stated units (low, high, kind)
    pending_pool = []         # pool rows waiting for pick_units, per parent heading

    def finish_parent():
        nonlocal parent, pending_pool
        if parent and pending_pool:
            units = parent["units"]
            if units is None:
                units = derive_pool_units(h2_rows_for(parent["h2"]), totals.get(parent["h2"]), pending_pool)
                parent["units"] = units
                if units:
                    prog.derived.add(parent["h2"])
                    prog.flag(f"'{parent['heading']}': pool set to {units} units, worked out from the "
                              f"{parent['h2']} total minus its other courses.")
                else:
                    prog.flag(f"'{parent['heading']}': could not work out how many units the pool needs; "
                              f"pick_units is blank.")
            for row in pending_pool:
                row["pick_units"] = units or ""
            dedupe_pool(prog, parent["heading"], pending_pool)
        elif parent and not pending_pool:
            prog.flag(f"'{parent['heading']}' has a rule but no course lists followed it: {parent['rule']}")
        parent, pending_pool = None, []

    def h2_rows_for(name):
        return [r for r in prog.rows if r.get("_h2") == name]

    for b in blocks:
        courses = [v for k, v in b["items"] if k == "course"]
        if b["level"] in (0, 2):
            finish_parent()
            h2 = b["heading"] or "(no heading)"
            h2_is_note = bool(NOTE_BLOCKS.search(h2))
            if h2_is_note:
                listed = ", ".join(code(c["subject"], c["catalog_num"]) for c in courses)
                body = " ".join(b["paras"]) + (f" Courses listed: {listed}." if listed else "")
                prog.notes.append((h2, body.strip() or "(no text)"))
                continue
            if not courses:
                # a heading whose lists (if any) are in the h3 blocks that follow
                for p in b["paras"]:
                    s = stated_units(p)
                    if s and h2 not in totals:
                        totals[h2] = s
                    else:
                        prog.notes.append((h2, p))
                        prog.flag(f"Text under '{h2}' was not read as a rule (no courses in that block): \"{p}\"")
                continue
        elif h2_is_note:
            prog.notes.append((f"{h2}: {b['heading']}", " ".join(b["paras"])))
            continue

        section = h2
        label = "Required"
        rule_paras, stated = [], None
        for p in b["paras"]:
            s = stated_units(p)
            if s and stated is None:
                stated = s
            else:
                rule_paras.append(p)
        if b["level"] == 2 and stated:
            totals[h2] = stated

        if b["level"] >= 3:
            if not courses:
                finish_parent()
                rule = " ".join(rule_paras)
                parent = {"heading": b["heading"], "h2": h2, "rule": rule, "units": None}
                amounts = UNIT_AMOUNT.findall(rule)
                if stated:
                    parent["units"] = f"{stated[0]}-{stated[1]}" if stated[1] and stated[1] != stated[0] else str(stated[0])
                elif len(amounts) == 1:
                    low, high = amounts[0]
                    parent["units"] = f"{low}-{high}" if high else low
                if rule:
                    prog.flag(f"'{b['heading']}' (under {h2}) is a rule in words, encoded as one pool; check it. "
                              f"Catalog: \"{rule}\"")
                continue
            label = b["heading"]
            if parent:
                section = parent["heading"]
            else:
                finish_parent()
        else:
            finish_parent()

        in_pool = bool(parent) and b["level"] >= 3
        block_note = rule_paras[:]
        for kind, value in b["items"]:
            if kind == "text" and value.strip():
                block_note.append(value)
                prog.flag(f"'{label}' in {section}: text between courses that was not read as a rule: \"{value}\"")
        if rule_paras and not in_pool:
            prog.flag(f"'{label}' in {section}: rule text kept as the note, check the group: \"{' '.join(rule_paras)}\"")

        required, groups = [], []
        for chain, joiners, loose, _ in chains(b["items"]):
            if len(chain) == 1:
                required.append(chain[0])
                continue
            if loose:
                prog.flag(f"{chain_label(chain, joiners)} in {section}: the 'or' sits next to other courses with "
                          f"no break, so it may cover more than one course. Check the catalog page.")
            if set(joiners) == {"or", "also"}:
                prog.flag(f"{chain_label(chain, joiners)} in {section} mixes 'or' and 'also listed as'; check it.")
            groups.append((chain, joiners))

        def row(course, rule, group_label, note_parts, pick_n=""):
            used_codes.add(code(course["subject"], course["catalog_num"]))
            r = {
                "major_id": "", "section": section, "group_label": group_label, "rule": rule, "pick_n": pick_n,
                "pick_units": "", "subject": subject_key(course["subject"]), "catalog_num": course["catalog_num"],
                "num_min": "", "num_max": "", "title": course["title"], "units": course["units"],
                "note": join_note(note_parts), "_h2": h2, "_code": code(course["subject"], course["catalog_num"]),
            }
            prog.rows.append(r)
            return r

        if in_pool:
            if parent["rule"]:
                block_note = [parent["rule"]] + block_note
            for chain, joiners, _, _ in chains(b["items"]):       # page order
                if len(chain) == 1:
                    course = chain[0]
                    pending_pool.append(row(course, "pool", label, block_note + course_note(course, gwar_codes)))
                    continue
                for course in chain:
                    others = [code(c["subject"], c["catalog_num"]) for c in chain if c is not course]
                    tie = f"{CROSS_NOTE} with {', '.join(others)}" if set(joiners) == {"also"} else f"Or {', '.join(others)}"
                    pending_pool.append(row(course, "pool", label, block_note + [tie] + course_note(course, gwar_codes)))
                prog.flag(f"{chain_label(chain, joiners)} in the '{label}' pool: kept as pool rows with a note "
                          f"(a pick-1 group inside a units pool would be counted on its own).")
            continue

        pool_units = None
        if stated and b["level"] >= 3:
            listed_low = sum(units_range(c["units"])[0] for c in required) + \
                sum(min(units_range(c["units"])[0] for c in chain) for chain, _ in groups)
            if listed_low > stated[0] and stated[2] == "exact":
                pool_units = f"{stated[0]}-{stated[1]}" if stated[1] != stated[0] else str(stated[0])
                prog.flag(f"'{label}' in {section} lists {listed_low} units but asks for {pool_units}: "
                          f"encoded as a pool in its own section '{label}', check it.")
                section = label        # an electives pool is always its own section (see the docstring)
        for course in required:
            if pool_units:
                row(course, "pool", label, block_note + course_note(course, gwar_codes))["pick_units"] = pool_units
            else:
                row(course, "required", label, block_note + course_note(course, gwar_codes))
        for chain, joiners in groups:
            group_label = chain_label(chain, joiners)
            if b["level"] >= 3:
                group_label = f"{label}: {group_label}"
            for course in chain:
                extra = [CROSS_NOTE] if set(joiners) == {"also"} else []
                row(course, "choose", group_label, block_note + extra + course_note(course, gwar_codes), pick_n="1")
    finish_parent()

    for c in sorted(gwar_codes - used_codes):
        prog.notes.append(("Graduation Writing Assessment Requirement", f"{c} is listed for the GWAR but not in the major lists."))

    order_rows(prog)
    check_units(prog, totals)


def dedupe_pool(prog, section, pool_rows):
    """A course in more than one pool group of one section (M E 544 in Mechanical and Thermal Systems):
    keep the first row, note the other groups on it, drop the rest (the pool counter adds units per row)."""
    first, dropped = {}, set()
    for r in pool_rows:
        keep = first.get(r["_code"])
        if keep is None:
            first[r["_code"]] = r
            continue
        if r["group_label"] != keep["group_label"]:
            keep["note"] = join_note([keep["note"], f"Also listed under {r['group_label']}"])
        dropped.add(id(r))
        prog.flag(f"{r['_code']} is listed under both '{keep['group_label']}' and '{r['group_label']}' in "
                  f"'{section}': kept once, under '{keep['group_label']}', with an \"Also listed under\" note.")
    if dropped:
        prog.rows = [r for r in prog.rows if id(r) not in dropped]
        pool_rows[:] = [r for r in pool_rows if id(r) not in dropped]


def derive_pool_units(h2_rows, total, pool_rows):
    """A rule in words ('6 units ... and 6 units ...'): the units are what the h2 total leaves after its other rows."""
    if not total:
        return ""
    pool_ids = {id(r) for r in pool_rows}
    other = [r for r in h2_rows if id(r) not in pool_ids]
    low, high = listed_units(other)
    need_low = total[0] - high
    need_high = (total[1] if total[1] is not None else total[0]) - low
    if need_low <= 0 and need_high <= 0:
        return ""
    need_low = max(need_low, 0)
    return str(need_low) if need_low == need_high else f"{min(need_low, need_high)}-{max(need_low, need_high)}"


def listed_units(rows):
    """Lowest and highest units the rows add up to: required rows, the cheapest/dearest course of each pick-n
    group, each pool section's pick_units, each open row's pick_units."""
    low = high = 0
    groups = collections.OrderedDict()
    pools = {}
    for r in rows:
        if r["rule"] == "required":
            a, b = units_range(r["units"])
            low, high = low + a, high + b
        elif r["rule"] == "choose":
            groups.setdefault((r["section"], r["group_label"]), []).append(r)
        elif r["rule"] in ("pool", "open"):
            pools[(r["section"], r["group_label"] if r["rule"] == "open" else "")] = r["pick_units"]
    for items in groups.values():
        n = int(items[0]["pick_n"] or 1)
        lows = sorted(units_range(r["units"])[0] for r in items)
        highs = sorted((units_range(r["units"])[1] for r in items), reverse=True)
        low, high = low + sum(lows[:n]), high + sum(highs[:n])
    for units in pools.values():
        a, b = units_range(units)
        low, high = low + a, high + b
    return low, high


def order_rows(prog):
    """Within each section: the Required group first, then the other groups in page order (like the existing rows)."""
    sections = collections.OrderedDict()
    for r in prog.rows:
        sections.setdefault(r["section"], []).append(r)
    ordered = []
    for rows in sections.values():
        ordered += [r for r in rows if r["group_label"] == "Required"] + [r for r in rows if r["group_label"] != "Required"]
    prog.rows = ordered


def check_units(prog, totals):
    for h2, (low_stated, high_stated, kind) in totals.items():
        rows = [r for r in prog.rows if r["_h2"] == h2]
        low, high = listed_units(rows)
        if kind == "exact":
            stated = f"{low_stated}-{high_stated}" if high_stated != low_stated else str(low_stated)
            ok = low_stated <= low <= high_stated or low_stated <= high <= high_stated or (low <= low_stated and high >= high_stated)
            inside = low_stated <= low and high <= high_stated
            verdict = "inside" if inside else "overlaps" if ok else "MISMATCH"
        else:
            stated = f"at least {low_stated}"
            verdict = "inside" if low >= low_stated else "MISMATCH"
        listed = f"{low}-{high}" if low != high else str(low)
        derived = " (elective units were worked out from this total)" if h2 in prog.derived else ""
        prog.units_checks.append((h2, stated, listed, verdict + derived))
        if verdict == "MISMATCH":
            prog.flag(f"Units check for {h2}: page says {stated}, listed courses add up to {listed}.")


# ---------- major ids ----------

ID_STOP = {"and", "of", "in", "the", "for", "with", "a", "an", "to", "emphasis", "specialization", "concentration",
           "track", "plus"}


DEGREE_SLUGS = {"ba", "bs", "bm", "bfa", "ma", "ms", "mba", "phd"}
# major names that have commas of their own, with the short form SDSU uses
BASE_NAMES = {
    "Business Administration": "ba",     # the existing ids: ba_general_bs, ba_marketing_bs
    "Television, Film and New Media": "tfm",
    "Lesbian, Gay, Bisexual, Transgender, Queer, and Plus (LGBTQ+) Studies": "lgbtq",
    "Language, Culture, and Society": "lcs",
    "Speech, Language, and Hearing Sciences": "slhs",
}
# long phrases in a program name, shortened for its id
ID_PHRASES = [
    (r"in preparation for the single subject teaching credential.*?(?=,|$)", "credential"),
    (r"preparation for the single subject teaching credential.*?(?=,|$)", "credential"),
    (r"second bachelor[’']?s degree", "second"),
    (r"certificate of the american chemical society", "acs"),
]


def slug_words(text):
    words = re.findall(r"[a-z0-9]+", text.lower().replace("’", "").replace("'", ""))
    return [w for w in words if w not in ID_STOP]


def degree_slug(degree):
    return re.sub(r"[^a-z]", "", degree.lower())


def id_parts(name):
    """'Civil Engineering, ...' -> (base 'Civil Engineering', short 'ce', full 'civil_engineering', rest)."""
    for base, short in BASE_NAMES.items():
        if name == base or name.startswith(base + ","):
            return base, short, short, name[len(base):]
    base, _, rest = name.partition(",")
    words = slug_words(base) or ["major"]
    full = "_".join(words)
    short = words[0] if len(words) == 1 else "".join(w[0] for w in words)
    if short in DEGREE_SLUGS:      # 'Brazilian Studies' -> 'bs' would read like a degree
        short = full
    return base.strip(), short, full, rest


def propose_id(name, degree, full=False, extra=2):
    """'Civil Engineering', 'B.S.' -> 'ce_bs'; 'Business Administration, Emphasis in Accounting' -> 'ba_accounting_bs'.
    full=True spells the base name out ('civil_engineering_bs'); extra is how many emphasis words to keep."""
    _, short, full_head, rest = id_parts(name)
    head = full_head if full else short
    for pattern, word in ID_PHRASES:
        rest = re.sub(pattern, f" {word} ", rest, flags=re.I)
    skip = set(head.split("_")) if head == full_head else set()   # no 'music_music_education'
    words = [w for w in slug_words(rest) if w not in skip][:extra]
    return "_".join([head] + words + [degree_slug(degree) or "x"])


def read_ids(path=IDS_FILE):
    if not os.path.exists(path):
        return collections.OrderedDict()
    with open(path, newline="", encoding="utf-8") as f:
        return collections.OrderedDict((r["poid"], r) for r in csv.DictReader(f) if r.get("poid"))


def write_ids(ids, path=IDS_FILE):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["poid", "major_id", "name", "degree"], lineterminator="\n")
        w.writeheader()
        w.writerows(ids.values())


def assign_ids(programs, ids, log):
    """Gives every program its major_id: the ids file first, then the 7 known ids, then a new one.
    New ids are added to `ids`; collisions are logged. Existing ids are never changed."""
    taken = {r["major_id"]: poid for poid, r in ids.items()}
    taken.update({mid: poid for poid, mid in KNOWN_IDS.items()})
    new = [p for p in programs if (p.poid or "") not in ids and (p.poid or "") not in KNOWN_IDS]

    # initials shared by different majors (Civil / Computer / Construction Engineering -> 'ce'):
    # every one of them is spelled out, so no major gets the short form just for coming first
    bases = collections.defaultdict(set)
    for name in [r.get("name", "") for r in ids.values()] + [p.name for p in programs]:
        base, short, _, _ = id_parts(name)
        bases[short].add(base)
    proposals = {}
    for p in new:
        base, short, _, _ = id_parts(p.name)
        spelled = len(bases[short]) > 1
        if spelled:
            log.append(f"'{short}' would fit {', '.join(sorted(bases[short]))}: {p.name}, {p.degree} is spelled out")
        proposals[id(p)] = (spelled, propose_id(p.name, p.degree, full=spelled))
    # the same id for two new programs, or an id already taken: more emphasis words for each of them
    counts = collections.Counter(mid for _, mid in proposals.values())
    for p in new:
        spelled, mid = proposals[id(p)]
        if counts[mid] > 1 or mid in taken:
            longer = propose_id(p.name, p.degree, full=spelled, extra=6)
            if longer != mid:
                log.append(f"id collision on '{mid}': {p.name}, {p.degree} (poid {p.poid}) gets '{longer}'")
            proposals[id(p)] = (spelled, longer)

    changed = False
    for prog in programs:
        poid = prog.poid or ""
        if poid in ids:
            prog.major_id = ids[poid]["major_id"]
            continue
        mid = KNOWN_IDS[poid] if poid in KNOWN_IDS else proposals[id(prog)][1]
        if mid in taken and taken[mid] != poid:
            n = 2
            while f"{mid}_{n}" in taken:
                n += 1
            log.append(f"id collision on '{mid}' (still taken): {prog.name}, {prog.degree} gets '{mid}_{n}'")
            mid = f"{mid}_{n}"
        if not re.fullmatch(r"[a-z0-9_]+", mid):
            raise SystemExit(f"bad major_id {mid!r} for {prog.name}, {prog.degree}")
        prog.major_id = mid
        taken[mid] = poid
        if poid:
            ids[poid] = {"poid": poid, "major_id": mid, "name": prog.name, "degree": prog.degree}
            changed = True
    return changed


# ---------- fetching (polite) ----------

def is_bot_challenge(text):
    """The AWS WAF 'verify that you're not a robot' page catalog.sdsu.edu sends to scripts."""
    return "AwsWafIntegration" in text or "awswaf.com" in text or "verify that you're not a robot" in text


class Fetcher:
    """Downloads catalog pages: robots.txt first, then at most one request per
    max(SECONDS_BETWEEN_REQUESTS, the robots.txt crawl-delay) seconds (catalog.sdsu.edu
    asks for 120), every page cached in data/catalog_html/ and reused on reruns."""

    def __init__(self, cache_dir=CACHE_DIR, robots=None):
        self.cache_dir = cache_dir
        self.last = 0.0
        self.robots = robots
        self.delay = SECONDS_BETWEEN_REQUESTS

    def allowed(self, url):
        if self.robots is None:
            self.robots = urllib.robotparser.RobotFileParser(f"{SITE}/robots.txt")
            try:
                self.robots.read()
            except urllib.error.URLError as e:
                raise SystemExit(f"Could not read {SITE}/robots.txt ({e}); not crawling. Use --html-dir with saved pages.")
            finally:
                self.last = time.monotonic()      # reading robots.txt counts as a request
        self.delay = max(SECONDS_BETWEEN_REQUESTS, float(self.robots.crawl_delay(USER_AGENT) or 0))
        return self.robots.can_fetch(USER_AGENT, url)

    def get(self, url, cache_name):
        path = os.path.join(self.cache_dir, cache_name)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            with open(path, encoding="utf-8") as f:
                text = f.read()
            if not is_bot_challenge(text):
                return text
        if not self.allowed(url):
            raise SystemExit(f"robots.txt does not allow {url}; not crawling. Save the pages by hand and use --html-dir.")
        wait = self.delay - (time.monotonic() - self.last)
        if wait > 0:
            print(f"  waiting {wait:.0f}s (robots.txt crawl-delay) before {url}", flush=True)
            time.sleep(wait)
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                text = body.decode(response.headers.get_content_charset() or "utf-8", "replace")
                if is_bot_challenge(text):
                    raise SystemExit(f"Stopped: {url} answered with a bot check (\"verify that you're not a robot\"), "
                                     f"so the site does not allow automated access. Not retrying and not caching it. "
                                     f"Save the pages from a browser and use --html-dir / --listing-html.")
                if not text.strip():
                    # never cache an empty page: a rerun would reuse it
                    headers = "; ".join(f"{k}: {v}" for k, v in response.headers.items() if k.lower() != "set-cookie")
                    raise SystemExit(f"Stopped: {url} answered {response.status} with an empty page "
                                     f"(final URL {response.geturl()}; {headers}). Not retrying. "
                                     f"Use --html-dir / --listing-html with pages saved from a browser.")
        except urllib.error.HTTPError as e:
            if e.code in (403, 429):
                raise SystemExit(f"Stopped: {url} answered {e.code}. Not retrying. Use --html-dir with saved pages.")
            raise
        finally:
            self.last = time.monotonic()
        os.makedirs(self.cache_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return text


# ---------- discovery ----------

def in_program_list(node):
    while node is not None:
        if node.tag == "ul" and "program-list" in node.classes():
            return True
        node = node.parent
    return False


def discover(listing_html):
    """The listing page -> (bachelor's programs [{poid, name, degree, title, url, group}], counts)."""
    root, _ = parse_html(listing_html)
    has_lists = root.find(lambda n: n.tag == "ul" and "program-list" in n.classes()) is not None
    group, seen, programs = "", set(), []
    counts = collections.Counter()
    for node in root.walk():
        if node.tag == "p" and node.find(lambda n: n.tag == "strong") and not node.find(lambda n: n.tag == "a"):
            group = node.text()
            continue
        if node.tag != "a" or "preview_program.php" not in (node.attrs.get("href") or ""):
            continue
        if has_lists and not in_program_list(node):
            continue            # site menu links, such as "General Education Requirements"
        title = node.text()
        href = urllib.parse.urljoin(SITE + "/", node.attrs["href"])
        poid = (re.search(r"poid=(\d+)", href) or [None, None])[1]
        if group.strip().lower() == "roadmap" or title.endswith("- Roadmap"):
            counts["roadmap"] += 1
            continue
        if not poid or poid in seen:
            counts["repeat"] += 1
            continue
        seen.add(poid)
        counts["programs"] += 1
        if not BACHELOR.search(title):
            counts["not bachelor's"] += 1
            continue
        if COMBINED.search(title):
            counts["4+1"] += 1
            continue
        if re.search(r"undeclared", title, re.I):
            counts["undeclared"] += 1
            continue
        name, degree, _ = split_title(title)
        url = f"{SITE}/preview_program.php?catoid={CATALOG_ID}&poid={poid}"
        programs.append({"poid": poid, "name": name, "degree": degree, "title": title, "url": url, "group": group,
                         "special": bool(SPECIAL.search(title))})
    counts["bachelor's"] = len(programs)
    return programs, counts


def write_urls(programs, path=URLS_FILE):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# Bachelor's programs in the {CATALOG_YEAR} SDSU catalog, from {LISTING_URL}\n")
        f.write("# name<TAB>degree<TAB>url. Only the URL is read; lines starting with # are skipped.\n")
        for p in programs:
            f.write(f"{p['name']}\t{p['degree']}\t{p['url']}\n")


def read_urls(path):
    urls = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("#"):
                continue
            m = re.search(r"https?://\S+", line)
            if m:
                urls.append(m.group().rstrip(",;"))
    return urls


# ---------- class data checks (reuses scripts/coverage_report.py) ----------

def coverage_module():
    spec = importlib.util.spec_from_file_location("coverage_report", os.path.join(ROOT, "scripts", "coverage_report.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def class_data():
    """(offered keys, {(subject, catalog): title}) from data/cleaned, or (None, None) when it is not there."""
    try:
        cov = coverage_module()
        offered = cov.offered_courses()
        titles = {(cov.norm(c["subject"]), c["catalog_num"].strip().upper()): c["title"].strip()
                  for c in cov.read("data", "cleaned", "courses.csv")}
        return offered, titles
    except (OSError, KeyError):
        return None, None


def same_title(a, b):
    squash = lambda t: re.sub(r"[^a-z0-9]+", " ", t.lower().replace("&", " and ")).strip()
    return squash(a) == squash(b)


# ---------- output ----------

def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def major_row(prog):
    return {"major_id": prog.major_id, "name": prog.name, "degree": prog.degree, "college": "",
            "catalog_year": CATALOG_YEAR, "status": "coming_soon"}


def write_staging(programs, out_dir, log, offered, titles):
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for prog in programs:
        for r in prog.rows:
            r["major_id"] = prog.major_id
            rows.append(r)
    write_csv(os.path.join(out_dir, "majors.csv"), MAJOR_FIELDS, [major_row(p) for p in programs])
    write_csv(os.path.join(out_dir, "major_requirements.csv"), REQ_FIELDS, rows)
    report = build_report(programs, log, offered, titles)
    with open(os.path.join(out_dir, "REPORT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(report)
    return report


def shown_path(path):
    """A path for the report: relative to the project when inside it, forward slashes."""
    full = os.path.abspath(path)
    if os.path.commonpath([full, ROOT]) == ROOT:
        full = os.path.relpath(full, ROOT)
    return full.replace(os.sep, "/") if not path.startswith("http") else path


def md(text):
    return text.replace("|", "\\|")


def build_report(programs, log, offered, titles):
    lines = [f"# Catalog import report ({CATALOG_YEAR})", "",
             "Staging only: nothing here is live. Every major is `coming_soon`. Check each one against its catalog "
             "page, then promote it with `python3 scripts/import_catalog_majors.py --promote <major_id>`.", "",
             "| Majors processed | Requirement rows | Majors with open review items |", "| --- | --- | --- |",
             f"| {len(programs)} | {sum(len(p.rows) for p in programs)} | {sum(1 for p in programs if p.review)} |", ""]
    if log:
        lines += ["## Run notes", ""] + [f"- {md(x)}" for x in log] + [""]
    lines += ["| major_id | Name | Degree | Rows | Review items |", "| --- | --- | --- | --- | --- |"]
    lines += [f"| `{p.major_id}` | {md(p.name)} | {p.degree} | {len(p.rows)} | {len(p.review)} |" for p in programs]
    lines.append("")
    for prog in programs:
        lines += [f"## {md(prog.name)}, {prog.degree} (`{prog.major_id}`)", "",
                  f"- Source: `{shown_path(prog.source)}`" + (f", poid {prog.poid}" if prog.poid else "")
                  + (f", major code {prog.major_code}" if prog.major_code else ""),
                  f"- Rows: {len(prog.rows)}", ""]
        lines += ["### Groups", "", "| Section | Group | Rule | Courses |", "| --- | --- | --- | --- |"]
        groups = collections.OrderedDict()
        for r in prog.rows:
            groups.setdefault((r["section"], r["group_label"], r["rule"], r["pick_n"], r["pick_units"]), []).append(r["_code"])
        for (section, label, rule, pick_n, pick_units), codes in groups.items():
            rule_text = rule + (f" {pick_n}" if pick_n else "") + (f", {pick_units} units" if pick_units else "")
            lines.append(f"| {md(section)} | {md(label)} | {rule_text} | {len(codes)}: {', '.join(codes)} |")
        lines.append("")
        lines += ["### Review list", ""] + ([f"- [ ] {md(x)}" for x in prog.review] or ["- nothing flagged"]) + [""]
        lines += ["### Units check (advisory)", ""]
        if prog.units_checks:
            lines += [f"- {md(h)}: page says {s} units, listed courses give {l}: **{v}**" for h, s, l, v in prog.units_checks]
        else:
            lines.append("- no units totals on the page")
        lines.append("")
        lines += ["### Major notes (no rows made; for a human)", ""]
        last = None
        for heading, text in prog.notes:
            if heading != last:
                lines.append(f"- **{md(heading)}**")
                last = heading
            lines.append(f"  - {md(text)}")
        lines.append("")
        lines += ["### Coverage (courses with no sections in data/cleaned)", ""]
        if offered is None:
            lines.append("- data/cleaned not found, skipped")
        else:
            missing = []
            for r in prog.rows:
                key = (r["subject"], r["catalog_num"])
                if r["catalog_num"] and key not in offered and r["_code"] not in missing:
                    missing.append(r["_code"])
            have = len({r["_code"] for r in prog.rows}) - len(missing)
            lines.append(f"- {have} of {have + len(missing)} listed courses have sections this term")
            if missing:
                lines.append(f"- no sections: {', '.join(missing)}")
        lines.append("")
        lines += ["### Title differences (catalog vs class data)", ""]
        diffs = []
        if titles:
            for r in prog.rows:
                theirs = titles.get((r["subject"], r["catalog_num"]))
                if theirs and not same_title(theirs, r["title"]) and r["_code"] not in [d[0] for d in diffs]:
                    diffs.append((r["_code"], r["title"], theirs))
        lines += [f"- {c}: catalog \"{md(a)}\", class data \"{md(b)}\"" for c, a, b in diffs] or ["- none"]
        lines.append("")
    return "\n".join(lines)


# ---------- promote ----------

def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def line_ending(path):
    with open(path, "rb") as f:
        return "\r\n" if b"\r\n" in f.read(4096) else "\n"


def promote(major_id, staging_dir=STAGING_DIR, live_dir=LIVE_DIR):
    """Copies one staged major into the live CSVs with status coming_soon.
    Refuses when the id already exists live, except an empty coming_soon placeholder
    (me_bs, ba_marketing_bs: a majors row with no requirement rows), whose row is filled in place:
    name and degree come from the staged row, college is kept, status stays coming_soon."""
    staged_majors = [m for m in read_csv(os.path.join(staging_dir, "majors.csv")) if m["major_id"] == major_id]
    staged_rows = [r for r in read_csv(os.path.join(staging_dir, "major_requirements.csv")) if r["major_id"] == major_id]
    if not staged_majors:
        raise SystemExit(f"{major_id} is not in {staging_dir}/majors.csv")
    if not staged_rows:
        raise SystemExit(f"{major_id} has no staged requirement rows; nothing to promote")
    live_majors_path = os.path.join(live_dir, "majors.csv")
    live_reqs_path = os.path.join(live_dir, "major_requirements.csv")
    live_majors = read_csv(live_majors_path)
    live_rows = read_csv(live_reqs_path)
    existing = next((m for m in live_majors if m["major_id"].strip() == major_id), None)
    has_rows = any(r["major_id"].strip() == major_id for r in live_rows)
    placeholder = existing is not None and (existing.get("status") or "live").strip() == "coming_soon" and not has_rows
    if (existing or has_rows) and not placeholder:
        raise SystemExit(f"Refusing: {major_id} already exists in {live_dir} "
                         f"({'status ' + existing.get('status', '') if existing else 'requirement rows'}). "
                         f"Live majors are never overwritten.")
    staged = staged_majors[0]
    new = {"major_id": major_id, "name": staged["name"], "degree": staged["degree"],
           "college": staged.get("college", ""), "catalog_year": staged.get("catalog_year") or CATALOG_YEAR,
           "status": "coming_soon"}
    if placeholder:
        new["college"] = existing.get("college") or new["college"]
        live_majors = [new if m["major_id"].strip() == major_id else m for m in live_majors]
    else:
        live_majors.append(new)
    write_csv_ending(live_majors_path, MAJOR_FIELDS, live_majors)
    write_csv_ending(live_reqs_path, REQ_FIELDS, live_rows + staged_rows)
    return len(staged_rows), placeholder


def write_csv_ending(path, fields, rows):
    ending = line_ending(path) if os.path.exists(path) else "\n"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator=ending)
        w.writeheader()
        w.writerows(rows)


# ---------- main ----------

def is_listing(text):
    return "Programs by Campus Location" in text[:5000] and "acalog-page-title" not in text


def run(pages, out_dir, ids_file=IDS_FILE):
    """pages: [(source, html, url)] -> programs written to out_dir."""
    log, programs = [], []
    for source, text, url in pages:
        if is_listing(text):
            continue
        prog = parse_program(text, source, url)
        if not prog.poid:
            log.append(f"{os.path.basename(source)}: no catalog program id (poid) found, skipped")
            continue
        programs.append(prog)
    dupes = [p for p, n in collections.Counter(p.poid for p in programs).items() if n > 1]
    if dupes:
        log.append(f"same program read more than once (poid {', '.join(dupes)}); keeping the first copy")
        seen = set()
        programs = [p for p in programs if not (p.poid in seen or seen.add(p.poid))]
    ids = read_ids(ids_file)
    if assign_ids(programs, ids, log):
        write_ids(ids, ids_file)
        log.append(f"new major_ids saved to {shown_path(ids_file)}")
    offered, titles = class_data()
    report = write_staging(programs, out_dir, log, offered, titles)
    return programs, report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--discover", action="store_true", help="read the program listing and write --urls-out")
    mode.add_argument("--urls", help="file with one catalog program URL per line")
    mode.add_argument("--html-dir", help="folder of saved program pages (offline)")
    mode.add_argument("--promote", metavar="MAJOR_ID", help="copy one staged major into data/majors")
    ap.add_argument("--out", default=STAGING_DIR, help="staging folder (default data/majors/staging)")
    ap.add_argument("--listing-html", help="--discover: use this saved listing page instead of fetching it")
    ap.add_argument("--urls-out", default=URLS_FILE, help="--discover: where to write the URL list")
    ap.add_argument("--ids", default=IDS_FILE, help="major_id file (default scripts/catalog_major_ids.csv)")
    args = ap.parse_args(argv)

    if args.promote:
        n, placeholder = promote(args.promote, args.out, LIVE_DIR)
        print(f"Promoted {args.promote}: {n} requirement rows, status coming_soon"
              + (" (filled the existing placeholder row)" if placeholder else ""))
        return 0

    if args.discover:
        if args.listing_html:
            with open(args.listing_html, encoding="utf-8") as f:
                text = f.read()
        else:
            text = Fetcher().get(LISTING_URL, "programs_listing.html")
        programs, counts = discover(text)
        write_urls(programs, args.urls_out)
        print(", ".join(f"{k}: {v}" for k, v in counts.items()))
        print(f"{len(programs)} bachelor's programs written to {shown_path(args.urls_out)}")
        # make every program's major_id now, once; later runs reuse the file and never change an id
        # (until an id is published, it can still be edited by hand)
        progs = []
        for p in programs:
            prog = Program(p["url"])
            prog.poid, prog.name, prog.degree = p["poid"], p["name"], p["degree"]
            progs.append(prog)
        ids, log = read_ids(args.ids), []
        before = len(ids)
        if assign_ids(progs, ids, log):
            write_ids(ids, args.ids)
        print(f"major ids: {len(ids) - before} new, {before} already in {shown_path(args.ids)}")
        for line in log:
            print("  " + line)
        special = [p["title"] for p in programs if p["special"]]
        print(f"{len(special)} special programs (always on the review list):\n  " + "\n  ".join(special))
        return 0

    pages = []
    if args.html_dir:
        for name in sorted(os.listdir(args.html_dir)):
            if name.lower().endswith((".html", ".htm")):
                path = os.path.join(args.html_dir, name)
                with open(path, encoding="utf-8", errors="replace") as f:
                    pages.append((path, f.read(), None))
    else:
        fetcher = Fetcher()
        urls = read_urls(args.urls)
        to_fetch = [u for u in urls if not os.path.exists(os.path.join(CACHE_DIR, f"program_{(re.search(r'poid=(\d+)', u) or [0, ''])[1]}.html"))]
        if to_fetch:
            fetcher.allowed(to_fetch[0])
            print(f"{len(to_fetch)} pages to download, one every {fetcher.delay:.0f}s: "
                  f"about {len(to_fetch) * fetcher.delay / 60:.0f} minutes. Saved pages are reused on reruns.")
        for url in urls:
            poid = (re.search(r"poid=(\d+)", url) or [None, None])[1]
            if not poid:
                print(f"skipping {url}: no poid")
                continue
            pages.append((url, fetcher.get(url, f"program_{poid}.html"), url))
    programs, _ = run(pages, args.out, args.ids)
    print(f"{len(programs)} majors, {sum(len(p.rows) for p in programs)} rows, "
          f"{sum(1 for p in programs if p.review)} with review items. See {os.path.join(args.out, 'REPORT.md')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

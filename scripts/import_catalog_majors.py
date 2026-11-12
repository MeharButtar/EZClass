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
        works fully offline on saved pages; --html-dir can be given more than once, and
        --expect scripts/catalog_batch1_urls.txt reports which batch pages were found
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
      * an h3 list asking for fewer units than it lists, or saying "12 units selected
        from:": the h3 becomes the section;
      * "6 units of upper division Accounting (ACCTG) courses" / "9 units ... numbered
        300-599" (no list): an open row (subject, number range, units) in the h3's section.
  - "Select at least one of the following courses:" over a list makes a pick-n group.
  - Text over a whole h2 list: "MKTG 490 may only be taken after ..." goes on those
    courses' rows; a sentence with a rule in it (must, required, may only, the C
    average, progress requirements) is the section note; anything else (pathways,
    "please visit", "should refer to") is a blurb and only goes to the report.
    "Cannot be taken Cr/NC" and "grade of C (2.0) or better" become the short
    grade note on each course. A "*" footnote is put on the courses marked "*".
  - A rule the app cannot express ("6 units from one area, at least 3 at the 500
    level") becomes one pool for the whole total, with the full catalog sentence
    as the section note, and goes on the review list. When the rule gives no single
    total, pick_units is what the h2 total leaves after its other rows.
  - Text about a whole section (that rule sentence, "6 units may be taken outside
    the college", "Select at least one") is one `note` row at the top of the
    section, shown once; course rows keep only their own notes (grade, footnote,
    cross-listing). "excluding ACCTG 325 and ACCTG 326" fills the open row's exclude.
  - An open rule can be several rows (see README): a range plus the courses a list adds
    ("12 units of CFD 300 to 599 ... include but are not limited to:", "up to three units
    ... from one of:"), a list plus "Any 500-level chemistry course", or a range minus the
    list under "excluding:". Groups that each say their own units ("At least three units
    must be taken from ...") are pools of their own; what the parent's total leaves is an
    open rule from the parent's sentence (Journalism: any upper division JMS or LDT).
    Biology's "all upper division biology courses numbered 350 and above (except ...); BIOL 597,
    BIOL 497, BIOL 495 (combined maximum of nine units); and all upper division chemistry courses
    (except ...)" is one open group of two ranges, each with its own exclude list, plus the listed
    courses, the cap as its note; its units are the Major total less the fewest its other rows add.
  - Units with no subject and no list ("12 units from a science ... approved by the
    adviser") stay a section note and are not counted; the note says the subject is not
    specified in the catalog and to ask an advisor, and the review list says so.
  - "TE 362 Units: 1-4 (3 units)": the course counts the units the page says it is taken for.
  - The GWAR note goes on the course the writing block names, listed or only in its text.
  - Group labels and "Or ..." notes use the app's codes (CIVE 160, not CIV E 160).
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
              "num_min", "num_max", "exclude", "title", "units", "note"]

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
                         r"|roadmap|time limitation|\bminor\b|recommend|^notes?$", re.I)
# "Prior approval ... is required to allow the following courses to fulfill ...": a list of courses that can
# count with approval, not a requirement
APPROVAL_LIST = re.compile(r"\bapproval\b.*\b(?:allow|count|fulfill)|\b(?:courses|units)\b[^.]*\bmay be (?:applied|counted)"
                           r"\s+(?:to|towards)\b", re.I)
# an h2 that is a requirement with no courses: a section with only its note (shown to the student)
LANGUAGE_BLOCK = re.compile(r"language requirement|abroad requirement|auxiliary discipline", re.I)
# 'Maximum nine units of ECON 496 or ECON 596 may be substituted ...': a rule about a list, never a pool
MAXIMUM_RULE = re.compile(r"^(?:a\s+)?maximum\b", re.I)
# 'A typical program might be': example courses, not a requirement
EXAMPLE_LIST = re.compile(r"\btypical program\b|\bfor example\b|\bcourses include:?\s*$", re.I)
# a choice written another way: 'requires one three-unit capstone course fulfilled by:', 'Three Units of Either ...'
CHOOSE_ANY = re.compile(r"\b(?:requires|complete|take|select)\s+(one|two|three)\s+(?:[\w-]+\s+){0,2}courses?\s+"
                        r"(?:fulfilled by|selected from|from)\b", re.I)
EITHER_UNITS = re.compile(r"^(\w+)\s+units?\s+of\s+either\b", re.I)
# 'Any 500-level chemistry course' as a line in a list: a range that also counts
ANY_RANGE = re.compile(r"^\(?any\s+(\d)00-level\s+([a-z ]+?)\s+courses?\)?\.?$", re.I)
# 'Mathematics Competency Requirement' over a list with no rule of its own: pick 1 for now (Mehar, 2026-11-11:
# to be confirmed with the department), the list as the catalog writes it in the note
COMPETENCY_BLOCK = re.compile(r"competency requirement", re.I)
# 'Emphasis in Bioengineering' over the whole program (Preparation, Major ... one level down)
EMPHASIS_WRAPPER = re.compile(r"^(?:emphasis|specialization|concentration|option)\s+in\b", re.I)
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
NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
                "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16,
                "seventeen": 17, "eighteen": 18, "twenty": 20}
UNIT_WORDS = re.compile(r"\b(\d+|" + "|".join(NUMBER_WORDS) + r")(?:\s*[-–]\s*(\d+))?\s+units?\b", re.I)

# sentences in a block's paragraphs, sorted by read_rule_text
TOTAL_SENTENCE = re.compile(r"^(?:the major requires\s+)?(?:a\s+)?(minimum of\s+)?(\d+)(?:\s*[-–]\s*(\d+))?\s+"
                            r"(?:upper[- ]division\s+)?(?:[A-Za-z]+\s+(?:\([A-Z]+\)\s+)?)?units?\s*(?:\([^)]*\)\s*)?"
                            r"(?:in\s+[A-Za-z ]+?\s+)?(?:to include|consisting of|selected with\b[^.:]*?\bto include|:)",
                            re.I)
NO_CRNC = re.compile(r"(?:these courses )?(?:cannot|may not) be taken (?:for )?(?:credit/\s*no credit\s*)?\(?Cr/\s*NC\)?",
                     re.I)
# a grade rule anywhere in a course's text: '(must be completed with a grade of C (2.0) or better)'
GRADE_ANY = re.compile(r"(?:must be completed )?with a grade (?:of )?([BC]-?) \(\d\.\s?\d\) or (?:higher |better)+", re.I)
BLOCK_GRADE = re.compile(r"minimum grade in each class is (C-?)(?![\w-])|^complete with a grade of (C-?) \(\d\.\d\) or better:?$",
                         re.I)
COURSE_GRADE = re.compile(r"^\(?(?:must be completed )?with a grade (?:of )?(C-?) \(\d\.\d\) or better\)?\.?$", re.I)
MAJOR_NOTE_SENTENCE = re.compile(r"average (?:of C \(2\.0\) )?or better is required|grade point average of C"
                                 r"|additional progress requirements", re.I)
# "MKTG 491, 492, 493, or 494 may only be taken after ...": a rule about those courses, put on their rows
COURSE_RULE = re.compile(r"^([A-Z][A-Z ]*?[A-Z])\s+(\d{3}[A-Z]?(?:(?:\s*,\s*(?:or\s+|and\s+)?|\s+(?:or|and)\s+)\d{3}[A-Z]?)*)"
                         r"\s+(?:may|must|can|cannot)\b")
# a sentence over a whole list that states a rule (kept as the section note); others are blurbs (report only)
RULE_WORDS = re.compile(r"\b(?:must|required|may only|only after|cannot|may not|minimum|at least|no more than|unless"
                        r"|except|include all|satisfied by|maximum)\b", re.I)
COURSE_CODE = re.compile(r"\b([A-Z][A-Z ]*?[A-Z])\s+(\d{3}[A-Z]?)\b")
FILLER = re.compile(r"^(?:required (?:upper division )?courses in the major|but not both|and|or|choose one"
                    r"|and one course selected from)\s*[:.]?$", re.I)
NOTE_HEADING = re.compile(r"^(?:notes?|recommended(?: courses)?)$", re.I)
RECOMMENDED = re.compile(r"^recommended\b", re.I)
# "... Electrical Engineering laboratory electives: 2 units selected from ..." inside an electives rule
LAB_RULE = re.compile(r"\blaboratory electives:\s*(\d+)(?:\s*[-–]\s*(\d+))?\s+units?\b", re.I)
LAB_SECTION = "Laboratory Electives"
FOOTNOTE = re.compile(r"^([*°†‡^]+)\s*(\S.*)$", re.S)
# "12 units selected from:" over an h3 course list: that list is a units pool
POOL_SENTENCE = re.compile(r"\b(?:selected|chosen)\s+(?:with\s+[^.:]*?\s+)?from\b|\bfrom the following\b"
                           r"|\bmust be taken from\b", re.I)
POOL_ONLY = re.compile(r"^\(?(?:\d+|" + "|".join(NUMBER_WORDS) + r")(?:\s*[-–]\s*\d+)?\s+units?\)?(?:\s+of\s+[^:.]*?)?"
                       r"\s+selected (?:with\s+[^.:]*?\s+)?from(?: the following)?:?$", re.I)
# "Select at least one of the following courses:" over a course list: a pick-n group
CHOOSE_SENTENCE = re.compile(r"^(?:select\s+|choose\s+|complete\s+)?((?:at least|a minimum of)\s+)?(\d+|one|two|three|four|five)"
                             r"\s+(?:of the following|(?:courses?\s+)?(?:selected\s+)?from\b|courses?\b(?!\s+in\b))", re.I)
# "5-6 elective units" in an open rule (one word may sit between the number and "units")
UNIT_WORDS_ADJ = re.compile(r"\b(\d+|" + "|".join(NUMBER_WORDS) + r")(?:\s*[-–]\s*(\d+))?\s+(?:[a-z]+\s+)?units?\b", re.I)
# department words for "Nine units of 300- to 500-level finance courses" (no subject code on the page)
SUBJECT_WORDS = {"accounting": "ACCTG", "finance": "FIN", "marketing": "MKTG", "management": "MGT",
                 "information systems": "MIS", "economics": "ECON", "psychology": "PSY", "biology": "BIOL",
                 "chemistry": "CHEM", "mathematics": "MATH", "communication": "COMM", "sociology": "SOC",
                 "political science": "POL S", "journalism and media studies": "JMS",
                 "learning design and technology": "LDT", "computer science": "CS", "statistics": "STAT"}


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
    taken = re.fullmatch(r"\((\d+|" + "|".join(NUMBER_WORDS) + r")\s+units?\)\.?", extra, re.I)
    span = re.fullmatch(r"(\d+)-(\d+)", units)
    if taken and span and int(span.group(1)) <= number(taken.group(1)) <= int(span.group(2)):
        units = str(number(taken.group(1)))     # 'TE 362 Units: 1-4 (3 units)': the major takes it for 3
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


def number(word):
    return int(word) if word.isdigit() else NUMBER_WORDS[word.lower()]


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.:])\s+(?=[A-Z(*\d])", text) if s.strip()]


def read_rule_text(prog, heading, paras):
    """A block's paragraphs, sorted: the units total, a no-Cr/NC rule, a minimum grade, sentences that are
    major notes (C average, progress requirements; added to prog.notes), filler, and what is left (the rule)."""
    out = {"stated": None, "crnc": False, "grade": "", "rule": []}
    for p in paras:
        s = stated_units(p)
        if s and out["stated"] is None:
            out["stated"] = s
            continue
        lead = re.match(r"^\(\s*(\d+)(?:\s*[-–]\s*(\d+))?\s+units?\s*\)\s+(\S.*)$", p, re.I | re.S)
        if lead and out["stated"] is None:
            low = int(lead.group(1))
            out["stated"] = (low, int(lead.group(2) or low), "exact")
            p = lead.group(3)
        for sent in sentences(p):
            only = stated_units(sent) if out["stated"] is None else None
            if only:
                out["stated"] = only
                continue
            t = TOTAL_SENTENCE.match(sent)
            if t and out["stated"] is None:
                low = int(t.group(2))
                out["stated"] = (low, None, "minimum") if t.group(1) else (low, int(t.group(3) or low), "exact")
                continue
            g = BLOCK_GRADE.search(sent)
            if NO_CRNC.search(sent) or g:
                out["crnc"] = out["crnc"] or bool(NO_CRNC.search(sent))
                out["grade"] = (g.group(1) or g.group(2)).upper() if g else out["grade"]
                continue
            if FILLER.match(sent):
                continue
            if MAJOR_NOTE_SENTENCE.search(sent):
                add_note(prog, heading, sent)
                prog.section_note(heading, sent)
                continue
            out["rule"].append(sent)
    return out


def add_note(prog, heading, text):
    if (heading, text) not in prog.notes:
        prog.notes.append((heading, text))


def parse_open(text, upper=False):
    """'9 units selected from Finance (FIN) courses numbered 300-599' ->
    {units, subjects, min, max, guessed, excluded, exclude, exclude_list}; None when the text is not one such rule.
    upper: the heading above says 'upper division', so no range in the text means 300-599.
    exclude_list: the sentence ends 'excluding:', so the list under it is what does not count."""
    amounts = UNIT_WORDS_ADJ.findall(text)
    lead = re.match(r"\s*(?:an?\s+additional\s+|additional\s+|a minimum of\s+)?" + UNIT_WORDS_ADJ.pattern, text, re.I)
    amount = r"\b(\d+|" + "|".join(NUMBER_WORDS) + r")(?:\s*[-–]\s*(\d+))?\s+(?:additional\s+)?units?\s+of\s+(?:additional\s+)?"
    words = (re.search(amount + r"upper[- ]division\s", text, re.I)
             or re.search(amount + r"(?:major\s+)?electives?\b", text, re.I)
             or re.search(amount + r"\w+\s", text, re.I))
    if len(amounts) != 1 and not lead and not words:
        return None
    a, b = (words.group(1), words.group(2)) if words and len(amounts) != 1 and not lead else amounts[0]
    m = re.search(r"\bnumbered\s+(\d{3})\s*[-–]\s*(\d{3})\b", text)
    n = re.search(r"\b(\d)00-?\s*(?:to|or|through|and)\s+(\d)00-level\b", text)
    coded = re.search(r"\b([A-Z]{2,6})\s+(\d{3})\s+to\s+(\d{3})\b", text)        # 'CFD 300 to 599'
    if m:
        low, high = int(m.group(1)), int(m.group(2))
    elif n:
        low, high = int(n.group(1)) * 100, int(n.group(2)) * 100 + 99
    elif coded:
        low, high = int(coded.group(2)), int(coded.group(3))
    elif re.search(r"\bupper[- ]division\b", text, re.I) or upper:
        low, high = 300, 599
    else:
        return None
    subjects = re.findall(r"\(([A-Z]{2,6})\)\s+(?:courses|electives|coursework)\b", text)
    if coded and not subjects:
        subjects = [coded.group(1)]
    guessed = False
    if not subjects:
        lowered = text.lower()
        tail = re.search(r"\b(?:coursework|courses|electives?)\s+in\s+(.+)$", lowered)
        subjects = [s for w, s in SUBJECT_WORDS.items()
                    if re.search(rf"\b{w}\s+(?:courses|electives|coursework)\b", lowered)
                    or (tail and re.search(rf"\b{w}\b", tail.group(1)))]
        guessed = True
    if not subjects or (len(subjects) > 1 and not re.search(r"\bor\b", text)):
        return None
    units = str(number(a)) + (f"-{b}" if b else "")
    excluded = re.search(r"\b(?:excluding|except)\s+([^)]+?)\)?\.?$", text) or re.search(r"\(except\s+([^)]+)\)", text)
    codes = [f"{subject_key(x)} {y}" for x, y in
             re.findall(r"\b([A-Z][A-Z ]*?[A-Z])\s+(\d{1,3}[A-Z]{0,3})\b", excluded.group(1))] if excluded else []
    return {"units": units, "subjects": subjects, "min": low, "max": high, "guessed": guessed,
            "excluded": excluded.group(1).strip() if excluded else "", "exclude": codes,
            "exclude_list": bool(re.search(r"\bexcluding:?\s*$", text, re.I))}


SUBJECT_NAMES = "|".join(sorted(map(re.escape, SUBJECT_WORDS), key=len, reverse=True))
NUMBERED_RANGE = re.compile(r"\b(" + SUBJECT_NAMES + r")\s+courses\s+numbered\s+(\d{3})\s+and\s+above"
                            r"(?:\s*\(except\s+([^)]*)\))?", re.I)
UPPER_RANGE = re.compile(r"\ball\s+upper\s+division\s+(" + SUBJECT_NAMES + r")\s+courses(?!\s+numbered)"
                         r"(?:\s*\(except\s+([^)]*)\))?", re.I)
CAPPED_LIST = re.compile(r"((?:[A-Z]{2,5}\s+\d{3}[A-Z]?\s*,?\s*)+)\(combined maximum of (\w+) units?\)")


def parse_ranges(text):
    """'... include all upper division biology courses numbered 350 and above (except BIOL 452); BIOL 597, BIOL 497,
    BIOL 495 (combined maximum of nine units); and all upper division chemistry courses (except CHEM 300, ...)':
    one range per subject, each with its own exclude list, the courses the sentence lists, and the cap.
    None unless it names at least two ranges."""
    def codes(part):
        return [f"{subject_key(s)} {n}" for s, n in COURSE_CODE.findall(part or "")]
    ranges = [{"subjects": [SUBJECT_WORDS[m.group(1).lower()]], "min": int(m.group(2)), "max": 599,
               "exclude": codes(m.group(3))} for m in NUMBERED_RANGE.finditer(text)]
    ranges += [{"subjects": [SUBJECT_WORDS[m.group(1).lower()]], "min": 300, "max": 599,
                "exclude": codes(m.group(2))} for m in UPPER_RANGE.finditer(text)]
    if len(ranges) < 2:
        return None
    cap = CAPPED_LIST.search(text)
    listed = [tuple(c.split(" ", 1)) for c in codes(cap.group(1))] if cap else []
    cap_note = (f"{', '.join(' '.join(c) for c in listed)}: combined maximum of {number(cap.group(2))} units"
                if cap else "")
    return {"ranges": ranges, "listed": listed, "cap_note": cap_note}


def unplaced_note(amount):
    """The note for units the catalog gives no subject or list for ('12 Units of Electives')."""
    units = str(number(amount.group(1))) + (f"-{amount.group(2)}" if amount.group(2) else "")
    return (f"{units} units of electives, subject not specified in the catalog: ask an advisor which courses count")


def course_note(course, gwar_codes, footnotes=None, crnc=False, grade=""):
    """The note for one course row: its grade rule (the block's or its own), its own text, a footnote it points to."""
    parts = []
    extra = course["extra"]
    if footnotes and extra in footnotes:
        extra = footnotes[extra]
    if GRADE_C.search(extra):
        grade, crnc = "C", True
        extra = clean(GRADE_C.sub("", extra))
    m = COURSE_GRADE.match(extra)
    if m:
        grade, extra = m.group(1).upper(), ""
    g = GRADE_ANY.search(extra)
    if g:
        grade, extra = g.group(1).upper(), clean(GRADE_ANY.sub("", extra))
    if NO_CRNC.search(extra):
        crnc, extra = True, clean(NO_CRNC.sub("", extra))
    if re.fullmatch(r"[\W_]*", extra) or re.fullmatch(r"\(?but not both\)?\.?\W*", extra, re.I):
        extra = ""                                     # only brackets left, or 'but not both' (the pick-1 says it)
    if grade:
        parts.append(f"Grade of {grade} or better" + (", no Cr/NC" if crnc else ""))
    elif crnc:
        parts.append("No Cr/NC")
    if extra:
        parts.append(extra)
    if code(course["subject"], course["catalog_num"]) in gwar_codes:
        parts.append(GWAR_NOTE)
    return parts


def join_note(parts):
    out = []
    for p in parts:
        p = p.strip().rstrip(".:").rstrip()       # 'selected from:' as a note reads without its colon
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


def app_code(course):
    """The code the app shows: 'CIV E 160' -> 'CIVE 160' (subjects lose their spaces)."""
    return f"{subject_key(course['subject'])} {course['catalog_num']}"


def chain_label(courses, joiners):
    names = [app_code(c) for c in courses]
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
        self.section_notes = collections.OrderedDict()   # section -> texts shown once under its heading
        self.special = False

    def section_note(self, section, text, first=False):
        text = join_note([text])
        same = lambda t: re.sub(r"[“”\"]", "", t).lower()     # 'A “C” average' and 'A C average' are one note
        if text and same(text) not in {same(t) for t in self.section_notes.get(section, [])}:
            notes = self.section_notes.setdefault(section, [])
            notes.insert(0, text) if first else notes.append(text)

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


def take_footnotes(blocks):
    """'*No design component.' (a paragraph or list item) -> {'*': 'No design component.'}; removed from the blocks."""
    footnotes, trailing = {}, []
    for b in blocks:
        keep = []
        for p in b["paras"]:
            m = FOOTNOTE.match(p)
            if m:
                footnotes.setdefault(m.group(1), clean(m.group(2)))
            else:
                keep.append(p)
        b["paras"] = keep
        items = []
        for kind, value in b["items"]:
            m = FOOTNOTE.match(value.strip()) if kind == "text" and value else None
            if m:
                footnotes.setdefault(m.group(1), clean(m.group(2)))
                if items and items[-1][0] == "course" and not items[-1][1]["extra"]:
                    trailing.append((m.group(1), items[-1][1]))
            else:
                items.append((kind, value))
        b["items"] = items
    used = {c["extra"] for b in blocks for k, c in b["items"] if k == "course"}
    for marker, course in trailing:
        if marker not in used:
            course["extra"] = marker     # '° A college level statistics course ...' right under PSY 280
    return footnotes


def take_and_or_pairs(items):
    """'BIOL 203 and BIOL 203L or BIOL 204 and BIOL 204L', 'B A 323 and FIN 329 or B A 350 and MGT 357 or ...',
    'CS 150 and CS 150L or CS 200 or STAT 200': a choice between alternatives, at least one of them several courses
    taken together. 'and' is a list line or the course's own text. Returns the items without them and the
    alternatives ([[BIOL 203, BIOL 203L], [BIOL 204, BIOL 204L]], ...)."""
    is_and = lambda it: it[0] == "text" and it[1].strip().lower() == "and"
    out, found, i = [], [], 0
    while i < len(items):
        if items[i][0] != "course":
            out.append(items[i])
            i += 1
            continue
        alts, alt, j = [], [items[i][1]], i + 1
        while j < len(items):
            prev = alt[-1]
            if prev["extra"].strip().lower() == "and" and j < len(items) and items[j][0] == "course":
                alt.append(items[j][1]); j += 1; continue
            if is_and(items[j]) and j + 1 < len(items) and items[j + 1][0] == "course":
                alt.append(items[j + 1][1]); j += 2; continue
            k = j
            while k < len(items) and items[k][0] == "sep":
                k += 1
            if k + 1 < len(items) and items[k][0] == "or" and items[k + 1][0] == "course":
                alts.append(alt); alt = [items[k + 1][1]]; j = k + 2; continue
            break
        alts.append(alt)
        if len(alts) >= 2 and any(len(a) >= 2 for a in alts):
            for a in alts:
                for c in a:
                    if c["extra"].strip().lower() == "and":
                        c["extra"] = ""
            found.append(alts)
            out.append(("sep", None))
            i = j
        else:
            out.append(items[i])
            i += 1
    return out, found


def pick_from(sentence):
    """How many courses a sentence asks to pick ('Select at least one of the following', 'One Course Selected
    From', 'requires one three-unit capstone course fulfilled by:', 'Three Units of Either ...'): (n, keep the
    sentence as a note) or None."""
    m = CHOOSE_SENTENCE.match(sentence)
    if m:
        return number(m.group(2)), bool(m.group(1))
    m = CHOOSE_ANY.search(sentence)
    if m:
        return number(m.group(1)), False
    if EITHER_UNITS.match(sentence):
        return 1, False
    return None


HEADING_POOL = re.compile(r"^(?:and\s+)?(\d+|" + "|".join(NUMBER_WORDS) + r")(?:\s*[-–]\s*(\d+))?\s+units?\s+"
                          r"(?:selected\s+)?from:?$", re.I)


def pool_units_from(sentence):
    """'9-10 units of upper division major electives selected from:' -> '9-10'; None if not such a sentence."""
    h = HEADING_POOL.match(sentence.strip())
    if h:
        return str(number(h.group(1))) + (f"-{h.group(2)}" if h.group(2) else "")
    amounts = UNIT_WORDS.findall(sentence)
    if not POOL_SENTENCE.search(sentence) or not amounts or pick_from(sentence):
        return None
    near = re.search(UNIT_WORDS.pattern + r"(?:\s+of\s+[^.:]*?)?\s+(?:may\s+(?:also\s+)?be\s+|must\s+be\s+)?"
                     r"(?:(?:selected|chosen)\s+(?:with\s+[^.:]*?\s+)?from|taken\s+from)",
                     sentence, re.I)
    if near:
        a, b = near.group(1), near.group(2)
    elif len(amounts) == 1:
        a, b = amounts[0]
    else:
        return None
    return str(number(a)) + (f"-{b}" if b else "")


def unwrap_emphasis(blocks):
    """'Emphasis in Bioengineering' (h2) over Preparation for the Major, Major ... (h3): those move up one
    level, so they read like any other program. The wrapper keeps only its text (a major note)."""
    shift = False
    for i, b in enumerate(blocks):
        if b["level"] in (0, 2):
            children = []
            for n in blocks[i + 1:]:
                if n["level"] in (0, 2):
                    break
                children.append(n)
            shift = bool(EMPHASIS_WRAPPER.match(b["heading"]) and not [k for k, _ in b["items"] if k == "course"]
                         and any(c["level"] == 3 and re.match(r"preparation for the major|major\b", c["heading"], re.I)
                                 for c in children))
            b["wrapper"] = shift
        elif shift:
            b["level"] -= 1


def map_blocks(prog, blocks):
    blocks = [dict(b) for b in blocks]
    unwrap_emphasis(blocks)
    footnotes = take_footnotes(blocks)
    gwar_codes = set()
    for b in blocks:
        if b["level"] == 2 and GWAR_BLOCK.search(b["heading"]):
            gwar_codes |= {code(v["subject"], v["catalog_num"]) for k, v in b["items"] if k == "course"}
            gwar_codes |= {code(a, n) for p in b["paras"] for a, n in COURSE_CODE.findall(p)}
    used_codes = set()

    h2 = None                 # current h2 heading
    h2_is_note = False
    parent = None             # an h3 with a rule but no courses: the following h3 lists are its groups
    totals = collections.OrderedDict()   # h2 -> stated units (low, high, kind)
    pending_pool = []         # pool rows waiting for pick_units, per parent heading
    course_rules = []         # ([app codes], sentence, section) to put on those courses' rows
    pool_ctx = None           # a pool section made from one list: deeper lists right after it join it
    h2_upper = False          # the h2 text says 'upper division' (an open rule without a range is 300-599)

    def finish_parent():
        nonlocal parent, pending_pool
        if parent and pending_pool and (split_labs(parent, pending_pool) or split_named_groups(parent, pending_pool)
                                        or pick_per_group(parent, pending_pool) or split_group_units(parent, pending_pool)):
            dedupe_pool(prog, parent["heading"], pending_pool)
            stale = f"'{parent['heading']}' (under {parent['h2']}) is a rule in words, encoded as one pool"
            prog.review = [x for x in prog.review if not x.startswith(stale)]
            prog.review = [x for x in prog.review if not (" pool: kept as pool rows" in x and parent["rule"]
                                                           and re.search(r"\bone course\b", parent["rule"]))]
        elif parent and not pending_pool and pool_from_rule_text(parent):
            pass
        elif parent and pending_pool:
            if parent["rule"]:
                prog.section_note(parent["heading"], parent["rule"], first=True)
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

    def split_labs(parent, rows):
        """'9 units selected from ... courses with no more than 3 units from ... . Laboratory electives: 2 units
        selected from ... laboratory courses.' over lists that hold both: two pools, the courses and the labs
        (the catalog numbers ending in L), each with the units the page gives it. False when it is not that rule."""
        lab = LAB_RULE.search(parent["rule"])
        main = re.match(r"\s*(\d+)(?:\s*[-–]\s*(\d+))?\s+units?\b", parent["rule"])
        labs = [r for r in rows if r["catalog_num"].endswith("L")]
        if not (lab and main and labs and len(labs) < len(rows)):
            return False
        lab_units = lab.group(1) + (f"-{lab.group(2)}" if lab.group(2) else "")
        main_units = main.group(1) + (f"-{main.group(2)}" if main.group(2) else "")
        limit = re.search(r"\bwith\s+(no more than [^.]*)", parent["rule"])
        limit_note = re.sub(r"\bupper division\s+", "", limit.group(1)) if limit else ""
        limit_note = limit_note[:1].upper() + limit_note[1:]
        for r in rows:
            if any(r is x for x in labs):
                r.update(section=LAB_SECTION, group_label=LAB_SECTION, pick_units=lab_units)
            else:
                r.update(pick_units=main_units)
        if limit_note:
            prog.section_note(parent["heading"], limit_note)
        prog.flag(f"'{parent['heading']}': split in two as the page states: '{parent['heading']}' "
                  f"({main_units} units, {len(rows) - len(labs)} courses) and '{LAB_SECTION}' ({lab_units} units, "
                  f"the {len(labs)} lab courses).")
        if limit_note:
            prog.flag(f"'{parent['heading']}': the app cannot count \"{limit_note}\"; it is the section note.")
        return True

    def split_named_groups(parent, rows):
        """'Three units from Technical elective A and one unit from Technical elective B': each group its own
        pool section with its own units. False unless every group's units are in the rule."""
        labels = list(dict.fromkeys(r["group_label"] for r in rows))
        units = {}
        for label in labels:
            m = re.search(r"\b(\d+|" + "|".join(NUMBER_WORDS) + r")(?:\s*[-–]\s*(\d+))?\s+units?\s+(?:selected\s+)?"
                          r"from\s+(?:the\s+)?" + re.escape(label) + r"\b", parent["rule"], re.I)
            if not m:
                return False
            units[label] = str(number(m.group(1))) + (f"-{m.group(2)}" if m.group(2) else "")
        if len(labels) < 2:
            return False
        for r in rows:
            r.update(section=r["group_label"], pick_units=units[r["group_label"]])
        prog.section_note(labels[0], parent["rule"], first=True)
        prog.flag(f"'{parent['heading']}': \"{parent['rule']}\" read as separate pools: "
                  + ", ".join(f"'{l}' {u} units" for l, u in units.items()) + ".")
        return True

    def split_group_units(parent, rows):
        """Each group says its own units ('At least three units must be taken from the following list', 'At least
        12 units selected from the public policy group'): each its own pool. What the parent's total leaves after
        them (and after its range groups) is an open rule from the parent's sentence, when it reads as one."""
        labels = list(dict.fromkeys(r["group_label"] for r in rows))
        units = {l: next((r["_group_units"] for r in rows if r["group_label"] == l and r.get("_group_units")), None)
                 for l in labels}
        if not all(units.values()):
            return False
        for r in rows:
            r.update(section=r["group_label"], pick_units=units[r["group_label"]])
        total = parent["units"]
        if total is None:
            amount = UNIT_WORDS.search(parent["rule"]) or UNIT_WORDS.search(parent["heading"])
            total = str(number(amount.group(1))) if amount else None
        left = (units_range(total)[0] - sum(units_range(u)[0] for u in units.values()) - parent["opens"]) if total else 0
        prog.section_note(labels[0], parent["rule"], first=True)
        opened = parse_open(parent["rule"], True) if left > 0 else None
        if opened:
            opened["units"] = str(left)
            open_row(parent["heading"], f"The rest of the {total} units", opened)
        prog.flag(f"'{parent['heading']}': each group gives its own units ("
                  + ", ".join(f"'{l}' {u}" for l, u in units.items()) + ")"
                  + (f"; the other {left} of the {total} units: any course the rule names" if opened else "")
                  + (f"; {left} of the {total} units are not placed, check it" if left > 0 and not opened else "") + ".")
        return True

    def pick_per_group(parent, rows):
        """'one course selected from Groups I, III, and IV': every group is a pick-1 group."""
        if not re.search(r"\bone course (?:selected )?from (?:each of )?(?:the )?groups?\b"
                         r"|\bone (?:[\w-]+\s+)?course in each of\b", parent["rule"], re.I):
            return False
        for r in rows:
            r.update(rule="choose", pick_n="1", pick_units="", group_label=f"{r['group_label']} (pick 1)",
                     note=join_note([p for p in r["note"].split(". ") if not p.startswith("Or ")]))
        prog.section_note(parent["heading"], parent["rule"], first=True)
        prog.flag(f"'{parent['heading']}': \"{parent['rule']}\" read as pick 1 in each group.")
        return True

    def pool_from_rule_text(parent):
        """'Nine units ... may be selected from M E 499 (3 units), M E 570, ... and other ... courses': no lists
        follow, so the courses named in the sentence are the pool."""
        rule = parent["rule"]
        lead = re.match(r"\s*(?:an?\s+additional\s+)?" + UNIT_WORDS.pattern, rule, re.I)
        found = list(dict.fromkeys(COURSE_CODE.findall(rule)))
        if not lead or len(found) < 2:
            return False
        units = str(number(lead.group(1))) + (f"-{lead.group(2)}" if lead.group(2) else "")
        for subj, num in found:
            u = re.search(re.escape(f"{subj} {num}") + r"\s*\((\d+)\s+units?\)", rule)
            used_codes.add(code(subj, num))
            prog.rows.append({
                "major_id": "", "section": parent["heading"], "group_label": parent["heading"], "rule": "pool",
                "pick_n": "", "pick_units": units, "subject": subject_key(subj), "catalog_num": num,
                "num_min": "", "num_max": "", "title": "", "units": u.group(1) if u else "", "note": "",
                "_h2": parent["h2"], "_code": code(subj, num),
            })
        prog.section_note(parent["heading"], rule)
        prog.flag(f"'{parent['heading']}': no lists follow, so the {len(found)} courses named in the rule are a "
                  f"{units}-unit pool; titles and units come from the class data. Check it: \"{rule}\"")
        return True

    def h2_rows_for(name):
        return [r for r in prog.rows if r.get("_h2") == name]

    def in_range(course, rule):
        n = re.match(r"\d+", course["catalog_num"])
        return (subject_key(course["subject"]) in {subject_key(x) for x in rule["subjects"]} and n
                and rule["min"] <= int(n.group()) <= rule["max"])

    def open_row(section, sentence, rule, extras=(), notes=(), pick_n="", label=None, more_ranges=()):
        """An open group: its range row (and more ranges), then the listed courses that also count (one row each,
        rule 'open' with a catalog number). With rule['exclude_list'] the listed courses are what does not count."""
        exclude = list(rule["exclude"])
        if rule.get("exclude_list"):
            exclude += [app_code(c) for c in extras]
            extras = ()
        extras = [c for c in extras if not in_range(c, rule) and not any(in_range(c, r) for r in more_ranges)]
        subjects = "|".join(subject_key(x) for x in rule["subjects"])
        label = label or (f"Any {'/'.join(rule['subjects'])} {rule['min']}-{rule['max']} course"
                          + (" or a listed course" if extras else ""))
        base = {"major_id": "", "section": section, "group_label": label, "rule": "open", "pick_n": "",
                "pick_units": "", "subject": "", "catalog_num": "", "num_min": "", "num_max": "", "exclude": "",
                "title": "", "units": "", "note": "", "_h2": h2, "_code": label}
        prog.rows.append(dict(base, pick_n=str(pick_n or ""), pick_units=rule["units"] or "", subject=subjects,
                              num_min=str(rule["min"]), num_max=str(rule["max"]), exclude="|".join(exclude),
                              note=join_note([sentence] + list(notes))))
        for r in more_ranges:
            prog.rows.append(dict(base, subject="|".join(subject_key(x) for x in r["subjects"]),
                                  num_min=str(r["min"]), num_max=str(r["max"]), exclude="|".join(r["exclude"])))
        for c in extras:
            used_codes.add(code(c["subject"], c["catalog_num"]))
            prog.rows.append(dict(base, subject=subject_key(c["subject"]), catalog_num=c["catalog_num"],
                                  title=c["title"], units=c["units"], _code=f"{label}: {app_code(c)}"))
        if extras:
            prog.flag(f"'{label}' in {section}: {len(extras)} listed courses outside the range also count "
                      f"({', '.join(app_code(c) for c in extras)}).")
        prog.flag(f"'{label}' in {section}: \"{sentence}\" encoded as an open rule ({subjects} "
                  f"{rule['min']}-{rule['max']}, {rule['units']} units); check it.")
        if rule["guessed"]:
            prog.flag(f"'{label}': the page names no subject code; {subjects} was read from the department "
                      f"name. Check it.")
        if exclude and (rule["excluded"] or rule.get("exclude_list")):
            prog.flag(f"'{label}': {', '.join(exclude)} left out of its list (exclude column).")
        elif rule["excluded"]:
            prog.flag(f"'{label}': \"excluding {rule['excluded']}\" names no course codes; nothing excluded, check it.")

    page_courses = {app_code(v): v for b_ in blocks for k, v in b_["items"] if k == "course"}
    ranged_groups = []

    def ranges_group(heading, sentence, found):
        """Biology's electives: two ranges (BIOL 350-599, CHEM 300-599) each with its own exclude list, plus the
        courses the sentence lists, the cap as the group's note. Its units are what the h2 total leaves."""
        section = heading if not NOTE_HEADING.match(heading) else "Other Upper Division Major Electives"
        label = "Any " + " or ".join(f"{r['subjects'][0]} {r['min']}-{r['max']}" for r in found["ranges"]) + " course"
        base = {"major_id": "", "section": section, "group_label": label, "rule": "open", "pick_n": "",
                "pick_units": "", "subject": "", "catalog_num": "", "num_min": "", "num_max": "", "exclude": "",
                "title": "", "units": "", "note": "", "_h2": h2, "_code": label}
        rows = []
        for n, r in enumerate(found["ranges"]):
            rows.append(dict(base, subject=r["subjects"][0], num_min=str(r["min"]), num_max=str(r["max"]),
                             exclude="|".join(r["exclude"]), note=found["cap_note"] if n == 0 else ""))
        for subj, num in found["listed"]:
            c = page_courses.get(f"{subj} {num}", {})
            used_codes.add(code(subj, num))
            rows.append(dict(base, subject=subject_key(subj), catalog_num=num, title=c.get("title", ""),
                             units=c.get("units", ""), _code=f"{label}: {subj} {num}"))
        prog.rows += rows
        ranged_groups.append((h2, rows))
        prog.flag(f"'{label}' in {section}: \"{sentence}\" encoded as one open rule of "
                  f"{len(found['ranges'])} ranges" + (f" plus {len(found['listed'])} listed courses" if found["listed"]
                                                      else "") + "; check it.")

    def text_rules(sentences_, section_name, prefix=""):
        """Text with no list of its own: course rules onto those courses, rules as the section note, the rest
        (advice, blurbs) only in the report. Returns the blurbs."""
        blurbs = []
        for p in sentences_:
            m = COURSE_RULE.match(p)
            if m:
                codes = [f"{subject_key(m.group(1))} {n}" for n in re.findall(r"\d{3}[A-Z]?", m.group(2))]
                course_rules.append((codes, p, section_name))
            elif RULE_WORDS.search(p):
                prog.section_note(section_name, f"{prefix}{p}")
            else:
                blurbs.append(p)
        return blurbs

    # every course in the major's own lists (not the note blocks), to know which writing courses are outside them
    list_codes, note_h2 = set(), False
    for b in blocks:
        if b["level"] in (0, 2):
            note_h2 = bool(NOTE_BLOCKS.search(b["heading"]))
        if not note_h2:
            list_codes |= {code(v["subject"], v["catalog_num"]) for k, v in b["items"] if k == "course"}

    def gwar_section(name, outside, b):
        """'Complete RWS 305W or PSFA 305W (recommended) and earn a grade of C (2.0) or better': its own section,
        pick 1 (or the one course), shown but not counted in the major's units."""
        text = " ".join(b["paras"])
        grade = re.search(r"grade of (C-?) \(\d\.\d\) or better", text, re.I)
        rule = "choose" if len(outside) > 1 else "required"
        label = " or ".join(app_code(c) for c in outside) + (" (pick 1)" if len(outside) > 1 else "")
        for c in outside:
            extra = clean(re.sub(r"[()]", "", c["extra"]))
            note = join_note(([f"Grade of {grade.group(1).upper()} or better"] if grade else [])
                             + ([extra[:1].upper() + extra[1:]] if extra else []))
            used_codes.add(code(c["subject"], c["catalog_num"]))
            prog.rows.append({"major_id": "", "section": name, "group_label": label, "rule": rule,
                              "pick_n": "1" if rule == "choose" else "", "pick_units": "0",
                              "subject": subject_key(c["subject"]), "catalog_num": c["catalog_num"], "num_min": "",
                              "num_max": "", "exclude": "", "title": c["title"], "units": c["units"], "note": note,
                              "_h2": name, "_code": code(c["subject"], c["catalog_num"])})
        prog.flag(f"'{name}': {label} is outside the major's lists: its own section, not counted in the major's units.")

    for i, b in enumerate(blocks):
        courses = [v for k, v in b["items"] if k == "course"]
        if b.get("wrapper"):
            for p in b["paras"]:
                add_note(prog, b["heading"], p)
            continue
        if b["level"] in (0, 2):
            finish_parent()
            pool_ctx = None
            h2 = b["heading"] or "(no heading)"
            h2_upper = bool(re.search(r"\bupper[- ]division\b", " ".join(b["paras"]), re.I))
            if LANGUAGE_BLOCK.search(h2) and not courses:
                text = " ".join(p for p in b["paras"] if not p.startswith("Refer to"))
                if text:
                    prog.section_note(h2, text)
                    prog.flag(f"'{h2}' has no courses; shown as a section with only its note: \"{text}\"")
                continue
            h2_is_note = bool(NOTE_BLOCKS.search(h2))
            if GWAR_BLOCK.search(h2):
                outside = [c for c in courses if code(c["subject"], c["catalog_num"]) not in list_codes]
                if outside:
                    gwar_section(h2, outside, b)
            if h2_is_note:
                listed = ", ".join(code(c["subject"], c["catalog_num"]) for c in courses)
                body = " ".join(b["paras"]) + (f" Courses listed: {listed}." if listed else "")
                prog.notes.append((h2, body.strip() or "(no text)"))
                continue
            if not courses:
                # a heading whose lists (if any) are in the h3 blocks that follow
                info = read_rule_text(prog, h2, b["paras"])
                if info["stated"] and h2 not in totals:
                    totals[h2] = info["stated"]
                for p in info["rule"]:
                    add_note(prog, h2, p)
                    prog.flag(f"Text under '{h2}' was not read as a rule (no courses in that block): \"{p}\"")
                continue
        elif h2_is_note:
            prog.notes.append((f"{h2}: {b['heading']}", " ".join(b["paras"])))
            continue

        section = h2
        label = "Required"
        info = read_rule_text(prog, h2, b["paras"])
        stated, rule_paras = info["stated"], info["rule"]
        if b["level"] == 2 and stated:
            totals[h2] = stated

        if b["level"] >= 3:
            if not courses:
                rule = " ".join(rule_paras)
                # lists that belong to this rule: a deeper block with courses before the next heading at this level,
                # or (Mechanical Systems / Thermal Systems) a same-level list right after it with no rule of its own
                has_lists = False
                for n in blocks[i + 1:]:
                    if n["level"] in (0, 2) or n["level"] < b["level"]:
                        break
                    if n["level"] == b["level"]:
                        has_lists = bool(UNIT_WORDS_ADJ.search(rule) and any(k == "course" for k, _ in n["items"])
                                         and not n["paras"] and not UNIT_WORDS.search(n["heading"]))
                        break
                    if any(k == "course" for k, _ in n["items"]):
                        has_lists = True
                        break
                if not rule and UNIT_WORDS.search(b["heading"]) and has_lists:
                    rule = b["heading"]               # 'Three Units from One of the Following Categories ...'
                ranged = next(((p, parse_ranges(p)) for p in rule_paras if parse_ranges(p)), None)
                if ranged and not has_lists:
                    finish_parent()
                    ranges_group(b["heading"], *ranged)
                    rest = [p for p in rule_paras if p != ranged[0]]
                    if rest:
                        text_rules(rest, h2, "" if NOTE_HEADING.match(b["heading"]) else f"{b['heading']}: ")
                    continue
                if (NOTE_HEADING.match(b["heading"]) or MAXIMUM_RULE.match(rule) or MAXIMUM_RULE.match(b["heading"])
                        or not (stated or UNIT_WORDS_ADJ.search(rule) or has_lists)):
                    # "Note: ..." or text with no units: its rules are the section note, the rest is for a human
                    target = parent["heading"] if parent else (pool_ctx["section"] if pool_ctx else h2)
                    prefix = "" if NOTE_HEADING.match(b["heading"]) else f"{b['heading']}: "
                    amount = UNIT_WORDS.match(b["heading"])
                    if amount and not has_lists and not parse_open(b["heading"]):
                        # '12 Units of Electives' with no subject and no list: say so, so students ask an advisor
                        prog.section_note(target, unplaced_note(amount))
                        prog.flag(f"'{b['heading']}': units with no subject or list; a '{target}' section note, "
                                  f"not counted in the totals. Check it.")
                    blurbs = text_rules(rule_paras, target, prefix)
                    for p in rule_paras:
                        add_note(prog, f"{h2}: {b['heading']}", p)
                    kept = [p for p in rule_paras if p not in blurbs]
                    if kept:
                        prog.flag(f"Text under '{b['heading']}' kept as the '{target}' section note: \"{' '.join(kept)}\"")
                    if blurbs and not NOTE_HEADING.match(b["heading"]):
                        prog.flag(f"Text under '{b['heading']}' left out (no rule in it; in the report only): "
                                  f"\"{' '.join(blurbs)}\"")
                    continue
                opened = None if stated or has_lists else parse_open(rule, h2_upper or bool(
                    parent and re.search(r"upper[- ]division", parent["rule"], re.I)))
                if opened and parent and b["level"] > parent["level"]:
                    # 'C. Upper Division Economics: Three additional units of upper division economics electives.'
                    open_row(b["heading"], rule, opened)
                    parent["opens"] += units_range(opened["units"])[0]
                    continue
                if opened:
                    finish_parent()
                    open_row(b["heading"], rule, opened)  # an electives rule is its own section (see the docstring)
                    continue
                if not has_lists and not stated and len(set(COURSE_CODE.findall(rule))) < 2:
                    target = parent["heading"] if parent else h2
                    text = rule if rule == b["heading"] else f"{b['heading']}: {rule}"
                    amount = UNIT_WORDS.search(rule)
                    if amount:
                        prog.section_note(target, unplaced_note(amount))
                    prog.section_note(target, text)
                    prog.flag(f"'{b['heading']}': units with no subject or list (\"{rule}\"); a '{target}' section "
                              f"note, not counted in the totals. Check it.")
                    continue
                finish_parent()
                parent = {"heading": b["heading"], "h2": h2, "rule": rule, "units": None, "level": b["level"],
                          "opens": 0}
                amounts = UNIT_AMOUNT.findall(rule) or [(str(number(a)), b_) for a, b_ in UNIT_WORDS.findall(rule)][:1]
                if stated:
                    parent["units"] = f"{stated[0]}-{stated[1]}" if stated[1] and stated[1] != stated[0] else str(stated[0])
                elif len(amounts) == 1:
                    low, high = amounts[0]
                    parent["units"] = f"{low}-{high}" if high else low
                if rule and not LAB_RULE.search(rule):
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
            pool_ctx = None

        b["items"], and_or = take_and_or_pairs(b["items"])
        heading = b["heading"] if b["level"] >= 3 else ""
        fixed = re.match(r"^(\d+|" + "|".join(NUMBER_WORDS) + r")\s+units?(?:\s+of)?:?$",
                         " ".join(rule_paras).strip() or heading.strip(), re.I)
        if fixed and len(courses) == 1:
            courses[0]["units"] = str(number(fixed.group(1)))
            rule_paras = []
            heading = "" if re.match(r"^\w+\s+units?$", heading, re.I) else heading
            label = "Required" if not heading else label
        heading_pick = pick_from(heading) if heading else None
        if courses and EXAMPLE_LIST.search(" ".join(rule_paras)):
            names = ", ".join(app_code(c) for c in courses)
            prog.section_note(parent["heading"] if parent else (section if b["level"] < 3 else heading),
                              f"{' '.join(rule_paras)} {names}")
            prog.flag(f"'{b['heading']}': example courses, not a requirement: a section note ({names}).")
            continue
        if heading and APPROVAL_LIST.search(" ".join(rule_paras)) and not heading_pick and not pool_units_from(heading):
            target = parent["heading"] if parent else h2
            names = ", ".join(app_code(c) for c in courses)
            prog.section_note(target, f"{' '.join(rule_paras)} ({names})")
            prog.flag(f"'{heading}': courses that count only with approval, not a requirement: a section note ({names}).")
            continue
        heading_pool = pool_units_from(heading) if heading and not heading_pick else None
        if heading and TOTAL_SENTENCE.match(heading):
            label = "Required"                    # 'A Minimum of 36 Upper Division Units to Include'
        if heading and RECOMMENDED.match(heading):
            target = parent["heading"] if parent else (pool_ctx["section"] if pool_ctx else h2)
            names = ", ".join(app_code(c) for c in courses)
            prog.section_note(target, f"{heading} (not required): {names}")
            prog.flag(f"'{heading}' list under '{target}' is not required: no rows, a section note ({names}).")
            continue
        if pool_ctx and b["level"] > pool_ctx["level"] and not parent:
            # a list right under a pool's list ('3 units may also be selected from:', 'no more than 9 units
            # selected from:'): more courses for the same pool, its text on its rows
            section = pool_ctx["section"]
            extra_note = [heading.rstrip(":")] if heading_pool else []
            for p in rule_paras:
                extra_note.append(p)
            sub_rows = []
            for chain, joiners, _, _ in chains(b["items"]):
                for course in chain:
                    others = [app_code(c) for c in chain if c is not course]
                    tie = ([f"{CROSS_NOTE} with {', '.join(others)}"] if set(joiners) == {"also"}
                           else [f"Or {', '.join(others)}"]) if others else []
                    used_codes.add(code(course["subject"], course["catalog_num"]))
                    r = {"major_id": "", "section": section, "group_label": label.rstrip(":"), "rule": "pool",
                         "pick_n": "", "pick_units": pool_ctx["units"], "subject": subject_key(course["subject"]),
                         "catalog_num": course["catalog_num"], "num_min": "", "num_max": "", "title": course["title"],
                         "units": course["units"],
                         "note": join_note(extra_note + tie + course_note(course, gwar_codes, footnotes,
                                                                          info["crnc"], info["grade"])),
                         "_h2": h2, "_code": code(course["subject"], course["catalog_num"])}
                    prog.rows.append(r)
                    sub_rows.append(r)
            dedupe_pool(prog, section, [r for r in prog.rows if r["section"] == section and r["rule"] == "pool"])
            prog.flag(f"'{label}' (a list under the '{section}' pool) joined that pool ({pool_ctx['units']} units)"
                      + (f" with the note \"{join_note(extra_note)}\"" if extra_note else "") + "; check it.")
            continue
        pool_ctx = None

        in_pool = bool(parent) and b["level"] >= 3

        # 'Twelve units of CFD courses ranging from CFD 300 to 599 ... include but are not limited to:' or
        # 'electives ... excluding:' over a list: an open group (the range, plus or minus the list)
        if courses and not in_pool:
            open_list = None
            excluding_line = [p_ for p_ in rule_paras if re.fullmatch(r"excluding:?", p_.strip(), re.I)]
            candidates = list(rule_paras)
            if heading and excluding_line:
                candidates.append(f"{heading} excluding:")
            for s_ in candidates:
                if POOL_SENTENCE.search(s_) and not re.search(r"excluding:?\s*$", s_, re.I):
                    continue
                o = parse_open(s_, h2_upper)
                if o:
                    open_list = (s_, o)
                    break
            adds = any(re.search(r"not limited to|\bfrom one of\b|ranging from|\bmay (?:also |optionally )?(?:take|include|count)",
                                 p_, re.I) for p_ in rule_paras)
            if open_list and not (open_list[1]["exclude_list"] or adds):
                open_list = None
            if open_list:
                s_, o = open_list
                target = label if b["level"] >= 3 else section
                others = [p for p in rule_paras if p is not s_ and p not in excluding_line]
                notes = [p for p in others if RULE_WORDS.search(p) or re.search(r"\bup to\b|\bfrom one of\b", p, re.I)]
                for p in others:
                    if p not in notes:
                        add_note(prog, h2, p)
                open_row(target, s_, o, extras=courses, notes=notes)
                continue

        # a units pool over this list ("12 units selected from:", or "(9 units)" over a longer list)
        pool_units = heading_pool if not in_pool else None
        if heading_pool and not in_pool:
            label = f"{h2} Electives" if heading_pool and label == heading else label   # the heading is the rule
            if label == f"{h2} Electives" and re.match(r"and\s", heading, re.I):
                # 'And Two Units from' after an electives rule: not the same as that 'Electives' section
                label = f"Additional Electives ({heading_pool} units)"
        if not pool_units and not in_pool:
            for s in rule_paras:
                pool_units = pool_units_from(s)
                if pool_units:
                    if POOL_ONLY.match(s):
                        rule_paras = [p for p in rule_paras if p is not s]   # the counter says the same
                    break
            if not pool_units and stated and stated[2] == "exact" and b["level"] >= 3:
                single = [c[0] for c, _, _, _ in chains(b["items"]) if len(c) == 1]
                multi = [c for c, _, _, _ in chains(b["items"]) if len(c) > 1]
                listed_low = sum(units_range(c["units"])[0] for c in single) + \
                    sum(min(units_range(c["units"])[0] for c in chain) for chain in multi)
                if listed_low > stated[0]:
                    pool_units = f"{stated[0]}-{stated[1]}" if stated[1] != stated[0] else str(stated[0])

        # a pick-n group over this list ("Select at least one of the following courses:")
        pick_n, choose_note = None, []
        if heading_pick and not in_pool:
            pick_n = heading_pick[0]
            label = heading.rstrip(":")
        for s in ([] if pick_n or in_pool else rule_paras):
            m = pick_from(s)
            if m:
                pick_n = m[0]
                rule_paras = [p for p in rule_paras if p is not s]
                # 'Select at least one ...' over a whole h2 list is kept (the section note); under it, the
                # group's "Pick n" says the same
                choose_note = [s.rstrip(":")] if m[1] and b["level"] < 3 else []
                break

        text_opens = []
        if b["level"] < 3 and rule_paras and not pool_units:
            # text over a whole h2 list describes the section, not each course; an open rule in it is its own group
            for p_ in rule_paras:
                o_ = parse_open(p_, h2_upper) if re.search(r"\bupper[- ]division\b.*\belectives\b", p_, re.I) else None
                if o_:
                    text_opens.append((p_, o_))
            rule_paras = [p_ for p_ in rule_paras if p_ not in {t for t, _ in text_opens}]
            blurbs = text_rules(rule_paras, section)
            for p in rule_paras:
                if p not in blurbs and not COURSE_RULE.match(p):
                    prog.flag(f"'{section}': rule text kept as the section note: \"{p}\"")
            for p in blurbs:
                add_note(prog, h2, p)
            if blurbs:
                prog.flag(f"Text under '{h2}' left out (no rule in it; in the report only): \"{' '.join(blurbs)}\"")
            rule_paras = []

        block_note = rule_paras[:]
        opens, any_ranges, or_note = list(text_opens), [], []
        for n_, (kind, value) in enumerate(b["items"]):
            if kind != "text" or not value.strip() or FILLER.match(value.strip()):
                continue
            a_ = ANY_RANGE.match(value.strip())
            subj = [sv for w, sv in SUBJECT_WORDS.items() if a_ and w == a_.group(2).lower().strip()]
            if a_ and subj:
                level = int(a_.group(1)) * 100
                any_ranges.append({"units": "", "subjects": subj, "min": level, "max": level + 99, "guessed": True,
                                   "excluded": "", "exclude": [], "exclude_list": False, "text": value.strip()})
                continue
            if n_ and b["items"][n_ - 1][0] == "or":
                or_note.append(f"Or {value.strip()[:1].lower()}{value.strip()[1:]}")   # 'or a three unit ... course'
                continue
            for sent in sentences(re.sub(r"\s*Units:\s*[\d\s–-]+$", "", value)):   # "... courses. Units: 9"
                opened = parse_open(sent, h2_upper)
                if opened:
                    opens.append((sent, opened))
                elif MAJOR_NOTE_SENTENCE.search(sent):
                    add_note(prog, h2, sent)
                    prog.section_note(h2, sent)
                elif not FILLER.match(sent):
                    block_note.append(sent)
                    prog.flag(f"'{label}' in {section}: text between courses that was not read as a rule: \"{sent}\"")
        if rule_paras and not in_pool and pool_units:
            prog.flag(f"'{label}': rule text kept as the section note, check it: \"{' '.join(rule_paras)}\"")
        elif rule_paras and not in_pool:
            prog.flag(f"'{label}' in {section}: rule text kept as the note, check the group: \"{' '.join(rule_paras)}\"")

        def note_for(course, before=()):
            return list(before) + course_note(course, gwar_codes, footnotes, info["crnc"], info["grade"])

        if any_ranges and (pool_units or pick_n) and not in_pool:
            # a list plus 'any 500-level ... course': one open group of the list and the range(s)
            target = label if b["level"] >= 3 else section
            first = dict(any_ranges[0], units=pool_units or "")
            group_label = (label if b["level"] >= 3 else section) + (f" (pick {pick_n})" if pick_n else "")
            open_row(target, " ".join(rule_paras), first, extras=courses, notes=[r["text"] for r in any_ranges],
                     pick_n=pick_n or "", label=group_label, more_ranges=any_ranges[1:])
            prog.flag(f"'{group_label}' in {target}: the list plus "
                      + ", ".join(r["text"] for r in any_ranges) + "; check it.")
            continue

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

        def pool_rows(note):
            """Every course of the list as a pool row, in page order; an or / also-listed-as chain stays as
            pool rows with a note (a pick-1 group inside a units pool would be counted on its own)."""
            made = []
            for chain, joiners, _, _ in chains(b["items"]):
                if len(chain) == 1:
                    made.append(row(chain[0], "pool", label, note_for(chain[0], note)))
                    continue
                for course in chain:
                    others = [app_code(c) for c in chain if c is not course]
                    tie = f"{CROSS_NOTE} with {', '.join(others)}" if set(joiners) == {"also"} else f"Or {', '.join(others)}"
                    made.append(row(course, "pool", label, note_for(course, note + [tie])))
                prog.flag(f"{chain_label(chain, joiners)} in the '{label}' pool: kept as pool rows with a note "
                          f"(a pick-1 group inside a units pool would be counted on its own).")
            return made

        if b["level"] < 3 and COMPETENCY_BLOCK.search(b["heading"]) and courses:
            # 'STAT 250, STAT 350A, STAT 350B or (highly recommended) SOC 201, SOC 406, SOC 407': all of one
            # sequence. Satisfied outside the major's units, so pick_units 0 (not in the totals).
            runs, flags, recommended = [[]], [], False
            for kind, value in b["items"]:
                if kind == "or":
                    runs.append([])
                elif kind == "text" and re.search(r"recommended", value, re.I):
                    recommended = True
                elif kind == "course":
                    runs[-1].append(value)
                    if len(runs[-1]) == 1:
                        flags.append(recommended)
                        recommended = False
            runs = [r for r in runs if r]
            prog.section_notes.pop(section, None)
            text = " ".join(b["paras"])
            text = re.sub(r"\.\s+or\s+(\w)", lambda m: ". Or " + m.group(1).lower(), text)   # the catalog's stray 'or'
            prog.section_note(section, text)
            if len(runs) >= 2 and all(len(r) >= 2 for r in runs):
                group_label = ", or ".join(", ".join(app_code(c) for c in r[:-1]) + " and " + app_code(r[-1])
                                           for r in runs)
                prog.section_note(section, "Take all the courses of one sequence")
                for run, rec in zip(runs, flags):
                    for course in run:
                        row(course, "choose", group_label,
                            note_for(course, ["Highly recommended sequence"] if rec else []),
                            pick_n=str(len(run)))["pick_units"] = "0"
                prog.flag(f"'{b['heading']}': all courses of one of {len(runs)} sequences ({group_label}); not counted "
                          f"in the major's units (pick_units 0). Check it.")
            else:
                group_label = f"{b['heading']} (pick 1)"
                for course in courses:
                    row(course, "choose", group_label, note_for(course, []), pick_n="1")["pick_units"] = "0"
                prog.flag(f"'{b['heading']}': read as pick 1 of {len(courses)}, not counted in the major's units; "
                          f"check it.")
            prog.review = [x for x in prog.review if not x.startswith(f"'Required' in {section}: text between courses")
                           and not x.startswith(f"'{section}': rule text kept") and
                           not x.startswith(f"Text under '{section}' left out")]
            continue
        only_alts = bool(and_or) and not [k for k, _ in b["items"] if k == "course"]
        if in_pool:
            own = next((pool_units_from(x) for x in [heading] + rule_paras if pool_units_from(x)), None)
            made = pool_rows([x for x in block_note if not (own and pool_units_from(x))])
            for r in made:
                r["_group_units"] = own
            pending_pool.extend(made)
        elif only_alts:
            pass
        elif pool_units and len(chains(b["items"])) == 1 and set(chains(b["items"])[0][1]) == {"or"}:
            chain = chains(b["items"])[0][0]
            if b["level"] >= 3:
                section = label
            for p in rule_paras:
                prog.section_note(section, p)
            for course in chain:
                row(course, "choose", label, note_for(course, [p for p in block_note if p not in rule_paras]), pick_n="1")
            prog.flag(f"'{label}' asks for {pool_units} units of one 'or' list ({chain_label(chain, ['or'] * (len(chain) - 1))}): "
                      f"read as pick 1; check it.")
        elif pool_units:
            if b["level"] >= 3:
                section = label    # an electives pool is always its own section (see the docstring)
            else:
                label = "Choose from these courses"    # the whole h2 list is the pool ('6 units selected from:')
            pool_ctx = {"section": section, "level": b["level"], "units": pool_units}
            for p in block_note:          # the rule text and any loose line in the list: once, for the section
                prog.section_note(section, p)
            for r in pool_rows([]):
                r["pick_units"] = pool_units
            if b["level"] >= 3:
                prog.flag(f"'{label}' (under {h2}) asks for {pool_units} units of its list: encoded as a pool in its "
                          f"own section '{label}', check it.")
            else:
                prog.flag(f"'{h2}' asks for {pool_units} units of its list: the whole list is a {pool_units}-unit "
                          f"pool, check it.")
        else:
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
            if pick_n and not groups:
                group_label = f"{b['heading'] or h2} (pick {pick_n})"
                if b["level"] < 3:
                    for p in choose_note:
                        prog.section_note(section, p)
                    choose_note = []
                for course in required:
                    row(course, "choose", group_label, note_for(course, block_note + choose_note), pick_n=str(pick_n))
                prog.flag(f"'{group_label}' in {section}: read as pick {pick_n} of {len(required)}; check it.")
                required = []
            elif pick_n:
                # 'A minimum of two courses selected from:' over a list with or / also-listed-as pairs: one
                # pick-n group; a pair's courses keep a note saying so
                base = label if label != "Required" else (b["heading"] or h2)    # not 'Required (pick 1)'
                group_label = label if heading_pick else f"{base} (pick {pick_n})"
                for chain, joiners, _, _ in chains(b["items"]):
                    for course in chain:
                        others = [app_code(c) for c in chain if c is not course]
                        tie = ([f"{CROSS_NOTE} with {', '.join(others)}"] if set(joiners) == {"also"}
                               else [f"Or {', '.join(others)}"]) if others else []
                        row(course, "choose", group_label, note_for(course, block_note + choose_note + tie),
                            pick_n=str(pick_n))
                prog.flag(f"'{group_label}' in {section}: read as pick {pick_n}, its or / also-listed-as pairs "
                          f"kept with a note; check it.")
                required, groups = [], []
            for course in required:
                row(course, "required", label, note_for(course, block_note))
            for chain, joiners in groups:
                group_label = chain_label(chain, joiners)
                if b["level"] >= 3:
                    group_label = f"{label}: {group_label}"
                for course in chain:
                    extra = [CROSS_NOTE] if set(joiners) == {"also"} else []
                    row(course, "choose", group_label, note_for(course, block_note + extra + or_note), pick_n="1")
        for alternatives in and_or:
            group_label = ", or ".join(" and ".join(app_code(c) for c in alt) for alt in alternatives)
            alt_units = min(sum(units_range(c["units"])[0] for c in alt) for alt in alternatives)
            same = len({len(alt) for alt in alternatives}) == 1
            if only_alts and pool_units and b["level"] >= 3:
                section = label                   # 'Upper Division Business Electives: 6-7 units selected from:'
            pick_units = pool_units if only_alts and pool_units else str(alt_units)
            for alt in alternatives:
                if same:
                    note = ["Take both courses of one pair" if len(alt) == 2 else f"Take all {len(alt)} courses of one choice"]
                else:
                    note = [f"Take {' and '.join(app_code(c) for c in alt)} together"] if len(alt) > 1 else []
                for course in alt:
                    row(course, "choose", group_label, note_for(course, note),
                        pick_n=str(len(alt)) if same else "1")["pick_units"] = pick_units
            prog.flag(f"'{group_label}' in {section}: a choice between alternatives of several courses, encoded as "
                      f"pick {len(alternatives[0]) if same else 1} ({pick_units} units) with a note; the app cannot "
                      f"check that the courses of one alternative are taken together. Check it.")
        for sent, opened in opens:
            open_row(section, sent, opened)
    finish_parent()

    for codes, sentence, section in course_rules:
        hits = [r for r in prog.rows if f"{r['subject']} {r['catalog_num']}" in codes]
        for r in hits:
            r["note"] = join_note([r["note"], sentence])
        if hits:
            names = ", ".join(dict.fromkeys(f"{r['subject']} {r['catalog_num']}" for r in hits))
            prog.flag(f"\"{sentence}\" put on {names}.")
        else:
            prog.section_note(section, sentence)
            prog.flag(f"\"{sentence}\": none of {', '.join(codes)} is in the lists; kept as the section note.")

    for c in sorted(gwar_codes - used_codes):
        prog.notes.append(("Graduation Writing Assessment Requirement", f"{c} is listed for the GWAR but not in the major lists."))
    for marker, text in footnotes.items():
        if not any(c["extra"] == marker for b in blocks for k, c in b["items"] if k == "course"):
            add_note(prog, "Footnotes", f"{marker} {text}")
            prog.flag(f"Footnote '{marker} {text}' has no course marked '{marker}'; kept as a major note.")

    for name, rows in ranged_groups:
        # 'the remaining units': the h2 total less the fewest units its other rows can add up to
        ids_ = {id(r) for r in rows}
        total = totals.get(name)
        low = listed_units([r for r in h2_rows_for(name) if id(r) not in ids_])[0]
        units = str(total[0] - low) if total and total[0] > low else ""
        rows[0]["pick_units"] = units
        if units:
            prog.derived.add(name)
            prog.flag(f"'{rows[0]['group_label']}': {units} units, worked out from the {name} total minus its "
                      f"other courses.")
        else:
            prog.flag(f"'{rows[0]['group_label']}': could not work out its units; pick_units is blank.")

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
        if r["rule"] == "required" and r.get("pick_units") == "0":
            continue                            # shown, not counted (a writing course outside the major's lists)
        if r["rule"] == "required":
            a, b = units_range(r["units"])
            low, high = low + a, high + b
        elif r["rule"] == "choose":
            groups.setdefault((r["section"], r["group_label"]), []).append(r)
        elif r["rule"] == "pool":
            pools[(r["section"], "")] = r["pick_units"]
        elif r["rule"] == "open":
            # one open group can be several rows (its ranges and listed courses): the first row says what it needs
            pools.setdefault((r["section"], r["group_label"]),
                             r["pick_units"] or (str(3 * int(r["pick_n"])) if r["pick_n"] else ""))
    for items in groups.values():
        if items[0].get("pick_units"):          # a pair choice: the units of one pair
            a, b = units_range(items[0]["pick_units"])
            low, high = low + a, high + b
            continue
        n = int(items[0]["pick_n"] or 1)
        lows = sorted(units_range(r["units"])[0] for r in items)
        highs = sorted((units_range(r["units"])[1] for r in items), reverse=True)
        low, high = low + sum(lows[:n]), high + sum(highs[:n])
    for units in pools.values():
        a, b = units_range(units)
        low, high = low + a, high + b
    return low, high


def order_rows(prog):
    """Within each section: its note row (if any), the Required group, then the other groups in page order."""
    sections = collections.OrderedDict()
    for r in prog.rows:
        sections.setdefault(r["section"], []).append(r)
    ordered = []
    for name, rows in sections.items():
        if name in prog.section_notes:
            ordered.append({"major_id": "", "section": name, "group_label": "", "rule": "note", "pick_n": "",
                            "pick_units": "", "subject": "", "catalog_num": "", "num_min": "", "num_max": "",
                            "exclude": "", "title": "", "units": "", "note": ". ".join(prog.section_notes[name]),
                            "_h2": rows[0]["_h2"], "_code": ""})
        ordered += [r for r in rows if r["group_label"] == "Required"] + [r for r in rows if r["group_label"] != "Required"]
    for name, notes in prog.section_notes.items():
        if name not in sections:     # a requirement with no courses ('Language Requirement'): a section of its note
            ordered.append({"major_id": "", "section": name, "group_label": "", "rule": "note", "pick_n": "",
                            "pick_units": "", "subject": "", "catalog_num": "", "num_min": "", "num_max": "",
                            "exclude": "", "title": "", "units": "", "note": ". ".join(notes), "_h2": name, "_code": ""})
    prog.rows = ordered


def check_units(prog, totals):
    order = list(dict.fromkeys(r["_h2"] for r in prog.rows))
    for h2, (low_stated, high_stated, kind) in totals.items():
        scope = {h2}
        if h2 == "Major" and h2 in order:
            # 'Capstone Requirement', 'Major Electives' after the Major heading, with no total of their own
            scope |= {x for x in order[order.index(h2) + 1:] if x not in totals and not LANGUAGE_BLOCK.search(x)
                      and not GWAR_BLOCK.search(x)}
        rows = [r for r in prog.rows if r["_h2"] in scope]
        low, high = listed_units(rows)
        if kind == "exact":
            stated = f"{low_stated}-{high_stated}" if high_stated != low_stated else str(low_stated)
            ok = low_stated <= low <= high_stated or low_stated <= high <= high_stated or (low <= low_stated and high >= high_stated)
            inside = low_stated <= low and high <= high_stated
            verdict = "inside" if inside else "overlaps" if ok else "MISMATCH"
            notes = " ".join(r["note"] for r in rows if r["rule"] == "note")
            ge = re.search(r"general education[^.()]*\((\d+) units?\)", notes, re.I)
            if verdict == "MISMATCH" and ge and low_stated <= low + int(ge.group(1)) <= high_stated:
                verdict = f"short by {ge.group(1)}: a General Education requirement with no course is part of the total"
        else:
            stated = f"at least {low_stated}"
            verdict = "inside" if low >= low_stated else "MISMATCH"
        listed = f"{low}-{high}" if low != high else str(low)
        derived = " (elective units were worked out from this total)" if h2 in prog.derived else ""
        prog.units_checks.append((h2, stated, listed, verdict + derived))
        if verdict == "MISMATCH" or verdict.startswith("short by"):
            prog.flag(f"Units check for {h2}: page says {stated}, listed courses add up to {listed}"
                      + ("." if verdict == "MISMATCH" else f" ({verdict})."))


# ---------- major ids ----------

ID_STOP = {"and", "of", "in", "the", "for", "with", "a", "an", "to", "emphasis", "specialization", "concentration",
           "track", "plus"}


DEGREE_SLUGS = {"ba", "bs", "bm", "bfa", "ma", "ms", "mba", "phd"}
# the API and the page accept ids up to this long (backend/routes/majors.py, frontend/js/store.js)
MAX_ID_LEN = 64
# major names that have commas of their own, and the words their ids start with
BASE_NAMES = {
    "Business Administration": "ba",     # the live ids: ba_general_bs, ba_accounting_bs, ...
    "Television, Film and New Media": "television_film_new_media",
    "Lesbian, Gay, Bisexual, Transgender, Queer, and Plus (LGBTQ+) Studies": "lgbtq_studies",
    "Language, Culture, and Society": "language_culture_society",
    "Speech, Language, and Hearing Sciences": "speech_language_hearing_sciences",
}
# long phrases in a program name, shortened for its id
ID_PHRASES = [
    (r"in preparation for the single subject teaching credential.*?(?=,|$)", "credential"),
    (r"preparation for the single subject teaching credential.*?(?=,|$)", "credential"),
    (r"second bachelor[’']?s degree", "second"),
    (r"(?:and )?certificate of the american chemical society", "american chemical society"),
]


def slug_words(text):
    words = re.findall(r"[a-z0-9]+", text.lower().replace("’", "").replace("'", ""))
    return [w for w in words if w not in ID_STOP]


def degree_slug(degree):
    return "".join(ch for ch in degree.lower() if ch.isalpha())


def id_parts(name):
    """'Civil Engineering, Emphasis in X' -> ('Civil Engineering', 'civil_engineering', ', Emphasis in X')."""
    for base, head in BASE_NAMES.items():
        if name == base or name.startswith(base + ","):
            return base, head, name[len(base):]
    base, _, rest = name.partition(",")
    return base.strip(), "_".join(slug_words(base) or ["major"]), rest


def propose_id(name, degree):
    """Full words, as decided with Mehar: 'Aerospace Engineering', 'B.S.' -> 'aerospace_engineering_bs';
    'Kinesiology, Emphasis in Fitness Specialist' -> 'kinesiology_fitness_specialist_bs'. Words already in the
    base are not repeated ('music_education_bm'). Emphasis words are dropped from the end only if the id would
    be longer than MAX_ID_LEN."""
    _, head, rest = id_parts(name)
    for pattern, word in ID_PHRASES:
        rest = re.sub(pattern, f" {word} ", rest, flags=re.I)
    # the whole base again is dropped ('Music, Music Education' -> music_education, 'Biology, Marine Biology' ->
    # biology_marine); part of it is kept ('Public Health, Environmental Health' -> public_health_environmental_health)
    base_words, words = head.split("_"), slug_words(rest)
    n = len(base_words)
    for i in range(len(words) - n + 1):
        if words[i:i + n] == base_words:
            words = words[:i] + words[i + n:]
            break
    words = list(dict.fromkeys(words))
    tail = degree_slug(degree) or "x"
    while words and len("_".join([head] + words + [tail])) > MAX_ID_LEN:
        words.pop()
    return "_".join([head] + words + [tail])[: MAX_ID_LEN]


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
    """Gives every program its major_id: the ids file first, then the 7 known ids, then a new one (full words,
    see propose_id). New ids are added to `ids`; collisions are logged. Existing ids are never changed."""
    taken = {r["major_id"]: poid for poid, r in ids.items()}
    taken.update({mid: poid for poid, mid in KNOWN_IDS.items()})
    changed = False
    for prog in programs:
        poid = prog.poid or ""
        if poid in ids:
            prog.major_id = ids[poid]["major_id"]
            continue
        mid = KNOWN_IDS[poid] if poid in KNOWN_IDS else propose_id(prog.name, prog.degree)
        if mid in taken and taken[mid] != poid:
            n = 2
            while f"{mid}_{n}" in taken:
                n += 1
            log.append(f"id collision on '{mid}': {prog.name}, {prog.degree} (poid {poid}) gets '{mid}_{n}'")
            mid = f"{mid}_{n}"
        if not re.fullmatch(r"[a-z0-9_]+", mid) or len(mid) > MAX_ID_LEN:
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


def is_abbreviation(short, full):
    """'Intro to Eng Materials' of 'Introduction to Engineering Materials': every word of the short title
    is a shortening (same first letter, letters in order) of a later word of the full one.
    The official schedule cuts titles to about 25 characters."""
    words = lambda t: re.findall(r"[a-z0-9]+", t.lower().replace("&", " and "))
    long_words = words(full)
    i = 0
    for w in words(short):
        while i < len(long_words) and not (long_words[i][0] == w[0] and _in_order(w, long_words[i])):
            i += 1
        if i == len(long_words):
            return False
        i += 1
    return True


def _in_order(short, word):
    it = iter(word)
    return all(ch in it for ch in short)


# ---------- output ----------

def write_csv(path, fields, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def major_row(prog):
    return {"major_id": prog.major_id, "name": prog.name, "degree": prog.degree, "college": "",
            "catalog_year": CATALOG_YEAR, "status": "coming_soon"}


def write_staging(programs, out_dir, log, offered, titles, batch=None):
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    for prog in programs:
        for r in prog.rows:
            r["major_id"] = prog.major_id
            rows.append(r)
    write_csv(os.path.join(out_dir, "majors.csv"), MAJOR_FIELDS, [major_row(p) for p in programs])
    write_csv(os.path.join(out_dir, "major_requirements.csv"), REQ_FIELDS, rows)
    report = build_report(programs, log, offered, titles, batch)
    with open(os.path.join(out_dir, "REPORT.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write(report)
    return report


def shown_path(path):
    """A path for the report: relative to the project when inside it, forward slashes."""
    full = os.path.abspath(path)
    if os.path.commonpath([full, ROOT]) == ROOT:
        full = os.path.relpath(full, ROOT)
    return full.replace(os.sep, "/") if not path.startswith("http") else path


def coverage(prog, offered):
    """{rule: (with sections [(code, n)], without [code])}, each course once, in row order."""
    out = collections.OrderedDict((rule, ([], [])) for rule in ("required", "choose", "pool"))
    seen = set()
    for r in prog.rows:
        if not r["catalog_num"] or r["_code"] in seen or r["rule"] not in out:
            continue
        seen.add(r["_code"])
        hit = offered.get((r["subject"], r["catalog_num"]))
        if hit:
            out[r["rule"]][0].append((r["_code"], hit["sections"]))
        else:
            out[r["rule"]][1].append(r["_code"])
    return out


def coverage_lines(prog, offered):
    names = {"required": "Required courses", "choose": "Pick-n group courses", "pool": "Elective pool courses"}
    lines = []
    for rule, (have, missing) in coverage(prog, offered).items():
        total = len(have) + len(missing)
        if not total:
            continue
        lines.append(f"- {names[rule]}: {len(have)} of {total} have sections")
        if have:
            lines.append("  - with sections: " + ", ".join(f"{c} ({n})" for c, n in have))
        if missing:
            lines.append("  - no sections: " + ", ".join(missing))
    required = {(r["subject"], r["catalog_num"]) for r in prog.rows if r["rule"] == "required"}
    for r in prog.rows:
        if r["rule"] != "open":
            continue
        subjects, low, high = set(r["subject"].split("|")), int(r["num_min"] or 0), int(r["num_max"] or 9999)
        excluded = {tuple(c.split()) for c in r.get("exclude", "").split("|") if c}
        found = [f"{s} {n}" for (s, n), hit in sorted(offered.items()) if s in subjects and hit["sections"]
                 and re.match(r"\d+", n) and low <= int(re.match(r"\d+", n).group()) <= high
                 and (s, n) not in excluded and (s, n) not in required]
        lines.append(f"- Open rule '{r['group_label']}' (without excluded and already-required courses): "
                     f"{len(found)} courses with sections"
                     + (f": {', '.join(found)}" if found else ""))
    return lines


def md(text):
    return text.replace("|", "\\|")


def build_report(programs, log, offered, titles, batch=None):
    lines = [f"# Catalog import report ({CATALOG_YEAR})", "",
             "Staging only: nothing here is live. Every major is `coming_soon`. Check each one against its catalog "
             "page, then promote it with `python3 scripts/import_catalog_majors.py --promote <major_id>`.", "",
             "| Majors processed | Requirement rows | Majors with open review items |", "| --- | --- | --- |",
             f"| {len(programs)} | {sum(len(p.rows) for p in programs)} | {sum(1 for p in programs if p.review)} |", ""]
    if batch is not None:
        missing = [b for b in batch if not b[4]]
        lines += [f"## Batch check: {len(batch) - len(missing)} of {len(batch)} pages found", "",
                  "| # | Program | major_id | Page |", "| --- | --- | --- | --- |"]
        lines += [f"| {n} | {md(name)}, {degree} | `{mid}` | {'found' if ok else '**missing**'} |"
                  for n, (name, degree, url, mid, ok) in enumerate(batch, 1)]
        lines.append("")
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
            if r["rule"] == "note":
                continue
            groups.setdefault((r["section"], r["group_label"], r["rule"], r["pick_n"], r["pick_units"]), []).append(r["_code"])
        for (section, label, rule, pick_n, pick_units), codes in groups.items():
            rule_text = rule + (f" {pick_n}" if pick_n else "") + (f", {pick_units} units" if pick_units else "")
            lines.append(f"| {md(section)} | {md(label)} | {rule_text} | {len(codes)}: {', '.join(codes)} |")
        lines.append("")
        notes = [r for r in prog.rows if r["rule"] == "note"]
        lines += ["### Section notes (shown once under the heading)", ""]
        lines += [f"- **{md(r['section'])}**: {md(r['note'])}" for r in notes] or ["- none"]
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
        lines += ["### Coverage (sections in data/cleaned)", ""]
        if offered is None:
            lines.append("- data/cleaned not found, skipped")
        else:
            lines += coverage_lines(prog, offered)
        lines.append("")
        lines += ["### Title differences (catalog vs class data)", ""]
        diffs, shortened = [], []
        if titles:
            for r in prog.rows:
                theirs = titles.get((r["subject"], r["catalog_num"]))
                if not theirs or same_title(theirs, r["title"]) or r["_code"] in [d[0] for d in diffs] + shortened:
                    continue
                if is_abbreviation(theirs, r["title"]):
                    shortened.append(r["_code"])
                else:
                    diffs.append((r["_code"], r["title"], theirs))
        lines += [f"- {c}: catalog \"{md(a)}\", class data \"{md(b)}\"" for c, a, b in diffs] or ["- none"]
        if shortened:
            lines.append(f"- {len(shortened)} more only shortened in the class data (not a real difference): "
                         + ", ".join(shortened))
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


def title_key(name, degree):
    squash = lambda t: re.sub(r"[^a-z0-9]+", " ", (t or "").lower().replace("’", "'")).strip()
    return squash(name), squash(degree)


def run(pages, out_dir, ids_file=IDS_FILE, expect=None):
    """pages: [(source, html, url)] -> programs written to out_dir.
    A page is matched to its major by what is inside it (the poid in the saved-from URL, the
    canonical link or the page's own links, else its title), never by the file name.
    expect: [(name, degree, url)] that should be among the pages (a batch list); the report says
    which were found and which are missing."""
    log, programs = [], []
    ids = read_ids(ids_file)
    by_title = {title_key(r.get("name"), r.get("degree")): poid for poid, r in ids.items()}
    for source, text, url in pages:
        if is_listing(text):
            continue
        if is_bot_challenge(text):
            log.append(f"{shown_path(source)}: a saved bot-check page, not a program page; skipped")
            continue
        prog = parse_program(text, source, url)
        if not prog.title:
            log.append(f"{shown_path(source)}: no program title on the page; skipped")
            continue
        from_title = by_title.get(title_key(prog.name, prog.degree))
        if not prog.poid:
            if not from_title:
                log.append(f"{shown_path(source)}: no program id (poid) and the title '{prog.title}' is not in "
                           f"{shown_path(ids_file)}; skipped")
                continue
            prog.poid = from_title
            log.append(f"{shown_path(source)}: no program id in the page; matched by its title to poid {from_title}")
        elif prog.poid in ids and title_key(prog.name, prog.degree) != title_key(ids[prog.poid].get("name"),
                                                                               ids[prog.poid].get("degree")):
            prog.flag(f"The page title '{prog.title}' differs from the listing's "
                      f"'{ids[prog.poid].get('name')}, {ids[prog.poid].get('degree')}' for poid {prog.poid}; check "
                      f"that the right page was saved.")
        programs.append(prog)
    dupes = [p for p, n in collections.Counter(p.poid for p in programs).items() if n > 1]
    if dupes:
        log.append(f"same program read more than once (poid {', '.join(dupes)}); keeping the first copy")
        seen = set()
        programs = [p for p in programs if not (p.poid in seen or seen.add(p.poid))]
    if assign_ids(programs, ids, log):
        write_ids(ids, ids_file)
        log.append(f"new major_ids saved to {shown_path(ids_file)}")
    batch = None
    if expect is not None:
        found = {p.poid for p in programs}
        batch = []
        for name, degree, url in expect:
            poid = (re.search(r"poid=(\d+)", url) or [None, None])[1]
            mid = ids.get(poid, {}).get("major_id", "")
            batch.append((name, degree, url, mid, poid in found))
    offered, titles = class_data()
    report = write_staging(programs, out_dir, log, offered, titles, batch)
    return programs, report


def read_expect(path):
    """A batch list (name<TAB>degree<TAB>url lines, like scripts/catalog_urls.txt)."""
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.rstrip("\n").split("\t")
            url = next((p for p in parts if p.startswith("http")), "")
            out.append((parts[0] if len(parts) > 1 else url, parts[1] if len(parts) > 2 else "", url))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--discover", action="store_true", help="read the program listing and write --urls-out")
    mode.add_argument("--urls", help="file with one catalog program URL per line")
    mode.add_argument("--html-dir", action="append",
                      help="folder of saved program pages (offline); give it more than once to stage several folders")
    mode.add_argument("--promote", metavar="MAJOR_ID", help="copy one staged major into data/majors")
    ap.add_argument("--out", default=STAGING_DIR, help="staging folder (default data/majors/staging)")
    ap.add_argument("--listing-html", help="--discover: use this saved listing page instead of fetching it")
    ap.add_argument("--urls-out", default=URLS_FILE, help="--discover: where to write the URL list")
    ap.add_argument("--ids", default=IDS_FILE, help="major_id file (default scripts/catalog_major_ids.csv)")
    ap.add_argument("--expect", help="a batch list (like scripts/catalog_batch1_urls.txt): report which of its "
                                     "programs were found among the pages and which are missing")
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
        for folder in args.html_dir:
            for name in sorted(os.listdir(folder)):
                if name.lower().endswith((".html", ".htm")):
                    path = os.path.join(folder, name)
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
    expect = read_expect(args.expect) if args.expect else None
    programs, _ = run(pages, args.out, args.ids, expect)
    print(f"{len(programs)} majors, {sum(len(p.rows) for p in programs)} rows, "
          f"{sum(1 for p in programs if p.review)} with review items. See {shown_path(os.path.join(args.out, 'REPORT.md'))}")
    if expect is not None:
        found = {p.poid for p in programs}
        for n, (name, degree, url) in enumerate(expect, 1):
            poid = (re.search(r"poid=(\d+)", url) or [None, None])[1]
            print(f"  {n:>2}. {'found  ' if poid in found else 'MISSING'} {name}, {degree}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

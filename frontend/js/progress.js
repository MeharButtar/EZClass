// Requirement counting for My Major that doesn't need the page, so it can be
// tested on its own (tests/js/progress.test.mjs).

// "3" -> 3, "1-4" -> 1 (the smallest the course can be), "14-15" -> 14
export const units = (value) => Number.parseFloat(String(value ?? "")) || 0;

// Pool sections (CS upper division electives): units from all their pool
// groups together. The catalog can list one course in two groups of the same
// section (M E 544 is in both Mechanical Systems and Thermal Systems), so each
// course code counts once.
export function sectionPool(section, isDone) {
  const need = units(section.pool_units);
  const done = new Map();
  for (const group of section.groups) {
    if (group.rule !== "pool") continue;
    for (const c of group.courses) if (isDone(c.code) && !done.has(c.code)) done.set(c.code, c);
  }
  const doneUnits = [...done.values()].reduce((n, c) => n + units(c.units), 0);
  return { text: `${doneUnits} of ${section.pool_units} units`, finished: doneUnits >= need,
           ratio: need ? Math.min(doneUnits / need, 1) : 0, needUnits: need, doneUnits: Math.min(doneUnits, need) };
}

// Pick-n groups: the units of the n smallest courses (a pick of CHEM 202 (4) or
// CHEM 200 (5) needs 4), or the group's pick_units when the catalog gives them.
// A course with no units counts as 3.
export function chooseNeedUnits(group) {
  // pick_units, when set, is what the pick needs (a lecture+lab pair: BIOL 203 and 203L = 4);
  // "0" means shown but not counted (a competency or writing requirement outside the major's units)
  if (group.pick_units !== null && group.pick_units !== undefined && String(group.pick_units).trim() !== "") {
    return units(group.pick_units);
  }
  const pick = group.pick_n || 1;
  const sizes = group.courses.map((c) => units(c.units) || 3).sort((a, b) => a - b);
  const counted = sizes.slice(0, pick);
  return counted.reduce((n, u) => n + u, 0) + Math.max(pick - counted.length, 0) * 3;
}

// The courses an open rule ("any ACCTG 300-599") lists: without the rule's
// exclude list (ACCTG 325, 326) and without courses the same major already
// requires (they can't count twice). hidden says how many were left out.
export function openChoices(courses, exclude = [], requiredCodes = new Set()) {
  return mergeOpen([{ courses, exclude }], [], requiredCodes);
}

// Course codes in order: subject, then the catalog number as a number ("CHEM 300" before "CHEM 1000").
export const byCode = (a, b) => a.code.localeCompare(b.code, "en", { numeric: true });

// An open rule made of several rows: every range's courses (each range leaves out its own exclude list),
// plus the courses the rule lists by name, each course once, without the major's required courses,
// sorted by code. ranges: [{ courses, exclude }], listed: [course]. Listed courses are only shown when
// they have sections, like the range results.
export function mergeOpen(ranges, listed = [], requiredCodes = new Set()) {
  const seen = new Map();
  const excludedCodes = new Set();
  for (const range of ranges) {
    const excluded = new Set(range.exclude || []);
    for (const c of range.courses || []) {
      if (excluded.has(c.code)) { excludedCodes.add(c.code); continue; }
      if (!seen.has(c.code)) seen.set(c.code, c);
    }
  }
  for (const c of listed) {
    if (c.has_sections && !seen.has(c.code)) seen.set(c.code, c);
  }
  // a course one range excludes still counts if another range or the list has it
  for (const code of seen.keys()) excludedCodes.delete(code);
  const shown = [];
  const hidden = { excluded: excludedCodes.size, required: 0 };
  for (const c of seen.values()) {
    if (requiredCodes.has(c.code)) hidden.required += 1;
    else shown.push(c);
  }
  shown.sort(byCode);
  return { shown, hidden };
}

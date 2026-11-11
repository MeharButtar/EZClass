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

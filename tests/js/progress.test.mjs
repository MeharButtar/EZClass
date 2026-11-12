// Tests for the My Major elective pool counter (frontend/js/progress.js).
// Run: node --test tests/js/progress.test.mjs

import assert from "node:assert/strict";
import { test } from "node:test";
import { chooseNeedUnits, mergeOpen, openChoices, sectionPool, units } from "../../frontend/js/progress.js";

const course = (code, u = "3") => ({ code, units: u });

// Like Mechanical Engineering: M E 544 and M E 570 are listed in both groups.
const meElectives = {
  pool_units: "12",
  groups: [
    { rule: "pool", courses: [course("M E 544"), course("M E 570"), course("M E 530")] },
    { rule: "pool", courses: [course("M E 544"), course("M E 570"), course("M E 580")] },
  ],
};
const doneOf = (...codes) => (code) => codes.includes(code);

test("a course listed in two pool groups counts once", () => {
  const p = sectionPool(meElectives, doneOf("M E 544"));
  assert.equal(p.doneUnits, 3);
  assert.equal(p.text, "3 of 12 units");
  assert.equal(p.finished, false);
});

test("different courses still add up, duplicates once each", () => {
  const p = sectionPool(meElectives, doneOf("M E 544", "M E 570", "M E 530", "M E 580"));
  assert.equal(p.text, "12 of 12 units");
  assert.equal(p.finished, true);
  assert.equal(p.ratio, 1);
  const three = sectionPool(meElectives, doneOf("M E 544", "M E 570", "M E 580"));
  assert.equal(three.text, "9 of 12 units");
  assert.equal(three.finished, false);
});

test("only pool groups count, and done units are capped at what the pool needs", () => {
  const section = {
    pool_units: "6",
    groups: [
      { rule: "required", courses: [course("CS 150")] },
      { rule: "pool", courses: [course("CS 420"), course("CS 450"), course("CS 460")] },
    ],
  };
  const p = sectionPool(section, doneOf("CS 150", "CS 420", "CS 450", "CS 460"));
  assert.equal(p.text, "9 of 6 units");
  assert.equal(p.doneUnits, 6);
  assert.equal(p.needUnits, 6);
  assert.equal(p.finished, true);
});

test("unit strings: ranges use the smallest number", () => {
  assert.equal(units("3"), 3);
  assert.equal(units("1-4"), 1);
  assert.equal(units(""), 0);
  assert.equal(units(null), 0);
});

test("a pick-1 group needs its smallest course's units, not a fixed 3", () => {
  const chem = { pick_n: 1, courses: [course("CHEM 202", "4"), course("CHEM 200", "5")] };
  assert.equal(chooseNeedUnits(chem), 4);
  const mktg = { pick_n: 1, courses: [course("MKTG 470", "4"), course("MKTG 480", "4")] };
  assert.equal(chooseNeedUnits(mktg), 4);
  assert.equal(chooseNeedUnits({ pick_n: 2, courses: [course("A 1", "1"), course("A 2", "3"), course("A 3", "2")] }), 3);
  assert.equal(chooseNeedUnits({ courses: [course("X 1", "")] }), 3);   // no units: counts as 3
});

test("open rule lists leave out excluded and already-required courses", () => {
  const found = ["ACCTG 325", "ACCTG 326", "ACCTG 331", "ACCTG 409", "ACCTG 503"].map((c) => course(c));
  const { shown, hidden } = openChoices(found, ["ACCTG 325", "ACCTG 326"], new Set(["ACCTG 331"]));
  assert.deepEqual(shown.map((c) => c.code), ["ACCTG 409", "ACCTG 503"]);
  assert.deepEqual(hidden, { excluded: 2, required: 1 });
  assert.equal(openChoices(found).shown.length, 5);
});

test("a pick group with pick_units needs those units (a lecture+lab pair)", () => {
  const pair = { pick_n: 2, pick_units: "4",
                 courses: [course("BIOL 203", "3"), course("BIOL 203L", "1"), course("BIOL 204", "3"), course("BIOL 204L", "1")] };
  assert.equal(chooseNeedUnits(pair), 4);
  assert.equal(chooseNeedUnits({ ...pair, pick_units: null }), 2);   // without it: the two smallest
});

test("pick_units 0: a group that is shown but not counted (math competency, writing course)", () => {
  const sequences = { pick_n: 3, pick_units: "0",
                      courses: ["STAT 250", "STAT 350A", "STAT 350B", "SOC 201", "SOC 406", "SOC 407"].map((c) => course(c)) };
  assert.equal(chooseNeedUnits(sequences), 0);
});

const offered = (code, u = "3") => ({ code, units: u, has_sections: true });

test("Biology: two ranges (BIOL 350-599, CHEM 300-599), each with its own exclude list, sorted and once each", () => {
  const biol = { courses: ["BIOL 452", "BIOL 350", "BIOL 510", "BIOL 366"].map((c) => offered(c)), exclude: ["BIOL 452"] };
  const chem = { courses: ["CHEM 560", "CHEM 300", "CHEM 432", "CHEM 365"].map((c) => offered(c)), exclude: ["CHEM 300", "CHEM 560"] };
  const { shown, hidden } = mergeOpen([biol, chem], [], new Set(["BIOL 366", "CHEM 365"]));
  assert.deepEqual(shown.map((c) => c.code), ["BIOL 350", "BIOL 510", "CHEM 432"]);
  assert.deepEqual(hidden, { excluded: 3, required: 2 });
});

test("Political Science: a range plus listed courses from other subjects; a course in both shows once", () => {
  const pols = { courses: ["POL S 390W", "POL S 301A", "POL S 422"].map((c) => offered(c)), exclude: ["POL S 390W"] };
  const listed = [offered("WGSS 375"), offered("AFRAS 321"), { code: "AMIND 485", units: "3", has_sections: false },
                  offered("POL S 422")];
  const { shown, hidden } = mergeOpen([pols], listed);
  assert.deepEqual(shown.map((c) => c.code), ["AFRAS 321", "POL S 301A", "POL S 422", "WGSS 375"]);   // no sections: not shown
  assert.deepEqual(hidden, { excluded: 1, required: 0 });
});

test("excluded courses and the major's required courses are left out of an open rule", () => {
  const acctg = { courses: ["ACCTG 325", "ACCTG 326", "ACCTG 331", "ACCTG 409", "ACCTG 503"].map((c) => offered(c)),
                  exclude: ["ACCTG 325", "ACCTG 326"] };
  const { shown, hidden } = mergeOpen([acctg], [], new Set(["ACCTG 331"]));
  assert.deepEqual(shown.map((c) => c.code), ["ACCTG 409", "ACCTG 503"]);
  assert.deepEqual(hidden, { excluded: 2, required: 1 });
  // the single-range helper the page used before gives the same answer
  assert.deepEqual(openChoices(acctg.courses, acctg.exclude, new Set(["ACCTG 331"])).shown.map((c) => c.code),
                   ["ACCTG 409", "ACCTG 503"]);
});


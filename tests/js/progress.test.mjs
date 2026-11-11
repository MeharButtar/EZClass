// Tests for the My Major elective pool counter (frontend/js/progress.js).
// Run: node --test tests/js/progress.test.mjs

import assert from "node:assert/strict";
import { test } from "node:test";
import { sectionPool, units } from "../../frontend/js/progress.js";

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

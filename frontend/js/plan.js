// The active plan as full section objects. The store only keeps section ids;
// this loads the details (cached in api.js) and calls back on every change,
// so the calendar and the lists on each page always draw the same plan.
//
// If a saved id is no longer in the class data (the section was removed in a
// data update), it is dropped from the plans and the student is told once.

import { sectionsByIds } from "./api.js";
import { forgetSections, getState, subscribe } from "./store.js";
import { toast } from "./ui.js";

// fn(sections, state, error). Called once right away and again after every change.
export function watchPlan(fn) {
  let seq = 0;
  async function run(state) {
    const mine = ++seq;
    const plan = state.plans[state.activePlan];
    try {
      const sections = await sectionsByIds(plan.sectionIds);
      if (mine !== seq) return;
      if (sections.length < plan.sectionIds.length) {
        const found = new Set(sections.map((s) => s.id));
        dropMissing(plan.sectionIds.filter((id) => !found.has(id)));
      }
      fn(sections, state, null);
    } catch (error) {
      if (mine === seq) fn([], state, error);
    }
  }
  run(getState());
  return subscribe((state) => run(state));
}

// Several watchers on one page notice the same missing ids; only the one that
// actually removes them tells the student.
function dropMissing(ids) {
  queueMicrotask(() => {
    if (!forgetSections(ids)) return;
    toast(ids.length === 1
      ? "A class in your plan is no longer in the schedule, so it was removed."
      : `${ids.length} classes in your plan are no longer in the schedule, so they were removed.`);
  });
}

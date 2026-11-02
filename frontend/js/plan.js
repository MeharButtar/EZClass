// The active plan as full section objects. The store only keeps section ids;
// this loads the details (cached in api.js) and calls back on every change,
// so the calendar and the lists on each page always draw the same plan.

import { sectionsByIds } from "./api.js";
import { getState, subscribe } from "./store.js";

// fn(sections, state, error). Called once right away and again after every change.
export function watchPlan(fn) {
  let seq = 0;
  async function run(state) {
    const mine = ++seq;
    const plan = state.plans[state.activePlan];
    try {
      const sections = await sectionsByIds(plan.sectionIds);
      if (mine === seq) fn(sections, state, null);
    } catch (error) {
      if (mine === seq) fn([], state, error);
    }
  }
  run(getState());
  return subscribe((state) => run(state));
}

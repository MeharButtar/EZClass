// The docked week calendar on My Major, GE and Search. On wide screens it sits
// on the right and stays in view while the lists scroll. On phones it is a
// bottom sheet opened with the "My week" button.

import { mountCalendar } from "./calendar.js";
import { watchPlan } from "./plan.js";
import { planUnits } from "./stats.js";
import { el, plural } from "./ui.js";

export function mountDock(aside) {
  const title = el("h2", { class: "dock-title", id: "dock-title" }, "My week");
  const summary = el("p", { class: "dock-summary muted small", "aria-live": "polite" });
  const close = el("button", { type: "button", class: "icon-btn dock-close", "aria-label": "Close my week" }, "×");
  const calHolder = el("div", { class: "dock-cal" });
  aside.setAttribute("aria-labelledby", "dock-title");
  aside.append(
    el("div", { class: "dock-head" }, el("div", {}, title, summary), close),
    calHolder,
    el("a", { class: "btn btn-block", href: "schedule.html" }, "Open My Schedule"));

  const calendar = mountCalendar(calHolder, {
    variant: "dock",
    emptyText: "Point at a section to preview it here. Classes you add stay on this week.",
  });

  // phone: a floating button opens the sheet
  const opener = el("button", { type: "button", class: "btn btn-primary week-fab", "aria-expanded": "false", "aria-controls": aside.id });
  const backdrop = el("div", { class: "sheet-backdrop", hidden: true });
  document.body.append(backdrop, opener);

  const setOpen = (open) => {
    aside.classList.toggle("sheet-open", open);
    backdrop.hidden = !open;
    opener.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("sheet-locked", open);
    if (open) close.focus();
    else opener.focus({ preventScroll: true });
  };
  opener.addEventListener("click", () => setOpen(true));
  close.addEventListener("click", () => setOpen(false));
  backdrop.addEventListener("click", () => setOpen(false));
  aside.addEventListener("keydown", (e) => { if (e.key === "Escape" && aside.classList.contains("sheet-open")) setOpen(false); });

  watchPlan((sections, state, error) => {
    const plan = state.plans[state.activePlan];
    const units = planUnits(sections);   // each course once, backups included only once
    title.textContent = `My week · ${plan.name}`;
    summary.textContent = error ? "Could not load your plan's classes." : sections.length
      ? `${plural(sections.length, "class", "classes")}, ${plural(units, "unit")}`
      : "Nothing added yet";
    opener.textContent = `My week (${plan.sectionIds.length})`;
    calendar.update(sections);
  });
  return calendar;
}

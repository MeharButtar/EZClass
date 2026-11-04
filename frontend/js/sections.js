// Section rows and course cards, shared by My Major, GE and Search.
//
// A section row shows the day strip, the time, professor, room and seats, and
// an Add button. Pointing at a row (mouse hover or keyboard focus) draws the
// ghost on the calendar. On touch screens there is no hover, so the first tap
// on Add shows the ghost and the second tap adds.
//
// Every Add button on the page is kept in sync with the active plan, and rows
// that would overlap something already in the plan say so.

import { setGhost } from "./calendar.js";
import { CONFIG } from "./config.js";
import { watchPlan } from "./plan.js";
import { activePlan, isCompleted, isInPlan, toggleCompleted, toggleSection } from "./store.js";
import { formatRange, overlaps } from "./time.js";
import { $$, dayStrip, el, plural, professorLink } from "./ui.js";

export const sectionLabel = (s) => `${s.code} (Sec ${s.sectionNumber})`;

// GE area pills plus the three GE tags (same wording as v1's results table).
export function geBadges(areas = [], { cd = false, es = false, ai = false } = {}) {
  return [
    ...areas.map((a) => el("span", { class: "pill pill-ge", title: `Counts for GE area ${a}` }, `GE ${a}`)),
    cd ? el("span", { class: "pill pill-tag", title: "Cultural diversity" }, "CD") : null,
    es ? el("span", { class: "pill pill-tag", title: "Counts for the Ethnic Studies graduation requirement" }, "ES") : null,
    ai ? el("span", { class: "pill pill-tag", title: "Counts for American Institutions" }, "AI") : null,
  ];
}

// "Nguyen · AH 2140 · 40 seats", with the professor's name linked to RateMyProfessors
function sectionMeta(s) {
  const parts = [professorLink(s.professor, s.professorLast), s.room || "Room TBA", s.capacity ? `${s.capacity} seats` : null].filter(Boolean);
  return parts.flatMap((part, i) => (i ? [" · ", part] : [part]));
}

const noHover = window.matchMedia("(hover: none)");
let armed = null;   // touch: the section whose Add button was tapped once

// section objects for the rows on this page, by id
const rowSections = new Map();

function addButton(s) {
  const button = el("button", { type: "button", class: "add-btn", dataset: { sectionId: s.id } });
  button.addEventListener("click", () => {
    if (noHover.matches && !isInPlan(s.id) && armed !== s.id) {
      armed = s.id;
      setGhost(s);
      syncRows();
      return;
    }
    armed = null;
    toggleSection(s.id, sectionLabel(s));
    setGhost(null);
  });
  return button;
}

export function sectionRow(s, { showCourse = false } = {}) {
  rowSections.set(s.id, s);
  const time = formatRange(s.startMin, s.endMin) || "No set time";
  const row = el("li", { class: "sec-row", dataset: { sectionId: s.id } },
    el("div", { class: "sec-when" }, dayStrip(s.dayList), el("span", { class: "sec-time" }, time)),
    el("div", { class: "sec-info" },
      el("span", { class: "sec-name" }, showCourse ? `${s.code} · Sec ${s.sectionNumber}` : `Section ${s.sectionNumber}`),
      showCourse && s.title ? el("span", { class: "sec-title" }, s.title) : null,
      el("span", { class: "sec-meta" }, sectionMeta(s)),
      showCourse && (s.geAreas.length || s.cd || s.es || s.ai)
        ? el("span", { class: "sec-tags" }, geBadges(s.geAreas, s)) : null,
      el("span", { class: "sec-clash", hidden: true })),
    addButton(s));
  row.addEventListener("mouseenter", () => { if (!noHover.matches) setGhost(s); });
  row.addEventListener("mouseleave", () => { if (!noHover.matches) setGhost(null); });
  row.addEventListener("focusin", () => setGhost(s));
  row.addEventListener("focusout", (e) => { if (!row.contains(e.relatedTarget)) setGhost(null); });
  syncRow(row);
  return row;
}

// ---------- keeping rows in sync with the plan ----------

let planSections = [];

function syncRow(row) {
  const id = Number(row.dataset.sectionId);
  const s = rowSections.get(id);
  if (!s) return;
  const added = isInPlan(id);
  const button = row.querySelector(".add-btn");
  const planName = activePlan().name;
  button.setAttribute("aria-pressed", String(added));
  button.textContent = added ? "✓ Added" : armed === id ? "Tap to add" : "+ Add";
  button.setAttribute("aria-label", added
    ? `Remove ${s.code} section ${s.sectionNumber} from ${planName}`
    : `Add ${s.code} section ${s.sectionNumber} to ${planName}`);
  row.classList.toggle("is-added", added);

  const clash = added ? null : planSections.find((p) => overlaps(p, s));
  const note = row.querySelector(".sec-clash");
  note.hidden = !clash;
  note.textContent = clash ? `Overlaps ${clash.code} in ${planName}` : "";
  row.classList.toggle("has-clash", Boolean(clash));
}

export function syncRows() {
  for (const row of $$(".sec-row[data-section-id]")) syncRow(row);
}

watchPlan((sections) => {
  planSections = sections;
  syncRows();
});

// ---------- course cards ----------

const unitsText = (units) => (units ? `${units} ${String(units) === "1" ? "unit" : "units"}` : "");

// course: { code, title, units, ge_areas, has_sections, section_count, note }
// sections: this course's sections (rendered the first time the card opens).
// options.takenToggle adds the "I already took this" switch (My Major).
export function courseCard(course, sections = [], { takenToggle = false, expanded = false, extraNote = null } = {}) {
  const offered = sections.length > 0;
  const bodyId = `course-${course.code.replace(/\W+/g, "-")}-${Math.random().toString(36).slice(2, 7)}`;
  const card = el("article", { class: `course${offered ? "" : " is-unoffered"}`, dataset: { code: course.code } });

  const tags = el("div", { class: "course-tags" },
    course.units ? el("span", { class: "pill" }, unitsText(course.units)) : null,
    geBadges(course.ge_areas || [], sections[0] || {}),
    el("span", { class: "pill pill-state", hidden: true }));

  const titleBits = [el("span", { class: "course-code" }, course.code), el("span", { class: "course-title" }, course.title || "")];
  const toggle = offered
    ? el("button", { type: "button", class: "course-toggle", "aria-expanded": "false", "aria-controls": bodyId },
        el("span", { class: "chev", "aria-hidden": "true" }), titleBits,
        el("span", { class: "course-count" }, plural(sections.length, "section")))
    : el("div", { class: "course-toggle is-static" }, titleBits,
        el("span", { class: "course-count" }, `Not offered in ${CONFIG.termName}, or not in our data yet`));

  const head = el("div", { class: "course-head" }, toggle, tags);
  if (takenToggle) {
    const box = el("input", { type: "checkbox", class: "switch", "aria-label": `I already took ${course.code}` });
    box.checked = isCompleted(course.code);
    box.addEventListener("change", () => toggleCompleted(course.code));
    head.append(el("label", { class: "taken" }, box, el("span", {}, "I took this")));
  }
  card.append(head);
  const note = [course.note, extraNote].filter(Boolean).join(" ");
  if (note) card.append(el("p", { class: "course-note" }, note));

  const body = el("div", { class: "course-body", id: bodyId, hidden: true });
  card.append(body);
  let filled = false;
  const setOpen = (open) => {
    if (!offered) return;
    if (open && !filled) {
      body.append(el("ul", { class: "sec-list" }, sections.map((s) => sectionRow(s))));
      filled = true;
    }
    body.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
    card.classList.toggle("is-open", open);
  };
  if (offered) toggle.addEventListener("click", () => setOpen(body.hidden));
  card.setOpen = setOpen;
  if (expanded) setOpen(true);
  return card;
}

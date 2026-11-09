// My Major: pick a major, see every class it requires, add sections.
//
// Requirements come from /api/majors/<id>/requirements as sections > groups >
// courses. Group rules:
//   required  every course is needed
//   choose    pick N of the courses listed
//   pool      the whole section needs N units from its groups (CS electives)
//   open      no list, a rule like "any PSY 300-599"; matching courses come from /api/courses
// A course counts as done when it is marked "I took this" or has a section in
// the active plan. Courses without sections stay on the list, greyed.

import "../nav.js";
import { findCourses, getMajors, getRequirements, sectionsForCourses } from "../api.js";
import { CONFIG } from "../config.js";
import { mountDock } from "../dock.js";
import { majorLabel, openMajorPrompt } from "../majorPrompt.js";
import { watchPlan } from "../plan.js";
import { courseCard } from "../sections.js";
import { getState, isCompleted, setMajor, subscribe } from "../store.js";
import { $, $$, clear, el, emptyBox, errorBox, loadingBox, plural } from "../ui.js";

const root = $("#major-root");
const notice = $("#major-notice");
const title = $("#major-title");
const sub = $("#major-sub");
const changeButton = $("#change-major");
changeButton.addEventListener("click", openMajorPrompt);
sub.textContent = `Every class your major requires, with the ${CONFIG.termName} sections under each one.`;

mountDock($("#dock"));

// ---------- numbers ----------

// "3" -> 3, "1-4" -> 1 (the smallest the course can be), "14-15" -> 14
const units = (value) => Number.parseFloat(String(value ?? "")) || 0;

let model = null;            // { majorId, major, tree, sectionsByCourse, openCourses }
let plannedCodes = new Set();

const isDone = (code) => isCompleted(code) || plannedCodes.has(code);

// What one group needs and how much of it is done. Pool groups are counted per
// section (see sectionPool), so they return null here.
function groupProgress(group, key) {
  const courses = group.rule === "open" ? (model.openCourses.get(key) || []) : group.courses;
  const done = courses.filter((c) => isDone(c.code));
  const doneUnits = done.reduce((n, c) => n + units(c.units), 0);
  if (group.rule === "required") {
    const need = group.courses.reduce((n, c) => n + units(c.units), 0);
    return { text: `${done.length} of ${courses.length} done`, finished: done.length === courses.length,
             ratio: courses.length ? done.length / courses.length : 0, needUnits: need, doneUnits };
  }
  if (group.rule === "choose") {
    const pick = group.pick_n || 1;
    const smallest = Math.min(...group.courses.map((c) => units(c.units)).filter(Boolean), 3);
    const counted = done.slice(0, pick);
    return { text: `${Math.min(done.length, pick)} of ${pick} picked`, finished: done.length >= pick,
             ratio: Math.min(done.length / pick, 1), needUnits: pick * smallest,
             doneUnits: counted.reduce((n, c) => n + units(c.units), 0) };
  }
  if (group.rule === "open") {
    const needUnits = units(group.pick_units) || (group.pick_n || 1) * 3;
    if (group.pick_n) {
      return { text: `${Math.min(done.length, group.pick_n)} of ${group.pick_n} courses`, finished: done.length >= group.pick_n,
               ratio: Math.min(done.length / group.pick_n, 1), needUnits, doneUnits: Math.min(doneUnits, needUnits) };
    }
    return { text: `${doneUnits} of ${group.pick_units || needUnits} units`, finished: doneUnits >= needUnits,
             ratio: Math.min(doneUnits / needUnits, 1), needUnits, doneUnits: Math.min(doneUnits, needUnits) };
  }
  return null;
}

// Pool sections (CS upper division electives): units from all their groups together.
function sectionPool(section) {
  const need = units(section.pool_units);
  const done = section.groups.filter((g) => g.rule === "pool").flatMap((g) => g.courses).filter((c) => isDone(c.code));
  const doneUnits = done.reduce((n, c) => n + units(c.units), 0);
  return { text: `${doneUnits} of ${section.pool_units} units`, finished: doneUnits >= need,
           ratio: need ? Math.min(doneUnits / need, 1) : 0, needUnits: need, doneUnits: Math.min(doneUnits, need) };
}

const groupKey = (si, gi) => `${si}:${gi}`;

function totals() {
  let need = 0, done = 0, finished = 0, count = 0;
  model.tree.sections.forEach((section, si) => {
    if (section.pool_units) {
      const p = sectionPool(section);
      need += p.needUnits; done += p.doneUnits; count += 1; finished += p.finished ? 1 : 0;
    }
    section.groups.forEach((group, gi) => {
      const p = groupProgress(group, groupKey(si, gi));
      if (!p) return;
      need += p.needUnits; done += p.doneUnits; count += 1; finished += p.finished ? 1 : 0;
    });
  });
  return { need, done, finished, count };
}

// ---------- rendering ----------

function progressPill(p) {
  return el("span", { class: `pill ${p.finished ? "pill-done" : ""}`, dataset: { progress: "" } },
    p.finished ? `✓ ${p.text}` : p.text);
}

function meter(ratio) {
  return el("div", { class: "meter", "aria-hidden": "true" }, el("span", { style: { width: `${Math.round(ratio * 100)}%` } }));
}

function ruleText(group) {
  if (group.rule === "required") return group.courses.length === 1 ? "Required" : "All required";
  if (group.rule === "choose") return `Pick ${group.pick_n || 1} of ${group.courses.length}`;
  if (group.rule === "pool") return "Counts toward the units above";
  if (group.rule === "open") {
    const o = group.open || {};
    const range = o.min || o.max ? ` ${o.min ?? ""}–${o.max ?? ""}` : "";
    return `Any ${(o.subjects || []).join(", ")}${range}`;
  }
  return group.rule;
}

function summaryCard() {
  const t = totals();
  const stat = (num, label, attr) => el("div", {}, el("div", { class: "stat-num", dataset: { stat: attr } }, num), el("div", { class: "stat-label" }, label));
  return el("div", { class: "summary", id: "major-summary" },
    stat(`≈ ${t.need}`, "units the major needs (estimate)", "need"),
    stat(String(t.done), "units covered by classes you took or planned", "done"),
    stat(`${t.finished} of ${t.count}`, "requirement groups finished", "groups"));
}

function renderGroup(group, key) {
  const head = el("div", { class: "req-group-head" },
    el("h3", {}, group.label),
    el("span", { class: "pill" }, ruleText(group)));
  const progress = groupProgress(group, key);
  if (progress) head.append(progressPill(progress));
  const box = el("section", { class: "req-group", dataset: { group: key } }, head);
  if (group.note) box.append(el("p", { class: "req-note" }, group.note));

  const courses = group.rule === "open" ? model.openCourses.get(key) : group.courses;
  if (group.rule === "open") {
    if (courses === null) {
      box.append(el("p", { class: "req-note" }, "Could not load matching courses right now."));
      return box;
    }
    box.append(el("p", { class: "req-note" }, courses.length
      ? `${plural(courses.length, "matching course")} with ${CONFIG.termName} sections in our data:`
      : `No matching courses have ${CONFIG.termName} sections in our data yet.`));
  }
  box.append(el("div", { class: "course-list" }, courses.map((course) =>
    courseCard(course, course.course_id ? (model.sectionsByCourse.get(course.course_id) || []) : [], { takenToggle: true }))));
  return box;
}

function render() {
  const { major, tree } = model;
  title.textContent = majorLabel(major);
  sub.textContent = `Everything the ${major.catalog_year || CONFIG.catalogYear} catalog lists for this major, with the ${CONFIG.termName} sections under each class.`;
  changeButton.hidden = false;

  const content = [summaryCard()];
  tree.sections.forEach((section, si) => {
    const head = el("div", { class: "req-section-head" }, el("h2", {}, section.name));
    if (section.pool_units) {
      const p = sectionPool(section);
      head.append(el("div", { class: "stack", dataset: { pool: si } }, progressPill(p), meter(p.ratio)));
    }
    content.push(el("section", { class: "req-section", "aria-label": section.name }, head,
      section.groups.map((group, gi) => renderGroup(group, groupKey(si, gi)))));
  });
  clear(root).append(...content);
  refresh();
}

// Updates progress and course states in place, so open cards and focus stay put.
function refresh() {
  if (!model) return;
  const t = totals();
  const set = (name, text) => { const n = root.querySelector(`[data-stat="${name}"]`); if (n) n.textContent = text; };
  set("need", `≈ ${t.need}`);
  set("done", String(t.done));
  set("groups", `${t.finished} of ${t.count}`);

  model.tree.sections.forEach((section, si) => {
    if (section.pool_units) {
      const holder = root.querySelector(`[data-pool="${si}"]`);
      if (holder) clear(holder).append(progressPill(sectionPool(section)), meter(sectionPool(section).ratio));
    }
    section.groups.forEach((group, gi) => {
      const p = groupProgress(group, groupKey(si, gi));
      const old = root.querySelector(`[data-group="${groupKey(si, gi)}"] [data-progress]`);
      if (p && old) old.replaceWith(progressPill(p));
    });
  });

  for (const card of $$(".course[data-code]", root)) {
    const code = card.dataset.code;
    const taken = isCompleted(code);
    const planned = plannedCodes.has(code);
    card.classList.toggle("is-taken", taken);
    card.classList.toggle("is-planned", planned && !taken);
    const state = card.querySelector(".pill-state");
    state.hidden = !taken && !planned;
    state.textContent = taken ? "Taken" : planned ? "In your plan" : "";
    const box = card.querySelector(".taken input");
    if (box) box.checked = taken;
    if (taken && card.setOpen) card.setOpen(false);
  }
}

// ---------- loading ----------

let loading = 0;

async function load(majorId) {
  const mine = ++loading;
  model = null;
  clear(root).append(loadingBox("Loading your major's requirements…", 6));
  try {
    const tree = await getRequirements(majorId);
    const openGroups = [];
    tree.sections.forEach((section, si) => section.groups.forEach((group, gi) => {
      if (group.rule === "open" && group.open) openGroups.push([groupKey(si, gi), group.open]);
    }));
    const openCourses = new Map();
    await Promise.all(openGroups.map(async ([key, rule]) => {
      try {
        openCourses.set(key, (await findCourses({ subjects: rule.subjects, min: rule.min, max: rule.max })).courses);
      } catch (e) {
        openCourses.set(key, null);
      }
    }));
    const courseIds = [
      ...tree.sections.flatMap((s) => s.groups.flatMap((g) => g.courses)),
      ...[...openCourses.values()].flatMap((list) => list || []),
    ].filter((c) => c.has_sections && c.course_id).map((c) => c.course_id);
    const sectionsByCourse = await sectionsForCourses(courseIds);
    if (mine !== loading) return;
    model = { majorId, major: tree.major, tree, sectionsByCourse, openCourses };
    render();
  } catch (e) {
    if (mine !== loading) return;
    clear(root).append(errorBox(e.message, () => load(majorId)));
  }
}

function showPickPrompt() {
  title.textContent = "My Major";
  changeButton.hidden = true;
  clear(root).append(emptyBox(
    "What's your major?",
    `Pick it and you'll see every class it requires, with the ${CONFIG.termName} sections under each one.`,
    el("button", { type: "button", class: "btn btn-primary", on: { click: openMajorPrompt } }, "Choose your major")));
  openMajorPrompt();
}

// ---------- start ----------

let currentMajor = getState().majorId;

watchPlan((sections) => {
  plannedCodes = new Set(sections.map((s) => s.code));
  refresh();
});

subscribe((state) => {
  if (state.majorId !== currentMajor) {
    const hadPlan = state.plans.some((p) => p.sectionIds.length);
    const hadMajor = Boolean(currentMajor);
    currentMajor = state.majorId;
    clear(notice);
    if (hadMajor && hadPlan) {
      notice.append(el("p", { class: "notice", role: "status" },
        "Major changed. Your plans were kept, so classes you added for the old major are still in them. ",
        el("a", { href: "schedule.html" }, "Review them on My Schedule")));
    }
    if (currentMajor) load(currentMajor); else showPickPrompt();
  } else {
    refresh();
  }
});

// ?major= names a major that's coming soon or doesn't exist: say so and offer
// the picker, instead of quietly showing the major picked last time.
function showUnavailable(major) {
  title.textContent = "My Major";
  changeButton.hidden = true;
  clear(root).append(emptyBox(
    "That major isn't available yet",
    major ? `${majorLabel(major)} is coming soon. Pick another major to see its classes.`
      : "We couldn't find that major. Pick yours from the list.",
    el("button", { type: "button", class: "btn btn-primary", on: { click: openMajorPrompt } }, "Choose your major")));
  openMajorPrompt();
}

async function start() {
  // ?major=cs_bs picks that major (only a live one from the list)
  const wanted = new URLSearchParams(location.search).get("major");
  if (wanted && wanted !== currentMajor) {
    try {
      const majors = await getMajors();
      const major = majors.find((m) => m.major_id === wanted);
      if (major?.status === "live") { setMajor(major.major_id); return; }   // the subscription loads it
      showUnavailable(major);
      return;
    } catch (e) { /* fall through to the stored major */ }
  }
  if (currentMajor) load(currentMajor); else showPickPrompt();
}
start();

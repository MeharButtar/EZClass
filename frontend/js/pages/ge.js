// GE Scheduler: one named block per GE area (14 of them, from ge_areas.csv),
// grouped the same way as the catalog. The strip at the top jumps to a block;
// areas with sub-areas (Area 1, 3, 5, Explorations) open a small menu first.
// An area is "covered by your major" when a course from the student's major
// that counts for it is in the active plan or marked as taken. Covered blocks
// start closed but can still be opened. Adding a section here adds it to the
// same active plan as everywhere else.

import "../nav.js";
import { getGeAreas, getRequirements, searchSections } from "../api.js";
import { CONFIG } from "../config.js";
import { mountDock } from "../dock.js";
import { watchPlan } from "../plan.js";
import { courseCard } from "../sections.js";
import { getState, isCompleted, subscribe } from "../store.js";
import { $, $$, announce, clear, el, emptyBox, errorBox, loadingBox, plural, signal } from "../ui.js";

const root = $("#ge-root");
const strip = $("#area-strip");
const countLine = $("#ge-count");
const daySelect = $("#ge-day");
const tagBoxes = { cd: $("#ge-cd"), es: $("#ge-es"), ai: $("#ge-ai") };
const profInput = $("#ge-professor");
const keywordInput = $("#ge-keyword");
$("#ge-sub").textContent = `Every General Education class with ${CONFIG.termName} sections, one block per GE area. Areas your major already covers are marked.`;

mountDock($("#dock"));

const blockId = (code) => `area-${code.replace(/[^A-Za-z0-9]/g, "-")}`;

let areas = [];              // [{ area_code, name, grp, section_count }]
let allSections = [];        // every GE section
let majorCourses = [];       // [{ code, ge_areas }] from the student's major, if any
let plannedSections = [];
const blocks = new Map();    // area code -> { box, body, head parts, open, covered }

// ---------- filtering ----------

// Professor and keyword work like the server's search: a case-insensitive
// "contains" on the professor's name, and on the course title or number.
function passes(s) {
  const day = daySelect.value;
  if (day && !s.dayList.includes(day)) return false;
  const prof = profInput.value.trim().toLowerCase();
  if (prof && !s.instructors.some((p) => p.name.toLowerCase().includes(prof))) return false;
  const q = keywordInput.value.trim().toLowerCase();
  if (q && !s.title.toLowerCase().includes(q) && !s.catalog.toLowerCase().includes(q)) return false;
  if (tagBoxes.cd.checked && !s.cd) return false;
  if (tagBoxes.es.checked && !s.es) return false;
  if (tagBoxes.ai.checked && !s.ai) return false;
  return true;
}

// Sections that count for one area, grouped by course.
function coursesFor(code) {
  const byCourse = new Map();
  for (const s of allSections) {
    if (!s.geAreas.includes(code) || !passes(s)) continue;
    if (!byCourse.has(s.code)) byCourse.set(s.code, []);
    byCourse.get(s.code).push(s);
  }
  return [...byCourse.values()];
}

// ---------- coverage ----------

function coverage(code) {
  const planned = new Set(plannedSections.map((s) => s.code));
  const byMajor = majorCourses
    .filter((c) => c.ge_areas.includes(code) && (planned.has(c.code) || isCompleted(c.code)))
    .map((c) => c.code);
  const majorCodes = new Set(majorCourses.map((c) => c.code));
  const inPlan = [...new Set(plannedSections.filter((s) => s.geAreas.includes(code) && !majorCodes.has(s.code)).map((s) => s.code))];
  return { byMajor: [...new Set(byMajor)], inPlan };
}

// ---------- rendering ----------

function renderStrip() {
  const groups = [];
  for (const a of areas) {
    const last = groups[groups.length - 1];
    if (last && last.grp === a.grp) last.areas.push(a); else groups.push({ grp: a.grp, areas: [a] });
  }
  clear(strip);
  for (const g of groups) {
    if (g.areas.length === 1) {
      const a = g.areas[0];
      strip.append(el("a", { class: "chip", href: `#${blockId(a.area_code)}`, dataset: { area: a.area_code } },
        `${a.area_code} ${shortName(a)}`));
      continue;
    }
    const menuId = `menu-${blockId(g.grp)}`;
    const menu = el("ul", { class: "area-menu", id: menuId, hidden: true },
      g.areas.map((a) => el("li", {}, el("a", { href: `#${blockId(a.area_code)}`, dataset: { area: a.area_code } },
        el("span", {}, `${a.area_code} ${a.name}`), el("span", { class: "muted" }, String(a.section_count))))));
    const button = el("button", { type: "button", class: "chip", "aria-expanded": "false", "aria-controls": menuId },
      g.grp.replace(/^Area (\d)\. .*/, "Area $1").replace("Explorations of Human Experience", "Explorations"),
      el("span", { class: "caret", "aria-hidden": "true" }, "▾"));
    button.addEventListener("click", () => {
      const open = menu.hidden;
      closeMenus();
      menu.hidden = !open;
      button.setAttribute("aria-expanded", String(open));
      if (open) menu.querySelector("a")?.focus();
    });
    menu.addEventListener("keydown", (e) => { if (e.key === "Escape") { closeMenus(); button.focus(); } });
    strip.append(el("div", { class: "chip-wrap" }, button, menu));
  }
}

const shortName = (a) => (a.name.length > 28 ? `${a.name.slice(0, 26)}…` : a.name);

function closeMenus() {
  for (const m of $$(".area-menu", strip)) m.hidden = true;
  for (const b of $$("button[aria-expanded]", strip)) b.setAttribute("aria-expanded", "false");
}
document.addEventListener("click", (e) => { if (!strip.contains(e.target)) closeMenus(); });

// Jumping to an area opens its block and counts as a GE search for that area.
strip.addEventListener("click", (e) => {
  const link = e.target.closest("a[data-area]");
  if (!link) return;
  e.preventDefault();
  closeMenus();
  const code = link.dataset.area;
  const block = blocks.get(code);
  if (!block) return;
  setOpen(code, true);
  block.box.scrollIntoView({ behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  block.toggle.focus({ preventScroll: true });
  history.replaceState(null, "", `#${blockId(code)}`);
  signal("ge_search", { areas: code, day: daySelect.value, results: block.sectionCount });
});

function setOpen(code, open) {
  const block = blocks.get(code);
  block.open = open;
  block.body.hidden = !open;
  block.toggle.setAttribute("aria-expanded", String(open));
  if (open && !block.filled) fillBlock(code);
}

function fillBlock(code) {
  const block = blocks.get(code);
  const courses = coursesFor(code);
  clear(block.body);
  block.body.append(courses.length
    ? el("div", { class: "course-list" }, courses.map((sections) => {
        const s = sections[0];
        return courseCard({ code: s.code, title: s.courseTitle, units: s.units, ge_areas: s.geAreas }, sections);
      }))
    : emptyBox("No sections match", "Try another day or turn off a filter."));
  block.filled = true;
}

function renderBlocks() {
  clear(root);
  blocks.clear();
  for (const a of areas) {
    const bodyId = `${blockId(a.area_code)}-body`;
    const toggle = el("button", { type: "button", class: "ge-block-head", "aria-expanded": "true", "aria-controls": bodyId },
      el("h2", {}, el("span", { class: "ge-code" }, a.area_code), el("span", {}, a.name)));
    const countPill = el("span", { class: "pill" });
    const coverPill = el("span", { class: "pill pill-done", hidden: true });
    const planPill = el("span", { class: "pill pill-accent", hidden: true });
    toggle.append(countPill, coverPill, planPill);
    const body = el("div", { class: "ge-block-body", id: bodyId });
    const box = el("section", { class: "ge-block", id: blockId(a.area_code), dataset: { area: a.area_code } }, toggle, body);
    root.append(box);
    const block = { box, toggle, body, countPill, coverPill, planPill, open: true, filled: false, covered: false, sectionCount: 0 };
    blocks.set(a.area_code, block);
    toggle.addEventListener("click", () => setOpen(a.area_code, !block.open));
  }
  updateCounts();
  updateCoverage(true);
  for (const code of blocks.keys()) setOpen(code, !blocks.get(code).covered);
}

function updateCounts() {
  const ids = new Set();
  for (const [code, block] of blocks) {
    const courses = coursesFor(code);
    block.sectionCount = courses.reduce((n, list) => n + list.length, 0);
    courses.flat().forEach((s) => ids.add(s.id));
    block.countPill.textContent = `${plural(courses.length, "class", "classes")}, ${plural(block.sectionCount, "section")}`;
  }
  announce(countLine, `${plural(ids.size, "GE section")} match${ids.size === 1 ? "es" : ""} your filters.`);
  return ids.size;
}

function updateCoverage(initial = false) {
  for (const [code, block] of blocks) {
    const { byMajor, inPlan } = coverage(code);
    const covered = byMajor.length > 0;
    block.coverPill.hidden = !covered;
    block.coverPill.textContent = covered ? `✓ Covered by your major: ${byMajor.join(", ")}` : "";
    block.planPill.hidden = !inPlan.length;
    block.planPill.textContent = inPlan.length ? `In your plan: ${inPlan.join(", ")}` : "";
    block.box.classList.toggle("is-covered", covered);
    if (!initial && covered && !block.covered && block.open) setOpen(code, false);   // newly covered: fold it away
    block.covered = covered;
  }
}

let appliedFilters = "";   // the filters last applied, so Enter + change don't run (and count) twice

function applyFilters() {
  const now = JSON.stringify([daySelect.value, profInput.value.trim(), keywordInput.value.trim(),
    tagBoxes.cd.checked, tagBoxes.es.checked, tagBoxes.ai.checked]);
  if (now === appliedFilters) return;
  appliedFilters = now;
  const total = updateCounts();
  for (const [code, block] of blocks) {
    block.filled = false;
    if (block.open) fillBlock(code);
  }
  signal("ge_search", { areas: "ALL", day: daySelect.value, results: total,
                       hasProf: Boolean(profInput.value.trim()), hasKw: Boolean(keywordInput.value.trim()) });
}

// Selects and checkboxes apply right away; the professor and keyword boxes on
// Enter or when you leave the box (both fire "change").
$("#ge-filters").addEventListener("change", applyFilters);
$("#ge-filters").addEventListener("submit", (e) => e.preventDefault());
for (const input of [profInput, keywordInput]) {
  input.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); applyFilters(); } });
}
$("#ge-expand").addEventListener("click", () => { for (const code of blocks.keys()) setOpen(code, true); });
$("#ge-collapse").addEventListener("click", () => { for (const code of blocks.keys()) setOpen(code, false); });

// ---------- loading ----------

async function loadMajor(majorId) {
  majorCourses = [];
  if (!majorId) return;
  try {
    const tree = await getRequirements(majorId);
    majorCourses = tree.sections.flatMap((s) => s.groups.flatMap((g) => g.courses))
      .map((c) => ({ code: c.code, ge_areas: c.ge_areas }));
  } catch (e) { /* coverage just won't show */ }
}

async function load() {
  clear(root).append(loadingBox("Loading GE classes…", 6));
  try {
    const [areaData, sections] = await Promise.all([getGeAreas(), searchSections({ ge: "ALL" }), loadMajor(getState().majorId)]);
    areas = areaData.areas;
    allSections = sections;
    renderStrip();
    renderBlocks();
    // arriving with #area-5C opens and shows that block
    const target = [...blocks.entries()].find(([code]) => `#${blockId(code)}` === location.hash);
    if (target) { setOpen(target[0], true); target[1].box.scrollIntoView(); }
  } catch (e) {
    clear(root).append(errorBox(e.message, load));
  }
}

let majorId = getState().majorId;
watchPlan((sections) => { plannedSections = sections; if (blocks.size) updateCoverage(); });
subscribe(async (state) => {
  if (state.majorId !== majorId) { majorId = state.majorId; await loadMajor(majorId); }
  if (blocks.size) updateCoverage();
});
load();

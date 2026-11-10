// My Schedule: plan tabs (A, B, C), the full-size week, a stats strip, the
// server conflict check with a plain explanation, and the list of classes
// with remove buttons. The conflict check runs by itself whenever the plan
// changes; "Check again" asks the server again.

import { reportLink } from "../nav.js";
import { cachedSection, checkConflicts, showDataDate } from "../api.js";
import { mountCalendar } from "../calendar.js";
import { CONFIG } from "../config.js";
import { watchPlan } from "../plan.js";
import { ratingControls } from "../ratings.js";
import { sectionLabel } from "../sections.js";
import { formatDuration, repeatedCourses, weekStats } from "../stats.js";
import {
  MAX_PLANS, canUndo, clearPlan, createPlan, deletePlan, duplicatePlan, getState, removeSection,
  renamePlan, subscribe, switchPlan, undo,
} from "../store.js";
import { DAY_SHORT, describeOverlap } from "../time.js";
import {
  $, announce, clear, confirmDialog, el, emptyBox, instructorLinks, meetingLines, plural, promptDialog, seatsLabel, signal,
} from "../ui.js";

const tabs = $("#plan-tabs");
const actions = $("#plan-actions");
const panel = $("#plan-panel");
const result = $("#conflict-result");
const checkButton = $("#check-btn");
const newPlan = $("#new-plan");
newPlan.addEventListener("click", createPlan);
$("#schedule-sub").textContent = `Your ${CONFIG.termName} week. Keep up to three plans; everything you add on My Major, GE or Search goes into the plan that's open here.`;

// Before you register: our copy of the schedule can be out of date.
const registerNote = $("#register-note");
const noteDate = el("span");
const noteReport = reportLink("Tell us", { kind: "wrong_info" });
registerNote.append(...[
  el("strong", {}, "Before you register: "),
  `confirm every class in ${CONFIG.registrationSite}. Times, rooms and professors can change.`,
  noteDate,
  noteReport && " Something wrong here? ", noteReport, noteReport && ".",
].filter(Boolean));
showDataDate(noteDate, " ");

const calendar = mountCalendar($("#week"), { variant: "full", emptyText: "No classes in this plan yet." });

// ---------- plan tabs ----------

function renderTabs(state) {
  clear(tabs);
  state.plans.forEach((plan, i) => {
    const selected = i === state.activePlan;
    const tab = el("button", {
      type: "button", role: "tab", class: "chip plan-tab", id: `plan-tab-${i}`,
      "aria-selected": String(selected), tabindex: selected ? "0" : "-1", "aria-controls": "plan-panel",
      on: { click: () => switchPlan(i) },
    }, plan.name, el("span", { class: "count" }, String(plan.sectionIds.length)));
    tabs.append(tab);
  });
  const full = state.plans.length >= MAX_PLANS;
  newPlan.disabled = full;
  newPlan.title = full ? `You can keep up to ${MAX_PLANS} plans` : "";
  panel.setAttribute("aria-labelledby", `plan-tab-${state.activePlan}`);
}

// arrow keys move between tabs
tabs.addEventListener("keydown", (e) => {
  const list = [...tabs.querySelectorAll("[role=tab]")];
  const i = list.indexOf(document.activeElement);
  if (i < 0 || !["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) return;
  e.preventDefault();
  const next = e.key === "Home" ? 0 : e.key === "End" ? list.length - 1 : (i + (e.key === "ArrowRight" ? 1 : -1) + list.length) % list.length;
  switchPlan(next);
  requestAnimationFrame(() => document.getElementById(`plan-tab-${next}`)?.focus());
});

function renderActions(state) {
  const plan = state.plans[state.activePlan];
  const i = state.activePlan;
  clear(actions).append(
    el("button", { type: "button", class: "btn btn-sm", on: { click: async () => {
      const name = await promptDialog("Rename plan", "Plan name", plan.name);
      if (name) renamePlan(i, name);
    } } }, "Rename"),
    el("button", { type: "button", class: "btn btn-sm", disabled: state.plans.length >= MAX_PLANS, on: { click: () => duplicatePlan(i) } }, "Duplicate"),
    el("button", { type: "button", class: "btn btn-sm", disabled: !plan.sectionIds.length, on: { click: clearPlan } }, "Clear"),
    el("button", { type: "button", class: "btn btn-sm btn-danger", on: { click: async () => {
      const last = state.plans.length === 1;
      const ok = await confirmDialog(last ? `Empty ${plan.name}?` : `Delete ${plan.name}?`,
        last ? "This is your only plan, so its classes are removed and the plan stays." : "You can undo this right after.",
        last ? "Empty it" : "Delete");
      if (ok) deletePlan(i);
    } } }, state.plans.length === 1 ? "Empty plan" : "Delete"),
    el("button", { type: "button", class: "btn btn-sm btn-ghost", disabled: !canUndo(), on: { click: undo } }, "Undo"));
}

// ---------- stats, list, conflicts ----------

function renderStats(sections) {
  const s = weekStats(sections);
  const cell = (num, label, ...more) => el("div", {},
    el("div", { class: "stat-num" }, num), el("div", { class: "stat-label" }, label), ...more);
  const names = (days) => days.map((d) => DAY_SHORT[d]).join(", ");
  const campus = s.campusDays.length;
  clear($("#stats")).append(
    cell(String(s.units), "units"),
    cell(formatDuration(Math.round(s.hoursInClass * 60)), "in class per week"),
    // live online classes (room "Online") are class time, but not a trip to campus
    cell(String(campus), `${campus === 1 ? "day" : "days"} on campus${campus ? ` (${names(s.campusDays)})` : ""}`,
      s.onlineOnlyDays.length ? el("div", { class: "stat-label stat-extra" }, `Online only: ${names(s.onlineOnlyDays)}`) : null),
    cell(formatDuration(s.longestGap), "longest gap in a day"));
}

// More than one section of a course: the calendar itself says so (calendar.js);
// here the stats get a note that hours count every section and units don't.
function renderRepeats(sections) {
  $("#stats-note").hidden = repeatedCourses(sections).length === 0;
}

function renderList(sections, state) {
  const box = $("#plan-list");
  const plan = state.plans[state.activePlan];
  $("#list-title").textContent = `Classes in ${plan.name}`;
  if (!sections.length) {
    clear(box).append(emptyBox("Nothing here yet", "Add classes from your major or the GE list.",
      el("a", { class: "btn btn-primary btn-sm", href: "major.html" }, "My Major"),
      el("a", { class: "btn btn-sm", href: "ge.html" }, "GE classes")));
    return;
  }
  clear(box).append(el("ul", { class: "plan-list" }, sections.map((s) => el("li", { class: "plan-item" },
    el("div", {},
      el("strong", {}, `${s.code} · Sec ${s.sectionNumber}`),
      el("div", { class: "small" }, s.title),
      meetingLines(s),
      el("div", { class: "muted small" }, instructorLinks(s), ` · ${seatsLabel(s)}`),
      ratingControls(s)),
    el("button", {
      type: "button", class: "btn btn-sm btn-danger", "aria-label": `Remove ${sectionLabel(s)} from ${plan.name}`,
      on: { click: () => removeSection(s.id, sectionLabel(s)) },
    }, "Remove")))));
}

let checkSeq = 0;
let currentIds = [];

async function runCheck() {
  const ids = currentIds;
  result.className = "conflict-box";
  checkButton.disabled = ids.length < 2;
  if (ids.length < 2) {
    announce(result, ids.length ? "Add at least one more class to check for overlaps." : "Add classes to check for overlaps.");
    return;
  }
  const mine = ++checkSeq;
  announce(result, "Checking…");
  try {
    const data = await checkConflicts(ids);
    if (mine !== checkSeq) return;
    signal("conflict_check", { conflictFree: data.conflict_free, cartSize: ids.length });
    if (data.conflict_free) {
      result.className = "conflict-box ok";
      announce(result, `✓ No overlaps. All ${ids.length} classes fit.`);
      return;
    }
    result.className = "conflict-box bad";
    clear(result).append(
      el("strong", {}, `${plural(data.conflicts.length, "overlap")} found:`),
      el("ul", {}, data.conflicts.map((c) => {
        const a = cachedSection(c.section_a.section_id);
        const b = cachedSection(c.section_b.section_id);
        if (!a || !b) return el("li", {}, `Sections ${c.section_a.section_id} and ${c.section_b.section_id} overlap.`);
        return el("li", {}, `${sectionLabel(a)} and ${sectionLabel(b)} are both on ${describeOverlap(a, b)}.`);
      })),
      el("p", { class: "small" }, "Swap one of them for another section, or try it in a different plan."));
  } catch (e) {
    if (mine !== checkSeq) return;
    result.className = "conflict-box bad";
    announce(result, `Could not run the check: ${e.message}`);
  }
}
checkButton.addEventListener("click", runCheck);

// ---------- wiring ----------

subscribe((state) => { renderTabs(state); renderActions(state); });
renderTabs(getState());
renderActions(getState());

watchPlan((sections, state, error) => {
  calendar.update(sections);
  renderStats(sections);
  renderRepeats(sections);
  renderList(sections, state);
  if (error) {
    result.className = "conflict-box bad";
    announce(result, `Could not load this plan's classes: ${error.message}`);
    return;
  }
  const ids = sections.map((s) => s.id);
  if (ids.join() !== currentIds.join()) {
    currentIds = ids;
    runCheck();
  }
});

// Search: subject, day, professor and keyword ("CS 480", "cs4", "data science").
// The matching happens on the server (backend/search.py). Results are section
// rows (with the hover ghost on the docked calendar), drawn 40 at a time so a
// search for everything stays fast.
// Typing searches by itself after a short pause; only Enter, the Search button
// and the dropdowns report to tracking, and only whether the professor or
// keyword box was used, never what was typed.

import "../nav.js";
import { getSubjects, searchSections } from "../api.js";
import { CONFIG } from "../config.js";
import { mountDock } from "../dock.js";
import { onlineHeading, sectionRow, timedFirst } from "../sections.js";
import { $, announce, clear, el, emptyBox, errorBox, loadingBox, plural, signal } from "../ui.js";

const CHUNK = 40;
const TYPING_PAUSE = 250;   // ms after the last key before searching
const form = $("#search-form");
const root = $("#search-root");
const countLine = $("#search-count");
const fields = { subject: $("#f-subject"), day: $("#f-day"), professor: $("#f-professor"), q: $("#f-keyword") };
$("#search-sub").textContent = `Every ${CONFIG.termName} class, by subject, day, professor or keyword.`;

mountDock($("#dock"));

async function loadSubjects() {
  try {
    for (const subject of await getSubjects()) fields.subject.append(el("option", { value: subject }, subject));
  } catch (e) { /* the search still works without the list */ }
}

function emptyMessage(params) {
  const tips = [];
  if (params.q) tips.push("Try just the number (480), just the subject (CS), or part of the title.");
  if (params.professor) tips.push("Try just the professor's last name.");
  if (!tips.length) tips.push("Try fewer filters.");
  return emptyBox(params.q ? "No classes match that." : "No classes match", tips.join(" "));
}

function renderResults(found, params) {
  clear(root);
  const sections = timedFirst(found);
  const online = sections.filter((s) => s.untimed).length;
  if (!sections.length) {
    root.append(emptyMessage(params));
    return;
  }
  const list = el("ul", { class: "sec-list" });
  const more = el("button", { type: "button", class: "btn btn-block" });
  let shown = 0;
  const showMore = () => {
    for (const s of sections.slice(shown, shown + CHUNK)) {
      if (s.untimed && !list.querySelector(".sec-group")) list.append(onlineHeading(online));
      list.append(sectionRow(s, { showCourse: true }));
    }
    shown = Math.min(shown + CHUNK, sections.length);
    more.hidden = shown >= sections.length;
    more.textContent = `Show ${Math.min(CHUNK, sections.length - shown)} more of ${sections.length - shown}`;
  };
  more.addEventListener("click", showMore);
  root.append(list, more);
  showMore();
}

let seq = 0;

async function search({ report = true } = {}) {
  const params = Object.fromEntries(Object.entries(fields).map(([k, input]) => [k, input.value.trim()]));
  const mine = ++seq;
  if (params.q.replace(/[^\p{L}\p{N}]/gu, "").length === 1) {   // one letter or digit: wait for more
    clear(root).append(emptyBox("Keep typing", "At least 2 characters."));
    announce(countLine, "Keep typing, at least 2 characters.");
    return;
  }
  clear(root).append(loadingBox("Searching…", 4));
  announce(countLine, "Searching…");
  try {
    const sections = await searchSections(params);
    if (mine !== seq) return;   // a newer search started
    renderResults(sections, params);
    announce(countLine, `${plural(sections.length, "section")} found.`);
    if (report) {
      signal("search", { subject: params.subject, day: params.day, hasProf: Boolean(params.professor),
                         hasKw: Boolean(params.q), results: sections.length });
    }
  } catch (e) {
    if (mine !== seq) return;
    clear(root).append(errorBox(e.message, () => search({ report })));
    announce(countLine, "");
  }
}

let typingTimer = 0;
form.addEventListener("submit", (e) => { e.preventDefault(); clearTimeout(typingTimer); search(); });
// search as you type (not reported; the seq guard drops answers that arrive late)
for (const input of [fields.q, fields.professor]) {
  input.addEventListener("input", () => {
    clearTimeout(typingTimer);
    typingTimer = setTimeout(() => search({ report: false }), TYPING_PAUSE);
  });
}
form.addEventListener("reset", () => setTimeout(() => search({ report: false }), 0));
fields.subject.addEventListener("change", () => search());
fields.day.addEventListener("change", () => search());

loadSubjects();
search({ report: false });

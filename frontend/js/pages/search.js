// Search: subject, day, professor and keyword ("CS 480", "cs4", "data science").
// The matching happens on the server (backend/search.py). Results are section
// rows (with the hover ghost on the docked calendar), drawn 40 at a time so a
// big search stays fast. With no filter at all nothing is loaded (the whole
// term is 5,000+ sections); the page asks for a subject, day or keyword first.
// A class number ("5834") puts that section on top under its own heading.
// Typing searches by itself after a short pause; only Enter, the Search button
// and the dropdowns report to tracking, and only whether the professor or
// keyword box was used, never what was typed.
// The filters live in the address (search.html?q=cs%20480&day=M), so a refresh,
// the Back button and a shared link all bring the same search back.

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
$("#search-sub").textContent = `Every ${CONFIG.termName} class, by subject, day, professor, keyword or class number.`;

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

// "5834" or "#5834": a class number, the number students register with
const classNumberIn = (q) => (/^#?\s*(\d{4,5})$/.exec(q.trim()) || [])[1] || "";

function renderResults(found, params) {
  clear(root);
  // a class number search: that section on top under its own heading, then the rest of the course
  const wanted = classNumberIn(params.q);
  const hit = wanted ? found.find((s) => s.classNumber === wanted) : null;
  const sections = timedFirst(hit ? found.filter((s) => s !== hit) : found);
  const online = sections.filter((s) => s.untimed).length;
  if (!sections.length && !hit) {
    root.append(emptyMessage(params));
    return;
  }
  const list = el("ul", { class: "sec-list" });
  if (hit) {
    list.append(el("li", { class: "sec-group" }, `Class # ${hit.classNumber}`), sectionRow(hit, { showCourse: true }));
    if (sections.length) list.append(el("li", { class: "sec-group" }, `Other sections of ${hit.code}`));
  }
  const more = el("button", { type: "button", class: "btn btn-block" });
  let shown = 0;
  const showMore = () => {
    for (const s of sections.slice(shown, shown + CHUNK)) {
      if (s.untimed && !list.querySelector(".sec-group.is-online")) list.append(onlineHeading(online));
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

// the address follows the filters (replaceState: typing doesn't fill the Back history)
function rememberInUrl(params) {
  try {
    const query = new URLSearchParams(Object.entries(params).filter(([, v]) => v)).toString();
    history.replaceState(null, "", query ? `?${query}` : location.pathname);
  } catch (e) { /* the search still works */ }
}

async function search({ report = true } = {}) {
  const params = Object.fromEntries(Object.entries(fields).map(([k, input]) => [k, input.value.trim()]));
  const mine = ++seq;
  rememberInUrl(params);
  if (params.q.replace(/[^\p{L}\p{N}]/gu, "").length === 1) {   // one letter or digit: wait for more
    clear(root).append(emptyBox("Keep typing", "At least 2 characters."));
    announce(countLine, "Keep typing, at least 2 characters.");
    return;
  }
  // nothing to search by: ask for a filter instead of loading every class (5,000+ sections)
  const typed = (text) => /[\p{L}\p{N}]/u.test(text);
  if (!params.subject && !params.day && !typed(params.q) && !typed(params.professor)) {
    clear(root).append(emptyBox("Search for a class",
      "Pick a subject or a day, or type a course (CS 150), a title, a professor or a class number (5834)."));
    announce(countLine, "");
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

// filters from the address (a shared link, a refresh, /search?q=...); a value a
// dropdown doesn't have is ignored. The first search waits for the subject list.
const fromUrl = new URLSearchParams(location.search);
fields.q.value = (fromUrl.get("q") || "").slice(0, 100);
fields.professor.value = (fromUrl.get("professor") || "").slice(0, 100);
const pick = (select, value) => { if ([...select.options].some((o) => o.value === value)) select.value = value; };
pick(fields.day, fromUrl.get("day") || "");

loadSubjects().finally(() => {
  pick(fields.subject, (fromUrl.get("subject") || "").replace(/[^A-Za-z0-9]/g, "").toUpperCase());
  search({ report: false });
});

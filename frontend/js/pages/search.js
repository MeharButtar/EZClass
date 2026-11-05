// Search: the subject / day / professor / keyword search from v1, restyled.
// Results are section rows (with the hover ghost on the docked calendar) and
// are drawn 40 at a time so a search for everything stays fast.
// Only whether the professor or keyword box was used is reported to
// tracking, never what was typed.

import "../nav.js";
import { getSubjects, searchSections } from "../api.js";
import { CONFIG } from "../config.js";
import { mountDock } from "../dock.js";
import { onlineHeading, sectionRow, timedFirst } from "../sections.js";
import { $, announce, clear, el, emptyBox, errorBox, loadingBox, plural, signal } from "../ui.js";

const CHUNK = 40;
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

function renderResults(found) {
  clear(root);
  const sections = timedFirst(found);
  const online = sections.filter((s) => s.untimed).length;
  if (!sections.length) {
    root.append(emptyBox("No classes match", "Try fewer filters, or a different spelling of the professor's name."));
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
  clear(root).append(loadingBox("Searching…", 4));
  announce(countLine, "Searching…");
  try {
    const sections = await searchSections(params);
    if (mine !== seq) return;   // a newer search started
    renderResults(sections);
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

form.addEventListener("submit", (e) => { e.preventDefault(); search(); });
form.addEventListener("reset", () => setTimeout(() => search({ report: false }), 0));
fields.subject.addEventListener("change", () => search());
fields.day.addEventListener("change", () => search());

loadSubjects();
search({ report: false });

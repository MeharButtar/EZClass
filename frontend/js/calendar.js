// The week grid. Docked beside the lists on My Major, GE and Search, and full
// size on My Schedule. It draws the sections of the active plan, plus a dashed
// "ghost" for whatever section the student is pointing at in a list, so they
// see where it lands before adding it. Classes that overlap sit side by side in
// lanes and are striped red; a ghost that would overlap turns red and says so.
// Sections without a set day and time are listed under the grid instead.

import { CONFIG } from "./config.js";
import { removeSection } from "./store.js";
import { DAYS, DAY_NAMES, DAY_SHORT, formatRange, formatTime, isTimed, overlaps } from "./time.js";
import { clear, dayStrip, el, openDialog } from "./ui.js";

const COLORS = 8;   // --sub-0 ... --sub-7 in base.css

// Subjects get colors in the order they first appear in the plan, so two
// subjects in one plan never share a color (up to eight). Every page draws the
// same plan, so a subject's color is the same everywhere. A ghost from a new
// subject gets the next free color.
function colorIndex(subject, order) {
  const i = order.indexOf(subject);
  return (i < 0 ? order.length : i) % COLORS;
}

// Splits one day's blocks into side-by-side lanes where they overlap.
function layoutDay(blocks) {
  const sorted = [...blocks].sort((a, b) => a.startMin - b.startMin || b.endMin - a.endMin);
  const out = [];
  let cluster = [];
  let clusterEnd = -1;
  const flush = () => {
    const lanes = [];
    for (const b of cluster) {
      let lane = lanes.findIndex((end) => end <= b.startMin);
      if (lane === -1) { lane = lanes.length; lanes.push(0); }
      lanes[lane] = b.endMin;
      out.push({ s: b, lane });
    }
    for (const p of out.slice(-cluster.length)) p.lanes = lanes.length;
    cluster = [];
  };
  for (const b of sorted) {
    if (cluster.length && b.startMin >= clusterEnd) flush();
    cluster.push(b);
    clusterEnd = Math.max(clusterEnd, b.endMin);
  }
  if (cluster.length) flush();
  return out;
}

// ---------- the ghost is shared by every calendar on the page ----------

const calendars = new Set();
let ghost = null;

export function setGhost(section) {
  if (ghost === section || (ghost && section && ghost.id === section.id)) return;
  ghost = section;
  for (const cal of calendars) cal.render();
}

// ---------- the small card that opens when a block is clicked ----------

export function showSectionCard(section) {
  const dialog = openDialog({
    title: `${section.code}, section ${section.sectionNumber}`,
    className: "dialog-small",
    content: [
      section.title ? el("p", { class: "muted" }, section.title) : null,
      el("dl", { class: "facts" },
        el("dt", {}, "Days"), el("dd", {}, dayStrip(section.dayList)),
        el("dt", {}, "Time"), el("dd", {}, formatRange(section.startMin, section.endMin) || "No set time"),
        el("dt", {}, "Room"), el("dd", {}, section.room || "TBA"),
        el("dt", {}, "Professor"), el("dd", {}, section.professor || "TBA"),
        el("dt", {}, "Units"), el("dd", {}, String(section.units || "–"))),
      el("div", { class: "dialog-actions" },
        el("button", { type: "button", class: "btn", on: { click: () => dialog.close() } }, "Close"),
        el("button", {
          type: "button", class: "btn btn-danger",
          on: { click: () => { removeSection(section.id, `${section.code} (Sec ${section.sectionNumber})`); dialog.close(); } },
        }, "Remove from plan")),
    ],
  });
}

// ---------- one calendar ----------

// variant: "dock" (beside the lists) or "full" (My Schedule).
export function mountCalendar(container, { variant = "dock", emptyText = "", onSelect = showSectionCard } = {}) {
  let sections = [];
  const root = el("div", { class: `cal cal-${variant}` });
  container.append(root);

  function render() {
    const timed = sections.filter(isTimed);
    const order = [...new Set(sections.map((s) => s.subject))];
    const ghostTimed = ghost && isTimed(ghost) && !sections.some((s) => s.id === ghost.id) ? ghost : null;
    const all = ghostTimed ? [...timed, ghostTimed] : timed;

    let first = Math.min(CONFIG.calendarStartHour * 60, ...all.map((s) => s.startMin));
    let last = Math.max(CONFIG.calendarEndHour * 60, ...all.map((s) => s.endMin));
    first = Math.floor(first / 60) * 60;
    last = Math.ceil(last / 60) * 60;
    const span = last - first;
    const pct = (m) => `${((m - first) / span) * 100}%`;
    const height = (a, b) => `${((b - a) / span) * 100}%`;

    const head = el("div", { class: "cal-head", "aria-hidden": "true" },
      el("span", {}),
      DAYS.map((d) => el("span", { class: "cal-dayhead" },
        el("span", { class: "long" }, DAY_SHORT[d]), el("span", { class: "short" }, d))));

    const gutter = el("div", { class: "cal-gutter", "aria-hidden": "true" });
    for (let m = first + 60; m < last; m += 60) gutter.append(el("span", { style: { top: pct(m) } }, formatTime(m)));

    const cols = DAYS.map((d) => {
      const today = timed.filter((s) => s.dayList.includes(d));
      const col = el("div", { class: "cal-col", role: "group", "aria-label": DAY_NAMES[d] });
      for (const { s, lane, lanes } of layoutDay(today)) {
        const clash = today.some((o) => overlaps(s, o));
        const width = 100 / lanes;
        const time = formatRange(s.startMin, s.endMin);
        col.append(el("button", {
          type: "button",
          class: `cal-blk sub-${colorIndex(s.subject, order)}${clash ? " clash" : ""}`,
          style: { top: pct(s.startMin), height: height(s.startMin, s.endMin), left: `${lane * width}%`, width: `${width}%` },
          "aria-label": `${s.code} section ${s.sectionNumber}, ${DAY_NAMES[d]} ${time}${s.room ? `, ${s.room}` : ""}${clash ? ", overlaps another class" : ""}. Details`,
          dataset: { sectionId: s.id },
          on: { click: () => onSelect(s) },
        },
        el("span", { class: "blk-code" }, s.code),
        el("span", { class: "blk-time" }, time),
        s.room ? el("span", { class: "blk-room" }, s.room) : null));
      }
      if (ghostTimed && ghostTimed.dayList.includes(d)) {
        const clash = today.some((o) => overlaps(ghostTimed, o));
        col.append(el("div", {
          class: `cal-ghost sub-${colorIndex(ghostTimed.subject, order)}${clash ? " clash" : ""}`,
          style: { top: pct(ghostTimed.startMin), height: height(ghostTimed.startMin, ghostTimed.endMin) },
          "aria-hidden": "true",
        },
        el("span", { class: "blk-code" }, ghostTimed.code),
        el("span", { class: "blk-time" }, clash ? "Overlaps" : formatRange(ghostTimed.startMin, ghostTimed.endMin))));
      }
      return col;
    });

    const body = el("div", { class: "cal-body" }, gutter, cols);
    body.style.setProperty("--hours", String(span / 60));
    if (!sections.length && !ghostTimed && emptyText) body.append(el("p", { class: "cal-empty" }, emptyText));

    const notes = el("div", { class: "cal-notes" });
    if (timed.some((a) => timed.some((b) => overlaps(a, b)))) {
      notes.append(el("p", { class: "cal-key" }, el("span", { class: "key-swatch", "aria-hidden": "true" }),
        "Striped red classes overlap another class in this plan."));
    }
    const untimed = sections.filter((s) => !isTimed(s));
    if (untimed.length) {
      notes.append(el("p", { class: "cal-key" },
        `Not on the grid (online or no set meeting time): ${untimed.map((s) => s.code).join(", ")}`));
    }
    if (ghost && !isTimed(ghost)) {
      notes.append(el("p", { class: "cal-key" }, `${ghost.code} has no set meeting time, so it won't show on the grid.`));
    }

    clear(root).append(head, body, notes);
  }

  const controller = {
    render,
    update(list) { sections = list; render(); },
    destroy() { calendars.delete(controller); root.remove(); },
  };
  calendars.add(controller);
  render();
  return controller;
}

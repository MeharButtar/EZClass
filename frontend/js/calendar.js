// The week grid. Docked beside the lists on My Major, GE and Search, and full
// size on My Schedule. It draws the sections of the active plan, plus a dashed
// "ghost" for whatever section the student is pointing at in a list, so they
// see where it lands before adding it. Classes that overlap sit side by side in
// lanes and are striped red; a ghost that would overlap turns red and says so.
//
// A section with several meetings (lecture + lab) gets a block for each
// meeting on each day. Only timed meetings go on the grid: a hybrid section's
// blocks say "+ online part", and online-only sections (and ones whose time
// isn't listed yet) are listed under the grid ("Online or no time listed"), never
// drawn and never in a clash.
//
// A student may add more than one section of a course (backups). That's
// allowed; the calendar says so in a note under the grid, the blocks of that
// course get a "2×" badge, and pointing at another section of a course that's
// already in the plan says it would be a second one.

import { CONFIG } from "./config.js";
import { ratingControls } from "./ratings.js";
import { reportUrl } from "./nav.js";
import { getState, removeSection } from "./store.js";
import { DAY_NAMES, DAY_SHORT, formatRange, formatTime, isTimed, timedMeetings, weekColumns } from "./time.js";
import { repeatedCourses } from "./stats.js";
import { clear, el, instructorLinks, meetingLines, openDialog, seatsLabel } from "./ui.js";

const COLORS = 8;   // --sub-0 ... --sub-7 in base.css

// Subjects get colors in the order they first appear in the plan, so two
// subjects in one plan never share a color (up to eight). Every page draws the
// same plan, so a subject's color is the same everywhere. A ghost from a new
// subject gets the next free color.
function colorIndex(subject, order) {
  const i = order.indexOf(subject);
  return (i < 0 ? order.length : i) % COLORS;
}

// One block per timed meeting per day: { s, m, idx, day, startMin, endMin }.
function blocksOf(sections) {
  return sections.flatMap((s) => timedMeetings(s).flatMap((m, idx) =>
    m.dayList.map((day) => ({ s, m, idx, day, startMin: m.startMin, endMin: m.endMin }))));
}

// Blocks of two different sections that are in class at the same time.
const blocksClash = (a, b) => a.s.id !== b.s.id && a.startMin < b.endMin && b.startMin < a.endMin;

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
      out.push({ b, lane });
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
  const many = section.instructors.length > 1;
  const dialog = openDialog({
    title: `${section.code}, section ${section.sectionNumber}`,
    className: "dialog-small",
    content: [
      section.title ? el("p", { class: "muted" }, section.title) : null,
      el("dl", { class: "facts" },
        el("dt", {}, "Meets"), el("dd", {}, meetingLines(section)),
        el("dt", {}, many ? "Professors" : "Professor"), el("dd", {}, instructorLinks(section, "TBA")),
        section.instructors.length ? el("dt", {}, many ? "Your scores" : "Your score") : null,
        section.instructors.length ? el("dd", {}, ratingControls(section, { beforeOpen: () => dialog.close() })) : null,
        el("dt", {}, "Seats"), el("dd", {}, seatsLabel(section)),
        el("dt", {}, "Units"), el("dd", {}, String(section.units || "–"))),
      el("p", { class: "small" }, el("a", {
        href: reportUrl({ kind: "wrong_info", course: section.code, section: section.sectionNumber }),
      }, "Report wrong info for this class")),
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
    const order = [...new Set(sections.map((s) => s.subject))];
    const blocks = blocksOf(sections);
    const ghostOn = ghost && isTimed(ghost) && !sections.some((s) => s.id === ghost.id);
    const ghostBlocks = ghostOn ? blocksOf([ghost]) : [];
    const all = [...blocks, ...ghostBlocks];
    const days = weekColumns(all.map((b) => [b.day]));
    const repeats = repeatedCourses(sections);
    const copies = new Map(repeats.map(({ code, sections: list }) => [code, list.length]));

    let first = Math.min(CONFIG.calendarStartHour * 60, ...all.map((b) => b.startMin));
    let last = Math.max(CONFIG.calendarEndHour * 60, ...all.map((b) => b.endMin));
    first = Math.floor(first / 60) * 60;
    last = Math.ceil(last / 60) * 60;
    const span = last - first;
    const pct = (m) => `${((m - first) / span) * 100}%`;
    const height = (a, b) => `${((b - a) / span) * 100}%`;

    const head = el("div", { class: "cal-head", "aria-hidden": "true" },
      el("span", {}),
      days.map((d) => el("span", { class: "cal-dayhead" },
        el("span", { class: "long" }, DAY_SHORT[d]), el("span", { class: "short" }, d))));

    const gutter = el("div", { class: "cal-gutter", "aria-hidden": "true" });
    for (let m = first + 60; m < last; m += 60) gutter.append(el("span", { style: { top: pct(m) } }, formatTime(m)));

    const cols = days.map((d) => {
      const today = blocks.filter((b) => b.day === d);
      const col = el("div", { class: "cal-col", role: "group", "aria-label": DAY_NAMES[d] });
      for (const { b, lane, lanes } of layoutDay(today)) {
        const { s, m } = b;
        const clash = today.some((o) => blocksClash(b, o));
        const width = 100 / lanes;
        const time = formatRange(b.startMin, b.endMin);
        const n = copies.get(s.code);
        col.append(el("button", {
          type: "button",
          class: `cal-blk sub-${colorIndex(s.subject, order)}${clash ? " clash" : ""}${n ? " repeat" : ""}`,
          style: { top: pct(b.startMin), height: height(b.startMin, b.endMin), left: `${lane * width}%`, width: `${width}%` },
          // starts with the words shown on the block (Label in Name), then the rest
          "aria-label": [s.code, time, m.room, s.onlinePart ? "+ online part" : ""].filter(Boolean).join(" ")
            + `, section ${s.sectionNumber}, ${DAY_NAMES[d]}${clash ? ", overlaps another class" : ""}`
            + `${n ? `, one of ${n} sections of ${s.code} in this plan` : ""}. Details`,
          dataset: { sectionId: s.id, meeting: b.idx, ...(n ? { repeat: String(n) } : {}) },
          on: { click: () => onSelect(s) },
        },
        el("span", { class: "blk-code" }, s.code), " ",
        el("span", { class: "blk-time" }, time), " ",
        m.room ? el("span", { class: "blk-room" }, m.room) : null, " ",
        s.onlinePart ? el("span", { class: "blk-online" }, "+ online part") : null));
      }
      for (const g of ghostBlocks.filter((b) => b.day === d)) {
        const clash = today.some((o) => blocksClash(g, o));
        col.append(el("div", {
          class: `cal-ghost sub-${colorIndex(g.s.subject, order)}${clash ? " clash" : ""}`,
          style: { top: pct(g.startMin), height: height(g.startMin, g.endMin) },
          "aria-hidden": "true",
        },
        el("span", { class: "blk-code" }, g.s.code),
        el("span", { class: "blk-time" }, clash ? "Overlaps" : formatRange(g.startMin, g.endMin))));
      }
      return col;
    });

    const body = el("div", { class: "cal-body" }, gutter, cols);
    body.style.setProperty("--hours", String(span / 60));
    body.style.setProperty("--days", String(days.length));
    head.style.setProperty("--days", String(days.length));
    if (!sections.length && !ghostBlocks.length && emptyText) body.append(el("p", { class: "cal-empty" }, emptyText));

    const notes = el("div", { class: "cal-notes" });
    if (repeats.length) {
      const plan = getState().plans[getState().activePlan];
      notes.append(el("div", { class: "cal-repeat" }, repeats.map(({ code, sections: list }) => el("p", {},
        el("span", { class: "repeat-badge", "aria-hidden": "true" }, `${list.length}×`), " ",
        el("strong", {}, `${list.length} sections of ${code}`),
        ` in ${plan?.name || "this plan"} (${list.map((x) => `Sec ${x.sectionNumber}`).join(", ")}). `
          + `Pick just one when you register, unless you're keeping ${list.length === 2 ? "the other as a backup" : "the others as backups"}.`))));
    }
    if (blocks.some((a) => blocks.some((b) => a.day === b.day && blocksClash(a, b)))) {
      notes.append(el("p", { class: "cal-key" }, el("span", { class: "key-swatch", "aria-hidden": "true" }),
        "Striped red classes overlap another class in this plan."));
    }
    const untimed = sections.filter((s) => !isTimed(s));
    if (untimed.length) {
      notes.append(el("div", { class: "cal-online" },
        el("p", { class: "cal-online-title" }, "Online or no time listed"),
        el("ul", {}, untimed.map((s) => el("li", {},
          el("button", {
            type: "button", class: "linkbtn small",
            "aria-label": `${s.code} · Sec ${s.sectionNumber}${s.noSchedule ? " (time not listed yet)" : ", online with no set time"}. Details`,
            on: { click: () => onSelect(s) },
          }, `${s.code} · Sec ${s.sectionNumber}${s.noSchedule ? " (time not listed yet)" : ""}`))))));
    }
    const twin = ghost && !sections.some((s) => s.id === ghost.id) && sections.find((s) => s.code === ghost.code);
    if (twin) {
      notes.append(el("p", { class: "cal-key cal-repeat-hint" }, el("span", { class: "repeat-badge", "aria-hidden": "true" }, `${(copies.get(ghost.code) || 1) + 1}×`),
        `${ghost.code} is already in this plan (Sec ${twin.sectionNumber}). Adding Sec ${ghost.sectionNumber} too is fine as a backup.`));
    }
    if (ghost && !isTimed(ghost)) {
      notes.append(el("p", { class: "cal-key" }, ghost.noSchedule
        ? `${ghost.code} has no time listed yet, so it won't show on the grid.`
        : `${ghost.code} is online with no set time, so it won't show on the grid.`));
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

// Small DOM helpers shared by every page: escaping, an element builder, the
// day strip, toasts, dialogs, and loading / empty / error boxes.
// Prefer el() and textContent. innerHTML is only ever used with esc().

import { CONFIG } from "./config.js";
import { DAYS, DAY_NAMES, WEEKEND, formatRange, isTimedMeeting } from "./time.js";

export function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]
  ));
}

// el("button", { class: "btn", type: "button", on: { click: fn }, dataset: { id: 3 } }, "Add")
// Children can be strings (added as text, never parsed), nodes, arrays, or null.
export function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key === "class") node.className = value;
    else if (key === "text") node.textContent = value;
    else if (key === "on") for (const [type, fn] of Object.entries(value)) node.addEventListener(type, fn);
    else if (key === "dataset") Object.assign(node.dataset, value);
    else if (key === "style") Object.assign(node.style, value);
    else if (value === true) node.setAttribute(key, "");
    else node.setAttribute(key, String(value));
  }
  append(node, children);
  return node;
}

function append(node, children) {
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
}

export const $ = (sel, root = document) => root.querySelector(sel);
export const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

export function clear(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
  return node;
}

// M T W Th F, with the meeting days filled in. Screen readers get "Meets Monday, Wednesday".
// Sa / Su only show up for a class that meets then.
export function dayStrip(dayList) {
  const label = dayList.length ? `Meets ${dayList.map((d) => DAY_NAMES[d]).join(", ")}` : "No set meeting days";
  return el("span", { class: "daystrip", role: "img", "aria-label": label },
    [...DAYS, ...WEEKEND.filter((d) => dayList.includes(d))]
      .map((d) => el("span", { class: dayList.includes(d) ? "on" : "", "aria-hidden": "true" }, d)));
}

// One line per meeting: day strip, time and room, or "Online" for a part with
// no set time. A section that is online only says "Online / no set time", and
// one whose schedule isn't entered yet says "Time not listed yet".
export function meetingLines(s) {
  if (!s.meetings.length) {
    return el("div", { class: "meets" }, el("div", { class: "meet" }, el("span", { class: "pill pill-online" }, "Time not listed yet")));
  }
  const timed = s.meetings.filter(isTimedMeeting);
  return el("div", { class: "meets" }, s.meetings.map((m) => {
    if (isTimedMeeting(m)) {
      return el("div", { class: "meet" }, dayStrip(m.dayList),
        el("span", { class: "meet-time" }, formatRange(m.startMin, m.endMin)),
        el("span", { class: "meet-room" }, m.room || "Room TBA"));
    }
    return el("div", { class: "meet" },
      el("span", { class: "pill pill-online" }, timed.length ? "+ online part" : "Online / no set time"));
  }));
}

// Every instructor, each linked to RateMyProfessors, or "Professor TBA".
export function instructorLinks(s, missing = "Professor TBA") {
  if (!s.instructors.length) return el("span", {}, missing);
  return el("span", { class: "instructors" },
    s.instructors.flatMap((p, i) => [i ? ", " : null, professorLink(p.name, p.last)]));
}

// "40 seats", "25 seats (100 / 25 by part)" or "Seats unknown". A student needs
// a seat in every part, so the smallest part is the number that counts.
export function seatsLabel(s) {
  if (s.seats === null || s.seats === undefined) return "Seats unknown";
  const count = `${s.seats} ${s.seats === 1 ? "seat" : "seats"}`;
  return s.seatsText.includes("/") ? `${count} (${s.seatsText} by part)` : count;
}

// ---------- loading, empty and error boxes ----------

export function loadingBox(text = "Loading…", lines = 3) {
  return el("div", { class: "state state-loading", role: "status" },
    el("span", { class: "sr-only" }, text),
    Array.from({ length: lines }, () => el("div", { class: "skeleton", "aria-hidden": "true" })));
}

export function emptyBox(title, body, ...actions) {
  return el("div", { class: "state state-empty" },
    el("p", { class: "state-title" }, title),
    body ? el("p", { class: "muted" }, body) : null,
    actions.length ? el("div", { class: "state-actions" }, actions) : null);
}

export function errorBox(text, retry) {
  return el("div", { class: "state state-error", role: "alert" },
    el("p", { class: "state-title" }, "Something went wrong"),
    el("p", { class: "muted" }, text),
    retry ? el("button", { type: "button", class: "btn", on: { click: retry } }, "Try again") : null);
}

// ---------- toasts ----------

let toastTimer = 0;

// One toast at a time. action: { label: "Undo", run: fn }
export function toast(message, action) {
  let region = document.getElementById("toast-region");
  if (!region) {
    region = el("div", { id: "toast-region", class: "toast-region", "aria-live": "polite" });
    document.body.append(region);
  }
  clearTimeout(toastTimer);
  clear(region);
  const box = el("div", { class: "toast" }, el("span", {}, message));
  if (action) {
    box.append(el("button", {
      type: "button", class: "toast-action",
      on: { click: () => { clear(region); action.run(); } },
    }, action.label));
  }
  box.append(el("button", { type: "button", class: "toast-close", "aria-label": "Dismiss", on: { click: () => clear(region) } }, "×"));
  region.append(box);
  toastTimer = setTimeout(() => clear(region), 6000);
}

// ---------- dialogs (native <dialog>: focus trap, Esc to close) ----------

// Opens a dialog and returns it. content is a node or array of nodes.
// onClose runs once, however the dialog is closed.
export function openDialog({ title, content, className = "", onClose, labelledBy } = {}) {
  const heading = el("h2", { class: "dialog-title", id: `dlg-${Math.random().toString(36).slice(2, 8)}` }, title);
  const dialog = el("dialog", { class: `dialog ${className}`, "aria-labelledby": labelledBy || heading.id },
    el("div", { class: "dialog-head" },
      heading,
      el("button", { type: "button", class: "icon-btn", "aria-label": "Close", on: { click: () => dialog.close() } }, "×")),
    el("div", { class: "dialog-body" }, content));
  // a click on the backdrop (the dialog element itself, outside the box) closes it
  dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });
  dialog.addEventListener("close", () => { dialog.remove(); onClose?.(dialog.returnValue); }, { once: true });
  document.body.append(dialog);
  dialog.showModal();
  return dialog;
}

export function confirmDialog(title, message, okLabel = "OK") {
  return new Promise((resolve) => {
    let answer = false;
    const dialog = openDialog({
      title,
      content: [
        el("p", {}, message),
        el("div", { class: "dialog-actions" },
          el("button", { type: "button", class: "btn", on: { click: () => dialog.close() } }, "Cancel"),
          el("button", { type: "button", class: "btn btn-primary", on: { click: () => { answer = true; dialog.close(); } } }, okLabel)),
      ],
      onClose: () => resolve(answer),
    });
  });
}

export function promptDialog(title, label, value = "", maxLength = 30) {
  return new Promise((resolve) => {
    let answer = null;
    const input = el("input", { type: "text", class: "input", value, maxlength: maxLength, required: true, autocomplete: "off" });
    const form = el("form", { method: "dialog", class: "stack" },
      el("label", { class: "field" }, el("span", {}, label), input),
      el("div", { class: "dialog-actions" },
        el("button", { type: "button", class: "btn", on: { click: () => dialog.close() } }, "Cancel"),
        el("button", { type: "submit", class: "btn btn-primary" }, "Save")));
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      if (input.value.trim()) { answer = input.value.trim(); dialog.close(); }
    });
    const dialog = openDialog({ title, content: form, onClose: () => resolve(answer) });
    input.select();
  });
}

// Puts a short message in an aria-live region (results counts, conflict results).
export function announce(region, text) {
  if (region && region.textContent !== text) region.textContent = text;
}

export function plural(n, word, many = `${word}s`) {
  return `${n} ${n === 1 ? word : many}`;
}

// Tells listeners (track.js) that something happened, the same way store.js
// reports plan changes. detail holds only safe values: never typed text.
export function signal(type, detail = {}) {
  try {
    document.dispatchEvent(new CustomEvent("ezclass:action", { detail: { type, ...detail } }));
  } catch (e) { /* never let a listener break the page */ }
}

// A professor's name linking to a RateMyProfessors search in a new tab, or
// "Professor TBA" when the section has no professor yet. Searches by last
// name at the school; falls back to the full name if the last name is missing.
export function professorLink(name, lastName, missing = "Professor TBA") {
  if (!name) return el("span", {}, missing);
  return el("a", {
    class: "prof-link", href: CONFIG.professorUrl(lastName || name), target: "_blank", rel: "noopener",
    "aria-label": `${name}: look up on ${CONFIG.professorSite} (opens in a new tab)`,
  }, name);
}

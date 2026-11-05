// Builds the same header and footer on every page, keeps the plan name and
// count in the header up to date, shows the Undo toast after every change,
// and handles the light/dark switch. Each page's HTML has an empty
// <header id="site-header"> and <footer id="site-footer"> and body[data-page].

import { getMajors, showDataDate } from "./api.js";
import { CONFIG } from "./config.js";
import { majorLabel, openMajorPrompt } from "./majorPrompt.js";
import { getState, isPersistent, readValue, subscribe, undo, writeValue } from "./store.js";
import { el, toast } from "./ui.js";

const page = document.body.dataset.page || "home";

const LINKS = [
  { page: "major", href: "major.html", label: "My Major", short: "Major" },
  { page: "ge", href: "ge.html", label: "GE", short: "GE" },
  { page: "search", href: "search.html", label: "Search", short: "Search" },
  { page: "schedule", href: "schedule.html", label: "My Schedule", short: "Schedule" },
];

// ---------- theme ----------

const THEME_KEY = "ezclass.theme";
const media = window.matchMedia("(prefers-color-scheme: dark)");
const currentTheme = () => document.documentElement.dataset.theme || (media.matches ? "dark" : "light");

function applyTheme(theme) {
  if (theme === "light" || theme === "dark") document.documentElement.dataset.theme = theme;
}
applyTheme(readValue(THEME_KEY));

function themeButton() {
  const button = el("button", { type: "button", class: "icon-btn theme-btn" });
  const label = () => {
    const next = currentTheme() === "dark" ? "light" : "dark";
    button.setAttribute("aria-label", `Switch to ${next} mode`);
    button.title = `Switch to ${next} mode`;
    button.textContent = currentTheme() === "dark" ? "☀" : "☾";
  };
  button.addEventListener("click", () => {
    const next = currentTheme() === "dark" ? "light" : "dark";
    applyTheme(next);
    writeValue(THEME_KEY, next);
    label();
  });
  media.addEventListener?.("change", label);
  label();
  return button;
}

// ---------- header ----------

const logo = () => el("a", { class: "logo", href: "index.html", "aria-label": `${CONFIG.productName} home` },
  el("span", { class: "logo-mark", "aria-hidden": "true" }), el("span", { class: "logo-text" }, CONFIG.productName));

function homeHeader() {
  return el("div", { class: "topbar-inner" },
    logo(),
    el("nav", { class: "homenav", "aria-label": "Main" },
      el("a", { href: "ge.html", class: "navlink" }, "GE"),
      el("a", { href: "major.html", class: "btn btn-primary btn-sm" }, "Start planning")),
    themeButton());
}

const majorChip = el("button", { type: "button", class: "chip chip-major", "aria-haspopup": "dialog", on: { click: openMajorPrompt } });
const planChip = el("a", { href: "schedule.html", class: "chip chip-plan" });

function appHeader() {
  return el("div", { class: "topbar-inner" },
    logo(),
    el("nav", { class: "mainnav", "aria-label": "Scheduler" },
      LINKS.map((l) => el("a", {
        href: l.href, class: "navlink", "aria-current": l.page === page ? "page" : null,
      }, el("span", { class: "nav-long" }, l.label), el("span", { class: "nav-short" }, l.short)))),
    el("div", { class: "topbar-tools" }, majorChip, planChip, themeButton()));
}

async function updateMajorChip(state) {
  majorChip.textContent = "";
  if (!state.majorId) {
    majorChip.append(el("span", {}, "Pick your major"));
    majorChip.setAttribute("aria-label", "Pick your major");
    return;
  }
  let name = state.majorId;
  try {
    const major = (await getMajors()).find((m) => m.major_id === state.majorId);
    if (major) name = majorLabel(major);
  } catch (e) { /* keep the id */ }
  majorChip.append(el("span", { class: "chip-text" }, name), el("span", { class: "caret", "aria-hidden": "true" }, "▾"));
  majorChip.setAttribute("aria-label", `Major: ${name}. Change major`);
}

function updatePlanChip(state) {
  const plan = state.plans[state.activePlan];
  const n = plan.sectionIds.length;
  planChip.textContent = "";
  planChip.append(el("span", { class: "chip-text" }, plan.name), el("span", { class: "count", "data-plan-count": "" }, String(n)));
  planChip.setAttribute("aria-label", `${plan.name}, ${n} ${n === 1 ? "section" : "sections"}. Open My Schedule`);
}

// ---------- footer ----------

// "Report a problem" link, or null when config.js has no URL for it.
export function reportLink(text = "Report a problem") {
  if (!CONFIG.reportProblemUrl) return null;
  return el("a", { href: CONFIG.reportProblemUrl, target: "_blank", rel: "noopener noreferrer" }, text);
}

function footer() {
  const updated = el("span", { "data-updated": "" });
  showDataDate(updated, " ");
  const report = reportLink("Report a wrong time or other problem");
  return el("div", { class: "footer-inner" },
    el("p", {},
      `${CONFIG.disclaimer} Class times are for ${CONFIG.termName} and can change, so confirm every class in ${CONFIG.registrationSite} before you register.`,
      updated, " Your plans are kept in this browser only.",
      report ? " " : null, report),
    el("p", {},
      "We count visits anonymously (pages viewed, majors picked, searches, plan changes and conflict checks), with no names, IP addresses or cookies. ",
      el("a", { href: "#", id: "track-optout" }, "Turn off counting")));
}

// ---------- wire up ----------

const header = document.getElementById("site-header");
if (header) {
  header.classList.add("topbar");
  header.append(page === "home" ? homeHeader() : appHeader());
}
const foot = document.getElementById("site-footer");
if (foot) {
  foot.classList.add("site-footer");
  foot.append(footer());
}

if (!isPersistent() && page !== "home") {
  header?.after(el("p", { class: "notice", role: "status" },
    "Your plans will not be saved on this device (this browser is blocking storage). They last until you close the tab."));
}

if (page !== "home") {
  const refresh = (state) => { updatePlanChip(state); updateMajorChip(state); };
  refresh(getState());
  subscribe((state, info) => {
    refresh(state);
    if (info.undoable) toast(info.label, { label: "Undo", run: undo });
    else if (info.undone) toast("Undone");
  });
}

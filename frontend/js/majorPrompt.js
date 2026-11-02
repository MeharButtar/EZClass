// The "What's your major?" dialog. Opens on My Major the first time, and from
// the major chip in the header on any page. Majors come from /api/majors;
// coming_soon ones are listed but can't be picked.

import { getMajors } from "./api.js";
import { CONFIG } from "./config.js";
import { getState, setMajor } from "./store.js";
import { clear, el, errorBox, loadingBox, openDialog } from "./ui.js";

export function majorLabel(major) {
  return major.degree ? `${major.name}, ${major.degree}` : major.name;
}

let open = false;

export function openMajorPrompt() {
  if (open) return;
  open = true;
  const current = getState().majorId;
  const list = el("ul", { class: "major-list", "aria-label": "Majors" });
  const search = el("input", {
    type: "search", class: "input", placeholder: "Start typing, e.g. psychology",
    autocomplete: "off", "aria-label": "Search majors",
  });
  const status = el("p", { class: "muted small", "aria-live": "polite" });
  const body = el("div", { class: "stack" },
    el("p", {}, `Pick your major and we'll show every class it requires, with the ${CONFIG.termName} sections under each one.`),
    search, status, list);

  const dialog = openDialog({
    title: current ? "Change your major" : "What's your major?",
    content: body,
    className: "dialog-major",
    onClose: () => { open = false; },
  });

  function choose(major) {
    setMajor(major.major_id);
    dialog.close();
    if (document.body.dataset.page !== "major") location.href = "major.html";
  }

  function render(majors) {
    clear(list);
    const q = search.value.trim().toLowerCase();
    const shown = majors.filter((m) => !q || majorLabel(m).toLowerCase().includes(q));
    for (const m of shown) {
      const soon = m.status !== "live";
      list.append(el("li", {},
        el("button", {
          type: "button", class: `major-option${m.major_id === current ? " current" : ""}`,
          disabled: soon, "aria-current": m.major_id === current ? "true" : null,
          dataset: { majorId: m.major_id },
          on: { click: () => choose(m) },
        },
        el("span", {}, majorLabel(m)),
        soon ? el("span", { class: "pill" }, "coming soon") : null,
        m.major_id === current ? el("span", { class: "pill pill-accent" }, "current") : null)));
    }
    status.textContent = shown.length ? "" : "No major matches that. More majors are on the way.";
    return shown;
  }

  async function load() {
    clear(list).append(loadingBox("Loading majors…", 4));
    try {
      const majors = await getMajors();
      if (!majors.length) {
        clear(list);
        status.textContent = "No majors are loaded yet.";
        return;
      }
      render(majors);
      search.addEventListener("input", () => render(majors));
      // Enter in the search box picks the first major that can be picked
      search.addEventListener("keydown", (e) => {
        if (e.key !== "Enter") return;
        e.preventDefault();
        const first = list.querySelector(".major-option:not([disabled])");
        if (first) first.click();
      });
    } catch (e) {
      clear(list).append(errorBox(e.message, load));
    }
  }
  load();
  search.focus();
}

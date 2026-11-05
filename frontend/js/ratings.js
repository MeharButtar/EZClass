// RateMyProfessors scores the student looks up and saves for professors of the
// classes in their plan. The student types the numbers in; nothing is fetched
// from RateMyProfessors, and the scores are saved in this browser only (store.js).
//
// ratingBadge()   read-only "★ 4.2" shown wherever that professor appears
// ratingControl() badge plus Add / Edit, for sections in the plan
//                 (My Schedule list and the calendar detail card)

import { CONFIG } from "./config.js";
import { clearProfRating, getProfRating, setProfRating } from "./store.js";
import { el, openDialog, professorLink } from "./ui.js";

export function ratingBadge(name) {
  const r = getProfRating(name);
  if (!r) return null;
  const label = `Your saved ${CONFIG.professorSite} score for ${name}: rating ${r.rating} out of 5`
    + (r.difficulty ? `, difficulty ${r.difficulty} out of 5` : "");
  return el("span", { class: "rating-badge", role: "img", title: label, "aria-label": label },
    el("span", { "aria-hidden": "true" }, `★ ${r.rating.toFixed(1)}`),
    r.difficulty ? el("span", { class: "rating-diff", "aria-hidden": "true" }, ` · diff ${r.difficulty.toFixed(1)}`) : null);
}

function scoreInput(id, value, required) {
  return el("input", {
    id, type: "number", class: "input", min: "1", max: "5", step: "0.1", inputmode: "decimal",
    required, value: value ? value.toFixed(1) : null, placeholder: required ? "e.g. 4.2" : "optional",
  });
}

export function openRatingDialog(name, lastName) {
  const saved = getProfRating(name);
  const rating = scoreInput("rating-quality", saved?.rating, true);
  const difficulty = scoreInput("rating-difficulty", saved?.difficulty, false);
  const error = el("p", { class: "field-error", role: "alert", hidden: true });

  const form = el("form", { class: "stack", novalidate: true },
    el("p", {}, "Look the professor up, then type in the numbers you see. They are saved in this browser only."),
    el("p", {}, professorLink(name, lastName), " (opens a search in a new tab)"),
    el("div", { class: "rating-fields" },
      el("label", { class: "field", for: "rating-quality" }, "Rating (1 to 5)", rating),
      el("label", { class: "field", for: "rating-difficulty" }, "Difficulty (1 to 5)", difficulty)),
    error,
    el("div", { class: "dialog-actions" },
      saved ? el("button", { type: "button", class: "btn btn-danger", on: { click: () => { clearProfRating(name); dialog.close(); } } }, "Remove") : null,
      el("button", { type: "button", class: "btn", on: { click: () => dialog.close() } }, "Cancel"),
      el("button", { type: "submit", class: "btn btn-primary" }, "Save")));

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const diffText = difficulty.value.trim();
    const okRating = rating.value.trim() !== "" && Number(rating.value) >= 1 && Number(rating.value) <= 5;
    const okDiff = diffText === "" || (Number(diffText) >= 1 && Number(diffText) <= 5);
    if (!okRating || !okDiff) {
      error.hidden = false;
      error.textContent = !okRating ? "Enter the rating as a number from 1 to 5, like 4.2." : "Difficulty must be a number from 1 to 5, or left blank.";
      (!okRating ? rating : difficulty).focus();
      return;
    }
    setProfRating(name, Number(rating.value), diffText === "" ? undefined : Number(diffText));
    dialog.close();
  });

  const dialog = openDialog({ title: `${CONFIG.professorSite} score: ${name}`, content: form, className: "dialog-small" });
  rating.focus();
  return dialog;
}

// Badge + Edit, or an "Add rating" button. Nothing for a section without a professor.
// beforeOpen runs first (the calendar card closes itself so it can't go stale).
export function ratingControl(section, { beforeOpen } = {}) {
  if (!section.professor) return null;
  const saved = getProfRating(section.professor);
  const open = () => { beforeOpen?.(); openRatingDialog(section.professor, section.professorLast); };
  return el("span", { class: "rating-control" },
    saved ? ratingBadge(section.professor) : null,
    el("button", {
      type: "button", class: "linkbtn small",
      "aria-label": `${saved ? "Edit" : "Add"} the ${CONFIG.professorSite} score for ${section.professor}`,
      on: { click: open },
    }, saved ? "Edit" : "Add rating"));
}

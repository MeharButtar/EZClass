// Reviews: the average and the approved reviews (20 at a time), and a form
// to leave one. New reviews wait for the owner to approve them, so nothing
// shows up right away. Everything a person typed is put on the page with
// textContent (el() does that), never as HTML.

import "../nav.js";
import { getReviews } from "../api.js";
import { busy, counter, sendForm } from "../feedback.js";
import { $, clear, el, plural, signal } from "../ui.js";

const PAGE = 20;
const COMMENT_MAX = 600;
const summary = $("#review-summary");
const list = $("#review-list");
const more = $("#review-more");
const form = $("#review-form");
const status = $("#review-status");
const sendButton = $("#review-send");
const starInputs = [...form.querySelectorAll("input[name=rating]")];

// "★★★★☆", read out as "4 out of 5 stars"
function stars(rating, extraClass = "") {
  const whole = Math.round(rating);
  return el("span", { class: `stars-show ${extraClass}`.trim(), role: "img", "aria-label": `${rating} out of 5 stars` },
    el("span", { class: "on", "aria-hidden": "true" }, "★".repeat(whole)),
    el("span", { class: "off", "aria-hidden": "true" }, "★".repeat(5 - whole)));
}

function formatDate(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || "");
  return m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]))
    .toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : "";
}

function reviewItem(r) {
  return el("li", { class: "review" },
    stars(r.rating),
    r.comment ? el("p", { class: "review-text" }, r.comment) : null,
    el("p", { class: "review-meta" }, `${r.name} · ${formatDate(r.date)}`));
}

let shown = 0;

async function load(first = false) {
  try {
    const data = await getReviews(shown, PAGE);
    if (first) {
      clear(summary).append(data.count
        ? el("div", { class: "review-average" },
            el("span", { class: "review-average-num" }, data.average.toFixed(1)),
            stars(data.average, "big"),
            el("span", { class: "muted" }, `from ${plural(data.count, "review")}`))
        : el("p", {}, "No reviews yet. Be the first."));
    }
    list.append(...data.reviews.map(reviewItem));
    shown += data.reviews.length;
    more.hidden = shown >= data.count;
  } catch (e) {
    if (first) clear(summary).append(el("p", {}, `Could not load reviews: ${e.message}`));
  }
}
more.addEventListener("click", () => load());

// ---------- the star picker: a radio group, so arrow keys work ----------

function paintStars(upTo) {
  starInputs.forEach((input) => input.nextElementSibling.classList.toggle("on", Number(input.value) <= upTo));
}
const chosen = () => Number(starInputs.find((i) => i.checked)?.value || 0);
for (const input of starInputs) {
  input.addEventListener("change", () => paintStars(chosen()));
  input.nextElementSibling.addEventListener("mouseenter", () => paintStars(Number(input.value)));
  input.nextElementSibling.addEventListener("mouseleave", () => paintStars(chosen()));
}

// ---------- sending ----------

const comment = form.elements.comment;
const updateCount = counter(comment, $("#review-count"), COMMENT_MAX);

function say(message, isError) {
  status.textContent = message;
  status.classList.toggle("is-error", Boolean(isError));
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (sendButton.disabled) return;
  const rating = chosen();
  const text = comment.value.trim();
  if (!rating) { say("Pick a rating from 1 to 5 stars.", true); starInputs[0].focus(); return; }
  if (text.length > COMMENT_MAX) { say(`Your comment can be at most ${COMMENT_MAX} characters.`, true); comment.focus(); return; }
  if (/http|www\./i.test(text)) { say("Please leave links out of your review.", true); comment.focus(); return; }
  busy(sendButton, true, "Send review");
  say("", false);
  try {
    await sendForm("/api/reviews", form, { rating, comment: text, name: form.elements.name.value.trim() });
    form.reset();
    paintStars(0);
    updateCount();
    say("Thanks! Reviews show up after we take a quick look.", false);
    signal("review_submit");
  } catch (err) {
    say(err.message, true);
  } finally {
    busy(sendButton, false, "Send review");
  }
});

load(true);

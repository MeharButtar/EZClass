// What the Reviews and Support forms share: sending, the spam checks the
// server expects, and the character counters.
//
// The server keeps only what the person typed (backend/routes/feedback.py).
// Sent along, and never stored: the hidden "website" field (a honeypot only
// bots fill in), how long the page has been open (bots send instantly), and a
// random id this browser makes up so the server can limit how often one
// browser sends (it keeps it in memory for 10 minutes, not in the database).

import { postJSON } from "./api.js";
import { readValue, writeValue } from "./store.js";

const opened = Date.now();
const SENDER_KEY = "ezclass_sender";
const ID_PATTERN = /^[A-Za-z0-9-]{8,64}$/;

function senderId() {
  let id = readValue(SENDER_KEY);
  if (!id || !ID_PATTERN.test(id)) {
    try {
      id = crypto.randomUUID ? crypto.randomUUID()
        : Array.from(crypto.getRandomValues(new Uint8Array(16)), (b) => b.toString(16).padStart(2, "0")).join("");
    } catch (e) {
      id = `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
    }
    writeValue(SENDER_KEY, id);
  }
  return id;
}

// POST the fields plus the spam checks. Resolves with the server's answer; an
// ApiError's message is a sentence the student can read.
export function sendForm(url, form, fields) {
  return postJSON(url, {
    ...fields,
    website: form.elements.website?.value || "",
    elapsed_ms: Date.now() - opened,
    visitor_id: senderId(),
  });
}

// "123 / 600" under a text box, updated as the student types.
export function counter(input, output, max) {
  const update = () => {
    const n = input.value.length;
    output.textContent = `${n} / ${max}`;
    output.classList.toggle("over", n > max);
  };
  input.addEventListener("input", update);
  update();
  return update;
}

// Sending... / Send, so a double click can't send twice.
export function busy(button, on, label) {
  button.disabled = on;
  button.textContent = on ? "Sending…" : label;
}

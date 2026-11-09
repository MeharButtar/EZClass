// Anonymous usage counting for EzClass. See backend/routes/analytics.py for
// what the server keeps.
//
// Pages and the store announce what happened with an "ezclass:action" event
// (see signal() in ui.js and emit() in store.js). This file turns those into
// analytics events, keeping only a short whitelist of safe values. It never
// reads the page, so nothing typed into a search box can reach it.
//
// Never sent: names, emails, or anything typed (only whether a box was used).
// Off when the browser sends Do Not Track or Global Privacy Control, or after
// the footer opt-out link. Every storage and network call is wrapped so
// tracking can never break the site.

import { readValue, removeValue, writeValue } from "./store.js";

const OPTOUT_KEY = "ezclass_optout";
const VISITOR_KEY = "ezclass_vid";      // same keys as v1, so returning visitors keep their id
const SESSION_KEY = "ezclass_sid";
const ID_PATTERN = /^[A-Za-z0-9-]{8,64}$/;
const VIEWS = ["home", "major", "ge", "search", "schedule", "reviews", "support"];

// ---------- ids ----------

function randomId() {
  try {
    if (crypto.randomUUID) return crypto.randomUUID();
    return Array.from(crypto.getRandomValues(new Uint8Array(16)), (b) => b.toString(16).padStart(2, "0")).join("");
  } catch (e) {
    return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
  }
}

function visitorId() {
  let id = readValue(VISITOR_KEY);
  if (!id || !ID_PATTERN.test(id)) { id = randomId(); writeValue(VISITOR_KEY, id); }
  return id;
}

let memorySession = null;
function sessionId() {
  try {
    let id = sessionStorage.getItem(SESSION_KEY);
    if (!id || !ID_PATTERN.test(id)) { id = randomId(); sessionStorage.setItem(SESSION_KEY, id); }
    return id;
  } catch (e) {
    memorySession = memorySession || randomId();
    return memorySession;
  }
}

// ---------- on / off ----------

function browserSaysNo() {
  try {
    return navigator.doNotTrack === "1" || window.doNotTrack === "1" || navigator.globalPrivacyControl === true;
  } catch (e) { return false; }
}
const optedOut = () => readValue(OPTOUT_KEY) === "1";
const enabled = () => !browserSaysNo() && !optedOut();

// ---------- sending ----------

function send(event, props) {
  if (!enabled()) return;
  try {
    const body = JSON.stringify({ event, visitor_id: visitorId(), session_id: sessionId(), props });
    // text/plain keeps the beacon a "simple" request (no preflight)
    const sent = navigator.sendBeacon && navigator.sendBeacon("/api/event", new Blob([body], { type: "text/plain" }));
    if (!sent) {
      fetch("/api/event", { method: "POST", body, keepalive: true, headers: { "Content-Type": "text/plain" } }).catch(() => {});
    }
  } catch (e) { /* tracking must never break the site */ }
}

// ---------- what each action becomes ----------

const str = (v) => (typeof v === "string" ? v.slice(0, 40) : "");
const num = (v) => (Number.isFinite(v) ? v : null);

const EVENTS = {
  cart_add: (d) => ({ cart_size: num(d.cartSize) }),
  cart_remove: (d) => ({ cart_size: num(d.cartSize) }),
  cart_clear: () => ({ cart_size: 0 }),
  plan_create: (d) => ({ cart_size: num(d.cartSize) }),
  major_select: (d) => ({ major: str(d.major) }),
  search: (d) => ({ subject: str(d.subject), day: str(d.day), has_prof: Boolean(d.hasProf), has_kw: Boolean(d.hasKw), results: num(d.results) }),
  ge_search: (d) => ({ areas: str(d.areas), day: str(d.day), has_prof: Boolean(d.hasProf), has_kw: Boolean(d.hasKw), results: num(d.results) }),
  conflict_check: (d) => ({ conflict_free: Boolean(d.conflictFree), cart_size: num(d.cartSize) }),
  // that something was sent, never what (the support kind is one of a fixed list)
  review_submit: () => ({}),
  support_submit: (d) => ({ kind: str(d.kind) }),
};

try {
  const view = document.body?.dataset.page;
  // a page that is only forwarding an old link isn't a visit; the page it opens counts
  if (!document.documentElement.dataset.leaving) send("page_view", { view: VIEWS.includes(view) ? view : "home" });

  document.addEventListener("ezclass:action", (e) => {
    try {
      const build = EVENTS[e.detail?.type];
      if (build) send(e.detail.type, build(e.detail));
    } catch (err) { /* ignore */ }
  });

  // footer opt-out link (built by nav.js)
  const label = () => {
    const link = document.getElementById("track-optout");
    if (!link) return;
    link.textContent = browserSaysNo() ? "Counting is off (your browser asks not to be tracked)"
      : optedOut() ? "Counting is off. Turn it back on" : "Turn off counting";
  };
  document.addEventListener("click", (e) => {
    const link = e.target.closest?.("#track-optout");
    if (!link) return;
    e.preventDefault();   // href="#" would otherwise jump to the top
    if (optedOut()) {
      removeValue(OPTOUT_KEY);
    } else {
      writeValue(OPTOUT_KEY, "1");
      removeValue(VISITOR_KEY);   // opting back in later starts a fresh id
    }
    label();
  });
  label();
} catch (e) { /* tracking must never break the site */ }

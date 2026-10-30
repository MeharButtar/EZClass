// Anonymous usage counting for EzClass. Loaded after app.js and only watches the
// page from the outside (clicks, changes, the conflict box), so app.js has no
// tracking code in it. See backend/routes/analytics.py for what the server keeps.
//
// Never sent: names, emails, or anything typed into the professor/keyword boxes
// (only whether they were used). Off when the browser sends Do Not Track or
// Global Privacy Control, or when the footer opt-out link has been clicked.
// Every storage and network call is wrapped so tracking can't break the site.

(function () {
  const OPTOUT_KEY = "ezclass_optout";
  const VISITOR_KEY = "ezclass_vid";
  const SESSION_KEY = "ezclass_sid";
  const RESULT_DELAY_MS = 900;   // long enough for the search fetch to finish and the count to update

  // ---------- storage helpers (private windows can throw on any of these) ----------

  function storage(kind) {
    try { return window[kind]; } catch (e) { return null; }
  }
  function getItem(kind, key) {
    try { return storage(kind).getItem(key); } catch (e) { return null; }
  }
  function setItem(kind, key, value) {
    try { storage(kind).setItem(key, value); } catch (e) { /* ignore */ }
  }
  function removeItem(kind, key) {
    try { storage(kind).removeItem(key); } catch (e) { /* ignore */ }
  }

  function randomId() {
    try {
      if (crypto.randomUUID) return crypto.randomUUID();
      const bytes = crypto.getRandomValues(new Uint8Array(16));
      return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
    } catch (e) {
      return Date.now().toString(36) + "-" + Math.random().toString(36).slice(2, 12);
    }
  }

  // random id that stays in this browser (or this tab, for the session id)
  const memoryIds = {};
  function storedId(kind, key) {
    let id = getItem(kind, key);
    if (!id || !/^[A-Za-z0-9-]{8,64}$/.test(id)) {
      id = memoryIds[key] || randomId();
      memoryIds[key] = id;   // keeps one id for this page even if storage is blocked
      setItem(kind, key, id);
    }
    return id;
  }

  // ---------- on/off ----------

  function browserSaysNo() {
    try {
      return navigator.doNotTrack === "1" || window.doNotTrack === "1" || navigator.globalPrivacyControl === true;
    } catch (e) { return false; }
  }
  function optedOut() { return getItem("localStorage", OPTOUT_KEY) === "1"; }
  function enabled() { return !browserSaysNo() && !optedOut(); }

  // ---------- sending ----------

  function send(event, props) {
    if (!enabled()) return;
    try {
      const body = JSON.stringify({
        event,
        visitor_id: storedId("localStorage", VISITOR_KEY),
        session_id: storedId("sessionStorage", SESSION_KEY),
        props: props || {},
      });
      // text/plain keeps sendBeacon a "simple" request (no preflight)
      const sent = navigator.sendBeacon && navigator.sendBeacon("/api/event", new Blob([body], { type: "text/plain" }));
      if (!sent) {
        fetch("/api/event", { method: "POST", body, keepalive: true, headers: { "Content-Type": "text/plain" } })
          .catch(() => {});
      }
    } catch (e) { /* tracking must never break the site */ }
  }

  // ---------- reading the page ----------

  function byId(id) { return document.getElementById(id); }
  function value(id) { const el = byId(id); return el ? el.value.trim() : ""; }
  function checked(id) { const el = byId(id); return !!(el && el.checked); }

  // "(42)" -> 42, anything else -> null
  function countIn(id) {
    const el = byId(id);
    const m = el && el.textContent.match(/\((\d+)\)/);
    return m ? Number(m[1]) : null;
  }
  function cartSize() { return countIn("cart-count") || 0; }

  function currentView() {
    const view = location.hash.replace("#", "") || "home";
    return ["home", "search", "ge"].includes(view) ? view : "home";
  }

  // Picked GE areas from the summary line, e.g. "Showing: 1B, 5C Clear" -> "1B,5C".
  // Don't "simplify" the capture to ([^C]*?): it stops at the C in codes like 5C
  // and the result silently falls back to "ALL".
  function geAreas() {
    const el = document.querySelector("#ge-chips .ge-summary");
    const m = el && el.textContent.match(/Showing:\s*(.*?)\s*(?:Clear)?\s*$/);
    return m ? m[1].replace(/\s+/g, "") : "ALL";
  }

  // Waits for the results to load, then sends. A new call within the delay replaces
  // the pending one, so clicking 1B then 5C quickly counts as one GE search.
  const pending = {};
  function sendAfterResults(event, buildProps) {
    clearTimeout(pending[event]);
    pending[event] = setTimeout(() => {
      try { send(event, buildProps()); } catch (e) { /* ignore */ }
    }, RESULT_DELAY_MS);
  }

  function trackSearch() {
    sendAfterResults("search", () => ({
      subject: value("subject-filter"),
      day: value("day-filter"),
      has_prof: !!value("professor-filter"),
      has_kw: !!value("keyword-filter"),
      results: countIn("search-count"),
    }));
  }

  function trackGeSearch() {
    sendAfterResults("ge_search", () => ({
      areas: geAreas(),
      day: value("ge-day"),
      has_prof: !!value("ge-professor"),
      has_kw: !!value("ge-keyword"),
      results: countIn("ge-count"),
    }));
  }

  function on(id, type, handler) {
    const el = byId(id);
    if (el) el.addEventListener(type, handler);
  }
  function onEnter(id, handler) {
    on(id, "keydown", (e) => { if (e.key === "Enter") handler(); });
  }

  // ---------- wiring ----------

  try {
    send("page_view", { view: currentView() });
    window.addEventListener("hashchange", () => send("page_view", { view: currentView() }));

    on("search-btn", "click", trackSearch);
    onEnter("professor-filter", trackSearch);
    onEnter("keyword-filter", trackSearch);

    // GE chips are redrawn on every click, so listen on the container. Buttons that
    // only open a dropdown don't run a search, so they don't count.
    on("ge-chips", "click", (e) => {
      const chip = e.target.closest && e.target.closest("[data-act]");
      if (chip && chip.dataset.act !== "open") trackGeSearch();
    });
    on("ge-search-btn", "click", trackGeSearch);
    for (const id of ["ge-cd", "ge-es", "ge-ai", "ge-day"]) on(id, "change", trackGeSearch);
    onEnter("ge-professor", trackGeSearch);
    onEnter("ge-keyword", trackGeSearch);

    // app.js updates the cart before the event bubbles up here, so cartSize() is current
    document.addEventListener("change", (e) => {
      const box = e.target;
      if (box.matches && box.matches("input[data-section-id]")) {
        send(box.checked ? "cart_add" : "cart_remove", { cart_size: cartSize() });
      }
    });
    on("schedule-list", "click", (e) => {
      if (e.target.closest && e.target.closest(".remove-btn")) send("cart_remove", { cart_size: cartSize() });
    });
    on("clear-cart-btn", "click", () => send("cart_clear", { cart_size: 0 }));

    // the conflict box gets class "ok" or "conflict" once the check comes back
    const result = byId("conflict-result");
    if (result && window.MutationObserver) {
      new MutationObserver(() => {
        if (result.classList.contains("ok")) send("conflict_check", { conflict_free: true, cart_size: cartSize() });
        else if (result.classList.contains("conflict")) send("conflict_check", { conflict_free: false, cart_size: cartSize() });
      }).observe(result, { attributes: true, attributeFilter: ["class"] });
    }

    // footer opt-out link
    const link = byId("track-optout");
    const label = () => {
      if (!link) return;
      link.textContent = browserSaysNo() ? "Counting is off (your browser asks not to be tracked)"
        : optedOut() ? "Counting is off. Turn it back on" : "Turn off counting";
    };
    if (link) {
      link.addEventListener("click", (e) => {
        e.preventDefault();   // href="#" would otherwise jump back to the home view
        if (optedOut()) {
          removeItem("localStorage", OPTOUT_KEY);
        } else {
          setItem("localStorage", OPTOUT_KEY, "1");
          removeItem("localStorage", VISITOR_KEY);   // opting back in later starts a fresh id
        }
        label();
      });
    }
    label();
  } catch (e) { /* tracking must never break the site */ }
})();

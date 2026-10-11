// EzClass frontend: a home page, a Search view, a GE Scheduler view, and a cart
// that stays on the right no matter which view you are on. No framework, just
// fetch() calls to the Flask backend.

const CART_KEY = "ezclass_cart_v1";
const VIEWS = ["home", "search", "ge"];
document.title = "EzClass (GE build 3)";

const state = {
  cart: new Map(),          // section_id -> section object
  gePicked: new Set(["ALL"]), // GE area codes currently selected ("ALL" = any GE)
};

// ---------- small helpers ----------

// Escape text before putting it in innerHTML (titles can contain & or quotes).
function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (ch) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch]
  ));
}

function $(id) { return document.getElementById(id); }

// ---------- cart (saved in the browser so it survives reloads) ----------

function saveCart() {
  try {
    localStorage.setItem(CART_KEY, JSON.stringify(Array.from(state.cart.values())));
  } catch (e) { /* private window or storage blocked: cart just won't persist */ }
}

function loadCart() {
  try {
    const raw = localStorage.getItem(CART_KEY);
    if (!raw) return;
    for (const s of JSON.parse(raw)) state.cart.set(s.section_id, s);
  } catch (e) { /* ignore a bad or missing saved cart */ }
}

function addToCart(s) { state.cart.set(s.section_id, s); saveCart(); renderCart(); }
function removeFromCart(id) { state.cart.delete(id); saveCart(); renderCart(); syncCheckboxes(); }

function courseLabel(s) {
  return `${s.subject} ${s.catalog_num} (Sec ${s.section_number})`;
}

function renderCart() {
  const list = $("schedule-list");
  list.innerHTML = "";
  $("cart-count").textContent = state.cart.size ? `(${state.cart.size})` : "";

  if (state.cart.size === 0) {
    list.innerHTML = `<li class="empty-state">Nothing here yet. Add classes with the checkboxes.</li>`;
  }
  for (const s of state.cart.values()) {
    const li = document.createElement("li");
    li.innerHTML = `
      <span>
        <strong>${esc(courseLabel(s))}</strong><br>
        <small>${esc(s.course_title)}<br>${esc(s.days)} ${esc(s.start_time)}-${esc(s.end_time)}</small>
      </span>
      <button class="remove-btn" data-id="${s.section_id}">Remove</button>`;
    li.querySelector(".remove-btn").addEventListener("click", () => removeFromCart(s.section_id));
    list.appendChild(li);
  }
  // any old result is out of date once the cart changes
  const result = $("conflict-result");
  result.textContent = "";
  result.className = "";
}

// keep every visible checkbox in line with the cart
function syncCheckboxes() {
  document.querySelectorAll("input[data-section-id]").forEach((box) => {
    box.checked = state.cart.has(Number(box.dataset.sectionId));
  });
}

async function checkConflicts() {
  const ids = Array.from(state.cart.keys());
  const result = $("conflict-result");
  if (ids.length < 2) {
    result.textContent = "Add at least two classes to check for conflicts.";
    result.className = "";
    return;
  }
  const res = await fetch("/api/schedule/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ section_ids: ids }),
  });
  const data = await res.json();

  if (data.conflict_free) {
    result.textContent = "No conflicts. This schedule works.";
    result.className = "ok";
    return;
  }
  const name = (sec) => {
    const full = state.cart.get(sec.section_id);
    const label = full ? courseLabel(full) : `Section ${sec.section_id}`;
    return `${label} ${sec.days} ${sec.start_time}-${sec.end_time}`;
  };
  result.innerHTML = `<strong>${data.conflicts.length} conflict${data.conflicts.length > 1 ? "s" : ""}:</strong><ul>` +
    data.conflicts.map((c) => `<li>${esc(name(c.section_a))} overlaps ${esc(name(c.section_b))}</li>`).join("") +
    "</ul>";
  result.className = "conflict";
}

// ---------- results table (shared by Search and GE views) ----------

// Link out to a RateMyProfessors search for this professor (no scraping,
// just a search URL that opens in a new tab).
function professorLink(name) {
  if (!name) return "TBA";
  const q = encodeURIComponent(name + " San Diego State University");
  const url = `https://www.ratemyprofessors.com/search/professors?q=${q}`;
  return `<a href="${url}" target="_blank" rel="noopener">${esc(name)}</a>`;
}

function geBadges(s) {
  const badges = (s.ge_areas || []).map((a) => `<span class="badge">${esc(a)}</span>`);
  if (s.cultural_diversity) badges.push(`<span class="badge tag" title="Cultural diversity">CD</span>`);
  if (s.ethnic_studies_grad) badges.push(`<span class="badge tag" title="Counts for the Ethnic Studies graduation requirement">ES</span>`);
  if (s.american_inst) badges.push(`<span class="badge tag" title="Counts for American Institutions">AI</span>`);
  return badges.join(" ");
}

function renderResults(tbodyId, countId, sections) {
  const tbody = $(tbodyId);
  tbody.innerHTML = "";
  $(countId).textContent = `(${sections.length})`;

  if (sections.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="empty-state">No sections match those filters.</td></tr>`;
    return;
  }
  for (const s of sections) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td><input type="checkbox" data-section-id="${s.section_id}" ${state.cart.has(s.section_id) ? "checked" : ""}></td>
      <td>${esc(s.subject)} ${esc(s.catalog_num)}</td>
      <td>${esc(s.course_title)}</td>
      <td>${esc(s.section_number)}</td>
      <td>${professorLink(s.professor_name)}</td>
      <td>${esc(s.days)}</td>
      <td>${esc(s.start_time)}-${esc(s.end_time)}</td>
      <td>${s.building ? esc(s.building + " " + s.room_number) : "TBA"}</td>
      <td>${geBadges(s)}</td>`;
    row.querySelector("input").addEventListener("change", (e) => {
      if (e.target.checked) addToCart(s); else removeFromCart(s.section_id);
      syncCheckboxes();
    });
    tbody.appendChild(row);
  }
}

// ---------- Search view ----------

async function loadSubjects() {
  const subjects = await (await fetch("/api/subjects")).json();
  const select = $("subject-filter");
  for (const subj of subjects) {
    const opt = document.createElement("option");
    opt.value = subj;
    opt.textContent = subj;
    select.appendChild(opt);
  }
}

let searchSeq = 0;
let geSeq = 0;

async function searchSections() {
  const params = new URLSearchParams();
  const fields = { subject: "subject-filter", day: "day-filter", professor: "professor-filter", q: "keyword-filter" };
  for (const [key, id] of Object.entries(fields)) {
    const v = $(id).value.trim();
    if (v) params.set(key, v);
  }
  const mine = ++searchSeq;
  const sections = await (await fetch(`/api/sections?${params}`, { cache: "no-store" })).json();
  if (mine !== searchSeq) return; // a newer search started, ignore this stale answer
  renderResults("results-body", "search-count", sections);
}

// ---------- GE Scheduler view ----------

let geGroups = [];   // [{grp, areas:[...]}] in display order
let geTotal = 0;
let geOpen = null;   // which group's dropdown is open (only one at a time)

async function loadGeChips() {
  const data = await (await fetch("/api/ge-areas")).json();
  geTotal = data.total_sections;
  const groups = new Map();
  for (const a of data.areas) {
    if (!groups.has(a.grp)) groups.set(a.grp, []);
    groups.get(a.grp).push(a);
  }
  geGroups = Array.from(groups, ([grp, areas]) => ({ grp, areas }));
  renderGeChips();
}

function groupState(g) {
  const picked = g.areas.filter((a) => state.gePicked.has(a.area_code)).length;
  return picked === 0 ? "off" : picked === g.areas.length ? "on" : "part";
}

function renderGeChips() {
  const box = $("ge-chips");
  const isAll = state.gePicked.has("ALL");

  // top row: All GE, then one button per main area (areas with sub-areas get a dropdown arrow)
  let top = `<button class="chip ${isAll ? "on" : ""}" data-act="all">All GE <span class="n">${geTotal}</span></button>`;
  for (const g of geGroups) {
    const single = g.areas.length === 1;
    const st = groupState(g);
    const picked = g.areas.filter((a) => state.gePicked.has(a.area_code)).length;
    const empty = g.areas.every((a) => a.section_count === 0);
    const extra = single
      ? `<span class="n">${g.areas[0].section_count}</span>`
      : (picked ? `<span class="n">${picked}/${g.areas.length}</span>` : "") + `<span class="caret">${geOpen === g.grp ? "\u25B4" : "\u25BE"}</span>`;
    top += `<button class="chip ${st} ${empty ? "empty" : ""} ${geOpen === g.grp ? "open" : ""}"
              data-act="${single ? "toggle" : "open"}" data-grp="${esc(g.grp)}" ${single ? `data-code="${esc(g.areas[0].area_code)}"` : ""}>
              ${esc(g.grp)} ${extra}</button>`;
  }

  // dropdown panel for the open group
  let panel = "";
  const open = geGroups.find((g) => g.grp === geOpen && g.areas.length > 1);
  if (open) {
    const st = groupState(open);
    panel = `<div class="ge-panel"><div class="chip-label">${esc(open.grp)}: pick one or more</div>
      <button class="chip ${st === "on" ? "on" : ""}" data-act="group" data-grp="${esc(open.grp)}">All of this area</button>` +
      open.areas.map((a) => `<button class="chip ${state.gePicked.has(a.area_code) ? "on" : ""} ${a.section_count === 0 ? "empty" : ""}"
          data-act="toggle" data-code="${esc(a.area_code)}">${esc(a.area_code)}. ${esc(a.name)} <span class="n">${a.section_count}</span></button>`).join("") +
      `</div>`;
  }

  // summary line of what is currently selected
  const summary = isAll ? "Showing every GE class"
    : `Showing: ${Array.from(state.gePicked).map(esc).join(", ")} <button class="linkbtn" data-act="all">Clear</button>`;

  box.innerHTML = `<div class="chip-group">${top}</div>${panel}<div class="ge-summary">${summary}</div>`;
  box.querySelectorAll("[data-act]").forEach((el) => el.addEventListener("click", () => geClick(el)));
}

function geClick(el) {
  const act = el.dataset.act;
  if (act === "open") {
    geOpen = geOpen === el.dataset.grp ? null : el.dataset.grp;
    renderGeChips();
    return;
  }
  if (act === "all") {
    state.gePicked = new Set(["ALL"]);
  } else if (act === "group") {
    const g = geGroups.find((x) => x.grp === el.dataset.grp);
    state.gePicked.delete("ALL");
    const allOn = g.areas.every((a) => state.gePicked.has(a.area_code));
    for (const a of g.areas) { if (allOn) state.gePicked.delete(a.area_code); else state.gePicked.add(a.area_code); }
  } else {
    const code = el.dataset.code;
    state.gePicked.delete("ALL");
    if (state.gePicked.has(code)) state.gePicked.delete(code); else state.gePicked.add(code);
  }
  if (state.gePicked.size === 0) state.gePicked.add("ALL");
  renderGeChips();
  searchGe();
}

async function searchGe() {
  const params = new URLSearchParams();
  params.set("ge", Array.from(state.gePicked).join(","));
  if ($("ge-cd").checked) params.set("cultural_diversity", "1");
  if ($("ge-es").checked) params.set("ethnic_studies", "1");
  if ($("ge-ai").checked) params.set("american_inst", "1");
  const day = $("ge-day").value;
  const prof = $("ge-professor").value.trim();
  const q = $("ge-keyword").value.trim();
  if (day) params.set("day", day);
  if (prof) params.set("professor", prof);
  if (q) params.set("q", q);
  const mine = ++geSeq;
  const sections = await (await fetch(`/api/sections?${params}`, { cache: "no-store" })).json();
  if (mine !== geSeq) return; // a newer search started, ignore this stale answer
  renderResults("ge-results-body", "ge-count", sections);
}

// ---------- views (the address bar #home / #search / #ge picks the view) ----------

let geLoaded = false;
let searchLoaded = false;

function showView() {
  let view = location.hash.replace("#", "") || "home";
  if (!VIEWS.includes(view)) view = "home";
  for (const v of VIEWS) $(`view-${v}`).hidden = v !== view;
  document.querySelectorAll("#nav a").forEach((a) => a.classList.toggle("active", a.dataset.view === view));

  if (view === "search" && !searchLoaded) { searchLoaded = true; loadSubjects().then(searchSections); }
  if (view === "ge" && !geLoaded) { geLoaded = true; loadGeChips().then(searchGe); }
  syncCheckboxes();
}

// ---------- wire it up ----------

$("search-btn").addEventListener("click", searchSections);
$("ge-search-btn").addEventListener("click", searchGe);
for (const id of ["ge-cd", "ge-es", "ge-ai", "ge-day"]) $(id).addEventListener("change", searchGe);
for (const id of ["professor-filter", "keyword-filter"]) $(id).addEventListener("keydown", (e) => { if (e.key === "Enter") searchSections(); });
for (const id of ["ge-professor", "ge-keyword"]) $(id).addEventListener("keydown", (e) => { if (e.key === "Enter") searchGe(); });
$("check-conflicts-btn").addEventListener("click", checkConflicts);
$("clear-cart-btn").addEventListener("click", () => { state.cart.clear(); saveCart(); renderCart(); syncCheckboxes(); });
window.addEventListener("hashchange", showView);

loadCart();
renderCart();
showView();

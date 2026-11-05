// The student's choices: major, up to three plans of sections, courses already
// taken, busy times, and the RateMyProfessors scores they looked up. This is
// the only file that touches localStorage.
//
// Shape (one key, "ezclass.state.v2"):
//   { majorId, plans: [{ name, sectionIds }], activePlan, completedCourses: ["CS 150"],
//     busy: [{ id, label, days, start, end }],
//     profRatings: { "Patricia Kraft": { rating: 4.2, difficulty: 3.1 } }, updatedAt }
//
// The "cart" is the active plan. Every change can be undone once. Pages read
// with getState() and react with subscribe(). Each action also fires an
// "ezclass:action" event on document, which track.js listens to.
//
// Built so it can sync to a server account later: the whole state is one plain
// JSON object with updatedAt, and every change goes through commit().

const KEY = "ezclass.state.v2";
export const MAX_PLANS = 3;
const PLAN_NAMES = ["Plan A", "Plan B", "Plan C"];
const MAX_SECTIONS = 60;
const MAX_NAME = 30;

// ---------- storage (any of this can throw in a private window) ----------

function openStorage() {
  try {
    const s = window.localStorage;
    s.setItem("ezclass.test", "1");
    s.removeItem("ezclass.test");
    return s;
  } catch (e) {
    return null;
  }
}

const storage = openStorage();
const memory = new Map();   // used for everything when storage is blocked

export const isPersistent = () => storage !== null;

// Small extra values (tracking ids, the opt-out flag, theme), kept beside the state.
export function readValue(key) {
  try { return storage ? storage.getItem(key) : (memory.get(key) ?? null); } catch (e) { return null; }
}
export function writeValue(key, value) {
  try { if (storage) storage.setItem(key, value); else memory.set(key, value); } catch (e) { /* full or blocked */ }
}
export function removeValue(key) {
  try { if (storage) storage.removeItem(key); else memory.delete(key); } catch (e) { /* ignore */ }
}

// ---------- shape checks ----------

const COURSE_CODE = /^[A-Z]{1,8} [0-9]{1,4}[A-Z]{0,2}$/;
const MAX_RATINGS = 200;

// RateMyProfessors scores run 1 to 5. One decimal, like the site shows them.
const score = (v) => {
  const n = typeof v === "string" ? Number.parseFloat(v.replace(",", ".")) : v;
  return Number.isFinite(n) && n >= 1 && n <= 5 ? Math.round(n * 10) / 10 : null;
};

// { rating, difficulty? } with valid scores, or null. The rating is required.
function cleanRating(value) {
  if (!value || typeof value !== "object") return null;
  const rating = score(value.rating);
  if (rating === null) return null;
  const difficulty = score(value.difficulty);
  return difficulty === null ? { rating } : { rating, difficulty };
}
const isId = (v) => Number.isInteger(v) && v > 0;

function blankState() {
  return { majorId: null, plans: [{ name: PLAN_NAMES[0], sectionIds: [] }], activePlan: 0,
           completedCourses: [], busy: [], profRatings: {}, updatedAt: 0 };
}

// Keeps whatever is the right shape and drops the rest, so a damaged or
// hand-edited value can never break a page.
function validate(raw) {
  const state = blankState();
  if (!raw || typeof raw !== "object") return state;
  if (typeof raw.majorId === "string" && /^[a-z0-9_]{1,40}$/.test(raw.majorId)) state.majorId = raw.majorId;
  if (Array.isArray(raw.plans)) {
    const plans = raw.plans.slice(0, MAX_PLANS).filter((p) => p && typeof p === "object").map((p, i) => ({
      name: typeof p.name === "string" && p.name.trim() ? p.name.trim().slice(0, MAX_NAME) : PLAN_NAMES[i],
      sectionIds: Array.isArray(p.sectionIds) ? [...new Set(p.sectionIds.filter(isId))].slice(0, MAX_SECTIONS) : [],
    }));
    if (plans.length) state.plans = plans;
  }
  if (Number.isInteger(raw.activePlan) && raw.activePlan >= 0 && raw.activePlan < state.plans.length) {
    state.activePlan = raw.activePlan;
  }
  if (Array.isArray(raw.completedCourses)) {
    state.completedCourses = [...new Set(raw.completedCourses.filter((c) => typeof c === "string" && COURSE_CODE.test(c)))].slice(0, 300);
  }
  if (Array.isArray(raw.busy)) {
    state.busy = raw.busy.filter((b) => b && typeof b === "object" && typeof b.id === "string"
      && typeof b.days === "string" && /^\d{2}:\d{2}$/.test(b.start) && /^\d{2}:\d{2}$/.test(b.end))
      .slice(0, 20)
      .map((b) => ({ id: b.id.slice(0, 20), label: String(b.label || "Busy").slice(0, 30), days: b.days.slice(0, 10), start: b.start, end: b.end }));
  }
  if (raw.profRatings && typeof raw.profRatings === "object" && !Array.isArray(raw.profRatings)) {
    for (const [name, value] of Object.entries(raw.profRatings).slice(0, MAX_RATINGS)) {
      const clean = cleanRating(value);
      if (typeof name === "string" && name.trim() && name.length <= 80 && clean) state.profRatings[name.trim()] = clean;
    }
  }
  if (Number.isFinite(raw.updatedAt)) state.updatedAt = raw.updatedAt;
  return state;
}

// The first version saved its cart as a list of section objects under this key.
// A returning visitor with no v2 state gets that cart back as Plan A.
const V1_CART_KEY = "ezclass_cart_v1";

function fromV1Cart() {
  try {
    const old = JSON.parse(readValue(V1_CART_KEY) || "null");
    if (!Array.isArray(old)) return null;
    const ids = old.map((s) => s && s.section_id).filter(isId);
    return ids.length ? validate({ plans: [{ name: PLAN_NAMES[0], sectionIds: ids }] }) : null;
  } catch (e) {
    return null;
  }
}

function load() {
  try {
    const text = readValue(KEY);
    if (!text) {
      const carried = fromV1Cart();
      if (carried) {
        writeValue(KEY, JSON.stringify(carried));
        return carried;
      }
    }
    return validate(text ? JSON.parse(text) : null);
  } catch (e) {
    return blankState();
  }
}

function save() {
  writeValue(KEY, JSON.stringify(state));
}

// ---------- state, subscribers, undo ----------

let state = load();
let undoState = null;
const listeners = new Set();

const clone = (value) => JSON.parse(JSON.stringify(value));

export function getState() {
  return clone(state);
}

export const activePlan = () => state.plans[state.activePlan];

export function isInPlan(sectionId) {
  return activePlan().sectionIds.includes(sectionId);
}

export function isCompleted(code) {
  return state.completedCourses.includes(code);
}

// fn(state, info). info: { label, undoable, external }. Returns an unsubscribe function.
export function subscribe(fn) {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

function notify(info) {
  const snapshot = getState();
  for (const fn of listeners) {
    try { fn(snapshot, info); } catch (e) { console.error(e); }
  }
}

function emit(type, detail = {}) {
  try {
    document.dispatchEvent(new CustomEvent("ezclass:action", { detail: { type, ...detail } }));
  } catch (e) { /* never let a listener break an action */ }
}

// Every change goes through here. label is what the Undo toast says.
function commit(change, label, action) {
  const before = clone(state);
  change(state);
  state.updatedAt = Date.now();
  undoState = label ? before : undoState;
  save();
  notify({ label, undoable: Boolean(label) });
  if (action) emit(action.type, action);
}

export const canUndo = () => undoState !== null;

export function undo() {
  if (!undoState) return;
  state = undoState;
  undoState = null;
  state.updatedAt = Date.now();
  save();
  notify({ label: null, undone: true });
}

// Another tab changed the state: pick it up so both tabs show the same plan.
window.addEventListener("storage", (e) => {
  if (e.key !== KEY) return;
  state = load();
  undoState = null;
  notify({ external: true });
});

// ---------- section actions (always on the active plan) ----------

export function addSection(id, label = "class") {
  if (!isId(id) || isInPlan(id)) return false;
  if (activePlan().sectionIds.length >= MAX_SECTIONS) return false;
  commit((s) => { s.plans[s.activePlan].sectionIds.push(id); }, `Added ${label} to ${activePlan().name}`,
    { type: "cart_add", cartSize: activePlan().sectionIds.length + 1 });
  return true;
}

export function removeSection(id, label = "class") {
  if (!isInPlan(id)) return;
  commit((s) => {
    const plan = s.plans[s.activePlan];
    plan.sectionIds = plan.sectionIds.filter((x) => x !== id);
  }, `Removed ${label}`, { type: "cart_remove", cartSize: activePlan().sectionIds.length - 1 });
}

// Sections that are no longer in the class data (removed in a data update) are
// dropped from every plan. Not undoable: undoing would only bring back ids
// that point at nothing.
export function forgetSections(ids) {
  const gone = new Set(ids);
  if (!state.plans.some((p) => p.sectionIds.some((id) => gone.has(id)))) return false;
  commit((s) => {
    for (const plan of s.plans) plan.sectionIds = plan.sectionIds.filter((id) => !gone.has(id));
  }, null);
  return true;
}

export function toggleSection(id, label) {
  if (isInPlan(id)) { removeSection(id, label); return false; }
  return addSection(id, label);
}

export function clearPlan() {
  if (!activePlan().sectionIds.length) return;
  commit((s) => { s.plans[s.activePlan].sectionIds = []; }, `Cleared ${activePlan().name}`, { type: "cart_clear", cartSize: 0 });
}

// ---------- plan actions ----------

function nextPlanName() {
  return PLAN_NAMES.find((n) => !state.plans.some((p) => p.name === n)) || `Plan ${state.plans.length + 1}`;
}

export function createPlan() {
  if (state.plans.length >= MAX_PLANS) return false;
  const name = nextPlanName();
  commit((s) => { s.plans.push({ name, sectionIds: [] }); s.activePlan = s.plans.length - 1; },
    `Created ${name}`, { type: "plan_create", cartSize: 0 });
  return true;
}

export function duplicatePlan(index = state.activePlan) {
  const source = state.plans[index];
  if (!source || state.plans.length >= MAX_PLANS) return false;
  const name = nextPlanName();
  commit((s) => { s.plans.push({ name, sectionIds: [...source.sectionIds] }); s.activePlan = s.plans.length - 1; },
    `Copied ${source.name} to ${name}`, { type: "plan_create", cartSize: source.sectionIds.length });
  return true;
}

export function renamePlan(index, name) {
  const clean = String(name || "").trim().slice(0, MAX_NAME);
  if (!clean || !state.plans[index]) return;
  commit((s) => { s.plans[index].name = clean; }, `Renamed to ${clean}`);
}

// The last plan can't be deleted; it is emptied instead.
export function deletePlan(index = state.activePlan) {
  const plan = state.plans[index];
  if (!plan) return;
  if (state.plans.length === 1) { clearPlan(); return; }
  commit((s) => {
    s.plans.splice(index, 1);
    if (s.activePlan >= s.plans.length || s.activePlan > index) s.activePlan = Math.max(0, s.activePlan - 1);
  }, `Deleted ${plan.name}`);
}

export function switchPlan(index) {
  if (index === state.activePlan || !state.plans[index]) return;
  commit((s) => { s.activePlan = index; }, `Switched to ${state.plans[index].name}`);
}

// ---------- RateMyProfessors scores the student saved ----------
// Kept per professor (by the name the schedule shows), so one score covers
// every section that professor teaches. They never leave the browser.

export function getProfRating(name) {
  return (name && state.profRatings[name]) || null;
}

// Returns false if the rating isn't a number from 1 to 5.
export function setProfRating(name, rating, difficulty) {
  const clean = cleanRating({ rating, difficulty });
  if (!name || !clean) return false;
  if (!state.profRatings[name] && Object.keys(state.profRatings).length >= MAX_RATINGS) return false;
  commit((s) => { s.profRatings[name] = clean; }, `Saved ${clean.rating} for ${name}`);
  return true;
}

export function clearProfRating(name) {
  if (!state.profRatings[name]) return;
  commit((s) => { delete s.profRatings[name]; }, `Removed the score for ${name}`);
}

// ---------- major and completed courses ----------

export function setMajor(majorId) {
  if (!/^[a-z0-9_]{1,40}$/.test(majorId) || majorId === state.majorId) return;
  commit((s) => { s.majorId = majorId; }, state.majorId ? "Changed your major" : null, { type: "major_select", major: majorId });
}

export function toggleCompleted(code) {
  if (!COURSE_CODE.test(code)) return;
  const taken = isCompleted(code);
  commit((s) => {
    s.completedCourses = taken ? s.completedCourses.filter((c) => c !== code) : [...s.completedCourses, code];
  }, taken ? `${code} no longer marked as taken` : `Marked ${code} as taken`);
}

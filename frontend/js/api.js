// Fetch helpers for the Flask API. Every call throws an ApiError with a
// sentence a student can read; pages show it in an error box with "Try again".
// Sections are turned into one shape (normalizeSection) and cached by id, so
// the calendar on every page can draw the plan without refetching.

import { ALL_DAYS, isTimedMeeting, parseDays, toMinutes } from "./time.js";

export class ApiError extends Error {}

async function request(url, options = {}) {
  let res;
  try {
    res = await fetch(url, { headers: { Accept: "application/json" }, ...options });
  } catch (e) {
    throw new ApiError("Could not reach EzClass. Check your connection and try again.");
  }
  if (!res.ok) {
    let message = `The server answered ${res.status}.`;
    try { message = (await res.json()).error || message; } catch (e) { /* not JSON */ }
    throw new ApiError(message);
  }
  try {
    return await res.json();
  } catch (e) {
    throw new ApiError("The server sent something unexpected.");
  }
}

const memo = new Map();   // url -> promise, for lists that don't change during a visit
function cached(url) {
  if (!memo.has(url)) memo.set(url, request(url).catch((e) => { memo.delete(url); throw e; }));
  return memo.get(url);
}

// ---------- data info ----------

// { data_updated: "2026-11-04" | null }, the day the class data was imported.
export const getDataInfo = () => cached("/api/info");

// "Nov 4, 2026" (parsed as a local date, so it doesn't slip a day west of UTC).
export function formatDataDate(iso) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(iso || "");
  if (!m) return null;
  return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]))
    .toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

// Fills `node` with "Class data last updated Nov 4, 2026." once it's known.
export function showDataDate(node, before = "", after = "") {
  getDataInfo().then((info) => {
    const date = formatDataDate(info.data_updated);
    if (date) node.textContent = `${before}Class data last updated ${date}.${after}`;
  }).catch(() => { /* leave it out */ });
}

// ---------- sections ----------

// Placeholder "professors" some data rows carry instead of a blank.
const NOT_A_PROFESSOR = /^(to be announced|tba|tbd|staff|instructor)$/i;

// One meeting: { days, dayList, startMin, endMin, building, room, online }.
// room is what students read ("GMCS 333", "Online" for a live online class at
// a set time); building is "" unless it's a place on campus or elsewhere.
function normalizeMeeting(raw) {
  const online = Boolean(raw.online);
  const building = String(raw.building || "").trim();
  const isOnlineBuilding = building.toUpperCase() === "ONLINE";
  return {
    days: online ? "" : raw.day || "",
    dayList: online ? [] : parseDays(raw.day),
    startMin: online ? NaN : toMinutes(raw.start),
    endMin: online ? NaN : toMinutes(raw.end),
    building: online || isOnlineBuilding ? "" : building,
    room: online ? "" : isOnlineBuilding ? "Online" : [building, raw.room].filter(Boolean).join(" "),
    online,
    // live online: a set day and time, but on Zoom (building "ONLINE"). It is
    // time in class, but not a day on campus. "ONLINE / BSE" is not live online.
    liveOnline: !online && isOnlineBuilding,
  };
}

// One shape for a section everywhere in the frontend. A section has zero or
// more meetings (zero = schedule not entered yet) and zero or more
// instructors; the single-value fields below
// them (professor, dayList, startMin, room ...) are summaries for filters and
// older code: the first instructor, every day it meets, the first timed meeting.
export function normalizeSection(raw) {
  const meetings = Array.isArray(raw.meetings)
    ? raw.meetings.map(normalizeMeeting)
    : [normalizeMeeting({ day: raw.days, start: raw.start_time, end: raw.end_time, building: raw.building, room: raw.room_number })];
  const people = Array.isArray(raw.instructors) ? raw.instructors
    : raw.professor_name ? [{ name: raw.professor_name, last: raw.professor_last }] : [];
  const instructors = people
    .map((p) => ({ name: String(p.name || "").trim(), last: String(p.last || "").trim() }))
    .filter((p) => p.name && !NOT_A_PROFESSOR.test(p.name));
  const timed = meetings.filter(isTimedMeeting);
  const first = timed[0];
  const seats = Number.isFinite(raw.seats_total) ? raw.seats_total : Number.isFinite(raw.capacity) ? raw.capacity : null;
  return {
    id: raw.section_id,
    courseId: raw.course_id,
    subject: raw.subject,
    catalog: raw.catalog_num,
    code: `${raw.subject} ${raw.catalog_num}`,
    title: raw.section_title || raw.course_title || "",   // special topics: the section's own title
    courseTitle: raw.course_title || "",
    sectionTitle: raw.section_title || "",
    units: Number.parseFloat(raw.units) || 0,
    sectionNumber: raw.section_number || "",
    classNumber: /^\d+$/.test(String(raw.class_number ?? "")) ? String(raw.class_number) : "",   // "5834", or "" when unknown
    meetings,
    instructors,
    untimed: timed.length === 0,                          // not on the calendar: online only, or no schedule yet
    onlineOnly: meetings.length > 0 && timed.length === 0,
    noSchedule: meetings.length === 0,                    // "Time not listed yet"
    onlinePart: timed.length > 0 && timed.length < meetings.length,   // hybrid: "+ online part"
    professor: instructors[0]?.name || "",
    professorLast: instructors[0]?.last || "",
    days: first?.days || "",
    dayList: ALL_DAYS.filter((d) => timed.some((m) => m.dayList.includes(d))),
    startMin: first ? first.startMin : NaN,
    endMin: first ? first.endMin : NaN,
    building: first?.building || "",
    room: [...new Set(timed.map((m) => m.room).filter(Boolean))].join(" + "),
    seats,                                    // smallest part; null = unknown
    seatsText: raw.seats_text || (seats === null ? "" : String(seats)),
    capacity: seats,
    geAreas: raw.ge_areas || [],
    cd: Boolean(raw.cultural_diversity),
    es: Boolean(raw.ethnic_studies_grad),
    ai: Boolean(raw.american_inst),
  };
}

const sectionCache = new Map();

function remember(list) {
  const sections = list.map(normalizeSection);
  for (const s of sections) sectionCache.set(s.id, s);
  return sections;
}

export const cachedSection = (id) => sectionCache.get(id) || null;

// /api/sections with any of its filters (subject, day, professor, q, ge, ...).
export async function searchSections(params = {}) {
  const query = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) if (v !== "" && v !== null && v !== undefined) query.set(k, v);
  return remember(await request(`/api/sections?${query}`, { cache: "no-store" }));
}

const chunks = (list, size) => Array.from({ length: Math.ceil(list.length / size) }, (_, i) => list.slice(i * size, i * size + size));

// Sections by id, in the order asked for. Ids that no longer exist are skipped.
export async function sectionsByIds(ids) {
  const missing = ids.filter((id) => !sectionCache.has(id));
  for (const part of chunks(missing, 200)) {
    remember(await request(`/api/sections?ids=${part.join(",")}`));
  }
  return ids.map((id) => sectionCache.get(id)).filter(Boolean);
}

// Every section of these courses, grouped: Map courseId -> [sections].
export async function sectionsForCourses(courseIds) {
  const byCourse = new Map(courseIds.map((id) => [id, []]));
  for (const part of chunks([...new Set(courseIds)], 200)) {
    for (const s of remember(await request(`/api/sections?course_id=${part.join(",")}`))) {
      byCourse.get(s.courseId)?.push(s);
    }
  }
  return byCourse;
}

// ---------- everything else ----------

export const getMajors = () => cached("/api/majors");
export const getRequirements = (majorId) => cached(`/api/majors/${encodeURIComponent(majorId)}/requirements`);
export const getSubjects = () => cached("/api/subjects");
export const getGeAreas = () => cached("/api/ge-areas");

export function findCourses({ subjects, min, max, hasSections = true }) {
  const query = new URLSearchParams({ subject: subjects.join("|") });
  if (min !== null && min !== undefined) query.set("min", min);
  if (max !== null && max !== undefined) query.set("max", max);
  if (hasSections) query.set("has_sections", "1");
  return cached(`/api/courses?${query}`);
}

export function postJSON(url, body) {
  return request(url, {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

// Approved reviews, newest first: { average, count, reviews: [{ rating, comment, name, date }] }
export const getReviews = (offset = 0, limit = 20) => request(`/api/reviews?limit=${limit}&offset=${offset}`, { cache: "no-store" });

export function checkConflicts(sectionIds) {
  return request("/api/schedule/check", {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ section_ids: sectionIds }),
  });
}

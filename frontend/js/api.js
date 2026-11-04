// Fetch helpers for the Flask API. Every call throws an ApiError with a
// sentence a student can read; pages show it in an error box with "Try again".
// Sections are turned into one shape (normalizeSection) and cached by id, so
// the calendar on every page can draw the plan without refetching.

import { parseDays, toMinutes } from "./time.js";

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

// ---------- sections ----------

// Placeholder "professors" some data rows carry instead of a blank.
const NOT_A_PROFESSOR = /^(to be announced|tba|tbd|staff|instructor)$/i;

// One shape for a section everywhere in the frontend.
export function normalizeSection(raw) {
  const professor = (raw.professor_name || "").trim();
  const hasProfessor = professor && !NOT_A_PROFESSOR.test(professor);
  const dayList = parseDays(raw.days);
  return {
    id: raw.section_id,
    courseId: raw.course_id,
    subject: raw.subject,
    catalog: raw.catalog_num,
    code: `${raw.subject} ${raw.catalog_num}`,
    title: raw.course_title || "",
    units: Number.parseFloat(raw.units) || 0,
    sectionNumber: raw.section_number || "",
    professor: hasProfessor ? professor : "",
    professorLast: hasProfessor ? (raw.professor_last || "").trim() : "",
    days: raw.days || "",
    dayList,
    start: raw.start_time || "",
    end: raw.end_time || "",
    startMin: toMinutes(raw.start_time),
    endMin: toMinutes(raw.end_time),
    building: raw.building || "",
    room: raw.building ? `${raw.building} ${raw.room_number || ""}`.trim() : "",
    capacity: raw.capacity ?? null,
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

export function checkConflicts(sectionIds) {
  return request("/api/schedule/check", {
    method: "POST",
    headers: { Accept: "application/json", "Content-Type": "application/json" },
    body: JSON.stringify({ section_ids: sectionIds }),
  });
}

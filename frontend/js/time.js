// Day, time and meeting helpers. These follow backend/models/conflicts.py
// exactly, so a clash the calendar shows is a clash the server's conflict
// check reports:
//   - day patterns: two-letter tokens (Tu, Th, Sa, Su) are read before
//     one-letter ones, so "TTh" is Tuesday + Thursday; "R" also means Thursday
//   - a section can meet more than once (lecture + lab, or a timed part and
//     an online part). Two sections clash when some timed meeting of one
//     shares a day with some timed meeting of the other and the times
//     overlap; back to back (one ends exactly when the next starts) is fine
//   - online meetings have no day or time, so they never clash

export const DAYS = ["M", "T", "W", "Th", "F"];
export const WEEKEND = ["Sa", "Su"];
export const ALL_DAYS = [...DAYS, ...WEEKEND];
export const DAY_NAMES = { M: "Monday", T: "Tuesday", W: "Wednesday", Th: "Thursday", F: "Friday", Sa: "Saturday", Su: "Sunday" };
export const DAY_SHORT = { M: "Mon", T: "Tue", W: "Wed", Th: "Thu", F: "Fri", Sa: "Sat", Su: "Sun" };

// Same table as DAY_TOKENS in conflicts.py, mapped to our day codes.
const TOKENS = { M: "M", T: "T", Tu: "T", W: "W", Th: "Th", R: "Th", F: "F", Sa: "Sa", Su: "Su" };

// "MWF" -> ["M", "W", "F"], "TTh" / "TR" -> ["T", "Th"]. Unknown letters are skipped.
export function parseDays(pattern) {
  const found = new Set();
  const s = String(pattern ?? "").trim();
  let i = 0;
  while (i < s.length) {
    const two = s.slice(i, i + 2);
    if (TOKENS[two]) { found.add(TOKENS[two]); i += 2; continue; }
    if (TOKENS[s[i]]) found.add(TOKENS[s[i]]);
    i += 1;
  }
  return ALL_DAYS.filter((d) => found.has(d));
}

// The calendar's columns: Monday to Friday, plus a weekend day only if a class meets then.
export function weekColumns(dayLists) {
  const used = new Set(dayLists.flat());
  return [...DAYS, ...WEEKEND.filter((d) => used.has(d))];
}

// "14:30" -> 870. Anything unreadable -> NaN (the meeting then shows as "no set time").
export function toMinutes(t) {
  const m = String(t ?? "").trim().match(/^(\d{1,2}):(\d{2})/);
  return m ? Number(m[1]) * 60 + Number(m[2]) : NaN;
}

// 870 -> "2:30pm", 600 -> "10am"
export function formatTime(mins) {
  if (!Number.isFinite(mins)) return "";
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  const suffix = h >= 12 ? "pm" : "am";
  const h12 = ((h + 11) % 12) + 1;
  return m ? `${h12}:${String(m).padStart(2, "0")}${suffix}` : `${h12}${suffix}`;
}

// "9:30–10:45am", or "11am–12:15pm" when the ends are on different halves of the day
export function formatRange(startMin, endMin) {
  if (!Number.isFinite(startMin) || !Number.isFinite(endMin)) return "";
  const a = formatTime(startMin);
  const b = formatTime(endMin);
  const sameHalf = (startMin < 720) === (endMin < 720);
  return `${sameHalf ? a.replace(/am|pm/, "") : a}–${b}`;
}

// ---------- meetings ----------

// A meeting with a day and a time (one that goes on the calendar).
export const isTimedMeeting = (m) => !m.online && Number.isFinite(m.startMin) && Number.isFinite(m.endMin) && m.dayList.length > 0;
export const timedMeetings = (s) => s.meetings.filter(isTimedMeeting);

// A section with at least one timed meeting. Online-only sections are listed apart, never on the grid.
export const isTimed = (s) => s.meetings.some(isTimedMeeting);

// Every pair of meetings where a and b are both in class: [{ a, b, days }].
export function meetingClashes(a, b) {
  if (a.id === b.id) return [];
  const out = [];
  for (const ma of timedMeetings(a)) {
    for (const mb of timedMeetings(b)) {
      const days = ma.dayList.filter((d) => mb.dayList.includes(d));
      if (days.length && ma.startMin < mb.endMin && mb.startMin < ma.endMin) out.push({ a: ma, b: mb, days });
    }
  }
  return out;
}

export const overlaps = (a, b) => meetingClashes(a, b).length > 0;

// "Mon and Wed, 9:30–10:15am": when two clashing sections are both in class.
// Clashes at the same time on different days are merged; different times are
// joined with "; " ("Mon and Wed, 12–12:50pm; Mon, 1–1:15pm").
export function describeOverlap(a, b) {
  const byTime = new Map();   // "12–12:50pm" -> { start, days }
  for (const { a: ma, b: mb, days } of meetingClashes(a, b)) {
    const start = Math.max(ma.startMin, mb.startMin);
    const range = formatRange(start, Math.min(ma.endMin, mb.endMin));
    if (!byTime.has(range)) byTime.set(range, { start, days: new Set() });
    for (const d of days) byTime.get(range).days.add(d);
  }
  return [...byTime].sort((x, y) => x[1].start - y[1].start).map(([range, { days }]) => {
    const names = ALL_DAYS.filter((d) => days.has(d)).map((d) => DAY_SHORT[d]);
    const list = names.length > 1 ? `${names.slice(0, -1).join(", ")} and ${names[names.length - 1]}` : names[0];
    return `${list}, ${range}`;
  }).join("; ");
}

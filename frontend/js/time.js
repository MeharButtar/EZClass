// Day and time helpers. These follow backend/models/conflicts.py exactly, so a
// clash the calendar shows is a clash the server's conflict check reports:
//   - day patterns: two-letter tokens (Tu, Th) are read before one-letter ones,
//     so "TTh" is Tuesday + Thursday; "R" also means Thursday ("TR")
//   - two sections clash when they share a day and their times overlap;
//     back to back (one ends exactly when the next starts) is fine

export const DAYS = ["M", "T", "W", "Th", "F"];
export const DAY_NAMES = { M: "Monday", T: "Tuesday", W: "Wednesday", Th: "Thursday", F: "Friday" };
export const DAY_SHORT = { M: "Mon", T: "Tue", W: "Wed", Th: "Thu", F: "Fri" };

// Same table as DAY_TOKENS in conflicts.py, mapped to our day codes.
const TOKENS = { M: "M", T: "T", Tu: "T", W: "W", Th: "Th", R: "Th", F: "F" };

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
  return DAYS.filter((d) => found.has(d));
}

// "14:30" -> 870. Anything unreadable -> NaN (the section then shows as "no set time").
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

export const isTimed = (s) => Number.isFinite(s.startMin) && Number.isFinite(s.endMin) && s.dayList.length > 0;

export function sharedDays(a, b) {
  return a.dayList.filter((d) => b.dayList.includes(d));
}

export function overlaps(a, b) {
  if (a.id === b.id || !isTimed(a) || !isTimed(b)) return false;
  if (!sharedDays(a, b).length) return false;
  return a.startMin < b.endMin && b.startMin < a.endMin;
}

// Every clashing pair in a list.
export function findOverlaps(sections) {
  const pairs = [];
  for (let i = 0; i < sections.length; i++) {
    for (let j = i + 1; j < sections.length; j++) {
      if (overlaps(sections[i], sections[j])) pairs.push([sections[i], sections[j]]);
    }
  }
  return pairs;
}

// "Mon and Wed, 9:30–10:15am": when two clashing sections are both in class.
export function describeOverlap(a, b) {
  const days = sharedDays(a, b).map((d) => DAY_SHORT[d]);
  const list = days.length > 1 ? `${days.slice(0, -1).join(", ")} and ${days[days.length - 1]}` : days[0];
  return `${list}, ${formatRange(Math.max(a.startMin, b.startMin), Math.min(a.endMin, b.endMin))}`;
}

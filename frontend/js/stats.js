// Numbers about a week of classes, for the strip under the calendar on
// My Schedule: units, hours in class, days on campus and gaps between classes.
// Counted per timed meeting; online parts take no time on the calendar.
// A live online meeting (set day and time, room "Online") is time in class
// but not a day on campus: a day with only those is an "online only" day.
// (There is no walking-time number: the data has building codes, not distances.)
// Pure functions, no DOM.

import { ALL_DAYS, timedMeetings } from "./time.js";

// A student may add several sections of one course on purpose (backups), so
// units count each course once. CS 150 and CS 150L are different courses.
export function planUnits(sections) {
  const units = new Map();
  for (const s of sections) if (!units.has(s.code)) units.set(s.code, s.units || 0);
  return [...units.values()].reduce((n, u) => n + u, 0);
}

// Courses with more than one section in the plan: [{ code, sections }], in plan order.
export function repeatedCourses(sections) {
  const byCode = new Map();
  for (const s of sections) {
    if (!byCode.has(s.code)) byCode.set(s.code, []);
    byCode.get(s.code).push(s);
  }
  return [...byCode].filter(([, list]) => list.length > 1).map(([code, list]) => ({ code, sections: list }));
}

export function weekStats(sections) {
  const byDay = new Map(ALL_DAYS.map((d) => [d, []]));
  for (const s of sections) {
    for (const m of timedMeetings(s)) {
      for (const d of m.dayList) byDay.get(d).push({ startMin: m.startMin, endMin: m.endMin, liveOnline: Boolean(m.liveOnline) });
    }
  }

  let minutesInClass = 0;
  let longestGap = 0;
  let totalGap = 0;

  for (const list of byDay.values()) {
    list.sort((a, b) => a.startMin - b.startMin);
    let busyUntil = null;
    for (const b of list) {
      // time already counted (two meetings at once, "one time, two rooms") isn't counted twice
      minutesInClass += Math.max(0, b.endMin - Math.max(b.startMin, busyUntil ?? b.startMin));
      if (busyUntil !== null && b.startMin > busyUntil) {
        totalGap += b.startMin - busyUntil;
        longestGap = Math.max(longestGap, b.startMin - busyUntil);
      }
      busyUntil = busyUntil === null ? b.endMin : Math.max(busyUntil, b.endMin);
    }
  }

  return {
    classes: sections.length,
    units: planUnits(sections),
    hoursInClass: minutesInClass / 60,
    days: ALL_DAYS.filter((d) => byDay.get(d).length),                                       // any class, campus or online
    campusDays: ALL_DAYS.filter((d) => byDay.get(d).some((b) => !b.liveOnline)),
    onlineOnlyDays: ALL_DAYS.filter((d) => byDay.get(d).length && byDay.get(d).every((b) => b.liveOnline)),
    longestGap,
    totalGap,
  };
}

// 95 -> "1h 35m", 30 -> "30m", 0 -> "none"
export function formatDuration(mins) {
  if (!mins) return "none";
  const h = Math.floor(mins / 60);
  const m = Math.round(mins % 60);
  if (!h) return `${m}m`;
  return m ? `${h}h ${m}m` : `${h}h`;
}

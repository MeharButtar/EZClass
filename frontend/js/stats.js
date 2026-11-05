// Numbers about a week of classes, for the strip under the calendar on
// My Schedule: units, hours in class, days on campus, gaps between classes,
// and "tight walks" (back to back classes in different buildings).
// Counted per timed meeting, so a lecture and its lab in different buildings
// count as a walk too. Online parts take no time on the calendar.
// Pure functions, no DOM.

import { ALL_DAYS, timedMeetings } from "./time.js";

export const TIGHT_WALK_MINUTES = 15;

export function weekStats(sections) {
  const byDay = new Map(ALL_DAYS.map((d) => [d, []]));
  for (const s of sections) {
    timedMeetings(s).forEach((m, idx) => {
      for (const d of m.dayList) byDay.get(d).push({ s, idx, startMin: m.startMin, endMin: m.endMin, building: m.building });
    });
  }

  let minutesInClass = 0;
  let longestGap = 0;
  let totalGap = 0;
  const walks = new Map();   // the same pair on Mon and Wed is listed once

  for (const [day, list] of byDay) {
    list.sort((a, b) => a.startMin - b.startMin);
    let busyUntil = null;
    let last = null;
    for (const b of list) {
      // time already counted (two meetings at once, "one time, two rooms") isn't counted twice
      minutesInClass += Math.max(0, b.endMin - Math.max(b.startMin, busyUntil ?? b.startMin));
      if (busyUntil !== null && b.startMin > busyUntil) {
        totalGap += b.startMin - busyUntil;
        longestGap = Math.max(longestGap, b.startMin - busyUntil);
      }
      if (last && b.startMin >= last.endMin && b.startMin - last.endMin <= TIGHT_WALK_MINUTES
          && last.building && b.building && last.building !== b.building) {
        const key = `${last.s.id}.${last.idx}-${b.s.id}.${b.idx}`;
        if (!walks.has(key)) {
          walks.set(key, { from: last.s, to: b.s, fromBuilding: last.building, toBuilding: b.building,
                           minutes: b.startMin - last.endMin, days: [] });
        }
        walks.get(key).days.push(day);
      }
      if (!last || b.endMin >= last.endMin) last = b;
      busyUntil = busyUntil === null ? b.endMin : Math.max(busyUntil, b.endMin);
    }
  }

  return {
    classes: sections.length,
    units: sections.reduce((n, s) => n + (s.units || 0), 0),
    hoursInClass: minutesInClass / 60,
    days: ALL_DAYS.filter((d) => byDay.get(d).length),
    longestGap,
    totalGap,
    tightWalks: [...walks.values()],
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

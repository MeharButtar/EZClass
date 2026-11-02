// Numbers about a week of classes, for the strip under the calendar on
// My Schedule: units, hours in class, days on campus, gaps between classes,
// and "tight walks" (back to back classes in different buildings).
// Pure functions, no DOM.

import { DAYS, isTimed } from "./time.js";

export const TIGHT_WALK_MINUTES = 15;

export function weekStats(sections) {
  const timed = sections.filter(isTimed);
  const byDay = new Map(DAYS.map((d) => [d, []]));
  for (const s of timed) for (const d of s.dayList) byDay.get(d).push(s);

  let minutesInClass = 0;
  let longestGap = 0;
  let totalGap = 0;
  const walks = new Map();   // the same pair on Mon and Wed is listed once

  for (const [day, list] of byDay) {
    list.sort((a, b) => a.startMin - b.startMin);
    let busyUntil = null;
    let last = null;
    for (const s of list) {
      minutesInClass += s.endMin - s.startMin;
      if (busyUntil !== null && s.startMin > busyUntil) {
        totalGap += s.startMin - busyUntil;
        longestGap = Math.max(longestGap, s.startMin - busyUntil);
      }
      if (last && s.startMin >= last.endMin && s.startMin - last.endMin <= TIGHT_WALK_MINUTES
          && last.building && s.building && last.building !== s.building) {
        const key = `${last.id}-${s.id}`;
        if (!walks.has(key)) walks.set(key, { from: last, to: s, minutes: s.startMin - last.endMin, days: [] });
        walks.get(key).days.push(day);
      }
      if (!last || s.endMin >= last.endMin) last = s;
      busyUntil = busyUntil === null ? s.endMin : Math.max(busyUntil, s.endMin);
    }
  }

  return {
    classes: sections.length,
    units: sections.reduce((n, s) => n + (s.units || 0), 0),
    hoursInClass: minutesInClass / 60,
    days: DAYS.filter((d) => byDay.get(d).length),
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

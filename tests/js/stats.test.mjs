// Tests for the My Schedule numbers (frontend/js/stats.js) and the meeting
// shape they read (normalizeSection in frontend/js/api.js).
// Run: node --test tests/js/stats.test.mjs   (tests/test_frontend_js.py runs every tests/js/*.test.mjs with the Python suite)

import assert from "node:assert/strict";
import { test } from "node:test";
import { normalizeSection } from "../../frontend/js/api.js";
import { planUnits, weekStats } from "../../frontend/js/stats.js";

let nextId = 1;
// A section in the shape /api/sections sends.
function section(subject, catalog, meetings, units = 3) {
  return normalizeSection({
    section_id: nextId++, course_id: nextId, subject, catalog_num: catalog, section_number: "01",
    units: String(units), course_title: `${subject} ${catalog}`, instructors: [], meetings,
  });
}
const meet = (day, start, end, building = "GMCS", room = "333", online = false) => ({ day, start, end, building, room, online });

const inPersonMW = () => section("CS", "450", [meet("MW", "10:00", "11:15")]);
const liveOnlineTTh = () => section("CS", "514", [meet("TTh", "14:00", "15:15", "ONLINE", "")]);

test("a live online meeting is flagged, keeps its time, and shows Online as the room", () => {
  const m = liveOnlineTTh().meetings[0];
  assert.equal(m.liveOnline, true);
  assert.equal(m.online, false);
  assert.equal(m.room, "Online");
  assert.equal(m.building, "");
  assert.deepEqual(m.dayList, ["T", "Th"]);
  assert.equal(m.startMin, 14 * 60);
  for (const building of ["online", " Online ", "ONLINE"]) {
    assert.equal(section("X", "1", [meet("M", "9:00", "9:50", building, "")]).meetings[0].liveOnline, true, building);
  }
});

test("in person, mixed and off-campus buildings are not live online", () => {
  for (const building of ["GMCS", "ONLINE / BSE", "Southwestern College", ""]) {
    assert.equal(section("X", "1", [meet("M", "9:00", "9:50", building, "1")]).meetings[0].liveOnline, false, building);
  }
  // an online part with no day or time is not "live online" either
  const part = section("X", "1", [meet("", "", "", "", "", true)]).meetings[0];
  assert.equal(part.online, true);
  assert.equal(part.liveOnline, false);
});

test("in person MW plus live online TTh: campus Mon and Wed, online only Tue and Thu, hours count both", () => {
  const s = weekStats([inPersonMW(), liveOnlineTTh()]);
  assert.deepEqual(s.campusDays, ["M", "W"]);
  assert.deepEqual(s.onlineOnlyDays, ["T", "Th"]);
  assert.deepEqual(s.days, ["M", "T", "W", "Th"]);
  assert.equal(s.hoursInClass, (75 * 4) / 60);   // 4 meetings of 75 minutes
  assert.equal(s.units, 6);
});

test("only live online classes: no campus days", () => {
  const s = weekStats([liveOnlineTTh(), section("CS", "577", [meet("T", "19:00", "21:40", "ONLINE", "")])]);
  assert.deepEqual(s.campusDays, []);
  assert.deepEqual(s.onlineOnlyDays, ["T", "Th"]);
  assert.ok(s.hoursInClass > 0);
});

test("in person and live online on the same day: a campus day, not online only", () => {
  const s = weekStats([inPersonMW(), section("CHIN", "102", [meet("M", "13:00", "13:50", "ONLINE", "")])]);
  assert.deepEqual(s.campusDays, ["M", "W"]);
  assert.deepEqual(s.onlineOnlyDays, []);
  // one section with both kinds of meeting on one day
  const both = weekStats([section("BA", "370", [meet("W", "9:00", "9:50"), meet("W", "11:00", "11:50", "ONLINE", "")])]);
  assert.deepEqual(both.campusDays, ["W"]);
  assert.deepEqual(both.onlineOnlyDays, []);
});

test("an online part with no day or time changes nothing", () => {
  const hybrid = section("AFRAS", "101", [meet("MW", "10:00", "10:50"), meet("", "", "", "", "", true)]);
  const plain = section("AFRAS", "101", [meet("MW", "10:00", "10:50")]);
  const a = weekStats([hybrid]);
  const b = weekStats([plain]);
  assert.deepEqual(a.campusDays, ["M", "W"]);
  assert.deepEqual(a.onlineOnlyDays, []);
  assert.equal(a.hoursInClass, b.hoursInClass);
  const onlineOnly = weekStats([section("RELS", "101", [meet("", "", "", "", "", true)])]);
  assert.deepEqual([onlineOnly.campusDays, onlineOnly.onlineOnlyDays, onlineOnly.days], [[], [], []]);
});

test("a mixed building (ONLINE / BSE) counts as a campus day", () => {
  const s = weekStats([section("CHEM", "103", [meet("F", "8:00", "10:45", "ONLINE / BSE", "")])]);
  assert.deepEqual(s.campusDays, ["F"]);
  assert.deepEqual(s.onlineOnlyDays, []);
});

test("units, gaps and hours are unchanged by the live online flag", () => {
  const mw = inPersonMW();
  const late = section("CS", "561", [meet("MW", "19:00", "20:15", "ONLINE", "")]);
  const s = weekStats([mw, late]);
  assert.equal(s.units, planUnits([mw, late]));
  assert.equal(s.longestGap, 19 * 60 - (11 * 60 + 15));
  assert.equal(s.hoursInClass, (75 * 4) / 60);
});

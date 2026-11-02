// Everything school-specific lives here, so EzClass can be pointed at another
// school by editing this one file (plus the data/ CSVs). Nothing else in the
// frontend should spell out the school, the term, or the catalog year.

export const CONFIG = Object.freeze({
  productName: "EzClass",
  schoolName: "San Diego State University",
  schoolShort: "SDSU",
  termName: "Spring 2027",
  catalogYear: "2026-27",

  // The footer line. Keep it: we are not the school and must never look like it.
  disclaimer: "EzClass is a student project, not affiliated with SDSU.",

  // Hours the week calendar always shows (it grows if a class starts earlier or ends later).
  calendarStartHour: 8,
  calendarEndHour: 18,

  // Most sections a plan can hold. Matches the server's conflict check limit.
  maxSectionsPerPlan: 60,
});

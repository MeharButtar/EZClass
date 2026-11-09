// Everything school-specific lives here, so EzClass can be pointed at another
// school by editing this one file (plus the data/ CSVs). Nothing else in the
// frontend should spell out the school, the term, or the catalog year.

// The school's id on RateMyProfessors (877 = San Diego State University),
// from ratemyprofessors.com/school/877.
const RATEMYPROFESSORS_SCHOOL_ID = 877;

export const CONFIG = Object.freeze({
  productName: "EzClass",
  schoolName: "San Diego State University",
  schoolShort: "SDSU",
  termName: "Spring 2027",
  catalogYear: "2026-27",

  // The footer line. Keep it: we are not the school and must never look like it.
  disclaimer: "EzClass is a student project, not affiliated with SDSU.",

  // Where students actually register. The site tells them to confirm every
  // class there, since our data is a copy that can go out of date.
  registrationSite: "WebPortal",

  // Where "Report a problem" links go. "" means our own Support page
  // (support.html); put a full URL here only to send reports somewhere else.
  reportProblemUrl: "",

  // Hours the week calendar always shows (it grows if a class starts earlier or ends later).
  calendarStartHour: 8,
  calendarEndHour: 18,

  // Most sections a plan can hold. Matches the server's conflict check limit.
  maxSectionsPerPlan: 60,

  // Professor names link to a RateMyProfessors search (a plain search link that
  // opens in a new tab; nothing is fetched or scraped). The search is limited to
  // the school and uses the last name, so it lists everyone at the school with
  // that last name, including profiles under a nickname ("Patty" for "Patricia").
  professorSite: "RateMyProfessors",
  professorUrl: (lastName) =>
    `https://www.ratemyprofessors.com/search/professors/${RATEMYPROFESSORS_SCHOOL_ID}?q=${encodeURIComponent(lastName)}`,
});

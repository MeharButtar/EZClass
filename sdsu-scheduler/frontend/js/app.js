// Minimal frontend logic: search sections, add to a schedule, check conflicts.
// No framework, just fetch() calls to the Flask backend. Frontend teammates
// can restructure this however they want once it's working.

const state = {
  selectedSections: new Map(), // section_id -> section object
};

async function loadSubjects() {
  const res = await fetch("/api/subjects");
  const subjects = await res.json();
  const select = document.getElementById("subject-filter");
  for (const subj of subjects) {
    const opt = document.createElement("option");
    opt.value = subj;
    opt.textContent = subj;
    select.appendChild(opt);
  }
}

function buildQueryString() {
  const params = new URLSearchParams();
  const subject = document.getElementById("subject-filter").value;
  const day = document.getElementById("day-filter").value;
  const professor = document.getElementById("professor-filter").value;
  const keyword = document.getElementById("keyword-filter").value;

  if (subject) params.set("subject", subject);
  if (day) params.set("day", day);
  if (professor) params.set("professor", professor);
  if (keyword) params.set("q", keyword);

  return params.toString();
}

async function searchSections() {
  const qs = buildQueryString();
  const res = await fetch(`/api/sections?${qs}`);
  const sections = await res.json();
  renderResults(sections);
}

// Link out to a RateMyProfessors search for this professor (no scraping,
// just a search URL that opens in a new tab).
function professorLink(name) {
  if (!name) return "TBA";
  const q = encodeURIComponent(name + " San Diego State University");
  const url = `https://www.ratemyprofessors.com/search/professors?q=${q}`;
  return `<a href="${url}" target="_blank" rel="noopener">${name}</a>`;
}

function renderResults(sections) {
  const tbody = document.getElementById("results-body");
  tbody.innerHTML = "";

  if (sections.length === 0) {
    const row = document.createElement("tr");
    row.innerHTML = `<td colspan="8" class="empty-state">No sections match those filters.</td>`;
    tbody.appendChild(row);
    return;
  }

  for (const s of sections) {
    const row = document.createElement("tr");
    const isSelected = state.selectedSections.has(s.section_id);
    row.innerHTML = `
      <td><input type="checkbox" data-section-id="${s.section_id}" ${isSelected ? "checked" : ""}></td>
      <td>${s.subject} ${s.catalog_num}</td>
      <td>${s.course_title}</td>
      <td>${s.section_number}</td>
      <td>${professorLink(s.professor_name)}</td>
      <td>${s.days}</td>
      <td>${s.start_time}-${s.end_time}</td>
      <td>${s.building ? s.building + " " + s.room_number : "TBA"}</td>
    `;
    tbody.appendChild(row);

    const checkbox = row.querySelector("input[type=checkbox]");
    checkbox.addEventListener("change", (e) => {
      if (e.target.checked) {
        state.selectedSections.set(s.section_id, s);
      } else {
        state.selectedSections.delete(s.section_id);
      }
      renderSchedule();
    });
  }
}

function renderSchedule() {
  const list = document.getElementById("schedule-list");
  list.innerHTML = "";

  if (state.selectedSections.size === 0) {
    list.innerHTML = `<li class="empty-state">No sections selected yet.</li>`;
    document.getElementById("conflict-result").textContent = "";
    document.getElementById("conflict-result").className = "";
    return;
  }

  for (const s of state.selectedSections.values()) {
    const li = document.createElement("li");
    li.innerHTML = `
      <span>${s.subject} ${s.catalog_num} (Sec ${s.section_number}) — ${s.days} ${s.start_time}-${s.end_time}</span>
      <button class="remove-btn" data-section-id="${s.section_id}">Remove</button>
    `;
    list.appendChild(li);

    li.querySelector(".remove-btn").addEventListener("click", () => {
      state.selectedSections.delete(s.section_id);
      renderSchedule();
      // uncheck the box in the results table if it's still visible
      const box = document.querySelector(`input[data-section-id="${s.section_id}"]`);
      if (box) box.checked = false;
    });
  }
}

async function checkConflicts() {
  const sectionIds = Array.from(state.selectedSections.keys());
  const res = await fetch("/api/schedule/check", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ section_ids: sectionIds }),
  });
  const data = await res.json();

  const resultDiv = document.getElementById("conflict-result");
  if (data.conflict_free) {
    resultDiv.textContent = "No conflicts. This schedule works.";
    resultDiv.className = "ok";
  } else {
    const lines = data.conflicts.map(
      (c) =>
        `${c.section_a.section_id} conflicts with ${c.section_b.section_id} (${c.section_a.days} overlap)`
    );
    resultDiv.textContent = `Conflicts found: ${lines.join("; ")}`;
    resultDiv.className = "conflict";
  }
}

document.getElementById("search-btn").addEventListener("click", searchSections);
document.getElementById("check-conflicts-btn").addEventListener("click", checkConflicts);

// initial load
loadSubjects();
searchSections();

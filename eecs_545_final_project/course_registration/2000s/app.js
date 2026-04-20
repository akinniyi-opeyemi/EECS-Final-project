const courses = [
  {
    id: "CS101",
    code: "CS 101",
    title: "Foundations of Programming",
    department: "CS",
    instructor: "Dr. Lina Park",
    days: ["Mon", "Wed"],
    start: "09:00",
    end: "10:15",
    seats: 22,
    capacity: 28,
    credits: 4,
    location: "Mercer Hall 210",
    color: "linear-gradient(135deg, #2364ff, #4bb5ff)",
  },
  {
    id: "CS215",
    code: "CS 215",
    title: "Data Structures Studio",
    department: "CS",
    instructor: "Prof. Asha Raman",
    days: ["Tue", "Thu"],
    start: "10:30",
    end: "11:45",
    seats: 4,
    capacity: 30,
    credits: 4,
    location: "Ridge Lab 120",
    color: "linear-gradient(135deg, #0f9d7a, #43c59d)",
  },
  {
    id: "CS240",
    code: "CS 240",
    title: "Computer Systems",
    department: "CS",
    instructor: "Dr. Elena Torres",
    days: ["Mon", "Wed"],
    start: "10:00",
    end: "11:15",
    seats: 7,
    capacity: 24,
    credits: 4,
    location: "North Center 315",
    color: "linear-gradient(135deg, #ff6b3d, #ff9a5b)",
  },
  {
    id: "CS275",
    code: "CS 275",
    title: "Human-Centered AI",
    department: "AI",
    instructor: "Prof. Maya Chen",
    days: ["Tue", "Thu"],
    start: "13:00",
    end: "14:15",
    seats: 12,
    capacity: 20,
    credits: 3,
    location: "Innovation Studio 04",
    color: "linear-gradient(135deg, #7d4dff, #bd76ff)",
  },
  {
    id: "CS310",
    code: "CS 310",
    title: "Algorithms",
    department: "CS",
    instructor: "Dr. Omar Siddiqui",
    days: ["Mon", "Wed"],
    start: "13:30",
    end: "14:45",
    seats: 2,
    capacity: 26,
    credits: 4,
    location: "Bishop Hall 108",
    color: "linear-gradient(135deg, #ef4444, #fb7185)",
  },
  {
    id: "CS330",
    code: "CS 330",
    title: "Database Systems",
    department: "DATA",
    instructor: "Dr. Priya Menon",
    days: ["Tue", "Thu"],
    start: "14:00",
    end: "15:15",
    seats: 0,
    capacity: 22,
    credits: 3,
    location: "Data Commons 202",
    color: "linear-gradient(135deg, #0d9488, #22c55e)",
  },
  {
    id: "CS355",
    code: "CS 355",
    title: "Computer Graphics",
    department: "CS",
    instructor: "Prof. Rowan Silva",
    days: ["Mon", "Wed"],
    start: "15:00",
    end: "16:15",
    seats: 11,
    capacity: 18,
    credits: 3,
    location: "Archer Hall 001",
    color: "linear-gradient(135deg, #f59e0b, #f97316)",
  },
  {
    id: "CS370",
    code: "CS 370",
    title: "Machine Learning Systems",
    department: "AI",
    instructor: "Dr. Theo Bennett",
    days: ["Mon", "Wed"],
    start: "15:30",
    end: "16:45",
    seats: 6,
    capacity: 24,
    credits: 4,
    location: "Kepler Center 412",
    color: "linear-gradient(135deg, #2563eb, #8b5cf6)",
  },
  {
    id: "CS398",
    code: "CS 398",
    title: "Secure Web Engineering",
    department: "CS",
    instructor: "Prof. Nadia Alvi",
    days: ["Tue", "Thu"],
    start: "18:00",
    end: "19:15",
    seats: 9,
    capacity: 16,
    credits: 3,
    location: "Mercer Hall 018",
    color: "linear-gradient(135deg, #111827, #374151)",
  },
  {
    id: "CS405",
    code: "CS 405",
    title: "Operating Systems",
    department: "CS",
    instructor: "Dr. Isabel Hart",
    days: ["Tue", "Thu"],
    start: "09:30",
    end: "10:45",
    seats: 14,
    capacity: 24,
    credits: 4,
    location: "North Center 410",
    color: "linear-gradient(135deg, #1d4ed8, #38bdf8)",
  },
  {
    id: "CS420",
    code: "CS 420",
    title: "Natural Language Processing",
    department: "AI",
    instructor: "Prof. Helen Zhou",
    days: ["Mon", "Wed"],
    start: "11:30",
    end: "12:45",
    seats: 8,
    capacity: 20,
    credits: 3,
    location: "Kepler Center 220",
    color: "linear-gradient(135deg, #8b5cf6, #ec4899)",
  },
  {
    id: "CS438",
    code: "CS 438",
    title: "Information Retrieval",
    department: "DATA",
    instructor: "Dr. Gavin Brooks",
    days: ["Tue", "Thu"],
    start: "12:30",
    end: "13:45",
    seats: 5,
    capacity: 18,
    credits: 3,
    location: "Data Commons 118",
    color: "linear-gradient(135deg, #0891b2, #22c55e)",
  },
  {
    id: "CS452",
    code: "CS 452",
    title: "Distributed Systems",
    department: "CS",
    instructor: "Prof. Marcus Lee",
    days: ["Mon", "Wed"],
    start: "17:00",
    end: "18:15",
    seats: 3,
    capacity: 20,
    credits: 4,
    location: "Bishop Hall 302",
    color: "linear-gradient(135deg, #f97316, #fb7185)",
  },
  {
    id: "CS467",
    code: "CS 467",
    title: "Computer Vision",
    department: "AI",
    instructor: "Dr. Sara Velasquez",
    days: ["Tue", "Thu"],
    start: "15:30",
    end: "16:45",
    seats: 10,
    capacity: 22,
    credits: 4,
    location: "Innovation Studio 12",
    color: "linear-gradient(135deg, #7c3aed, #2563eb)",
  },
  {
    id: "CS480",
    code: "CS 480",
    title: "Advanced Software Engineering",
    department: "CS",
    instructor: "Prof. Daniel Kim",
    days: ["Fri"],
    start: "10:00",
    end: "12:30",
    seats: 16,
    capacity: 25,
    credits: 3,
    location: "Mercer Hall 340",
    color: "linear-gradient(135deg, #0f766e, #14b8a6)",
  },
];

const state = {
  department: "all",
  time: "all",
  search: "",
  selectedIds: ["CS310", "CS355", "CS370"],
  activeCourseId: "CS310",
  detailMode: "ops",
};

const els = {
  departmentFilter: document.querySelector("#department-filter"),
  timeFilter: document.querySelector("#time-filter"),
  searchFilter: document.querySelector("#search-filter"),
  resetFilters: document.querySelector("#reset-filters"),
  courseTableBody: document.querySelector("#course-table-body"),
  visibleCourseCount: document.querySelector("#visible-course-count"),
  cartCount: document.querySelector("#cart-count"),
  detailCourseName: document.querySelector("#detail-course-name"),
  detailCourseMeta: document.querySelector("#detail-course-meta"),
  detailPanel: document.querySelector("#detail-panel"),
  openCourseCount: document.querySelector("#open-course-count"),
  selectedCreditCount: document.querySelector("#selected-credit-count"),
  warningCount: document.querySelector("#warning-count"),
  detailTabs: Array.from(document.querySelectorAll(".detail-tab")),
};

const days = ["Mon", "Tue", "Wed", "Thu", "Fri"];

function init() {
  renderDepartmentOptions();
  bindEvents();
  render();
}

function renderDepartmentOptions() {
  const departments = ["all", ...new Set(courses.map((course) => course.department))];
  els.departmentFilter.innerHTML = departments
    .map(
      (department) =>
        `<option value="${department}">${
          department === "all" ? "ALL" : department
        }</option>`
    )
    .join("");
}

function bindEvents() {
  els.departmentFilter.addEventListener("change", (event) => {
    state.department = event.target.value;
    render();
  });

  els.timeFilter.addEventListener("change", (event) => {
    state.time = event.target.value;
    render();
  });

  els.searchFilter.addEventListener("input", (event) => {
    state.search = event.target.value.trim().toLowerCase();
    render();
  });

  els.resetFilters.addEventListener("click", () => {
    state.department = "all";
    state.time = "all";
    state.search = "";
    els.departmentFilter.value = "all";
    els.timeFilter.value = "all";
    els.searchFilter.value = "";
    render();
  });

  els.courseTableBody.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-course-id]");
    if (button) {
      loadCourse(button.dataset.courseId);
      return;
    }

    const row = event.target.closest("tr[data-course-id]");
    if (row) {
      loadCourse(row.dataset.courseId);
    }
  });

  els.detailPanel.addEventListener("click", (event) => {
    const button = event.target.closest("button[data-course-id]");
    if (!button) return;
    if (button.dataset.action === "toggle") {
      toggleCourse(button.dataset.courseId);
    } else if (button.dataset.action === "inspect") {
      loadCourse(button.dataset.courseId);
    }
  });

  els.detailTabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      state.detailMode = tab.dataset.mode;
      render();
    });
  });
}

function render() {
  const filteredCourses = getFilteredCourses();
  const selectedCourses = getSelectedCourses();
  const warnings = getWarnings(selectedCourses);

  renderMetrics(selectedCourses, warnings);
  renderCourseTable(filteredCourses);
  renderDetailConsole(selectedCourses, warnings);
}

function getFilteredCourses() {
  return courses.filter((course) => {
    const departmentMatch =
      state.department === "all" || course.department === state.department;
    const timeMatch = matchesTimeFilter(course, state.time);
    const searchMatch =
      state.search === "" ||
      `${course.code} ${course.title} ${course.instructor}`.toLowerCase().includes(state.search);

    return departmentMatch && timeMatch && searchMatch;
  });
}

function matchesTimeFilter(course, filter) {
  if (filter === "all") return true;
  const startMinutes = timeToMinutes(course.start);

  if (filter === "morning") return startMinutes < 10 * 60;
  if (filter === "midday") return startMinutes >= 10 * 60 && startMinutes < 13 * 60;
  if (filter === "afternoon") return startMinutes >= 13 * 60 && startMinutes < 17 * 60;
  return startMinutes >= 17 * 60;
}

function getSelectedCourses() {
  return courses.filter((course) => state.selectedIds.includes(course.id));
}

function renderMetrics(selectedCourses, warnings) {
  els.openCourseCount.textContent = courses.filter((course) => course.seats > 0).length;
  els.selectedCreditCount.textContent = selectedCourses.reduce(
    (sum, course) => sum + course.credits,
    0
  );
  els.warningCount.textContent = warnings.length;
}

function renderCourseTable(filteredCourses) {
  els.visibleCourseCount.textContent = `${filteredCourses.length} REC`;

  if (!filteredCourses.length) {
    els.courseTableBody.innerHTML = `
      <tr>
        <td colspan="7"><div class="empty-state">NO MATCHING SECTIONS FOUND.</div></td>
      </tr>
    `;
    return;
  }

  els.courseTableBody.innerHTML = filteredCourses
    .map((course) => {
      const isSelected = state.selectedIds.includes(course.id);
      return `
        <tr class="course-row ${course.id === state.activeCourseId ? "is-active" : ""}" data-course-id="${
          course.id
        }">
          <td>
            <div class="crn-title">${course.code} :: ${course.title}</div>
            <div class="subtle">${course.location}</div>
          </td>
          <td>${course.department}</td>
          <td>
            ${formatDays(course.days)}
            <div class="subtle">${formatTimeRange(course.start, course.end)}</div>
          </td>
          <td>${course.instructor}</td>
          <td class="${seatClass(course)}">${course.seats}/${course.capacity}</td>
          <td>${course.credits}</td>
          <td><button class="row-button" data-course-id="${course.id}" type="button">OPEN</button></td>
        </tr>
      `;
    })
    .join("");
}

function renderDetailConsole(selectedCourses, warnings) {
  const activeCourse = courses.find((course) => course.id === state.activeCourseId) || courses[0];
  if (!activeCourse) return;

  els.detailCourseName.textContent = `${activeCourse.code} :: ${activeCourse.title}`;
  els.detailCourseMeta.textContent =
    `${activeCourse.department} | ${formatDays(activeCourse.days)} | ${formatTimeRange(
      activeCourse.start,
      activeCourse.end
    )} | ${activeCourse.instructor}`;
  els.cartCount.textContent = `${selectedCourses.length} SEL`;
  els.detailTabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.mode === state.detailMode);
  });

  if (state.detailMode === "ops") {
    renderOpsPanel(activeCourse, selectedCourses);
    return;
  }

  if (state.detailMode === "alerts") {
    renderAlertPanel(activeCourse, selectedCourses, warnings);
    return;
  }

  renderWeekPanel(activeCourse, selectedCourses);
}

function renderOpsPanel(activeCourse, selectedCourses) {
  const isSelected = state.selectedIds.includes(activeCourse.id);
  const isFull = activeCourse.seats === 0;
  const queueHtml = selectedCourses.length
    ? selectedCourses
        .map(
          (course) => `
            <div class="queue-item">
              <div class="queue-head">
                <span class="queue-code">${course.code}</span>
                <span class="queue-op">${course.id === activeCourse.id ? "LOADED" : "IN Q"}</span>
              </div>
              <div>${course.title}</div>
              <div class="subtle">${formatDays(course.days)} ${formatTimeRange(
                course.start,
                course.end
              )}</div>
              <div class="subtle">
                <button class="queue-button" data-action="inspect" data-course-id="${course.id}" type="button">LOAD</button>
              </div>
            </div>
          `
        )
        .join("")
    : '<div class="empty-state">QUEUE EMPTY. NO REGISTERED ITEMS.</div>';

  els.detailPanel.innerHTML = `
    <div class="ops-grid">
      <div class="ops-box">
        <div class="mini-label">PRIMARY ACTION</div>
        <div class="subtle">Seat state: ${activeCourse.seats}/${activeCourse.capacity}</div>
        <div class="subtle">Credits: ${activeCourse.credits}</div>
        <div style="margin-top: 6px;">
          <button
            class="queue-button"
            data-action="toggle"
            data-course-id="${activeCourse.id}"
            type="button"
            ${isFull && !isSelected ? "disabled" : ""}
          >
            ${isSelected ? "DROP LOADED COURSE" : isFull ? "SECTION FULL" : "ADD LOADED COURSE"}
          </button>
        </div>
      </div>
      <div class="ops-box">
        <div class="mini-label">CURRENT QUEUE</div>
        ${queueHtml}
      </div>
    </div>
  `;
}

function renderAlertPanel(activeCourse, selectedCourses, warnings) {
  const activeAlerts = getCourseAlerts(activeCourse, selectedCourses, warnings);
  if (!activeAlerts.length) {
    els.detailPanel.innerHTML =
      '<div class="empty-state">NO ACTIVE ALERTS FOR LOADED COURSE.</div>';
    return;
  }

  els.detailPanel.innerHTML = activeAlerts
    .map(
      (warning, index) => `
        <div class="warning-item ${warning.type}">
          <div class="warning-code">MSG-${index + 1} / ${
            warning.type === "conflict" ? "CNFL" : "SEAT"
          }</div>
          <div><strong>${warning.title}</strong></div>
          <div class="subtle">${warning.detail}</div>
        </div>
      `
    )
    .join("");
}

function renderWeekPanel(activeCourse, selectedCourses) {
  const rows = days.map((day) => {
    const coursesForDay = selectedCourses
      .filter((course) => course.days.includes(day))
      .sort((a, b) => timeToMinutes(a.start) - timeToMinutes(b.start));

    if (!coursesForDay.length) {
      return `
        <tr>
          <td>${day}</td>
          <td>NONE</td>
        </tr>
      `;
    }

    return `
      <tr>
        <td>${day}</td>
        <td>${coursesForDay
          .map(
            (course) =>
              `${course.code} ${formatTimeRange(course.start, course.end)} ${course.title}`
          )
          .join("<br />")}</td>
      </tr>
    `;
  });

  els.detailPanel.innerHTML = `
    <div class="ops-box">
      <div class="mini-label">LOADED COURSE WINDOW</div>
      <div>${activeCourse.code} ${formatDays(activeCourse.days)} ${formatTimeRange(
        activeCourse.start,
        activeCourse.end
      )}</div>
      <div class="subtle">${activeCourse.title}</div>
    </div>
    <table class="schedule-table" cellspacing="0" cellpadding="0">
      <thead>
        <tr>
          <th>DAY</th>
          <th>REGISTERED ITEMS</th>
        </tr>
      </thead>
      <tbody>${rows.join("")}</tbody>
    </table>
  `;
}

function getWarnings(selectedCourses) {
  const warnings = [];

  for (const course of selectedCourses) {
    if (course.seats <= 4) {
      warnings.push({
        type: "notice",
        title: `${course.code} LOW SEAT AVAILABILITY`,
        detail: `${course.seats} seat${course.seats === 1 ? "" : "s"} remaining in ${
          course.title
        }.`,
      });
    }
  }

  for (let i = 0; i < selectedCourses.length; i += 1) {
    for (let j = i + 1; j < selectedCourses.length; j += 1) {
      if (coursesConflict(selectedCourses[i], selectedCourses[j])) {
        warnings.push({
          type: "conflict",
          title: "TIME CONFLICT DETECTED",
          detail: `${selectedCourses[i].code} overlaps with ${selectedCourses[j].code}.`,
        });
      }
    }
  }

  return warnings;
}

function coursesConflict(courseA, courseB) {
  const sharedDay = courseA.days.some((day) => courseB.days.includes(day));
  if (!sharedDay) return false;

  const aStart = timeToMinutes(courseA.start);
  const aEnd = timeToMinutes(courseA.end);
  const bStart = timeToMinutes(courseB.start);
  const bEnd = timeToMinutes(courseB.end);

  return aStart < bEnd && bStart < aEnd;
}

function toggleCourse(courseId) {
  if (state.selectedIds.includes(courseId)) {
    state.selectedIds = state.selectedIds.filter((id) => id !== courseId);
  } else {
    state.selectedIds = [...state.selectedIds, courseId];
  }

  render();
}

function loadCourse(courseId) {
  state.activeCourseId = courseId;
  render();
}

function getCourseAlerts(activeCourse, selectedCourses, warnings) {
  return warnings.filter((warning) => {
    if (warning.detail.includes(activeCourse.code) || warning.title.includes(activeCourse.code)) {
      return true;
    }

    return false;
  });
}

function seatClass(course) {
  if (course.seats === 0) return "seat-full";
  if (course.seats <= 4) return "seat-low";
  return "seat-ok";
}

function formatDays(courseDays) {
  return courseDays.join(" / ");
}

function formatTimeRange(start, end) {
  return `${formatSingleTime(start)} - ${formatSingleTime(end)}`;
}

function formatSingleTime(value) {
  const [hoursText, minutes] = value.split(":");
  const hours = Number(hoursText);
  const suffix = hours >= 12 ? "PM" : "AM";
  const twelveHour = hours % 12 === 0 ? 12 : hours % 12;
  return `${twelveHour}:${minutes} ${suffix}`;
}

function timeToMinutes(value) {
  const [hours, minutes] = value.split(":").map(Number);
  return hours * 60 + minutes;
}

init();

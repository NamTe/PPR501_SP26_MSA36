const API_BASE = "/v1/api";

const form = document.getElementById("student-form");
const rows = document.getElementById("student-rows");
const searchInput = document.getElementById("search-input");
const refreshBtn = document.getElementById("refresh-btn");
const cancelBtn = document.getElementById("cancel-btn");
const toast = document.getElementById("toast");
const formTitle = document.getElementById("form-title");
const formSubtitle = document.getElementById("form-subtitle");

const statTotal = document.getElementById("stat-total");
const statMath = document.getElementById("stat-math");
const statLiterature = document.getElementById("stat-literature");
const statEnglish = document.getElementById("stat-english");

const state = {
  students: [],
  editingId: null,
};

const request = async (path, options = {}) => {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
    },
    ...options,
  });

  if (!response.ok) {
    let detail = "Request failed";
    try {
      const payload = await response.json();
      if (payload && payload.detail) {
        detail = payload.detail;
      }
    } catch (error) {
      detail = response.statusText || detail;
    }
    throw new Error(detail);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
};

const showToast = (message, tone = "dark") => {
  toast.textContent = message;
  toast.classList.add("show");
  toast.style.background = tone === "error" ? "#291914" : "#1e1e24";
  window.clearTimeout(showToast._timer);
  showToast._timer = window.setTimeout(() => {
    toast.classList.remove("show");
  }, 2500);
};

const normalizeScore = (value) => {
  if (value === "" || value === null || value === undefined) {
    return null;
  }
  const parsed = Number(value);
  return Number.isNaN(parsed) ? null : parsed;
};

const formatScore = (value) => {
  if (value === null || value === undefined) {
    return "-";
  }
  return Number(value).toFixed(1);
};

const formatDate = (value) => {
  if (!value) {
    return "-";
  }
  return value;
};

const updateStats = () => {
  const total = state.students.length;
  const average = (field) => {
    const valid = state.students.map((student) => student[field]).filter((score) => score !== null);
    if (!valid.length) {
      return "0.0";
    }
    const sum = valid.reduce((acc, score) => acc + Number(score), 0);
    return (sum / valid.length).toFixed(1);
  };

  statTotal.textContent = total;
  statMath.textContent = average("math_score");
  statLiterature.textContent = average("literature_score");
  statEnglish.textContent = average("english_score");
};

const renderTable = () => {
  const query = searchInput.value.trim().toLowerCase();
  const filtered = state.students.filter((student) => {
    if (!query) {
      return true;
    }
    const target = `${student.first_name} ${student.last_name} ${student.email} ${student.home_town}`.toLowerCase();
    return target.includes(query);
  });

  if (!filtered.length) {
    rows.innerHTML = `<tr><td colspan="9" class="empty">No students found.</td></tr>`;
    return;
  }

  rows.innerHTML = filtered
    .map(
      (student) => `
        <tr data-id="${student.student_id}">
          <td><span class="badge">${student.student_id}</span></td>
          <td>${student.first_name} ${student.last_name}</td>
          <td>${student.email}</td>
          <td>${formatDate(student.date_of_birth)}</td>
          <td>${student.home_town}</td>
          <td>${formatScore(student.math_score)}</td>
          <td>${formatScore(student.literature_score)}</td>
          <td>${formatScore(student.english_score)}</td>
          <td class="actions">
            <button class="secondary" data-action="edit" type="button">Edit</button>
            <button class="ghost" data-action="delete" type="button">Delete</button>
          </td>
        </tr>
      `
    )
    .join("");
};

const loadStudents = async () => {
  rows.innerHTML = `<tr><td colspan="9" class="empty">Loading students...</td></tr>`;
  try {
    state.students = await request("/students");
    updateStats();
    renderTable();
  } catch (error) {
    rows.innerHTML = `<tr><td colspan="9" class="empty">Failed to load students.</td></tr>`;
    showToast(error.message, "error");
  }
};

const getFormPayload = () => {
  const formData = new FormData(form);
  return {
    first_name: formData.get("first_name").trim(),
    last_name: formData.get("last_name").trim(),
    email: formData.get("email").trim(),
    date_of_birth: formData.get("date_of_birth"),
    home_town: formData.get("home_town").trim(),
    math_score: normalizeScore(formData.get("math_score")),
    literature_score: normalizeScore(formData.get("literature_score")),
    english_score: normalizeScore(formData.get("english_score")),
  };
};

const setFormValues = (student) => {
  form.first_name.value = student.first_name;
  form.last_name.value = student.last_name;
  form.email.value = student.email;
  form.date_of_birth.value = student.date_of_birth;
  form.home_town.value = student.home_town;
  form.math_score.value = student.math_score ?? "";
  form.literature_score.value = student.literature_score ?? "";
  form.english_score.value = student.english_score ?? "";
};

const resetForm = () => {
  state.editingId = null;
  form.reset();
  formTitle.textContent = "Add Student";
  formSubtitle.textContent = "Create a new record.";
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = getFormPayload();

  try {
    if (state.editingId) {
      await request(`/students/${state.editingId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      showToast("Student updated.");
    } else {
      await request("/students", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      showToast("Student created.");
    }
    resetForm();
    await loadStudents();
  } catch (error) {
    showToast(error.message, "error");
  }
});

rows.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button) {
    return;
  }
  const action = button.dataset.action;
  const row = button.closest("tr");
  if (!row) {
    return;
  }
  const studentId = row.dataset.id;
  const student = state.students.find((item) => item.student_id === studentId);

  if (action === "edit" && student) {
    state.editingId = studentId;
    setFormValues(student);
    formTitle.textContent = "Edit Student";
    formSubtitle.textContent = `Updating ${student.first_name} ${student.last_name}.`;
    formTitle.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  if (action === "delete") {
    const confirmed = window.confirm("Delete this student record?");
    if (!confirmed) {
      return;
    }
    try {
      await request(`/students/${studentId}`, { method: "DELETE" });
      showToast("Student deleted.");
      await loadStudents();
    } catch (error) {
      showToast(error.message, "error");
    }
  }
});

searchInput.addEventListener("input", renderTable);
refreshBtn.addEventListener("click", loadStudents);
cancelBtn.addEventListener("click", resetForm);

loadStudents();

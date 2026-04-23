function createApiFetch() {
  const sharedAuth = window.BrainBoostAuth || {};
  if (typeof sharedAuth.apiFetch === "function") {
    return sharedAuth.apiFetch;
  }

  return async function fallbackApiFetch(url, options = {}) {
    const token = localStorage.getItem("brainboost_token");
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401 && !window.location.pathname.includes("login")) {
      window.location.href = "/login";
    }
    return response;
  };
}

const dashboardApiFetch = createApiFetch();
let dailyChart;
let weeklyChart;
let monthlyChart;

function renderEmptyList(host, message) {
  host.innerHTML = "";
  const empty = document.createElement("div");
  empty.className = "list-item";
  empty.textContent = message;
  host.appendChild(empty);
}

function renderChart(canvasId, label, labels, values, existingChart) {
  if (!window.Chart) {
    return existingChart;
  }
  if (existingChart) {
    existingChart.destroy();
  }
  const ctx = document.getElementById(canvasId);
  return new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label,
          data: values,
          borderColor: "#ff5f5f",
          backgroundColor: "rgba(255, 95, 95, 0.18)",
          fill: true,
          tension: 0.35,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true },
      },
    },
  });
}

async function refreshOverview() {
  const response = await dashboardApiFetch("/analytics/overview");
  if (!response.ok) return;
  const data = await response.json();
  document.getElementById("totalSessions").textContent = data.total_sessions;
  document.getElementById("totalMinutes").textContent = data.total_minutes;
  document.getElementById("streakDays").textContent = data.current_streak_days;
  document.getElementById("dueRevisions").textContent = data.due_revisions;
}

async function refreshSessions() {
  const response = await dashboardApiFetch("/sessions/?limit=12");
  const host = document.getElementById("sessionList");
  if (!response.ok) {
    renderEmptyList(host, "Unable to load sessions right now.");
    return;
  }
  const sessions = await response.json();
  host.innerHTML = "";
  if (!sessions.length) {
    renderEmptyList(host, "No study sessions yet.");
    return;
  }
  for (const session of sessions) {
    const item = document.createElement("div");
    item.className = "list-item";
    const title = document.createElement("strong");
    title.textContent = session.subject;
    item.append(
      title,
      ` - ${session.topic}`,
      document.createElement("br"),
      `${session.duration_minutes} min on ${session.session_date}`
    );
    host.appendChild(item);
  }
}

async function refreshRevisionItems() {
  const response = await dashboardApiFetch("/revisions/");
  const host = document.getElementById("revisionList");
  if (!response.ok) {
    renderEmptyList(host, "Unable to load revision items right now.");
    return;
  }

  const items = (await response.json()).slice(0, 12);
  host.innerHTML = "";
  if (!items.length) {
    renderEmptyList(host, "No revision items yet.");
    return;
  }

  for (const item of items) {
    const node = document.createElement("div");
    node.className = "list-item";
    const title = document.createElement("strong");
    title.textContent = item.topic;
    node.append(
      title,
      document.createElement("br"),
      `Next review: ${item.next_review_date}`,
      document.createElement("br"),
      `Confidence: ${item.confidence_level}`
    );
    host.appendChild(node);
  }
}

async function refreshCharts() {
  const [dailyRes, weeklyRes, monthlyRes] = await Promise.all([
    dashboardApiFetch("/analytics/daily?days=14"),
    dashboardApiFetch("/analytics/weekly?weeks=10"),
    dashboardApiFetch("/analytics/monthly?months=6"),
  ]);

  if (dailyRes.ok) {
    const data = await dailyRes.json();
    dailyChart = renderChart(
      "dailyChart",
      "Minutes",
      data.map((x) => x.bucket),
      data.map((x) => x.total_minutes),
      dailyChart
    );
  }

  if (weeklyRes.ok) {
    const data = await weeklyRes.json();
    weeklyChart = renderChart(
      "weeklyChart",
      "Minutes",
      data.map((x) => x.bucket),
      data.map((x) => x.total_minutes),
      weeklyChart
    );
  }

  if (monthlyRes.ok) {
    const data = await monthlyRes.json();
    monthlyChart = renderChart(
      "monthlyChart",
      "Minutes",
      data.map((x) => x.bucket),
      data.map((x) => x.total_minutes),
      monthlyChart
    );
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const studyForm = document.getElementById("studyForm");
  if (studyForm) {
    const sessionDateInput = studyForm.querySelector('[name="session_date"]');
    if (sessionDateInput) {
      sessionDateInput.value = new Date().toISOString().slice(0, 10);
    }

    studyForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const formData = new FormData(studyForm);
      const payload = {
        subject: formData.get("subject"),
        topic: formData.get("topic"),
        duration_minutes: Number(formData.get("duration_minutes")),
        session_date: formData.get("session_date"),
        notes: formData.get("notes") || null,
      };

      const response = await dashboardApiFetch("/sessions/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      const message = document.getElementById("studyMessage");
      message.textContent = response.ok ? "Session saved." : "Could not save session.";
      if (response.ok) {
        studyForm.reset();
        if (sessionDateInput) {
          sessionDateInput.value = new Date().toISOString().slice(0, 10);
        }
        await Promise.all([refreshOverview(), refreshSessions(), refreshRevisionItems(), refreshCharts()]);
      }
    });
  }

  const questionForm = document.getElementById("questionForm");
  if (questionForm) {
    questionForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const formData = new FormData(questionForm);
      const payload = {
        topic: formData.get("topic"),
        difficulty: formData.get("difficulty"),
        count: Number(formData.get("count")),
      };
      const output = document.getElementById("aiOutput");
      output.textContent = "Generating...";

      const response = await dashboardApiFetch("/practice/generate", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        output.textContent = "Unable to generate questions right now.";
        return;
      }
      const questions = await response.json();
      output.textContent = questions
        .map((item, index) => {
          const options = item.options.map((option) => `  - ${option}`).join("\n");
          return `${index + 1}. ${item.question}\n${options}\nAnswer: ${item.answer}\nExplanation: ${item.explanation}`;
        })
        .join("\n\n");
    });
  }

  Promise.all([refreshOverview(), refreshSessions(), refreshRevisionItems(), refreshCharts()]);
});

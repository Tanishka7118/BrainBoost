const { apiFetch } = window.BrainBoostAuth;
let dailyChart;
let weeklyChart;
let monthlyChart;

function renderChart(canvasId, label, labels, values, existingChart) {
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
          borderColor: "#ff6a3d",
          backgroundColor: "rgba(255, 106, 61, 0.18)",
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
  const response = await apiFetch("/api/study/analytics/overview");
  if (!response.ok) return;
  const data = await response.json();
  document.getElementById("totalSessions").textContent = data.total_sessions;
  document.getElementById("totalMinutes").textContent = data.total_minutes;
  document.getElementById("streakDays").textContent = data.current_streak_days;
  document.getElementById("dueRevisions").textContent = data.due_revisions;
}

async function refreshSessions() {
  const response = await apiFetch("/api/study/sessions?limit=12");
  if (!response.ok) return;
  const sessions = await response.json();
  const host = document.getElementById("sessionList");
  host.innerHTML = "";
  for (const session of sessions) {
    const item = document.createElement("div");
    item.className = "list-item";
    item.innerHTML = `<strong>${session.subject}</strong> - ${session.topic}<br>${session.duration_minutes} min on ${session.session_date}`;
    host.appendChild(item);
  }
}

async function refreshCharts() {
  const [dailyRes, weeklyRes, monthlyRes] = await Promise.all([
    apiFetch("/api/study/analytics/daily?days=14"),
    apiFetch("/api/study/analytics/weekly?weeks=10"),
    apiFetch("/api/study/analytics/monthly?months=6"),
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

const studyForm = document.getElementById("studyForm");
studyForm.session_date.value = new Date().toISOString().slice(0, 10);
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

  const response = await apiFetch("/api/study/sessions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  const message = document.getElementById("studyMessage");
  message.textContent = response.ok ? "Session saved." : "Could not save session.";
  if (response.ok) {
    studyForm.reset();
    studyForm.session_date.value = new Date().toISOString().slice(0, 10);
    await Promise.all([refreshOverview(), refreshSessions(), refreshCharts()]);
  }
});

const questionForm = document.getElementById("questionForm");
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

  const response = await apiFetch("/api/ai/generate-questions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    output.textContent = "Unable to generate questions right now.";
    return;
  }
  const data = await response.json();
  output.textContent = data.content;
});

Promise.all([refreshOverview(), refreshSessions(), refreshCharts()]);

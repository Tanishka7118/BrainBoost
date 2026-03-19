const { apiFetch } = window.BrainBoostAuth;

async function loadDueRevisions() {
  const response = await apiFetch("/api/revision/items?due_only=true");
  if (!response.ok) return;
  const items = await response.json();
  const host = document.getElementById("dueList");
  host.innerHTML = "";

  for (const item of items) {
    const node = document.createElement("div");
    node.className = "list-item";
    node.innerHTML = `
      <strong>${item.topic}</strong><br>
      Next review: ${item.next_review_date}<br>
      Confidence: ${item.confidence_level}
      <div style="margin-top:8px">
        <button class="button" data-review-id="${item.id}" type="button">Mark Reviewed</button>
      </div>
    `;
    host.appendChild(node);
  }

  host.querySelectorAll("[data-review-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      const payload = {
        confidence_level: 4,
        interval_days: 3,
        notes: "Reviewed from dashboard",
      };
      const res = await apiFetch(`/api/revision/items/${button.dataset.reviewId}/review`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        await loadDueRevisions();
      }
    });
  });
}

const revisionForm = document.getElementById("revisionForm");
revisionForm.next_review_date.value = new Date().toISOString().slice(0, 10);
revisionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(revisionForm);
  const payload = {
    topic: formData.get("topic"),
    confidence_level: Number(formData.get("confidence_level")),
    next_review_date: formData.get("next_review_date"),
    notes: formData.get("notes") || null,
  };

  const response = await apiFetch("/api/revision/items", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  const message = document.getElementById("revisionMessage");
  message.textContent = response.ok ? "Revision item created." : "Failed to create item.";
  if (response.ok) {
    revisionForm.reset();
    revisionForm.next_review_date.value = new Date().toISOString().slice(0, 10);
    await loadDueRevisions();
  }
});

const explainForm = document.getElementById("explainForm");
explainForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(explainForm);
  const payload = {
    question: formData.get("question"),
    answer: formData.get("answer"),
  };

  const output = document.getElementById("explainOutput");
  output.textContent = "Generating explanation...";

  const response = await apiFetch("/api/ai/explain", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    output.textContent = "Unable to generate explanation right now.";
    return;
  }

  const data = await response.json();
  output.textContent = data.content;
});

loadDueRevisions();

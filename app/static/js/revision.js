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

const revisionApiFetch = createApiFetch();

async function loadRevisionItems() {
  const response = await revisionApiFetch("/revisions/");
  if (!response.ok) return;
  const items = await response.json();
  const host = document.getElementById("dueList");
  host.innerHTML = "";

  for (const item of items) {
    const node = document.createElement("div");
    node.className = "list-item";
    const title = document.createElement("strong");
    title.textContent = item.topic;
    const button = document.createElement("button");
    button.className = "button";
    button.dataset.reviewId = item.id;
    button.type = "button";
    button.textContent = "Mark Reviewed";
    const actions = document.createElement("div");
    actions.className = "inline-actions";
    actions.appendChild(button);
    node.append(
      title,
      document.createElement("br"),
      `Next review: ${item.next_review_date}`,
      document.createElement("br"),
      `Confidence: ${item.confidence_level}`,
      actions
    );
    host.appendChild(node);
  }

  host.querySelectorAll("[data-review-id]").forEach((button) => {
    button.addEventListener("click", async () => {
      const payload = {
        confidence_level: 4,
        notes: "Reviewed from dashboard",
      };
      const res = await revisionApiFetch(`/revisions/${button.dataset.reviewId}/review`, {
        method: "POST",
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        await loadRevisionItems();
      }
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const revisionForm = document.getElementById("revisionForm");
  if (revisionForm) {
    revisionForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const formData = new FormData(revisionForm);
      const payload = {
        topic: formData.get("topic"),
        confidence_level: Number(formData.get("confidence_level")),
        notes: formData.get("notes") || null,
      };

      const response = await revisionApiFetch("/revisions/", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      const message = document.getElementById("revisionMessage");
      if (response.ok) {
        const saved = await response.json();
        message.textContent = `Revision item created. Next review: ${saved.next_review_date}.`;
      } else {
        message.textContent = "Failed to create item.";
      }
      if (response.ok) {
        revisionForm.reset();
        await loadRevisionItems();
      }
    });
  }

  const explainForm = document.getElementById("explainForm");
  if (explainForm) {
    explainForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      const formData = new FormData(explainForm);
      const payload = {
        question: formData.get("question"),
        answer: formData.get("answer"),
      };

      const output = document.getElementById("explainOutput");
      output.textContent = "Generating explanation...";

      const response = await revisionApiFetch("/explain", {
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
  }

  loadRevisionItems();
});

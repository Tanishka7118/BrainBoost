const TOKEN_KEY = "brainboost_token";

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function authHeaders() {
  const token = getToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function apiFetch(url, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
    ...authHeaders(),
  };
  const response = await fetch(url, { ...options, headers });
  if (response.status === 401) {
    clearToken();
    if (!window.location.pathname.includes("login")) {
      window.location.href = "/login";
    }
  }
  return response;
}

const logoutBtn = document.getElementById("logoutBtn");
if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    clearToken();
    window.location.href = "/login";
  });
}

const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(loginForm);

    const body = new URLSearchParams();
    body.append("username", formData.get("email"));
    body.append("password", formData.get("password"));

    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });

    const message = document.getElementById("loginMessage");
    if (!response.ok) {
      message.textContent = "Login failed. Check your credentials.";
      return;
    }

    const data = await response.json();
    saveToken(data.access_token);
    window.location.href = "/dashboard";
  });
}

const registerForm = document.getElementById("registerForm");
if (registerForm) {
  registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(registerForm);

    const payload = {
      name: formData.get("name"),
      email: formData.get("email"),
      password: formData.get("password"),
    };

    const response = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const message = document.getElementById("registerMessage");
    if (!response.ok) {
      message.textContent = "Registration failed. Try another email.";
      return;
    }

    message.textContent = "Registration successful. Redirecting to login...";
    setTimeout(() => {
      window.location.href = "/login";
    }, 700);
  });
}

if (
  window.location.pathname.includes("dashboard") ||
  window.location.pathname.includes("revision")
) {
  if (!getToken()) {
    window.location.href = "/login";
  }
}

window.BrainBoostAuth = {
  apiFetch,
};

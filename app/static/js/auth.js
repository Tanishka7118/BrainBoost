const TOKEN_KEY = "brainboost_token";
const USER_NAME_KEY = "brainboost_user_name";
const PENDING_NAME_KEY = "brainboost_pending_name";
const PENDING_EMAIL_KEY = "brainboost_pending_email";

function saveToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function saveUserName(name) {
  if (!name) {
    return;
  }
  localStorage.setItem(USER_NAME_KEY, name);
}

function getUserName() {
  return localStorage.getItem(USER_NAME_KEY);
}

function clearUserName() {
  localStorage.removeItem(USER_NAME_KEY);
}

function savePendingRegistration(name, email) {
  if (name) {
    localStorage.setItem(PENDING_NAME_KEY, name);
  }
  if (email) {
    localStorage.setItem(PENDING_EMAIL_KEY, String(email).toLowerCase());
  }
}

function consumePendingRegistration(email) {
  const pendingEmail = localStorage.getItem(PENDING_EMAIL_KEY);
  const pendingName = localStorage.getItem(PENDING_NAME_KEY);
  if (!pendingEmail || !pendingName || pendingEmail !== String(email || "").toLowerCase()) {
    return null;
  }
  localStorage.removeItem(PENDING_EMAIL_KEY);
  localStorage.removeItem(PENDING_NAME_KEY);
  return pendingName;
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
    clearUserName();
    localStorage.removeItem(PENDING_NAME_KEY);
    localStorage.removeItem(PENDING_EMAIL_KEY);
    window.location.href = "/login";
  });
}

const profileTrigger = document.getElementById("profileTrigger");
const profileDropdown = document.getElementById("profileDropdown");
const profileName = document.getElementById("profileName");

if (profileTrigger && profileDropdown) {
  profileTrigger.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    const isOpen = !profileDropdown.hidden;
    profileDropdown.hidden = isOpen;
    profileTrigger.setAttribute("aria-expanded", String(!isOpen));
  });

  document.addEventListener("pointerdown", (event) => {
    const menuRoot = document.getElementById("profileMenu");
    if (!menuRoot || menuRoot.contains(event.target)) {
      return;
    }
    profileDropdown.hidden = true;
    profileTrigger.setAttribute("aria-expanded", "false");
  });
}

async function loadProfileName() {
  const onProtectedPage =
    window.location.pathname.includes("dashboard") ||
    window.location.pathname.includes("revision");
  if (!onProtectedPage || !getToken() || !profileName) {
    return;
  }

  const cachedName = getUserName();
  if (cachedName) {
    profileName.textContent = cachedName;
  }

  try {
    let response = await apiFetch("/auth/me", { method: "GET" });
    if (!response.ok) {
      response = await apiFetch("/api/auth/me", { method: "GET" });
    }
    if (!response.ok) {
      return;
    }
    const user = await response.json();
    if (user?.name) {
      saveUserName(user.name);
      profileName.textContent = user.name;
    }
  } catch {
    // Keep default name on fetch failures.
  }
}

const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(loginForm);

    const body = new URLSearchParams();
    body.append("username", formData.get("email"));
    body.append("password", formData.get("password"));

    const response = await fetch("/auth/login", {
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

    const loginEmail = String(formData.get("email") || "").toLowerCase();
    const pendingName = consumePendingRegistration(loginEmail);
    const fallbackName = pendingName || String(formData.get("email") || "").split("@")[0] || "User";
    saveUserName(fallbackName);

    try {
      const meResponse = await apiFetch("/auth/me", { method: "GET" });
      if (meResponse.ok) {
        const me = await meResponse.json();
        if (me?.name) {
          saveUserName(me.name);
        }
      }
    } catch {
      // Keep fallback user name.
    }

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

    const response = await fetch("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const message = document.getElementById("registerMessage");
    if (!response.ok) {
      message.textContent = "Registration failed. Try another email.";
      return;
    }

    savePendingRegistration(payload.name, payload.email);

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

loadProfileName();

window.BrainBoostAuth = {
  apiFetch,
};

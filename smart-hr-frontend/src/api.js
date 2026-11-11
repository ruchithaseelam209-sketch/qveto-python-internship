
const API_BASE_URL = "http://localhost:8000/api";

// Read a cookie from the browser
function getCookie(name) {
  const cookies = document.cookie.split(";");

  for (const cookie of cookies) {
    const trimmed = cookie.trim();

    if (trimmed.startsWith(name + "=")) {
      return decodeURIComponent(
        trimmed.substring(name.length + 1)
      );
    }
  }

  return null;
}

// Get CSRF cookie from Django
export async function getCsrfToken() {
  const response = await fetch(
    `${API_BASE_URL}/auth/csrf/`,
    { credentials: "include" }
  );

  if (!response.ok) {
    throw new Error("Could not obtain CSRF token.");
  }

  return getCookie("csrftoken");
}

// Common function for backend API requests
export async function apiRequest(path, options = {}) {
  const method = (options.method || "GET").toUpperCase();

  const headers = {
    ...options.headers,
  };

  const requestOptions = {
    ...options,
    method,
    headers,
    credentials: "include",
  };

  if (options.body && typeof options.body !== "string") {
    headers["Content-Type"] = "application/json";
    requestOptions.body = JSON.stringify(options.body);
  }

  if (!["GET", "HEAD", "OPTIONS", "TRACE"].includes(method)) {
    let csrfToken = getCookie("csrftoken");

    if (!csrfToken) {
      csrfToken = await getCsrfToken();
    }

    if (!csrfToken) {
      throw new Error("CSRF token is missing.");
    }

    headers["X-CSRFToken"] = csrfToken;
  }

  const response = await fetch(
    `${API_BASE_URL}${path}`,
    requestOptions
  );

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(
      data.error || data.detail || "API request failed."
    );
  }

  return data;
}

// Login
export async function loginUser(username, password) {
  await getCsrfToken();

  return apiRequest("/auth/login/", {
    method: "POST",
    body: { username, password },
  });
}

// Logout
export async function logoutUser() {
  return apiRequest("/auth/logout/", {
    method: "POST",
  });
}

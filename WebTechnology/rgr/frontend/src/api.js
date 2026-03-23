const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

function getToken() {
  return localStorage.getItem("access_token");
}

export function saveTokens(tokens) {
  localStorage.setItem("access_token", tokens.access);
  localStorage.setItem("refresh_token", tokens.refresh);
}

export function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers || {});
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const token = getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || "Request failed");
  }

  if (response.status === 204) {
    return null;
  }

  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }
  return response.text();
}

export function register(data) {
  return apiRequest("/auth/register/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function login(data) {
  return apiRequest("/auth/token/", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function fetchVideos() {
  return apiRequest("/videos/");
}

export function uploadVideo(formData) {
  return apiRequest("/videos/", {
    method: "POST",
    body: formData,
  });
}

export function getVideo(id) {
  return apiRequest(`/videos/${id}/`);
}

export function streamUrl(id) {
  return `${API_URL}/videos/${id}/stream/`;
}

/**
 * Central API Client for local development.
 * Forces connections to localhost:8000
 */

export const CANDIDATE_BASE_URLS = ["http://localhost:8000"];

export async function getApiBaseUrl() {
  return "http://localhost:8000";
}

export async function fetchWithFallback(path, options = {}) {
  let cleanPath = path;
  if (cleanPath.startsWith("http://localhost:8000")) {
    cleanPath = cleanPath.replace("http://localhost:8000", "");
  }
  if (!cleanPath.startsWith('/')) {
    cleanPath = '/' + cleanPath;
  }
  const fullUrl = `http://localhost:8000${cleanPath}`;
  return fetch(fullUrl, options);
}


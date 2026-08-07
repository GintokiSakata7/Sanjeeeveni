/**
 * Central API Client with dynamic local-first auto-fallback to Render cloud backend.
 * Try local server (http://localhost:8000) first; if unreachable, fall back seamlessly to Render.
 */

const CANDIDATE_BASE_URLS = [
  import.meta.env.VITE_API_URL || "http://localhost:8000",
  "https://sanjeeeveni.onrender.com"
];

let workingBaseUrl = null;

/**
 * Reset working base URL cache (useful if network conditions change)
 */
export function resetWorkingBaseUrl() {
  workingBaseUrl = null;
}

/**
 * Returns active working base URL or tries candidate endpoints dynamically.
 */
export async function getApiBaseUrl() {
  if (workingBaseUrl) return workingBaseUrl;

  for (const base of CANDIDATE_BASE_URLS) {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000);
      const res = await fetch(`${base}/docs`, { method: "HEAD", signal: controller.signal });
      clearTimeout(timeoutId);
      if (res.ok || res.status === 404 || res.status === 200 || res.status === 405) {
        workingBaseUrl = base;
        return base;
      }
    } catch (e) {
      // Continue to next candidate URL
    }
  }

  // Fallback default
  return CANDIDATE_BASE_URLS[0];
}

/**
 * Helper to perform fetch requests with automatic fallback between local and Render backend.
 * @param {string} path - E.g. "/api/v1/hospital/all" or "http://localhost:8000/api/v1/hospital/all"
 * @param {RequestInit} [options]
 */
export async function fetchWithFallback(path, options = {}) {
  // Extract route path if absolute URL was passed
  let cleanPath = path;
  for (const base of CANDIDATE_BASE_URLS) {
    if (cleanPath.startsWith(base)) {
      cleanPath = cleanPath.substring(base.length);
      break;
    }
  }
  // Also strip any other http://localhost:8000 or 127.0.0.1 prefix if present
  cleanPath = cleanPath.replace(/^http:\/\/(localhost|127\.0\.0\.1):8000/, '');
  cleanPath = cleanPath.replace(/^https:\/\/sanjeeeveni\.onrender\.com/, '');

  if (!cleanPath.startsWith('/')) {
    cleanPath = '/' + cleanPath;
  }

  const targets = workingBaseUrl
    ? [workingBaseUrl, ...CANDIDATE_BASE_URLS.filter((u) => u !== workingBaseUrl)]
    : CANDIDATE_BASE_URLS;

  let lastError = null;

  for (const base of targets) {
    const fullUrl = `${base}${cleanPath}`;
    try {
      const response = await fetch(fullUrl, options);
      
      // Received response (even 4xx/5xx means backend host is reachable)
      workingBaseUrl = base;
      return response;
    } catch (error) {
      console.warn(`[ApiClient] Failed connection to ${fullUrl}, attempting fallback host...`, error);
      lastError = error;
    }
  }

  throw lastError || new Error("Cannot connect to backend server on localhost or Render.");
}

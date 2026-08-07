/**
 * Central API Client - Zero CORS Architecture
 *
 * ALL requests go through the Vite dev server proxy (never cross-origin from browser):
 *   /api/*     → Vite proxies → http://localhost:8000  (local uvicorn)
 *   /render/*  → Vite proxies → https://sanjeeeveni.onrender.com  (cloud fallback)
 *
 * Flow:
 *  1. Try /api/... (local backend via Vite proxy)
 *  2. If 503 (DB offline) or network error → retry via /render/... (Render via Vite proxy)
 */

const IS_DEV = import.meta.env.DEV;

// Once local fails, stay on Render for the session to avoid repeated timeouts
let preferRender = false;

export const CANDIDATE_BASE_URLS = ["http://localhost:8000", "https://sanjeeeveni.onrender.com"];

export function resetWorkingBaseUrl() {
  preferRender = false;
}

export async function getApiBaseUrl() {
  return '';
}

export async function fetchWithFallback(path, options = {}) {
  let cleanPath = normalizePath(path);

  if (!IS_DEV) {
    // Production: just use relative path directly
    return fetch(cleanPath, options);
  }

  if (!preferRender) {
    try {
      const res = await fetchViaLocal(cleanPath, options);
      if (res.status === 503 || res.status === 502 || res.status === 504) {
        console.warn(`[ApiClient] Local DB offline (${res.status}) for ${cleanPath}, switching to Render`);
        preferRender = true;
        return await fetchViaRender(cleanPath, options);
      }
      return res;
    } catch (err) {
      console.warn(`[ApiClient] Local backend unreachable for ${cleanPath}, switching to Render`, err.message);
      preferRender = true;
      return await fetchViaRender(cleanPath, options);
    }
  }

  return await fetchViaRender(cleanPath, options);
}

async function fetchViaLocal(path, options) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 6000);
  try {
    const res = await fetch(path, { ...options, signal: controller.signal });
    clearTimeout(timer);
    return res;
  } catch (e) {
    clearTimeout(timer);
    throw e;
  }
}

async function fetchViaRender(path, options) {
  const renderPath = '/render' + path;
  return fetch(renderPath, options);
}

function normalizePath(path) {
  let clean = path.replace(/^https?:\/\/[^/]+/, '');
  clean = clean.replace(/^\/render/, '');
  if (!clean.startsWith('/')) clean = '/' + clean;
  return clean;
}

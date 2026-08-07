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
const RENDER_BASE_URL = "https://sanjeeeveni.onrender.com";

// Keep using the server that worked last to avoid repeated timeouts.
let preferLocal = false;

export const CANDIDATE_BASE_URLS = ["https://sanjeeeveni.onrender.com", "http://localhost:8000"];

export function resetWorkingBaseUrl() {
  preferLocal = false;
}

export async function getApiBaseUrl() {
  return '';
}

export async function fetchWithFallback(path, options = {}) {
  let cleanPath = normalizePath(path);

  if (!IS_DEV) {
    return fetch(`${RENDER_BASE_URL}${cleanPath}`, options);
  }

  try {
    const res = await fetchViaLocal(cleanPath, options);
    if (res.status >= 500) {
      console.warn(`[ApiClient] Local returned ${res.status}, trying Render fallback...`);
      return await fetchViaRender(cleanPath, options);
    }
    return res;
  } catch (err) {
    console.warn(`[ApiClient] Local unreachable for ${cleanPath}, trying Render...`, err.message);
    return await fetchViaRender(cleanPath, options);
  }
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

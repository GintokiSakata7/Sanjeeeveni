// Automatically use localhost if running locally, otherwise use the remote production URL
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || (isLocalhost 
  ? 'http://localhost:8000' 
  : 'https://sanjeeeveni.onrender.com');

// Helper to construct full API endpoints
export const getApiUrl = (path) => {
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
};

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

// Helper to construct full API endpoints
export const getApiUrl = (path) => {
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
};

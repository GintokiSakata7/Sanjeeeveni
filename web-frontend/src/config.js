// Force localhost since Render is not yet updated with REST API keys
export const API_BASE_URL = 'http://localhost:8000';

// Helper to construct full API endpoints
export const getApiUrl = (path) => {
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
};

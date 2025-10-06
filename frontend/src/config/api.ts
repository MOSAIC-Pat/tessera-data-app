const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5005';

export const API_ENDPOINTS = {
  base: API_BASE_URL,
  auth: `${API_BASE_URL}/api/auth`,
  health: `${API_BASE_URL}/api/health`
};

export default API_BASE_URL;

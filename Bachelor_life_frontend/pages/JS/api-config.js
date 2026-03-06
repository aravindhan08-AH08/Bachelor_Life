// Backend API base URL
// Automatically detects if running on Vercel or locally
const isLocal = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:";

// On production, we use window.location.origin directly
const API_BASE_URL = isLocal ? "http://127.0.0.1:8000" : window.location.origin;

window.API_CONFIG = {
  BASE_URL: API_BASE_URL,
  ROOMS: `${API_BASE_URL}/rooms`,
  LOGIN: {
    USER: `${API_BASE_URL}/user/login`,
    OWNER: `${API_BASE_URL}/owner/login`,
  },
  SIGNUP: {
    USER: `${API_BASE_URL}/user/`,
    OWNER: `${API_BASE_URL}/owner/`,
  },
  BOOKING: `${API_BASE_URL}/booking`,
  CONTACT: `${API_BASE_URL}/contact`,
  USER_DASHBOARD: `${API_BASE_URL}/user-dashboard`,
  OWNER_DASHBOARD: `${API_BASE_URL}/owner/dashboard`,
};

// Backend API base URL detection
const isLocal = (
  window.location.hostname === "localhost" ||
  window.location.hostname === "127.0.0.1" ||
  window.location.protocol === "file:" ||
  window.location.hostname.startsWith("192.168.") ||
  window.location.hostname.startsWith("10.") ||
  window.location.hostname.startsWith("172.")
);

// If local, we force port 8000. If production (Vercel), we use origin.
const API_BASE_URL = isLocal ? `http://${window.location.hostname === "localhost" || window.location.protocol === "file:" ? "127.0.0.1" : window.location.hostname}:8000` : window.location.origin;

console.log(`[API Config] Mode: ${isLocal ? "Local" : "Production"} | Base URL: ${API_BASE_URL}`);

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

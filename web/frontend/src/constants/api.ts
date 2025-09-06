export const API_CONFIG = {
  BASE_URL: 'http://localhost:8080/api',
  TIMEOUT: 30000,
  RETRY_ATTEMPTS: 3,
} as const;

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
  },
  USER: {
    PROFILE: '/users/me',
    UPDATE_PROFILE: '/users/profile',
  },
  CHAT: {
    CREATE_SESSION: '/chat/sessions',
    SEND_MESSAGE: '/chat/messages',
    GET_HISTORY: '/chat/history',
  },
  HEALTH: {
    CHECK: '/health',
  },
} as const;

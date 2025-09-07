export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  PROFILE_SETUP: '/profile-setup',
  DASHBOARD: '/dashboard',
  CHAT: '/chat',
  CHAT_SESSION: '/chat/:sessionId',
  PROFILE: '/profile',
  SETTINGS: '/settings',
} as const;

export const PROTECTED_ROUTES = [
  ROUTES.DASHBOARD,
  ROUTES.CHAT,
  ROUTES.CHAT_SESSION,
  ROUTES.PROFILE,
  ROUTES.SETTINGS,
] as const;

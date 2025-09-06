export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  PROFILE_SETUP: '/profile-setup',
  DASHBOARD: '/dashboard',
  CHAT: '/chat',
  PROFILE: '/profile',
  SETTINGS: '/settings',
} as const;

export const PROTECTED_ROUTES = [
  ROUTES.DASHBOARD,
  ROUTES.CHAT,
  ROUTES.PROFILE,
  ROUTES.SETTINGS,
] as const;

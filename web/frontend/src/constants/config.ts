// Application Configuration
export const APP_CONFIG = {
  // Chuyển MOCK_MODE = false khi muốn kết nối thật với backend
  MOCK_MODE: false, // true = chỉ dùng mock data, false = kết nối backend thật
  
  // API Configuration
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080/api',
  API_TIMEOUT: 30000,
  
  // Development settings
  ENABLE_LOGGING: import.meta.env.MODE === 'development',
  
  // Mock data settings
  MOCK_RESPONSE_DELAY: 1000, // ms
  MOCK_SUCCESS_RATE: 0.9, // 90% success rate for mock APIs
} as const;

// Helper functions
export const isMockMode = () => APP_CONFIG.MOCK_MODE;
export const isProductionMode = () => import.meta.env.MODE === 'production';
export const isDevelopmentMode = () => import.meta.env.MODE === 'development';

// Logging helper
export const logger = {
  info: (...args: any[]) => {
    if (APP_CONFIG.ENABLE_LOGGING) {
      console.log('[INFO]', ...args);
    }
  },
  warn: (...args: any[]) => {
    if (APP_CONFIG.ENABLE_LOGGING) {
      console.warn('[WARN]', ...args);
    }
  },
  error: (...args: any[]) => {
    if (APP_CONFIG.ENABLE_LOGGING) {
      console.error('[ERROR]', ...args);
    }
  },
};

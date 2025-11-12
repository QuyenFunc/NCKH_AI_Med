type StorageType = 'localStorage' | 'sessionStorage';

class StorageManager {
  private getStorage(type: StorageType): Storage {
    return type === 'localStorage' ? localStorage : sessionStorage;
  }

  setItem(key: string, value: any, type: StorageType = 'localStorage'): void {
    try {
      const storage = this.getStorage(type);
      // Avoid saving undefined which becomes the string "undefined" and breaks JSON.parse
      if (value === undefined) {
        storage.removeItem(key);
        return;
      }
      storage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error setting storage item:', error);
    }
  }

  getItem<T>(key: string, type: StorageType = 'localStorage'): T | null {
    try {
      const storage = this.getStorage(type);
      const item = storage.getItem(key);
      
      // ✅ Guard against invalid JSON strings
      if (!item || item === 'undefined' || item === 'null' || item.trim() === '') {
        return null;
      }
      
      return JSON.parse(item);
    } catch (error) {
      console.error('Error getting storage item:', key, error);
      return null;
    }
  }

  removeItem(key: string, type: StorageType = 'localStorage'): void {
    try {
      const storage = this.getStorage(type);
      storage.removeItem(key);
    } catch (error) {
      console.error('Error removing storage item:', error);
    }
  }

  clear(type: StorageType = 'localStorage'): void {
    try {
      const storage = this.getStorage(type);
      storage.clear();
    } catch (error) {
      console.error('Error clearing storage:', error);
    }
  }
}

export const storage = new StorageManager();

// Predefined keys for consistency
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'auth_token',
  USER_DATA: 'user_data',
  CHAT_HISTORY: 'chat_history',
  PROFILE_DATA: 'profile_data',
  APP_SETTINGS: 'app_settings',
} as const;

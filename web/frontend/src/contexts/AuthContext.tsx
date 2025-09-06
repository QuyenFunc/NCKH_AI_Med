import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

type AuthMode = 'login' | 'register' | 'authenticated';

interface User {
  name: string;
  email: string;
}

interface AuthContextType {
  authMode: AuthMode;
  user: User | null;
  hasCompletedProfile: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => void;
  register: (name: string, email: string, password: string) => void;
  logout: () => void;
  switchToRegister: () => void;
  switchToLogin: () => void;
  setHasCompletedProfile: (completed: boolean) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

// LocalStorage keys
const AUTH_STORAGE_KEY = 'nckh_auth';
const USER_STORAGE_KEY = 'nckh_user';
const PROFILE_STORAGE_KEY = 'nckh_profile_completed';

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [user, setUser] = useState<User | null>(null);
  const [hasCompletedProfile, setHasCompletedProfile] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Load auth state from localStorage on mount
  useEffect(() => {
    try {
      const savedAuthMode = localStorage.getItem(AUTH_STORAGE_KEY) as AuthMode;
      const savedUser = localStorage.getItem(USER_STORAGE_KEY);
      const savedProfileStatus = localStorage.getItem(PROFILE_STORAGE_KEY);

      if (savedAuthMode && savedUser) {
        setAuthMode(savedAuthMode);
        setUser(JSON.parse(savedUser));
        setHasCompletedProfile(savedProfileStatus === 'true');
      }
    } catch (error) {
      console.warn('Failed to load auth state from localStorage:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = useCallback((email: string, _password: string) => {
    // Mock authentication
    const newUser = { name: 'Người dùng', email };
    setUser(newUser);
    setAuthMode('authenticated');
    
    // Save to localStorage
    localStorage.setItem(AUTH_STORAGE_KEY, 'authenticated');
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser));
  }, []);

  const register = useCallback((name: string, email: string, _password: string) => {
    // Mock registration
    const newUser = { name, email };
    setUser(newUser);
    setAuthMode('authenticated');
    
    // Save to localStorage
    localStorage.setItem(AUTH_STORAGE_KEY, 'authenticated');
    localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(newUser));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    setAuthMode('login');
    setHasCompletedProfile(false);
    
    // Clear localStorage
    localStorage.removeItem(AUTH_STORAGE_KEY);
    localStorage.removeItem(USER_STORAGE_KEY);
    localStorage.removeItem(PROFILE_STORAGE_KEY);
  }, []);

  const switchToRegister = useCallback(() => setAuthMode('register'), []);
  const switchToLogin = useCallback(() => setAuthMode('login'), []);

  const setHasCompletedProfileWithPersist = useCallback((completed: boolean) => {
    setHasCompletedProfile(completed);
    localStorage.setItem(PROFILE_STORAGE_KEY, completed.toString());
  }, []);

  const value: AuthContextType = {
    authMode,
    user,
    hasCompletedProfile,
    isLoading,
    login,
    register,
    logout,
    switchToRegister,
    switchToLogin,
    setHasCompletedProfile: setHasCompletedProfileWithPersist,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

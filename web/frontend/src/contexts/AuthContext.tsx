import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';
import { AuthService } from '../services/auth.service';
import type { UserInfo } from '../types';

type AuthMode = 'login' | 'register' | 'authenticated';

interface AuthContextType {
  authMode: AuthMode;
  user: UserInfo | null;
  hasCompletedProfile: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, confirmPassword: string) => Promise<void>;
  logout: () => Promise<void>;
  switchToRegister: () => void;
  switchToLogin: () => void;
  setHasCompletedProfile: (completed: boolean) => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: React.ReactNode;
}

// LocalStorage keys
const PROFILE_STORAGE_KEY = 'nckh_profile_completed';

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [authMode, setAuthMode] = useState<AuthMode>('login');
  const [user, setUser] = useState<UserInfo | null>(null);
  const [hasCompletedProfile, setHasCompletedProfile] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load auth state from localStorage on mount
  useEffect(() => {
    const loadAuthState = async () => {
      try {
        // Kiểm tra token có tồn tại không
        if (AuthService.isAuthenticated()) {
          try {
            // Lấy thông tin user từ localStorage trước
            const savedUser = AuthService.getUserInfo();
            if (savedUser) {
              setUser(savedUser);
              setAuthMode('authenticated');
              setHasCompletedProfile(savedUser.isProfileComplete);
            }

            // Verify token với backend (optional, có thể làm trong background)
            const currentUser = await AuthService.getCurrentUser();
            setUser(currentUser);
            setHasCompletedProfile(currentUser.isProfileComplete);
          } catch (error) {
            console.warn('Token verification failed:', error);
            AuthService.clearAuth();
            setAuthMode('login');
          }
        }
        
        // Load profile completion status
        const savedProfileStatus = localStorage.getItem(PROFILE_STORAGE_KEY);
        if (savedProfileStatus === 'true') {
          setHasCompletedProfile(true);
        }
      } catch (error) {
        console.warn('Failed to load auth state:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadAuthState();
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const authResponse = await AuthService.login({ email, password });
      setUser(authResponse.user);
      setAuthMode('authenticated');
      setHasCompletedProfile(authResponse.user.isProfileComplete);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Đăng nhập thất bại';
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (name: string, email: string, password: string, confirmPassword: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const authResponse = await AuthService.register({ 
        name, 
        email, 
        password, 
        confirmPassword 
      });
      setUser(authResponse.user);
      setAuthMode('authenticated');
      setHasCompletedProfile(authResponse.user.isProfileComplete);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Đăng ký thất bại';
      setError(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await AuthService.logout();
    } catch (error) {
      console.warn('Logout error:', error);
    } finally {
      setUser(null);
      setAuthMode('login');
      setHasCompletedProfile(false);
      localStorage.removeItem(PROFILE_STORAGE_KEY);
    }
  }, []);

  const switchToRegister = useCallback(() => setAuthMode('register'), []);
  const switchToLogin = useCallback(() => setAuthMode('login'), []);

  const setHasCompletedProfileWithPersist = useCallback((completed: boolean) => {
    setHasCompletedProfile(completed);
    localStorage.setItem(PROFILE_STORAGE_KEY, completed.toString());
  }, []);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  const value: AuthContextType = {
    authMode,
    user,
    hasCompletedProfile,
    isLoading,
    error,
    login,
    register,
    logout,
    switchToRegister,
    switchToLogin,
    setHasCompletedProfile: setHasCompletedProfileWithPersist,
    clearError,
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

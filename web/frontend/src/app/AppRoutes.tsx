import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

// Auth Pages
import LoginPage from '../features/auth/LoginPage';
import RegisterPage from '../features/auth/RegisterPage';

// Profile Pages
import ProfileSetupScreen from '../features/profile/ProfileSetupScreen';

// Dashboard & Layout
import { DashboardPage } from '../features/dashboard';
import { SettingsPage } from '../features/settings';
import { MainLayout } from '../components/layout';

export const AppRoutes: React.FC = () => {
  const { authMode, hasCompletedProfile, isLoading } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-content">
          <div className="loading-spinner" />
          <p className="loading-text">Đang tải...</p>
        </div>
      </div>
    );
  }

  if (authMode === 'login') {
    return <LoginPage />;
  }

  if (authMode === 'register') {
    return <RegisterPage />;
  }

  return (
    <Routes>
      <Route 
        path="/" 
        element={
          hasCompletedProfile ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <Navigate to="/profile-setup" replace />
          )
        } 
      />
      <Route 
        path="/profile-setup" 
        element={<ProfileSetupScreen />} 
      />
      <Route 
        path="/dashboard" 
        element={
          <MainLayout>
            <DashboardPage />
          </MainLayout>
        } 
      />
      <Route 
        path="/settings" 
        element={<SettingsPage />} 
      />
    </Routes>
  );
};

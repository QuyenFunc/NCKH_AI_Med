import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useChat } from '../contexts/ChatContext';

// Auth Pages
import LoginPage from '../features/auth/LoginPage';
import RegisterPage from '../features/auth/RegisterPage';

// Profile Pages
import ProfileSetupScreen from '../features/profile/ProfileSetupScreen';

// Dashboard & Layout
import { DashboardPage } from '../features/dashboard';
import { MainLayout } from '../components/layout';

export const AppRoutes: React.FC = () => {
  const { authMode, hasCompletedProfile, isLoading } = useAuth();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: '#ffffff',
        color: '#374151',
        fontFamily: 'Inter, sans-serif'
      }}>
        <div style={{
          textAlign: 'center',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '16px'
        }}>
          <div style={{
            width: '40px',
            height: '40px',
            border: '3px solid #e5e7eb',
            borderTop: '3px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite'
          }} />
          <p style={{ margin: 0, fontSize: '16px', color: '#6b7280' }}>Đang tải...</p>
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
    </Routes>
  );
};

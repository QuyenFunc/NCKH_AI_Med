import React from 'react';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import './ThemeToggle.css';

interface ThemeToggleProps {
  showLabel?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({ 
  showLabel = true, 
  size = 'md' 
}) => {
  const { isDark, toggleTheme } = useTheme();

  return (
    <div className={`theme-toggle-container ${size}`}>
      {showLabel && (
        <div className="theme-toggle-label">
          <Sun size={18} className="theme-icon light" />
          <span>Chế độ tối</span>
        </div>
      )}
      
      <button
        onClick={toggleTheme}
        className={`theme-toggle-switch ${isDark ? 'active' : ''}`}
        aria-label={isDark ? 'Chuyển sang chế độ sáng' : 'Chuyển sang chế độ tối'}
        title={isDark ? 'Chuyển sang chế độ sáng' : 'Chuyển sang chế độ tối'}
      >
        <div className="toggle-track">
          <div className="toggle-thumb">
            {isDark ? (
              <Moon size={14} className="theme-icon" />
            ) : (
              <Sun size={14} className="theme-icon" />
            )}
          </div>
        </div>
      </button>
    </div>
  );
};

import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  Home, 
  Package, 
  ShoppingCart, 
  Shield, 
  BarChart3, 
  Menu, 
  X,
  Bell,
  User,
  Settings,
  Heart,
  Users
} from 'lucide-react';
import './Layout.css';

const Layout = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const navigationItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: Home
    },
    {
      name: 'Nhận hàng',
      href: '/receive-goods',
      icon: ShoppingCart
    },
    {
      name: 'Quản lý Kho',
      href: '/inventory',
      icon: Package
    },
    {
      name: 'Xác thực tại quầy',
      href: '/verification',
      icon: Shield
    },
    {
      name: 'Báo cáo',
      href: '/reports',
      icon: BarChart3
    },
    {
      name: 'Tài khoản',
      href: '/account',
      icon: Users
    }
  ];

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="app-layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo">
            <Heart size={32} />
            <span className="logo-text">Pharmacy Portal</span>
          </div>
          <button className="sidebar-close" onClick={toggleSidebar}>
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          <ul className="nav-list">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              
              return (
                <li key={item.href} className="nav-item">
                  <NavLink
                    to={item.href}
                    className={`nav-link ${isActive ? 'nav-link-active' : ''}`}
                    onClick={() => setSidebarOpen(false)}
                  >
                    <Icon size={20} />
                    <span>{item.name}</span>
                  </NavLink>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="sidebar-footer">
          <div className="company-info">
            <div className="company-logo">
              <Heart size={24} />
            </div>
            <div className="company-details">
              <div className="company-name">Hiệu thuốc ABC</div>
              <div className="company-role">Hiệu thuốc</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Sidebar Overlay */}
      {sidebarOpen && (
        <div className="sidebar-overlay" onClick={toggleSidebar} />
      )}

      {/* Main Content */}
      <div className="main-wrapper">
        {/* Header */}
        <header className="header">
          <div className="header-left">
            <button className="sidebar-toggle" onClick={toggleSidebar}>
              <Menu size={20} />
            </button>
            <h1 className="page-title">Pharmacy Portal</h1>
          </div>

          <div className="header-right">
            <button className="header-btn">
              <Bell size={20} />
              <span className="notification-badge">2</span>
            </button>
            
            <div className="user-menu">
              <button className="user-btn">
                <User size={20} />
                <span>Dược sĩ</span>
              </button>
            </div>

            <button className="header-btn">
              <Settings size={20} />
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;

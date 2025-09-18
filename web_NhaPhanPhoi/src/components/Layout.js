import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  Home, 
  Package, 
  Plus, 
  Truck, 
  BarChart3, 
  Menu, 
  X,
  Bell,
  User,
  Settings,
  Download,
  Upload
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
      name: 'Nhập kho (NSX)',
      href: '/receive-goods',
      icon: Download
    },
    {
      name: 'Quản lý Kho',
      href: '/batches',
      icon: Package
    },
    {
      name: 'Xuất kho (HT)',
      href: '/create-shipment',
      icon: Upload
    },
    {
      name: 'Theo dõi Vận chuyển',
      href: '/shipments',
      icon: Truck
    },
    {
      name: 'Báo cáo',
      href: '/reports',
      icon: BarChart3
    }
  ];

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="layout">
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div 
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-header">
          <div className="logo">
            <Package className="logo-icon" />
            <span className="logo-text">Nhà Phân Phối</span>
          </div>
          <button 
            className="sidebar-close mobile-only"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={20} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) => 
                  `nav-item ${isActive ? 'nav-item-active' : ''}`
                }
                onClick={() => setSidebarOpen(false)}
              >
                <Icon size={20} />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <div className="user-avatar">
              <User size={16} />
            </div>
            <div className="user-details">
              <div className="user-name">Nhà Phân Phối</div>
              <div className="user-role">Distributor</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="main-content">
        {/* Header */}
        <header className="header">
          <div className="header-left">
            <button 
              className="menu-button"
              onClick={toggleSidebar}
            >
              <Menu size={20} />
            </button>
            <h1 className="page-title">
              {navigationItems.find(item => item.href === location.pathname)?.name || 'Dashboard'}
            </h1>
          </div>

          <div className="header-right">
            <button className="notification-button">
              <Bell size={20} />
              <span className="notification-badge">3</span>
            </button>
            
            <button className="settings-button">
              <Settings size={20} />
            </button>

            <div className="blockchain-status">
              <div className="status-indicator status-connected"></div>
              <span className="status-text">Blockchain Connected</span>
            </div>
          </div>
        </header>

        {/* Content */}
        <main className="content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;

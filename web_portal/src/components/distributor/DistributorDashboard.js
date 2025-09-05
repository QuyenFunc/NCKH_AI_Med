import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Truck, Package, Users, AlertTriangle, Clock, CheckCircle, XCircle } from 'lucide-react';
import './DistributorDashboard.css';

// Mock data
const statsData = [
  {
    title: 'Lô hàng đang vận chuyển',
    value: '15',
    icon: Truck,
    color: 'bg-blue-500',
    change: '+2 từ hôm qua'
  },
  {
    title: 'Lô hàng đã giao (tuần này)',
    value: '128',
    icon: CheckCircle,
    color: 'bg-green-500',
    change: '+12% so với tuần trước'
  },
  {
    title: 'Đối tác nhận hàng',
    value: '45',
    icon: Users,
    color: 'bg-purple-500',
    change: '3 đối tác mới'
  },
  {
    title: 'Cảnh báo',
    value: '2',
    icon: AlertTriangle,
    color: 'bg-red-500',
    change: 'Lô hàng trễ hẹn'
  }
];

const shipmentStatusData = [
  { name: 'Đang vận chuyển', value: 15, color: '#3b82f6' },
  { name: 'Đã giao thành công', value: 128, color: '#10b981' },
  { name: 'Bị trả lại', value: 3, color: '#ef4444' }
];

const recentActivities = [
  {
    id: 1,
    type: 'created',
    shipmentId: 'LOT001234',
    pharmacy: 'Hiệu thuốc ABC',
    time: '2 giờ trước',
    status: 'Mới tạo'
  },
  {
    id: 2,
    type: 'delivered',
    shipmentId: 'LOT001230',
    pharmacy: 'Hiệu thuốc XYZ',
    time: '4 giờ trước',
    status: 'Đã giao'
  },
  {
    id: 3,
    type: 'shipping',
    shipmentId: 'LOT001228',
    pharmacy: 'Hiệu thuốc DEF',
    time: '6 giờ trước',
    status: 'Đang giao'
  },
  {
    id: 4,
    type: 'created',
    shipmentId: 'LOT001225',
    pharmacy: 'Hiệu thuốc GHI',
    time: '1 ngày trước',
    status: 'Mới tạo'
  },
  {
    id: 5,
    type: 'delivered',
    shipmentId: 'LOT001220',
    pharmacy: 'Hiệu thuốc JKL',
    time: '1 ngày trước',
    status: 'Đã giao'
  }
];

function DistributorDashboard() {
  const getActivityIcon = (type) => {
    switch (type) {
      case 'created':
        return <Package className="activity-icon created" />;
      case 'shipping':
        return <Clock className="activity-icon shipping" />;
      case 'delivered':
        return <CheckCircle className="activity-icon delivered" />;
      default:
        return <Package className="activity-icon" />;
    }
  };

  return (
    <div className="distributor-dashboard">
      <div className="dashboard-header">
        <h1>Dashboard Nhà Phân Phối</h1>
        <p>Tổng quan hoạt động phân phối và giao hàng</p>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        {statsData.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div key={index} className="stat-card">
              <div className="stat-icon-wrapper">
                <Icon className="stat-icon" />
              </div>
              <div className="stat-content">
                <h3 className="stat-value">{stat.value}</h3>
                <p className="stat-title">{stat.title}</p>
                <p className="stat-change">{stat.change}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-grid">
        {/* Recent Activities */}
        <div className="dashboard-card activities-card">
          <div className="card-header">
            <h2>Hoạt động Giao hàng Gần đây</h2>
          </div>
          <div className="activities-list">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="activity-item">
                {getActivityIcon(activity.type)}
                <div className="activity-content">
                  <div className="activity-main">
                    <span className="shipment-id">{activity.shipmentId}</span>
                    <span className="pharmacy-name">{activity.pharmacy}</span>
                  </div>
                  <div className="activity-meta">
                    <span className={`activity-status ${activity.type}`}>
                      {activity.status}
                    </span>
                    <span className="activity-time">{activity.time}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Shipment Status Chart */}
        <div className="dashboard-card chart-card">
          <div className="card-header">
            <h2>Tỷ lệ Trạng thái Lô hàng</h2>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={shipmentStatusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {shipmentStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="chart-legend">
              {shipmentStatusData.map((item, index) => (
                <div key={index} className="legend-item">
                  <div
                    className="legend-color"
                    style={{ backgroundColor: item.color }}
                  ></div>
                  <span className="legend-label">{item.name}</span>
                  <span className="legend-value">{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Thao tác Nhanh</h2>
        <div className="action-buttons">
          <button className="action-btn primary">
            <Package />
            Tạo lô hàng mới
          </button>
          <button className="action-btn secondary">
            <Truck />
            Xem tất cả lô hàng
          </button>
          <button className="action-btn secondary">
            <Users />
            Quản lý đối tác
          </button>
        </div>
      </div>
    </div>
  );
}

export default DistributorDashboard;


import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { 
  Package, 
  AlertTriangle, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  Calendar,
  ShoppingCart,
  Archive
} from 'lucide-react';
import './PharmacyDashboard.css';

// Mock data
const statsData = [
  {
    title: 'Lô hàng đang đến',
    value: '8',
    icon: Package,
    color: 'bg-blue-500',
    change: '+3 lô hàng trong tuần'
  },
  {
    title: 'Sản phẩm trong kho',
    value: '2,540',
    icon: Archive,
    color: 'bg-green-500',
    change: '+120 sản phẩm tuần này'
  },
  {
    title: 'Sản phẩm sắp hết hạn',
    value: '30',
    icon: AlertTriangle,
    color: 'bg-yellow-500',
    change: 'Cần kiểm tra trong 30 ngày'
  },
  {
    title: 'Sản phẩm sắp hết hàng',
    value: '5',
    icon: TrendingUp,
    color: 'bg-red-500',
    change: 'Cần đặt hàng bổ sung'
  }
];

const incomingShipments = [
  {
    id: 'LOT001234',
    distributor: 'Nhà phân phối ABC',
    expectedDate: '2024-01-18',
    status: 'Đang vận chuyển',
    items: 3
  },
  {
    id: 'LOT001235',
    distributor: 'Nhà phân phối XYZ',
    expectedDate: '2024-01-19',
    status: 'Chuẩn bị giao',
    items: 2
  },
  {
    id: 'LOT001236',
    distributor: 'Nhà phân phối DEF',
    expectedDate: '2024-01-20',
    status: 'Đang vận chuyển',
    items: 5
  },
  {
    id: 'LOT001237',
    distributor: 'Nhà phân phối ABC',
    expectedDate: '2024-01-21',
    status: 'Chờ xử lý',
    items: 1
  }
];

const topSellingProducts = [
  { name: 'Paracetamol 500mg', sales: 450 },
  { name: 'Vitamin C 1000mg', sales: 380 },
  { name: 'Amoxicillin 250mg', sales: 320 },
  { name: 'Cetirizine 10mg', sales: 280 },
  { name: 'Omeprazole 20mg', sales: 240 },
  { name: 'Aspirin 300mg', sales: 200 }
];

function PharmacyDashboard() {
  const getShipmentStatusClass = (status) => {
    switch (status) {
      case 'Đang vận chuyển':
        return 'status-shipping';
      case 'Chuẩn bị giao':
        return 'status-ready';
      case 'Chờ xử lý':
        return 'status-pending';
      default:
        return '';
    }
  };

  return (
    <div className="pharmacy-dashboard">
      <div className="dashboard-header">
        <h1>Dashboard Hiệu Thuốc</h1>
        <p>Tổng quan quản lý kho và nhận hàng</p>
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
        {/* Incoming Shipments */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2>Lô hàng đang chờ nhận</h2>
            <span className="badge">{incomingShipments.length}</span>
          </div>
          <div className="shipments-list">
            {incomingShipments.map((shipment) => (
              <div key={shipment.id} className="shipment-item">
                <div className="shipment-info">
                  <div className="shipment-main">
                    <span className="shipment-id">{shipment.id}</span>
                    <span className="distributor-name">{shipment.distributor}</span>
                  </div>
                  <div className="shipment-meta">
                    <div className="shipment-date">
                      <Calendar className="meta-icon" />
                      <span>{new Date(shipment.expectedDate).toLocaleDateString('vi-VN')}</span>
                    </div>
                    <div className="shipment-items">
                      <Package className="meta-icon" />
                      <span>{shipment.items} sản phẩm</span>
                    </div>
                  </div>
                  <div className="shipment-status">
                    <span className={`status-badge ${getShipmentStatusClass(shipment.status)}`}>
                      {shipment.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="card-footer">
            <button className="btn btn-primary btn-full">
              <ShoppingCart />
              Đi đến nhận hàng
            </button>
          </div>
        </div>

        {/* Top Selling Products Chart */}
        <div className="dashboard-card chart-card">
          <div className="card-header">
            <h2>Sản phẩm bán chạy nhất (tháng này)</h2>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={topSellingProducts}
                margin={{
                  top: 20,
                  right: 30,
                  left: 20,
                  bottom: 5,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  tick={{ fontSize: 12 }}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="sales" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Alerts Section */}
      <div className="alerts-section">
        <h2>Cảnh báo và Thông báo</h2>
        <div className="alerts-grid">
          <div className="alert-card warning">
            <AlertTriangle className="alert-icon" />
            <div className="alert-content">
              <h3>Sản phẩm sắp hết hạn</h3>
              <p>30 sản phẩm sẽ hết hạn trong 30 ngày tới</p>
              <button className="btn btn-secondary btn-small">Xem chi tiết</button>
            </div>
          </div>
          <div className="alert-card danger">
            <TrendingUp className="alert-icon" />
            <div className="alert-content">
              <h3>Sản phẩm sắp hết hàng</h3>
              <p>5 sản phẩm có lượng tồn kho dưới mức tối thiểu</p>
              <button className="btn btn-secondary btn-small">Đặt hàng ngay</button>
            </div>
          </div>
          <div className="alert-card success">
            <CheckCircle className="alert-icon" />
            <div className="alert-content">
              <h3>Nhận hàng thành công</h3>
              <p>3 lô hàng đã được nhận và xác thực hôm nay</p>
              <button className="btn btn-secondary btn-small">Xem lịch sử</button>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h2>Thao tác Nhanh</h2>
        <div className="action-buttons">
          <button className="action-btn primary">
            <ShoppingCart />
            Nhận hàng mới
          </button>
          <button className="action-btn secondary">
            <Archive />
            Xem kho hàng
          </button>
          <button className="action-btn secondary">
            <Clock />
            Lịch sử giao dịch
          </button>
        </div>
      </div>
    </div>
  );
}

export default PharmacyDashboard;




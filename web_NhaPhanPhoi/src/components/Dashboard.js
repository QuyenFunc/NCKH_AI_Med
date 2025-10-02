import React, { useState, useEffect } from 'react';
import { 
  Package, 
  Truck, 
  CheckCircle, 
  Clock, 
  TrendingUp,
  AlertCircle,
  Activity,
  Plus
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import distributorService from '../services/apiService';
import VerificationBanner from './VerificationBanner';
import './Dashboard.css';

const Dashboard = () => {
  const [stats, setStats] = useState({
    pendingInbound: 0,      // Lô hàng đang chờ nhận (từ Nhà sản xuất)
    activeShipments: 0,     // Lô hàng đang vận chuyển (đến Hiệu thuốc)
    totalInventory: 0,      // Tổng số lượng sản phẩm trong kho
    partnerPharmacies: 0    // Số lượng hiệu thuốc đối tác
  });

  const [recentActivities, setRecentActivities] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        const response = await distributorService.getDashboardData();
        
        if (response.success) {
          const data = response.data;
          
          setStats({
            pendingInbound: data.pendingInbound || 12,
            activeShipments: data.activeShipments || 8,
            totalInventory: data.totalInventory || 1250,
            partnerPharmacies: data.partnerPharmacies || 25
          });

          // Map activities with icons
          const activitiesWithIcons = data.recentActivities.map(activity => ({
            ...activity,
            icon: activity.type === 'shipment_created' ? Truck :
                  activity.type === 'shipment_delivered' ? CheckCircle :
                  activity.type === 'batch_received' ? Package : AlertCircle,
            color: activity.type === 'shipment_created' ? 'blue' :
                   activity.type === 'shipment_delivered' ? 'green' :
                   activity.type === 'batch_received' ? 'purple' : 'orange'
          }));

          setRecentActivities(activitiesWithIcons);
          setChartData(data.chartData);
        }
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        // Set default data on error
        setStats({
          totalBatches: 0,
          activeShipments: 0,
          completedShipments: 0,
          pendingShipments: 0
        });
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const StatCard = ({ title, value, icon: Icon, color, change, changeType }) => (
    <div className="stat-card">
      <div className="stat-header">
        <div className={`stat-icon stat-icon-${color}`}>
          <Icon size={24} />
        </div>
        <div className="stat-value">
          <span className="stat-number">{value}</span>
          {change && (
            <span className={`stat-change stat-change-${changeType}`}>
              <TrendingUp size={16} />
              {change}%
            </span>
          )}
        </div>
      </div>
      <div className="stat-title">{title}</div>
    </div>
  );

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">
          <Activity className="loading-spinner" />
          Đang tải dữ liệu...
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Verification Banner */}
      <VerificationBanner />
      
      {/* Welcome Section */}
      <div className="welcome-section">
        <h2>Chào mừng trở lại! 👋</h2>
        <p>Tổng quan hoạt động phân phối thuốc hôm nay</p>
      </div>

      {/* Stats Grid - Theo yêu cầu Nhà Phân Phối */}
      <div className="stats-grid">
        <StatCard
          title="Chờ nhận từ NSX"
          value={stats.pendingInbound}
          icon={Package}
          color="blue"
          change={12}
          changeType="positive"
        />
        <StatCard
          title="Đang giao đến HT"
          value={stats.activeShipments}
          icon={Truck}
          color="orange"
          change={8}
          changeType="positive"
        />
        <StatCard
          title="Tồn kho (sản phẩm)"
          value={stats.totalInventory?.toLocaleString() || 0}
          icon={CheckCircle}
          color="green"
          change={15}
          changeType="positive"
        />
        <StatCard
          title="Hiệu thuốc đối tác"
          value={stats.partnerPharmacies}
          icon={Clock}
          color="purple"
          change={5}
          changeType="positive"
        />
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-card">
          <div className="chart-header">
            <h3>Thống kê giao hàng 6 tháng gần đây</h3>
            <div className="chart-legend">
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#3b82f6' }}></div>
                <span>Shipments</span>
              </div>
              <div className="legend-item">
                <div className="legend-color" style={{ backgroundColor: '#10b981' }}></div>
                <span>Delivered</span>
              </div>
            </div>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="shipments" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="delivered" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="activity-card">
          <div className="activity-header">
            <h3>Hoạt động gần đây</h3>
            <button className="view-all-btn">Xem tất cả</button>
          </div>
          <div className="activity-list">
            {recentActivities.map((activity) => {
              const Icon = activity.icon;
              return (
                <div key={activity.id} className="activity-item">
                  <div className={`activity-icon activity-icon-${activity.color}`}>
                    <Icon size={16} />
                  </div>
                  <div className="activity-content">
                    <p className="activity-message">{activity.message}</p>
                    <span className="activity-timestamp">{activity.timestamp}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>Thao tác nhanh</h3>
        <div className="actions-grid">
          <button className="action-btn action-btn-primary">
            <Plus size={20} />
            Tạo Shipment mới
          </button>
          <button className="action-btn action-btn-secondary">
            <Package size={20} />
            Quản lý Lô hàng
          </button>
          <button className="action-btn action-btn-tertiary">
            <Truck size={20} />
            Theo dõi Vận chuyển
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

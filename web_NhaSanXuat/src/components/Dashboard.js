import React, { useState, useEffect } from 'react';
import { 
  Factory, 
  Package, 
  Truck, 
  TrendingUp,
  AlertCircle,
  Activity,
  Users,
  CheckCircle,
  Clock,
  Plus,
  BarChart3
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import manufacturerService from '../services/apiService';
import './Dashboard.css';

const Dashboard = () => {
  const [stats, setStats] = useState({
    totalProducts: 0,        // Tổng số dòng sản phẩm
    activeBatches: 0,        // Lô thuốc đang sản xuất
    shippedBatches: 0,       // Lô hàng đã xuất
    totalDistributors: 0     // Số nhà phân phối đối tác
  });

  const [recentActivities, setRecentActivities] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [productionData, setProductionData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // Fetch real data from API
        const response = await manufacturerService.getDashboardData();
        
        if (response.success && response.data) {
          setStats(response.data.stats || {
            totalProducts: 0,
            activeBatches: 0,
            shippedBatches: 0,
            totalDistributors: 0
          });

          setRecentActivities(response.data.recentActivities || []);
          setChartData(response.data.chartData || []);
          setProductionData(response.data.productionData || []);
        } else {
          // Set empty states if no data
          setStats({
            totalProducts: 0,
            activeBatches: 0,
            shippedBatches: 0,
            totalDistributors: 0
          });
          setRecentActivities([]);
          setChartData([]);
          setProductionData([]);
        }

      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        // Set empty states on error
        setStats({
          totalProducts: 0,
          activeBatches: 0,
          shippedBatches: 0,
          totalDistributors: 0
        });
        setRecentActivities([]);
        setChartData([]);
        setProductionData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const StatCard = ({ title, value, icon: Icon, color, change, changeType }) => (
    <div className={`stat-card stat-card-${color}`}>
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

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (minutes < 60) {
      return `${minutes} phút trước`;
    } else {
      return `${hours} giờ trước`;
    }
  };

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
      {/* Welcome Section */}
      <div className="welcome-section">
        <h2>Chào mừng đến Manufacturer Portal! 🏭</h2>
        <p>Tổng quan hoạt động sản xuất và phân phối thuốc hôm nay</p>
      </div>

      {/* Stats Grid - Theo yêu cầu Nhà Sản Xuất */}
      <div className="stats-grid">
        <StatCard
          title="Dòng sản phẩm"
          value={stats.totalProducts}
          icon={Factory}
          color="blue"
          change={8}
          changeType="positive"
        />
        <StatCard
          title="Lô đang sản xuất"
          value={stats.activeBatches}
          icon={Package}
          color="orange"
          change={12}
          changeType="positive"
        />
        <StatCard
          title="Lô hàng đã xuất"
          value={stats.shippedBatches}
          icon={Truck}
          color="green"
          change={15}
          changeType="positive"
        />
        <StatCard
          title="Nhà phân phối"
          value={stats.totalDistributors}
          icon={Users}
          color="purple"
          change={5}
          changeType="positive"
        />
      </div>

      {/* Charts Section */}
      <div className="charts-section">
        <div className="chart-card">
          <div className="chart-header">
            <h3>Sản xuất và Xuất hàng theo tháng</h3>
            <p>So sánh khối lượng sản xuất với số lượng đã xuất hàng</p>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    value + ' lô',
                    name === 'production' ? 'Sản xuất' : 'Xuất hàng'
                  ]}
                />
                <Bar dataKey="production" fill="#3498db" name="production" />
                <Bar dataKey="shipped" fill="#27ae60" name="shipped" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="chart-card">
          <div className="chart-header">
            <h3>Phân bố sản xuất theo danh mục</h3>
            <p>Tỷ lệ sản xuất các loại thuốc khác nhau</p>
          </div>
          <div className="chart-container">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={productionData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {productionData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="activities-section">
        <div className="activities-header">
          <h3>Hoạt động gần đây</h3>
          <p>Theo dõi các hoạt động sản xuất và xuất hàng mới nhất</p>
        </div>
        
        <div className="activities-list">
          {recentActivities.length === 0 ? (
            <div className="no-activities">
              <AlertCircle size={48} />
              <p>Chưa có hoạt động nào gần đây</p>
            </div>
          ) : (
            recentActivities.map((activity) => {
              const Icon = activity.icon;
              return (
                <div key={activity.id} className="activity-item">
                  <div className="activity-icon">
                    <Icon size={20} />
                  </div>
                  <div className="activity-content">
                    <div className="activity-message">{activity.message}</div>
                    <div className="activity-time">{formatTimeAgo(activity.timestamp)}</div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="quick-actions">
        <h3>Thao tác nhanh</h3>
        <div className="action-buttons">
          <button className="action-btn action-btn-primary">
            <Plus size={20} />
            Tạo lô thuốc mới
          </button>
          <button className="action-btn action-btn-secondary">
            <Package size={20} />
            Quản lý sản phẩm
          </button>
          <button className="action-btn action-btn-accent">
            <Truck size={20} />
            Tạo lô hàng xuất
          </button>
          <button className="action-btn action-btn-neutral">
            <BarChart3 size={20} />
            Xem báo cáo
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

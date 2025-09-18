import React, { useState } from 'react';
import { BarChart3, TrendingUp, Package, Truck } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './Reports.css';

const Reports = () => {
  const [reportData] = useState({
    monthlyProduction: [
      { month: 'T7', production: 120000, shipped: 115000 },
      { month: 'T8', production: 135000, shipped: 128000 },
      { month: 'T9', production: 142000, shipped: 138000 },
      { month: 'T10', production: 158000, shipped: 145000 },
      { month: 'T11', production: 165000, shipped: 162000 },
      { month: 'T12', production: 175000, shipped: 168000 }
    ]
  });

  return (
    <div className="reports">
      <div className="page-header">
        <h1>
          <BarChart3 className="page-icon" />
          Báo cáo & Thống kê
        </h1>
        <p>Theo dõi trạng thái các lô hàng và xuất báo cáo về sản lượng</p>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon production">
            <Package size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-value">1,295,000</div>
            <div className="metric-label">Tổng sản lượng (viên)</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon shipped">
            <Truck size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-value">1,256,000</div>
            <div className="metric-label">Đã xuất hàng (viên)</div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon efficiency">
            <TrendingUp size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-value">97%</div>
            <div className="metric-label">Hiệu suất xuất hàng</div>
          </div>
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-header">
          <h3>Sản lượng và Xuất hàng theo tháng</h3>
          <p>So sánh khối lượng sản xuất với số lượng đã xuất hàng</p>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={reportData.monthlyProduction}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip 
                formatter={(value, name) => [
                  value.toLocaleString() + ' viên',
                  name === 'production' ? 'Sản xuất' : 'Xuất hàng'
                ]}
              />
              <Bar dataKey="production" fill="#3498db" name="production" />
              <Bar dataKey="shipped" fill="#27ae60" name="shipped" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default Reports;

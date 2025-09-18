import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Download, 
  Calendar,
  TrendingUp,
  Package,
  ShoppingCart,
  DollarSign,
  FileText,
  RefreshCw
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line } from 'recharts';
// import pharmacyService from '../services/apiService';
import './Reports.css';

const Reports = () => {
  const [activeReport, setActiveReport] = useState('sales');
  const [dateRange, setDateRange] = useState({
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    endDate: new Date().toISOString().split('T')[0]
  });
  const [loading, setLoading] = useState(false);
  const [reportData, setReportData] = useState({});

  const reportTypes = [
    {
      id: 'sales',
      name: 'Báo cáo bán hàng',
      icon: TrendingUp,
      description: 'Doanh thu, sản phẩm bán chạy, xu hướng bán hàng'
    },
    {
      id: 'inventory',
      name: 'Báo cáo tồn kho',
      icon: Package,
      description: 'Tình hình tồn kho, vòng quay hàng tồn, phân tích ABC'
    },
    {
      id: 'receipts',
      name: 'Báo cáo nhập hàng',
      icon: ShoppingCart,
      description: 'Lịch sử nhập hàng, nhà cung cấp, xu hướng nhập'
    }
  ];

  useEffect(() => {
    fetchReportData();
  }, [activeReport, dateRange]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchReportData = async () => {
    try {
      setLoading(true);

      if (activeReport === 'sales') {
        const mockSalesData = {
          summary: {
            totalRevenue: 125500000,
            totalOrders: 847,
            avgOrderValue: 148200,
            bestSellingProduct: 'Paracetamol 500mg'
          },
          dailySales: [
            { date: '2024-09-12', revenue: 4200000, orders: 28 },
            { date: '2024-09-13', revenue: 3800000, orders: 25 },
            { date: '2024-09-14', revenue: 4500000, orders: 32 },
            { date: '2024-09-15', revenue: 3950000, orders: 27 },
            { date: '2024-09-16', revenue: 4800000, orders: 35 },
            { date: '2024-09-17', revenue: 5200000, orders: 38 },
            { date: '2024-09-18', revenue: 4100000, orders: 29 }
          ],
          topProducts: [
            { name: 'Paracetamol 500mg', quantity: 2450, revenue: 12250000, percentage: 9.8 },
            { name: 'Amoxicillin 250mg', quantity: 1680, revenue: 20160000, percentage: 16.1 },
            { name: 'Vitamin C 1000mg', quantity: 1250, revenue: 10000000, percentage: 8.0 },
            { name: 'Metformin 500mg', quantity: 980, revenue: 7350000, percentage: 5.9 },
            { name: 'Aspirin 100mg', quantity: 850, revenue: 5100000, percentage: 4.1 }
          ],
          categorySales: [
            { category: 'Giảm đau hạ sốt', revenue: 25500000, color: '#3498db' },
            { category: 'Kháng sinh', revenue: 35200000, color: '#27ae60' },
            { category: 'Vitamin & KCS', revenue: 18300000, color: '#f39c12' },
            { category: 'Thuốc tim mạch', revenue: 22100000, color: '#e74c3c' },
            { category: 'Thuốc tiêu hóa', revenue: 15800000, color: '#9b59b6' },
            { category: 'Khác', revenue: 8600000, color: '#95a5a6' }
          ]
        };
        setReportData(mockSalesData);
      } 
      else if (activeReport === 'inventory') {
        const mockInventoryData = {
          summary: {
            totalItems: 156,
            totalValue: 285600000,
            lowStockItems: 12,
            expiringItems: 5
          },
          categoryBreakdown: [
            { category: 'Giảm đau hạ sốt', items: 28, value: 45200000, percentage: 15.8 },
            { category: 'Kháng sinh', items: 35, value: 78500000, percentage: 27.5 },
            { category: 'Vitamin & KCS', items: 24, value: 35800000, percentage: 12.5 },
            { category: 'Thuốc tim mạch', items: 22, value: 52100000, percentage: 18.2 },
            { category: 'Thuốc tiêu hóa', items: 18, value: 31200000, percentage: 10.9 },
            { category: 'Khác', items: 29, value: 42800000, percentage: 15.0 }
          ],
          turnoverAnalysis: [
            { month: 'T6', turnover: 2.1 },
            { month: 'T7', turnover: 2.3 },
            { month: 'T8', turnover: 1.9 },
            { month: 'T9', turnover: 2.5 }
          ],
          abcAnalysis: [
            { group: 'A (20%)', items: 31, value: 171360000, percentage: 60.0 },
            { group: 'B (30%)', items: 47, value: 85680000, percentage: 30.0 },
            { group: 'C (50%)', items: 78, value: 28560000, percentage: 10.0 }
          ]
        };
        setReportData(mockInventoryData);
      }
      else if (activeReport === 'receipts') {
        const mockReceiptData = {
          summary: {
            totalReceipts: 45,
            totalValue: 180500000,
            avgReceiptValue: 4011111,
            topSupplier: 'Nhà phân phối ABC'
          },
          monthlyReceipts: [
            { month: 'T6', receipts: 12, value: 38200000 },
            { month: 'T7', receipts: 15, value: 45800000 },
            { month: 'T8', receipts: 10, value: 32500000 },
            { month: 'T9', receipts: 8, value: 28000000 }
          ],
          supplierBreakdown: [
            { supplier: 'Nhà phân phối ABC', receipts: 18, value: 72200000, percentage: 40.0 },
            { supplier: 'Công ty Dược DEF', receipts: 12, value: 54150000, percentage: 30.0 },
            { supplier: 'NPP GHI', receipts: 8, value: 32100000, percentage: 17.8 },
            { supplier: 'Công ty JKL', receipts: 7, value: 22050000, percentage: 12.2 }
          ]
        };
        setReportData(mockReceiptData);
      }
    } catch (error) {
      console.error('Error fetching report data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(value);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('vi-VN');
  };

  const exportReport = () => {
    const reportName = reportTypes.find(r => r.id === activeReport)?.name || 'Báo cáo';
    const fileName = `${reportName}_${dateRange.startDate}_${dateRange.endDate}.pdf`;
    
    // Mock export functionality
    alert(`Đang xuất báo cáo: ${fileName}`);
  };

  const SalesReport = () => (
    <div className="report-content">
      <div className="summary-cards">
        <div className="summary-card revenue">
          <div className="card-icon">
            <DollarSign size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{formatCurrency(reportData.summary?.totalRevenue || 0)}</div>
            <div className="card-label">Tổng doanh thu</div>
          </div>
        </div>
        <div className="summary-card orders">
          <div className="card-icon">
            <ShoppingCart size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{reportData.summary?.totalOrders || 0}</div>
            <div className="card-label">Tổng đơn hàng</div>
          </div>
        </div>
        <div className="summary-card avg">
          <div className="card-icon">
            <TrendingUp size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{formatCurrency(reportData.summary?.avgOrderValue || 0)}</div>
            <div className="card-label">Giá trị TB/đơn</div>
          </div>
        </div>
        <div className="summary-card product">
          <div className="card-icon">
            <Package size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{reportData.summary?.bestSellingProduct || 'N/A'}</div>
            <div className="card-label">Sản phẩm bán chạy</div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Doanh thu theo ngày</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={reportData.dailySales || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tickFormatter={(value) => new Date(value).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' })} />
              <YAxis tickFormatter={(value) => (value / 1000000).toFixed(1) + 'M'} />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'revenue' ? formatCurrency(value) : value,
                  name === 'revenue' ? 'Doanh thu' : 'Đơn hàng'
                ]}
                labelFormatter={(value) => formatDate(value)}
              />
              <Line type="monotone" dataKey="revenue" stroke="#3498db" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Doanh thu theo danh mục</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={reportData.categorySales || []}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ category, percentage }) => `${category}: ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="revenue"
              >
                {(reportData.categorySales || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [formatCurrency(value), 'Doanh thu']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="table-section">
        <h3>Top sản phẩm bán chạy</h3>
        <table className="report-table">
          <thead>
            <tr>
              <th>Sản phẩm</th>
              <th>Số lượng bán</th>
              <th>Doanh thu</th>
              <th>% Tổng doanh thu</th>
            </tr>
          </thead>
          <tbody>
            {(reportData.topProducts || []).map((product, index) => (
              <tr key={index}>
                <td>{product.name}</td>
                <td>{product.quantity.toLocaleString()}</td>
                <td>{formatCurrency(product.revenue)}</td>
                <td>{product.percentage}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const InventoryReport = () => (
    <div className="report-content">
      <div className="summary-cards">
        <div className="summary-card items">
          <div className="card-icon">
            <Package size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{reportData.summary?.totalItems || 0}</div>
            <div className="card-label">Tổng mặt hàng</div>
          </div>
        </div>
        <div className="summary-card value">
          <div className="card-icon">
            <DollarSign size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{formatCurrency(reportData.summary?.totalValue || 0)}</div>
            <div className="card-label">Giá trị tồn kho</div>
          </div>
        </div>
        <div className="summary-card warning">
          <div className="card-icon">
            <Package size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{reportData.summary?.lowStockItems || 0}</div>
            <div className="card-label">Sắp hết hàng</div>
          </div>
        </div>
        <div className="summary-card danger">
          <div className="card-icon">
            <Calendar size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{reportData.summary?.expiringItems || 0}</div>
            <div className="card-label">Sắp hết hạn</div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Phân tích ABC</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={reportData.abcAnalysis || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="group" />
              <YAxis tickFormatter={(value) => (value / 1000000).toFixed(0) + 'M'} />
              <Tooltip formatter={(value) => [formatCurrency(value), 'Giá trị']} />
              <Bar dataKey="value" fill="#3498db" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Vòng quay hàng tồn kho</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={reportData.turnoverAnalysis || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip formatter={(value) => [value.toFixed(1), 'Vòng quay']} />
              <Line type="monotone" dataKey="turnover" stroke="#27ae60" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="table-section">
        <h3>Phân bố theo danh mục</h3>
        <table className="report-table">
          <thead>
            <tr>
              <th>Danh mục</th>
              <th>Số mặt hàng</th>
              <th>Giá trị</th>
              <th>% Tổng giá trị</th>
            </tr>
          </thead>
          <tbody>
            {(reportData.categoryBreakdown || []).map((category, index) => (
              <tr key={index}>
                <td>{category.category}</td>
                <td>{category.items}</td>
                <td>{formatCurrency(category.value)}</td>
                <td>{category.percentage}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const ReceiptsReport = () => (
    <div className="report-content">
      <div className="summary-cards">
        <div className="summary-card receipts">
          <div className="card-icon">
            <ShoppingCart size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{reportData.summary?.totalReceipts || 0}</div>
            <div className="card-label">Tổng lần nhập</div>
          </div>
        </div>
        <div className="summary-card value">
          <div className="card-icon">
            <DollarSign size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{formatCurrency(reportData.summary?.totalValue || 0)}</div>
            <div className="card-label">Tổng giá trị nhập</div>
          </div>
        </div>
        <div className="summary-card avg">
          <div className="card-icon">
            <TrendingUp size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{formatCurrency(reportData.summary?.avgReceiptValue || 0)}</div>
            <div className="card-label">Giá trị TB/lần</div>
          </div>
        </div>
        <div className="summary-card supplier">
          <div className="card-icon">
            <Package size={32} />
          </div>
          <div className="card-content">
            <div className="card-value">{reportData.summary?.topSupplier || 'N/A'}</div>
            <div className="card-label">NCC chính</div>
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>Nhập hàng theo tháng</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={reportData.monthlyReceipts || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis tickFormatter={(value) => (value / 1000000).toFixed(0) + 'M'} />
              <Tooltip 
                formatter={(value, name) => [
                  name === 'value' ? formatCurrency(value) : value,
                  name === 'value' ? 'Giá trị' : 'Số lần'
                ]}
              />
              <Bar dataKey="value" fill="#f39c12" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>Nhà cung cấp</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={reportData.supplierBreakdown || []}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ supplier, percentage }) => `${supplier}: ${percentage}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {(reportData.supplierBreakdown || []).map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={`hsl(${index * 45}, 70%, 50%)`} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => [formatCurrency(value), 'Giá trị']} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="table-section">
        <h3>Chi tiết theo nhà cung cấp</h3>
        <table className="report-table">
          <thead>
            <tr>
              <th>Nhà cung cấp</th>
              <th>Số lần nhập</th>
              <th>Giá trị</th>
              <th>% Tổng giá trị</th>
            </tr>
          </thead>
          <tbody>
            {(reportData.supplierBreakdown || []).map((supplier, index) => (
              <tr key={index}>
                <td>{supplier.supplier}</td>
                <td>{supplier.receipts}</td>
                <td>{formatCurrency(supplier.value)}</td>
                <td>{supplier.percentage}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderReport = () => {
    switch (activeReport) {
      case 'sales':
        return <SalesReport />;
      case 'inventory':
        return <InventoryReport />;
      case 'receipts':
        return <ReceiptsReport />;
      default:
        return <SalesReport />;
    }
  };

  return (
    <div className="reports">
      <div className="page-header">
        <h1>
          <BarChart3 className="page-icon" />
          Báo cáo
        </h1>
        <p>Lịch sử nhập hàng, tồn kho, sản phẩm bán chạy và các phân tích kinh doanh</p>
      </div>

      {/* Report Navigation */}
      <div className="report-nav">
        {reportTypes.map(report => {
          const Icon = report.icon;
          return (
            <button
              key={report.id}
              onClick={() => setActiveReport(report.id)}
              className={`report-nav-item ${activeReport === report.id ? 'active' : ''}`}
            >
              <Icon size={20} />
              <div>
                <div className="nav-title">{report.name}</div>
                <div className="nav-desc">{report.description}</div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Controls */}
      <div className="report-controls">
        <div className="date-filters">
          <div className="date-group">
            <label>Từ ngày:</label>
            <input
              type="date"
              value={dateRange.startDate}
              onChange={(e) => setDateRange({...dateRange, startDate: e.target.value})}
              max={dateRange.endDate}
            />
          </div>
          <div className="date-group">
            <label>Đến ngày:</label>
            <input
              type="date"
              value={dateRange.endDate}
              onChange={(e) => setDateRange({...dateRange, endDate: e.target.value})}
              min={dateRange.startDate}
            />
          </div>
          <button 
            onClick={fetchReportData}
            disabled={loading}
            className="btn btn-outline"
          >
            <RefreshCw size={16} />
            {loading ? 'Đang tải...' : 'Làm mới'}
          </button>
        </div>

        <div className="action-buttons">
          <button onClick={exportReport} className="btn btn-primary">
            <Download size={16} />
            Xuất PDF
          </button>
          <button className="btn btn-outline">
            <FileText size={16} />
            In báo cáo
          </button>
        </div>
      </div>

      {/* Report Content */}
      {loading ? (
        <div className="loading-section">
          <RefreshCw className="loading-spinner" />
          <p>Đang tạo báo cáo...</p>
        </div>
      ) : (
        renderReport()
      )}
    </div>
  );
};

export default Reports;

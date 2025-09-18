import React, { useState } from 'react';
import { 
  Search, 
  Filter, 
  Eye, 
  AlertTriangle, 
  Package, 
  Calendar,
  History,
  FileText,
  TrendingDown,
  Clock
} from 'lucide-react';
import './ManageInventory.css';

function ManageInventory() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [expiryFilter, setExpiryFilter] = useState('all');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  // Mock data cho sản phẩm trong kho
  const inventoryData = [
    {
      id: 1,
      name: 'Paracetamol 500mg',
      manufacturer: 'Công ty Dược ABC',
      batchNumber: 'LOT2024001',
      quantity: 850,
      originalQuantity: 1000,
      unit: 'viên',
      manufactureDate: '2024-01-01',
      expireDate: '2025-12-31',
      registrationNumber: 'VD-12345-67',
      status: 'in_stock',
      receivedDate: '2024-01-17',
      distributorName: 'Nhà phân phối ABC',
      shipmentId: 'LOT001234',
      location: 'Kệ A1-01',
      price: 500,
      history: [
        { date: '2024-01-17', action: 'Nhập kho', quantity: 1000, note: 'Nhận từ Nhà phân phối ABC' },
        { date: '2024-01-18', action: 'Xuất bán', quantity: -50, note: 'Bán lẻ' },
        { date: '2024-01-19', action: 'Xuất bán', quantity: -100, note: 'Đơn hàng lớn' }
      ]
    },
    {
      id: 2,
      name: 'Amoxicillin 250mg',
      manufacturer: 'Công ty Dược XYZ',
      batchNumber: 'LOT2024002',
      quantity: 350,
      originalQuantity: 500,
      unit: 'viên',
      manufactureDate: '2023-12-01',
      expireDate: '2025-06-30',
      registrationNumber: 'VD-12345-68',
      status: 'in_stock',
      receivedDate: '2024-01-17',
      distributorName: 'Nhà phân phối ABC',
      shipmentId: 'LOT001234',
      location: 'Kệ A1-02',
      price: 1200,
      history: [
        { date: '2024-01-17', action: 'Nhập kho', quantity: 500, note: 'Nhận từ Nhà phân phối ABC' },
        { date: '2024-01-18', action: 'Xuất bán', quantity: -150, note: 'Bán theo đơn' }
      ]
    },
    {
      id: 3,
      name: 'Vitamin C 1000mg',
      manufacturer: 'Công ty Dược DEF',
      batchNumber: 'LOT2024003',
      quantity: 1800,
      originalQuantity: 2000,
      unit: 'viên',
      manufactureDate: '2024-01-10',
      expireDate: '2026-01-10',
      registrationNumber: 'VD-12345-69',
      status: 'in_stock',
      receivedDate: '2024-01-16',
      distributorName: 'Nhà phân phối XYZ',
      shipmentId: 'LOT001233',
      location: 'Kệ B2-05',
      price: 800,
      history: [
        { date: '2024-01-16', action: 'Nhập kho', quantity: 2000, note: 'Nhận từ Nhà phân phối XYZ' },
        { date: '2024-01-17', action: 'Xuất bán', quantity: -200, note: 'Bán lẻ' }
      ]
    },
    {
      id: 4,
      name: 'Aspirin 300mg',
      manufacturer: 'Công ty Dược GHI',
      batchNumber: 'LOT2024004',
      quantity: 50,
      originalQuantity: 800,
      unit: 'viên',
      manufactureDate: '2023-06-01',
      expireDate: '2024-06-01',
      registrationNumber: 'VD-12345-70',
      status: 'low_stock',
      receivedDate: '2024-01-15',
      distributorName: 'Nhà phân phối DEF',
      shipmentId: 'LOT001232',
      location: 'Kệ C3-01',
      price: 600,
      history: [
        { date: '2024-01-15', action: 'Nhập kho', quantity: 800, note: 'Nhận từ Nhà phân phối DEF' },
        { date: '2024-01-16', action: 'Xuất bán', quantity: -300, note: 'Đơn hàng lớn' },
        { date: '2024-01-17', action: 'Xuất bán', quantity: -450, note: 'Bán theo đơn' }
      ]
    },
    {
      id: 5,
      name: 'Ibuprofen 400mg',
      manufacturer: 'Công ty Dược JKL',
      batchNumber: 'LOT2024005',
      quantity: 420,
      originalQuantity: 600,
      unit: 'viên',
      manufactureDate: '2023-08-01',
      expireDate: '2024-02-15',
      registrationNumber: 'VD-12345-71',
      status: 'expired_soon',
      receivedDate: '2024-01-15',
      distributorName: 'Nhà phân phối DEF',
      shipmentId: 'LOT001232',
      location: 'Kệ C3-02',
      price: 900,
      history: [
        { date: '2024-01-15', action: 'Nhập kho', quantity: 600, note: 'Nhận từ Nhà phân phối DEF' },
        { date: '2024-01-16', action: 'Xuất bán', quantity: -180, note: 'Bán lẻ' }
      ]
    }
  ];

  const getStatusDisplay = (status) => {
    const statusMap = {
      in_stock: { label: 'Còn hàng', class: 'status-in-stock' },
      low_stock: { label: 'Sắp hết hàng', class: 'status-low-stock' },
      expired_soon: { label: 'Sắp hết hạn', class: 'status-expired-soon' }
    };
    return statusMap[status] || { label: status, class: '' };
  };

  const isExpiringSoon = (expireDate) => {
    const today = new Date();
    const expire = new Date(expireDate);
    const diffTime = expire - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 30;
  };

  const filteredInventory = inventoryData.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         product.batchNumber.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || product.status === statusFilter;
    
    let matchesExpiry = true;
    if (expiryFilter === 'expiring') {
      matchesExpiry = isExpiringSoon(product.expireDate);
    } else if (expiryFilter === 'normal') {
      matchesExpiry = !isExpiringSoon(product.expireDate);
    }
    
    return matchesSearch && matchesStatus && matchesExpiry;
  });

  const handleViewDetails = (product) => {
    setSelectedProduct(product);
    setShowHistory(false);
  };

  const handleViewHistory = (product) => {
    setSelectedProduct(product);
    setShowHistory(true);
  };

  const closeModal = () => {
    setSelectedProduct(null);
    setShowHistory(false);
  };

  return (
    <div className="manage-inventory">
      <div className="page-header">
        <h1>Quản lý Kho</h1>
        <p>Theo dõi và quản lý tất cả sản phẩm đã được xác thực trong kho</p>
      </div>

      <div className="inventory-container">
        {/* Summary Cards */}
        <div className="summary-cards">
          <div className="summary-card">
            <Package className="summary-icon" />
            <div className="summary-content">
              <h3>{inventoryData.length}</h3>
              <p>Tổng loại sản phẩm</p>
            </div>
          </div>
          <div className="summary-card warning">
            <TrendingDown className="summary-icon" />
            <div className="summary-content">
              <h3>{inventoryData.filter(p => p.status === 'low_stock').length}</h3>
              <p>Sản phẩm sắp hết</p>
            </div>
          </div>
          <div className="summary-card danger">
            <Clock className="summary-icon" />
            <div className="summary-content">
              <h3>{inventoryData.filter(p => isExpiringSoon(p.expireDate)).length}</h3>
              <p>Sản phẩm sắp hết hạn</p>
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="filters-section">
          <div className="search-wrapper">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Tìm kiếm theo tên thuốc hoặc số lô..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input search-input"
            />
          </div>
          
          <div className="filter-group">
            <div className="filter-item">
              <label htmlFor="status-filter">Trạng thái:</label>
              <select
                id="status-filter"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="input filter-select"
              >
                <option value="all">Tất cả</option>
                <option value="in_stock">Còn hàng</option>
                <option value="low_stock">Sắp hết hàng</option>
                <option value="expired_soon">Sắp hết hạn</option>
              </select>
            </div>
            
            <div className="filter-item">
              <label htmlFor="expiry-filter">Hạn sử dụng:</label>
              <select
                id="expiry-filter"
                value={expiryFilter}
                onChange={(e) => setExpiryFilter(e.target.value)}
                className="input filter-select"
              >
                <option value="all">Tất cả</option>
                <option value="expiring">Sắp hết hạn (30 ngày)</option>
                <option value="normal">Bình thường</option>
              </select>
            </div>
          </div>
        </div>

        {/* Inventory Table */}
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Tên sản phẩm</th>
                <th>Số lô</th>
                <th>Số lượng</th>
                <th>Hạn sử dụng</th>
                <th>Vị trí</th>
                <th>Trạng thái</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {filteredInventory.map(product => {
                const statusInfo = getStatusDisplay(product.status);
                const isExpiring = isExpiringSoon(product.expireDate);
                
                return (
                  <tr key={product.id} className={isExpiring ? 'row-warning' : ''}>
                    <td>
                      <div className="product-cell">
                        <div className="product-name">{product.name}</div>
                        <div className="product-manufacturer">{product.manufacturer}</div>
                      </div>
                    </td>
                    <td className="batch-number">{product.batchNumber}</td>
                    <td>
                      <div className="quantity-cell">
                        <span className="quantity">{product.quantity.toLocaleString()}</span>
                        <span className="unit">{product.unit}</span>
                      </div>
                    </td>
                    <td>
                      <div className="expiry-cell">
                        <span className={isExpiring ? 'expiry-warning' : ''}>
                          {new Date(product.expireDate).toLocaleDateString('vi-VN')}
                        </span>
                      </div>
                    </td>
                    <td>{product.location}</td>
                    <td>
                      <span className={`status-badge ${statusInfo.class}`}>
                        {statusInfo.label}
                      </span>
                    </td>
                    <td>
                      <div className="action-buttons">
                        <button
                          className="btn btn-secondary btn-small"
                          onClick={() => handleViewDetails(product)}
                        >
                          <Eye />
                        </button>
                        <button
                          className="btn btn-secondary btn-small"
                          onClick={() => handleViewHistory(product)}
                        >
                          <History />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          
          {filteredInventory.length === 0 && (
            <div className="empty-state">
              <Package className="empty-icon" />
              <h3>Không tìm thấy sản phẩm nào</h3>
              <p>Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm</p>
            </div>
          )}
        </div>
      </div>

      {/* Detail Modal */}
      {selectedProduct && !showHistory && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Chi tiết sản phẩm</h2>
              <button className="modal-close" onClick={closeModal}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="product-details">
                <div className="detail-section">
                  <h3>Thông tin sản phẩm</h3>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <strong>Tên sản phẩm:</strong>
                      <span>{selectedProduct.name}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Nhà sản xuất:</strong>
                      <span>{selectedProduct.manufacturer}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Số lô:</strong>
                      <span>{selectedProduct.batchNumber}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Số đăng ký:</strong>
                      <span>{selectedProduct.registrationNumber}</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Thông tin kho</h3>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <strong>Số lượng hiện tại:</strong>
                      <span>{selectedProduct.quantity.toLocaleString()} {selectedProduct.unit}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Số lượng ban đầu:</strong>
                      <span>{selectedProduct.originalQuantity.toLocaleString()} {selectedProduct.unit}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Vị trí:</strong>
                      <span>{selectedProduct.location}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Giá bán:</strong>
                      <span>{selectedProduct.price.toLocaleString()} VNĐ/{selectedProduct.unit}</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Thông tin xuất xứ</h3>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <strong>Ngày sản xuất:</strong>
                      <span>{new Date(selectedProduct.manufactureDate).toLocaleDateString('vi-VN')}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Hạn sử dụng:</strong>
                      <span className={isExpiringSoon(selectedProduct.expireDate) ? 'expiry-warning' : ''}>
                        {new Date(selectedProduct.expireDate).toLocaleDateString('vi-VN')}
                      </span>
                    </div>
                    <div className="detail-item">
                      <strong>Nhà phân phối:</strong>
                      <span>{selectedProduct.distributorName}</span>
                    </div>
                    <div className="detail-item">
                      <strong>Mã lô hàng:</strong>
                      <span>{selectedProduct.shipmentId}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* History Modal */}
      {selectedProduct && showHistory && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content history-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Lịch sử di chuyển - {selectedProduct.name}</h2>
              <button className="modal-close" onClick={closeModal}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="history-timeline">
                {selectedProduct.history.map((record, index) => (
                  <div key={index} className="timeline-item">
                    <div className="timeline-date">
                      <Calendar className="timeline-icon" />
                      <span>{new Date(record.date).toLocaleDateString('vi-VN')}</span>
                    </div>
                    <div className="timeline-content">
                      <div className="timeline-action">
                        <span className={`action-badge ${record.action === 'Nhập kho' ? 'action-in' : 'action-out'}`}>
                          {record.action}
                        </span>
                        <span className={`quantity-change ${record.quantity > 0 ? 'quantity-positive' : 'quantity-negative'}`}>
                          {record.quantity > 0 ? '+' : ''}{record.quantity.toLocaleString()} {selectedProduct.unit}
                        </span>
                      </div>
                      <p className="timeline-note">{record.note}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ManageInventory;




import React, { useState, useEffect } from 'react';
import { 
  Package, 
  Search, 
  Filter, 
  Eye, 
  Truck, 
  Calendar,
  MapPin,
  Clock,
  AlertTriangle,
  CheckCircle,
  RefreshCw
} from 'lucide-react';
import './BatchManagement.css';

const BatchManagement = () => {
  const [batches, setBatches] = useState([]);
  const [filteredBatches, setFilteredBatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);

  // Mock data - sẽ thay thế bằng API calls
  useEffect(() => {
    const fetchBatches = async () => {
      setLoading(true);
      
      // Simulate API call
      setTimeout(() => {
        const mockBatches = [
          {
            id: 'BT001234',
            drugName: 'Paracetamol 500mg',
            manufacturer: 'ABC Pharma Ltd',
            quantity: 1000,
            availableQuantity: 750,
            manufactureDate: '2024-01-15',
            expiryDate: '2026-01-15',
            status: 'available',
            qrCode: 'QR_BT001234',
            location: 'Kho A - Kệ 1B',
            registrationNumber: 'VD-123456-24',
            activeIngredient: 'Acetaminophen'
          },
          {
            id: 'BT001235',
            drugName: 'Amoxicillin 250mg',
            manufacturer: 'XYZ Healthcare',
            quantity: 500,
            availableQuantity: 0,
            manufactureDate: '2024-02-01',
            expiryDate: '2025-02-01',
            status: 'out_of_stock',
            qrCode: 'QR_BT001235',
            location: 'Kho B - Kệ 2A',
            registrationNumber: 'VD-789012-24',
            activeIngredient: 'Amoxicillin trihydrate'
          },
          {
            id: 'BT001236',
            drugName: 'Vitamin C 1000mg',
            manufacturer: 'Health Plus Co',
            quantity: 2000,
            availableQuantity: 1850,
            manufactureDate: '2024-03-10',
            expiryDate: '2025-09-10',
            status: 'expiring_soon',
            qrCode: 'QR_BT001236',
            location: 'Kho A - Kệ 3C',
            registrationNumber: 'VD-345678-24',
            activeIngredient: 'Ascorbic acid'
          },
          {
            id: 'BT001237',
            drugName: 'Ibuprofen 400mg',
            manufacturer: 'MediCare Inc',
            quantity: 800,
            availableQuantity: 650,
            manufactureDate: '2024-01-20',
            expiryDate: '2027-01-20',
            status: 'available',
            qrCode: 'QR_BT001237',
            location: 'Kho B - Kệ 1A',
            registrationNumber: 'VD-901234-24',
            activeIngredient: 'Ibuprofen'
          },
          {
            id: 'BT001238',
            drugName: 'Cetirizine 10mg',
            manufacturer: 'PharmaTech Ltd',
            quantity: 1500,
            availableQuantity: 1200,
            manufactureDate: '2024-02-15',
            expiryDate: '2026-08-15',
            status: 'available',
            qrCode: 'QR_BT001238',
            location: 'Kho A - Kệ 2B',
            registrationNumber: 'VD-567890-24',
            activeIngredient: 'Cetirizine dihydrochloride'
          }
        ];
        
        setBatches(mockBatches);
        setFilteredBatches(mockBatches);
        setLoading(false);
      }, 1000);
    };

    fetchBatches();
  }, []);

  // Filter batches based on search and status
  useEffect(() => {
    let filtered = batches;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(batch => 
        batch.drugName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        batch.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        batch.manufacturer.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(batch => batch.status === statusFilter);
    }

    setFilteredBatches(filtered);
  }, [searchTerm, statusFilter, batches]);

  const getStatusBadge = (status) => {
    const statusConfig = {
      available: {
        label: 'Còn hàng',
        className: 'status-available',
        icon: CheckCircle
      },
      out_of_stock: {
        label: 'Hết hàng',
        className: 'status-out-of-stock',
        icon: AlertTriangle
      },
      expiring_soon: {
        label: 'Sắp hết hạn',
        className: 'status-expiring',
        icon: Clock
      }
    };

    const config = statusConfig[status] || statusConfig.available;
    const Icon = config.icon;

    return (
      <span className={`status-badge ${config.className}`}>
        <Icon size={14} />
        {config.label}
      </span>
    );
  };

  const getDaysUntilExpiry = (expiryDate) => {
    const today = new Date();
    const expiry = new Date(expiryDate);
    const diffTime = expiry - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const handleViewDetails = (batch) => {
    setSelectedBatch(batch);
    setShowDetailModal(true);
  };

  const handleCreateShipment = (batchId) => {
    // Navigate to create shipment with pre-filled batch
    console.log('Create shipment for batch:', batchId);
    // TODO: Implement navigation
  };

  const refreshData = () => {
    window.location.reload(); // Simple refresh - replace with proper data refetch
  };

  if (loading) {
    return (
      <div className="batch-management">
        <div className="loading">
          <RefreshCw className="loading-spinner" />
          Đang tải dữ liệu lô hàng...
        </div>
      </div>
    );
  }

  return (
    <div className="batch-management">
      {/* Header */}
      <div className="page-header">
        <div className="header-content">
          <h1>Quản lý Lô hàng</h1>
          <p>Theo dõi và quản lý tất cả lô thuốc trong kho</p>
        </div>
        <button className="btn btn-primary" onClick={refreshData}>
          <RefreshCw size={20} />
          Làm mới
        </button>
      </div>

      {/* Filters */}
      <div className="filters-section">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Tìm kiếm theo tên thuốc, mã lô, nhà sản xuất..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <Filter size={20} />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="available">Còn hàng</option>
            <option value="out_of_stock">Hết hàng</option>
            <option value="expiring_soon">Sắp hết hạn</option>
          </select>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="summary-stats">
        <div className="stat-item">
          <Package className="stat-icon" />
          <div className="stat-info">
            <span className="stat-value">{batches.length}</span>
            <span className="stat-label">Tổng lô hàng</span>
          </div>
        </div>
        <div className="stat-item">
          <CheckCircle className="stat-icon stat-success" />
          <div className="stat-info">
            <span className="stat-value">
              {batches.filter(b => b.status === 'available').length}
            </span>
            <span className="stat-label">Còn hàng</span>
          </div>
        </div>
        <div className="stat-item">
          <AlertTriangle className="stat-icon stat-warning" />
          <div className="stat-info">
            <span className="stat-value">
              {batches.filter(b => b.status === 'out_of_stock').length}
            </span>
            <span className="stat-label">Hết hàng</span>
          </div>
        </div>
        <div className="stat-item">
          <Clock className="stat-icon stat-danger" />
          <div className="stat-info">
            <span className="stat-value">
              {batches.filter(b => b.status === 'expiring_soon').length}
            </span>
            <span className="stat-label">Sắp hết hạn</span>
          </div>
        </div>
      </div>

      {/* Batches Table */}
      <div className="table-container">
        <table className="batches-table">
          <thead>
            <tr>
              <th>Mã lô</th>
              <th>Tên thuốc</th>
              <th>Nhà sản xuất</th>
              <th>Số lượng</th>
              <th>Ngày hết hạn</th>
              <th>Trạng thái</th>
              <th>Thao tác</th>
            </tr>
          </thead>
          <tbody>
            {filteredBatches.map((batch) => {
              const daysUntilExpiry = getDaysUntilExpiry(batch.expiryDate);
              
              return (
                <tr key={batch.id}>
                  <td>
                    <div className="batch-id">
                      <strong>{batch.id}</strong>
                      <span className="qr-code">{batch.qrCode}</span>
                    </div>
                  </td>
                  <td>
                    <div className="drug-info">
                      <strong>{batch.drugName}</strong>
                      <span className="ingredient">{batch.activeIngredient}</span>
                    </div>
                  </td>
                  <td>{batch.manufacturer}</td>
                  <td>
                    <div className="quantity-info">
                      <span className="available">{batch.availableQuantity}</span>
                      <span className="total">/ {batch.quantity}</span>
                    </div>
                  </td>
                  <td>
                    <div className="expiry-info">
                      <span className="date">{batch.expiryDate}</span>
                      <span className={`days-left ${daysUntilExpiry < 90 ? 'warning' : ''}`}>
                        {daysUntilExpiry} ngày
                      </span>
                    </div>
                  </td>
                  <td>{getStatusBadge(batch.status)}</td>
                  <td>
                    <div className="action-buttons">
                      <button
                        className="btn-icon btn-view"
                        onClick={() => handleViewDetails(batch)}
                        title="Xem chi tiết"
                      >
                        <Eye size={16} />
                      </button>
                      <button
                        className="btn-icon btn-ship"
                        onClick={() => handleCreateShipment(batch.id)}
                        title="Tạo shipment"
                        disabled={batch.availableQuantity === 0}
                      >
                        <Truck size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {filteredBatches.length === 0 && (
          <div className="empty-state">
            <Package size={48} />
            <h3>Không tìm thấy lô hàng</h3>
            <p>Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm</p>
          </div>
        )}
      </div>

      {/* Batch Detail Modal */}
      {showDetailModal && selectedBatch && (
        <div className="modal-overlay" onClick={() => setShowDetailModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Chi tiết lô hàng {selectedBatch.id}</h2>
              <button 
                className="modal-close"
                onClick={() => setShowDetailModal(false)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <div className="detail-grid">
                <div className="detail-group">
                  <h3>Thông tin thuốc</h3>
                  <div className="detail-item">
                    <label>Tên thuốc:</label>
                    <span>{selectedBatch.drugName}</span>
                  </div>
                  <div className="detail-item">
                    <label>Hoạt chất:</label>
                    <span>{selectedBatch.activeIngredient}</span>
                  </div>
                  <div className="detail-item">
                    <label>Số đăng ký:</label>
                    <span>{selectedBatch.registrationNumber}</span>
                  </div>
                </div>

                <div className="detail-group">
                  <h3>Thông tin sản xuất</h3>
                  <div className="detail-item">
                    <label>Nhà sản xuất:</label>
                    <span>{selectedBatch.manufacturer}</span>
                  </div>
                  <div className="detail-item">
                    <label>Ngày sản xuất:</label>
                    <span>{selectedBatch.manufactureDate}</span>
                  </div>
                  <div className="detail-item">
                    <label>Ngày hết hạn:</label>
                    <span>{selectedBatch.expiryDate}</span>
                  </div>
                </div>

                <div className="detail-group">
                  <h3>Thông tin kho</h3>
                  <div className="detail-item">
                    <label>Vị trí:</label>
                    <span>{selectedBatch.location}</span>
                  </div>
                  <div className="detail-item">
                    <label>Tổng số lượng:</label>
                    <span>{selectedBatch.quantity} viên</span>
                  </div>
                  <div className="detail-item">
                    <label>Còn lại:</label>
                    <span>{selectedBatch.availableQuantity} viên</span>
                  </div>
                </div>

                <div className="detail-group">
                  <h3>Blockchain</h3>
                  <div className="detail-item">
                    <label>QR Code:</label>
                    <span className="qr-code-display">{selectedBatch.qrCode}</span>
                  </div>
                  <div className="detail-item">
                    <label>Trạng thái:</label>
                    {getStatusBadge(selectedBatch.status)}
                  </div>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button 
                className="btn btn-primary"
                onClick={() => handleCreateShipment(selectedBatch.id)}
              >
                <Truck size={16} />
                Tạo Shipment
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => setShowDetailModal(false)}
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BatchManagement;

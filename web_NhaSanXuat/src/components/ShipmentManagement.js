import React, { useState, useEffect } from 'react';
import { 
  Truck, 
  Plus, 
  Eye, 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  Package, 
  Building, 
  MapPin,
  Calendar,
  User,
  Hash,
  X,
  Save
} from 'lucide-react';
import manufacturerService from '../services/apiService';
import './ShipmentManagement.css';

const ShipmentManagement = () => {
  const [shipments, setShipments] = useState([]);
  const [availableBatches, setAvailableBatches] = useState([]);
  const [distributors, setDistributors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Form states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState('');
  const [selectedDistributor, setSelectedDistributor] = useState('');
  const [shipmentQuantity, setShipmentQuantity] = useState('');
  const [trackingInfo, setTrackingInfo] = useState('');
  const [creating, setCreating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load existing shipments
      const shipmentsResponse = await manufacturerService.getShipments();
      if (shipmentsResponse.success) {
        setShipments(shipmentsResponse.data);
      }

      // Load available batches for shipment
      try {
        const batchesResponse = await manufacturerService.getBatchesReadyForShipment();
        if (batchesResponse.success) {
          setAvailableBatches(batchesResponse.data);
        }
      } catch (err) {
        console.warn('Failed to get ready batches, trying all batches:', err.message);
        try {
          const allBatchesResponse = await manufacturerService.getBatches();
          if (allBatchesResponse.success) {
            setAvailableBatches(allBatchesResponse.data);
          }
        } catch (batchErr) {
          console.error('Failed to get batches:', batchErr.message);
          setError('Không thể tải danh sách lô thuốc');
        }
      }

      // Load distributors
      try {
        const distributorsResponse = await manufacturerService.getDistributors();
        if (distributorsResponse.success) {
          setDistributors(distributorsResponse.data);
        }
      } catch (err) {
        console.error('Failed to get distributors:', err.message);
        setError('Không thể tải danh sách nhà phân phối');
      }

    } catch (err) {
      console.error('Error loading data:', err);
      setError('Không thể tải dữ liệu: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateShipment = async () => {
    if (!selectedBatch || !selectedDistributor || !shipmentQuantity) {
      setError('Vui lòng điền đầy đủ thông tin bắt buộc');
      return;
    }

    const batch = availableBatches.find(b => b.batchId == selectedBatch);
    const distributor = distributors.find(d => d.id == selectedDistributor);

    if (!batch || !distributor) {
      setError('Thông tin lô thuốc hoặc nhà phân phối không hợp lệ');
      return;
    }

    if (parseInt(shipmentQuantity) > batch.quantity) {
      setError('Số lượng vận chuyển không được vượt quá số lượng trong lô');
      return;
    }

    try {
      setCreating(true);
      setError(null);

      const shipmentData = {
        batchId: selectedBatch, // Keep as string for BigInteger parsing
        toAddress: distributor.walletAddress,
        quantity: parseInt(shipmentQuantity),
        trackingInfo: trackingInfo || `Shipment to ${distributor.name}`
      };

      console.log('Creating shipment with data:', shipmentData);

      const response = await manufacturerService.createShipment(shipmentData);

      if (response.success) {
        setSuccess(`Tạo lô hàng thành công! 
        Mã lô hàng: ${response.data.shipmentId || 'N/A'}
        Transaction Hash: ${response.data.transactionHash || 'N/A'}`);
        
        // Reset form
        setSelectedBatch('');
        setSelectedDistributor('');
        setShipmentQuantity('');
        setTrackingInfo('');
        setShowCreateModal(false);
        
        // Reload data
        await loadData();
      } else {
        setError(response.message || 'Không thể tạo lô hàng');
      }
    } catch (err) {
      console.error('Error creating shipment:', err);
      setError('Lỗi tạo lô hàng: ' + err.message);
    } finally {
      setCreating(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'DELIVERED':
      case 'delivered':
        return <CheckCircle size={14} className="text-green-600" />;
      case 'IN_TRANSIT':
      case 'in_transit':
        return <Truck size={14} className="text-blue-600" />;
      case 'PENDING':
      case 'pending':
        return <Clock size={14} className="text-yellow-600" />;
      default:
        return <AlertCircle size={14} className="text-gray-600" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'DELIVERED':
      case 'delivered':
        return 'Đã giao';
      case 'IN_TRANSIT':
      case 'in_transit':
        return 'Đang giao';
      case 'PENDING':
      case 'pending':
        return 'Chờ xử lý';
      default:
        return 'Không xác định';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('vi-VN');
  };

  if (loading) {
    return (
      <div className="shipment-management">
        <div className="loading">Đang tải dữ liệu...</div>
      </div>
    );
  }

  return (
    <div className="shipment-management">
      <div className="page-header">
        <h1>
          <Truck className="page-icon" />
          Quản lý Xuất hàng
        </h1>
        <p>Tạo và quản lý các lệnh vận chuyển đến nhà phân phối</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {success && (
        <div className="alert alert-success">
          <CheckCircle size={20} />
          {success}
        </div>
      )}

      {/* Action buttons */}
      <div className="action-buttons">
        <button 
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary"
          disabled={availableBatches.length === 0 || distributors.length === 0}
        >
          <Plus size={16} />
          Tạo lô hàng mới
        </button>
        <button onClick={loadData} className="btn btn-outline">
          Làm mới
        </button>
      </div>

      {/* Statistics */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <Package />
          </div>
          <div className="stat-content">
            <h3>{availableBatches.length}</h3>
            <p>Lô sẵn sàng xuất</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Building />
          </div>
          <div className="stat-content">
            <h3>{distributors.length}</h3>
            <p>Nhà phân phối</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <Truck />
          </div>
          <div className="stat-content">
            <h3>{shipments.length}</h3>
            <p>Tổng lô hàng</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <CheckCircle />
          </div>
          <div className="stat-content">
            <h3>{shipments.filter(s => s.status === 'DELIVERED' || s.status === 'delivered').length}</h3>
            <p>Đã giao thành công</p>
          </div>
        </div>
      </div>

      {/* Shipments table */}
      <div className="shipments-table-container">
        <h2>Danh sách lô hàng ({shipments.length})</h2>
        {shipments.length === 0 ? (
          <div className="no-data">
            <Package size={48} className="no-data-icon" />
            <h3>Chưa có lô hàng nào</h3>
            <p>Tạo lô hàng đầu tiên để bắt đầu</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="shipments-table">
              <thead>
                <tr>
                  <th>Mã lô hàng</th>
                  <th>Lô thuốc</th>
                  <th>Sản phẩm</th>
                  <th>Người nhận</th>
                  <th>Số lượng</th>
                  <th>Trạng thái</th>
                  <th>Ngày tạo</th>
                  <th>Thao tác</th>
                </tr>
              </thead>
              <tbody>
                {shipments.map(shipment => (
                  <tr key={shipment.id}>
                    <td>
                      <div className="shipment-id">
                        <Hash size={14} />
                        {shipment.shipmentId || shipment.id}
                      </div>
                    </td>
                    <td>{shipment.drugBatch?.batchNumber || 'N/A'}</td>
                    <td>{shipment.drugBatch?.drugName || 'N/A'}</td>
                    <td>
                      <div className="recipient-info">
                        <Building size={14} />
                        {shipment.toAddress}
                      </div>
                    </td>
                    <td>{shipment.quantity?.toLocaleString() || 'N/A'}</td>
                    <td>
                      <span className={`status-badge status-${shipment.status?.toLowerCase()}`}>
                        {getStatusIcon(shipment.status)}
                        {getStatusText(shipment.status)}
                      </span>
                    </td>
                    <td>{formatDate(shipment.shipmentTimestamp || shipment.createdAt)}</td>
                    <td>
                      <button className="btn btn-outline btn-sm">
                        <Eye size={14} />
                        Chi tiết
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Shipment Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Tạo lô hàng mới</h3>
              <button onClick={() => setShowCreateModal(false)} className="modal-close">
                <X size={20} />
              </button>
            </div>

            <div className="modal-body">
              {/* Select Batch */}
              <div className="form-group">
                <label>Chọn lô thuốc *</label>
                <select
                  value={selectedBatch}
                  onChange={(e) => setSelectedBatch(e.target.value)}
                  className="form-control"
                  required
                >
                  <option value="">-- Chọn lô thuốc --</option>
                  {availableBatches.map(batch => (
                    <option key={batch.batchId} value={batch.batchId}>
                      {batch.batchNumber} - {batch.drugName} ({batch.quantity} viên)
                    </option>
                  ))}
                </select>
                {availableBatches.length === 0 && (
                  <p className="form-help">Không có lô thuốc nào sẵn sàng để xuất</p>
                )}
              </div>

              {/* Select Distributor */}
              <div className="form-group">
                <label>Chọn nhà phân phối *</label>
                <select
                  value={selectedDistributor}
                  onChange={(e) => setSelectedDistributor(e.target.value)}
                  className="form-control"
                  required
                >
                  <option value="">-- Chọn nhà phân phối --</option>
                  {distributors.map(distributor => (
                    <option key={distributor.id} value={distributor.id}>
                      {distributor.name} - {distributor.address}
                    </option>
                  ))}
                </select>
                {distributors.length === 0 && (
                  <p className="form-help">Không có nhà phân phối nào khả dụng</p>
                )}
              </div>

              {/* Quantity */}
              <div className="form-group">
                <label>Số lượng *</label>
                <input
                  type="number"
                  value={shipmentQuantity}
                  onChange={(e) => setShipmentQuantity(e.target.value)}
                  className="form-control"
                  min="1"
                  max={selectedBatch ? availableBatches.find(b => b.batchId == selectedBatch)?.quantity : undefined}
                  placeholder="Nhập số lượng"
                  required
                />
                {selectedBatch && (
                  <p className="form-help">
                    Tối đa: {availableBatches.find(b => b.batchId == selectedBatch)?.quantity || 0} viên
                  </p>
                )}
              </div>

              {/* Tracking Info */}
              <div className="form-group">
                <label>Thông tin theo dõi</label>
                <textarea
                  value={trackingInfo}
                  onChange={(e) => setTrackingInfo(e.target.value)}
                  className="form-control"
                  rows="3"
                  placeholder="Ghi chú về lô hàng (tùy chọn)"
                />
              </div>
            </div>

            <div className="modal-footer">
              <button 
                onClick={() => setShowCreateModal(false)}
                className="btn btn-secondary"
                disabled={creating}
              >
                Hủy
              </button>
              <button 
                onClick={handleCreateShipment}
                className="btn btn-primary"
                disabled={creating || !selectedBatch || !selectedDistributor || !shipmentQuantity}
              >
                <Save size={16} />
                {creating ? 'Đang tạo...' : 'Tạo lô hàng'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShipmentManagement;
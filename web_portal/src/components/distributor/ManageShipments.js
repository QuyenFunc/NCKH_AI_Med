import React, { useState } from 'react';
import { Search, Filter, Eye, Calendar, MapPin, Package } from 'lucide-react';
import './ManageShipments.css';

function ManageShipments() {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');
  const [selectedShipment, setSelectedShipment] = useState(null);

  // Mock data cho lô hàng
  const shipments = [
    {
      id: 'LOT001234',
      pharmacy: 'Hiệu thuốc ABC',
      pharmacyAddress: '123 Nguyễn Trãi, Q1, HCM',
      createdDate: '2024-01-15',
      deliveryDate: '2024-01-17',
      status: 'shipping',
      items: [
        { name: 'Paracetamol 500mg', quantity: 1000, batchNumber: 'LOT2024001' },
        { name: 'Amoxicillin 250mg', quantity: 500, batchNumber: 'LOT2024002' }
      ],
      transportMethod: 'Xe tải',
      notes: 'Giao hàng trong giờ hành chính'
    },
    {
      id: 'LOT001233',
      pharmacy: 'Hiệu thuốc XYZ',
      pharmacyAddress: '456 Lê Lợi, Q3, HCM',
      createdDate: '2024-01-14',
      deliveryDate: '2024-01-16',
      status: 'delivered',
      items: [
        { name: 'Vitamin C 1000mg', quantity: 2000, batchNumber: 'LOT2024003' }
      ],
      transportMethod: 'Xe van',
      notes: ''
    },
    {
      id: 'LOT001232',
      pharmacy: 'Hiệu thuốc DEF',
      pharmacyAddress: '789 Hai Bà Trưng, Q1, HCM',
      createdDate: '2024-01-13',
      deliveryDate: '2024-01-15',
      status: 'delayed',
      items: [
        { name: 'Aspirin 300mg', quantity: 800, batchNumber: 'LOT2024004' },
        { name: 'Ibuprofen 400mg', quantity: 600, batchNumber: 'LOT2024005' }
      ],
      transportMethod: 'Xe tải',
      notes: 'Khách hàng yêu cầu gọi trước khi giao'
    },
    {
      id: 'LOT001231',
      pharmacy: 'Hiệu thuốc GHI',
      pharmacyAddress: '321 Điện Biên Phủ, Q10, HCM',
      createdDate: '2024-01-12',
      deliveryDate: '2024-01-14',
      status: 'delivered',
      items: [
        { name: 'Cetirizine 10mg', quantity: 1200, batchNumber: 'LOT2024006' }
      ],
      transportMethod: 'Xe máy',
      notes: ''
    },
    {
      id: 'LOT001230',
      pharmacy: 'Hiệu thuốc JKL',
      pharmacyAddress: '654 Cách Mạng Tháng Tám, Q3, HCM',
      createdDate: '2024-01-11',
      deliveryDate: '2024-01-13',
      status: 'shipping',
      items: [
        { name: 'Omeprazole 20mg', quantity: 400, batchNumber: 'LOT2024007' }
      ],
      transportMethod: 'Xe van',
      notes: 'Hàng dễ vỡ, cẩn thận khi vận chuyển'
    }
  ];

  const getStatusDisplay = (status) => {
    const statusMap = {
      shipping: { label: 'Đang vận chuyển', class: 'status-shipping' },
      delivered: { label: 'Đã giao thành công', class: 'status-delivered' },
      delayed: { label: 'Trễ hẹn', class: 'status-delayed' }
    };
    return statusMap[status] || { label: status, class: '' };
  };

  const filteredShipments = shipments.filter(shipment => {
    const matchesSearch = shipment.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         shipment.pharmacy.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || shipment.status === statusFilter;
    
    let matchesDate = true;
    if (dateFilter !== 'all') {
      const today = new Date();
      const shipmentDate = new Date(shipment.createdDate);
      const diffTime = Math.abs(today - shipmentDate);
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      switch (dateFilter) {
        case 'today':
          matchesDate = diffDays <= 1;
          break;
        case 'week':
          matchesDate = diffDays <= 7;
          break;
        case 'month':
          matchesDate = diffDays <= 30;
          break;
        default:
          matchesDate = true;
      }
    }
    
    return matchesSearch && matchesStatus && matchesDate;
  });

  const handleViewDetails = (shipment) => {
    setSelectedShipment(shipment);
  };

  const closeModal = () => {
    setSelectedShipment(null);
  };

  return (
    <div className="manage-shipments">
      <div className="page-header">
        <h1>Quản lý Lô hàng</h1>
        <p>Theo dõi và quản lý tất cả các lô hàng đã gửi</p>
      </div>

      <div className="shipments-container">
        {/* Filters */}
        <div className="filters-section">
          <div className="search-wrapper">
            <Search className="search-icon" />
            <input
              type="text"
              placeholder="Tìm kiếm theo mã lô hàng hoặc tên hiệu thuốc..."
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
                <option value="shipping">Đang vận chuyển</option>
                <option value="delivered">Đã giao</option>
                <option value="delayed">Trễ hẹn</option>
              </select>
            </div>
            
            <div className="filter-item">
              <label htmlFor="date-filter">Thời gian:</label>
              <select
                id="date-filter"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="input filter-select"
              >
                <option value="all">Tất cả</option>
                <option value="today">Hôm nay</option>
                <option value="week">7 ngày qua</option>
                <option value="month">30 ngày qua</option>
              </select>
            </div>
          </div>
        </div>

        {/* Shipments Table */}
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Mã lô hàng</th>
                <th>Người nhận</th>
                <th>Ngày tạo</th>
                <th>Ngày giao</th>
                <th>Trạng thái</th>
                <th>Thao tác</th>
              </tr>
            </thead>
            <tbody>
              {filteredShipments.map(shipment => {
                const statusInfo = getStatusDisplay(shipment.status);
                return (
                  <tr key={shipment.id}>
                    <td className="shipment-id">{shipment.id}</td>
                    <td>
                      <div className="pharmacy-cell">
                        <div className="pharmacy-name">{shipment.pharmacy}</div>
                        <div className="pharmacy-address">{shipment.pharmacyAddress}</div>
                      </div>
                    </td>
                    <td>{new Date(shipment.createdDate).toLocaleDateString('vi-VN')}</td>
                    <td>{new Date(shipment.deliveryDate).toLocaleDateString('vi-VN')}</td>
                    <td>
                      <span className={`status-badge ${statusInfo.class}`}>
                        {statusInfo.label}
                      </span>
                    </td>
                    <td>
                      <button
                        className="btn btn-secondary btn-small"
                        onClick={() => handleViewDetails(shipment)}
                      >
                        <Eye />
                        Xem chi tiết
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          
          {filteredShipments.length === 0 && (
            <div className="empty-state">
              <Package className="empty-icon" />
              <h3>Không tìm thấy lô hàng nào</h3>
              <p>Thử thay đổi bộ lọc hoặc từ khóa tìm kiếm</p>
            </div>
          )}
        </div>
      </div>

      {/* Detail Modal */}
      {selectedShipment && (
        <div className="modal-overlay" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Chi tiết lô hàng {selectedShipment.id}</h2>
              <button className="modal-close" onClick={closeModal}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="detail-section">
                <h3>Thông tin giao hàng</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <MapPin className="detail-icon" />
                    <div>
                      <strong>Người nhận:</strong>
                      <p>{selectedShipment.pharmacy}</p>
                      <p>{selectedShipment.pharmacyAddress}</p>
                    </div>
                  </div>
                  <div className="detail-item">
                    <Calendar className="detail-icon" />
                    <div>
                      <strong>Thời gian:</strong>
                      <p>Tạo: {new Date(selectedShipment.createdDate).toLocaleDateString('vi-VN')}</p>
                      <p>Giao: {new Date(selectedShipment.deliveryDate).toLocaleDateString('vi-VN')}</p>
                    </div>
                  </div>
                </div>
                <div className="detail-item">
                  <strong>Phương tiện vận chuyển:</strong> {selectedShipment.transportMethod}
                </div>
                {selectedShipment.notes && (
                  <div className="detail-item">
                    <strong>Ghi chú:</strong> {selectedShipment.notes}
                  </div>
                )}
              </div>
              
              <div className="detail-section">
                <h3>Danh sách sản phẩm</h3>
                <div className="products-list">
                  {selectedShipment.items.map((item, index) => (
                    <div key={index} className="product-item">
                      <Package className="product-icon" />
                      <div className="product-info">
                        <h4>{item.name}</h4>
                        <p>Số lượng: {item.quantity}</p>
                        <p>Số lô: {item.batchNumber}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ManageShipments;




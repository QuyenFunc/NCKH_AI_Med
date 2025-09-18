import React, { useState, useEffect } from 'react';
import { Package, Truck, MapPin, Clock, CheckCircle, AlertCircle, Search, Filter } from 'lucide-react';
import './ShipmentTracking.css';

const ShipmentTracking = () => {
    const [shipments, setShipments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [statusFilter, setStatusFilter] = useState('all');
    const [selectedShipment, setSelectedShipment] = useState(null);

    useEffect(() => {
        fetchShipments();
    }, []);

    const fetchShipments = async () => {
        try {
            setLoading(true);
            // Mock data - replace with actual API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const mockShipments = [
                {
                    id: 'SH001',
                    batchId: 'BT2024001',
                    from: 'Nhà sản xuất ABC',
                    to: 'Hiệu thuốc XYZ',
                    status: 'in_transit',
                    createdAt: '2024-09-18T10:00:00Z',
                    estimatedDelivery: '2024-09-20T15:00:00Z',
                    currentLocation: 'Kho trung chuyển Hà Nội',
                    trackingNumber: 'TRK001234567',
                    quantity: 100,
                    drugName: 'Paracetamol 500mg'
                },
                {
                    id: 'SH002',
                    batchId: 'BT2024002',
                    from: 'Nhà sản xuất DEF',
                    to: 'Hiệu thuốc ABC',
                    status: 'delivered',
                    createdAt: '2024-09-17T09:30:00Z',
                    deliveredAt: '2024-09-18T14:20:00Z',
                    currentLocation: 'Đã giao hàng',
                    trackingNumber: 'TRK001234568',
                    quantity: 50,
                    drugName: 'Amoxicillin 250mg'
                },
                {
                    id: 'SH003',
                    batchId: 'BT2024003',
                    from: 'Nhà sản xuất GHI',
                    to: 'Hiệu thuốc DEF',
                    status: 'pending',
                    createdAt: '2024-09-18T14:15:00Z',
                    estimatedDelivery: '2024-09-21T10:00:00Z',
                    currentLocation: 'Chờ xuất kho',
                    trackingNumber: 'TRK001234569',
                    quantity: 200,
                    drugName: 'Vitamin C 1000mg'
                }
            ];
            
            setShipments(mockShipments);
        } catch (err) {
            setError('Không thể tải danh sách lô hàng: ' + err.message);
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (status) => {
        switch (status) {
            case 'pending':
                return <Clock className="status-icon pending" />;
            case 'in_transit':
                return <Truck className="status-icon transit" />;
            case 'delivered':
                return <CheckCircle className="status-icon delivered" />;
            default:
                return <AlertCircle className="status-icon unknown" />;
        }
    };

    const getStatusText = (status) => {
        switch (status) {
            case 'pending':
                return 'Chờ xuất kho';
            case 'in_transit':
                return 'Đang vận chuyển';
            case 'delivered':
                return 'Đã giao hàng';
            default:
                return 'Không xác định';
        }
    };

    const getStatusClass = (status) => {
        switch (status) {
            case 'pending':
                return 'status-pending';
            case 'in_transit':
                return 'status-transit';
            case 'delivered':
                return 'status-delivered';
            default:
                return 'status-unknown';
        }
    };

    const filteredShipments = shipments.filter(shipment => {
        const matchesSearch = 
            shipment.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
            shipment.batchId.toLowerCase().includes(searchTerm.toLowerCase()) ||
            shipment.trackingNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
            shipment.drugName.toLowerCase().includes(searchTerm.toLowerCase());
        
        const matchesStatus = statusFilter === 'all' || shipment.status === statusFilter;
        
        return matchesSearch && matchesStatus;
    });

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const trackShipment = (shipment) => {
        setSelectedShipment(shipment);
    };

    const closeTrackingModal = () => {
        setSelectedShipment(null);
    };

    if (loading) {
        return (
            <div className="shipment-tracking">
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p>Đang tải danh sách lô hàng...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="shipment-tracking">
            <div className="page-header">
                <h1>
                    <Truck className="page-icon" />
                    Theo dõi Lô hàng
                </h1>
                <p>Quản lý và theo dõi trạng thái các lô hàng đã gửi</p>
            </div>

            {error && (
                <div className="alert alert-error">
                    <AlertCircle size={20} />
                    {error}
                </div>
            )}

            <div className="controls">
                <div className="search-box">
                    <Search className="search-icon" />
                    <input
                        type="text"
                        placeholder="Tìm kiếm theo mã lô hàng, mã batch, mã vận đơn hoặc tên thuốc..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="search-input"
                    />
                </div>

                <div className="filter-box">
                    <Filter className="filter-icon" />
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="filter-select"
                    >
                        <option value="all">Tất cả trạng thái</option>
                        <option value="pending">Chờ xuất kho</option>
                        <option value="in_transit">Đang vận chuyển</option>
                        <option value="delivered">Đã giao hàng</option>
                    </select>
                </div>
            </div>

            <div className="shipments-grid">
                {filteredShipments.length === 0 ? (
                    <div className="no-data">
                        <Package size={64} className="no-data-icon" />
                        <h3>Không có lô hàng nào</h3>
                        <p>
                            {searchTerm || statusFilter !== 'all' 
                                ? 'Không tìm thấy lô hàng nào phù hợp với bộ lọc.'
                                : 'Chưa có lô hàng nào được tạo.'
                            }
                        </p>
                    </div>
                ) : (
                    filteredShipments.map(shipment => (
                        <div key={shipment.id} className="shipment-card">
                            <div className="card-header">
                                <div className="shipment-id">
                                    <Package size={20} />
                                    <span>{shipment.id}</span>
                                </div>
                                <div className={`status-badge ${getStatusClass(shipment.status)}`}>
                                    {getStatusIcon(shipment.status)}
                                    {getStatusText(shipment.status)}
                                </div>
                            </div>

                            <div className="card-content">
                                <div className="info-row">
                                    <span className="label">Mã Batch:</span>
                                    <span className="value">{shipment.batchId}</span>
                                </div>
                                <div className="info-row">
                                    <span className="label">Thuốc:</span>
                                    <span className="value">{shipment.drugName}</span>
                                </div>
                                <div className="info-row">
                                    <span className="label">Số lượng:</span>
                                    <span className="value">{shipment.quantity} viên</span>
                                </div>
                                <div className="info-row">
                                    <span className="label">Từ:</span>
                                    <span className="value">{shipment.from}</span>
                                </div>
                                <div className="info-row">
                                    <span className="label">Đến:</span>
                                    <span className="value">{shipment.to}</span>
                                </div>
                                <div className="info-row">
                                    <span className="label">Vị trí hiện tại:</span>
                                    <span className="value">
                                        <MapPin size={16} />
                                        {shipment.currentLocation}
                                    </span>
                                </div>
                                <div className="info-row">
                                    <span className="label">Ngày tạo:</span>
                                    <span className="value">{formatDate(shipment.createdAt)}</span>
                                </div>
                                {shipment.estimatedDelivery && (
                                    <div className="info-row">
                                        <span className="label">Dự kiến giao:</span>
                                        <span className="value">{formatDate(shipment.estimatedDelivery)}</span>
                                    </div>
                                )}
                                {shipment.deliveredAt && (
                                    <div className="info-row">
                                        <span className="label">Đã giao lúc:</span>
                                        <span className="value delivered">{formatDate(shipment.deliveredAt)}</span>
                                    </div>
                                )}
                            </div>

                            <div className="card-actions">
                                <button
                                    onClick={() => trackShipment(shipment)}
                                    className="btn btn-primary"
                                >
                                    <Search size={16} />
                                    Chi tiết theo dõi
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Tracking Detail Modal */}
            {selectedShipment && (
                <div className="modal-overlay" onClick={closeTrackingModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Chi tiết theo dõi lô hàng {selectedShipment.id}</h2>
                            <button onClick={closeTrackingModal} className="close-button">×</button>
                        </div>
                        <div className="modal-body">
                            <div className="tracking-info">
                                <div className="info-section">
                                    <h3>Thông tin chung</h3>
                                    <div className="info-grid">
                                        <div className="info-item">
                                            <span className="label">Mã vận đơn:</span>
                                            <span className="value">{selectedShipment.trackingNumber}</span>
                                        </div>
                                        <div className="info-item">
                                            <span className="label">Trạng thái:</span>
                                            <span className={`value ${getStatusClass(selectedShipment.status)}`}>
                                                {getStatusIcon(selectedShipment.status)}
                                                {getStatusText(selectedShipment.status)}
                                            </span>
                                        </div>
                                        <div className="info-item">
                                            <span className="label">Vị trí hiện tại:</span>
                                            <span className="value">
                                                <MapPin size={16} />
                                                {selectedShipment.currentLocation}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="info-section">
                                    <h3>Lịch sử di chuyển</h3>
                                    <div className="timeline">
                                        <div className="timeline-item completed">
                                            <div className="timeline-icon">
                                                <CheckCircle size={20} />
                                            </div>
                                            <div className="timeline-content">
                                                <div className="timeline-title">Tạo lô hàng</div>
                                                <div className="timeline-date">{formatDate(selectedShipment.createdAt)}</div>
                                                <div className="timeline-location">Xuất phát từ {selectedShipment.from}</div>
                                            </div>
                                        </div>

                                        {selectedShipment.status !== 'pending' && (
                                            <div className="timeline-item completed">
                                                <div className="timeline-icon">
                                                    <Truck size={20} />
                                                </div>
                                                <div className="timeline-content">
                                                    <div className="timeline-title">Bắt đầu vận chuyển</div>
                                                    <div className="timeline-date">{formatDate(selectedShipment.createdAt)}</div>
                                                    <div className="timeline-location">Rời khỏi kho xuất phát</div>
                                                </div>
                                            </div>
                                        )}

                                        {selectedShipment.status === 'delivered' && (
                                            <div className="timeline-item completed">
                                                <div className="timeline-icon">
                                                    <CheckCircle size={20} />
                                                </div>
                                                <div className="timeline-content">
                                                    <div className="timeline-title">Giao hàng thành công</div>
                                                    <div className="timeline-date">{formatDate(selectedShipment.deliveredAt)}</div>
                                                    <div className="timeline-location">Đã giao đến {selectedShipment.to}</div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ShipmentTracking;

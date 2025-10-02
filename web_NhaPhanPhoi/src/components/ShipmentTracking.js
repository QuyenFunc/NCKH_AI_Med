import React, { useState, useEffect } from 'react';
import { Package, Truck, MapPin, Clock, CheckCircle, AlertCircle, Search, Filter } from 'lucide-react';
import distributorService from '../services/apiService';
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
            setError(null);
            
            // Get recipient's wallet address
            const recipientAddress = localStorage.getItem('walletAddress');
            if (!recipientAddress) {
                setError('Không tìm thấy địa chỉ ví nhà phân phối. Vui lòng đăng nhập.');
                setShipments([]);
                return;
            }

            // Fetch real shipments data
            const response = await distributorService.getShipmentsByRecipient(recipientAddress);
            if (response.success && response.data) {
                // Filter out invalid shipments (shipmentId = 0 or null)
                const validShipments = response.data.filter(shipment => 
                    shipment.shipmentId && shipment.shipmentId > 0
                );
                setShipments(validShipments);
            } else {
                setShipments([]);
                setError(response.message || 'Không thể tải danh sách lô hàng');
            }
        } catch (err) {
            console.error('Error fetching shipments:', err);
            setError('Không thể tải danh sách lô hàng: ' + err.message);
            setShipments([]);
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (status) => {
        switch (status?.toLowerCase()) {
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
        switch (status?.toLowerCase()) {
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
        switch (status?.toLowerCase()) {
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

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        try {
            return new Date(dateString).toLocaleDateString('vi-VN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return 'N/A';
        }
    };

    const filteredShipments = shipments.filter(shipment => {
        const matchesSearch = searchTerm === '' || 
            shipment.shipmentId?.toString().toLowerCase().includes(searchTerm.toLowerCase()) ||
            shipment.trackingInfo?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            shipment.drugBatch?.drugName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            shipment.drugBatch?.batchNumber?.toLowerCase().includes(searchTerm.toLowerCase());
        
        const matchesStatus = statusFilter === 'all' || shipment.status?.toLowerCase() === statusFilter;
        
        return matchesSearch && matchesStatus;
    });

    const handleShipmentClick = (shipment) => {
        setSelectedShipment(shipment);
    };

    const closeModal = () => {
        setSelectedShipment(null);
    };

    if (loading) {
        return (
            <div className="shipment-tracking">
                <div className="loading-container">
                    <div className="loading-spinner"></div>
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
                    Theo dõi vận chuyển
                </h1>
                <p>Theo dõi tình trạng vận chuyển các lô hàng</p>
            </div>

            {error && (
                <div className="alert alert-error">
                    <AlertCircle size={20} />
                    {error}
                </div>
            )}

            {/* Search and Filter Controls */}
            <div className="controls-section">
                <div className="search-box">
                    <Search className="search-icon" />
                    <input
                        type="text"
                        placeholder="Tìm kiếm theo mã lô hàng, mã vận đơn, tên thuốc..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="search-input"
                    />
                </div>
                
                <div className="filter-section">
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

                <button 
                    onClick={fetchShipments}
                    className="btn btn-primary"
                    disabled={loading}
                >
                    Làm mới
                </button>
            </div>

            {/* Shipments List */}
            <div className="shipments-container">
                {filteredShipments.length === 0 ? (
                    <div className="no-data">
                        <Package size={48} className="no-data-icon" />
                        <h3>Không có lô hàng nào</h3>
                        <p>
                            {searchTerm || statusFilter !== 'all' 
                                ? 'Không tìm thấy lô hàng nào phù hợp với bộ lọc'
                                : 'Chưa có lô hàng nào được gửi đến bạn'
                            }
                        </p>
                    </div>
                ) : (
                    <div className="shipments-grid">
                        {filteredShipments.map(shipment => (
                            <div 
                                key={shipment.id} 
                                className="shipment-card"
                                onClick={() => handleShipmentClick(shipment)}
                            >
                                <div className="shipment-header">
                                    <div className="shipment-id">
                                        <Package size={16} />
                                        <span>SHIP-{shipment.shipmentId || shipment.id}</span>
                                    </div>
                                    <div className={`status-badge ${getStatusClass(shipment.status)}`}>
                                        {getStatusIcon(shipment.status)}
                                        <span>{getStatusText(shipment.status)}</span>
                                    </div>
                                </div>
                                
                                <div className="shipment-content">
                                    <div className="drug-info">
                                        <h4>{shipment.drugBatch?.drugName || 'N/A'}</h4>
                                        <p>Lô: {shipment.drugBatch?.batchNumber || 'N/A'}</p>
                                        <p>Số lượng: {shipment.quantity?.toLocaleString() || 'N/A'}</p>
                                    </div>
                                    
                                    <div className="shipment-details">
                                        <div className="detail-item">
                                            <MapPin size={14} />
                                            <span>Từ: {shipment.fromAddress || 'N/A'}</span>
                                        </div>
                                        <div className="detail-item">
                                            <Clock size={14} />
                                            <span>Ngày tạo: {formatDate(shipment.shipmentTimestamp)}</span>
                                        </div>
                                        {shipment.trackingInfo && (
                                            <div className="detail-item">
                                                <span>Ghi chú: {shipment.trackingInfo}</span>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Shipment Detail Modal */}
            {selectedShipment && (
                <div className="modal-overlay" onClick={closeModal}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <div className="modal-header">
                            <h3>Chi tiết lô hàng SHIP-{selectedShipment.shipmentId}</h3>
                            <button onClick={closeModal} className="modal-close">×</button>
                        </div>
                        
                        <div className="modal-body">
                            <div className="detail-section">
                                <h4>Thông tin chung</h4>
                                <div className="detail-grid">
                                    <div className="detail-item">
                                        <strong>Mã shipment:</strong>
                                        <span>SHIP-{selectedShipment.shipmentId}</span>
                                    </div>
                                    <div className="detail-item">
                                        <strong>Trạng thái:</strong>
                                        <div className={`status-badge ${getStatusClass(selectedShipment.status)}`}>
                                            {getStatusIcon(selectedShipment.status)}
                                            <span>{getStatusText(selectedShipment.status)}</span>
                                        </div>
                                    </div>
                                    <div className="detail-item">
                                        <strong>Địa chỉ gửi:</strong>
                                        <span>{selectedShipment.fromAddress || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <strong>Địa chỉ nhận:</strong>
                                        <span>{selectedShipment.toAddress || 'N/A'}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="detail-section">
                                <h4>Thông tin thuốc</h4>
                                <div className="detail-grid">
                                    <div className="detail-item">
                                        <strong>Tên thuốc:</strong>
                                        <span>{selectedShipment.drugBatch?.drugName || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <strong>Số lô:</strong>
                                        <span>{selectedShipment.drugBatch?.batchNumber || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <strong>Nhà sản xuất:</strong>
                                        <span>{selectedShipment.drugBatch?.manufacturer || 'N/A'}</span>
                                    </div>
                                    <div className="detail-item">
                                        <strong>Số lượng:</strong>
                                        <span>{selectedShipment.quantity?.toLocaleString() || 'N/A'}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="detail-section">
                                <h4>Thời gian</h4>
                                <div className="detail-grid">
                                    <div className="detail-item">
                                        <strong>Ngày tạo:</strong>
                                        <span>{formatDate(selectedShipment.shipmentTimestamp)}</span>
                                    </div>
                                    <div className="detail-item">
                                        <strong>Cập nhật cuối:</strong>
                                        <span>{formatDate(selectedShipment.updatedAt)}</span>
                                    </div>
                                </div>
                            </div>

                            {selectedShipment.trackingInfo && (
                                <div className="detail-section">
                                    <h4>Ghi chú</h4>
                                    <p>{selectedShipment.trackingInfo}</p>
                                </div>
                            )}

                            {selectedShipment.transactionHash && (
                                <div className="detail-section">
                                    <h4>Blockchain</h4>
                                    <div className="detail-item">
                                        <strong>Transaction Hash:</strong>
                                        <span className="hash-text">{selectedShipment.transactionHash}</span>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ShipmentTracking;
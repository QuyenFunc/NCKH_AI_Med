import React, { useState, useEffect } from 'react';
import { 
  ShoppingCart, 
  Scan, 
  CheckCircle, 
  AlertCircle, 
  Package, 
  Info, 
  QrCode,
  Truck
} from 'lucide-react';
import pharmacyService from '../services/apiService';
import './ReceiveGoods.css';

const ReceiveGoods = () => {
  const [scanInput, setScanInput] = useState('');
  const [shipmentDetails, setShipmentDetails] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [pendingShipments, setPendingShipments] = useState([]);

  useEffect(() => {
    fetchPendingShipments();
  }, []);

  const fetchPendingShipments = async () => {
    try {
      // Mock data - replace with actual API call
      const mockPendingShipments = [
        {
          id: 'SH001',
          from: 'Nhà phân phối ABC',
          fromType: 'distributor',
          trackingCode: 'TRK123456789',
          expectedDate: '2024-09-20',
          products: [
            { name: 'Paracetamol 500mg', quantity: 1000, batchCode: 'BT2024001', expiry: '2027-09-15' },
            { name: 'Amoxicillin 250mg', quantity: 500, batchCode: 'BT2024002', expiry: '2026-09-16' }
          ],
          totalValue: 150000000,
          driverName: 'Nguyễn Văn A',
          vehicleNumber: '29A-123456'
        },
        {
          id: 'SH002',
          from: 'Công ty Dược DEF', 
          fromType: 'manufacturer',
          trackingCode: 'TRK987654321',
          expectedDate: '2024-09-21',
          products: [
            { name: 'Vitamin C 1000mg', quantity: 800, batchCode: 'BT2024003', expiry: '2026-03-10' }
          ],
          totalValue: 80000000
        }
      ];
      setPendingShipments(mockPendingShipments);
    } catch (err) {
      console.error('Error fetching pending shipments:', err);
    }
  };

  const handleScan = async () => {
    if (!scanInput.trim()) {
      setError('Vui lòng nhập mã lô hàng hoặc mã vận đơn');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Mock API call - replace with actual implementation
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Find matching shipment from pending list
      const foundShipment = pendingShipments.find(
        shipment => shipment.trackingCode === scanInput || shipment.id === scanInput
      );

      if (foundShipment) {
        setShipmentDetails(foundShipment);
      } else {
        // Mock successful scan with sample data
        const mockShipmentDetails = {
          id: scanInput,
          from: 'Nhà phân phối ABC',
          fromType: 'distributor',
          trackingCode: scanInput,
          expectedDate: '2024-09-20',
          products: [
            { 
              name: 'Paracetamol 500mg', 
              quantity: 500, 
              batchCode: 'BT2024' + scanInput.slice(-3),
              expiry: '2027-12-31',
              manufacturer: 'Công ty Dược ABC'
            }
          ],
          totalValue: 75000000,
          driverName: 'Trần Văn B',
          vehicleNumber: '30A-654321',
          notes: 'Hàng cần kiểm tra nhiệt độ, bảo quản nơi khô ráo'
        };
        setShipmentDetails(mockShipmentDetails);
      }
    } catch (err) {
      setError('Không thể tìm thấy thông tin lô hàng: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirmReceive = async () => {
    if (!shipmentDetails) return;

    try {
      setLoading(true);
      setError(null);

      // Call blockchain API to confirm receipt and update ownership
      const response = await pharmacyService.confirmReceiveGoods({
        shipmentId: shipmentDetails.id,
        trackingCode: shipmentDetails.trackingCode,
        products: shipmentDetails.products,
        confirmedBy: 'Pharmacy User', // Get from auth context
        confirmationDate: new Date().toISOString(),
        pharmacyInfo: {
          name: 'Hiệu thuốc ABC',
          address: '456 Đường XYZ, Quận 2, TP.HCM',
          license: 'GPP-2024-002'
        }
      });

      if (response.success) {
        setSuccess(`Đã xác nhận nhận hàng thành công! Quyền giám sát đã được cập nhật trên blockchain. Transaction: ${response.data.transactionHash}`);
        
        // Reset form
        setScanInput('');
        setShipmentDetails(null);
        
        // Refresh pending shipments
        await fetchPendingShipments();
      } else {
        setError(response.message || 'Không thể xác nhận nhận hàng');
      }
    } catch (err) {
      setError('Lỗi xác nhận nhận hàng: ' + err.message);
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

  return (
    <div className="receive-goods">
      <div className="page-header">
        <h1>
          <ShoppingCart className="page-icon" />
          Nhận hàng
        </h1>
        <p>Quét và xác nhận đã nhận lô hàng, cập nhật quyền giám sát trên blockchain</p>
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

      {/* Scanner Section */}
      <div className="scanner-section">
        <div className="scanner-card">
          <div className="scanner-header">
            <QrCode size={32} />
            <h3>Quét mã nhận hàng</h3>
            <p>Quét mã lô hàng hoặc mã vận đơn để xác thực và nhận hàng</p>
          </div>

          <div className="scanner-input">
            <div className="input-group">
              <Scan className="input-icon" />
              <input
                type="text"
                value={scanInput}
                onChange={(e) => setScanInput(e.target.value)}
                placeholder="Nhập hoặc quét mã lô hàng (VD: SH001, TRK123456789)"
                className="scan-input"
                onKeyPress={(e) => e.key === 'Enter' && handleScan()}
              />
              <button 
                onClick={handleScan}
                disabled={loading}
                className="btn btn-primary scan-btn"
              >
                {loading ? 'Đang tìm...' : 'Quét'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Shipment Details */}
      {shipmentDetails && (
        <div className="shipment-details">
          <div className="details-card">
            <div className="details-header">
              <h3>
                <Info size={24} />
                Chi tiết lô hàng
              </h3>
              <div className="shipment-id">ID: {shipmentDetails.id}</div>
            </div>

            <div className="details-content">
              <div className="info-section">
                <h4>Thông tin vận chuyển</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">Từ:</span>
                    <span className="value">
                      {shipmentDetails.from}
                      <span className={`source-type ${shipmentDetails.fromType}`}>
                        ({shipmentDetails.fromType === 'manufacturer' ? 'NSX' : 'NPP'})
                      </span>
                    </span>
                  </div>
                  <div className="info-item">
                    <span className="label">Mã vận đơn:</span>
                    <span className="value">{shipmentDetails.trackingCode}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Ngày dự kiến:</span>
                    <span className="value">{formatDate(shipmentDetails.expectedDate)}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Tổng giá trị:</span>
                    <span className="value highlight">{formatCurrency(shipmentDetails.totalValue)}</span>
                  </div>
                  {shipmentDetails.driverName && (
                    <div className="info-item">
                      <span className="label">Tài xế:</span>
                      <span className="value">{shipmentDetails.driverName}</span>
                    </div>
                  )}
                  {shipmentDetails.vehicleNumber && (
                    <div className="info-item">
                      <span className="label">Biển số xe:</span>
                      <span className="value">{shipmentDetails.vehicleNumber}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="products-section">
                <h4>Danh sách sản phẩm</h4>
                <div className="products-table">
                  <table>
                    <thead>
                      <tr>
                        <th>Tên sản phẩm</th>
                        <th>Mã lô</th>
                        <th>Số lượng</th>
                        <th>Hạn sử dụng</th>
                        <th>Nguồn gốc</th>
                        <th>Trạng thái</th>
                      </tr>
                    </thead>
                    <tbody>
                      {shipmentDetails.products.map((product, index) => (
                        <tr key={index}>
                          <td className="product-name">{product.name}</td>
                          <td className="batch-code">{product.batchCode}</td>
                          <td className="quantity">{product.quantity.toLocaleString()} viên</td>
                          <td className="expiry">{formatDate(product.expiry)}</td>
                          <td className="source">{product.manufacturer || shipmentDetails.from}</td>
                          <td className="status">
                            <span className="status-badge status-verified">
                              <CheckCircle size={14} />
                              Đã xác thực
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {shipmentDetails.notes && (
                <div className="notes-section">
                  <h4>Ghi chú đặc biệt</h4>
                  <div className="notes-content">
                    <AlertCircle size={16} />
                    {shipmentDetails.notes}
                  </div>
                </div>
              )}

              <div className="blockchain-info">
                <h4>Thông tin Blockchain</h4>
                <div className="blockchain-note">
                  <Info size={16} />
                  Khi xác nhận nhận hàng, quyền giám sát sản phẩm sẽ được chuyển từ <strong>{shipmentDetails.fromType === 'manufacturer' ? 'Nhà sản xuất' : 'Nhà phân phối'}</strong> sang <strong>Hiệu thuốc</strong> và ghi nhận trên blockchain.
                </div>
              </div>
            </div>

            <div className="details-actions">
              <button 
                onClick={() => {
                  setScanInput('');
                  setShipmentDetails(null);
                  setError(null);
                  setSuccess(null);
                }}
                className="btn btn-secondary"
              >
                Hủy
              </button>
              <button 
                onClick={handleConfirmReceive}
                disabled={loading}
                className="btn btn-success"
              >
                <CheckCircle size={16} />
                {loading ? 'Đang xác nhận...' : 'Xác nhận đã nhận hàng & Cập nhật Blockchain'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pending Shipments */}
      <div className="pending-shipments">
        <div className="pending-header">
          <h3>
            <Truck size={24} />
            Lô hàng đang chờ nhận ({pendingShipments.length})
          </h3>
        </div>

        <div className="pending-grid">
          {pendingShipments.length === 0 ? (
            <div className="no-pending">
              <Package size={48} className="no-data-icon" />
              <h4>Không có lô hàng nào đang chờ</h4>
              <p>Tất cả lô hàng đã được xử lý</p>
            </div>
          ) : (
            pendingShipments.map(shipment => (
              <div key={shipment.id} className="pending-card">
                <div className="pending-header-info">
                  <div className="shipment-id">{shipment.id}</div>
                  <div className="tracking-code">{shipment.trackingCode}</div>
                </div>
                <div className="pending-content">
                  <div className="from-info">
                    <strong>{shipment.from}</strong>
                    <span className={`source-badge ${shipment.fromType}`}>
                      {shipment.fromType === 'manufacturer' ? 'NSX' : 'NPP'}
                    </span>
                  </div>
                  <div className="expected-date">
                    Dự kiến: {formatDate(shipment.expectedDate)}
                  </div>
                  <div className="products-count">
                    {shipment.products.length} sản phẩm
                  </div>
                  <div className="total-value">
                    {formatCurrency(shipment.totalValue)}
                  </div>
                </div>
                <div className="pending-actions">
                  <button 
                    onClick={() => {
                      setScanInput(shipment.trackingCode);
                      handleScan();
                    }}
                    className="btn btn-outline"
                  >
                    Xem chi tiết
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default ReceiveGoods;

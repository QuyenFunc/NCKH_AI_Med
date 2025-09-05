import React, { useState } from 'react';
import { QrCode, Package, CheckCircle, AlertCircle, Scan, Calendar, User } from 'lucide-react';
import './ReceiveGoods.css';

function ReceiveGoods() {
  const [shipmentCode, setShipmentCode] = useState('');
  const [showScanner, setShowScanner] = useState(false);
  const [shipmentData, setShipmentData] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);

  // Mock data cho lô hàng
  const mockShipmentData = {
    'LOT001234': {
      id: 'LOT001234',
      distributor: 'Nhà phân phối ABC',
      distributorAddress: '456 Đường ABC, Q1, TP.HCM',
      shippedDate: '2024-01-15',
      expectedDeliveryDate: '2024-01-17',
      transportMethod: 'Xe tải',
      driver: 'Nguyễn Văn A',
      driverPhone: '0901234567',
      items: [
        {
          id: 1,
          name: 'Paracetamol 500mg',
          manufacturer: 'Công ty Dược ABC',
          batchNumber: 'LOT2024001',
          quantity: 1000,
          unit: 'viên',
          expireDate: '2025-12-31',
          registrationNumber: 'VD-12345-67'
        },
        {
          id: 2,
          name: 'Amoxicillin 250mg',
          manufacturer: 'Công ty Dược XYZ',
          batchNumber: 'LOT2024002',
          quantity: 500,
          unit: 'viên',
          expireDate: '2025-06-30',
          registrationNumber: 'VD-12345-68'
        }
      ],
      notes: 'Giao hàng trong giờ hành chính',
      status: 'shipping'
    }
  };

  const handleScanCode = () => {
    if (shipmentCode && mockShipmentData[shipmentCode]) {
      setShipmentData(mockShipmentData[shipmentCode]);
      setShowScanner(false);
    } else {
      alert('Không tìm thấy thông tin lô hàng với mã: ' + shipmentCode);
      setShipmentCode('');
    }
  };

  const handleVerifyShipment = () => {
    setIsVerifying(true);
    
    // Mock verification process
    setTimeout(() => {
      setIsVerifying(false);
      setVerificationResult({
        success: true,
        blockchainTxId: 'TX' + Date.now(),
        timestamp: new Date().toISOString(),
        verifiedBy: 'Dược sĩ Nguyễn Thị B'
      });
    }, 2000);
  };

  const resetForm = () => {
    setShipmentCode('');
    setShipmentData(null);
    setVerificationResult(null);
    setShowScanner(false);
  };

  return (
    <div className="receive-goods">
      <div className="page-header">
        <h1>Nhận Hàng</h1>
        <p>Quét mã lô hàng để xác thực và nhận vào kho</p>
      </div>

      <div className="receive-container">
        {!shipmentData && !verificationResult && (
          <div className="scanner-section">
            <div className="scanner-card">
              <div className="scanner-header">
                <QrCode className="scanner-icon" />
                <h2>Quét hoặc Nhập mã Lô hàng</h2>
                <p>Sử dụng máy quét barcode hoặc nhập mã thủ công</p>
              </div>

              {!showScanner ? (
                <button
                  className="btn btn-primary scanner-btn"
                  onClick={() => setShowScanner(true)}
                >
                  <Scan />
                  Bắt đầu quét mã
                </button>
              ) : (
                <div className="input-section">
                  <div className="input-group">
                    <input
                      type="text"
                      value={shipmentCode}
                      onChange={(e) => setShipmentCode(e.target.value)}
                      placeholder="Nhập mã lô hàng (VD: LOT001234)"
                      className="input scanner-input"
                      autoFocus
                    />
                    <button
                      className="btn btn-primary"
                      onClick={handleScanCode}
                      disabled={!shipmentCode}
                    >
                      Kiểm tra
                    </button>
                  </div>
                  <p className="helper-text">
                    Mã demo: LOT001234
                  </p>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setShowScanner(false)}
                  >
                    Hủy
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {shipmentData && !verificationResult && (
          <div className="shipment-details">
            <div className="details-header">
              <h2>Chi tiết lô hàng {shipmentData.id}</h2>
              <span className="status-badge status-shipping">
                Đang giao hàng
              </span>
            </div>

            <div className="details-grid">
              {/* Thông tin người gửi */}
              <div className="info-card">
                <div className="card-header">
                  <User className="card-icon" />
                  <h3>Thông tin người gửi</h3>
                </div>
                <div className="info-content">
                  <div className="info-item">
                    <strong>Nhà phân phối:</strong>
                    <span>{shipmentData.distributor}</span>
                  </div>
                  <div className="info-item">
                    <strong>Địa chỉ:</strong>
                    <span>{shipmentData.distributorAddress}</span>
                  </div>
                  <div className="info-item">
                    <strong>Tài xế:</strong>
                    <span>{shipmentData.driver}</span>
                  </div>
                  <div className="info-item">
                    <strong>SĐT tài xế:</strong>
                    <span>{shipmentData.driverPhone}</span>
                  </div>
                </div>
              </div>

              {/* Thông tin vận chuyển */}
              <div className="info-card">
                <div className="card-header">
                  <Calendar className="card-icon" />
                  <h3>Thông tin vận chuyển</h3>
                </div>
                <div className="info-content">
                  <div className="info-item">
                    <strong>Ngày gửi:</strong>
                    <span>{new Date(shipmentData.shippedDate).toLocaleDateString('vi-VN')}</span>
                  </div>
                  <div className="info-item">
                    <strong>Ngày giao dự kiến:</strong>
                    <span>{new Date(shipmentData.expectedDeliveryDate).toLocaleDateString('vi-VN')}</span>
                  </div>
                  <div className="info-item">
                    <strong>Phương tiện:</strong>
                    <span>{shipmentData.transportMethod}</span>
                  </div>
                  {shipmentData.notes && (
                    <div className="info-item">
                      <strong>Ghi chú:</strong>
                      <span>{shipmentData.notes}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Danh sách sản phẩm */}
            <div className="products-section">
              <div className="section-header">
                <Package className="section-icon" />
                <h3>Danh sách sản phẩm ({shipmentData.items.length} loại)</h3>
              </div>
              <div className="products-list">
                {shipmentData.items.map((item) => (
                  <div key={item.id} className="product-card">
                    <div className="product-header">
                      <h4>{item.name}</h4>
                      <span className="quantity-badge">
                        {item.quantity.toLocaleString()} {item.unit}
                      </span>
                    </div>
                    <div className="product-details">
                      <div className="detail-row">
                        <span className="label">Nhà sản xuất:</span>
                        <span className="value">{item.manufacturer}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Số lô:</span>
                        <span className="value">{item.batchNumber}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Hạn sử dụng:</span>
                        <span className="value">{new Date(item.expireDate).toLocaleDateString('vi-VN')}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Số đăng ký:</span>
                        <span className="value">{item.registrationNumber}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Action buttons */}
            <div className="action-section">
              <div className="action-info">
                <AlertCircle className="info-icon" />
                <div>
                  <h4>Xác nhận nhận hàng</h4>
                  <p>Sau khi xác nhận, thông tin sẽ được ghi lên blockchain và không thể thay đổi</p>
                </div>
              </div>
              <div className="action-buttons">
                <button
                  className="btn btn-secondary"
                  onClick={resetForm}
                >
                  Hủy
                </button>
                <button
                  className="btn btn-primary verify-btn"
                  onClick={handleVerifyShipment}
                  disabled={isVerifying}
                >
                  {isVerifying ? (
                    <>
                      <div className="loading-spinner"></div>
                      Đang xác thực...
                    </>
                  ) : (
                    <>
                      <CheckCircle />
                      Xác nhận đã nhận hàng
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {verificationResult && (
          <div className="verification-result">
            <div className="result-card success">
              <CheckCircle className="result-icon" />
              <div className="result-content">
                <h2>Nhận hàng thành công!</h2>
                <p>Lô hàng {shipmentData.id} đã được xác thực và ghi lên blockchain</p>
                
                <div className="blockchain-info">
                  <h3>Thông tin blockchain:</h3>
                  <div className="blockchain-details">
                    <div className="blockchain-item">
                      <strong>Transaction ID:</strong>
                      <span className="tx-id">{verificationResult.blockchainTxId}</span>
                    </div>
                    <div className="blockchain-item">
                      <strong>Thời gian xác thực:</strong>
                      <span>{new Date(verificationResult.timestamp).toLocaleString('vi-VN')}</span>
                    </div>
                    <div className="blockchain-item">
                      <strong>Xác thực bởi:</strong>
                      <span>{verificationResult.verifiedBy}</span>
                    </div>
                  </div>
                </div>

                <div className="result-actions">
                  <button
                    className="btn btn-primary"
                    onClick={resetForm}
                  >
                    Nhận lô hàng khác
                  </button>
                  <button className="btn btn-secondary">
                    Xem trong kho
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ReceiveGoods;


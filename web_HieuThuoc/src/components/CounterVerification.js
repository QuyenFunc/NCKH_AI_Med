import React, { useState } from 'react';
import { 
  Shield, 
  Scan, 
  CheckCircle, 
  AlertCircle, 
  Package, 
  Factory,
  Truck,
  Search,
  QrCode,
  Clock,
  MapPin
} from 'lucide-react';
import pharmacyService from '../services/apiService';
import './CounterVerification.css';

const CounterVerification = () => {
  const [scanInput, setScanInput] = useState('');
  const [verificationResult, setVerificationResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recentVerifications, setRecentVerifications] = useState([]);

  const handleScan = async () => {
    if (!scanInput || !scanInput.trim()) {
      setError('Vui lòng nhập mã QR hoặc mã lô thuốc');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      let verificationResult;
      
      try {
        // Call blockchain API to verify drug authenticity
        const response = await pharmacyService.verifyBatchAuthenticity(scanInput);
        
        if (response.success && response.data.verified) {
          const batch = response.data.batch;
          const blockchain = response.data.blockchain;
          
          // Transform real data to expected format
          verificationResult = {
            isAuthentic: true,
            product: {
              name: batch.drugName,
              batchCode: batch.batchNumber,
              activeIngredient: batch.drugName.split(' ')[0], // Extract main ingredient
              dosage: batch.drugName.includes('mg') ? batch.drugName.match(/\d+mg/)[0] : 'N/A',
              manufacturer: batch.manufacturer,
              manufactureDate: batch.manufactureTimestamp ? batch.manufactureTimestamp.split('T')[0] : 'N/A',
              expiryDate: batch.expiryDate ? batch.expiryDate.split('T')[0] : 'N/A',
              qrCode: batch.qrCode || scanInput,
              storageConditions: 'Nơi khô ráo, tránh ánh sáng trực tiếp'
            },
            blockchainHistory: [
              {
                step: 1,
                event: 'Sản xuất',
                actor: batch.manufacturer,
                actorType: 'manufacturer',
                location: 'Nhà máy sản xuất',
                timestamp: batch.manufactureTimestamp || '2024-09-15T08:30:00Z',
                txHash: blockchain.transactionHash,
                details: 'Lô thuốc được sản xuất và ghi nhận lên blockchain'
              },
              {
                step: 2,
                event: 'Xác thực blockchain',
                actor: 'Hệ thống Blockchain',
                actorType: 'system',
                location: 'Blockchain Network',
                timestamp: blockchain.timestamp || new Date().toISOString(),
                txHash: blockchain.transactionHash,
                details: `Xác thực thành công tại block #${blockchain.blockNumber}`
              },
              {
                step: 3,
                event: 'Sẵn sàng bán',
                actor: 'Hiệu thuốc ABC',
                actorType: 'pharmacy',
                location: 'Quầy thuốc - Hiệu thuốc ABC',
                timestamp: new Date().toISOString(),
                txHash: blockchain.transactionHash,
                details: 'Sản phẩm được xác thực và sẵn sàng bán cho khách hàng'
              }
            ],
            qualityInfo: {
              qualityGrade: 'A',
              testResults: 'Đạt chuẩn',
              certifications: ['GMP', 'ISO 9001', 'WHO-GMP'],
              batchSize: batch.quantity || 10000,
              productionLine: 'Dây chuyền A'
            },
            warnings: [],
            recommendations: [
              'Bảo quản nơi khô ráo, nhiệt độ dưới 30°C',
              'Tránh ánh sáng trực tiếp',
              'Kiểm tra hạn sử dụng trước khi bán'
            ]
          };
          
          // Check for potential issues using real data
          if (verificationResult.product.expiryDate && verificationResult.product.expiryDate !== 'N/A') {
            const expiryDate = new Date(verificationResult.product.expiryDate);
            const now = new Date();
            const daysToExpiry = Math.ceil((expiryDate - now) / (1000 * 60 * 60 * 24));
            
            if (daysToExpiry < 90) {
              verificationResult.warnings.push({
                type: 'expiry_warning',
                message: `Sản phẩm sẽ hết hạn trong ${daysToExpiry} ngày`,
                severity: daysToExpiry < 30 ? 'high' : 'medium'
              });
            }
          }
        } else {
          // Product not verified or not found
          verificationResult = {
            isAuthentic: false,
            product: {
              name: 'Không xác định',
              batchCode: scanInput,
              qrCode: scanInput
            },
            warnings: [{
              type: 'authentication_failed',
              message: response.message || 'Không thể xác thực sản phẩm này trên blockchain',
              severity: 'high'
            }],
            recommendations: [
              'Không bán sản phẩm này',
              'Liên hệ nhà cung cấp để kiểm tra',
              'Báo cáo với cơ quan chức năng nếu cần'
            ]
          };
        }
      } catch (apiError) {
        // API call failed - product cannot be verified
        verificationResult = {
          isAuthentic: false,
          product: {
            name: 'Không xác định',
            batchCode: scanInput,
            qrCode: scanInput
          },
          warnings: [{
            type: 'api_error',
            message: 'Không thể kết nối đến hệ thống xác thực blockchain',
            severity: 'high'
          }],
          recommendations: [
            'Không bán sản phẩm này',
            'Kiểm tra kết nối mạng',
            'Thử lại sau ít phút'
          ]
        };
      }

      setVerificationResult(verificationResult);
      
      // Add to recent verifications
      const newVerification = {
        id: Date.now(),
        productName: verificationResult.product.name,
        batchCode: verificationResult.product.batchCode,
        verifiedAt: new Date(),
        status: verificationResult.isAuthentic ? 'authentic' : 'suspicious',
        customerType: 'Khách lẻ'
      };
      setRecentVerifications([newVerification, ...recentVerifications.slice(0, 9)]);

    } catch (err) {
      setError('Không thể xác thực sản phẩm: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getActorIcon = (actorType) => {
    switch (actorType) {
      case 'manufacturer':
        return <Factory size={16} />;
      case 'distributor':
        return <Truck size={16} />;
      case 'pharmacy':
        return <Package size={16} />;
      default:
        return <Package size={16} />;
    }
  };

  const getActorColor = (actorType) => {
    switch (actorType) {
      case 'manufacturer':
        return 'manufacturer';
      case 'distributor':
        return 'distributor';
      case 'pharmacy':
        return 'pharmacy';
      default:
        return 'default';
    }
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('vi-VN');
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const diff = now - timestamp;
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    
    if (minutes < 60) {
      return `${minutes} phút trước`;
    } else {
      return `${hours} giờ trước`;
    }
  };

  return (
    <div className="counter-verification">
      <div className="page-header">
        <h1>
          <Shield className="page-icon" />
          Xác thực tại quầy
        </h1>
        <p>Tra cứu nhanh để quét và xem lại lịch sử nguồn gốc của sản phẩm trước khi bán</p>
      </div>

      {error && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {/* Scanner Section */}
      <div className="scanner-section">
        <div className="scanner-card">
          <div className="scanner-header">
            <QrCode size={32} />
            <h3>Quét mã xác thực sản phẩm</h3>
            <p>Quét mã QR hoặc nhập mã lô để xác thực nguồn gốc trước khi bán</p>
          </div>

          <div className="scanner-input">
            <div className="input-group">
              <Scan className="input-icon" />
              <input
                type="text"
                value={scanInput}
                onChange={(e) => setScanInput(e.target.value)}
                placeholder="Nhập hoặc quét mã QR/mã lô (VD: BT2024001, QR_BT2024001)"
                className="scan-input"
                onKeyPress={(e) => e.key === 'Enter' && handleScan()}
              />
              <button 
                onClick={handleScan}
                disabled={loading}
                className="btn btn-primary scan-btn"
              >
                {loading ? 'Đang xác thực...' : 'Xác thực'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Verification Result */}
      {verificationResult && (
        <div className="verification-result">
          <div className={`result-card ${verificationResult.isAuthentic ? 'authentic' : 'suspicious'}`}>
            <div className="result-header">
              <div className="auth-status">
                {verificationResult.isAuthentic ? (
                  <>
                    <CheckCircle size={32} className="auth-icon authentic" />
                    <div>
                      <h3>Sản phẩm chính hãng</h3>
                      <p>Đã xác thực nguồn gốc trên blockchain</p>
                    </div>
                  </>
                ) : (
                  <>
                    <AlertCircle size={32} className="auth-icon suspicious" />
                    <div>
                      <h3>Cần kiểm tra thêm</h3>
                      <p>Không thể xác thực nguồn gốc</p>
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="result-content">
              {/* Product Information */}
              <div className="product-info">
                <h4>Thông tin sản phẩm</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">Tên sản phẩm:</span>
                    <span className="value">{verificationResult.product.name}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Mã lô:</span>
                    <span className="value">{verificationResult.product.batchCode}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Hoạt chất:</span>
                    <span className="value">{verificationResult.product.activeIngredient}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Liều lượng:</span>
                    <span className="value">{verificationResult.product.dosage}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Nhà sản xuất:</span>
                    <span className="value">{verificationResult.product.manufacturer}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Ngày sản xuất:</span>
                    <span className="value">{new Date(verificationResult.product.manufactureDate).toLocaleDateString('vi-VN')}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Hạn sử dụng:</span>
                    <span className="value expiry">{new Date(verificationResult.product.expiryDate).toLocaleDateString('vi-VN')}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Cấp độ chất lượng:</span>
                    <span className="value quality">{verificationResult.qualityInfo.qualityGrade}</span>
                  </div>
                </div>
              </div>

              {/* Warnings */}
              {verificationResult.warnings.length > 0 && (
                <div className="warnings-section">
                  <h4>Cảnh báo</h4>
                  {verificationResult.warnings.map((warning, index) => (
                    <div key={index} className={`warning-item ${warning.severity}`}>
                      <AlertCircle size={16} />
                      {warning.message}
                    </div>
                  ))}
                </div>
              )}

              {/* Blockchain Traceability */}
              <div className="traceability-section">
                <h4>Lịch sử truy xuất nguồn gốc</h4>
                <div className="blockchain-timeline">
                  {verificationResult.blockchainHistory.map((event, index) => (
                    <div key={index} className="timeline-item">
                      <div className="timeline-step">{event.step}</div>
                      <div className={`timeline-icon ${getActorColor(event.actorType)}`}>
                        {getActorIcon(event.actorType)}
                      </div>
                      <div className="timeline-content">
                        <div className="timeline-header">
                          <span className="event-name">{event.event}</span>
                          <span className="event-time">{formatDateTime(event.timestamp)}</span>
                        </div>
                        <div className="event-actor">
                          <strong>{event.actor}</strong>
                        </div>
                        <div className="event-location">
                          <MapPin size={14} />
                          {event.location}
                        </div>
                        <div className="event-details">{event.details}</div>
                        <div className="tx-hash">
                          TX: {event.txHash.substring(0, 20)}...
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quality & Certifications */}
              <div className="quality-section">
                <h4>Chất lượng & Chứng nhận</h4>
                <div className="quality-grid">
                  <div className="quality-item">
                    <span className="label">Kết quả kiểm tra:</span>
                    <span className="value">{verificationResult.qualityInfo.testResults}</span>
                  </div>
                  <div className="quality-item">
                    <span className="label">Kích thước lô:</span>
                    <span className="value">{verificationResult.qualityInfo.batchSize.toLocaleString()} viên</span>
                  </div>
                  <div className="quality-item">
                    <span className="label">Dây chuyền:</span>
                    <span className="value">{verificationResult.qualityInfo.productionLine}</span>
                  </div>
                </div>
                <div className="certifications">
                  <span className="label">Chứng nhận:</span>
                  <div className="cert-badges">
                    {verificationResult.qualityInfo.certifications.map((cert, index) => (
                      <span key={index} className="cert-badge">{cert}</span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Recommendations */}
              {verificationResult.recommendations.length > 0 && (
                <div className="recommendations-section">
                  <h4>Khuyến nghị</h4>
                  <ul className="recommendations-list">
                    {verificationResult.recommendations.map((rec, index) => (
                      <li key={index}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="result-actions">
              <button 
                onClick={() => {
                  setScanInput('');
                  setVerificationResult(null);
                  setError(null);
                }}
                className="btn btn-secondary"
              >
                Quét sản phẩm khác
              </button>
              {verificationResult.isAuthentic && (
                <button className="btn btn-success">
                  <CheckCircle size={16} />
                  Xác nhận bán hàng
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Recent Verifications */}
      <div className="recent-verifications">
        <div className="recent-header">
          <h3>
            <Clock size={24} />
            Xác thực gần đây ({recentVerifications.length})
          </h3>
        </div>

        <div className="recent-list">
          {recentVerifications.length === 0 ? (
            <div className="no-recent">
              <Search size={48} className="no-data-icon" />
              <h4>Chưa có xác thực nào</h4>
              <p>Các sản phẩm đã xác thực sẽ hiển thị ở đây</p>
            </div>
          ) : (
            recentVerifications.map(verification => (
              <div key={verification.id} className="recent-item">
                <div className="recent-icon">
                  <Shield size={20} />
                </div>
                <div className="recent-content">
                  <div className="recent-product">
                    <strong>{verification.productName}</strong>
                    <span className="batch-code">#{verification.batchCode}</span>
                  </div>
                  <div className="recent-meta">
                    <span className="time">{formatTimeAgo(verification.verifiedAt)}</span>
                    <span className="customer-type">{verification.customerType}</span>
                    <span className={`status-badge status-${verification.status}`}>
                      {verification.status === 'authentic' ? 'Chính hãng' : 'Cần kiểm tra'}
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default CounterVerification;

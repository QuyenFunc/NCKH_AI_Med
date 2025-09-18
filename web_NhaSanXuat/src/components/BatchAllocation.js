import React, { useState, useEffect } from 'react';
import { 
  Package, 
  Plus, 
  QrCode,
  Calendar,
  Factory,
  CheckCircle,
  AlertCircle,
  Hash,
  Clipboard,
  Save
} from 'lucide-react';
import manufacturerService from '../services/apiService';
import './BatchAllocation.css';

const BatchAllocation = () => {
  const [products, setProducts] = useState([]);
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  const [batchForm, setBatchForm] = useState({
    productId: '',
    quantity: '',
    manufactureDate: '',
    expiryDate: '',
    productionLine: '',
    qualityControlNotes: '',
    storageLocation: ''
  });

  const [generatedBatch, setGeneratedBatch] = useState(null);

  useEffect(() => {
    fetchProducts();
    fetchRecentBatches();
  }, []);

  const fetchProducts = async () => {
    try {
      // Mock data for active products
      const mockProducts = [
        {
          id: 'PROD001',
          name: 'Paracetamol 500mg',
          category: 'Giảm đau hạ sốt',
          activeIngredient: 'Paracetamol',
          dosage: '500mg',
          unit: 'viên',
          shelfLife: '36 tháng',
          storageConditions: 'Nơi khô ráo, tránh ánh sáng'
        },
        {
          id: 'PROD002',
          name: 'Amoxicillin 250mg',
          category: 'Kháng sinh',
          activeIngredient: 'Amoxicillin',
          dosage: '250mg',
          unit: 'viên',
          shelfLife: '24 tháng',
          storageConditions: 'Nhiệt độ phòng, tránh ẩm'
        },
        {
          id: 'PROD003',
          name: 'Vitamin C 1000mg',
          category: 'Vitamin & Khoáng chất',
          activeIngredient: 'Ascorbic Acid',
          dosage: '1000mg',
          unit: 'viên',
          shelfLife: '24 tháng',
          storageConditions: 'Nơi khô ráo, nhiệt độ dưới 30°C'
        }
      ];
      setProducts(mockProducts.filter(p => p.status !== 'inactive'));
    } catch (err) {
      setError('Không thể tải danh sách sản phẩm: ' + err.message);
    }
  };

  const fetchRecentBatches = async () => {
    try {
      // Mock recent batches
      const mockBatches = [
        {
          id: 'BT2024001',
          productId: 'PROD001',
          productName: 'Paracetamol 500mg',
          quantity: 10000,
          manufactureDate: '2024-09-15',
          expiryDate: '2027-09-15',
          qrCode: 'QR_BT2024001',
          status: 'completed',
          blockchainTx: '0x1234567890abcdef...',
          createdAt: '2024-09-15T08:30:00Z'
        },
        {
          id: 'BT2024002',
          productId: 'PROD002',
          productName: 'Amoxicillin 250mg',
          quantity: 5000,
          manufactureDate: '2024-09-16',
          expiryDate: '2026-09-16',
          qrCode: 'QR_BT2024002',
          status: 'completed',
          blockchainTx: '0xabcdef1234567890...',
          createdAt: '2024-09-16T10:15:00Z'
        }
      ];
      setBatches(mockBatches);
    } catch (err) {
      console.error('Error fetching recent batches:', err);
    }
  };

  const generateBatchId = () => {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const time = String(now.getHours()).padStart(2, '0') + String(now.getMinutes()).padStart(2, '0');
    return `BT${year}${month}${day}${time}`;
  };

  const generateQRCode = (batchId) => {
    return `QR_${batchId}_${Date.now()}`;
  };

  const calculateExpiryDate = (manufactureDate, shelfLifeMonths) => {
    const date = new Date(manufactureDate);
    date.setMonth(date.getMonth() + parseInt(shelfLifeMonths));
    return date.toISOString().split('T')[0];
  };

  const handleProductChange = (productId) => {
    setBatchForm({...batchForm, productId});
    
    // Auto-calculate expiry date if manufacture date is set
    if (batchForm.manufactureDate && productId) {
      const product = products.find(p => p.id === productId);
      if (product && product.shelfLife) {
        const shelfLifeMonths = parseInt(product.shelfLife.split(' ')[0]);
        const expiryDate = calculateExpiryDate(batchForm.manufactureDate, shelfLifeMonths);
        setBatchForm(prev => ({...prev, productId, expiryDate}));
      }
    } else {
      setBatchForm(prev => ({...prev, productId}));
    }
  };

  const handleManufactureDateChange = (date) => {
    setBatchForm({...batchForm, manufactureDate: date});
    
    // Auto-calculate expiry date
    if (batchForm.productId && date) {
      const product = products.find(p => p.id === batchForm.productId);
      if (product && product.shelfLife) {
        const shelfLifeMonths = parseInt(product.shelfLife.split(' ')[0]);
        const expiryDate = calculateExpiryDate(date, shelfLifeMonths);
        setBatchForm(prev => ({...prev, manufactureDate: date, expiryDate}));
      }
    }
  };

  const handleCreateBatch = async () => {
    if (!batchForm.productId || !batchForm.quantity || !batchForm.manufactureDate) {
      setError('Vui lòng điền đầy đủ thông tin bắt buộc');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const batchId = generateBatchId();
      const qrCode = generateQRCode(batchId);
      const product = products.find(p => p.id === batchForm.productId);

      const batchData = {
        id: batchId,
        productId: batchForm.productId,
        productName: product.name,
        quantity: parseInt(batchForm.quantity),
        manufactureDate: batchForm.manufactureDate,
        expiryDate: batchForm.expiryDate,
        productionLine: batchForm.productionLine,
        qualityControlNotes: batchForm.qualityControlNotes,
        storageLocation: batchForm.storageLocation,
        qrCode: qrCode,
        manufacturer: 'Công ty Dược ABC',
        activeIngredient: product.activeIngredient,
        dosage: product.dosage,
        storageConditions: product.storageConditions
      };

      // Call blockchain API to create batch
      const response = await manufacturerService.createBatch(batchData);

      if (response.success) {
        setGeneratedBatch({
          ...batchData,
          blockchainTx: response.data.transactionHash,
          status: 'completed',
          createdAt: new Date().toISOString()
        });

        setSuccess(`Đã tạo lô thuốc ${batchId} thành công! Transaction: ${response.data.transactionHash}`);
        
        // Reset form
        setBatchForm({
          productId: '',
          quantity: '',
          manufactureDate: '',
          expiryDate: '',
          productionLine: '',
          qualityControlNotes: '',
          storageLocation: ''
        });

        // Refresh recent batches
        await fetchRecentBatches();
      } else {
        setError(response.message || 'Không thể tạo lô thuốc');
      }
    } catch (err) {
      setError('Lỗi tạo lô thuốc: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('vi-VN');
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('vi-VN');
  };

  return (
    <div className="batch-allocation">
      <div className="page-header">
        <h1>
          <Package className="page-icon" />
          Cấp phát Lô thuốc mới
        </h1>
        <p>Tạo định danh duy nhất và ghi nhận lên blockchain</p>
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

      <div className="content-grid">
        {/* Create Batch Form */}
        <div className="create-batch-section">
          <div className="section-card">
            <div className="section-header">
              <h3>
                <Plus size={24} />
                Tạo lô thuốc mới
              </h3>
              <p>Nhập thông tin để cấp phát lô thuốc và ghi lên blockchain</p>
            </div>

            <div className="batch-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Sản phẩm *</label>
                  <select
                    value={batchForm.productId}
                    onChange={(e) => handleProductChange(e.target.value)}
                    className="form-select"
                  >
                    <option value="">Chọn sản phẩm</option>
                    {products.map(product => (
                      <option key={product.id} value={product.id}>
                        {product.name} - {product.dosage}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label>Số lượng sản xuất *</label>
                  <input
                    type="number"
                    value={batchForm.quantity}
                    onChange={(e) => setBatchForm({...batchForm, quantity: e.target.value})}
                    placeholder="VD: 10000"
                    className="form-input"
                    min="1"
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Ngày sản xuất *</label>
                  <input
                    type="date"
                    value={batchForm.manufactureDate}
                    onChange={(e) => handleManufactureDateChange(e.target.value)}
                    className="form-input"
                    max={new Date().toISOString().split('T')[0]}
                  />
                </div>

                <div className="form-group">
                  <label>Ngày hết hạn</label>
                  <input
                    type="date"
                    value={batchForm.expiryDate}
                    onChange={(e) => setBatchForm({...batchForm, expiryDate: e.target.value})}
                    className="form-input"
                    min={batchForm.manufactureDate}
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Dây chuyền sản xuất</label>
                  <select
                    value={batchForm.productionLine}
                    onChange={(e) => setBatchForm({...batchForm, productionLine: e.target.value})}
                    className="form-select"
                  >
                    <option value="">Chọn dây chuyền</option>
                    <option value="LINE_A">Dây chuyền A</option>
                    <option value="LINE_B">Dây chuyền B</option>
                    <option value="LINE_C">Dây chuyền C</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Vị trí lưu kho</label>
                  <input
                    type="text"
                    value={batchForm.storageLocation}
                    onChange={(e) => setBatchForm({...batchForm, storageLocation: e.target.value})}
                    placeholder="VD: Kho A - Kệ 1"
                    className="form-input"
                  />
                </div>
              </div>

              <div className="form-group full-width">
                <label>Ghi chú kiểm soát chất lượng</label>
                <textarea
                  value={batchForm.qualityControlNotes}
                  onChange={(e) => setBatchForm({...batchForm, qualityControlNotes: e.target.value})}
                  placeholder="Ghi chú về kiểm tra chất lượng, tiêu chuẩn đạt được..."
                  className="form-textarea"
                  rows="3"
                />
              </div>

              <div className="form-actions">
                <button 
                  onClick={handleCreateBatch}
                  disabled={loading || !batchForm.productId || !batchForm.quantity || !batchForm.manufactureDate}
                  className="btn btn-primary create-btn"
                >
                  {loading ? (
                    <>
                      <div className="spinner-small"></div>
                      Đang tạo lô...
                    </>
                  ) : (
                    <>
                      <Save size={16} />
                      Tạo lô thuốc & Ghi blockchain
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Generated Batch Info */}
        {generatedBatch && (
          <div className="generated-batch-section">
            <div className="section-card success-card">
              <div className="section-header">
                <h3>
                  <CheckCircle size={24} />
                  Lô thuốc đã được tạo thành công
                </h3>
                <p>Thông tin lô thuốc và blockchain transaction</p>
              </div>

              <div className="batch-details">
                <div className="detail-row">
                  <span className="label">Mã lô:</span>
                  <span className="value batch-id">
                    {generatedBatch.id}
                    <button 
                      onClick={() => copyToClipboard(generatedBatch.id)}
                      className="copy-btn"
                      title="Copy mã lô"
                    >
                      <Clipboard size={14} />
                    </button>
                  </span>
                </div>

                <div className="detail-row">
                  <span className="label">QR Code:</span>
                  <span className="value qr-code">
                    {generatedBatch.qrCode}
                    <button 
                      onClick={() => copyToClipboard(generatedBatch.qrCode)}
                      className="copy-btn"
                      title="Copy QR code"
                    >
                      <Clipboard size={14} />
                    </button>
                  </span>
                </div>

                <div className="detail-row">
                  <span className="label">Sản phẩm:</span>
                  <span className="value">{generatedBatch.productName}</span>
                </div>

                <div className="detail-row">
                  <span className="label">Số lượng:</span>
                  <span className="value">{generatedBatch.quantity.toLocaleString()} viên</span>
                </div>

                <div className="detail-row">
                  <span className="label">Blockchain TX:</span>
                  <span className="value blockchain-tx">
                    {generatedBatch.blockchainTx}
                    <button 
                      onClick={() => copyToClipboard(generatedBatch.blockchainTx)}
                      className="copy-btn"
                      title="Copy transaction hash"
                    >
                      <Clipboard size={14} />
                    </button>
                  </span>
                </div>

                <div className="qr-placeholder">
                  <QrCode size={64} />
                  <p>QR Code sẽ được tạo cho lô này</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recent Batches */}
      <div className="recent-batches-section">
        <div className="section-card">
          <div className="section-header">
            <h3>
              <Factory size={24} />
              Lô thuốc gần đây ({batches.length})
            </h3>
            <p>Danh sách các lô thuốc đã được tạo</p>
          </div>

          <div className="batches-table">
            <table>
              <thead>
                <tr>
                  <th>Mã lô</th>
                  <th>Sản phẩm</th>
                  <th>Số lượng</th>
                  <th>Ngày SX</th>
                  <th>Hạn SD</th>
                  <th>Trạng thái</th>
                  <th>Blockchain TX</th>
                  <th>Ngày tạo</th>
                </tr>
              </thead>
              <tbody>
                {batches.length === 0 ? (
                  <tr>
                    <td colSpan="8" className="no-data">
                      <Package size={48} className="no-data-icon" />
                      <div>
                        <h4>Chưa có lô thuốc nào</h4>
                        <p>Hãy tạo lô thuốc đầu tiên</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  batches.map(batch => (
                    <tr key={batch.id}>
                      <td className="batch-id">
                        <Hash size={14} />
                        {batch.id}
                      </td>
                      <td className="product-name">{batch.productName}</td>
                      <td className="quantity">{batch.quantity.toLocaleString()}</td>
                      <td className="date">{formatDate(batch.manufactureDate)}</td>
                      <td className="date">{formatDate(batch.expiryDate)}</td>
                      <td className="status">
                        <span className={`status-badge status-${batch.status}`}>
                          <CheckCircle size={14} />
                          Hoàn thành
                        </span>
                      </td>
                      <td className="blockchain-tx">
                        <span title={batch.blockchainTx}>
                          {batch.blockchainTx.substring(0, 10)}...
                        </span>
                        <button 
                          onClick={() => copyToClipboard(batch.blockchainTx)}
                          className="copy-btn"
                        >
                          <Clipboard size={12} />
                        </button>
                      </td>
                      <td className="datetime">{formatDateTime(batch.createdAt)}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BatchAllocation;

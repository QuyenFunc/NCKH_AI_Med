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
      console.log('Fetching products from API...');
      const response = await manufacturerService.getProducts();
      console.log('Products response:', response);
      
      if (response.success && response.data) {
        setProducts(response.data.filter(p => p.status === 'active'));
        console.log('Loaded products:', response.data.length);
      } else {
        throw new Error('Invalid response format');
      }
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Không thể tải danh sách sản phẩm: ' + err.message);
      // Set empty array as fallback
      setProducts([]);
    }
  };

  const fetchRecentBatches = async () => {
    try {
      console.log('Fetching recent batches from API...');
      const response = await manufacturerService.getBatches();
      console.log('Batches response:', response);
      
      if (response.success && response.data) {
        // Transform API data to expected format
        const transformedBatches = response.data.map(batch => {
          // Safe string processing with null checks
          const safeString = (str) => str ? String(str) : '';
          const safeSplit = (str, separator, index = 0) => {
            if (!str) return '';
            const parts = String(str).split(separator);
            return parts[index] || '';
          };

          return {
            id: safeString(batch.batchNumber || batch.id),
            productId: batch.id || 0,
            productName: safeString(batch.drugName),
            quantity: batch.quantity || 0,
            manufactureDate: safeSplit(batch.manufactureTimestamp, ' ', 0),
            expiryDate: safeSplit(batch.expiryDate, ' ', 0),
            qrCode: safeString(batch.qrCode),
            status: 'completed',
            blockchainTx: safeString(batch.transactionHash),
            createdAt: safeString(batch.createdAt)
          };
        });
        setBatches(transformedBatches);
        console.log('Loaded batches:', transformedBatches.length);
      } else {
        setBatches([]);
      }
    } catch (err) {
      console.error('Error fetching recent batches:', err);
      setBatches([]);
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

      // Validate form first
      if (!batchForm.productId || batchForm.productId === '') {
        throw new Error('Vui lòng chọn sản phẩm');
      }

      if (!batchForm.quantity || parseInt(batchForm.quantity) <= 0) {
        throw new Error('Vui lòng nhập số lượng hợp lệ');
      }

      const batchId = generateBatchId();
      const qrCode = generateQRCode(batchId);
      console.log('Available products:', products);
      console.log('Looking for product ID:', batchForm.productId, 'Type:', typeof batchForm.productId);
      
      const product = products.find(p => {
        console.log('Comparing:', p.id, 'vs', batchForm.productId, 'Types:', typeof p.id, typeof batchForm.productId);
        return Number(p.id) === Number(batchForm.productId); // Convert both to numbers
      });

      if (!product) {
        throw new Error(`Không tìm thấy sản phẩm với ID: ${batchForm.productId}. Available products: ${products.map(p => p.id).join(', ')}`);
      }

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
                        <span title={batch.blockchainTx || 'N/A'}>
                          {batch.blockchainTx ? batch.blockchainTx.substring(0, 10) + '...' : 'N/A'}
                        </span>
                        <button 
                          onClick={() => copyToClipboard(batch.blockchainTx || '')}
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

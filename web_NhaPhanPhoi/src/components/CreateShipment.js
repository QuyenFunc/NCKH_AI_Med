import React, { useState, useEffect } from 'react';
import { 
  Package, 
  MapPin, 
  Truck, 
  Calendar,
  Hash,
  AlertCircle,
  CheckCircle,
  Search,
  User,
  Phone,
  Mail,
  Building,
  ArrowRight,
  Loader
} from 'lucide-react';
import './CreateShipment.css';

const CreateShipment = () => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [batches, setBatches] = useState([]);
  const [pharmacies, setPharmacies] = useState([]);
  
  const [formData, setFormData] = useState({
    batchId: '',
    pharmacyId: '',
    quantity: '',
    trackingNumber: '',
    notes: '',
    estimatedDelivery: '',
    priority: 'normal'
  });

  const [selectedBatch, setSelectedBatch] = useState(null);
  const [selectedPharmacy, setSelectedPharmacy] = useState(null);
  const [errors, setErrors] = useState({});

  // Mock data - thay thế bằng API calls
  useEffect(() => {
    const fetchData = async () => {
      // Mock batches
      const mockBatches = [
        {
          id: 'BT001234',
          drugName: 'Paracetamol 500mg',
          manufacturer: 'ABC Pharma Ltd',
          availableQuantity: 750,
          totalQuantity: 1000,
          expiryDate: '2026-01-15',
          location: 'Kho A - Kệ 1B'
        },
        {
          id: 'BT001237',
          drugName: 'Ibuprofen 400mg',
          manufacturer: 'MediCare Inc',
          availableQuantity: 650,
          totalQuantity: 800,
          expiryDate: '2027-01-20',
          location: 'Kho B - Kệ 1A'
        },
        {
          id: 'BT001238',
          drugName: 'Cetirizine 10mg',
          manufacturer: 'PharmaTech Ltd',
          availableQuantity: 1200,
          totalQuantity: 1500,
          expiryDate: '2026-08-15',
          location: 'Kho A - Kệ 2B'
        }
      ];

      // Mock pharmacies
      const mockPharmacies = [
        {
          id: 'PH001',
          name: 'Hiệu thuốc Sài Gòn',
          address: '123 Nguyễn Văn Cừ, Q1, TP.HCM',
          contactPerson: 'Nguyễn Văn A',
          phone: '0901234567',
          email: 'contact@pharmasaigon.com',
          walletAddress: '0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC'
        },
        {
          id: 'PH002',
          name: 'Hiệu thuốc Hà Nội',
          address: '456 Phố Huế, Hai Bà Trưng, Hà Nội',
          contactPerson: 'Trần Thị B',
          phone: '0907654321',
          email: 'info@pharmahanoi.com',
          walletAddress: '0x90F79bf6EB2c4f870365E785982E1f101E93b906'
        },
        {
          id: 'PH003',
          name: 'Hiệu thuốc Miền Tây',
          address: '789 Đường 30/4, Cần Thơ',
          contactPerson: 'Lê Văn C',
          phone: '0909876543',
          email: 'support@pharmamientay.com',
          walletAddress: '0x15d34AAf54267DB7D7c367839AAf71A00a2C6A65'
        }
      ];

      setBatches(mockBatches.filter(b => b.availableQuantity > 0));
      setPharmacies(mockPharmacies);
    };

    fetchData();
  }, []);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const validateStep = (stepNumber) => {
    const newErrors = {};

    switch (stepNumber) {
      case 1:
        if (!formData.batchId) {
          newErrors.batchId = 'Vui lòng chọn lô hàng';
        }
        if (!formData.quantity) {
          newErrors.quantity = 'Vui lòng nhập số lượng';
        } else if (selectedBatch && parseInt(formData.quantity) > selectedBatch.availableQuantity) {
          newErrors.quantity = `Số lượng không được vượt quá ${selectedBatch.availableQuantity}`;
        } else if (parseInt(formData.quantity) <= 0) {
          newErrors.quantity = 'Số lượng phải lớn hơn 0';
        }
        break;

      case 2:
        if (!formData.pharmacyId) {
          newErrors.pharmacyId = 'Vui lòng chọn hiệu thuốc';
        }
        if (!formData.estimatedDelivery) {
          newErrors.estimatedDelivery = 'Vui lòng chọn ngày giao hàng dự kiến';
        }
        break;

      case 3:
        if (!formData.trackingNumber) {
          newErrors.trackingNumber = 'Vui lòng nhập mã vận đơn';
        }
        break;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep(prev => prev + 1);
    }
  };

  const handlePrevious = () => {
    setStep(prev => prev - 1);
  };

  const handleBatchSelect = (batch) => {
    setSelectedBatch(batch);
    handleInputChange('batchId', batch.id);
  };

  const handlePharmacySelect = (pharmacy) => {
    setSelectedPharmacy(pharmacy);
    handleInputChange('pharmacyId', pharmacy.id);
  };

  const generateTrackingNumber = () => {
    const prefix = 'SH';
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.random().toString(36).substring(2, 5).toUpperCase();
    const trackingNumber = `${prefix}${timestamp}${random}`;
    handleInputChange('trackingNumber', trackingNumber);
  };

  const handleSubmit = async () => {
    if (!validateStep(3)) return;

    setLoading(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // TODO: Call actual blockchain API
      console.log('Creating shipment:', {
        ...formData,
        selectedBatch,
        selectedPharmacy
      });

      // Show success and redirect
      alert('Shipment đã được tạo thành công!');
      
      // Reset form
      setFormData({
        batchId: '',
        pharmacyId: '',
        quantity: '',
        trackingNumber: '',
        notes: '',
        estimatedDelivery: '',
        priority: 'normal'
      });
      setSelectedBatch(null);
      setSelectedPharmacy(null);
      setStep(1);
      
    } catch (error) {
      console.error('Error creating shipment:', error);
      alert('Có lỗi xảy ra khi tạo shipment. Vui lòng thử lại.');
    } finally {
      setLoading(false);
    }
  };

  const getMinDate = () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  };

  const StepIndicator = () => (
    <div className="step-indicator">
      {[1, 2, 3].map((stepNumber) => (
        <div key={stepNumber} className="step-item">
          <div className={`step-circle ${step >= stepNumber ? 'active' : ''}`}>
            {step > stepNumber ? <CheckCircle size={16} /> : stepNumber}
          </div>
          <span className={`step-label ${step >= stepNumber ? 'active' : ''}`}>
            {stepNumber === 1 && 'Chọn lô hàng'}
            {stepNumber === 2 && 'Chọn điểm đến'}
            {stepNumber === 3 && 'Xác nhận'}
          </span>
          {stepNumber < 3 && <ArrowRight className="step-arrow" size={16} />}
        </div>
      ))}
    </div>
  );

  return (
    <div className="create-shipment">
      {/* Header */}
      <div className="page-header">
        <div className="header-content">
          <h1>Tạo Shipment mới</h1>
          <p>Tạo đơn vận chuyển thuốc đến hiệu thuốc</p>
        </div>
      </div>

      <StepIndicator />

      <div className="form-container">
        {/* Step 1: Select Batch */}
        {step === 1 && (
          <div className="step-content">
            <h2>Bước 1: Chọn lô hàng</h2>
            
            <div className="batch-selection">
              <div className="section-header">
                <Package size={20} />
                <span>Chọn lô hàng muốn vận chuyển</span>
              </div>

              <div className="batch-grid">
                {batches.map((batch) => (
                  <div
                    key={batch.id}
                    className={`batch-card ${selectedBatch?.id === batch.id ? 'selected' : ''}`}
                    onClick={() => handleBatchSelect(batch)}
                  >
                    <div className="batch-header">
                      <strong>{batch.drugName}</strong>
                      <span className="batch-id">{batch.id}</span>
                    </div>
                    <div className="batch-details">
                      <p>Nhà sản xuất: {batch.manufacturer}</p>
                      <p>Vị trí: {batch.location}</p>
                      <p>Hết hạn: {batch.expiryDate}</p>
                    </div>
                    <div className="batch-quantity">
                      <span className="available">{batch.availableQuantity}</span>
                      <span className="total">/ {batch.totalQuantity} viên</span>
                    </div>
                  </div>
                ))}
              </div>

              {errors.batchId && (
                <div className="error-message">
                  <AlertCircle size={16} />
                  {errors.batchId}
                </div>
              )}
            </div>

            {selectedBatch && (
              <div className="quantity-input">
                <label>Số lượng cần vận chuyển</label>
                <div className="input-group">
                  <input
                    type="number"
                    value={formData.quantity}
                    onChange={(e) => handleInputChange('quantity', e.target.value)}
                    placeholder="Nhập số lượng"
                    min="1"
                    max={selectedBatch.availableQuantity}
                  />
                  <span className="unit">viên</span>
                </div>
                <p className="help-text">
                  Tối đa: {selectedBatch.availableQuantity} viên
                </p>
                {errors.quantity && (
                  <div className="error-message">
                    <AlertCircle size={16} />
                    {errors.quantity}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Step 2: Select Pharmacy */}
        {step === 2 && (
          <div className="step-content">
            <h2>Bước 2: Chọn điểm đến</h2>
            
            <div className="pharmacy-selection">
              <div className="section-header">
                <Building size={20} />
                <span>Chọn hiệu thuốc nhận hàng</span>
              </div>

              <div className="pharmacy-grid">
                {pharmacies.map((pharmacy) => (
                  <div
                    key={pharmacy.id}
                    className={`pharmacy-card ${selectedPharmacy?.id === pharmacy.id ? 'selected' : ''}`}
                    onClick={() => handlePharmacySelect(pharmacy)}
                  >
                    <div className="pharmacy-header">
                      <h3>{pharmacy.name}</h3>
                      <span className="pharmacy-id">{pharmacy.id}</span>
                    </div>
                    <div className="pharmacy-details">
                      <div className="detail-item">
                        <MapPin size={16} />
                        <span>{pharmacy.address}</span>
                      </div>
                      <div className="detail-item">
                        <User size={16} />
                        <span>{pharmacy.contactPerson}</span>
                      </div>
                      <div className="detail-item">
                        <Phone size={16} />
                        <span>{pharmacy.phone}</span>
                      </div>
                      <div className="detail-item">
                        <Mail size={16} />
                        <span>{pharmacy.email}</span>
                      </div>
                    </div>
                    <div className="wallet-address">
                      <Hash size={14} />
                      <span>{pharmacy.walletAddress}</span>
                    </div>
                  </div>
                ))}
              </div>

              {errors.pharmacyId && (
                <div className="error-message">
                  <AlertCircle size={16} />
                  {errors.pharmacyId}
                </div>
              )}
            </div>

            <div className="delivery-details">
              <h3>Chi tiết giao hàng</h3>
              
              <div className="form-row">
                <div className="form-group">
                  <label>Ngày giao hàng dự kiến</label>
                  <input
                    type="date"
                    value={formData.estimatedDelivery}
                    onChange={(e) => handleInputChange('estimatedDelivery', e.target.value)}
                    min={getMinDate()}
                  />
                  {errors.estimatedDelivery && (
                    <div className="error-message">
                      <AlertCircle size={16} />
                      {errors.estimatedDelivery}
                    </div>
                  )}
                </div>

                <div className="form-group">
                  <label>Độ ưu tiên</label>
                  <select
                    value={formData.priority}
                    onChange={(e) => handleInputChange('priority', e.target.value)}
                  >
                    <option value="normal">Bình thường</option>
                    <option value="high">Cao</option>
                    <option value="urgent">Khẩn cấp</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step 3: Confirmation */}
        {step === 3 && (
          <div className="step-content">
            <h2>Bước 3: Xác nhận thông tin</h2>
            
            <div className="confirmation-summary">
              <div className="summary-section">
                <h3>Thông tin lô hàng</h3>
                <div className="summary-card">
                  <div className="summary-item">
                    <label>Mã lô:</label>
                    <span>{selectedBatch?.id}</span>
                  </div>
                  <div className="summary-item">
                    <label>Tên thuốc:</label>
                    <span>{selectedBatch?.drugName}</span>
                  </div>
                  <div className="summary-item">
                    <label>Số lượng:</label>
                    <span>{formData.quantity} viên</span>
                  </div>
                </div>
              </div>

              <div className="summary-section">
                <h3>Thông tin điểm đến</h3>
                <div className="summary-card">
                  <div className="summary-item">
                    <label>Hiệu thuốc:</label>
                    <span>{selectedPharmacy?.name}</span>
                  </div>
                  <div className="summary-item">
                    <label>Địa chỉ:</label>
                    <span>{selectedPharmacy?.address}</span>
                  </div>
                  <div className="summary-item">
                    <label>Người liên hệ:</label>
                    <span>{selectedPharmacy?.contactPerson}</span>
                  </div>
                  <div className="summary-item">
                    <label>Điện thoại:</label>
                    <span>{selectedPharmacy?.phone}</span>
                  </div>
                </div>
              </div>

              <div className="summary-section">
                <h3>Thông tin vận chuyển</h3>
                <div className="summary-card">
                  <div className="form-group">
                    <label>Mã vận đơn</label>
                    <div className="input-group">
                      <input
                        type="text"
                        value={formData.trackingNumber}
                        onChange={(e) => handleInputChange('trackingNumber', e.target.value)}
                        placeholder="Nhập mã vận đơn"
                      />
                      <button type="button" onClick={generateTrackingNumber} className="btn-generate">
                        Tự động tạo
                      </button>
                    </div>
                    {errors.trackingNumber && (
                      <div className="error-message">
                        <AlertCircle size={16} />
                        {errors.trackingNumber}
                      </div>
                    )}
                  </div>

                  <div className="summary-item">
                    <label>Ngày giao dự kiến:</label>
                    <span>{formData.estimatedDelivery}</span>
                  </div>
                  <div className="summary-item">
                    <label>Độ ưu tiên:</label>
                    <span>
                      {formData.priority === 'normal' && 'Bình thường'}
                      {formData.priority === 'high' && 'Cao'}
                      {formData.priority === 'urgent' && 'Khẩn cấp'}
                    </span>
                  </div>

                  <div className="form-group">
                    <label>Ghi chú (tùy chọn)</label>
                    <textarea
                      value={formData.notes}
                      onChange={(e) => handleInputChange('notes', e.target.value)}
                      placeholder="Nhập ghi chú về shipment..."
                      rows={3}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Navigation Buttons */}
        <div className="form-navigation">
          <div className="nav-left">
            {step > 1 && (
              <button 
                type="button" 
                className="btn btn-secondary"
                onClick={handlePrevious}
              >
                Quay lại
              </button>
            )}
          </div>

          <div className="nav-right">
            {step < 3 ? (
              <button 
                type="button" 
                className="btn btn-primary"
                onClick={handleNext}
              >
                Tiếp tục
                <ArrowRight size={16} />
              </button>
            ) : (
              <button 
                type="button" 
                className="btn btn-success"
                onClick={handleSubmit}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Loader size={16} className="loading-spinner" />
                    Đang tạo...
                  </>
                ) : (
                  <>
                    <CheckCircle size={16} />
                    Tạo Shipment
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateShipment;

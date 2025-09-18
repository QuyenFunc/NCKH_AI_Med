import React, { useState } from 'react';
import { Search, Plus, Trash2, QrCode, Package, Truck, Calendar } from 'lucide-react';
import './CreateShipment.css';

function CreateShipment() {
  const [selectedPharmacy, setSelectedPharmacy] = useState(null);
  const [medicineItems, setMedicineItems] = useState([]);
  const [formData, setFormData] = useState({
    deliveryDate: '',
    transportMethod: '',
    notes: ''
  });
  const [showScanner, setShowScanner] = useState(false);
  const [batchCode, setBatchCode] = useState('');

  // Mock data cho hiệu thuốc
  const pharmacies = [
    { id: 1, name: 'Hiệu thuốc ABC', address: '123 Nguyễn Trãi, Q1, HCM', phone: '0901234567' },
    { id: 2, name: 'Hiệu thuốc XYZ', address: '456 Lê Lợi, Q3, HCM', phone: '0907654321' },
    { id: 3, name: 'Hiệu thuốc DEF', address: '789 Hai Bà Trưng, Q1, HCM', phone: '0908765432' }
  ];

  // Mock data cho thuốc
  const mockMedicineData = {
    'LOT2024001': {
      name: 'Paracetamol 500mg',
      manufacturer: 'Công ty Dược ABC',
      quantity: 1000,
      expireDate: '2025-12-31',
      batchNumber: 'LOT2024001'
    },
    'LOT2024002': {
      name: 'Amoxicillin 250mg',
      manufacturer: 'Công ty Dược XYZ',
      quantity: 500,
      expireDate: '2025-06-30',
      batchNumber: 'LOT2024002'
    }
  };

  const handlePharmacySelect = (pharmacy) => {
    setSelectedPharmacy(pharmacy);
  };

  const handleScanCode = () => {
    if (batchCode && mockMedicineData[batchCode]) {
      const medicine = mockMedicineData[batchCode];
      setMedicineItems([...medicineItems, { ...medicine, id: Date.now() }]);
      setBatchCode('');
      setShowScanner(false);
    } else {
      alert('Không tìm thấy thông tin lô thuốc với mã: ' + batchCode);
    }
  };

  const removeMedicineItem = (id) => {
    setMedicineItems(medicineItems.filter(item => item.id !== id));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedPharmacy) {
      alert('Vui lòng chọn hiệu thuốc nhận hàng');
      return;
    }
    if (medicineItems.length === 0) {
      alert('Vui lòng thêm ít nhất một lô thuốc');
      return;
    }
    
    // Mock tạo lô hàng
    const shipmentData = {
      pharmacy: selectedPharmacy,
      medicines: medicineItems,
      ...formData,
      createdAt: new Date(),
      shipmentId: 'LOT' + Date.now()
    };
    
    console.log('Tạo lô hàng:', shipmentData);
    alert('Tạo lô hàng thành công! Mã lô hàng: ' + shipmentData.shipmentId);
    
    // Reset form
    setSelectedPharmacy(null);
    setMedicineItems([]);
    setFormData({ deliveryDate: '', transportMethod: '', notes: '' });
  };

  return (
    <div className="create-shipment">
      <div className="page-header">
        <h1>Tạo Lô hàng Mới</h1>
        <p>Tạo lô hàng gửi đến các hiệu thuốc đối tác</p>
      </div>

      <form onSubmit={handleSubmit} className="shipment-form">
        {/* Chọn hiệu thuốc */}
        <div className="form-section">
          <div className="section-header">
            <h2>Thông tin Người nhận</h2>
          </div>
          <div className="pharmacy-selector">
            {!selectedPharmacy ? (
              <div className="pharmacy-search">
                <div className="search-wrapper">
                  <Search className="search-icon" />
                  <input
                    type="text"
                    placeholder="Tìm kiếm hiệu thuốc..."
                    className="input search-input"
                  />
                </div>
                <div className="pharmacy-list">
                  {pharmacies.map(pharmacy => (
                    <div
                      key={pharmacy.id}
                      className="pharmacy-item"
                      onClick={() => handlePharmacySelect(pharmacy)}
                    >
                      <div className="pharmacy-info">
                        <h3>{pharmacy.name}</h3>
                        <p>{pharmacy.address}</p>
                        <p>SĐT: {pharmacy.phone}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="selected-pharmacy">
                <div className="pharmacy-info">
                  <h3>{selectedPharmacy.name}</h3>
                  <p>{selectedPharmacy.address}</p>
                  <p>SĐT: {selectedPharmacy.phone}</p>
                </div>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setSelectedPharmacy(null)}
                >
                  Đổi hiệu thuốc
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Thông tin lô hàng */}
        <div className="form-section">
          <div className="section-header">
            <h2>Thông tin Lô hàng</h2>
          </div>
          
          {/* Scanner/Input mã lô thuốc */}
          <div className="medicine-scanner">
            {!showScanner ? (
              <button
                type="button"
                className="btn btn-primary scanner-btn"
                onClick={() => setShowScanner(true)}
              >
                <QrCode />
                Quét/Nhập mã lô thuốc
              </button>
            ) : (
              <div className="scanner-form">
                <div className="input-group">
                  <input
                    type="text"
                    value={batchCode}
                    onChange={(e) => setBatchCode(e.target.value)}
                    placeholder="Nhập mã lô thuốc (VD: LOT2024001)"
                    className="input"
                  />
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleScanCode}
                  >
                    Thêm
                  </button>
                  <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => setShowScanner(false)}
                  >
                    Hủy
                  </button>
                </div>
                <p className="helper-text">
                  Mã demo có sẵn: LOT2024001, LOT2024002
                </p>
              </div>
            )}
          </div>

          {/* Danh sách thuốc đã thêm */}
          {medicineItems.length > 0 && (
            <div className="medicine-list">
              <h3>Danh sách thuốc trong lô hàng:</h3>
              {medicineItems.map(item => (
                <div key={item.id} className="medicine-item">
                  <Package className="medicine-icon" />
                  <div className="medicine-info">
                    <h4>{item.name}</h4>
                    <p>Nhà sản xuất: {item.manufacturer}</p>
                    <p>Số lượng: {item.quantity} viên</p>
                    <p>Hạn sử dụng: {item.expireDate}</p>
                    <p>Số lô: {item.batchNumber}</p>
                  </div>
                  <button
                    type="button"
                    className="btn-remove"
                    onClick={() => removeMedicineItem(item.id)}
                  >
                    <Trash2 />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Thông tin vận chuyển */}
        <div className="form-section">
          <div className="section-header">
            <h2>Thông tin Vận chuyển</h2>
          </div>
          <div className="form-grid">
            <div className="form-group">
              <label htmlFor="deliveryDate">Ngày gửi dự kiến</label>
              <div className="input-wrapper">
                <Calendar className="input-icon" />
                <input
                  id="deliveryDate"
                  type="date"
                  value={formData.deliveryDate}
                  onChange={(e) => setFormData({...formData, deliveryDate: e.target.value})}
                  className="input"
                  required
                />
              </div>
            </div>
            <div className="form-group">
              <label htmlFor="transportMethod">Phương tiện vận chuyển</label>
              <div className="input-wrapper">
                <Truck className="input-icon" />
                <select
                  id="transportMethod"
                  value={formData.transportMethod}
                  onChange={(e) => setFormData({...formData, transportMethod: e.target.value})}
                  className="input"
                  required
                >
                  <option value="">Chọn phương tiện</option>
                  <option value="truck">Xe tải</option>
                  <option value="van">Xe van</option>
                  <option value="motorcycle">Xe máy</option>
                </select>
              </div>
            </div>
          </div>
          <div className="form-group">
            <label htmlFor="notes">Ghi chú</label>
            <textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => setFormData({...formData, notes: e.target.value})}
              placeholder="Ghi chú thêm về lô hàng..."
              className="input textarea"
              rows="3"
            />
          </div>
        </div>

        {/* Submit button */}
        <div className="form-actions">
          <button type="submit" className="btn btn-primary submit-btn">
            <Package />
            Xác nhận và Gửi đi
          </button>
        </div>
      </form>
    </div>
  );
}

export default CreateShipment;




# 🔄 API Flow Summary - Drug Traceability System

## **Luồng hoạt động API theo từng giai đoạn**

### **🏭 Giai đoạn 1: Nhà Sản Xuất (web_NhaSanXuat)**

#### **1.1 Cấp phát lô thuốc (Batch Creation)**
```http
POST /api/blockchain/drugs/batches
{
  "drugName": "Paracetamol 500mg",
  "manufacturer": "Công ty Dược ABC", 
  "batchNumber": "BT20241220123456",
  "quantity": 1000,
  "expiryDate": "2025-12-31T00:00:00",
  "storageConditions": "Nơi khô ráo, tránh ánh sáng"
}
```
**✅ Blockchain Action**: Tạo NFT với `issueBatch()` smart contract

#### **1.2 Tạo lô hàng xuất**
```http
POST /api/blockchain/drugs/shipments
{
  "batchId": "123456",
  "toAddress": "0x742d35Cc6634C0532925a3b8D867B3E68b7Fbb22",
  "quantity": 500,
  "trackingInfo": "SHIPMENT-001"
}
```
**✅ Blockchain Action**: `transferOwnership()` NFT từ NSX → NPP

### **🚚 Giai đoạn 2: Nhà Phân Phối (web_NhaPhanPhoi)**

#### **2.1 Nhận hàng từ NSX**
```http
# Lấy danh sách lô hàng đến
GET /api/blockchain/drugs/shipments/recipient/{recipientAddress}

# Xác thực ownership trước khi nhận
GET /api/blockchain/drugs/shipments/{shipmentId}/verify-ownership?expectedOwner={address}

# Xác nhận nhận hàng
POST /api/blockchain/drugs/shipments/{shipmentId}/receive
```
**✅ Blockchain Action**: Xác thực NFT ownership + cập nhật trạng thái

#### **2.2 Tạo lô hàng đến hiệu thuốc**
```http
# Lấy lô thuốc thuộc sở hữu NPP
GET /api/blockchain/drugs/batches/owner/{ownerAddress}

# Tạo shipment mới đến hiệu thuốc
POST /api/blockchain/drugs/shipments
{
  "batchId": "123456",
  "toAddress": "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
  "quantity": 200,
  "trackingInfo": "SHIPMENT-002"
}
```
**✅ Blockchain Action**: `transferOwnership()` NFT từ NPP → Hiệu thuốc

### **🏥 Giai đoạn 3: Hiệu Thuốc (web_HieuThuoc)**

#### **3.1 Nhận hàng từ NPP**
```http
# Lấy pending shipments
GET /api/blockchain/drugs/shipments/recipient/{pharmacyAddress}

# Xác thực ownership
GET /api/blockchain/drugs/shipments/{shipmentId}/verify-ownership?expectedOwner={address}

# Confirm nhận hàng
POST /api/blockchain/drugs/shipments/{shipmentId}/receive
```
**✅ Blockchain Action**: Xác thực và cập nhật ownership cuối cùng

#### **3.2 Inventory Management**
```http
# Xem tồn kho
GET /api/blockchain/drugs/batches/owner/{pharmacyAddress}

# Lấy lịch sử của lô hàng
GET /api/blockchain/drugs/batches/{batchId}/transactions
```

### **📱 Giai đoạn 4: Người dùng cuối (Flutter App)**

#### **4.1 Xác thực QR Code**
```http
POST /api/blockchain/drugs/verify
{
  "qrCode": "QR_BT20241220123456_001234"
}

Response:
{
  "success": true,
  "data": {
    "isValid": true,
    "drugInfo": {
      "name": "Paracetamol 500mg",
      "manufacturer": "Công ty Dược ABC",
      "batchNumber": "BT20241220123456",
      "expiryDate": "2025-12-31"
    },
    "ownershipHistory": [
      {
        "action": "MINT",
        "fromAddress": "SYSTEM", 
        "toAddress": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "timestamp": "2024-12-20T10:00:00"
      },
      {
        "action": "TRANSFER",
        "fromAddress": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
        "toAddress": "0x742d35Cc6634C0532925a3b8D867B3E68b7Fbb22", 
        "timestamp": "2024-12-20T14:30:00"
      }
    ],
    "transactionHash": "0x1234567890abcdef..."
  }
}
```
**✅ Blockchain Action**: Đọc toàn bộ lịch sử ownership từ blockchain

## **🔗 API Endpoints Matrix**

| Endpoint | Method | NSX | NPP | HT | Flutter |
|----------|--------|-----|-----|----|---------| 
| `/blockchain/drugs/batches` | POST | ✅ | | | |
| `/blockchain/drugs/batches` | GET | ✅ | ✅ | ✅ | |
| `/blockchain/drugs/batches/owner/{address}` | GET | | ✅ | ✅ | |
| `/blockchain/drugs/shipments` | POST | ✅ | ✅ | | |
| `/blockchain/drugs/shipments/recipient/{address}` | GET | | ✅ | ✅ | |
| `/blockchain/drugs/shipments/{id}/receive` | POST | | ✅ | ✅ | |
| `/blockchain/drugs/shipments/{id}/verify-ownership` | GET | | ✅ | ✅ | |
| `/blockchain/drugs/verify` | POST | | | | ✅ |

## **🛡️ Security & Anti-Counterfeit Measures**

### **Dual Verification System**
1. **Off-chain**: Database validation
2. **On-chain**: Blockchain NFT ownership verification

### **Critical Checkpoints**
1. **NPP nhận hàng**: Verify NFT ownership trước khi accept
2. **Hiệu thuốc nhận hàng**: Double-check ownership + database consistency  
3. **QR Verification**: Full ownership history từ blockchain

### **Error Handling**
- NFT ownership mismatch → ⚠️ "Có thể là hàng giả!"
- QR không tồn tại → ❌ "Sản phẩm không hợp lệ"
- Blockchain down → 🔄 Fallback to database với warning

## **📊 Data Flow Optimization**

### **Caching Strategy**
- Batch ownership: Cache 5 phút
- Shipment status: Real-time
- Ownership history: Cache 1 giờ

### **Performance Optimizations**
- Parallel API calls cho dashboard stats
- Lazy loading cho large inventory lists
- Debounced search inputs
- Optimistic UI updates cho blockchain transactions

### **Error Recovery**
- Automatic retry cho failed blockchain calls (3x)
- Graceful degradation khi blockchain unavailable
- User-friendly error messages in Vietnamese

---

## **✅ Completion Status**

- [x] **NSX APIs**: Batch creation + Shipment to NPP
- [x] **NPP APIs**: Receive from NSX + Send to Pharmacy  
- [x] **Hiệu thuốc APIs**: Receive from NPP + Inventory
- [x] **Flutter APIs**: QR verification with full history
- [x] **Anti-counterfeit**: Dual verification system
- [x] **Error handling**: Graceful degradation
- [x] **Real data**: No mock data, all from blockchain/database

**🎯 System ready for production deployment!**

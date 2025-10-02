# NCKH AI Medical - Setup Guide

## Hệ thống truy xuất nguồn gốc thuốc sử dụng Blockchain

### Prerequisites

1. **Node.js** (v18 hoặc cao hơn)
2. **Java 21**
3. **Maven 3.6+**
4. **MySQL 8.0+**
5. **PowerShell** (Windows)

### Cấu hình Port cho các ứng dụng

- **Blockchain (Hardhat)**: Port 8545
- **Backend (Spring Boot)**: Port 8080
- **Web Nhà Sản Xuất**: Port 3001
- **Web Nhà Phân Phối**: Port 3002  
- **Web Hiệu Thuốc**: Port 3003
- **Web Người Dùng**: Port 3004
- **BlockScout Explorer**: Port 26000

### Các bước Setup

#### 1. Chuẩn bị Database

```sql
CREATE DATABASE dia5_medical_ai;
```

Cập nhật file `backend/src/main/resources/application.properties`:
```properties
spring.datasource.username=your_username
spring.datasource.password=your_password
```

#### 2. Install Dependencies

```bash
# Install backend dependencies
cd backend
mvn clean install

# Install frontend dependencies
cd ../web_NhaSanXuat
npm install

cd ../web_NhaPhanPhoi  
npm install

cd ../web_HieuThuoc
npm install

cd ../web_NguoiDung/frontend
npm install

# Install blockchain dependencies
cd ../../contracts
npm install
```

#### 3. Deploy Smart Contract

```bash
cd contracts
npx hardhat node     # Terminal 1 - Keep running
npx hardhat run scripts/deploy.js --network localhost    # Terminal 2
```

#### 4. Start All Services

Sử dụng script PowerShell:
```powershell
.\start-all-services.ps1
```

Hoặc khởi động thủ công:

**Terminal 1 - Blockchain:**
```bash
cd contracts
npx hardhat node
```

**Terminal 2 - Backend:**
```bash
cd backend  
mvn spring-boot:run
```

**Terminal 3 - Web Nhà Sản Xuất:**
```bash
cd web_NhaSanXuat
npm start
```

**Terminal 4 - Web Nhà Phân Phối:**
```bash
cd web_NhaPhanPhoi
npm start
```

**Terminal 5 - Web Hiệu Thuốc:**
```bash
cd web_HieuThuoc
npm start
```

**Terminal 6 - Web Người Dùng:**
```bash
cd web_NguoiDung/frontend
npm run dev
```

### Các URL truy cập

- **Web Nhà Sản Xuất**: http://localhost:3001
- **Web Nhà Phân Phối**: http://localhost:3002
- **Web Hiệu Thuốc**: http://localhost:3003
- **Web Người Dùng**: http://localhost:3004
- **Backend API**: http://localhost:8080
- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **BlockScout Explorer**: http://localhost:26000

### Test Blockchain Integration

Để test việc tạo batch trên blockchain:

```powershell
.\test-blockchain-integration.ps1
```

### Chức năng chính

#### Nhà Sản Xuất (Port 3001)
- Tạo lô thuốc mới và ghi lên blockchain
- Quản lý sản phẩm
- Tạo shipment giao hàng
- Xem báo cáo sản xuất

#### Nhà Phân Phối (Port 3002)  
- Nhận shipment từ nhà sản xuất
- Chuyển tiếp hàng đến hiệu thuốc
- Theo dõi inventory
- Xem lịch sử giao dịch

#### Hiệu Thuốc (Port 3003)
- Nhận hàng từ nhà phân phối
- Xác thực thuốc bằng QR code
- Bán thuốc cho người dùng cuối
- Quản lý kho

#### Người Dùng (Port 3004)
- Tra cứu thông tin thuốc
- Xác thực tính chính hãng
- Xem lịch sử xuất xứ
- Chat với AI medical assistant

### Smart Contract Functions

1. **issueBatch**: Tạo lô thuốc mới
2. **createShipment**: Tạo shipment giao hàng
3. **receiveShipment**: Nhận shipment  
4. **verifyByQRCode**: Xác thực bằng QR code
5. **verifyOwnership**: Kiểm tra quyền sở hữu

### Troubleshooting

#### Blockchain không kết nối được
- Kiểm tra Hardhat node đang chạy trên port 8545
- Verify contract address trong `application.properties`

#### Backend lỗi khi tạo batch
- Kiểm tra private key trong `application.properties`
- Đảm bảo account có role MANUFACTURER_ROLE

#### Frontend không gọi được API
- Kiểm tra CORS configuration trong backend
- Verify API URL trong các file service

### Logs và Monitoring

- Backend logs: `backend/logs/`
- Blockchain transactions: BlockScout Explorer
- Frontend console: Browser Developer Tools

### Production Deployment

1. Update environment variables
2. Use production database
3. Deploy to mainnet/testnet
4. Configure reverse proxy (nginx)
5. Enable SSL certificates
6. Set up monitoring and alerting

## Support

Để được hỗ trợ, vui lòng liên hệ NCKH AI Medical Team.

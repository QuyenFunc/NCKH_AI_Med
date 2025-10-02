# Hướng dẫn sử dụng Blockscout với PharmaLedger

## Tổng quan
Blockscout là một blockchain explorer mã nguồn mở cho phép bạn xem và tương tác với blockchain. Với project PharmaLedger, bạn có thể sử dụng Blockscout để:

- Xem các transactions của smart contract PharmaLedger
- Theo dõi việc tạo và chuyển các batch thuốc (tokens)
- Kiểm tra trạng thái của các shipment
- Verify smart contracts
- Xem chi tiết các blocks và addresses

## Cài đặt và chạy

### 1. Yêu cầu hệ thống
- Docker và Docker Compose đã được cài đặt
- Hardhat node đang chạy trên port 8545

### 2. Khởi động Hardhat Network trước
```bash
cd contracts
npm run node
```

### 3. Khởi động Blockscout
```bash
# Từ thư mục gốc của project
docker-compose up -d
```

### 4. Đợi services khởi động
Việc khởi động lần đầu có thể mất 2-5 phút. Bạn có thể theo dõi logs:
```bash
docker-compose logs -f blockscout
```

### 5. Truy cập Blockscout
- **Blockscout Explorer (qua Nginx Gateway)**: http://localhost:3000
- **API (qua Gateway, không CORS)**: http://localhost:3000/api/v2/
- **WebSocket (qua Gateway)**: ws://localhost:3000/socket/v2/websocket
- **Direct API Backend (nếu cần debug)**: http://localhost:4000/api/v2/

**Lưu ý**: Tất cả truy cập thông qua port 3000, không còn vấn đề CORS.

## Sử dụng với PharmaLedger Contract

### 1. Deploy contract
```bash
cd contracts
npm run deploy-local
```

### 2. Tìm contract trên Blockscout
1. Mở http://localhost:4000
2. Tìm kiếm contract address từ deployment
3. Xem chi tiết contract và các transactions

### 3. Verify contract (tùy chọn)
1. Vào trang contract detail
2. Click "Verify & Publish"
3. Upload source code và compiler settings

## Các endpoints hữu ích

### API Endpoints
- **All transactions**: `http://localhost:4000/api/v2/transactions`
- **Contract info**: `http://localhost:4000/api/v2/addresses/{contract_address}`
- **Token transfers**: `http://localhost:4000/api/v2/tokens/{contract_address}/transfers`

### Microservices
- **Smart Contract Verifier**: http://localhost:8050
- **Visualizer**: http://localhost:8052  
- **Signature Provider**: http://localhost:8054

## Cấu hình nâng cao

### Environment Variables
Chỉnh sửa file `blockscout.env` để thay đổi cấu hình:

```bash
# Network configuration
CHAIN_ID=1337
NETWORK_NAME=PharmaLedger Local Network

# API settings
API_V1_READ_METHODS_DISABLED=false
API_V1_WRITE_METHODS_DISABLED=false

# Features
ADMIN_PANEL_ENABLED=true
```

### Custom branding
Để thay đổi logo và colors, chỉnh sửa trong docker-compose.yml:

```yaml
environment:
  LOGO: /images/your_logo.svg
  HOMEPAGE_PLATE_BACKGROUND_COLOR: "rgb(46, 125, 50)"
  HOMEPAGE_PLATE_TEXT_COLOR: "white"
```

## Troubleshooting

### 1. Blockscout không kết nối được với Hardhat
- Kiểm tra Hardhat node đang chạy: `curl http://localhost:8545`
- Kiểm tra network settings trong docker-compose.yml

### 2. Log spam "Index had to catch up" liên tục
**Đã fix**: Indexer đã được disable (`DISABLE_INDEXER: "true"`) để tránh loop vô hạn khi không có blocks mới.
- Blockscout vẫn có thể xem transactions và blocks
- API vẫn hoạt động bình thường
- Để bật lại indexer (khi cần index historical blocks):
  ```yaml
  DISABLE_INDEXER: "false"
  ```

### 3. Database connection error
```bash
# Reset database
docker-compose down -v
docker-compose up -d
```

### 4. Services không start
```bash
# Xem logs
docker-compose logs [service_name]

# Restart specific service
docker-compose restart [service_name]
```

### 5. Memory issues
Tăng memory limit cho Docker Desktop (ít nhất 4GB)

## Dừng services

```bash
# Dừng tất cả services
docker-compose down

# Dừng và xóa volumes (reset data)
docker-compose down -v
```

## Monitoring

### Health checks
- **Blockscout**: http://localhost:4000/api/v1/health/liveness
- **Database**: Kiểm tra via pgAdmin hoặc psql client

### Performance
- Redis cache: http://localhost:6379
- PostgreSQL: http://localhost:5432

## Integration với web apps

Các web app của bạn (web_HieuThuoc, web_NhaSanXuat, web_NhaPhanPhoi) có thể sử dụng Blockscout API:

```javascript
// Example: Get contract transactions
const response = await fetch('http://localhost:4000/api/v2/addresses/{contract_address}/transactions');
const transactions = await response.json();
```

## Notes
- Đây là môi trường development, không dùng cho production
- Data sẽ bị mất khi restart containers (trừ khi dùng volumes)
- Để production, cần cấu hình SSL, security, và external database
- **Indexer đã được disable** để tránh log spam khi chưa có blocks. Blockscout vẫn có thể xem data mới khi có transactions thực tế
- Khi deploy contract và có transactions, data sẽ tự động xuất hiện trên Blockscout ngay lập tức qua API

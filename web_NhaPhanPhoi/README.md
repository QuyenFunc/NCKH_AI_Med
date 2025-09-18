# 🏭 **Nhà Phân Phối - Web Portal**

> **Giao diện web quản lý chuỗi cung ứng thuốc cho Nhà Phân Phối**  
> **Công nghệ**: React 18 + Blockchain Integration  
> **Trạng thái**: ✅ Sẵn sàng sử dụng

---

## 🚀 **Tính năng chính**

### **📊 Dashboard**
- Thống kê tổng quan về lô hàng và hoạt động giao hàng
- Biểu đồ phân tích xu hướng 6 tháng gần đây
- Hoạt động gần đây với blockchain transaction tracking
- Chỉ báo kết nối blockchain real-time

### **📦 Quản lý Lô hàng**
- Xem danh sách tất cả lô thuốc có sẵn
- Tìm kiếm và lọc theo trạng thái, tên thuốc, nhà sản xuất
- Chi tiết đầy đủ: QR code, ngày hết hạn, vị trí kho
- Cảnh báo lô hàng sắp hết hạn hoặc hết số lượng

### **🚚 Tạo Shipment**
- **Bước 1**: Chọn lô hàng và số lượng
- **Bước 2**: Chọn hiệu thuốc đích và thông tin giao hàng
- **Bước 3**: Xác nhận và tạo blockchain transaction
- Tự động tạo mã vận đơn (tracking number)
- Tích hợp với smart contract PharmaLedger

### **📍 Theo dõi Vận chuyển**
- Danh sách tất cả shipments đã tạo
- Trạng thái real-time: Pending → In Transit → Delivered
- Lịch sử blockchain transactions
- Thông tin chi tiết hiệu thuốc nhận hàng

### **📈 Báo cáo**
- Thống kê hiệu suất giao hàng
- Phân tích xu hướng theo thời gian
- Export dữ liệu CSV/PDF (sắp triển khai)

---

## 🛠️ **Công nghệ sử dụng**

### **Frontend Stack**
- **React**: 18.2.0
- **React Router**: 6.3.0 (Navigation)
- **Recharts**: 2.7.2 (Biểu đồ)
- **Lucide React**: Icons
- **Axios**: HTTP client

### **Blockchain Integration**
- **Web3j**: Java-Blockchain connector
- **PharmaLedger Smart Contract**: ERC-721 Soul-Bound Token
- **Ethereum/Hardhat**: Local blockchain network

### **Backend APIs**
- **Spring Boot**: 3.5.5
- **MySQL**: Database
- **JWT**: Authentication

---

## 🎯 **Cài đặt và chạy**

### **Prerequisites**
- Node.js >= 16.0.0
- npm >= 8.0.0
- Backend API running on port 8080
- Blockchain node running on port 8545

### **1. Cài đặt dependencies**
```bash
cd web_NhaPhanPhoi
npm install
```

### **2. Cấu hình environment**
Tạo file `.env` trong thư mục root:
```env
REACT_APP_API_URL=http://localhost:8080/api
REACT_APP_BLOCKCHAIN_NETWORK=http://localhost:8545
REACT_APP_ENV=development
```

### **3. Chạy ứng dụng (Development)**
```bash
npm start
```
Ứng dụng sẽ chạy tại: `http://localhost:3001`

### **4. Build cho Production**
```bash
npm run build
```

---

## 🔗 **API Endpoints sử dụng**

### **Blockchain APIs**
- `GET /api/blockchain/health` - Health check
- `POST /api/blockchain/distributor/shipment` - Tạo shipment
- `GET /api/blockchain/batch/{id}` - Chi tiết lô hàng
- `GET /api/blockchain/batches` - Danh sách lô hàng
- `GET /api/blockchain/shipments` - Danh sách shipments

### **Mock Data (Fallback)**
Khi backend không khả dụng, ứng dụng tự động chuyển sang mock data để demo.

---

## 📱 **Responsive Design**

### **Supported Devices**
- **Desktop**: >= 1024px (Optimal experience)
- **Tablet**: 768px - 1023px
- **Mobile**: < 768px (Limited features)

### **Browser Support**
- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

---

## 🎨 **Design System**

### **Colors**
- **Primary**: #3b82f6 (Blue)
- **Success**: #10b981 (Green)
- **Warning**: #f59e0b (Orange)
- **Danger**: #ef4444 (Red)
- **Neutral**: #64748b (Gray)

### **Typography**
- **Font Family**: Inter, -apple-system, BlinkMacSystemFont
- **Headings**: 600-700 weight
- **Body**: 400-500 weight

---

## 📁 **Cấu trúc dự án**

```
web_NhaPhanPhoi/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Layout.js          # Main layout với sidebar
│   │   ├── Dashboard.js       # Trang chủ với stats
│   │   ├── BatchManagement.js # Quản lý lô hàng
│   │   ├── CreateShipment.js  # Tạo shipment (3 bước)
│   │   ├── ShipmentTracking.js # Theo dõi vận chuyển
│   │   └── Reports.js         # Báo cáo và thống kê
│   ├── services/
│   │   └── apiService.js      # API calls & mock data
│   ├── App.js                 # Main app với routing
│   ├── index.js               # Entry point
│   └── index.css              # Global styles
├── package.json
└── README.md
```

---

## 🔧 **Development Guide**

### **Adding New Features**
1. Create component in `src/components/`
2. Add route in `App.js`
3. Update navigation in `Layout.js`
4. Add API calls in `apiService.js`

### **Styling Guidelines**
- Use BEM methodology for CSS classes
- Mobile-first responsive design
- Consistent spacing (0.5rem increments)
- Use CSS custom properties for colors

### **API Integration**
- All API calls go through `apiService.js`
- Automatic fallback to mock data
- Error handling with user-friendly messages
- Loading states for better UX

---

## 🧪 **Testing**

### **Manual Testing Workflow**
1. **Dashboard**: Verify stats và charts load correctly
2. **Batch Management**: Test search, filter, view details
3. **Create Shipment**: Complete 3-step wizard
4. **Shipment Tracking**: Verify status updates

### **Test Data**
- Mock batches: BT001234, BT001235, BT001237, BT001238
- Mock pharmacies: PH001, PH002, PH003
- Mock shipments: SH001234, SH001235

---

## 🚀 **Deployment**

### **Environment Variables**
```env
# Production
REACT_APP_API_URL=https://api.yourdomain.com/api
REACT_APP_BLOCKCHAIN_NETWORK=https://blockchain.yourdomain.com
REACT_APP_ENV=production
```

### **Docker Deployment**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3001
CMD ["npm", "start"]
```

### **Nginx Configuration**
```nginx
server {
    listen 80;
    location / {
        root /var/www/distributor-web;
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8080;
    }
}
```

---

## ⚠️ **Known Issues & Limitations**

1. **Backend Dependency**: Cần backend API để có đầy đủ tính năng
2. **Blockchain Connection**: Yêu cầu local Hardhat node
3. **Real-time Updates**: Chưa implement WebSocket/SSE
4. **File Upload**: Chưa hỗ trợ upload file đính kèm

---

## 🔄 **Changelog**

### **v1.0.0** (2025-09-18)
- ✅ Initial release
- ✅ Dashboard với statistics
- ✅ Batch management với search/filter
- ✅ Create shipment wizard (3 steps)
- ✅ API service với mock data fallback
- ✅ Responsive design
- ✅ Blockchain integration ready

---

## 📞 **Support**

- **Project**: NCKH AI Medical - Blockchain Drug Traceability
- **Team**: Distributor Portal Development
- **Version**: 1.0.0

---

🎉 **Ready for production use with blockchain backend!** 🚀

# Partner Portal - Cổng Thông Tin Đối Tác

Ứng dụng web quản lý chuỗi cung ứng dược phẩm cho hai vai trò chính: **Nhà Phân Phối** và **Chuỗi Hiệu Thuốc**.

## 🚀 Tính năng chính

### Vai trò Nhà Phân Phối 🏭
- **Dashboard**: Thống kê tổng quan về lô hàng và hoạt động giao hàng
- **Tạo Lô hàng Mới**: Quét/nhập mã lô thuốc và tạo lô hàng gửi đến hiệu thuốc
- **Quản lý Lô hàng**: Theo dõi trạng thái và lịch sử các lô hàng đã gửi

### Vai trò Chuỗi Hiệu Thuốc 🏥
- **Dashboard**: Thống kê kho hàng và các lô hàng đang chờ nhận
- **Nhận Hàng**: Quét mã lô hàng để xác thực và ghi lên blockchain
- **Quản lý Kho**: Xem và quản lý tất cả sản phẩm đã xác thực trong kho

## 🛠️ Công nghệ sử dụng

- **Frontend**: React 18, React Router DOM
- **UI/UX**: CSS3, Responsive Design
- **Icons**: Lucide React
- **Charts**: Recharts
- **State Management**: React Context API

## 📋 Yêu cầu hệ thống

- Node.js >= 14.0.0
- npm >= 6.0.0

## 🎯 Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
cd web_portal
npm install
```

### 2. Chạy ứng dụng (Development)
```bash
npm start
```

Ứng dụng sẽ chạy tại: `http://localhost:3000`

### 3. Build cho Production
```bash
npm run build
```

## 🔐 Tài khoản demo

### Nhà Phân Phối
- **Email**: `distributor@demo.com`
- **Mật khẩu**: `demo123`

### Hiệu Thuốc
- **Email**: `pharmacy@demo.com`
- **Mật khẩu**: `demo123`

## 🎮 Hướng dẫn sử dụng

### Đăng nhập
1. Truy cập trang login
2. Sử dụng tài khoản demo hoặc nhấn nút "Demo" tương ứng
3. Hệ thống sẽ chuyển hướng đến dashboard phù hợp với vai trò

### Nhà Phân Phối
1. **Tạo lô hàng mới**:
   - Chọn hiệu thuốc nhận hàng
   - Quét/nhập mã lô thuốc (demo: `LOT2024001`, `LOT2024002`)
   - Điền thông tin vận chuyển
   - Xác nhận gửi

2. **Quản lý lô hàng**:
   - Xem danh sách tất cả lô hàng
   - Lọc theo trạng thái, thời gian
   - Xem chi tiết từng lô hàng

### Hiệu Thuốc
1. **Nhận hàng**:
   - Quét/nhập mã lô hàng (demo: `LOT001234`)
   - Kiểm tra thông tin chi tiết
   - Xác nhận nhận hàng (ghi lên blockchain)

2. **Quản lý kho**:
   - Xem tồn kho hiện tại
   - Theo dõi sản phẩm sắp hết hạn/hết hàng
   - Xem lịch sử di chuyển sản phẩm

## 📱 Responsive Design

Ứng dụng được thiết kế responsive, hỗ trợ:
- Desktop (>= 1024px)
- Tablet (768px - 1023px)  
- Mobile (< 768px)

## 🎨 Design System

### Màu sắc chính
- **Primary**: #3b82f6 (Blue)
- **Secondary**: #10b981 (Green) 
- **Warning**: #f59e0b (Yellow)
- **Danger**: #ef4444 (Red)
- **Neutral**: #6b7280 (Gray)

### Typography
- **Font**: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto'
- **Heading**: 700 weight
- **Body**: 400-500 weight

## 📁 Cấu trúc thư mục

```
web_portal/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginScreen.js
│   │   │   └── LoginScreen.css
│   │   ├── layout/
│   │   │   ├── Dashboard.js
│   │   │   ├── Header.js
│   │   │   ├── Sidebar.js
│   │   │   └── MainContent.js
│   │   ├── distributor/
│   │   │   ├── DistributorDashboard.js
│   │   │   ├── CreateShipment.js
│   │   │   └── ManageShipments.js
│   │   └── pharmacy/
│   │       ├── PharmacyDashboard.js
│   │       ├── ReceiveGoods.js
│   │       └── ManageInventory.js
│   ├── contexts/
│   │   └── AuthContext.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## 🤝 Đóng góp

1. Fork project
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

Distributed under the MIT License.

## 📞 Liên hệ

- **Project**: AI Medical Diagnosis - NCKH
- **Developer**: Partner Portal Team
- **Version**: 1.0.0

---

⭐ **Lưu ý**: Đây là phiên bản demo với dữ liệu mẫu. Trong môi trường thực tế, cần tích hợp với backend API và blockchain thực tế.


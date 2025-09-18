# 🏭 **Manufacturer Portal - Nhà Sản Xuất**

Ứng dụng web quản lý sản xuất và phân phối dược phẩm dành cho **Nhà sản xuất thuốc**.

## 🚀 Tính năng chính

### 1. 📊 Dashboard (Bảng điều khiển)
- **Thống kê tổng quan**: Dòng sản phẩm, Lô đang sản xuất, Lô hàng đã xuất, Nhà phân phối đối tác
- **Biểu đồ sản xuất**: Theo dõi sản lượng và xuất hàng theo tháng
- **Phân bố danh mục**: Tỷ lệ sản xuất các loại thuốc
- **Hoạt động gần đây**: Theo dõi các hoạt động sản xuất và xuất hàng mới nhất
- **Thao tác nhanh**: Truy cập nhanh các chức năng chính

### 2. 📦 Quản lý Dòng sản phẩm
- **Thêm sản phẩm mới**: Tạo thông tin sản phẩm với đầy đủ chi tiết
- **Chỉnh sửa thông tin**: Cập nhật liều lượng, hoạt chất, điều kiện bảo quản
- **Vô hiệu hóa sản phẩm**: Ngưng sản xuất những sản phẩm không còn hiệu lực
- **Tìm kiếm & Lọc**: Theo tên, danh mục, hoạt chất, trạng thái
- **Thống kê sản xuất**: Số lô đã sản xuất, tổng sản lượng

### 3. ⚡ Cấp phát Lô thuốc mới (Core Function)
- **Tạo định danh duy nhất**: Tự động sinh mã lô theo chuẩn
- **Ghi nhận blockchain**: Lưu trữ bất biến thông tin lô thuốc
- **QR Code generation**: Tạo mã QR cho từng lô thuốc
- **Quản lý sản xuất**: Dây chuyền, vị trí kho, kiểm soát chất lượng
- **Tính toán tự động**: Hạn sử dụng dựa trên shelf life
- **Lịch sử lô thuốc**: Theo dõi tất cả lô đã được tạo

### 4. 🚚 Quản lý Xuất hàng
- **Tạo lô hàng**: Gửi thuốc đến nhà phân phối hoặc hiệu thuốc
- **Theo dõi vận chuyển**: Trạng thái giao hàng real-time
- **Quản lý đối tác**: Danh sách nhà phân phối và hiệu thuốc
- **Blockchain integration**: Cập nhật quyền sở hữu khi xuất hàng

### 5. 📈 Theo dõi & Báo cáo
- **Báo cáo sản lượng**: Thống kê theo tháng, quý, năm
- **Hiệu suất xuất hàng**: Tỷ lệ sản xuất vs xuất hàng
- **Phân tích danh mục**: Sản phẩm bán chạy, chậm luân chuyển
- **Export báo cáo**: Xuất file PDF, Excel cho báo cáo quản lý

### 6. 👥 Quản lý Tài khoản
- **Thông tin công ty**: Tên, địa chỉ, giấy phép kinh doanh
- **Quản lý nhân viên**: Danh sách, vai trò, quyền hạn
- **Cài đặt hệ thống**: Cấu hình thông báo, bảo mật

## 🛠️ Công nghệ sử dụng

- **Frontend**: React 18, React Router DOM
- **UI/UX**: CSS3, Responsive Design  
- **Icons**: Lucide React
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Blockchain**: Web3j Integration (Backend)

## 📋 Yêu cầu hệ thống

- Node.js >= 14.0.0
- npm >= 6.0.0

## 🎯 Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
cd web_NhaSanXuat
npm install
```

### 2. Chạy ứng dụng (Development)
```bash
npm start
```

Ứng dụng sẽ chạy tại: `http://localhost:3002`

### 3. Build cho Production
```bash
npm run build
```

## 🔐 Tài khoản demo

- **Email**: `manufacturer@demo.com`
- **Mật khẩu**: `demo123`
- **Công ty**: Công ty Dược phẩm ABC

## 🎮 Hướng dẫn sử dụng

### Cấp phát Lô thuốc mới (Core Feature)
1. **Chọn sản phẩm**: Từ danh sách sản phẩm đang hoạt động
2. **Nhập thông tin sản xuất**:
   - Số lượng sản xuất
   - Ngày sản xuất  
   - Dây chuyền sản xuất
   - Vị trí lưu kho
3. **Kiểm soát chất lượng**: Thêm ghi chú QC
4. **Tạo lô & Blockchain**: Hệ thống tự động:
   - Sinh mã lô duy nhất
   - Tạo QR Code
   - Ghi thông tin lên blockchain
   - Trả về transaction hash

### Quản lý Dòng sản phẩm
1. **Thêm sản phẩm mới**:
   - Tên sản phẩm, liều lượng
   - Danh mục (Giảm đau, Kháng sinh, Vitamin...)
   - Hoạt chất chính
   - Điều kiện bảo quản, hạn sử dụng
2. **Chỉnh sửa**: Click nút Edit để cập nhật thông tin
3. **Vô hiệu hóa**: Ngưng sản xuất sản phẩm không còn cần thiết

### Quản lý Xuất hàng
1. **Tạo lô hàng xuất**:
   - Chọn lô thuốc đã sản xuất
   - Chọn đối tác nhận hàng
   - Số lượng xuất hàng
2. **Theo dõi vận chuyển**: Xem trạng thái đang giao/đã giao
3. **Blockchain update**: Cập nhật quyền sở hữu tự động

## 📱 Responsive Design

Ứng dụng được thiết kế responsive, hỗ trợ:
- Desktop (>= 1024px)
- Tablet (768px - 1023px)
- Mobile (< 768px)

## 🎨 Design System

### Màu sắc chính
- **Primary**: #3498db (Blue) - Chức năng chính
- **Secondary**: #27ae60 (Green) - Thành công, hoàn thành
- **Warning**: #f39c12 (Orange) - Cảnh báo, đang xử lý
- **Danger**: #e74c3c (Red) - Lỗi, ngưng hoạt động
- **Purple**: #9b59b6 - Thông tin bổ sung

### Typography
- **Font**: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto'
- **Heading**: 600-700 weight
- **Body**: 400-500 weight

## 📁 Cấu trúc thư mục

```
web_NhaSanXuat/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Layout.js & Layout.css
│   │   ├── Dashboard.js & Dashboard.css
│   │   ├── ProductManagement.js & ProductManagement.css
│   │   ├── BatchAllocation.js & BatchAllocation.css
│   │   ├── ShipmentManagement.js & ShipmentManagement.css
│   │   ├── Reports.js & Reports.css
│   │   └── AccountManagement.js & AccountManagement.css
│   ├── services/
│   │   └── apiService.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## 🔗 API Integration

### Blockchain APIs
- `POST /api/blockchain/batches` - Tạo lô thuốc mới
- `POST /api/blockchain/shipments` - Tạo lô hàng xuất
- `GET /api/blockchain/batches/{id}` - Chi tiết lô thuốc
- `GET /api/blockchain/manufacturer/stats` - Thống kê nhà sản xuất

### Product Management APIs
- `GET /api/products` - Danh sách sản phẩm
- `POST /api/products` - Tạo sản phẩm mới
- `PUT /api/products/{id}` - Cập nhật sản phẩm
- `DELETE /api/products/{id}` - Xóa sản phẩm

## 🔧 Cấu hình

### Environment Variables
```bash
REACT_APP_API_URL=http://localhost:8080/api
```

### Backend Requirements
- Spring Boot API running on port 8080
- Blockchain integration enabled
- Database configured

## 📊 KPIs & Metrics

### Core Metrics
- **Sản lượng tháng**: Số viên thuốc sản xuất
- **Hiệu suất xuất hàng**: % lô hàng đã xuất so với sản xuất
- **Số lô blockchain**: Lô thuốc đã được ghi blockchain
- **Đối tác hoạt động**: Nhà phân phối & hiệu thuốc

### Business Intelligence
- Phân tích xu hướng sản xuất
- Dự báo nhu cầu theo danh mục
- Hiệu suất dây chuyền sản xuất
- Tối ưu hóa inventory

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
- **Developer**: Manufacturer Portal Team
- **Version**: 1.0.0

---

⭐ **Lưu ý**: Core feature là **Cấp phát Lô thuốc mới** với blockchain integration. Tất cả lô thuốc được tạo sẽ có định danh duy nhất và được ghi nhận bất biến trên blockchain để đảm bảo truy xuất nguồn gốc.
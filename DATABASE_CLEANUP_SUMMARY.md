# Database Cleanup Summary - Pharmacy Tables

## 📊 Phân tích 2 bảng trùng lặp

### ✅ `pharma_companies` (GIỮ LẠI)
**Bảng hiện đại, đa năng cho tất cả công ty dược**

| Trường | Mô tả |
|--------|-------|
| `company_type` | ENUM(MANUFACTURER, DISTRIBUTOR, PHARMACY) |
| `blockchain_verified` | Xác thực blockchain |
| `wallet_address` | Địa chỉ ví blockchain |
| `manufacturer_user_id` | Liên kết với user |
| `is_active` | Trạng thái hoạt động |

**Sử dụng trong code:**
- ✅ DrugTraceabilityService (8 lần)
- ✅ ShipmentAdapter (16 lần) 
- ✅ DrugProductController (19 lần)
- ✅ PharmaCompanyRepository (5 lần)
- **Tổng: 53 lần sử dụng**

### ❌ `pharmacies` (ĐÃ XÓA)
**Bảng cũ, chỉ dành cho hiệu thuốc**

| Trường | Mô tả |
|--------|-------|
| `status` | ENUM(ACTIVE, INACTIVE, SUSPENDED) |
| `manager` | Tên quản lý |
| `license_issue_date` | Ngày cấp phép |
| `license_expiry_date` | Ngày hết hạn |
| `website` | Website |

**Vấn đề:**
- ❌ Chỉ dành riêng cho pharmacy
- ❌ Trùng lặp với `pharmacy_users` (bảng đăng nhập)
- ❌ Không tích hợp blockchain tốt
- ❌ Thiết kế cũ, không linh hoạt

---

## 🔧 Thay đổi đã thực hiện

### 1. **Xóa Database Table**
```sql
-- Backup trước khi xóa
CREATE TABLE pharmacies_backup_20250930 AS SELECT * FROM pharmacies;

-- Xóa bảng cũ
DROP TABLE IF EXISTS pharmacies;
```

### 2. **Xóa Model & Repository**
- ❌ Deleted: `backend/src/main/java/com/nckh/dia5/model/Pharmacy.java`
- ❌ Deleted: `backend/src/main/java/com/nckh/dia5/repository/PharmacyRepository.java`

### 3. **Cập nhật Controller**
**File: `PharmacyController.java`**

**Trước:**
```java
import com.nckh.dia5.model.Pharmacy;
import com.nckh.dia5.repository.PharmacyRepository;

private final PharmacyRepository pharmacyRepository;

List<Pharmacy> pharmacies = pharmacyRepository.findByStatusOrderByName(
    Pharmacy.PharmacyStatus.ACTIVE);
```

**Sau:**
```java
import com.nckh.dia5.model.PharmaCompany;
import com.nckh.dia5.repository.PharmaCompanyRepository;

private final PharmaCompanyRepository pharmaCompanyRepository;

List<PharmaCompany> pharmacies = pharmaCompanyRepository.findByCompanyTypeAndIsActive(
    PharmaCompany.CompanyType.PHARMACY, true);
```

---

## 📋 Cấu trúc hệ thống SAU khi cleanup

### Bảng liên quan đến Pharmacy:

1. **`pharmacy_users`** - Đăng nhập hiệu thuốc ✅
   - Email, password
   - pharmacy_name, pharmacy_code
   - wallet_address
   - Được sử dụng cho authentication

2. **`pharma_companies`** - Thông tin công ty ✅
   - company_type = 'PHARMACY' cho hiệu thuốc
   - Quản lý tất cả: NSX, NPP, Hiệu thuốc
   - Tích hợp blockchain đầy đủ

### Flow hoạt động:

```
1. User đăng nhập → pharmacy_users (authentication)
2. Lấy wallet_address từ pharmacy_users
3. Tìm thông tin công ty → pharma_companies (WHERE wallet_address = ?)
4. Sử dụng company_type để phân biệt PHARMACY/MANUFACTURER/DISTRIBUTOR
```

---

## ✅ Checklist hoàn thành

- [x] Phân tích 2 bảng trùng lặp
- [x] Xác định bảng nào giữ lại (pharma_companies)
- [x] Backup bảng pharmacies
- [x] Xóa bảng pharmacies trong database
- [x] Xóa model Pharmacy.java
- [x] Xóa repository PharmacyRepository.java
- [x] Cập nhật PharmacyController.java
- [x] Tạo script SQL cleanup

---

## 🚀 Cách chạy

### 1. Chạy SQL Script
```bash
mysql -u root -p dia5_medical_ai < cleanup_duplicate_pharmacy_table.sql
```

### 2. Restart Backend
```bash
cd backend
./mvnw spring-boot:run
```

### 3. Verify
- ✅ Backend khởi động không lỗi
- ✅ API `/api/pharmacies` hoạt động
- ✅ Không còn reference đến bảng `pharmacies`

---

## 📝 Notes

- Backup table được lưu tại: `pharmacies_backup_20250930`
- Nếu cần rollback, restore từ backup table
- Frontend không bị ảnh hưởng (API endpoint không đổi)
- PharmaCompany với company_type='PHARMACY' thay thế hoàn toàn Pharmacy

---

**Ngày thực hiện:** 30/09/2025  
**Trạng thái:** ✅ Hoàn thành

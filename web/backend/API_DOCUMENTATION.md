# Dia5 Medical AI API Documentation

## Tổng quan

API cho ứng dụng chẩn đoán y tế thông minh Dia5, cung cấp các endpoint để quản lý người dùng, báo cáo triệu chứng, và tương tác với hệ thống AI chẩn đoán.

**Base URL**: `http://localhost:8080`  
**Version**: 1.0.0  
**Authentication**: JWT Bearer Token

## Cấu trúc Response chung

Tất cả API responses đều tuân theo cấu trúc sau:

```json
{
  "success": true,
  "message": "Thông báo",
  "data": {
    /* Dữ liệu response */
  },
  "statusCode": 200,
  "timestamp": "2024-01-01T10:00:00"
}
```

## Authentication

### Headers yêu cầu cho protected endpoints

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## 1. Authentication API

### 1.1. Đăng ký tài khoản

**POST** `/api/auth/register`

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "confirmPassword": "password123",
  "name": "Tên người dùng"
}
```

**Response Success (200):**

```json
{
  "success": true,
  "message": "Đăng ký thành công",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "tokenType": "Bearer",
    "expiresIn": 86400,
    "user": {
      "id": "user-id",
      "email": "user@example.com",
      "name": "Tên người dùng",
      "isProfileComplete": false,
      "isActive": true
    }
  }
}
```

### 1.2. Đăng nhập

**POST** `/api/auth/login`

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:** Tương tự như đăng ký

### 1.3. Đăng xuất

**POST** `/api/auth/logout`

**Response Success (200):**

```json
{
  "success": true,
  "message": "Đăng xuất thành công",
  "data": null
}
```

### 1.4. Kiểm tra trạng thái đăng nhập

**GET** `/api/auth/me`

**Response Success (200):**

```json
{
  "success": true,
  "data": {
    "id": "user-id",
    "email": "user@example.com",
    "name": "Tên người dùng",
    "isProfileComplete": true,
    "isActive": true
  }
}
```

---

## 2. User Management API

### 2.1. Lấy thông tin người dùng hiện tại

**GET** `/api/users/me`

**Response Success (200):**

```json
{
  "success": true,
  "data": {
    "id": "user-id",
    "email": "user@example.com",
    "name": "Tên người dùng",
    "isProfileComplete": true,
    "isActive": true,
    "createdAt": "2024-01-01T10:00:00",
    "updatedAt": "2024-01-01T10:00:00"
  }
}
```

### 2.2. Lấy profile đầy đủ của người dùng

**GET** `/api/users/profile`

**Response Success (200):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "user-id",
      "email": "user@example.com",
      "name": "Tên người dùng"
    },
    "demographics": {
      "birthYear": 1990,
      "birthMonth": 5,
      "gender": "MALE",
      "heightCm": 175,
      "weightKg": 70.5,
      "bloodType": "A_POSITIVE",
      "educationLevel": "UNIVERSITY"
    },
    "location": {
      "provinceId": 1,
      "provinceName": "Hà Nội"
    }
  }
}
```

### 2.3. Cập nhật profile người dùng

**PUT** `/api/users/profile`

**Request Body:**

```json
{
  "name": "Tên mới",
  "birthYear": 1990,
  "birthMonth": 5,
  "gender": "MALE",
  "heightCm": 175,
  "weightKg": 70.5,
  "bloodType": "A_POSITIVE",
  "provinceId": 1,
  "occupation": "Kỹ sư phần mềm",
  "educationLevel": "UNIVERSITY"
}
```

**Response:** Tương tự như GET profile

### 2.4. Lấy thông tin người dùng theo ID

**GET** `/api/users/{userId}`

**Response:** Tương tự như GET current user

---

## 3. Medical Specialty API

### 3.1. Lấy danh sách tất cả chuyên khoa

**GET** `/api/medical-specialties`

**Response Success (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Nội khoa",
      "description": "Chuyên khoa điều trị các bệnh nội khoa",
      "parentId": null,
      "isActive": true
    }
  ]
}
```

### 3.2. Lấy danh sách chuyên khoa gốc

**GET** `/api/medical-specialties/root`

### 3.3. Lấy danh sách chuyên khoa con

**GET** `/api/medical-specialties/parent/{parentId}`

### 3.4. Tìm kiếm chuyên khoa

**GET** `/api/medical-specialties/search?keyword={keyword}`

---

## 4. Province Management API

### 4.1. Lấy danh sách tất cả tỉnh thành

**GET** `/api/provinces`

**Response Success (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Hà Nội",
      "code": "HN",
      "region": "NORTH",
      "climate": "SUBTROPICAL",
      "population": 8000000
    }
  ]
}
```

### 4.2. Lấy danh sách tỉnh thành theo vùng

**GET** `/api/provinces/region/{region}`

**Region values:** `NORTH`, `CENTRAL`, `SOUTH`

### 4.3. Lấy danh sách tỉnh thành theo khí hậu

**GET** `/api/provinces/climate/{climate}`

**Climate values:** `TROPICAL`, `SUBTROPICAL`, `TEMPERATE`

---

## 5. Symptom Report API

### 5.1. Báo cáo triệu chứng

**POST** `/api/symptom-reports`

**Request Body:**

```json
{
  "sessionId": "session-123",
  "symptomId": 1,
  "severity": 7,
  "durationHours": 24,
  "frequency": "DAILY",
  "triggers": ["stress", "lack_of_sleep"],
  "associatedSymptoms": ["headache", "fatigue"],
  "locationBodyPart": "head",
  "qualityDescription": "throbbing pain",
  "onsetType": "GRADUAL"
}
```

**Response Success (200):**

```json
{
  "success": true,
  "message": "Báo cáo triệu chứng thành công",
  "data": {
    "id": "report-id",
    "sessionId": "session-123",
    "symptomId": 1,
    "severity": 7,
    "durationHours": 24,
    "frequency": "DAILY",
    "reportedAt": "2024-01-01T10:00:00"
  }
}
```

### 5.2. Lấy danh sách báo cáo triệu chứng của người dùng

**GET** `/api/symptom-reports?page=0&size=20&sortBy=reportedAt&sortDir=desc`

**Query Parameters:**

- `page` (int): Số trang (default: 0)
- `size` (int): Kích thước trang (default: 20)
- `sortBy` (string): Trường sắp xếp (default: reportedAt)
- `sortDir` (string): Hướng sắp xếp - asc/desc (default: desc)

**Response Success (200):**

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "id": "report-id",
        "sessionId": "session-123",
        "symptomId": 1,
        "severity": 7,
        "reportedAt": "2024-01-01T10:00:00"
      }
    ],
    "pageable": {
      "pageNumber": 0,
      "pageSize": 20,
      "sort": {
        "sorted": true,
        "direction": "DESC",
        "properties": ["reportedAt"]
      }
    },
    "totalElements": 100,
    "totalPages": 5,
    "first": true,
    "last": false
  }
}
```

### 5.3. Lấy báo cáo triệu chứng theo phiên

**GET** `/api/symptom-reports/session/{sessionId}`

### 5.4. Lấy danh sách ID phiên của người dùng

**GET** `/api/symptom-reports/sessions`

**Response Success (200):**

```json
{
  "success": true,
  "data": ["session-123", "session-456", "session-789"]
}
```

### 5.5. Đếm số báo cáo triệu chứng của người dùng

**GET** `/api/symptom-reports/count`

**Response Success (200):**

```json
{
  "success": true,
  "data": 25
}
```

---

## 6. AI Diagnosis API

### 6.1. Chẩn đoán AI từ triệu chứng

**POST** `/api/ai-diagnosis/diagnose/{sessionId}`

**Description:** Gọi AI service để chẩn đoán dựa trên các triệu chứng đã báo cáo trong session

**Response Success (200):**

```json
{
  "success": true,
  "message": "Chẩn đoán AI thành công",
  "data": {
    "diagnosisId": "diag-123",
    "sessionId": "session-123",
    "results": [
      {
        "diseaseName": "Cảm cúm",
        "diseaseCode": "J11",
        "probability": 0.85,
        "description": "Bệnh cảm cúm do virus gây ra",
        "severity": "MILD",
        "matchedSymptoms": ["sốt", "ho", "đau đầu"],
        "additionalQuestions": ["Bạn có tiếp xúc với người bệnh không?"],
        "recommendedSpecialty": "Nội khoa",
        "requiresImmediateAttention": false
      }
    ],
    "recommendations": [
      "Nghỉ ngơi đầy đủ",
      "Uống nhiều nước",
      "Theo dõi triệu chứng"
    ],
    "urgencyLevel": "LOW",
    "confidenceScore": 0.82,
    "generatedAt": "2024-01-01T10:00:00",
    "disclaimerMessage": "Kết quả chỉ mang tính chất tham khảo, vui lòng tham khảo ý kiến bác sĩ"
  }
}
```

### 6.2. Lấy lịch sử chẩn đoán AI

**GET** `/api/ai-diagnosis/history`

**Response Success (200):**

```json
{
  "success": true,
  "data": [
    {
      "id": "diag-id",
      "sessionId": "session-123",
      "diagnosisResults": "[{...}]",
      "recommendations": "Nghỉ ngơi; Uống thuốc",
      "urgencyLevel": "LOW",
      "confidenceScore": 0.82,
      "generatedAt": "2024-01-01T10:00:00"
    }
  ]
}
```

### 6.3. Lấy kết quả chẩn đoán theo session

**GET** `/api/ai-diagnosis/session/{sessionId}`

**Response Success (200):**

```json
{
  "success": true,
  "data": {
    "id": "diag-id",
    "sessionId": "session-123",
    "diagnosisResults": "[{...}]",
    "recommendations": "Nghỉ ngơi; Uống thuốc",
    "urgencyLevel": "LOW",
    "confidenceScore": 0.82,
    "generatedAt": "2024-01-01T10:00:00"
  }
}
```

---

## Error Responses

### 400 Bad Request

```json
{
  "success": false,
  "message": "Dữ liệu không hợp lệ",
  "statusCode": 400,
  "timestamp": "2024-01-01T10:00:00"
}
```

### 401 Unauthorized

```json
{
  "success": false,
  "message": "Token không hợp lệ hoặc đã hết hạn",
  "statusCode": 401,
  "timestamp": "2024-01-01T10:00:00"
}
```

### 403 Forbidden

```json
{
  "success": false,
  "message": "Không có quyền truy cập",
  "statusCode": 403,
  "timestamp": "2024-01-01T10:00:00"
}
```

### 404 Not Found

```json
{
  "success": false,
  "message": "Không tìm thấy tài nguyên",
  "statusCode": 404,
  "timestamp": "2024-01-01T10:00:00"
}
```

### 500 Internal Server Error

```json
{
  "success": false,
  "message": "Lỗi server nội bộ",
  "statusCode": 500,
  "timestamp": "2024-01-01T10:00:00"
}
```

---

## Data Types và Enums

### Gender

- `MALE`: Nam
- `FEMALE`: Nữ
- `OTHER`: Khác

### BloodType

- `A_POSITIVE`: A+
- `A_NEGATIVE`: A-
- `B_POSITIVE`: B+
- `B_NEGATIVE`: B-
- `AB_POSITIVE`: AB+
- `AB_NEGATIVE`: AB-
- `O_POSITIVE`: O+
- `O_NEGATIVE`: O-

### EducationLevel

- `PRIMARY`: Tiểu học
- `SECONDARY`: Trung học cơ sở
- `HIGH_SCHOOL`: Trung học phổ thông
- `VOCATIONAL`: Trung cấp nghề
- `COLLEGE`: Cao đẳng
- `UNIVERSITY`: Đại học
- `POSTGRADUATE`: Sau đại học

### Frequency

- `NEVER`: Không bao giờ
- `RARELY`: Hiếm khi
- `SOMETIMES`: Thỉnh thoảng
- `OFTEN`: Thường xuyên
- `DAILY`: Hàng ngày
- `CONSTANT`: Liên tục

### OnsetType

- `SUDDEN`: Đột ngột
- `GRADUAL`: Từ từ
- `INTERMITTENT`: Không liên tục

### UrgencyLevel (AI Diagnosis)

- `LOW`: Mức độ thấp - có thể theo dõi tại nhà
- `MEDIUM`: Mức độ trung bình - nên đến khám trong vài ngày
- `HIGH`: Mức độ cao - cần đến khám ngay
- `CRITICAL`: Nguy cấp - cần cấp cứu ngay lập tức

### Severity (Disease)

- `MILD`: Nhẹ
- `MODERATE`: Trung bình
- `SEVERE`: Nặng
- `CRITICAL`: Nguy kịch

---

## Rate Limiting

- Tối đa 1000 requests/giờ cho mỗi user
- Tối đa 100 requests/phút cho authentication endpoints

## Notes

1. Tất cả timestamps đều sử dụng ISO 8601 format
2. JWT tokens có thời gian sống 24 giờ
3. Passwords phải có ít nhất 6 ký tự
4. Email phải đúng định dạng và unique trong hệ thống
5. Tất cả số điện thoại phải tuân theo định dạng Việt Nam

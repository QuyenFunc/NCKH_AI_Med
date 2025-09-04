# Database Setup Guide for Dia5 Medical App

## 📊 Current Status
- ✅ Mock data trong Flutter app
- ✅ Database schema designed 
- ❌ MySQL chưa được setup
- ❌ Backend API chưa được triển khai

## 🗄️ Files đã tạo:

### 1. `database_schema.sql`
- Schema MySQL hoàn chỉnh
- 8 tables chính: users, user_profiles, medical_history, chat_history, news_articles, etc.
- Indexes và relationships
- Sample data cho provinces và chronic diseases

### 2. `backend_api_example.php`
- REST API example bằng PHP
- Endpoints: /auth/login, /auth/register, /profile/save, /news, /chat
- Password hashing với bcrypt
- JSON responses

## 🚀 Bước triển khai:

### Bước 1: Setup MySQL Database
```bash
# 1. Cài đặt MySQL
# 2. Tạo database
mysql -u root -p
CREATE DATABASE dia5_medical_app;

# 3. Import schema
mysql -u root -p dia5_medical_app < database_schema.sql
```

### Bước 2: Setup Backend Server
```bash
# Option A: PHP + Apache/Nginx
cp backend_api_example.php /var/www/html/api/

# Option B: Node.js Express
# Option C: Python Flask/Django
```

### Bước 3: Update Flutter Services
Trong các file service, thay thế mock methods:

```dart
// lib/services/auth_service.dart
Future<Map<String, dynamic>?> _realLoginAPI(String email, String password) async {
  final response = await http.post(
    Uri.parse('$_baseUrl/auth/login'),
    headers: {'Content-Type': 'application/json'},
    body: json.encode({'email': email, 'password': password}),
  );
  
  if (response.statusCode == 200) {
    return json.decode(response.body);
  }
  return null;
}
```

### Bước 4: RSS News Integration
```php
// Backend PHP script để lấy RSS từ suckhoedoisong.vn
function fetchRSSNews() {
    $rss = simplexml_load_file('https://suckhoedoisong.vn/rss/y-te-13.rss');
    // Parse và lưu vào database
}
```

## 🔧 Environment Variables cần thiết:
```
DB_HOST=localhost
DB_NAME=dia5_medical_app
DB_USER=your_username
DB_PASS=your_password
API_BASE_URL=https://your-domain.com/api
```

## 📱 Cấu trúc Data Flow:
```
Flutter App → HTTP Request → Backend API → MySQL Database
            ← JSON Response ←              ←
```

## 🔐 Security Features:
- ✅ Password hashing (SHA-256 + salt)
- ✅ SQL injection protection (PDO prepared statements)
- ✅ CORS headers
- ❌ JWT authentication (cần implement)
- ❌ Rate limiting (cần implement)
- ❌ Input validation (cần strengthen)

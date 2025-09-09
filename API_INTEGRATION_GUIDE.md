# Hướng dẫn tích hợp API Backend cho Android App

## Tổng quan
Đã hoàn thành việc tích hợp Android Flutter app với backend Java Spring Boot. Các API services đã được tạo và cấu hình sẵn sàng để sử dụng.

## Các Services đã tạo

### 1. ApiService (`lib/services/api_service.dart`)
- Service tổng quát để quản lý HTTP requests
- Hỗ trợ GET, POST, PUT, DELETE
- Tự động xử lý authentication headers
- Error handling và timeout configuration
- Base URL: `http://10.0.2.2:8080/api` (cho Android emulator)

### 2. AuthService (`lib/services/auth_service.dart`)
- Đăng ký, đăng nhập, đăng xuất
- Quản lý JWT token
- Lưu trữ thông tin user và profile
- API endpoints:
  - `POST /auth/login`
  - `POST /auth/register` 
  - `POST /auth/logout`
  - `GET /auth/me`
  - `POST /users/profile`

### 3. ChatService (`lib/services/chat_service.dart`)
- Tạo và quản lý chat sessions
- Gửi tin nhắn user và lưu vào backend
- Stream response từ Python chatbot
- Lưu AI response vào backend
- API endpoints:
  - `POST /chat/sessions`
  - `POST /chat/sessions/{sessionId}/messages`
  - `POST /chat/sessions/{sessionId}/ai-response`
  - `GET /chat/sessions/{sessionId}/messages`
  - `GET /chat/sessions`

### 4. DiagnosisService (`lib/services/diagnosis_service.dart`)
- Thực hiện AI diagnosis cho chat session
- Lấy lịch sử chẩn đoán
- API endpoints:
  - `POST /ai-diagnosis/diagnose/{sessionId}`
  - `GET /ai-diagnosis/history`
  - `GET /ai-diagnosis/session/{sessionId}`

## Cấu hình đã thực hiện

### Android Manifest
- Thêm INTERNET và ACCESS_NETWORK_STATE permissions
- Thêm `android:usesCleartextTraffic="true"` để cho phép HTTP requests

### Models cập nhật
- User model đã được cập nhật để match với backend DTOs
- Thêm các response models cho API calls

### UI Screens cập nhật  
- LoginScreen: Sử dụng AuthResult thay vì boolean
- RegisterScreen: Xử lý lỗi chi tiết hơn
- ChatScreen: Tích hợp với backend chat API và streaming

## Cách test API connections

### 1. Khởi động Backend
```bash
cd web/backend
./mvnw spring-boot:run
```
Backend sẽ chạy trên port 8080.

### 2. Khởi động Python Chatbot (tùy chọn)
```bash
cd web/chatbox
python medical_chatbot_enhanced.py
```
Chatbot sẽ chạy trên port 5001.

### 3. Test trên Android Emulator
```bash
flutter run
```

### 4. Kiểm tra kết nối

#### Cách 1: Test thông qua UI
- Đăng ký tài khoản mới
- Đăng nhập
- Gửi tin nhắn trong chat
- Kiểm tra console logs để xem API calls

#### Cách 2: Sử dụng API Test Script
Thêm vào `lib/main.dart`:
```dart
import 'services/api_test.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await AuthService.instance.initialize();
  
  // Uncomment để chạy API tests
  // await runApiTests();
  
  runApp(const Dia5App());
}
```

#### Debug Console Output
Kiểm tra các logs sau trong console:
- `🌐 Testing network connectivity...`
- `🏥 Testing backend services health...`
- `🔐 Testing Auth API...`
- `💬 Testing Chat API...`
- `🔬 Testing Diagnosis API...`

## Troubleshooting

### Lỗi kết nối network
- Đảm bảo backend đang chạy trên port 8080
- Kiểm tra firewall không block port
- Với physical device, thay `10.0.2.2` bằng IP thực của máy
- Chạy `flutter run` với `--verbose` để xem chi tiết logs

### Các lỗi thường gặp

#### 1. `SocketException: Connection refused`
```bash
# Kiểm tra backend có chạy không
curl http://localhost:8080/api/chat/health

# Nếu không chạy, khởi động backend
cd web/backend
./mvnw spring-boot:run
```

#### 2. `TimeoutException: Request timeout`
- Tăng timeout trong ApiService
- Kiểm tra network connectivity
- Backend có thể đang overload

#### 3. `401 Unauthorized`
- Token đã hết hạn, đăng nhập lại
- Kiểm tra JWT secret trong backend config

#### 4. Lỗi CORS
- Backend đã cấu hình CORS cho development
- Nếu vẫn lỗi, kiểm tra `application.properties`

#### 5. Lỗi SSL/TLS
- App đã cấu hình `usesCleartextTraffic="true"`
- Cho phép HTTP requests trong development

### Debug Commands
```bash
# Xem logs chi tiết
flutter run --verbose

# Xem logs device
flutter logs

# Clear cache nếu cần
flutter clean && flutter pub get
```

## URLs cần cập nhật khi deploy

### Development (hiện tại)
- Backend API: `http://10.0.2.2:8080/api`
- Python Chatbot: `http://10.0.2.2:5001`

### Production (cần thay đổi)
- Backend API: `https://your-backend-domain.com/api`
- Python Chatbot: `https://your-chatbot-domain.com`

## Database Requirements

Backend cần MySQL database với schema:
- Database name: `dia5_medical_ai`
- Username: `root` 
- Password: (empty trong development)

## Next Steps

1. ✅ Test đăng ký/đăng nhập
2. ✅ Test chat functionality
3. ⏳ Test AI diagnosis
4. ⏳ Test với real backend data
5. ⏳ Performance optimization
6. ⏳ Production deployment setup

## Ghi chú quan trọng

- API service tự động handle JWT token
- Error messages được hiển thị bằng tiếng Việt
- Timeout được set 30 giây cho mỗi request
- Chat streaming hoạt động real-time
- Tất cả API calls đều có error handling

## File đã thay đổi

```
lib/services/
├── api_service.dart (NEW)
├── auth_service.dart (UPDATED)
├── chat_service.dart (UPDATED)
└── diagnosis_service.dart (NEW)

lib/models/
└── user.dart (UPDATED)

lib/screens/
├── login_screen.dart (UPDATED)
├── register_screen.dart (UPDATED)
└── chat_screen.dart (UPDATED)

android/app/src/main/
└── AndroidManifest.xml (UPDATED)
```

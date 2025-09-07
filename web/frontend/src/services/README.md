# Services

## AuthService

Service để xử lý authentication với backend Spring Boot.

### Các phương thức:

- `login(credentials)`: Đăng nhập
- `register(userData)`: Đăng ký
- `logout()`: Đăng xuất
- `getCurrentUser()`: Lấy thông tin user hiện tại
- `saveToken(token)`: Lưu JWT token
- `getToken()`: Lấy JWT token
- `getUserInfo()`: Lấy thông tin user từ localStorage
- `isAuthenticated()`: Kiểm tra đã đăng nhập chưa
- `clearAuth()`: Xóa thông tin xác thực
- `getAuthHeaders()`: Tạo Authorization header

### Sử dụng:

```typescript
import { AuthService } from "./auth.service";

// Đăng nhập
try {
  const response = await AuthService.login({ email, password });
  console.log("Login successful:", response);
} catch (error) {
  console.error("Login failed:", error.message);
}

// Đăng ký
try {
  const response = await AuthService.register({
    name,
    email,
    password,
    confirmPassword,
  });
  console.log("Register successful:", response);
} catch (error) {
  console.error("Register failed:", error.message);
}
```

### Backend API Endpoints:

- `POST /api/auth/login`: Đăng nhập
- `POST /api/auth/register`: Đăng ký
- `POST /api/auth/logout`: Đăng xuất
- `GET /api/auth/me`: Lấy thông tin user hiện tại

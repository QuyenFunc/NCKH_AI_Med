# Dia5 Medical AI API

API backend cho ứng dụng chẩn đoán y tế thông minh Dia5, được xây dựng bằng Spring Boot với JWT Authentication và RAG-based AI Chatbot sử dụng dữ liệu từ WHO ICD-11.

## Tính năng chính

- **Quản lý người dùng**: Đăng ký, đăng nhập, quản lý profile
- **JWT Authentication**: Bảo mật API với token JWT
- **Quản lý dữ liệu y tế**: Triệu chứng, bệnh, thuốc, dị ứng
- **Báo cáo triệu chứng**: Ghi lại và theo dõi triệu chứng của người dùng
- **RAG-based AI Chatbot**: Sử dụng dữ liệu WHO ICD-11 với FAISS vector search
- **API Documentation**: Swagger UI tích hợp
- **Database**: MySQL với JPA/Hibernate

## Công nghệ sử dụng

- **Java 21**
- **Spring Boot 3.5.5**
- **Spring Security** với JWT
- **Spring Data JPA**
- **MySQL**
- **Lombok**
- **MapStruct**
- **Swagger/OpenAPI 3**
- **Maven**

## Cài đặt và chạy

### Yêu cầu hệ thống

- Java 21 hoặc cao hơn
- MySQL 8.0 hoặc cao hơn
- Maven 3.6 hoặc cao hơn

### Cấu hình database

1. Tạo database MySQL:

```sql
CREATE DATABASE dia5_medical_ai;
```

2. Cập nhật thông tin database trong `src/main/resources/application.properties`:

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/dia5_medical_ai?useSSL=false&serverTimezone=UTC&allowPublicKeyRetrieval=true
spring.datasource.username=your_username
spring.datasource.password=your_password
```

3. Chạy script tạo database schema từ file `enhanced_database_schema.sql`

### Chạy ứng dụng

1. Clone repository:

```bash
git clone <repository-url>
cd backend
```

2. Cài đặt dependencies:

```bash
mvn clean install
```

3. Chạy ứng dụng:

```bash
mvn spring-boot:run
```

Hoặc chạy từ IDE của bạn.

### Build production

```bash
mvn clean package
java -jar target/dia5-medical-api-1.0.0.jar
```

## API Documentation

Sau khi chạy ứng dụng, truy cập Swagger UI tại:

- **Swagger UI**: http://localhost:8080/swagger-ui.html
- **API Docs**: http://localhost:8080/v3/api-docs

## Endpoints chính

### Authentication

- `POST /api/auth/register` - Đăng ký tài khoản
- `POST /api/auth/login` - Đăng nhập
- `POST /api/auth/logout` - Đăng xuất
- `GET /api/auth/me` - Thông tin người dùng hiện tại

### User Management

- `GET /api/users/me` - Thông tin người dùng
- `GET /api/users/profile` - Profile đầy đủ
- `PUT /api/users/profile` - Cập nhật profile

### Medical Data

- `GET /api/provinces` - Danh sách tỉnh thành
- `GET /api/medical-specialties` - Danh sách chuyên khoa
- `POST /api/symptom-reports` - Báo cáo triệu chứng
- `GET /api/symptom-reports` - Lịch sử báo cáo triệu chứng

### AI Chatbot (RAG System)

- `POST /ask` - Chat với AI doctor (streaming response)
- `POST /ask_structured` - Chat với structured response
- `GET /medical_stats` - Thống kê medical knowledge base
- `POST /medical_search` - Tìm kiếm y tế chuyên dụng
- `GET /health` - Health check cho AI system

## Authentication

API sử dụng JWT Bearer Token authentication. Để truy cập các endpoint được bảo vệ:

1. Đăng ký hoặc đăng nhập để nhận token
2. Thêm header `Authorization: Bearer <token>` vào request

Ví dụ:

```bash
curl -H "Authorization: Bearer your_jwt_token" \
     http://localhost:8080/api/users/me
```

## Cấu trúc database

Database được thiết kế theo chuẩn y tế với các bảng chính:

- **users**: Thông tin người dùng cơ bản
- **user_demographics**: Thông tin nhân khẩu học
- **provinces**: Danh mục tỉnh thành
- **medical_specialties**: Chuyên khoa y tế
- **disease_categories**: Danh mục bệnh
- **medications**: Thuốc
- **symptoms**: Triệu chứng
- **user_symptom_reports**: Báo cáo triệu chứng
- **ai_diagnoses**: Kết quả chẩn đoán AI

## Cấu hình môi trường

### Development

```properties
# Database
spring.datasource.url=jdbc:mysql://localhost:3306/dia5_medical_ai
spring.datasource.username=root
spring.datasource.password=password

# JWT
app.jwt.secret=your_secret_key
app.jwt.expiration=86400000

# Logging
logging.level.com.nckh.dia5=DEBUG
```

### Production

```properties
# Database
spring.datasource.url=${DATABASE_URL}
spring.datasource.username=${DB_USERNAME}
spring.datasource.password=${DB_PASSWORD}

# JWT
app.jwt.secret=${JWT_SECRET}
app.jwt.expiration=86400000

# Logging
logging.level.com.nckh.dia5=INFO
```

## Deployment

### Docker

```dockerfile
FROM openjdk:21-jre-slim
COPY target/dia5-medical-api-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

### Docker Compose

```yaml
version: "3.8"
services:
  app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=jdbc:mysql://db:3306/dia5_medical_ai
      - DB_USERNAME=root
      - DB_PASSWORD=password
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=password
      - MYSQL_DATABASE=dia5_medical_ai
    ports:
      - "3306:3306"
```

## Monitoring và Health Check

- **Health Check**: http://localhost:8080/actuator/health
- **Application Info**: http://localhost:8080/actuator/info

## Bảo mật

- JWT token với thời gian hết hạn có thể cấu hình
- Password được mã hóa bằng BCrypt
- CORS được cấu hình cho phép cross-origin requests
- Input validation với Bean Validation
- SQL injection protection với JPA

## Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

MIT License

## Liên hệ

- **Team**: Dia5 Development Team
- **Email**: support@dia5.vn
- **Website**: https://dia5.vn

## API Response Format

Tất cả API response đều tuân theo format sau:

```json
{
  "success": true,
  "message": "Success message",
  "data": {
    // Response data
  },
  "statusCode": 200,
  "timestamp": "2024-01-01T10:00:00"
}
```

### Error Response

```json
{
  "success": false,
  "message": "Error message",
  "data": null,
  "statusCode": 400,
  "timestamp": "2024-01-01T10:00:00"
}
```

## Ví dụ sử dụng

### Đăng ký tài khoản

```bash
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "confirmPassword": "password123",
    "name": "Nguyen Van A"
  }'
```

### Đăng nhập

```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Báo cáo triệu chứng

```bash
curl -X POST http://localhost:8080/api/symptom-reports \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_jwt_token" \
  -d '{
    "symptomId": 1,
    "severity": 7,
    "durationHours": 24,
    "frequency": "constant",
    "locationBodyPart": "head",
    "qualityDescription": "throbbing pain"
  }'
```

## Setup RAG-based AI Chatbot

Hệ thống AI Chatbot sử dụng RAG (Retrieval-Augmented Generation) với dữ liệu từ WHO ICD-11.

### Yêu cầu

```bash
cd chatbox
pip install -r rag_requirements.txt
```

### Setup dữ liệu ICD-11

```bash
cd chatbox
python setup_icd_rag.py
```

Script này sẽ:

- Kết nối với WHO ICD-11 API
- Lấy dữ liệu bệnh lý và triệu chứng
- Tạo FAISS vector index cho tìm kiếm
- Lưu dữ liệu vào `medical_chunks_with_metadata.pkl`

### Chạy AI Chatbot

```bash
cd chatbox
python app.py
```

Truy cập: http://localhost:5000

### Test hệ thống

```bash
cd chatbox
python test_icd_rag_system.py
```

### API Examples cho AI Chatbot

#### Chat với AI Doctor

```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tôi bị đau đầu và buồn nôn",
    "session_id": "user123"
  }'
```

#### Tìm kiếm y tế

```bash
curl -X POST http://localhost:5000/medical_search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "sốt cao",
    "search_type": "symptoms",
    "top_k": 5
  }'
```

#### Thống kê knowledge base

```bash
curl -X GET http://localhost:5000/medical_stats
```

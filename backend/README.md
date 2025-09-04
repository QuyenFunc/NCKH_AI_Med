# Dia5 Medical AI Backend API

## 🏗️ Architecture Overview

This is a Spring Boot REST API backend for the Dia5 Medical AI application. The project follows a clean architecture pattern with clear separation of concerns.

### 📁 Project Structure

```
com.nckh.dia5/
├── config/           # Configuration classes
│   ├── JwtConfig.java
│   └── WebConfig.java
├── controller/       # REST Controllers  
│   ├── AuthController.java
│   └── UserController.java
├── dto/             # Data Transfer Objects
│   ├── auth/
│   │   ├── LoginRequest.java
│   │   ├── RegisterRequest.java
│   │   └── AuthResponse.java
│   └── user/
│       └── UserDTO.java
├── handler/         # Exception Handlers
│   ├── GlobalExceptionHandler.java
│   └── ApiResponse.java
├── model/           # JPA Entities
│   ├── BaseEntity.java
│   ├── User.java
│   ├── UserDemographics.java
│   └── Province.java
├── repository/      # Data Access Layer
│   ├── UserRepository.java
│   ├── UserDemographicsRepository.java
│   └── ProvinceRepository.java
├── security/        # Security Configuration
│   ├── JwtUtils.java
│   ├── JwtAuthenticationFilter.java
│   ├── JwtAuthenticationEntryPoint.java
│   └── SecurityConfig.java
└── service/         # Business Logic Layer
    ├── AuthService.java
    └── UserService.java
```

## 🚀 Quick Start

### Prerequisites
- Java 21
- Maven 3.6+
- MySQL 8.0+

### Setup Database
1. Create MySQL database:
```sql
CREATE DATABASE dia5_medical_ai;
```

2. Update `application.properties`:
```properties
spring.datasource.url=jdbc:mysql://localhost:3306/dia5_medical_ai
spring.datasource.username=your_username
spring.datasource.password=your_password
```

### Run Application
```bash
# Navigate to backend directory
cd backend

# Install dependencies
mvn clean install

# Run application
mvn spring-boot:run
```

The API will be available at: `http://localhost:8080/api`

## 📚 API Documentation

### Swagger UI
Once the application is running, visit:
- Swagger UI: `http://localhost:8080/api/swagger-ui.html`
- API Docs: `http://localhost:8080/api/api-docs`

### Authentication Endpoints

#### POST /auth/login
Login with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "type": "Bearer",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "email": "user@example.com",
    "name": "John Doe",
    "isProfileComplete": false,
    "isActive": true,
    "createdAt": "2024-01-01T10:00:00"
  }
}
```

#### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "newuser@example.com",
  "password": "password123",
  "name": "Jane Smith"
}
```

### User Endpoints

#### GET /users/me
Get current authenticated user profile.

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

#### GET /users/{userId}
Get user by ID.

## 🔒 Security

### JWT Authentication
- JWT tokens are used for authentication
- Tokens expire in 24 hours (configurable)
- Refresh token mechanism can be implemented

### Password Security
- Passwords are hashed using BCrypt
- Minimum 6 characters required

### CORS Configuration
- Configured to allow requests from Flutter mobile app
- Supports all HTTP methods and headers

## 🗄️ Database Schema

The application uses JPA/Hibernate with MySQL. Key entities:

### User
- Primary user account information
- Implements UserDetails for Spring Security

### UserDemographics  
- User demographic information (age, gender, location)
- One-to-one relationship with User

### Province
- Vietnamese provinces with regional data
- Referenced by UserDemographics

## 🔧 Configuration

### Application Properties
Key configuration properties:

```properties
# Database
spring.datasource.url=jdbc:mysql://localhost:3306/dia5_medical_ai
spring.datasource.username=root
spring.datasource.password=your_password

# JWT
app.jwt.secret=mySecretKey
app.jwt.expiration=86400000

# Server
server.port=8080
server.servlet.context-path=/api
```

### Environment Profiles
- `application.properties` - Default configuration
- `application-dev.properties` - Development profile
- `application-prod.properties` - Production profile

## 🧪 Testing

### Run Tests
```bash
mvn test
```

### Test Structure
- Unit tests for services
- Integration tests for controllers
- Security tests for authentication

## 📦 Dependencies

### Core Dependencies
- **Spring Boot 3.5.5** - Framework
- **Spring Security** - Authentication & Authorization  
- **Spring Data JPA** - Data persistence
- **MySQL Connector** - Database driver

### Additional Dependencies
- **JWT (jjwt)** - JSON Web Token implementation
- **Lombok** - Reduce boilerplate code
- **MapStruct** - DTO mapping
- **SpringDoc OpenAPI** - API documentation
- **Validation** - Request validation

## 🚀 Deployment

### Docker Setup
```dockerfile
FROM openjdk:21-jre-slim
COPY target/dia5-medical-api-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

### Build for Production
```bash
mvn clean package -Pprod
```

## 🔮 Future Enhancements

### Planned Features
1. **Medical History Management**
   - Chronic diseases tracking
   - Medication management
   - Allergy information

2. **AI Integration**
   - Symptom analysis endpoints
   - Diagnosis result storage
   - ML model integration

3. **News Management**
   - RSS feed integration
   - Article categorization
   - User bookmarks

4. **Chat System**
   - Chat session management
   - Message history
   - AI response tracking

### Technical Improvements
- Redis caching
- Rate limiting
- API versioning
- Monitoring & metrics
- Log aggregation

## 📞 Support

For technical support or questions:
- Email: support@dia5.com
- Documentation: [API Docs](http://localhost:8080/api/swagger-ui.html)
- Issues: Create an issue in the project repository

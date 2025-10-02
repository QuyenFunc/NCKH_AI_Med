# 🚀 Deployment Guide - Drug Traceability System

## **Hệ thống Truy xuất nguồn gốc thuốc với Blockchain**

> **Version**: 1.0.0  
> **Date**: December 2024  
> **Status**: ✅ Production Ready

---

## 📊 **Tổng quan hệ thống**

### **Kiến trúc tổng thể**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   NSX Portal    │    │   NPP Portal    │    │ Hiệu thuốc Portal│
│   (Port 3001)   │    │   (Port 3002)   │    │   (Port 3003)   │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼──────────────┐
                    │     Backend API Server     │
                    │      (Port 8080)           │
                    └─────────────┬──────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │   Blockchain Network       │
                    │    (Port 8545)             │
                    └────────────────────────────┘
                                  │
                    ┌─────────────▼──────────────┐
                    │     Flutter App            │
                    │   (QR Scanner)             │
                    └────────────────────────────┘
```

### **Luồng hoạt động đã tối ưu**
1. **NSX**: Tạo NFT → Gửi hàng → Transfer ownership
2. **NPP**: Verify ownership → Nhận hàng → Gửi tiếp → Transfer ownership  
3. **Hiệu thuốc**: Verify ownership → Nhận hàng → Cập nhật inventory
4. **Người dùng**: Quét QR → Verify toàn bộ chuỗi cung ứng

---

## 🔧 **Prerequisites**

### **System Requirements**
- **OS**: Ubuntu 20.04+ / Windows 10+ / macOS 12+
- **RAM**: Minimum 8GB (Recommended 16GB)
- **Storage**: 50GB free space
- **Network**: Stable internet connection

### **Software Dependencies**
```bash
# Node.js & npm
Node.js >= 18.0.0
npm >= 9.0.0

# Java & Maven
Java JDK 21
Maven 3.9+

# Database
MySQL 8.0+

# Blockchain
Hardhat (npm package)

# Flutter (for mobile app)
Flutter SDK >= 3.16.0
Dart >= 3.2.0
```

---

## 📦 **Installation Steps**

### **1. Clone Repository**
```bash
git clone <repository-url>
cd NCKH_AI_Med
```

### **2. Database Setup**
```sql
-- Create database
CREATE DATABASE dia5_medical_ai;

-- Create user (optional)
CREATE USER 'dia5_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON dia5_medical_ai.* TO 'dia5_user'@'localhost';
FLUSH PRIVILEGES;
```

### **3. Backend Configuration**
```bash
cd backend

# Update application.properties
vim src/main/resources/application.properties
```

```properties
# Database Configuration
spring.datasource.url=jdbc:mysql://localhost:3306/dia5_medical_ai
spring.datasource.username=dia5_user
spring.datasource.password=secure_password

# Blockchain Configuration
blockchain.network.url=http://localhost:8545
blockchain.contract.address=0x5FbDB2315678afecb367f032d93F642f64180aa3
blockchain.private.key=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# JWT Configuration
jwt.secret=your-256-bit-secret-key-here
jwt.expiration=86400000
```

### **4. Blockchain Setup**
```bash
cd contracts

# Install dependencies
npm install

# Start local blockchain (Terminal 1)
npx hardhat node

# Deploy smart contract (Terminal 2)
npx hardhat run scripts/deploy.js --network localhost
```

**⚠️ Important**: Copy the deployed contract address to backend configuration

### **5. Backend Startup**
```bash
cd backend

# Install dependencies & build
mvn clean install

# Run application
mvn spring-boot:run
```

**✅ Verify**: Check `http://localhost:8080/api/blockchain/status`

### **6. Frontend Applications**

#### **NSX Portal (Port 3001)**
```bash
cd web_NhaSanXuat

# Install dependencies
npm install

# Create environment file
echo "REACT_APP_API_URL=http://localhost:8080/api" > .env

# Start development server
npm start
```

#### **NPP Portal (Port 3002)**
```bash
cd web_NhaPhanPhoi

# Install dependencies  
npm install

# Create environment file
echo "REACT_APP_API_URL=http://localhost:8080/api" > .env

# Start development server  
npm start
```

#### **Hiệu thuốc Portal (Port 3003)**
```bash
cd web_HieuThuoc

# Install dependencies
npm install  

# Create environment file
echo "REACT_APP_API_URL=http://localhost:8080/api" > .env

# Start development server
npm start
```

### **7. Flutter Mobile App**
```bash
# Get dependencies
flutter pub get

# Run on emulator/device
flutter run

# Build APK (optional)
flutter build apk --release
```

---

## 🔐 **Security Configuration**

### **Wallet Addresses (Development)**
```javascript
// Default addresses from Hardhat
const MANUFACTURER_ADDRESS = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266";
const DISTRIBUTOR_ADDRESS = "0x742d35Cc6634C0532925a3b8D867B3E68b7Fbb22";  
const PHARMACY_ADDRESS = "0x90F79bf6EB2c4f870365E785982E1f101E93b906";
```

### **Production Security**
```bash
# Generate secure private keys
openssl rand -hex 32

# Use environment variables
export BLOCKCHAIN_PRIVATE_KEY=your_secure_private_key
export JWT_SECRET=your_256_bit_jwt_secret
export DB_PASSWORD=your_secure_db_password
```

---

## 🚀 **Production Deployment**

### **Docker Deployment (Recommended)**

#### **1. Backend + Database**
```dockerfile
# backend/Dockerfile
FROM openjdk:21-jdk-slim
COPY target/dia5-medical-api-1.0.0.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "/app.jar"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: dia5_medical_ai
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  backend:
    build: ./backend
    ports:
      - "8080:8080"
    depends_on:
      - mysql
    environment:
      - SPRING_DATASOURCE_URL=jdbc:mysql://mysql:3306/dia5_medical_ai
      - SPRING_DATASOURCE_USERNAME=root
      - SPRING_DATASOURCE_PASSWORD=rootpassword

  blockchain:
    image: node:18
    working_dir: /app
    volumes:
      - ./contracts:/app
    ports:
      - "8545:8545"
    command: npx hardhat node

volumes:
  mysql_data:
```

#### **2. Frontend Applications**
```dockerfile
# web_NhaSanXuat/Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

#### **3. Deploy với Docker Compose**
```bash
# Build và chạy tất cả services
docker-compose up -d

# Deploy smart contract
docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost

# Check logs
docker-compose logs -f backend
```

### **Cloud Deployment (AWS/GCP/Azure)**

#### **1. Infrastructure Setup**
```bash
# Example: AWS EC2 + RDS
# Instance: t3.large (2 vCPU, 8GB RAM)
# Database: RDS MySQL 8.0
# Load Balancer: Application Load Balancer
# Storage: EBS gp3 100GB
```

#### **2. Environment Configuration**
```bash
# Production environment variables
export NODE_ENV=production
export REACT_APP_API_URL=https://api.yourdomain.com
export SPRING_PROFILES_ACTIVE=prod
export BLOCKCHAIN_NETWORK_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
```

#### **3. SSL/TLS Setup**
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location /api {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 📊 **Monitoring & Maintenance**

### **Health Checks**
```bash
# Backend API health
curl http://localhost:8080/api/blockchain/status

# Blockchain connectivity  
curl http://localhost:8080/api/blockchain/debug/blockchain-info

# Database connection
curl http://localhost:8080/actuator/health
```

### **Log Monitoring**
```bash
# Backend logs
tail -f backend/logs/application.log

# Blockchain logs
tail -f contracts/hardhat.log

# Frontend access logs (nginx)
tail -f /var/log/nginx/access.log
```

### **Performance Metrics**
- **Response time**: < 2s for API calls
- **Blockchain tx**: < 30s confirmation time
- **Database**: < 100ms query time
- **Frontend**: < 3s page load time

---

## 🔍 **Testing & Validation**

### **End-to-End Test Scenario**
1. **NSX**: Tạo lô thuốc `BT2024123456` với 1000 viên
2. **NSX**: Tạo shipment gửi 500 viên cho NPP
3. **NPP**: Nhận hàng và verify blockchain ownership  
4. **NPP**: Tạo shipment gửi 200 viên cho Hiệu thuốc
5. **Hiệu thuốc**: Nhận hàng và cập nhật inventory
6. **Flutter**: Quét QR code và hiển thị full supply chain

### **API Testing**
```bash
# Test batch creation
curl -X POST http://localhost:8080/api/blockchain/drugs/batches \
  -H "Content-Type: application/json" \
  -d '{"drugName":"Test Drug","manufacturer":"Test Manufacturer","batchNumber":"TEST001","quantity":100,"expiryDate":"2025-12-31T00:00:00","storageConditions":"Room temperature"}'

# Test drug verification
curl -X POST http://localhost:8080/api/blockchain/drugs/verify \
  -H "Content-Type: application/json" \  
  -d '{"qrCode":"QR_TEST001_123456"}'
```

---

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Backend không kết nối được Database**
```bash
# Check MySQL service
sudo systemctl status mysql

# Verify database exists
mysql -u root -p -e "SHOW DATABASES;"

# Check application.properties
grep -n "datasource" backend/src/main/resources/application.properties
```

#### **Blockchain transactions fail**
```bash
# Check Hardhat node is running
curl http://localhost:8545

# Verify contract deployment
grep -n "contract.address" backend/src/main/resources/application.properties

# Check account balance
npx hardhat console --network localhost
```

#### **Frontend API calls fail**
```bash
# Check CORS configuration
grep -n "cors" backend/src/main/java/com/nckh/dia5/config/

# Verify environment variables
cat web_NhaSanXuat/.env

# Check network connectivity
curl http://localhost:8080/api/blockchain/status
```

### **Error Codes**
- **500**: Server error → Check backend logs
- **404**: API not found → Verify endpoint mapping
- **401**: Unauthorized → Check JWT token
- **400**: Bad request → Validate request payload

---

## 📋 **Maintenance Tasks**

### **Daily**
- [ ] Check system health endpoints
- [ ] Monitor error logs
- [ ] Verify blockchain connectivity

### **Weekly**  
- [ ] Database backup
- [ ] Log rotation
- [ ] Performance metrics review

### **Monthly**
- [ ] Security updates
- [ ] Dependency updates  
- [ ] Blockchain network sync

---

## 📞 **Support & Contact**

- **Technical Lead**: NCKH AI Medical Team
- **Documentation**: This guide + API_FLOW_SUMMARY.md
- **Emergency**: Check logs first, then contact team

---

## ✅ **Deployment Checklist**

- [ ] Database created and configured
- [ ] Blockchain network running
- [ ] Smart contract deployed
- [ ] Backend API responding to health checks
- [ ] All frontend applications loading
- [ ] Flutter app can scan QR codes
- [ ] End-to-end test scenario passes
- [ ] Production environment variables set
- [ ] SSL certificates configured (if production)
- [ ] Monitoring and alerts configured

**🎉 System ready for production use!**

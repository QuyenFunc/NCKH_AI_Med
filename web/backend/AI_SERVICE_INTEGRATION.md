# Hướng dẫn tích hợp AI Service với Backend Spring Boot

## 📋 Tổng quan

Hệ thống đã được thiết kế để tích hợp với AI service Flask của bạn thông qua RESTful API. Backend Spring Boot sẽ gọi AI service để thực hiện chẩn đoán dựa trên triệu chứng người dùng đã báo cáo.

## 🏗️ Kiến trúc hệ thống

```
Frontend (React) → Backend (Spring Boot) → AI Service (Flask + RAG)
                        ↓
                   Database (MySQL)
```

### Lợi ích của kiến trúc này:

- ✅ **Bảo mật**: API keys không lộ ra frontend
- ✅ **Kiểm soát**: Validate và transform data trước khi gửi AI
- ✅ **Lưu trữ**: Lịch sử chẩn đoán được lưu vào database
- ✅ **Monitoring**: Centralized logging và error handling
- ✅ **Caching**: Có thể cache kết quả để tối ưu performance

## ⚙️ Cấu hình

### 1. Cấu hình trong `application.properties`

```properties
# AI Diagnosis Service Configuration
ai.diagnosis.service.url=http://localhost:5000
ai.diagnosis.service.api-key=your-secret-api-key
ai.diagnosis.service.timeout.connect=30
ai.diagnosis.service.timeout.read=60
```

### 2. Cấu hình AI Service Flask

AI service Flask của bạn cần có endpoint sau:

**POST** `/diagnosis`

**Request format:**

```json
{
  "sessionId": "session-123",
  "userId": "user-456",
  "userProfile": {
    "age": 30,
    "gender": "MALE",
    "heightCm": 175,
    "weightKg": 70.5,
    "province": "Hà Nội",
    "medicalHistory": [],
    "allergies": [],
    "currentMedications": []
  },
  "symptoms": [
    {
      "name": "Đau đầu",
      "severity": 7,
      "durationHours": 24,
      "frequency": "DAILY",
      "location": "head",
      "description": "Đau nhức âm ỉ",
      "triggers": ["stress", "lack_of_sleep"]
    }
  ],
  "additionalContext": "Chẩn đoán y tế thông qua ứng dụng Dia5"
}
```

**Response format:**

```json
{
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
  "disclaimerMessage": "Kết quả chỉ mang tính chất tham khảo"
}
```

## 🔐 Bảo mật

### Headers yêu cầu cho AI service:

```
Content-Type: application/json
X-API-Key: your-secret-api-key
User-Agent: Dia5-Medical-App/1.0
```

### Trong Flask service:

```python
from flask import Flask, request, jsonify

@app.route('/diagnosis', methods=['POST'])
def diagnose():
    # Verify API key
    api_key = request.headers.get('X-API-Key')
    if api_key != 'your-secret-api-key':
        return jsonify({'error': 'Invalid API key'}), 401

    # Process diagnosis
    data = request.json
    # ... your RAG logic here ...

    return jsonify(diagnosis_result)
```

## 🚀 Sử dụng API

### 1. Báo cáo triệu chứng trước

```bash
POST /api/symptom-reports
{
  "sessionId": "session-123",
  "symptomId": 1,
  "severity": 7,
  "durationHours": 24,
  "frequency": "DAILY"
}
```

### 2. Gọi AI chẩn đoán

```bash
POST /api/ai-diagnosis/diagnose/session-123
Authorization: Bearer <token>
```

### 3. Lấy lịch sử chẩn đoán

```bash
GET /api/ai-diagnosis/history
Authorization: Bearer <token>
```

## 🔧 Troubleshooting

### Lỗi thường gặp:

1. **Connection timeout**

   - Kiểm tra AI service có đang chạy không
   - Kiểm tra URL và port trong config

2. **Authentication failed**

   - Kiểm tra API key trong config
   - Kiểm tra header X-API-Key

3. **No symptoms found**
   - Đảm bảo đã báo cáo triệu chứng trước khi gọi AI

### Logging:

```properties
# Bật debug logging cho AI service
logging.level.com.nckh.dia5.service.AiDiagnosisService=DEBUG
```

## 📊 Monitoring

### Metrics có thể theo dõi:

- Response time của AI service
- Success/failure rate
- Confidence score average
- Urgency level distribution

### Health check:

```bash
GET /actuator/health
```

## 🔄 Flow hoàn chỉnh

1. **User báo cáo triệu chứng** → `POST /api/symptom-reports`
2. **User yêu cầu chẩn đoán** → `POST /api/ai-diagnosis/diagnose/{sessionId}`
3. **Backend validate** user và symptoms
4. **Backend gọi AI service** với structured data
5. **AI service trả về** diagnosis results
6. **Backend lưu kết quả** vào database
7. **Backend trả response** cho frontend
8. **Frontend hiển thị** kết quả cho user

## 💡 Best Practices

1. **Always validate** user input trước khi gọi AI
2. **Handle errors gracefully** - AI service có thể fail
3. **Cache results** nếu cần thiết
4. **Log all requests** cho debugging
5. **Set proper timeouts** để tránh hang
6. **Use circuit breaker** pattern nếu AI service không ổn định
7. **Implement retry logic** với exponential backoff

## 🚦 Environment Setup

### Development:

```properties
ai.diagnosis.service.url=http://localhost:5000
ai.diagnosis.service.api-key=dev-api-key
```

### Production:

```properties
ai.diagnosis.service.url=https://your-ai-service.com
ai.diagnosis.service.api-key=${AI_SERVICE_API_KEY}
```

Sử dụng environment variables cho production để bảo mật API keys.

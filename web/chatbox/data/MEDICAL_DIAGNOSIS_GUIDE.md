# Medical Diagnosis Chatbot - Hướng Dẫn Sử Dụng

## 🏥 Tổng Quan

Hệ thống Medical-Only Diagnosis Chatbot sử dụng dữ liệu từ WHO ICD-11 API để hỗ trợ chẩn đoán và tư vấn y tế.

**🔄 THAY ĐỔI MỚI: Đã loại bỏ hoàn toàn phần e-commerce, chỉ tập trung vào y tế**

Chatbot có khả năng:

- Phân tích triệu chứng và đưa ra gợi ý chẩn đoán
- Cung cấp thông tin về các bệnh lý
- Tư vấn về điều trị và phòng ngừa
- Nhận diện tình huống khẩn cấp
- Hỗ trợ tìm kiếm thông tin y tế dựa trên ICD-11
- **Tất cả query đều được xử lý như medical query**

## 📋 Yêu Cầu Hệ Thống

### Dependencies

```bash
pip install -r rag_requirements.txt
```

### Thư viện chính:

- `sentence-transformers`: Tạo embeddings
- `faiss-cpu`: Vector search
- `requests`: API calls
- `flask`: Web framework
- `langchain`: Text processing

## 🚀 Hướng Dẫn Cài Đặt

### Bước 1: Setup Dữ Liệu Y Tế

```bash
cd chatbox
python setup_icd_rag.py
```

Script này sẽ:

- Kết nối với WHO ICD API
- Tải dữ liệu các bệnh lý và triệu chứng từ ICD-11
- Tạo FAISS index cho việc tìm kiếm
- Lưu dữ liệu vào `medical_chunks_with_metadata.pkl` và `medical_faiss_index.index`

### Bước 2: Chạy Test Hệ Thống

Cho Medical-Only system:

```bash
python test_medical_only.py
```

Hoặc test comprehensive (bao gồm cả setup data):

```bash
python test_medical_system.py
```

### Bước 3: Khởi Động Chatbot

```bash
python app.py
```

Truy cập: http://localhost:5000

## 🔧 Cấu Hình WHO ICD API

### Thông tin xác thực (đã cấu hình sẵn):

```python
CLIENT_ID = "4876fbe9-043e-417d-bbf6-e1e67ee1d749_1491c0e8-e6fe-4da6-be8c-8635d935a285"
CLIENT_SECRET = "w6ilxOd6Ik/CXNdIjK0NmsNzc1krj6Ci/606KCWB2eM="
```

### Cách lấy credentials mới (nếu cần):

1. Truy cập: https://icd.who.int/icdapi
2. Đăng ký tài khoản
3. Tạo application mới
4. Lấy Client ID và Client Secret
5. Cập nhật trong file `setup_icd_faiss.py`

## 💬 Sử Dụng Chatbot

### Loại câu hỏi được hỗ trợ:

#### 1. Triệu chứng (Symptom Inquiry)

```
- "tôi bị đau đầu và chóng mặt"
- "có triệu chứng sốt và ho"
- "bị đau bụng và buồn nôn"
```

#### 2. Bệnh lý (Disease Inquiry)

```
- "bệnh tiểu đường là gì?"
- "nguyên nhân gây cao huyết áp"
- "hội chứng Down có di truyền không?"
```

#### 3. Điều trị (Treatment Inquiry)

```
- "cách điều trị bệnh hen suyễn"
- "thuốc nào dùng cho cao huyết áp?"
- "phẫu thuật tim hở có rủi ro gì?"
```

#### 4. Phòng ngừa (Prevention Inquiry)

```
- "làm sao phòng ngừa đột quỵ?"
- "cách tránh bệnh tim mạch"
- "ăn gì để không bị tiểu đường?"
```

#### 5. Khẩn cấp (Emergency)

```
- "đau ngực dữ dội"
- "khó thở và ngất xỉu"
- "co giật liên tục"
```

### Ví dụ tương tác:

```
👤 User: "Tôi bị đau đầu mấy ngày nay, có kèm theo buồn nôn và chóng mặt"

🤖 Bot:
⚕️ PHÂN TÍCH TRIỆU CHỨNG

Các triệu chứng bạn mô tả:
- Đau đầu kéo dài
- Buồn nôn
- Chóng mặt

CÁC KHẨY NĂNG CÓ THỂ XẢY RA:
1. Đau nửa đầu (Migraine) - ICD: 8A80
2. Đau đầu do căng thẳng - ICD: 8A81
3. Hội chứng tiền đình - ICD: AB32

KHUYẾN CÁO:
- Nếu đau đầu dữ dội hoặc kèm sốt cao → Đi khám ngay
- Nếu triệu chứng nhẹ → Nghỉ ngơi, uống đủ nước
- Theo dõi thêm 1-2 ngày, nếu không cải thiện hãy gặp bác sĩ

🩺 Lưu ý: Đây chỉ là tham khảo, không thay thế chẩn đoán của bác sĩ.
```

## 🛠️ API Endpoints

### 1. Medical Statistics

```http
GET /medical_stats
```

Response:

```json
{
  "success": true,
  "total_chunks": 1250,
  "total_categories": 18,
  "chunks_with_icd_code": 980,
  "data_source": "WHO ICD API",
  "coverage_percentage": 78.4,
  "categories": {
    "0M": { "id": "0M", "name": "Triệu chứng, dấu hiệu", "count": 156 }
  }
}
```

### 2. Medical Search

```http
POST /medical_search
```

Request:

```json
{
  "query": "đau đầu",
  "search_type": "symptoms", // "symptoms", "diseases", "general"
  "top_k": 5
}
```

Response:

```json
{
  "success": true,
  "query": "đau đầu",
  "medical_intent": "symptom_inquiry",
  "total_results": 3,
  "results": [
    {
      "entity_name": "Headache",
      "icd_code": "MB40",
      "category_name": "Triệu chứng, dấu hiệu",
      "relevance_score": 0.89
    }
  ]
}
```

### 3. Chatbot (Medical-Only)

```http
POST /ask
```

Request:

```json
{
  "query": "tôi bị đau đầu",
  "session_id": "user_123"
}
```

Response: Server-Sent Events (SSE) stream

**⚠️ Lưu ý**: Tất cả query đều được xử lý như medical query

### 4. Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy",
  "service": "Medical Diagnosis Chatbot",
  "version": "1.0",
  "timestamp": "2024-01-01T00:00:00"
}
```

### 5. Session Management

```http
POST /session/new
GET /sessions
POST /session/{id}/clear
GET /session/{id}/history
```

## 📁 Cấu Trúc Files

```
chatbox/
├── setup_icd_rag.py                # Setup dữ liệu WHO ICD-11 cho RAG
├── medical_rag_utils.py             # RAG functions cho medical
├── app.py                           # Flask chatbot (Medical-Only)
├── app_ecommerce_backup.py          # Backup e-commerce version
├── test_medical_system.py           # Test suite (comprehensive)
├── test_medical_only.py             # Test suite (medical-only)
├── medical_chunks_with_metadata.pkl # Medical data
├── medical_faiss_index.index        # FAISS index
└── ...
```

## 🔍 Cách Hoạt Động

### 1. Data Pipeline

```
WHO ICD API → Data Extraction → Text Processing → Embeddings → FAISS Index
```

### 2. Query Pipeline

```
User Query → Intent Classification → Medical Search → Context Creation → LLM Response
```

### 3. Intent Classification

- **symptom_inquiry**: Hỏi về triệu chứng
- **disease_inquiry**: Hỏi về bệnh lý
- **treatment_inquiry**: Hỏi về điều trị
- **prevention_inquiry**: Hỏi về phòng ngừa
- **emergency**: Tình huống khẩn cấp
- **general_medical**: Y tế tổng quát

## ⚠️ Lưu Ý Quan Trọng

### Medical Disclaimer

- ✅ **Chỉ mang tính chất tham khảo**
- ✅ **Không thay thế chẩn đoán của bác sĩ**
- ✅ **Tình huống khẩn cấp → Gọi 115 ngay**
- ✅ **Luôn tham khảo ý kiến chuyên gia y tế**

### Giới Hạn Hệ Thống

- Dữ liệu từ WHO ICD-11 (không bao gồm điều trị cụ thể)
- Không có dữ liệu về liều lượng thuốc
- Không thay thế khám lâm sàng
- Chỉ hỗ trợ tiếng Việt và tiếng Anh

## 🔧 Troubleshooting

### Lỗi thường gặp:

#### 1. Lỗi WHO ICD API

```
Error: Authentication failed
```

**Giải pháp**: Kiểm tra CLIENT_ID và CLIENT_SECRET

#### 2. Lỗi FAISS Index

```
Error: Medical data not found
```

**Giải pháp**: Chạy lại `python setup_icd_rag.py`

#### 3. Lỗi Memory

```
Error: Out of memory
```

**Giải pháp**: Giảm `max_entities_per_category` trong setup

#### 4. Lỗi Network

```
Error: Request timeout
```

**Giải pháp**: Kiểm tra kết nối internet, tăng timeout

## 📊 Performance

### Thời gian setup (lần đầu):

- Nạp dữ liệu WHO ICD: 5-10 phút
- Tạo embeddings: 2-5 phút
- Tổng cộng: ~15 phút

### Thời gian response:

- Medical search: 50-100ms
- Chatbot response: 1-3 giây
- Intent classification: 10-20ms

### Dung lượng:

- Medical data: ~50-100MB
- FAISS index: ~20-50MB
- Models: ~500MB

## 🤝 Đóng Góp

### Cách thêm dữ liệu y tế mới:

1. Cập nhật `setup_icd_faiss.py`
2. Thêm categories mới vào `main_categories`
3. Cập nhật `get_category_name_vietnamese()`
4. Chạy lại setup

### Cách cải thiện intent classification:

1. Cập nhật `classify_medical_query_intent()` trong `medical_rag_utils.py`
2. Thêm keywords mới
3. Test với `test_medical_system.py`

## 📞 Hỗ Trợ

### Issues & Bugs:

- GitHub Issues: [Link to your repo]
- Email: your-email@domain.com

### Resources:

- WHO ICD-11: https://icd.who.int/
- WHO ICD API Docs: https://icd.who.int/docs/icd-api/
- FAISS Documentation: https://faiss.ai/

---

**🏥 Medical Diagnosis Chatbot v1.0**  
_Powered by WHO ICD-11 & OpenAI_  
_Made with ❤️ for healthcare_

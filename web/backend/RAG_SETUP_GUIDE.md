# 🧠 Hướng dẫn Setup RAG (Retrieval-Augmented Generation) cho AI Chẩn đoán Y tế

## 📋 Tổng quan

RAG system kết hợp **Retrieval** (tìm kiếm thông tin) với **Generation** (tạo câu trả lời) để cung cấp chẩn đoán y tế chính xác và có căn cứ.

### 🏗️ Kiến trúc RAG

```
User Query → [Embedding] → [Vector Search] → [Relevant Docs] → [LLM + Context] → [Response]
```

## 🚀 Bước 1: Setup Environment

### 1.1. Tạo Virtual Environment

```bash
python -m venv rag_env
source rag_env/bin/activate  # Linux/Mac
# rag_env\Scripts\activate   # Windows

pip install -r rag_requirements.txt
```

### 1.2. Download Models

```bash
# Download Vietnamese sentence transformer
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('keepitreal/vietnamese-sbert')"

# Download SpaCy models
python -m spacy download en_core_web_sm
python -m spacy download vi_core_news_sm
```

## 📊 Bước 2: Thu thập Dữ liệu

### 2.1. Chạy Data Collection

```bash
python data_collection_guide.py
```

### 2.2. Nguồn dữ liệu được khuyến nghị:

#### **🇻🇳 Dữ liệu Việt Nam:**

- **ICD-10 Việt Nam** từ Bộ Y tế
- **Hướng dẫn chẩn đoán** từ bệnh viện lớn
- **Danh mục thuốc** từ Cục Quản lý Dược

#### **🌍 Dữ liệu Quốc tế:**

- **SNOMED CT** - Thuật ngữ y tế chuẩn
- **MedlinePlus** - Thông tin y tế tin cậy
- **Mayo Clinic** - Cơ sở dữ liệu triệu chứng
- **PubMed** - Bài báo nghiên cứu y học

### 2.3. Cấu trúc dữ liệu mẫu:

```json
{
  "diseases": [
    {
      "name": "Cảm cúm",
      "icd_code": "J11",
      "symptoms": ["sốt", "ho", "đau đầu"],
      "treatment": "Nghỉ ngơi, uống thuốc hạ sốt",
      "severity": "mild",
      "duration": "7-10 ngày"
    }
  ],
  "symptoms": [
    {
      "name": "sốt",
      "description": "Nhiệt độ cơ thể tăng cao",
      "possible_diseases": ["cúm", "COVID-19", "nhiễm khuẩn"],
      "questions": ["Sốt bao nhiều độ?", "Sốt từ khi nào?"]
    }
  ]
}
```

## 🔧 Bước 3: Xử lý Dữ liệu

### 3.1. Chạy Data Processing

```bash
python rag_data_preparation.py
```

### 3.2. Kết quả sau xử lý:

- `medical_knowledge_base/documents.json` - Documents đã xử lý
- `medical_knowledge_base/embeddings.npy` - Vector embeddings
- `medical_knowledge_base/faiss_index.bin` - Search index

## 🔍 Bước 4: Setup RAG System

### 4.1. Tạo RAG Flask API

```python
# rag_api.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_data_preparation import MedicalRAGDataProcessor
import openai  # hoặc dùng local LLM như llama-cpp-python

app = Flask(__name__)
CORS(app)

# Load RAG system
processor = MedicalRAGDataProcessor()
processor.load_knowledge_base("medical_knowledge_base")

# Setup LLM (có thể dùng OpenAI, Anthropic, hoặc local model)
openai.api_key = "your-api-key"

@app.route('/diagnosis', methods=['POST'])
def diagnose():
    try:
        data = request.json

        # Extract user info và symptoms
        user_profile = data.get('userProfile', {})
        symptoms = data.get('symptoms', [])

        # Tạo query từ symptoms
        symptom_text = ", ".join([s.get('name', '') for s in symptoms])
        query = f"Triệu chứng: {symptom_text}. Tuổi: {user_profile.get('age', 'N/A')}. Giới tính: {user_profile.get('gender', 'N/A')}"

        # Retrieve relevant documents
        relevant_docs = processor.search_similar_documents(query, top_k=5)

        # Prepare context for LLM
        context = "\n\n".join([doc.content for doc, score in relevant_docs])

        # Generate diagnosis using LLM
        diagnosis_response = generate_diagnosis(query, context, user_profile, symptoms)

        return jsonify(diagnosis_response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def generate_diagnosis(query, context, user_profile, symptoms):
    """Generate diagnosis using LLM với retrieved context"""

    prompt = f"""
    Bạn là một AI y tế hỗ trợ chẩn đoán. Dựa trên thông tin sau, hãy đưa ra chẩn đoán có thể và khuyến nghị:

    THÔNG TIN BỆNH NHÂN:
    {query}

    THÔNG TIN Y TẾ THAM KHẢO:
    {context}

    Hãy trả lời theo format JSON:
    {{
        "results": [
            {{
                "diseaseName": "Tên bệnh",
                "probability": 0.8,
                "description": "Mô tả bệnh",
                "severity": "MILD/MODERATE/SEVERE",
                "matchedSymptoms": ["triệu chứng khớp"],
                "recommendedSpecialty": "Chuyên khoa khuyến nghị"
            }}
        ],
        "recommendations": ["Khuyến nghị 1", "Khuyến nghị 2"],
        "urgencyLevel": "LOW/MEDIUM/HIGH/CRITICAL",
        "disclaimerMessage": "Kết quả chỉ mang tính chất tham khảo"
    }}
    """

    # Gọi LLM (OpenAI GPT, Claude, hoặc local model)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    # Parse response
    import json
    try:
        result = json.loads(response.choices[0].message.content)
        return result
    except:
        # Fallback response
        return {
            "results": [{"diseaseName": "Cần thêm thông tin", "probability": 0.5}],
            "recommendations": ["Nên tham khảo ý kiến bác sĩ"],
            "urgencyLevel": "MEDIUM"
        }

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### 4.2. Alternative: Sử dụng Local LLM

```python
# Sử dụng llama-cpp-python cho local LLM
from llama_cpp import Llama

# Load local model (ví dụ: Code Llama, Mistral, Zephyr)
llm = Llama(model_path="path/to/model.gguf", n_ctx=4096)

def generate_with_local_llm(prompt):
    output = llm(prompt, max_tokens=1000, temperature=0.3)
    return output['choices'][0]['text']
```

## 🎯 Bước 5: Testing & Validation

### 5.1. Test RAG System

```python
# test_rag.py
from rag_data_preparation import MedicalRAGDataProcessor

processor = MedicalRAGDataProcessor()
processor.load_knowledge_base("medical_knowledge_base")

# Test queries
test_queries = [
    "đau đầu và sốt",
    "ho khan kéo dài",
    "đau bụng và buồn nôn",
    "mệt mỏi và khó thở"
]

for query in test_queries:
    print(f"\nQuery: {query}")
    results = processor.search_similar_documents(query, top_k=3)
    for doc, score in results:
        print(f"  Score: {score:.3f} - {doc.title}")
```

### 5.2. Evaluate RAG Performance

```python
# Metrics để đánh giá:
# - Precision@K: Độ chính xác của top-K results
# - Recall@K: Tỷ lệ relevant docs được retrieve
# - MRR (Mean Reciprocal Rank): Vị trí của relevant doc đầu tiên
```

## 🔧 Bước 6: Integration với Backend

### 6.1. Start Flask RAG API

```bash
python rag_api.py
# API sẽ chạy tại http://localhost:5000
```

### 6.2. Test Integration

```bash
curl -X POST http://localhost:5000/diagnosis \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session",
    "userProfile": {"age": 30, "gender": "MALE"},
    "symptoms": [{"name": "đau đầu", "severity": 7}]
  }'
```

### 6.3. Backend Spring Boot sẽ gọi API này

- URL: `http://localhost:5000/diagnosis`
- API Key authentication
- Structured request/response format

## 📈 Bước 7: Optimization & Scaling

### 7.1. Performance Optimization

```python
# Caching với Redis
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

def cached_search(query):
    cache_key = f"search:{hash(query)}"
    cached_result = r.get(cache_key)
    if cached_result:
        return json.loads(cached_result)

    result = processor.search_similar_documents(query)
    r.setex(cache_key, 3600, json.dumps(result))  # Cache 1 hour
    return result
```

### 7.2. Model Updates

```python
# Định kỳ update knowledge base
def update_knowledge_base():
    # Re-crawl data
    # Re-process documents
    # Rebuild FAISS index
    # Hot-swap in production
    pass
```

### 7.3. Monitoring

```python
# Log tất cả queries và responses
import logging
import wandb  # Weights & Biases for ML monitoring

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/diagnosis', methods=['POST'])
def diagnose():
    start_time = time.time()

    # ... processing ...

    # Log metrics
    response_time = time.time() - start_time
    logger.info(f"Query processed in {response_time:.2f}s")

    # Track with W&B
    wandb.log({
        "response_time": response_time,
        "query_length": len(query),
        "num_symptoms": len(symptoms)
    })
```

## 🚀 Production Deployment

### Docker Setup

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY rag_requirements.txt .
RUN pip install -r rag_requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "rag_api.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: "3.8"
services:
  rag-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./medical_knowledge_base:/app/medical_knowledge_base

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## 📊 Data Quality & Legal Considerations

### ⚠️ Lưu ý quan trọng:

1. **Bản quyền & Pháp lý**

   - Tuân thủ robots.txt khi scraping
   - Xin phép sử dụng dữ liệu y tế
   - Tuân thủ GDPR, HIPAA

2. **Chất lượng dữ liệu**

   - Validate từ nhiều nguồn
   - Kiểm tra bởi chuyên gia y tế
   - Cập nhật định kỳ

3. **Disclaimer**
   - Luôn cảnh báo: "Chỉ mang tính chất tham khảo"
   - Khuyến khích gặp bác sĩ
   - Không thay thế chẩn đoán y tế

## 🎓 Tài nguyên học thêm

- [LangChain Documentation](https://python.langchain.com/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [Sentence Transformers](https://www.sbert.net/)
- [Medical NLP with spaCy](https://spacy.io/universe/project/medspacy)

## 🔧 Next Steps

1. ✅ **Implement RAG system** như hướng dẫn trên
2. ✅ **Test với dữ liệu thật**
3. ✅ **Fine-tune embedding model** với medical domain
4. ✅ **Setup monitoring & logging**
5. ✅ **Deploy to production**

Chúc bạn thành công với RAG system! 🚀🏥


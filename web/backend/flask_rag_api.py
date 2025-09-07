#!/usr/bin/env python3
"""
Flask API for Medical RAG (Retrieval-Augmented Generation) System
Dia5 Medical AI Diagnosis Service
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any
import os
from dataclasses import asdict

# Import RAG components
from rag_data_preparation import MedicalRAGDataProcessor

# For LLM - you can choose one of these:
# Option 1: OpenAI (requires API key)
# import openai

# Option 2: Local LLM (requires model file)
# from llama_cpp import Llama

# Option 3: Hugging Face Transformers
# from transformers import pipeline

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MedicalRAGAPI:
    """Medical RAG API Class"""
    
    def __init__(self):
        self.processor = None
        self.llm = None
        self.api_key = os.getenv('RAG_API_KEY', 'your-secret-api-key')
        self.setup_rag_system()
        self.setup_llm()
    
    def setup_rag_system(self):
        """Initialize RAG system"""
        try:
            logger.info("Loading RAG system...")
            self.processor = MedicalRAGDataProcessor()
            
            # Load knowledge base if exists
            kb_path = "medical_knowledge_base"
            if os.path.exists(f"{kb_path}/documents.json"):
                self.processor.load_knowledge_base(kb_path)
                logger.info(f"Loaded knowledge base with {len(self.processor.documents)} documents")
            else:
                logger.warning(f"Knowledge base not found at {kb_path}")
                logger.info("Please run rag_data_preparation.py first to build the knowledge base")
                
        except Exception as e:
            logger.error(f"Failed to load RAG system: {e}")
            self.processor = None
    
    def setup_llm(self):
        """Setup Language Model"""
        try:
            # Option 1: OpenAI GPT
            # openai.api_key = os.getenv('OPENAI_API_KEY')
            # self.llm_type = 'openai'
            
            # Option 2: Local LLM (example with llama-cpp-python)
            # model_path = "path/to/your/model.gguf"
            # if os.path.exists(model_path):
            #     self.llm = Llama(model_path=model_path, n_ctx=4096)
            #     self.llm_type = 'local'
            
            # Option 3: Simple rule-based fallback (for testing)
            self.llm_type = 'rule_based'
            logger.info(f"LLM setup completed: {self.llm_type}")
            
        except Exception as e:
            logger.error(f"Failed to setup LLM: {e}")
            self.llm_type = 'rule_based'
    
    def authenticate(self, api_key: str) -> bool:
        """Simple API key authentication"""
        return api_key == self.api_key
    
    def search_relevant_documents(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for relevant medical documents"""
        if not self.processor:
            return []
        
        try:
            results = self.processor.search_similar_documents(query, top_k)
            return [
                {
                    "id": doc.id,
                    "title": doc.title,
                    "content": doc.content,
                    "category": doc.category,
                    "score": float(score),
                    "metadata": doc.metadata
                }
                for doc, score in results
            ]
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def generate_diagnosis_openai(self, query: str, context: str, user_profile: Dict, symptoms: List[Dict]) -> Dict:
        """Generate diagnosis using OpenAI GPT"""
        import openai
        
        prompt = f"""
        Bạn là một AI y tế hỗ trợ chẩn đoán. Dựa trên thông tin sau, hãy đưa ra chẩn đoán có thể và khuyến nghị:

        THÔNG TIN BỆNH NHÂN:
        - Tuổi: {user_profile.get('age', 'N/A')}
        - Giới tính: {user_profile.get('gender', 'N/A')}
        - Cân nặng: {user_profile.get('weightKg', 'N/A')} kg
        - Chiều cao: {user_profile.get('heightCm', 'N/A')} cm
        - Tỉnh thành: {user_profile.get('province', 'N/A')}

        TRIỆU CHỨNG:
        {json.dumps(symptoms, ensure_ascii=False, indent=2)}

        THÔNG TIN Y TẾ THAM KHẢO:
        {context}

        Hãy phân tích và trả lời theo format JSON sau:
        {{
            "results": [
                {{
                    "diseaseName": "Tên bệnh có thể",
                    "diseaseCode": "Mã ICD nếu có",
                    "probability": 0.85,
                    "description": "Mô tả ngắn gọn về bệnh",
                    "severity": "MILD",
                    "matchedSymptoms": ["triệu chứng khớp với bệnh"],
                    "additionalQuestions": ["Câu hỏi thêm để xác định"],
                    "recommendedSpecialty": "Chuyên khoa nên khám",
                    "requiresImmediateAttention": false
                }}
            ],
            "recommendations": [
                "Nghỉ ngơi đầy đủ",
                "Uống nhiều nước",
                "Theo dõi triệu chứng"
            ],
            "urgencyLevel": "LOW",
            "confidenceScore": 0.82,
            "disclaimerMessage": "Kết quả chỉ mang tính chất tham khảo, vui lòng tham khảo ý kiến bác sĩ chuyên khoa để có chẩn đoán chính xác."
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content
            return json.loads(result_text)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self.generate_fallback_diagnosis(symptoms)
    
    def generate_diagnosis_local(self, query: str, context: str, user_profile: Dict, symptoms: List[Dict]) -> Dict:
        """Generate diagnosis using local LLM"""
        # Similar to OpenAI but using local model
        # Implementation depends on your chosen local LLM
        return self.generate_fallback_diagnosis(symptoms)
    
    def generate_fallback_diagnosis(self, symptoms: List[Dict]) -> Dict:
        """Rule-based fallback diagnosis for testing"""
        symptom_names = [s.get('name', '').lower() for s in symptoms]
        
        # Simple rule-based logic for common symptoms
        if any(s in ['sốt', 'fever'] for s in symptom_names):
            if any(s in ['ho', 'cough'] for s in symptom_names):
                return {
                    "results": [
                        {
                            "diseaseName": "Cảm cúm",
                            "diseaseCode": "J11",
                            "probability": 0.75,
                            "description": "Nhiễm virus cúm gây sốt và ho",
                            "severity": "MILD",
                            "matchedSymptoms": ["sốt", "ho"],
                            "additionalQuestions": ["Có tiếp xúc với người bệnh?", "Đã tiêm vaccine cúm chưa?"],
                            "recommendedSpecialty": "Nội khoa",
                            "requiresImmediateAttention": False
                        }
                    ],
                    "recommendations": [
                        "Nghỉ ngơi tại nhà",
                        "Uống nhiều nước ấm",
                        "Dùng thuốc hạ sốt nếu cần",
                        "Theo dõi triệu chứng"
                    ],
                    "urgencyLevel": "LOW",
                    "confidenceScore": 0.75,
                    "disclaimerMessage": "Đây là kết quả chẩn đoán sơ bộ. Vui lòng tham khảo ý kiến bác sĩ để có chẩn đoán chính xác."
                }
        
        # Default response
        return {
            "results": [
                {
                    "diseaseName": "Cần đánh giá thêm",
                    "diseaseCode": "",
                    "probability": 0.5,
                    "description": "Triệu chứng cần được đánh giá bởi bác sĩ",
                    "severity": "UNKNOWN",
                    "matchedSymptoms": symptom_names,
                    "additionalQuestions": ["Triệu chứng xuất hiện từ khi nào?", "Có yếu tố nguy cơ nào khác?"],
                    "recommendedSpecialty": "Khoa Khám bệnh",
                    "requiresImmediateAttention": False
                }
            ],
            "recommendations": [
                "Nên đến khám bác sĩ để được tư vấn",
                "Theo dõi và ghi lại các triệu chứng",
                "Nghỉ ngơi và giữ gìn sức khỏe"
            ],
            "urgencyLevel": "MEDIUM",
            "confidenceScore": 0.5,
            "disclaimerMessage": "Vui lòng tham khảo ý kiến bác sĩ chuyên khoa để có chẩn đoán và điều trị phù hợp."
        }
    
    def generate_diagnosis(self, query: str, context: str, user_profile: Dict, symptoms: List[Dict]) -> Dict:
        """Main diagnosis generation method"""
        try:
            if self.llm_type == 'openai':
                return self.generate_diagnosis_openai(query, context, user_profile, symptoms)
            elif self.llm_type == 'local':
                return self.generate_diagnosis_local(query, context, user_profile, symptoms)
            else:
                return self.generate_fallback_diagnosis(symptoms)
                
        except Exception as e:
            logger.error(f"Error generating diagnosis: {e}")
            return self.generate_fallback_diagnosis(symptoms)

# Initialize RAG API
rag_api = MedicalRAGAPI()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "rag_ready": rag_api.processor is not None,
        "llm_type": rag_api.llm_type
    })

@app.route('/diagnosis', methods=['POST'])
def diagnose():
    """Main diagnosis endpoint"""
    start_time = time.time()
    
    try:
        # Authentication
        api_key = request.headers.get('X-API-Key')
        if not rag_api.authenticate(api_key):
            return jsonify({"error": "Invalid API key"}), 401
        
        # Parse request
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        session_id = data.get('sessionId', '')
        user_id = data.get('userId', '')
        user_profile = data.get('userProfile', {})
        symptoms = data.get('symptoms', [])
        additional_context = data.get('additionalContext', '')
        
        if not symptoms:
            return jsonify({"error": "No symptoms provided"}), 400
        
        # Build query from symptoms and user info
        symptom_descriptions = []
        for symptom in symptoms:
            desc = f"{symptom.get('name', '')}"
            if symptom.get('severity'):
                desc += f" (mức độ {symptom.get('severity')}/10)"
            if symptom.get('durationHours'):
                desc += f" (kéo dài {symptom.get('durationHours')} giờ)"
            symptom_descriptions.append(desc)
        
        query_parts = [
            f"Triệu chứng: {', '.join(symptom_descriptions)}",
            f"Tuổi: {user_profile.get('age', 'N/A')}",
            f"Giới tính: {user_profile.get('gender', 'N/A')}"
        ]
        
        if user_profile.get('province'):
            query_parts.append(f"Khu vực: {user_profile.get('province')}")
        
        query = ". ".join(query_parts)
        
        # Search relevant documents
        relevant_docs = rag_api.search_relevant_documents(query, top_k=5)
        
        # Prepare context
        context = "\n\n".join([
            f"Tài liệu {i+1}: {doc['title']}\n{doc['content']}"
            for i, doc in enumerate(relevant_docs)
        ])
        
        # Generate diagnosis
        diagnosis_result = rag_api.generate_diagnosis(query, context, user_profile, symptoms)
        
        # Add metadata
        diagnosis_result.update({
            "diagnosisId": f"diag_{hashlib.md5(f'{session_id}_{time.time()}'.encode()).hexdigest()[:8]}",
            "sessionId": session_id,
            "generatedAt": datetime.now().isoformat(),
            "retrievedDocuments": len(relevant_docs),
            "processingTime": round(time.time() - start_time, 2)
        })
        
        # Log the request
        logger.info(f"Diagnosis completed for session {session_id} in {time.time() - start_time:.2f}s")
        
        return jsonify(diagnosis_result)
        
    except Exception as e:
        logger.error(f"Error processing diagnosis request: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500

@app.route('/search', methods=['POST'])
def search_documents():
    """Search medical documents endpoint"""
    try:
        # Authentication
        api_key = request.headers.get('X-API-Key')
        if not rag_api.authenticate(api_key):
            return jsonify({"error": "Invalid API key"}), 401
        
        data = request.json
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({"error": "No query provided"}), 400
        
        results = rag_api.search_relevant_documents(query, top_k)
        
        return jsonify({
            "query": query,
            "results": results,
            "total": len(results)
        })
        
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/knowledge-base/stats', methods=['GET'])
def knowledge_base_stats():
    """Get knowledge base statistics"""
    try:
        if not rag_api.processor:
            return jsonify({"error": "Knowledge base not loaded"}), 503
        
        docs = rag_api.processor.documents
        categories = {}
        
        for doc in docs:
            category = doc.category
            if category not in categories:
                categories[category] = 0
            categories[category] += 1
        
        return jsonify({
            "total_documents": len(docs),
            "categories": categories,
            "index_ready": rag_api.processor.index is not None
        })
        
    except Exception as e:
        logger.error(f"Error getting KB stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Medical RAG API...")
    logger.info(f"API Key: {rag_api.api_key}")
    logger.info(f"LLM Type: {rag_api.llm_type}")
    logger.info(f"RAG Ready: {rag_api.processor is not None}")
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('DEBUG', 'False').lower() == 'true'
    )


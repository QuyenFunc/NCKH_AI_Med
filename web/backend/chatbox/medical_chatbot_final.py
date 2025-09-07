#!/usr/bin/env python3
"""
Medical AI RAG Chatbot - Hoàn chỉnh cho chẩn đoán bệnh
Sử dụng all-mpnet-base-v2 với improved search và Vietnamese enhancement
"""
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json
from datetime import datetime
import uuid
import time
import re

# Import RAG utilities
from medical_rag_utils import (
    search_medical_symptoms_and_diseases,
    create_medical_diagnostic_context,
    get_medical_statistics,
    improve_vietnamese_query
)

# Import Hybrid Search
from hybrid_search import get_hybrid_search_engine

# Import Enhanced Features từ app.py
from query_transformation import transform_medical_query
from structured_extraction import extract_medical_structure
from medical_logging import log_query, log_search, log_llm, log_extraction, log_error, get_stats

app = Flask(__name__)
CORS(app)

class MedicalChatbot:
    """Medical AI RAG Chatbot cho chẩn đoán bệnh"""
    
    def __init__(self):
        self.conversation_history = {}
        self.session_timeout = 30 * 60  # 30 phút
        self.hybrid_search_engine = None
        self.answer_cache = {}  # Cache for responses
        self.max_cache_size = 1000  # Giới hạn cache
        self._init_hybrid_search()
    
    def _init_hybrid_search(self):
        """Initialize hybrid search engine"""
        try:
            print("🔄 Initializing hybrid search engine...")
            self.hybrid_search_engine = get_hybrid_search_engine()
            print("✅ Hybrid search engine initialized successfully")
            print(f"   📊 BM25 corpus size: {len(self.hybrid_search_engine.tokenized_corpus) if self.hybrid_search_engine.tokenized_corpus else 0}")
            print(f"   🔍 Search method: Hybrid (Semantic + BM25)")
        except Exception as e:
            print(f"⚠️ Could not initialize hybrid search: {e}")
            print("   🔄 Falling back to pure semantic search")
            self.hybrid_search_engine = None
        
    def classify_medical_intent(self, query):
        """Phân loại ý định của câu hỏi y tế"""
        query_lower = query.lower()
        
        # Triệu chứng keywords
        symptom_keywords = [
            'đau', 'buồn nôn', 'sốt', 'ho', 'khó thở', 'mệt mỏi', 'chóng mặt',
            'pain', 'fever', 'cough', 'nausea', 'headache', 'fatigue'
        ]
        
        # Bệnh keywords  
        disease_keywords = [
            'bệnh', 'chẩn đoán', 'điều trị', 'thuốc', 'viêm', 'ung thư', 'tiểu đường',
            'disease', 'diagnosis', 'treatment', 'medicine', 'diabetes', 'cancer'
        ]
        
        # Tư vấn keywords
        consultation_keywords = [
            'nên làm gì', 'có nên', 'khám ở đâu', 'bác sĩ', 'tư vấn',
            'what should', 'should i', 'doctor', 'advice', 'recommend'
        ]
        
        symptom_count = sum(1 for keyword in symptom_keywords if keyword in query_lower)
        disease_count = sum(1 for keyword in disease_keywords if keyword in query_lower) 
        consultation_count = sum(1 for keyword in consultation_keywords if keyword in query_lower)
        
        if symptom_count > 0:
            return 'symptom_analysis'
        elif disease_count > 0:
            return 'disease_inquiry'
        elif consultation_count > 0:
            return 'medical_consultation'
        else:
            return 'general_medical'
    
    def create_medical_response(self, query, search_results, intent):
        """Tạo phản hồi y tế dựa trên kết quả tìm kiếm và ý định"""
        
        if not search_results:
            return {
                'response': "Xin lỗi, tôi không tìm thấy thông tin y tế liên quan đến câu hỏi của bạn. Bạn có thể mô tả rõ hơn các triệu chứng hoặc vấn đề sức khỏe không?",
                'confidence': 0.0,
                'sources': [],
                'recommendations': ["Mô tả chi tiết hơn các triệu chứng", "Tham khảo ý kiến bác sĩ"]
            }
        
        # Tạo context từ search results
        context_parts = []
        sources = []
        
        for i, result in enumerate(search_results[:3], 1):
            metadata = result['metadata']
            entity_name = metadata.get('entity_name', 'Unknown')
            text_snippet = result['text'][:200] + "..." if len(result['text']) > 200 else result['text']
            
            context_parts.append(f"{i}. {entity_name}: {text_snippet}")
            
            sources.append({
                'title': entity_name,
                'url': metadata.get('browser_url', ''),
                'relevance': result.get('relevance_score', result.get('semantic_score', 0)),
                'icd_code': metadata.get('entity_code', '')
            })
        
        context = "\n".join(context_parts)
        
        # Tạo response dựa trên intent
        if intent == 'symptom_analysis':
            response_template = f"""Dựa trên các triệu chứng bạn mô tả, đây là những thông tin y tế liên quan:

{context}

**Lưu ý quan trọng:**
- Đây chỉ là thông tin tham khảo từ cơ sở dữ liệu y tế ICD-11
- Không thể thay thế việc khám và chẩn đoán của bác sĩ
- Nếu triệu chứng nghiêm trọng hoặc kéo dài, hãy đến gặp bác sĩ ngay

**Khuyến nghị:**
- Theo dõi và ghi chép các triệu chứng
- Tham khảo ý kiến bác sĩ để được chẩn đoán chính xác
- Không tự ý dùng thuốc mà chưa có chỉ định của bác sĩ"""
            
        elif intent == 'disease_inquiry':
            response_template = f"""Thông tin về vấn đề sức khỏe bạn quan tâm:

{context}

**Thông tin này từ cơ sở dữ liệu ICD-11 của WHO:**
- Được sử dụng làm tiêu chuẩn quốc tế cho phân loại bệnh tật
- Cung cấp thông tin về định nghĩa, tiêu chí chẩn đoán
- Giúp hiểu rõ hơn về các tình trạng sức khỏe

**Khuyến nghị:**
- Tham khảo thêm ý kiến của các chuyên gia y tế
- Thực hiện các xét nghiệm cần thiết nếu bác sĩ chỉ định
- Tuân thủ phác đồ điều trị của bác sĩ"""
            
        elif intent == 'medical_consultation':
            response_template = f"""Dựa trên thông tin y tế có sẵn:

{context}

**Tư vấn y tế:**
- Thông tin trên chỉ mang tính chất tham khảo
- Mỗi trường hợp cụ thể cần được đánh giá riêng biệt
- Việc chẩn đoán và điều trị phải do bác sĩ thực hiện

**Khuyến nghị hành động:**
- Đặt lịch khám với bác sĩ chuyên khoa phù hợp
- Chuẩn bị đầy đủ thông tin về triệu chứng và tiền sử bệnh
- Tuân thủ nghiêm ngặt chỉ định của bác sĩ"""
            
        else:  # general_medical
            response_template = f"""Thông tin y tế liên quan đến câu hỏi của bạn:

{context}

**Thông tin từ cơ sở dữ liệu y tế ICD-11:**
- Đây là hệ thống phân loại bệnh tật quốc tế của WHO
- Cung cấp thông tin chuẩn mực về các vấn đề sức khỏe
- Được sử dụng rộng rãi trong hệ thống y tế toàn cầu

**Lời khuyên:**
- Sử dụng thông tin này để hiểu rõ hơn về sức khỏe
- Luôn tham khảo ý kiến bác sĩ cho các vấn đề cụ thể
- Không tự chẩn đoán hoặc điều trị dựa trên thông tin này"""
        
        # Tính confidence score
        avg_relevance = sum(result.get('relevance_score', result.get('semantic_score', 0)) for result in search_results[:3]) / min(3, len(search_results))
        confidence = min(avg_relevance * 1.2, 1.0)  # Scale up but cap at 1.0
        
        return {
            'response': response_template,
            'confidence': confidence,
            'sources': sources,
            'intent': intent,
            'enhanced_query': improve_vietnamese_query(query) if query != improve_vietnamese_query(query) else None
        }
    
    def get_session(self, session_id):
        """Lấy hoặc tạo session mới"""
        current_time = datetime.now()
        
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = {
                'messages': [],
                'created_at': current_time,
                'last_activity': current_time
            }
        else:
            self.conversation_history[session_id]['last_activity'] = current_time
        
        return self.conversation_history[session_id]
    
    def clean_expired_sessions(self):
        """Dọn dẹp các session hết hạn"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.conversation_history.items():
            if (current_time - session_data['last_activity']).seconds > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.conversation_history[session_id]
    
    def chat(self, query, session_id=None):
        """Main chat function"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Clean expired sessions
        self.clean_expired_sessions()
        
        # Get session
        session = self.get_session(session_id)
        
        # Classify intent
        intent = self.classify_medical_intent(query)
        
        # Search medical knowledge base với hybrid search
        search_start_time = time.time()
        if self.hybrid_search_engine:
            try:
                search_results = self.hybrid_search_engine.hybrid_search(query, top_k=5)
                search_time = time.time() - search_start_time
                print(f"🔍 Hybrid search: {len(search_results)} results in {search_time:.2f}s")
            except Exception as e:
                print(f"⚠️ Hybrid search failed, falling back to semantic: {e}")
                search_results = search_medical_symptoms_and_diseases(query, top_k=5)
                search_time = time.time() - search_start_time
                print(f"🔄 Semantic fallback: {len(search_results)} results in {search_time:.2f}s")
        else:
            search_results = search_medical_symptoms_and_diseases(query, top_k=5)
            search_time = time.time() - search_start_time
            print(f"🔍 Semantic search: {len(search_results)} results in {search_time:.2f}s")
        
        # Create response
        response_data = self.create_medical_response(query, search_results, intent)
        
        # Add to conversation history
        session['messages'].append({
            'timestamp': datetime.now().isoformat(),
            'user_query': query,
            'intent': intent,
            'response': response_data['response'],
            'confidence': response_data['confidence'],
            'sources_count': len(response_data['sources'])
        })
        
        # Limit history size
        if len(session['messages']) > 20:
            session['messages'] = session['messages'][-20:]
        
        # Add session info to response
        response_data['session_id'] = session_id
        response_data['message_count'] = len(session['messages'])
        response_data['search_method'] = 'hybrid' if self.hybrid_search_engine else 'semantic'
        response_data['search_time'] = search_time
        response_data['timestamp'] = datetime.now().isoformat()
        
        return response_data

# Initialize chatbot
chatbot = MedicalChatbot()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Medical AI RAG Chatbot',
        'version': '1.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    """Main chat endpoint"""
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            return jsonify({
                'error': 'Missing query parameter',
                'message': 'Vui lòng cung cấp câu hỏi y tế'
            }), 400
        
        query = data['query'].strip()
        session_id = data.get('session_id')
        
        if not query:
            return jsonify({
                'error': 'Empty query',
                'message': 'Câu hỏi không được để trống'
            }), 400
        
        # Process chat
        start_time = time.time()
        response = chatbot.chat(query, session_id)
        processing_time = time.time() - start_time
        
        # Add metadata
        response['processing_time'] = round(processing_time, 3)
        response['timestamp'] = datetime.now().isoformat()
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'message': f'Đã xảy ra lỗi: {str(e)}'
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        stats = get_medical_statistics()
        
        # Add chatbot stats
        total_sessions = len(chatbot.conversation_history)
        total_messages = sum(len(session['messages']) for session in chatbot.conversation_history.values())
        
        stats.update({
            'chatbot': {
                'active_sessions': total_sessions,
                'total_messages': total_messages,
                'model': 'all-MiniLM-L6-v2',
                'search_method': 'hybrid' if chatbot.hybrid_search_engine else 'semantic',
                'features': ['Vietnamese enhancement', 'Intent classification', 'Medical context', 'Hybrid search']
            }
        })
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'error': 'Cannot get statistics',
            'message': str(e)
        }), 500

@app.route('/session/<session_id>/history', methods=['GET'])
def get_session_history(session_id):
    """Get conversation history for a session"""
    if session_id not in chatbot.conversation_history:
        return jsonify({
            'error': 'Session not found',
            'message': 'Không tìm thấy phiên trò chuyện'
        }), 404
    
    session = chatbot.conversation_history[session_id]
    return jsonify({
        'session_id': session_id,
        'created_at': session['created_at'].isoformat(),
        'last_activity': session['last_activity'].isoformat(),
        'message_count': len(session['messages']),
        'messages': session['messages']
    })

if __name__ == '__main__':
    print("🏥 MEDICAL AI RAG CHATBOT - CHẨN ĐOÁN BỆNH")
    print("=" * 60)
    print("🤖 Model: all-MiniLM-L6-v2 với Vietnamese enhancement")
    print("🔍 RAG: Hybrid search (Semantic + BM25) với ICD-11 data")
    print("💬 Features: Intent classification, Medical context, Hybrid search")
    print("=" * 60)
    print("🚀 Starting server...")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
                           
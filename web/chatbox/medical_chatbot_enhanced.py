#!/usr/bin/env python3
"""
Enhanced Medical AI RAG Chatbot
Tích hợp features từ app.py: logging, caching, query transformation, structured extraction
"""
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from datetime import datetime
import uuid
import time
import re
import json
from collections import deque
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

def ensure_json_serializable(obj):
    """Convert any NumPy types to Python native types for JSON serialization"""
    if hasattr(obj, 'item'):  # NumPy scalar
        return obj.item()
    elif NUMPY_AVAILABLE and isinstance(obj, np.ndarray):
        return obj.tolist()
    elif NUMPY_AVAILABLE and isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif NUMPY_AVAILABLE and isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, dict):
        return {k: ensure_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [ensure_json_serializable(item) for item in obj]
    else:
        return obj

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
try:
    from query_transformation import transform_medical_query
    QUERY_TRANSFORM_AVAILABLE = True
except ImportError:
    print("⚠️ Query transformation not available")
    QUERY_TRANSFORM_AVAILABLE = False

try:
    from structured_extraction import extract_medical_structure
    EXTRACTION_AVAILABLE = True
except ImportError:
    print("⚠️ Structured extraction not available")
    EXTRACTION_AVAILABLE = False

try:
    from medical_logging import log_query, log_search, log_llm, log_extraction, log_error, get_stats
    LOGGING_AVAILABLE = True
except ImportError:
    print("⚠️ Medical logging not available")
    LOGGING_AVAILABLE = False

# Import New Enhancement Modules
try:
    from enhanced_search_quality import get_search_quality_enhancer
    SEARCH_QUALITY_AVAILABLE = True
except ImportError:
    print("⚠️ Enhanced search quality not available")
    SEARCH_QUALITY_AVAILABLE = False

try:
    from medical_ner import get_medical_ner
    NER_AVAILABLE = True
except ImportError:
    print("⚠️ Medical NER not available")
    NER_AVAILABLE = False

try:
    from enhanced_confidence import get_confidence_calculator
    ENHANCED_CONFIDENCE_AVAILABLE = True
except ImportError:
    print("⚠️ Enhanced confidence not available")
    ENHANCED_CONFIDENCE_AVAILABLE = False

try:
    from performance_optimizer import get_performance_optimizer
    PERFORMANCE_OPTIMIZER_AVAILABLE = True
except ImportError:
    print("⚠️ Performance optimizer not available")
    PERFORMANCE_OPTIMIZER_AVAILABLE = False

# Import Ultra-Fast Optimization Modules
try:
    from optimized_hybrid_search import get_fast_hybrid_search_engine
    FAST_HYBRID_AVAILABLE = True
except ImportError:
    print("⚠️ Fast hybrid search not available")
    FAST_HYBRID_AVAILABLE = False

try:
    from advanced_cache import get_smart_query_cache, get_result_cache
    ADVANCED_CACHE_AVAILABLE = True
except ImportError:
    print("⚠️ Advanced cache not available")
    ADVANCED_CACHE_AVAILABLE = False

try:
    from async_processor import (
        get_parallel_entity_extractor, 
        get_parallel_search_processor,
        get_async_response_generator
    )
    ASYNC_PROCESSOR_AVAILABLE = True
except ImportError:
    print("⚠️ Async processor not available")
    ASYNC_PROCESSOR_AVAILABLE = False

try:
    from query_compression import get_query_compressor
    QUERY_COMPRESSION_AVAILABLE = True
except ImportError:
    print("⚠️ Query compression not available")
    QUERY_COMPRESSION_AVAILABLE = False

# Import AI Service for OpenRouter DeepSeek
try:
    from ai_service import get_medical_ai_service
    AI_SERVICE_AVAILABLE = True
except ImportError:
    print("⚠️ AI service not available")
    AI_SERVICE_AVAILABLE = False

app = Flask(__name__)
CORS(app)

class EnhancedMedicalChatbot:
    """Enhanced Medical AI RAG Chatbot với advanced features"""
    
    def __init__(self):
        self.conversation_history = {}
        self.session_timeout = 30 * 60  # 30 phút
        self.hybrid_search_engine = None
        self.answer_cache = {}  # Cache for responses
        self.max_cache_size = 1000  # Giới hạn cache
        self.stats = {
            'total_queries': 0,
            'cache_hits': 0,
            'search_times': [],
            'response_times': []
        }
        
        # Initialize enhancement modules
        self.search_quality_enhancer = None
        self.medical_ner = None
        self.confidence_calculator = None
        self.performance_optimizer = None
        
        # Initialize ultra-fast optimization modules
        self.fast_hybrid_engine = None
        self.smart_cache = None
        self.result_cache = None
        self.parallel_extractor = None
        self.parallel_search = None
        self.async_generator = None
        self.query_compressor = None
        
        # Initialize AI service
        self.ai_service = None
        
        # Ultra-fast performance tracking
        self.ultra_fast_stats = {
            'sub_3s_responses': 0,
            'optimization_wins': {
                'fast_hybrid': 0,
                'advanced_cache': 0,
                'async_processing': 0,
                'query_compression': 0
            }
        }
        
        self._init_all_systems()
    
    def _init_all_systems(self):
        """Initialize all enhancement systems"""
        print("🚀 Initializing Enhanced Medical Chatbot Systems...")
        
        # Initialize hybrid search
        self._init_hybrid_search()
        
        # Initialize search quality enhancer
        if SEARCH_QUALITY_AVAILABLE:
            try:
                self.search_quality_enhancer = get_search_quality_enhancer()
                print("✅ Search quality enhancer initialized")
            except Exception as e:
                print(f"⚠️ Search quality enhancer failed: {e}")
        
        # Initialize medical NER
        if NER_AVAILABLE:
            try:
                self.medical_ner = get_medical_ner()
                print("✅ Medical NER initialized")
            except Exception as e:
                print(f"⚠️ Medical NER failed: {e}")
        
        # Initialize enhanced confidence calculator
        if ENHANCED_CONFIDENCE_AVAILABLE:
            try:
                self.confidence_calculator = get_confidence_calculator()
                print("✅ Enhanced confidence calculator initialized")
            except Exception as e:
                print(f"⚠️ Enhanced confidence calculator failed: {e}")
        
        # Initialize performance optimizer
        if PERFORMANCE_OPTIMIZER_AVAILABLE:
            try:
                self.performance_optimizer = get_performance_optimizer()
                print("✅ Performance optimizer initialized")
            except Exception as e:
                print(f"⚠️ Performance optimizer failed: {e}")
        
        # Initialize ultra-fast optimization systems
        self._init_ultra_fast_systems()
        
        print("🎉 All systems initialized!")
    
    def _init_ultra_fast_systems(self):
        """Initialize ultra-fast optimization systems"""
        print("⚡ Initializing Ultra-Fast Optimization Systems...")
        
        # 1. Fast Hybrid Search
        if FAST_HYBRID_AVAILABLE:
            try:
                print("🔄 Loading fast hybrid search...")
                from medical_rag_utils import load_medical_data
                medical_data = load_medical_data()
                self.fast_hybrid_engine = get_fast_hybrid_search_engine(
                    chunks_data=medical_data,
                    medical_rag_utils=None
                )
                print("✅ Fast hybrid search ready")
            except Exception as e:
                print(f"⚠️ Fast hybrid search failed: {e}")
        
        # 2. Advanced Caching
        if ADVANCED_CACHE_AVAILABLE:
            try:
                self.smart_cache = get_smart_query_cache()
                self.result_cache = get_result_cache()
                print("✅ Advanced caching ready")
            except Exception as e:
                print(f"⚠️ Advanced caching failed: {e}")
        
        # 3. Async Processing
        if ASYNC_PROCESSOR_AVAILABLE:
            try:
                # Initialize with NER if available
                ner_models = []
                if self.medical_ner:
                    ner_models = [self.medical_ner]
                
                self.parallel_extractor = get_parallel_entity_extractor(ner_models)
                self.parallel_search = get_parallel_search_processor()
                self.async_generator = get_async_response_generator()
                print("✅ Async processing ready")
            except Exception as e:
                print(f"⚠️ Async processing failed: {e}")
        
        # 4. Query Compression
        if QUERY_COMPRESSION_AVAILABLE:
            try:
                self.query_compressor = get_query_compressor()
                print("✅ Query compression ready")
            except Exception as e:
                print(f"⚠️ Query compression failed: {e}")
        
        if AI_SERVICE_AVAILABLE:
            try:
                self.ai_service = get_medical_ai_service()
                print("✅ AI Service (OpenRouter DeepSeek) ready")
            except Exception as e:
                print(f"⚠️ AI Service failed: {e}")
        
        print("🚀 Ultra-fast optimizations ready!")
    
    def _init_hybrid_search(self):
        """Initialize hybrid search engine"""
        try:
            print("🔄 Initializing enhanced hybrid search engine...")
            self.hybrid_search_engine = get_hybrid_search_engine()
            print("✅ Enhanced hybrid search engine initialized successfully")
            print(f"   📊 BM25 corpus size: {len(self.hybrid_search_engine.tokenized_corpus) if self.hybrid_search_engine.tokenized_corpus else 0}")
            print(f"   🔍 Search method: Enhanced Hybrid (Semantic + BM25 + Caching)")
        except Exception as e:
            print(f"⚠️ Could not initialize hybrid search: {e}")
            print("   🔄 Falling back to pure semantic search")
            self.hybrid_search_engine = None

    def classify_medical_intent(self, query):
        """Phân loại ý định của câu hỏi y tế"""
        query_lower = query.lower()
        
        # Triệu chứng keywords
        symptom_keywords = [
            'đau', 'sốt', 'ho', 'buồn nôn', 'chóng mặt', 'mệt mỏi', 'khó thở',
            'đau đầu', 'đau bụng', 'tiêu chảy', 'táo bón', 'phát ban', 'ngứa',
            'sưng', 'viêm', 'nhiễm trùng', 'cảm lạnh', 'cúm', 'bệnh tật'
        ]
        
        # Emergency keywords  
        emergency_keywords = [
            'cấp cứu', 'nguy hiểm', 'khẩn cấp', 'nghiêm trọng', 'nặng',
            'đau ngực', 'khó thở', 'choáng váng', 'bất tỉnh', 'máu'
        ]
        
        # Disease inquiry keywords
        disease_keywords = [
            'bệnh', 'hội chứng', 'rối loạn', 'triệu chứng', 'nguyên nhân',
            'điều trị', 'thuốc', 'phòng ngừa', 'biến chứng'
        ]
        
        # Consultation keywords
        consultation_keywords = [
            'nên làm gì', 'cách điều trị', 'khám bác sĩ', 'đi viện',
            'lời khuyên', 'tư vấn', 'hướng dẫn', 'chăm sóc'
        ]
        
        # Check patterns
        if any(keyword in query_lower for keyword in emergency_keywords):
            return 'emergency'
        elif any(keyword in query_lower for keyword in consultation_keywords):
            return 'medical_consultation'
        elif any(keyword in query_lower for keyword in disease_keywords):
            return 'disease_inquiry'
        elif any(keyword in query_lower for keyword in symptom_keywords):
            return 'symptom_analysis'
        else:
            return 'general_medical'

    def get_session(self, session_id):
        """Get or create conversation session"""
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
        """Clean expired conversation sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.conversation_history.items():
            if (current_time - session['last_activity']).seconds > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.conversation_history[session_id]
            print(f"🗑️ Expired session cleaned: {session_id}")

    def extract_conversation_context(self, session):
        """Extract relevant context from conversation history"""
        if not session['messages']:
            return None
        
        # Get last few messages for context
        recent_messages = session['messages'][-6:]  # Last 3 exchanges
        
        context_info = {
            'mentioned_diseases': [],
            'mentioned_symptoms': [],
            'mentioned_treatments': [],
            'mentioned_entities': [],  # General medical entities
            'last_topic': None,
            'conversation_summary': []
        }
        
        # Extract entities from conversation
        for msg in recent_messages:
            content = msg.get('user_query', '') + ' ' + msg.get('response', '')
            content_lower = content.lower()
            
            # Extract diseases mentioned
            disease_keywords = ['tiểu đường', 'cao huyết áp', 'viêm phổi', 'cúm', 'sốt xuất huyết', 
                              'ung thư', 'tim mạch', 'đột quỵ', 'hen suyễn', 'dị ứng', 'viêm gan',
                              'viêm dạ dày', 'loét dạ dày', 'suy thận', 'sỏi thận', 'Covid-19']
            for disease in disease_keywords:
                if disease in content_lower and disease not in context_info['mentioned_diseases']:
                    context_info['mentioned_diseases'].append(disease)
                    context_info['mentioned_entities'].append(disease)
            
            # Extract symptoms mentioned  
            symptom_keywords = ['đau đầu', 'sốt', 'ho', 'buồn nôn', 'chóng mặt', 'mệt mỏi',
                               'khó thở', 'đau bụng', 'tiêu chảy', 'phát ban', 'ngứa', 'đau ngực',
                               'đau lưng', 'đau cổ', 'khàn tiếng', 'nghẹt mũi', 'chảy nước mũi']
            for symptom in symptom_keywords:
                if symptom in content_lower and symptom not in context_info['mentioned_symptoms']:
                    context_info['mentioned_symptoms'].append(symptom)
                    context_info['mentioned_entities'].append(symptom)
            
            # Extract treatments mentioned
            treatment_keywords = ['thuốc', 'điều trị', 'phẫu thuật', 'khám bác sĩ', 'nghỉ ngơi',
                                 'uống nước', 'ăn kiêng', 'tập thể dục', 'vaccine', 'tiêm chủng',
                                 'xét nghiệm', 'chụp X-quang', 'siêu âm', 'nội soi']
            for treatment in treatment_keywords:
                if treatment in content_lower and treatment not in context_info['mentioned_treatments']:
                    context_info['mentioned_treatments'].append(treatment)
                    context_info['mentioned_entities'].append(treatment)
            
            # Add to conversation summary
            if msg.get('user_query'):
                context_info['conversation_summary'].append(f"User: {msg['user_query']}")
            if msg.get('intent'):
                context_info['last_topic'] = msg['intent']
        
        return context_info

    def resolve_query_references(self, query, context_info):
        """Resolve pronouns and references in query using context"""
        if not context_info:
            return query
        
        resolved_query = query
        query_lower = query.lower()
        
        # Common reference patterns với Vietnamese
        reference_patterns = {
            'cái này': context_info['mentioned_entities'][-1:],
            'cái đó': context_info['mentioned_entities'][-1:],
            'cái kia': context_info['mentioned_entities'][-2:-1] if len(context_info['mentioned_entities']) > 1 else context_info['mentioned_entities'][-1:],
            'nó': context_info['mentioned_entities'][-1:],
            'chúng': context_info['mentioned_entities'][-2:],
            'bệnh này': context_info['mentioned_diseases'][-1:],
            'bệnh đó': context_info['mentioned_diseases'][-1:],
            'bệnh kia': context_info['mentioned_diseases'][-2:-1] if len(context_info['mentioned_diseases']) > 1 else context_info['mentioned_diseases'][-1:],
            'triệu chứng này': context_info['mentioned_symptoms'][-1:],
            'triệu chứng đó': context_info['mentioned_symptoms'][-1:],
            'triệu chứng kia': context_info['mentioned_symptoms'][-2:-1] if len(context_info['mentioned_symptoms']) > 1 else context_info['mentioned_symptoms'][-1:],
            'thuốc này': context_info['mentioned_treatments'][-1:],
            'thuốc đó': context_info['mentioned_treatments'][-1:],
            'cách điều trị này': context_info['mentioned_treatments'][-1:],
            'phương pháp này': context_info['mentioned_treatments'][-1:]
        }
        
        # Replace references with actual entities
        for reference, entities in reference_patterns.items():
            if reference in query_lower and entities:
                # Replace with most recent relevant entity
                replacement = entities[0]
                resolved_query = resolved_query.replace(reference, replacement)
                print(f"🔗 Resolved '{reference}' → '{replacement}'")
        
        # Handle more complex reference patterns
        if any(pattern in query_lower for pattern in ['làm sao', 'như thế nào', 'có sao không', 'nguy hiểm không', 
                                                     'cần làm gì', 'có nên', 'có thể', 'phải không']):
            context_added = False
            
            # Add disease context if available
            if context_info['mentioned_diseases'] and not context_added:
                disease_context = context_info['mentioned_diseases'][-1]
                resolved_query = f"{resolved_query} (về {disease_context})"
                print(f"🎯 Added disease context: {disease_context}")
                context_added = True
            
            # Add symptom context if no disease context
            elif context_info['mentioned_symptoms'] and not context_added:
                symptom_context = context_info['mentioned_symptoms'][-1]
                resolved_query = f"{resolved_query} (về {symptom_context})"
                print(f"🎯 Added symptom context: {symptom_context}")
                context_added = True
        
        return resolved_query
    
    def _create_sources_from_results(self, search_results):
        """Create sources list from search results"""
        sources = []
        for result in search_results:
            metadata = result.get('metadata', {})
            sources.append({
                'title': metadata.get('entity_name', 'Unknown'),
                'url': metadata.get('browser_url', ''),
                'relevance': result.get('relevance_score', result.get('semantic_score', 0)),
                'icd_code': metadata.get('entity_code', '')
            })
        return sources
    
    def _get_lightweight_session_context(self, session_id):
        """Get lightweight session context for caching"""
        if not session_id or session_id not in self.conversation_history:
            return {}
        
        session = self.conversation_history[session_id]
        return {
            'has_history': len(session.get('messages', [])) > 0,
            'recent_queries': len(session.get('messages', []))
        }

    def enhance_query_with_context(self, query, context_info):
        """Enhance query with conversation context for better search"""
        if not context_info:
            return query
        
        enhanced_query = query
        
        # Add relevant context entities to query for better search
        relevant_context = []
        
        # Add recent diseases for context (max 2)
        if context_info['mentioned_diseases']:
            relevant_context.extend(context_info['mentioned_diseases'][-2:])
        
        # Add recent symptoms for context (max 2)
        if context_info['mentioned_symptoms']:
            relevant_context.extend(context_info['mentioned_symptoms'][-2:])
        
        # Add recent treatments for context (max 1)
        if context_info['mentioned_treatments']:
            relevant_context.extend(context_info['mentioned_treatments'][-1:])
        
        if relevant_context:
            # Remove duplicates while preserving order
            unique_context = []
            for item in relevant_context:
                if item not in unique_context:
                    unique_context.append(item)
            
            context_string = ' '.join(unique_context[:3])  # Max 3 context items
            enhanced_query = f"{query} {context_string}"
            print(f"🔍 Enhanced query with context: {context_string}")
        
        return enhanced_query

    def create_medical_response(self, query, search_results, intent):
        """Create medical response based on intent and search results"""
        sources = []
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
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
        
        context = "\\n".join(context_parts)
        
        # Enhanced response templates based on intent
        if intent == 'emergency':
            response_template = f"""⚠️ **TÌNH HUỐNG Y TẾ KHẨN CẤP**

🚨 **LƯU Ý QUAN TRỌNG:** Nếu đây là tình huống khẩn cấp, hãy gọi ngay:
- **115** (Cấp cứu)
- **Đến bệnh viện gần nhất**

**Thông tin tham khảo từ cơ sở dữ liệu ICD-11:**
{context}

⚠️ **Lưu ý:** Đây chỉ là thông tin tham khảo. KHÔNG trì hoãn việc tìm kiếm sự chăm sóc y tế khẩn cấp."""

        elif intent == 'symptom_analysis':
            response_template = f"""🔍 **PHÂN TÍCH TRIỆU CHỨNG**

**Câu hỏi của bạn:** {query}

**Thông tin từ cơ sở dữ liệu ICD-11:**
{context}

💡 **Phân tích:**
Dựa trên các triệu chứng bạn mô tả, có thể liên quan đến các tình trạng sức khỏe được liệt kê ở trên. 

⚠️ **Khuyến nghị:**
- Theo dõi triệu chứng trong 24-48 giờ
- Ghi chép thời gian, mức độ nghiêm trọng
- Tham khảo ý kiến bác sĩ nếu triệu chứng kéo dài hoặc nặng hơn
- Không tự chẩn đoán hoặc tự điều trị"""

        elif intent == 'disease_inquiry':
            response_template = f"""📚 **THÔNG TIN BỆNH LÝ**

**Câu hỏi của bạn:** {query}

**Thông tin chi tiết từ ICD-11:**
{context}

📋 **Tổng quan:**
Thông tin trên cung cấp kiến thức y khoa chính thức từ Tổ chức Y tế Thế giới (WHO).

💊 **Lưu ý điều trị:**
- Mọi quyết định điều trị cần được bác sĩ chuyên khoa quyết định
- Không tự ý sử dụng thuốc mà không có chỉ định
- Tuân thủ theo dõi và tái khám định kỳ"""

        elif intent == 'medical_consultation':
            response_template = f"""🩺 **TƯ VẤN Y TẾ**

**Câu hỏi của bạn:** {query}

**Thông tin tham khảo từ ICD-11:**
{context}

💬 **Lời khuyên:**
Dựa trên thông tin y khoa hiện có, tôi khuyến nghị bạn:

1. **Tham khảo ý kiến chuyên gia:** Liên hệ với bác sĩ chuyên khoa phù hợp
2. **Chuẩn bị thông tin:** Ghi chép triệu chứng, thời gian xuất hiện, các yếu tố liên quan
3. **Theo dõi sát sao:** Ghi nhận mọi thay đổi về tình trạng sức khỏe
4. **Tuân thủ hướng dẫn:** Làm theo chỉ định y tế chính thức

📞 **Khi nào cần gấp:** Nếu có dấu hiệu nghiêm trọng, hãy tìm kiếm sự chăm sóc y tế ngay lập tức."""

        else:  # general_medical
            response_template = f"""🏥 **THÔNG TIN Y TẾ TỔNG QUÁT**

**Câu hỏi của bạn:** {query}

**Thông tin từ cơ sở dữ liệu ICD-11:**
{context}

💡 **Thông tin tham khảo:**
Đây là thông tin y khoa chính thức được cung cấp từ hệ thống phân loại bệnh quốc tế ICD-11 của WHO.

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
            'intent': intent
        }

    def semantic_search(self, query, session_id=None):
        """Ultra-fast enhanced chat function với streaming support"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        total_start_time = time.time()
        self.stats['total_queries'] += 1
        
        # 1. Ultra-fast cache check first (Advanced Cache)
        if self.smart_cache:
            try:
                session_context = self._get_lightweight_session_context(session_id)
                cached_result, cache_level = self.smart_cache.get_cached_result(
                    query, context=session_context
                )
                if cached_result:
                    print(f"💾 Using {cache_level} cached response")
                    self.stats['cache_hits'] += 1
                    self.ultra_fast_stats['optimization_wins']['advanced_cache'] += 1
                    cached_result['from_cache'] = True
                    cached_result['cache_level'] = cache_level
                    cached_result['total_time'] = time.time() - total_start_time
                    # ✅ Add missing fields for chat_stream compatibility
                    cached_result['session_id'] = session_id
                    session = self.get_session(session_id)
                    cached_result['context_info'] = self.extract_conversation_context(session)
                    return cached_result
            except Exception as e:
                print(f"⚠️ Advanced cache failed: {e}")
        
        # 2. Fallback to simple cache
        cache_key = f"{session_id}:{query}"
        if cache_key in self.answer_cache:
            print("💾 Using simple cached response")
            self.stats['cache_hits'] += 1
            cached_response = self.answer_cache[cache_key].copy()
            cached_response['from_cache'] = True
            cached_response['cache_level'] = 'simple'
            cached_response['total_time'] = time.time() - total_start_time
            # ✅ Add missing fields for chat_stream compatibility
            cached_response['session_id'] = session_id
            session = self.get_session(session_id)
            cached_response['context_info'] = self.extract_conversation_context(session)
            return cached_response
        
        # 3. Log initial query
        if LOGGING_AVAILABLE:
            try:
                log_query(query, session_id, "unknown")
            except Exception as e:
                print(f"⚠️ Logging failed: {e}")
        
        # 4. Query Compression (Ultra-fast optimization)
        compression_start = time.time()
        compressed_query_info = None
        if self.query_compressor:
            try:
                compressed_query_info = self.query_compressor.compress_query(query, target_length=40)
                if compressed_query_info.compression_ratio < 0.8:
                    print(f"🗜️ Query compressed: '{query}' → '{compressed_query_info.compressed}'")
                    self.ultra_fast_stats['optimization_wins']['query_compression'] += 1
            except Exception as e:
                print(f"⚠️ Query compression failed: {e}")
        compression_time = time.time() - compression_start
        
        # 5. Clean expired sessions
        self.clean_expired_sessions()
        
        # 6. Get session
        session = self.get_session(session_id)
        
        # 7. Extract conversation context
        context_info = self.extract_conversation_context(session)
        
        # 8. Resolve references in query using context
        original_query = query
        resolved_query = self.resolve_query_references(query, context_info)
        
        # 9. Query transformation
        if QUERY_TRANSFORM_AVAILABLE:
            try:
                transformed_result = transform_medical_query(resolved_query)
                if isinstance(transformed_result, dict):
                    transformed_query = transformed_result.get('enriched_query', resolved_query)
                    if transformed_query != resolved_query:
                        print(f"🔄 Query transformed: '{resolved_query}' → '{transformed_query}'")
                        resolved_query = transformed_query
                else:
                    if transformed_result != resolved_query:
                        print(f"🔄 Query transformed: '{resolved_query}' → '{transformed_result}'")
                        resolved_query = transformed_result
            except Exception as e:
                print(f"⚠️ Query transformation failed: {e}")
        
        # 10. Enhance query with context for better search
        enhanced_query = self.enhance_query_with_context(resolved_query, context_info)
        
        # Use compressed query if available and beneficial
        if compressed_query_info and compressed_query_info.compression_ratio < 0.8:
            search_query = compressed_query_info.compressed
        else:
            search_query = enhanced_query
        
        # Log the query processing pipeline
        print(f"💬 Original: '{original_query}'")
        if resolved_query != original_query:
            print(f"🔗 Resolved: '{resolved_query}'")
        if enhanced_query != resolved_query:
            print(f"🔍 Enhanced: '{enhanced_query}'")
        if compressed_query_info and search_query == compressed_query_info.compressed:
            print(f"🗜️ Using compressed: '{search_query}'")
        
        # Use resolved query for intent classification
        intent_query = resolved_query
        
        # 11. AI-powered intent classification
        if self.ai_service:
            try:
                intent_info = self.ai_service.classify_intent_with_ai(intent_query, context_info)
                intent = intent_info['intent']
                print(f"🤖 AI Intent: {intent} (confidence: {intent_info['confidence']:.2f})")
            except Exception as e:
                print(f"⚠️ AI intent classification failed: {e}")
                intent_info = {'intent': self.classify_medical_intent(intent_query), 'confidence': 0.5}
                intent = intent_info['intent']
        else:
            # Fallback to rule-based
            intent = self.classify_medical_intent(intent_query)
            intent_info = {'intent': intent, 'confidence': 0.5}
        
        # 12. Ultra-fast search with multiple strategies
        search_start_time = time.time()
        search_results = []
        search_method = "unknown"
        

        search_results = search_medical_symptoms_and_diseases(search_query, top_k=5)
        search_time = time.time() - search_start_time
        search_method = "fallback_semantic"
        print(f"🔄 Fallback semantic: {len(search_results)} results in {search_time:.2f}s")
        print(search_results)
        self.stats['search_times'].append(search_time)
        
        # 13. AI-powered response generation
        response_start_time = time.time()
        response_data = {
            "intent_info" : intent_info,
            "intent": intent,  # ✅ intent đã là string rồi, không cần ['intent']
            "confidence": intent_info['confidence'],  # ✅ confidence nằm trong intent_info
            "sources": search_results,
            "search_time": search_time,
            "total_time": time.time() - total_start_time,
            "session_id": session_id,
            "context_info": context_info
        }
        return response_data
    
    def _get_optimizations_used(self):
        """Get list of active optimizations"""
        optimizations = []
        
        if self.fast_hybrid_engine:
            optimizations.append('ultra_fast_hybrid_search')
        if self.smart_cache:
            optimizations.append('advanced_multi_level_caching')
        if self.parallel_extractor:
            optimizations.append('parallel_entity_extraction')
        if self.query_compressor:
            optimizations.append('intelligent_query_compression')
        if self.hybrid_search_engine:
            optimizations.append('standard_hybrid_search')
        if self.search_quality_enhancer:
            optimizations.append('enhanced_search_quality')
        if self.medical_ner:
            optimizations.append('medical_ner')
        if self.confidence_calculator:
            optimizations.append('enhanced_confidence_scoring')
        if self.ai_service:
            optimizations.append('ai_powered_intent_and_response')
        
        return optimizations
    
    def _get_performance_grade(self, response_time):
        """Get performance grade based on response time"""
        if response_time < 1.0:
            return 'A+ (Excellent < 1s)'
        elif response_time < 2.0:
            return 'A (Very Good < 2s)'
        elif response_time < 3.0:
            return 'B (Good < 3s)'
        elif response_time < 5.0:
            return 'C (Acceptable < 5s)'
        else:
            return 'D (Needs Improvement)'

    def get_chatbot_stats(self):
        """Get comprehensive ultra-fast chatbot statistics"""
        total_queries = self.stats['total_queries']
        avg_search_time = sum(self.stats['search_times']) / max(1, len(self.stats['search_times']))
        avg_response_time = sum(self.stats['response_times']) / max(1, len(self.stats['response_times']))
        
        stats = {
            # Basic stats
            'total_queries': total_queries,
            'cache_hits': self.stats['cache_hits'],
            'cache_hit_rate': self.stats['cache_hits'] / max(1, total_queries),
            'cache_size': len(self.answer_cache),
            'active_sessions': len(self.conversation_history),
            'avg_search_time': avg_search_time,
            'avg_response_time': avg_response_time,
            
            # Ultra-fast performance stats
            'ultra_fast_performance': {
                'sub_3s_responses': self.ultra_fast_stats['sub_3s_responses'],
                'sub_3s_success_rate': self.ultra_fast_stats['sub_3s_responses'] / max(1, total_queries),
                'avg_total_time': avg_search_time + avg_response_time,
                'performance_grade': self._get_performance_grade(avg_search_time + avg_response_time),
                'optimization_wins': self.ultra_fast_stats['optimization_wins']
            },
            
            # System availability
            'systems_available': {
                'fast_hybrid_search': bool(self.fast_hybrid_engine),
                'advanced_caching': bool(self.smart_cache),
                'async_processing': bool(self.parallel_extractor),
                'query_compression': bool(self.query_compressor),
                'standard_hybrid_search': bool(self.hybrid_search_engine),
                'enhanced_search_quality': bool(self.search_quality_enhancer),
                'medical_ner': bool(self.medical_ner),
                'enhanced_confidence': bool(self.confidence_calculator),
                'ai_service': bool(self.ai_service),
                'query_transformation': QUERY_TRANSFORM_AVAILABLE,
                'structured_extraction': EXTRACTION_AVAILABLE,
                'medical_logging': LOGGING_AVAILABLE
            },
            
            # Active optimizations
            'active_optimizations': self._get_optimizations_used(),
            
            # Legacy features for compatibility
            'features': [
                'Ultra-Fast Hybrid Search',
                'Advanced Multi-Level Caching',
                'Parallel Processing',
                'Query Compression',
                'Enhanced Search Quality',
                'Medical NER',
                'Enhanced Confidence Scoring',
                'AI-Powered Intent & Response (OpenRouter DeepSeek)',
                'Vietnamese Enhancement', 
                'Conversation Context',
                'Query Transformation' if QUERY_TRANSFORM_AVAILABLE else None,
                'Structured Extraction' if EXTRACTION_AVAILABLE else None,
                'Medical Logging' if LOGGING_AVAILABLE else None
            ]
        }
        
        # Remove None values from features
        stats['features'] = [f for f in stats['features'] if f is not None]
        
        return stats

# Initialize enhanced chatbot
chatbot = EnhancedMedicalChatbot()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Enhanced Medical AI RAG Chatbot',
        'version': '2.0.0',
        'features': chatbot.get_chatbot_stats()['features']
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Enhanced chat endpoint"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        session_id = data.get('session_id')
        
        # Get response from chatbot
        response = chatbot.chat(query, session_id)
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/chat/stream', methods=['POST'])
def chat_stream():
    """Streaming chat endpoint"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        query = data['query'].strip()
        session_id = data.get('session_id')
        
        # ✅ Fixed: Sử dụng đúng tên method
        response = chatbot.semantic_search(query, session_id)
        intent_info = response['intent_info']
        intent = intent_info['intent']
        confidence = response['confidence']
        search_results = response['sources']
        search_time = response['search_time']
        total_time = response['total_time']
        session_id = response['session_id']
        context_info = response['context_info']
        
        # Generate streaming response
        def generate_stream():
            try:
                full_answer_parts = []  # ✅ Collect chunks to build full answer
                
                for chunk in chatbot.ai_service.generate_medical_response(
                    query, search_results, intent_info, context_info, stream=True
                ):
                    if chunk:
                        # ✅ Transform data to match frontend format
                        transformed_chunk = None
                        
                        if chunk.get('type') == 'chunk' and chunk.get('content'):
                            # Transform chunk data for frontend
                            full_answer_parts.append(chunk['content'])
                            transformed_chunk = {
                                'chunk': chunk['content'],  # ✅ 'content' → 'chunk' 
                                'word_index': 0,
                                'session_id': session_id
                            }
                            # ✅ Ensure chunk data is JSON serializable
                            transformed_chunk = ensure_json_serializable(transformed_chunk)
                            
                        elif chunk.get('type') == 'final':
                            # Transform final data for frontend
                            if chunk.get('response'):
                                full_answer_parts.append(chunk['response'])
                            
                            # ✅ Transform sources format
                            transformed_sources = []
                            for source in search_results:
                                metadata = source.get('metadata', {})
                                transformed_sources.append({
                                    'title': metadata.get('entity_name', 'Unknown Medical Entity'),
                                    'url': metadata.get('browser_url', ''),
                                    'content': metadata.get('description', ''),
                                    'confidence': source.get('relevance_score', source.get('semantic_score', 0))
                                })
                            
                            transformed_chunk = {
                'type': 'final',
                                'confidence': confidence,
                                'sources': transformed_sources,
                                'processing_time': chunk.get('response_time', total_time),
                                'search_time': search_time,
                                'session_id': session_id,
                                'intent': intent
                            }
                            
                            # ✅ Ensure all data is JSON serializable
                            transformed_chunk = ensure_json_serializable(transformed_chunk)
                        
                        if transformed_chunk:
                            yield f"data: {json.dumps(transformed_chunk)}\n\n"
                
                # ✅ Build complete answer from collected parts
                full_answer = ''.join(full_answer_parts) if full_answer_parts else "AI response generated"
                
                # Save to conversation history  
                conversation_data = {
                    'timestamp': datetime.now().isoformat(),
                    'user_query': query,
                    'response': full_answer,
                    'confidence': confidence,
                    'sources_count': len(search_results),
                    'intent': intent,
                    'search_time': search_time,
                    'total_time': total_time
                }
                # ✅ Ensure conversation data is JSON serializable
                conversation_data = ensure_json_serializable(conversation_data)
                chatbot.conversation_history[session_id]['messages'].append(conversation_data)
                
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                print(f"❌ Stream generation error: {e}")
                # ✅ Send error in format frontend expects
                error_chunk = {
                    'type': 'error',
                    'error': str(e),
                    'session_id': session_id
                }
                # ✅ Ensure error data is JSON serializable
                error_chunk = ensure_json_serializable(error_chunk)
                yield f"data: {json.dumps(error_chunk)}\n\n"
        
        return Response(
            stream_with_context(generate_stream()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type'
            }
        )
        
    except Exception as e:
        print(f"❌ Stream error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/medical_stats', methods=['GET'])
def medical_stats():
    """Enhanced medical statistics endpoint"""
    try:
        # Get base medical stats
        stats = get_medical_statistics()
        
        # Add enhanced chatbot stats
        chatbot_stats = chatbot.get_chatbot_stats()
        stats.update({
            'enhanced_chatbot': chatbot_stats,
            'model': 'all-MiniLM-L6-v2',
            'data_source': 'WHO ICD-11 API Enhanced'
        })
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get medical statistics',
            'message': str(e)
        }), 500

@app.route('/session/<session_id>', methods=['GET'])
def get_session_info(session_id):
    """Get session information"""
    try:
        if session_id not in chatbot.conversation_history:
            return jsonify({'error': 'Session not found'}), 404
        
        session = chatbot.conversation_history[session_id]
        return jsonify({
            'session_id': session_id,
            'created_at': session['created_at'].isoformat(),
            'last_activity': session['last_activity'].isoformat(),
            'message_count': len(session['messages']),
            'messages': session['messages']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Get cache statistics"""
    return jsonify({
        'cache_size': len(chatbot.answer_cache),
        'max_cache_size': chatbot.max_cache_size,
        'cache_hit_rate': chatbot.stats['cache_hits'] / max(1, chatbot.stats['total_queries']),
        'total_queries': chatbot.stats['total_queries'],
        'cache_hits': chatbot.stats['cache_hits']
    })

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear response cache"""
    chatbot.answer_cache.clear()
    if chatbot.smart_cache:
        chatbot.smart_cache.clear_cache()
    return jsonify({'message': 'All caches cleared successfully'})

@app.route('/ultra_fast_chat', methods=['POST'])
def ultra_fast_chat():
    """Ultra-fast chat endpoint with aggressive optimizations"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400
        
        query = data['query'].strip()
        if not query:
            return jsonify({'error': 'Empty query'}), 400
        
        session_id = data.get('session_id')
        
        # Use the same chat function but emphasize ultra-fast features
        response = chatbot.chat(query, session_id)
        
        # Add ultra-fast specific metadata
        response['endpoint'] = 'ultra_fast_chat'
        response['target_performance'] = '< 3 seconds'
        
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ Ultra-fast chat error: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/performance_stats', methods=['GET'])
def performance_stats():
    """Get detailed performance statistics"""
    try:
        stats = chatbot.get_chatbot_stats()
        
        # Add additional performance insights
        performance_insights = []
        
        ultra_perf = stats['ultra_fast_performance']
        if ultra_perf['sub_3s_success_rate'] > 0.8:
            performance_insights.append("🏆 Excellent performance - Meeting sub-3s target")
        elif ultra_perf['sub_3s_success_rate'] > 0.6:
            performance_insights.append("✅ Good performance - Close to target")
        else:
            performance_insights.append("⚠️ Performance needs improvement")
        
        if stats['cache_hit_rate'] > 0.3:
            performance_insights.append("💾 Cache working effectively")
        
        active_opts = len(stats['active_optimizations'])
        if active_opts >= 6:
            performance_insights.append(f"🚀 All optimizations active ({active_opts})")
        elif active_opts >= 4:
            performance_insights.append(f"⚡ Most optimizations active ({active_opts})")
        else:
            performance_insights.append(f"⚠️ Some optimizations missing ({active_opts})")
        
        stats['performance_insights'] = performance_insights
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get performance statistics',
            'message': str(e)
        }), 500

@app.route('/ai_stats', methods=['GET'])
def ai_stats():
    """Get AI service statistics"""
    try:
        if not chatbot.ai_service:
            return jsonify({
                'error': 'AI service not available',
                'status': 'disabled'
            }), 404
        
        ai_stats = chatbot.ai_service.get_ai_stats()
        return jsonify(ai_stats)
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to get AI statistics',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("🏥 ULTRA-FAST ENHANCED MEDICAL AI RAG CHATBOT")
    print("=" * 80)
    print("🤖 Model: all-MiniLM-L6-v2 với Vietnamese enhancement")
    print("🔍 RAG: Ultra-Fast Multi-Strategy Search")
    print("🎯 Target: < 3 seconds response time")
    print()
    
    # Show system status
    stats = chatbot.get_chatbot_stats()
    systems = stats['systems_available']
    
    print("🚀 OPTIMIZATION SYSTEMS:")
    print(f"   {'✅' if systems['fast_hybrid_search'] else '❌'} Ultra-Fast Hybrid Search")
    print(f"   {'✅' if systems['advanced_caching'] else '❌'} Advanced Multi-Level Caching")
    print(f"   {'✅' if systems['async_processing'] else '❌'} Parallel Async Processing")
    print(f"   {'✅' if systems['query_compression'] else '❌'} Intelligent Query Compression")
    print(f"   {'✅' if systems['enhanced_search_quality'] else '❌'} Enhanced Search Quality")
    print(f"   {'✅' if systems['medical_ner'] else '❌'} Medical NER")
    print(f"   {'✅' if systems['enhanced_confidence'] else '❌'} Enhanced Confidence Scoring")
    print(f"   {'✅' if systems['ai_service'] else '❌'} AI Service (OpenRouter DeepSeek)")
    print()
    
    print("🔥 ACTIVE FEATURES:")
    for feature in stats['features']:
        print(f"   ✅ {feature}")
    print()
    
    active_opts = len(stats['active_optimizations'])
    total_opts = 8  # Total possible optimizations
    
    print(f"⚡ PERFORMANCE STATUS:")
    print(f"   🎯 Target: < 3s response time")
    print(f"   🚀 Optimizations: {active_opts}/{total_opts} active")
    print(f"   💾 Caching: {'Advanced + Simple' if systems['advanced_caching'] else 'Simple only'}")
    print(f"   🔍 Search: {'Ultra-Fast Multi-Strategy' if systems['fast_hybrid_search'] else 'Standard'}")
    print()
    
    print("📡 ENDPOINTS:")
    print("   📬 /chat - Standard enhanced chat")
    print("   🚀 /ultra_fast_chat - Ultra-fast optimized chat")
    print("   📊 /performance_stats - Detailed performance metrics")
    print("   🩺 /medical_stats - Medical system statistics")
    print("   🤖 /ai_stats - AI service statistics")
    print()
    
    print("=" * 80)
    print("🚀 Starting Ultra-Fast Enhanced Medical Chatbot Server...")
    print("🎯 Ready for sub-3s medical consultations!")
    
    app.run(debug=False, host='0.0.0.0', port=5001, threaded=True)  # Optimized for performance

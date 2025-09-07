#!/usr/bin/env python3
"""
Ultra-Fast Medical Chatbot - Target < 3s response time
AI RAG Chatbot y tế với tốc độ tối ưu
"""
import time
import hashlib
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json

# Import core modules
from medical_rag_utils import (
    load_medical_data,
    search_medical_symptoms_and_diseases,
    classify_medical_query_intent, 
    create_medical_diagnostic_context,
    improve_vietnamese_query
)

# Import ultra-fast optimization modules
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

try:
    from enhanced_confidence import get_confidence_calculator
    ENHANCED_CONFIDENCE_AVAILABLE = True
except ImportError:
    print("⚠️ Enhanced confidence not available")
    ENHANCED_CONFIDENCE_AVAILABLE = False

try:
    from medical_ner import get_medical_ner
    NER_AVAILABLE = True
except ImportError:
    print("⚠️ Medical NER not available")
    NER_AVAILABLE = False

app = Flask(__name__)
CORS(app)

class UltraFastMedicalChatbot:
    """Ultra-fast medical chatbot với sub-3s response time"""
    
    def __init__(self):
        # Performance tracking
        self.stats = {
            'total_queries': 0,
            'avg_response_time': 0.0,
            'sub_3s_responses': 0,
            'cache_hits': 0,
            'optimization_wins': {
                'fast_hybrid': 0,
                'advanced_cache': 0,
                'async_processing': 0,
                'query_compression': 0
            }
        }
        
        # Session management (lightweight)
        self.sessions = {}
        self.session_timeout = 1800  # 30 minutes
        
        # Initialize all optimization systems
        self._init_ultra_fast_systems()
    
    def _init_ultra_fast_systems(self):
        """Initialize all ultra-fast optimization systems"""
        print("🚀 Initializing Ultra-Fast Medical Chatbot...")
        start_time = time.time()
        
        # 1. Fast Hybrid Search
        if FAST_HYBRID_AVAILABLE:
            try:
                print("🔄 Loading fast hybrid search...")
                medical_data = load_medical_data()
                self.fast_hybrid_engine = get_fast_hybrid_search_engine(
                    chunks_data=medical_data,
                    medical_rag_utils=None  # Will use function directly
                )
                print("✅ Fast hybrid search ready")
                self.hybrid_available = True
            except Exception as e:
                print(f"⚠️ Fast hybrid search failed: {e}")
                self.hybrid_available = False
        else:
            self.hybrid_available = False
        
        # 2. Advanced Caching
        if ADVANCED_CACHE_AVAILABLE:
            try:
                self.smart_cache = get_smart_query_cache()
                self.result_cache = get_result_cache()
                print("✅ Advanced caching ready")
                self.cache_available = True
            except Exception as e:
                print(f"⚠️ Advanced caching failed: {e}")
                self.cache_available = False
        else:
            self.cache_available = False
        
        # 3. Async Processing
        if ASYNC_PROCESSOR_AVAILABLE:
            try:
                # Initialize with NER if available
                ner_models = []
                if NER_AVAILABLE:
                    ner_models = [get_medical_ner()]
                
                self.parallel_extractor = get_parallel_entity_extractor(ner_models)
                self.parallel_search = get_parallel_search_processor()
                self.async_generator = get_async_response_generator()
                print("✅ Async processing ready")
                self.async_available = True
            except Exception as e:
                print(f"⚠️ Async processing failed: {e}")
                self.async_available = False
        else:
            self.async_available = False
        
        # 4. Query Compression
        if QUERY_COMPRESSION_AVAILABLE:
            try:
                self.query_compressor = get_query_compressor()
                print("✅ Query compression ready")
                self.compression_available = True
            except Exception as e:
                print(f"⚠️ Query compression failed: {e}")
                self.compression_available = False
        else:
            self.compression_available = False
        
        # 5. Enhanced Confidence (optional for speed)
        if ENHANCED_CONFIDENCE_AVAILABLE:
            try:
                self.confidence_calculator = get_confidence_calculator()
                self.enhanced_confidence_available = True
            except Exception as e:
                print(f"⚠️ Enhanced confidence failed: {e}")
                self.enhanced_confidence_available = False
        else:
            self.enhanced_confidence_available = False
        
        init_time = time.time() - start_time
        print(f"🎯 Ultra-fast systems initialized in {init_time:.2f}s")
        print(f"🔥 Target: < 3s response time")
    
    def ultra_fast_chat(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """Ultra-fast chat with aggressive optimizations"""
        total_start_time = time.time()
        self.stats['total_queries'] += 1
        
        # Stage 1: Fast cache check (Target: 0.1s)
        cache_start = time.time()
        cached_result = self._ultra_fast_cache_check(query, session_id)
        if cached_result:
            self.stats['cache_hits'] += 1
            self.stats['optimization_wins']['advanced_cache'] += 1
            cache_time = time.time() - cache_start
            
            # Update response metadata
            cached_result['response_metadata']['from_cache'] = True
            cached_result['response_metadata']['cache_time'] = cache_time
            cached_result['response_metadata']['total_time'] = time.time() - total_start_time
            
            return cached_result
        
        cache_time = time.time() - cache_start
        
        # Stage 2: Query compression (Target: 0.2s)
        compression_start = time.time()
        compressed_query = self._ultra_fast_query_compression(query)
        compression_time = time.time() - compression_start
        
        # Stage 3: Ultra-fast search (Target: 1.5s)
        search_start = time.time()
        search_results = self._ultra_fast_search(compressed_query.compressed, query)
        search_time = time.time() - search_start
        
        # Stage 4: Fast response generation (Target: 1.0s)
        response_start = time.time()
        response = self._ultra_fast_response_generation(
            search_results, query, compressed_query
        )
        response_time = time.time() - response_start
        
        # Stage 5: Fast confidence calculation (Target: 0.2s)
        confidence_start = time.time()
        confidence = self._ultra_fast_confidence(search_results, query)
        confidence_time = time.time() - confidence_start
        
        # Build final response
        total_time = time.time() - total_start_time
        
        final_response = {
            'answer': response,
            'confidence': confidence,
            'sources': search_results[:3],  # Top 3 sources only
            'query_info': {
                'original': query,
                'compressed': compressed_query.compressed,
                'compression_ratio': compressed_query.compression_ratio,
                'keywords': compressed_query.keywords[:5]  # Top 5 keywords
            },
            'response_metadata': {
                'total_time': total_time,
                'cache_time': cache_time,
                'compression_time': compression_time,
                'search_time': search_time,
                'response_time': response_time,
                'confidence_time': confidence_time,
                'from_cache': False,
                'optimizations_used': self._get_optimizations_used()
            }
        }
        
        # Cache successful result
        if self.cache_available and total_time < 5.0:  # Only cache fast responses
            self._cache_response(query, session_id, final_response)
        
        # Update statistics
        self._update_performance_stats(total_time)
        
        return final_response
    
    def _ultra_fast_cache_check(self, query: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Ultra-fast cache check with multiple strategies"""
        if not self.cache_available:
            return None
        
        try:
            # Get session context for cache key
            session_context = self._get_lightweight_session_context(session_id)
            
            # Check smart query cache
            cached_result, cache_level = self.smart_cache.get_cached_result(
                query, context=session_context
            )
            
            if cached_result:
                return cached_result
            
            return None
        
        except Exception as e:
            print(f"⚠️ Cache check failed: {e}")
            return None
    
    def _ultra_fast_query_compression(self, query: str):
        """Ultra-fast query compression"""
        if not self.compression_available:
            # Fallback simple compression
            return type('CompressedQuery', (), {
                'compressed': query[:50],  # Simple truncation
                'compression_ratio': min(50 / len(query), 1.0),
                'keywords': query.split()[:5]
            })()
        
        try:
            compressed = self.query_compressor.compress_query(query, target_length=40)
            self.stats['optimization_wins']['query_compression'] += 1
            return compressed
        
        except Exception as e:
            print(f"⚠️ Query compression failed: {e}")
            # Fallback
            return type('CompressedQuery', (), {
                'compressed': query,
                'compression_ratio': 1.0,
                'keywords': query.split()[:5]
            })()
    
    def _ultra_fast_search(self, compressed_query: str, original_query: str) -> List[Dict[str, Any]]:
        """Ultra-fast search with multiple optimization strategies"""
        
        # Strategy 1: Fast hybrid search (if available)
        if self.hybrid_available:
            try:
                search_start = time.time()
                results = self.fast_hybrid_engine.fast_hybrid_search(
                    compressed_query, top_k=5, use_cache=True
                )
                search_time = time.time() - search_start
                
                if results and search_time < 2.0:  # Good performance
                    self.stats['optimization_wins']['fast_hybrid'] += 1
                    return results
            
            except Exception as e:
                print(f"⚠️ Fast hybrid search failed: {e}")
        
        # Strategy 2: Parallel search (if available)
        if self.async_available:
            try:
                search_results = self.parallel_search.parallel_search(
                    compressed_query, 
                    search_methods=['semantic'], 
                    top_k=5
                )
                
                if search_results.get('semantic'):
                    self.stats['optimization_wins']['async_processing'] += 1
                    return search_results['semantic']
            
            except Exception as e:
                print(f"⚠️ Parallel search failed: {e}")
        
        # Strategy 3: Fallback to standard semantic search
        try:
            enhanced_query = improve_vietnamese_query(compressed_query)
            results = search_medical_symptoms_and_diseases(enhanced_query, top_k=5)
            return results
        
        except Exception as e:
            print(f"⚠️ Fallback search failed: {e}")
            return []
    
    def _ultra_fast_response_generation(self, search_results: List[Dict], 
                                      query: str, compressed_query) -> str:
        """Ultra-fast response generation"""
        
        if not search_results:
            return "Xin lỗi, tôi không tìm thấy thông tin phù hợp. Vui lòng tham khảo ý kiến bác sĩ."
        
        # Fast response using async generator (if available)
        if self.async_available:
            try:
                # Create quick context from top results
                context = ' '.join([result.get('text', '')[:200] for result in search_results[:2]])
                response = self.async_generator.generate_response_async(
                    context, query, use_cache=True
                )
                if response:
                    return response
            except Exception as e:
                print(f"⚠️ Async response generation failed: {e}")
        
        # Fallback to standard response generation
        try:
            context = create_medical_diagnostic_context(search_results[:3], query)
            
            # Simple template-based response for speed
            if 'đau đầu' in query.lower():
                return f"Về đau đầu: {context[:300]}... Khuyến nghị thăm khám bác sĩ để được tư vấn chính xác."
            elif 'sốt' in query.lower():
                return f"Về sốt: {context[:300]}... Theo dõi nhiệt độ và tham khảo ý kiến y tế nếu cần."
            else:
                return f"Thông tin y tế: {context[:400]}... Vui lòng tham khảo chuyên gia để được tư vấn phù hợp."
        
        except Exception as e:
            print(f"⚠️ Response generation failed: {e}")
            return "Tôi cần thêm thông tin để đưa ra tư vấn chính xác. Vui lòng mô tả chi tiết hơn."
    
    def _ultra_fast_confidence(self, search_results: List[Dict], query: str) -> float:
        """Ultra-fast confidence calculation"""
        
        if not search_results:
            return 0.0
        
        # Fast confidence based on top result only
        top_result = search_results[0]
        base_confidence = top_result.get('relevance_score', 
                                       top_result.get('semantic_score', 0.5))
        
        # Quick adjustments
        if len(search_results) >= 3:
            base_confidence *= 1.1  # Multiple good results
        
        if any(term in query.lower() for term in ['đau đầu', 'sốt', 'tiểu đường']):
            base_confidence *= 1.05  # Common medical terms
        
        return min(base_confidence, 1.0)
    
    def _get_lightweight_session_context(self, session_id: str) -> Dict[str, Any]:
        """Get lightweight session context for caching"""
        if not session_id or session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        return {
            'has_history': len(session.get('messages', [])) > 0,
            'recent_queries': len(session.get('messages', []))
        }
    
    def _cache_response(self, query: str, session_id: str, response: Dict[str, Any]):
        """Cache response for future use"""
        if not self.cache_available:
            return
        
        try:
            session_context = self._get_lightweight_session_context(session_id)
            self.smart_cache.cache_result(
                query, response, 
                context=session_context, 
                ttl=1800  # 30 minutes
            )
        except Exception as e:
            print(f"⚠️ Response caching failed: {e}")
    
    def _get_optimizations_used(self) -> List[str]:
        """Get list of optimizations used"""
        optimizations = []
        
        if self.hybrid_available:
            optimizations.append('fast_hybrid_search')
        if self.cache_available:
            optimizations.append('advanced_caching')
        if self.async_available:
            optimizations.append('async_processing')
        if self.compression_available:
            optimizations.append('query_compression')
        
        return optimizations
    
    def _update_performance_stats(self, response_time: float):
        """Update performance statistics"""
        # Update average response time
        total_queries = self.stats['total_queries']
        current_avg = self.stats['avg_response_time']
        
        self.stats['avg_response_time'] = (
            (current_avg * (total_queries - 1) + response_time) / total_queries
        )
        
        # Track sub-3s responses
        if response_time < 3.0:
            self.stats['sub_3s_responses'] += 1
    
    def get_ultra_fast_stats(self) -> Dict[str, Any]:
        """Get ultra-fast performance statistics"""
        total_queries = self.stats['total_queries']
        
        return {
            'total_queries': total_queries,
            'avg_response_time': self.stats['avg_response_time'],
            'sub_3s_success_rate': (
                self.stats['sub_3s_responses'] / total_queries 
                if total_queries > 0 else 0
            ),
            'cache_hit_rate': (
                self.stats['cache_hits'] / total_queries 
                if total_queries > 0 else 0
            ),
            'optimization_wins': self.stats['optimization_wins'],
            'systems_available': {
                'fast_hybrid': self.hybrid_available,
                'advanced_cache': self.cache_available,
                'async_processing': self.async_available,
                'query_compression': self.compression_available,
                'enhanced_confidence': self.enhanced_confidence_available
            },
            'performance_grade': self._get_performance_grade()
        }
    
    def _get_performance_grade(self) -> str:
        """Get performance grade based on metrics"""
        if self.stats['total_queries'] == 0:
            return 'No data'
        
        avg_time = self.stats['avg_response_time']
        sub_3s_rate = self.stats['sub_3s_responses'] / self.stats['total_queries']
        
        if avg_time < 2.0 and sub_3s_rate > 0.9:
            return 'A+ (Excellent)'
        elif avg_time < 3.0 and sub_3s_rate > 0.8:
            return 'A (Very Good)'
        elif avg_time < 4.0 and sub_3s_rate > 0.6:
            return 'B (Good)'
        elif avg_time < 5.0:
            return 'C (Acceptable)'
        else:
            return 'D (Needs Improvement)'

# Initialize ultra-fast chatbot
ultra_fast_chatbot = UltraFastMedicalChatbot()

@app.route('/ultra_fast_chat', methods=['POST'])
def ultra_fast_chat():
    """Ultra-fast chat endpoint"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Process with ultra-fast chatbot
        result = ultra_fast_chatbot.ultra_fast_chat(query, session_id)
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Ultra-fast chat error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/ultra_fast_stats', methods=['GET'])
def ultra_fast_stats():
    """Get ultra-fast performance statistics"""
    try:
        stats = ultra_fast_chatbot.get_ultra_fast_stats()
        return jsonify(stats)
    
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return jsonify({'error': 'Failed to get stats'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'chatbot': 'ultra_fast_medical_chatbot',
        'timestamp': time.time()
    })

if __name__ == '__main__':
    print("🚀 Starting Ultra-Fast Medical Chatbot...")
    print("🎯 Target: < 3s response time")
    print("🔥 All optimizations active!")
    print("💫 Ready for production deployment!")
    
    app.run(
        host='0.0.0.0',
        port=5002,  # Different port to avoid conflicts
        debug=False,  # Disable debug for max performance
        threaded=True
    )

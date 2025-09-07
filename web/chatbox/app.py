from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from config import init_app_context, DB_CONFIG, client, APP_CONTEXT
import uuid
from collections import deque

from medical_rag_utils import (
    search_medical_symptoms_and_diseases,
    search_symptoms_only,
    search_diseases_only,
    create_medical_diagnostic_context,
    create_medical_consultation_context,
    classify_medical_query_intent,
    get_medical_statistics
)
from hybrid_search import get_hybrid_search_engine
from query_transformation import transform_medical_query
from structured_extraction import extract_medical_structure
from medical_logging import log_query, log_search, log_llm, log_extraction, log_error, get_stats
import time
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, origins=['http://localhost:5173'])

# Khởi tạo ứng dụng
init_app_context(app)

# Biến toàn cục
answer_cache = {}

conversation_sessions = {}  # {session_id: {"history": deque, "last_activity": datetime}}
MAX_HISTORY_LENGTH = 20     # Giới hạn số tin nhắn trong lịch sử
SESSION_TIMEOUT = 30 * 60   # 30 phút timeout

# Thêm hàm helper để quản lý session
def get_or_create_session(session_id=None):
    """Lấy hoặc tạo session mới"""
    if not session_id:
        session_id = str(uuid.uuid4())
    
    current_time = datetime.now()
    
    # Làm sạch các session hết hạn
    expired_sessions = []
    for sid, session_data in conversation_sessions.items():
        if (current_time - session_data["last_activity"]).seconds > SESSION_TIMEOUT:
            expired_sessions.append(sid)
    
    for sid in expired_sessions:
        del conversation_sessions[sid]
    
    # Tạo session mới nếu chưa tồn tại
    if session_id not in conversation_sessions:
        conversation_sessions[session_id] = {
            "history": deque(maxlen=MAX_HISTORY_LENGTH),
            "last_activity": current_time
        }
    else:
        conversation_sessions[session_id]["last_activity"] = current_time
    
    return session_id

def add_to_conversation_history(session_id, role, content):
    """Thêm tin nhắn vào lịch sử hội thoại"""
    if session_id in conversation_sessions:
        conversation_sessions[session_id]["history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

def get_conversation_context(session_id, max_messages=10):
    """Lấy ngữ cảnh hội thoại gần đây"""
    if session_id not in conversation_sessions:
        return []
    
    history = list(conversation_sessions[session_id]["history"])
    # Lấy max_messages tin nhắn gần nhất
    recent_history = history[-max_messages:] if len(history) > max_messages else history
    
    # Chuyển đổi format cho OpenAI API
    context_messages = []
    for msg in recent_history:
        context_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    return context_messages

@app.route('/ask', methods=['POST'])
def ask():
    user_query = request.json['query']
    session_id = request.json.get('session_id')  # Thêm session_id từ request
    
    # Tạo hoặc lấy session
    session_id = get_or_create_session(session_id)
    
    # Kiểm tra cache với session_id
    cache_key = f"{session_id}:{user_query}"
    if cache_key in answer_cache:
        def cached_response():
            cached_answer = answer_cache[cache_key]
            words = cached_answer.split(' ')
            for i in range(0, len(words), 2):
                chunk = ' '.join(words[i:i+2])
                if i + 2 < len(words):
                    chunk += ' '
                yield "data: " + json.dumps({
                    'chunk': chunk, 
                    'session_id': session_id
                }) + "\n\n"
                time.sleep(0.05)
            yield "data: [DONE]\n\n"
        
        return Response(cached_response(), mimetype='text/event-stream', 
                       headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'X-Accel-Buffering': 'no'})
    
    # Lấy ngữ cảnh hội thoại
    conversation_context = get_conversation_context(session_id, max_messages=6)
    print("conversation_context")
    print(conversation_context)
    
    # 1. Phân loại medical intent
    medical_intent = classify_medical_query_intent(user_query)
    print(f"📋 Medical intent: {medical_intent}")
    
    # 2. Transform query for better search
    try:
        query_transformation = transform_medical_query(user_query, conversation_context)
        print(f"🔄 Query transformed: {query_transformation['search_strategy']}")
    except Exception as e:
        print(f"⚠️ Query transformation error: {e}")
        query_transformation = {
            'original_query': user_query,
            'enriched_query': user_query,
            'sub_queries': [user_query],
            'search_strategy': 'default'
        }
    
    # 3. Perform hybrid search
    try:
        hybrid_engine = get_hybrid_search_engine()
        
        if hybrid_engine:
            # Get search weights based on strategy
            weights = query_transformation.get('search_strategy', 'general')
            if weights == 'emergency':
                semantic_weight, keyword_weight = 0.8, 0.2
            elif weights == 'multi_symptom':
                semantic_weight, keyword_weight = 0.6, 0.4
            elif weights == 'treatment_focused':
                semantic_weight, keyword_weight = 0.5, 0.5
            else:
                semantic_weight, keyword_weight = 0.7, 0.3
            
            # Perform hybrid search with multiple queries
            all_search_results = []
            
            # Search with original query
            main_results = hybrid_engine.hybrid_search(
                user_query, top_k=8, 
                semantic_weight=semantic_weight, 
                keyword_weight=keyword_weight
            )
            all_search_results.extend(main_results)
            
            # Search with enriched query if different
            enriched_query = query_transformation.get('enriched_query', '')
            if enriched_query and enriched_query != user_query:
                enriched_results = hybrid_engine.hybrid_search(
                    enriched_query, top_k=5,
                    semantic_weight=semantic_weight,
                    keyword_weight=keyword_weight
                )
                all_search_results.extend(enriched_results)
            
            # Search with sub-queries
            for sub_query in query_transformation.get('sub_queries', [])[:2]:
                if sub_query != user_query:
                    sub_results = hybrid_engine.hybrid_search(
                        sub_query, top_k=3,
                        semantic_weight=semantic_weight,
                        keyword_weight=keyword_weight
                    )
                    all_search_results.extend(sub_results)
            
            # Remove duplicates and keep top results
            seen_indices = set()
            unique_results = []
            for result in all_search_results:
                idx = result.get('index')
                if idx not in seen_indices:
                    seen_indices.add(idx)
                    unique_results.append(result)
            
            # Sort by hybrid score and take top 10
            search_results = sorted(unique_results, key=lambda x: x.get('hybrid_score', 0), reverse=True)[:10]
            
            print(f"🔍 Hybrid search found {len(search_results)} unique results")
            
        else:
            # Fallback to traditional search
            print("⚠️ Falling back to traditional search")
            search_results = search_medical_symptoms_and_diseases(user_query, top_k=8)
        
        # Create context for LLM
        if search_results:
            if medical_intent == "emergency":
                context = create_medical_diagnostic_context(search_results[:5], user_query)
                context += "\n\n⚠️ CẢNH BÁO: Đây có thể là tình huống khẩn cấp. Vui lòng liên hệ ngay với cơ sở y tế hoặc gọi 115!"
            else:
                context = create_medical_consultation_context(search_results[:8], medical_intent)
        else:
            context = "Không tìm thấy thông tin y tế phù hợp trong cơ sở dữ liệu."
        
    except Exception as e:
        print(f"❌ Hybrid search error: {e}")
        # Fallback to traditional search
        try:
            search_results = search_medical_symptoms_and_diseases(user_query, top_k=5)
            context = create_medical_consultation_context(search_results, medical_intent)
        except Exception as fallback_error:
            print(f"❌ Fallback search error: {fallback_error}")
            search_results = []
            context = "Xin lỗi, có lỗi xảy ra khi tìm kiếm thông tin y tế. Vui lòng thử lại hoặc liên hệ với bác sĩ."
    
    def generate():
        yield "data: " + json.dumps({'chunk': '', 'session_id': session_id}) + "\n\n"
        time.sleep(0.1)
        
        # Tạo system message cho medical consultation
        if medical_intent == "emergency":
            system_content = f"""Bạn là một trợ lý y tế thông minh và có trách nhiệm.
            
            ⚠️ TÌNH HUỐNG KHẨN CẤP ⚠️
            
            QUAN TRỌNG - XỬ LÝ NGỮ CẢNH:
            - Tham khảo cuộc hội thoại trước để hiểu đầy đủ tình trạng bệnh nhân
            - Ưu tiên đánh giá mức độ nghiêm trọng của triệu chứng
            - Đưa ra hướng dẫn cấp cứu phù hợp
            
            NHIỆM VỤ KHẨN CẤP:
            - Đánh giá nhanh mức độ nghiêm trọng của triệu chứng
            - Cung cấp hướng dẫn sơ cứu ban đầu (nếu phù hợp)
            - Khuyến cáo liên hệ ngay với cơ sở y tế
            - KHÔNG cố gắng chẩn đoán chính xác - chỉ phân tích sơ bộ
            
            HƯỚNG DẪN TRẢ LỜI:
            - Bắt đầu với: "⚠️ TÌNH HUỐNG KHẨN CẤP"
            - Đánh giá nhanh triệu chứng dựa trên thông tin y tế
            - Đưa ra hướng dẫn cấp cứu cơ bản (nếu có)
            - Kết thúc với: "🚨 LIÊN HỆ NGAY: 115 (Cấp cứu) hoặc đến bệnh viện gần nhất"
            
            THÔNG TIN Y TẾ LIÊN QUAN:
            {context}
            
            🏥 Hãy ưu tiên an toàn của bệnh nhân và khuyến cáo tìm kiếm sự trợ giúp y tế chuyên nghiệp ngay lập tức."""
            
        elif medical_intent == "symptom_inquiry":
            system_content = f"""Bạn là một trợ lý y tế thông minh, chuyên phân tích triệu chứng và hỗ trợ chẩn đoán sơ bộ.
            
            QUAN TRỌNG - XỬ LÝ NGỮ CẢNH:
            - Tham khảo cuộc hội thoại trước để hiểu đầy đủ các triệu chứng
            - Kết hợp các triệu chứng đã được mô tả để đưa ra đánh giá tổng thể
            - Hỏi thêm thông tin nếu cần thiết để chẩn đoán chính xác hơn
            
            NHIỆM VỤ CHÍNH:
            - Phân tích các triệu chứng được mô tả
            - Tìm kiếm các bệnh lý có thể liên quan
            - Đưa ra gợi ý về nguyên nhân có thể xảy ra
            - Tư vấn về việc có nên đi khám bác sĩ hay không
            
            HƯỚNG DẪN TRẢ LỜI:
            - Tóm tắt lại các triệu chứng đã được mô tả
            - Phân tích dựa trên kiến thức y tế từ ICD-11
            - Liệt kê các khả năng có thể xảy ra (từ nhẹ đến nặng)
            - Đưa ra lời khuyên về việc tìm kiếm sự chăm sóc y tế
            - Luôn nhấn mạnh rằng đây chỉ là tham khảo, không thay thế bác sĩ
            
            THÔNG TIN TRIỆU CHỨNG VÀ BỆNH LÝ LIÊN QUAN:
            {context}
            
            🩺 Lưu ý: Thông tin này chỉ mang tính chất tham khảo. Để có chẩn đoán chính xác, vui lòng thăm khám bác sĩ."""
            
        elif medical_intent == "disease_inquiry":
            system_content = f"""Bạn là một trợ lý y tế chuyên cung cấp thông tin về các bệnh lý và tình trạng sức khỏe.
            
            QUAN TRỌNG - XỬ LÝ NGỮ CẢNH:
            - Tham khảo cuộc hội thoại trước để hiểu rõ loại thông tin bệnh nhân quan tâm
            - Cung cấp thông tin phù hợp với mức độ hiểu biết của người hỏi
            - Liên kết với các triệu chứng đã thảo luận trước đó (nếu có)
            
            NHIỆM VỤ CHÍNH:
            - Giải thích về bệnh lý được hỏi
            - Cung cấp thông tin về nguyên nhân, triệu chứng
            - Mô tả quá trình phát triển của bệnh
            - Thông tin về các phương pháp chẩn đoán
            
            HƯỚNG DẪN TRẢ LỜI:
            - Định nghĩa rõ ràng về bệnh lý
            - Giải thích nguyên nhân gây bệnh
            - Mô tả các triệu chứng thường gặp
            - Thông tin về độ phổ biến và nhóm đối tượng dễ mắc
            - Đề cập đến các biến chứng có thể xảy ra
            - Khuyến cáo về việc phòng ngừa và theo dõi
            
            THÔNG TIN BỆNH LÝ TỪ ICD-11:
            {context}
            
            📚 Thông tin được cung cấp dựa trên tiêu chuẩn y tế quốc tế ICD-11. Luôn tham khảo ý kiến bác sĩ để có hướng dẫn cụ thể."""
            
        else:  # treatment_inquiry, prevention_inquiry, general_medical
            system_content = f"""Bạn là một trợ lý y tế hỗ trợ tư vấn sức khỏe tổng quát.
            
            QUAN TRỌNG - XỬ LÝ NGỮ CẢNH:
            - Tham khảo toàn bộ cuộc hội thoại để đưa ra tư vấn phù hợp
            - Kết nối thông tin với bệnh lý hoặc triệu chứng đã thảo luận
            - Cung cấp thông tin thực tế và có cơ sở khoa học
            
            NHIỆM VỤ CHÍNH:
            - Tư vấn về phòng ngừa bệnh tật
            - Cung cấp thông tin về lối sống lành mạnh
            - Hướng dẫn chăm sóc sức khỏe cơ bản
            - Giải đáp các thắc mắc y tế tổng quát
            
            HƯỚNG DẪN TRẢ LỜI:
            - Cung cấp thông tin dựa trên bằng chứng khoa học
            - Đưa ra lời khuyên thực tế và dễ thực hiện
            - Nhấn mạnh tầm quan trọng của việc khám sức khỏe định kỳ
            - Khuyến khích lối sống lành mạnh
            - Luôn khuyến cáo tham khảo ý kiến bác sĩ khi cần thiết
            
            THÔNG TIN Y TẾ LIÊN QUAN:
            {context}
            
            🌟 Sức khỏe là tài sản quý giá nhất. Hãy chăm sóc bản thân và đừng ngần ngại tìm kiếm sự trợ giúp y tế khi cần."""

        # Tạo prompt với lịch sử hội thoại
        messages = [{"role": "system", "content": system_content}]
        
        # Thêm lịch sử hội thoại vào prompt
        if conversation_context:
            messages.extend(conversation_context)
        
        # Thêm câu hỏi hiện tại
        messages.append({"role": "user", "content": user_query})
        
        try:
            stream = client.chat.completions.create(
                model="deepseek/deepseek-r1:free",
                messages=messages,
                stream=True,
                temperature=0.7,
                max_tokens=3000
            )
            
            full_answer = ""
            chunk_buffer = ""
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_answer += content
                    chunk_buffer += content
                    
                    if len(chunk_buffer) >= 10 or content in ['.', '!', '?', '\n']:
                        yield "data: " + json.dumps({
                            'chunk': chunk_buffer, 
                            'session_id': session_id
                        }) + "\n\n"
                        chunk_buffer = ""
                        time.sleep(0.03)
            
            if chunk_buffer:
                yield "data: " + json.dumps({
                    'chunk': chunk_buffer, 
                    'session_id': session_id
                }) + "\n\n"
            
            # 4. Extract structured information
            try:
                structured_response = extract_medical_structure(
                    search_results, user_query, medical_intent, full_answer
                )
                print(f"📊 Structured extraction completed: {structured_response['schema_type']}")
                
                # Send structured data as final chunk
                yield "data: " + json.dumps({
                    'structured_data': structured_response,
                    'session_id': session_id
                }) + "\n\n"
                
            except Exception as struct_error:
                print(f"⚠️ Structured extraction error: {struct_error}")
            
            # Lưu vào cache với session_id
            answer_cache[cache_key] = full_answer
            
            # Lưu vào lịch sử hội thoại
            add_to_conversation_history(session_id, "user", user_query)
            add_to_conversation_history(session_id, "assistant", full_answer)
            
            print("✅ Full Answer: " + full_answer[:200] + "...")
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            print("Error: " + str(e))
            yield "data: " + json.dumps({'error': str(e), 'session_id': session_id}) + "\n\n"
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream', 
                   headers={'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'X-Accel-Buffering': 'no', 
                           'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type'})

# Session management routes
@app.route('/session/new', methods=['POST'])
def create_new_session():
    """Tạo session mới"""
    session_id = get_or_create_session()
    return jsonify({
        'session_id': session_id,
        'message': 'Session mới đã được tạo'
    })

@app.route('/session/<session_id>/history', methods=['GET'])
def get_session_history(session_id):
    """Lấy lịch sử hội thoại của session"""
    if session_id not in conversation_sessions:
        return jsonify({'error': 'Session không tồn tại'}), 404
    
    history = list(conversation_sessions[session_id]["history"])
    return jsonify({
        'session_id': session_id,
        'history': history,
        'total_messages': len(history)
    })

@app.route('/session/<session_id>/clear', methods=['POST'])
def clear_session_history(session_id):
    """Xóa lịch sử hội thoại của session"""
    if session_id not in conversation_sessions:
        return jsonify({'error': 'Session không tồn tại'}), 404
    
    conversation_sessions[session_id]["history"].clear()
    return jsonify({
        'session_id': session_id,
        'message': 'Lịch sử hội thoại đã được xóa'
    })

@app.route('/sessions', methods=['GET'])
def get_all_sessions():
    """Lấy danh sách tất cả sessions"""
    current_time = datetime.now()
    sessions_info = []
    
    for session_id, session_data in conversation_sessions.items():
        last_activity = session_data["last_activity"]
        time_since_activity = (current_time - last_activity).seconds
        
        sessions_info.append({
            'session_id': session_id,
            'last_activity': last_activity.isoformat(),
            'messages_count': len(session_data["history"]),
            'time_since_activity_minutes': round(time_since_activity / 60, 1),
            'is_active': time_since_activity < SESSION_TIMEOUT
        })
    
    return jsonify({
        'total_sessions': len(sessions_info),
        'active_sessions': len([s for s in sessions_info if s['is_active']]),
        'sessions': sessions_info
    })

@app.route('/medical_stats', methods=['GET'])
def get_medical_stats():
    """
    Endpoint để lấy thống kê về medical knowledge base
    """
    try:
        stats = get_medical_statistics()
        
        if 'error' in stats:
            return jsonify({'error': stats['error']}), 404
        
        # Thêm thông tin chi tiết về categories
        formatted_categories = {}
        for category_id, category_info in stats.get('categories', {}).items():
            if isinstance(category_info, dict):
                formatted_categories[category_id] = {
                    'id': category_id,
                    'name': category_info.get('name', f'Category {category_id}'),
                    'count': category_info.get('count', 0)
                }
            else:
                formatted_categories[category_id] = {
                    'id': category_id,
                    'name': f'Category {category_id}',
                    'count': category_info
                }
        
        response_data = {
            'success': True,
            'total_chunks': stats.get('total_chunks', 0),
            'total_categories': stats.get('total_categories', 0),
            'chunks_with_icd_code': stats.get('has_icd_code', 0),
            'data_source': stats.get('data_source', 'WHO ICD-11 API'),
            'created_at': stats.get('created_at'),
            'categories': formatted_categories,
            'entity_types': stats.get('entity_types', {}),
            'coverage_percentage': round((stats.get('has_icd_code', 0) / max(stats.get('total_chunks', 1), 1)) * 100, 2)
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error getting medical statistics: {str(e)}'
        }), 500

@app.route('/medical_search', methods=['POST'])
def medical_search():
    """
    Endpoint chuyên dụng cho tìm kiếm y tế
    """
    try:
        data = request.json
        query = data.get('query', '')
        search_type = data.get('search_type', 'general')  # general, symptoms, diseases
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Phân loại intent
        medical_intent = classify_medical_query_intent(query)
        
        # Tìm kiếm dựa trên loại
        if search_type == 'symptoms':
            results = search_symptoms_only(query, top_k=top_k)
        elif search_type == 'diseases':
            results = search_diseases_only(query, top_k=top_k)
        else:
            results = search_medical_symptoms_and_diseases(query, top_k=top_k)
        
        # Format kết quả
        formatted_results = []
        for result in results:
            metadata = result['metadata']
            formatted_results.append({
                'entity_name': metadata.get('entity_name', 'Unknown'),
                'icd_code': metadata.get('icd_code'),
                'category_id': metadata.get('category_id'),
                'category_name': metadata.get('category_name'),
                'entity_type': metadata.get('entity_type'),
                'source_type': metadata.get('source_type'),
                'relevance_score': result['relevance_score'],
                'text_preview': result['text'][:200] + '...' if len(result['text']) > 200 else result['text']
            })
        
        return jsonify({
            'success': True,
            'query': query,
            'medical_intent': medical_intent,
            'search_type': search_type,
            'total_results': len(formatted_results),
            'results': formatted_results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Medical search error: {str(e)}'
        }), 500

@app.route('/ask_structured', methods=['POST'])
def ask_structured():
    """
    Enhanced medical consultation endpoint with structured response
    """
    try:
        data = request.json
        user_query = data.get('query', '')
        session_id = data.get('session_id')
        
        if not user_query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get or create session
        session_id = get_or_create_session(session_id)
        
        # Get conversation context
        conversation_context = get_conversation_context(session_id, max_messages=6)
        
        # 1. Classify medical intent
        medical_intent = classify_medical_query_intent(user_query)
        
        # 2. Transform query
        start_time = time.time()
        query_transformation = transform_medical_query(user_query, conversation_context)
        
        # Log the query request
        log_query(session_id, user_query, medical_intent, query_transformation)
        
        # 3. Hybrid search
        search_start_time = time.time()
        hybrid_engine = get_hybrid_search_engine()
        
        if hybrid_engine:
            # Determine search weights
            strategy = query_transformation.get('search_strategy', 'general')
            if strategy == 'emergency':
                semantic_weight, keyword_weight = 0.8, 0.2
            elif strategy == 'multi_symptom':
                semantic_weight, keyword_weight = 0.6, 0.4
            elif strategy == 'treatment_focused':
                semantic_weight, keyword_weight = 0.5, 0.5
            else:
                semantic_weight, keyword_weight = 0.7, 0.3
            
            # Perform search
            search_results = hybrid_engine.hybrid_search(
                user_query, top_k=10,
                semantic_weight=semantic_weight,
                keyword_weight=keyword_weight
            )
        else:
            # Fallback search
            search_results = search_medical_symptoms_and_diseases(user_query, top_k=8)
        
        # Log search performance
        search_time = time.time() - search_start_time
        search_method = "hybrid_search" if hybrid_engine else "fallback_search"
        top_scores = [r.get('hybrid_score', r.get('relevance_score', 0)) for r in search_results[:5]]
        log_search(session_id, search_method, user_query, len(search_results), search_time, top_scores)
        
        # 4. Generate LLM response
        llm_start_time = time.time()
        context = create_medical_consultation_context(search_results[:5], medical_intent)
        
        # Build system message
        if medical_intent == "emergency":
            system_content = f"""⚠️ TÌNH HUỐNG KHẨN CẤP ⚠️
            
Bạn là trợ lý y tế. Hãy đánh giá nhanh tình huống và đưa ra khuyến cáo cấp cứu.

THÔNG TIN Y TẾ: {context}

Trả lời ngắn gọn, tập trung vào:
1. Đánh giá mức độ nghiêm trọng
2. Hành động cần làm ngay
3. Khi nào cần gọi 115"""
        else:
            system_content = f"""Bạn là trợ lý y tế chuyên nghiệp.

THÔNG TIN Y TẾ: {context}

Hãy tư vấn dựa trên thông tin từ WHO ICD-11, đảm bảo:
- Chính xác về y khoa
- Dễ hiểu
- Khuyến cáo tham khảo bác sĩ khi cần"""
        
        # Generate response
        messages = [
            {"role": "system", "content": system_content}
        ]
        
        if conversation_context:
            messages.extend(conversation_context)
        
        messages.append({"role": "user", "content": user_query})
        
        response = client.chat.completions.create(
            model="deepseek/deepseek-r1:free",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        llm_response = response.choices[0].message.content
        
        # Log LLM interaction
        llm_time = time.time() - llm_start_time
        log_llm(session_id, user_query, llm_response, len(context), llm_time)
        
        # 5. Extract structured data
        extraction_start_time = time.time()
        structured_response = extract_medical_structure(
            search_results, user_query, medical_intent, llm_response
        )
        
        # Log structured extraction
        extraction_time = time.time() - extraction_start_time
        extraction_success = structured_response.get('data') is not None
        confidence_score = structured_response.get('confidence_score', 0.0)
        log_extraction(
            session_id, medical_intent, structured_response.get('schema_type', 'unknown'),
            extraction_success, confidence_score, extraction_time
        )
        
        # 6. Save to conversation history
        add_to_conversation_history(session_id, "user", user_query)
        add_to_conversation_history(session_id, "assistant", llm_response)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'query': user_query,
            'intent': medical_intent,
            'strategy': query_transformation.get('search_strategy'),
            'search_results_count': len(search_results),
            'llm_response': llm_response,
            'structured_data': structured_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Structured ask error: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Enhanced Medical Diagnosis Chatbot',
        'version': '2.0',
        'features': [
            'Hybrid Search (Semantic + BM25)',
            'Query Transformation',
            'Structured Data Extraction',
            'Source Citation',
            'Follow-up Suggestions'
        ],
        'timestamp': datetime.now().isoformat()
    })

@app.route('/suggestions/<intent>', methods=['POST'])
def get_follow_up_suggestions(intent):
    """
    Get follow-up question suggestions based on intent and conversation
    """
    try:
        data = request.json or {}
        current_topic = data.get('current_topic', '')
        
        suggestions_map = {
            'disease_inquiry': [
                f"Cách phòng ngừa {current_topic}",
                f"Triệu chứng của {current_topic}",
                f"Điều trị {current_topic} như thế nào",
                f"Khi nào cần đi khám bác sĩ về {current_topic}",
                f"Biến chứng của {current_topic}"
            ],
            'symptom_inquiry': [
                "Các bệnh có thể gây ra triệu chứng này",
                "Cách giảm nhẹ triệu chứng tại nhà", 
                "Khi nào cần đi cấp cứu",
                "Triệu chứng nào cần theo dõi thêm",
                "Xét nghiệm gì cần làm"
            ],
            'treatment_inquiry': [
                "Tác dụng phụ của điều trị này",
                "Thời gian điều trị bao lâu",
                "Cách theo dõi hiệu quả điều trị",
                "Phương pháp điều trị thay thế",
                "Chế độ ăn trong quá trình điều trị"
            ],
            'prevention_inquiry': [
                "Chế độ ăn phòng ngừa",
                "Bài tập thể dục phù hợp",
                "Tần suất khám sức khỏe định kỳ",
                "Vaccine cần tiêm",
                "Lối sống cần thay đổi"
            ],
            'emergency': [
                "Các dấu hiệu nguy hiểm khác",
                "Sơ cứu ban đầu như thế nào", 
                "Thông tin cần cung cấp cho bác sĩ",
                "Sau cấp cứu cần làm gì"
            ]
        }
        
        suggestions = suggestions_map.get(intent, [
            "Hãy hỏi về triệu chứng cụ thể",
            "Tìm hiểu về phòng ngừa bệnh",
            "Khám sức khỏe định kỳ thế nào",
            "Lối sống lành mạnh"
        ])
        
        return jsonify({
            'success': True,
            'intent': intent,
            'suggestions': suggestions[:5],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analytics/stats', methods=['GET'])
def get_analytics_stats():
    """
    Get detailed analytics and statistics
    """
    try:
        date = request.args.get('date')  # YYYY-MM-DD format
        
        # Get daily statistics
        stats = get_stats(date)
        
        return jsonify({
            'success': True,
            'analytics': stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        log_error('analytics_error', str(e))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/analytics/summary', methods=['GET'])
def get_analytics_summary():
    """
    Get quick analytics summary for dashboard
    """
    try:
        today_stats = get_stats()
        
        summary = {
            'today': {
                'total_queries': today_stats.get('total_queries', 0),
                'unique_sessions': today_stats.get('unique_sessions', 0),
                'top_intents': dict(list(today_stats.get('intent_breakdown', {}).items())[:3])
            },
            'search_performance': today_stats.get('search_performance', {}),
            'system_health': {
                'hybrid_search_ratio': (
                    today_stats.get('search_performance', {}).get('hybrid_searches', 0) /
                    max(
                        today_stats.get('search_performance', {}).get('hybrid_searches', 0) +
                        today_stats.get('search_performance', {}).get('fallback_searches', 0),
                        1
                    )
                ) * 100
            }
        }
        
        return jsonify({
            'success': True,
            'summary': summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        log_error('analytics_summary_error', str(e))
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Enhanced Medical Diagnosis Chatbot...")
    print("=" * 60)
    print("🏥 MEDICAL RAG SYSTEM v2.0")
    print("=" * 60)
    print("📋 Available endpoints:")
    print("   🔄 POST /ask                     : Main streaming chatbot endpoint")
    print("   📊 POST /ask_structured          : Enhanced structured response endpoint")  
    print("   📈 GET  /medical_stats           : Medical knowledge base statistics")
    print("   🔍 POST /medical_search          : Medical search endpoint")
    print("   💡 POST /suggestions/<intent>    : Get follow-up suggestions")
    print("   👥 POST /session/new             : Create new session")
    print("   📝 GET  /sessions                : List all sessions")
    print("   📊 GET  /analytics/stats         : Detailed analytics and statistics")
    print("   📈 GET  /analytics/summary       : Quick analytics summary")
    print("   🏥 GET  /health                  : Health check")
    print("")
    print("🎯 Features:")
    print("   ✅ Hybrid Search (Semantic + BM25)")
    print("   ✅ Query Transformation")  
    print("   ✅ Structured Data Extraction")
    print("   ✅ WHO ICD-11 Source Citation")
    print("   ✅ Follow-up Suggestions")
    print("   ✅ Session Management")
    print("   ✅ Comprehensive Logging & Analytics")
    print("")
    print("🌐 Access at: http://localhost:5000")
    print("🧪 Test with: /ask_structured endpoint for best experience")
    print("=" * 60)
    
    # Initialize hybrid search engine on startup
    try:
        from hybrid_search import initialize_hybrid_search
        print("🔄 Initializing Hybrid Search Engine...")
        if initialize_hybrid_search():
            print("✅ Hybrid Search Engine ready!")
        else:
            print("⚠️ Hybrid Search Engine failed to initialize - using fallback")
    except Exception as e:
        print(f"⚠️ Hybrid Search initialization error: {e}")
    
    app.run(debug=True, threaded=True, port=5000)

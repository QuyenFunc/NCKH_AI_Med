import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle
import json
import os
from datetime import datetime
import re

def load_medical_data():
    """Load medical FAISS index và chunks data"""
    try:
        # Đảm bảo tìm file trong thư mục chatbox
        current_dir = os.path.dirname(__file__)
        chunks_file = os.path.join(current_dir, "medical_chunks_with_metadata.pkl")
        index_file = os.path.join(current_dir, "medical_faiss_index.index")
        
        with open(chunks_file, "rb") as f:
            data = pickle.load(f)
        
        # Handle different data formats
        if isinstance(data, dict) and 'chunks' in data:
            chunks_data = data['chunks']
        elif isinstance(data, list):
            chunks_data = data
        else:
            print("❌ Unknown chunks data format")
            return None, None, None
        
        index = faiss.read_index(index_file)
        
        # Load embedder - sử dụng all-MiniLM-L6-v2 để match với FAISS index hiện tại
        try:
            embedder = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Using model: all-MiniLM-L6-v2 (compatible with existing FAISS index)")
        except Exception as model_error:
            print(f"❌ Cannot load embedding model: {model_error}")
            return None, None, None
        
        return index, chunks_data, embedder
    except FileNotFoundError:
        print("❌ Không tìm thấy medical data files. Vui lòng chạy setup_icd_rag.py trước.")
        return None, None, None
    except Exception as e:
        print(f"❌ Lỗi khi load medical data: {e}")
        return None, None, None

def improve_vietnamese_query(query):
    """Cải thiện query tiếng Việt bằng cách thêm keywords tiếng Anh"""
    
    # Dictionary dịch các từ y tế phổ biến
    medical_translations = {
        # Triệu chứng
        "đau đầu": "headache head pain",
        "buồn nôn": "nausea vomiting", 
        "sốt cao": "high fever temperature",
        "ho": "cough coughing",
        "đau ngực": "chest pain",
        "khó thở": "difficulty breathing dyspnea",
        "đau dạ dày": "stomach pain gastric pain",
        
        # Bệnh
        "tiểu đường": "diabetes mellitus",
        "cao huyết áp": "hypertension high blood pressure",
        "viêm phổi": "pneumonia lung inflammation",
        "ung thư phổi": "lung cancer pulmonary cancer",
        "viêm gan": "hepatitis liver inflammation",
        "đau tim": "heart pain cardiac pain",
        
        # Bộ phận cơ thể
        "phổi": "lung pulmonary",
        "tim": "heart cardiac",
        "gan": "liver hepatic",
        "dạ dày": "stomach gastric",
        "thận": "kidney renal",
        "não": "brain cerebral"
    }
    
    enhanced_query = query.lower()
    
    # Thêm từ tiếng Anh tương ứng
    for vietnamese, english in medical_translations.items():
        if vietnamese in enhanced_query:
            enhanced_query += f" {english}"
    
    return enhanced_query

def search_medical_symptoms_and_diseases(query, top_k=5, filters=None):
    """
    Tìm kiếm các triệu chứng và bệnh tật từ medical knowledge base với improved search
    
    Args:
        query: Câu hỏi hoặc mô tả triệu chứng của người dùng
        top_k: Số lượng kết quả trả về
        filters: Bộ lọc tìm kiếm (category_id, entity_type, etc.)
    """
    index, chunks_data, embedder = load_medical_data()
    
    if not index or not chunks_data or not embedder:
        return []
    
    try:
        # Tạo query embedding
        # Cải thiện query với Vietnamese enhancement
        enhanced_query = improve_vietnamese_query(query)
        
        # Tạo embedding cho enhanced query
        query_embedding = embedder.encode([enhanced_query], convert_to_numpy=True)
        
        # Tìm kiếm trong FAISS (lấy nhiều hơn để filter)
        search_size = min(top_k * 5, len(chunks_data))
        distances, indices = index.search(query_embedding, search_size)
        
        results = []
        seen_entities = set()  # Tránh duplicate entities
        
        for i, idx in enumerate(indices[0]):
            chunk_data = chunks_data[idx]
            metadata = chunk_data['metadata']
            
            # Áp dụng filters nếu có
            if filters:
                skip = False
                for key, value in filters.items():
                    if key == 'category_id':
                        if isinstance(value, list):
                            if metadata.get('category_id') not in value:
                                skip = True
                                break
                        else:
                            if metadata.get('category_id') != value:
                                skip = True
                                break
                    elif key == 'entity_type' and metadata.get('entity_type') != value:
                        skip = True
                        break
                    elif key == 'has_icd_code' and value and not metadata.get('icd_code'):
                        skip = True
                        break
                    elif key == 'source_type' and metadata.get('source_type') != value:
                        skip = True
                        break
                
                if skip:
                    continue
            
            # Tránh duplicate entities (trừ khi là category)
            entity_identifier = f"{metadata.get('entity_name', '')}-{metadata.get('icd_code', '')}"
            if entity_identifier in seen_entities and metadata.get('source_type') != 'icd_category':
                continue
            seen_entities.add(entity_identifier)
            
            # Tính relevance score với boost cho medical relevance
            base_score = 1 / (1 + distances[0][i])
            
            # Boost score based on medical relevance
            boost_factor = 1.0
            
            # Boost cho entities có ICD code
            if metadata.get('icd_code'):
                boost_factor *= 1.2
            
            # Boost cho diseases/conditions
            if metadata.get('entity_type') == 'disease_condition':
                boost_factor *= 1.1
            
            # Boost cho categories liên quan đến triệu chứng
            if metadata.get('category_id') in ['0M']:  # Symptoms, signs or clinical findings
                boost_factor *= 1.3
            
            final_score = base_score * boost_factor
            
            results.append({
                'text': chunk_data['text'],
                'metadata': metadata,
                'distance': distances[0][i],
                'relevance_score': final_score
            })
            
            if len(results) >= top_k:
                break
        
        # Sort by final relevance score
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return results[:top_k]
        
    except Exception as e:
        print(f"❌ Lỗi khi tìm kiếm medical data: {e}")
        import traceback
        traceback.print_exc()
        return []




def create_medical_diagnostic_context(search_results, user_symptoms=""):
    """
    Tạo context cho chẩn đoán y tế từ search results
    
    Args:
        search_results: Kết quả tìm kiếm từ medical knowledge base
        user_symptoms: Triệu chứng mà user mô tả
    """
    if not search_results:
        return "Không tìm thấy thông tin y tế liên quan trong cơ sở dữ liệu."
    
    context_parts = []
    
    # Thêm thông tin về triệu chứng user mô tả
    if user_symptoms:
        context_parts.append(f"=== TRIỆU CHỨNG NGƯỜI DÙNG MÔ TẢ ===")
        context_parts.append(f"Mô tả: {user_symptoms}")
        context_parts.append("")
    
    # Phân loại results theo loại
    symptoms_results = []
    diseases_results = []
    categories_results = []
    
    for result in search_results:
        metadata = result['metadata']
        if metadata.get('category_id') == '0M':  # Symptoms category
            symptoms_results.append(result)
        elif metadata.get('source_type') == 'icd_category':
            categories_results.append(result)
        else:
            diseases_results.append(result)
    
    # Hiển thị triệu chứng liên quan
    if symptoms_results:
        context_parts.append("=== TRIỆU CHỨNG VÀ DẤU HIỆU LIÊN QUAN ===")
        for i, result in enumerate(symptoms_results, 1):
            metadata = result['metadata']
            
            context_parts.append(f"Triệu chứng {i}:")
            if metadata.get('entity_name'):
                context_parts.append(f"- Tên: {metadata['entity_name']}")
            if metadata.get('icd_code'):
                context_parts.append(f"- Mã ICD-11: {metadata['icd_code']}")
            
            # Lấy phần definition từ text
            text_lines = result['text'].split('\n')
            for line in text_lines:
                if 'Định nghĩa:' in line or 'Định nghĩa chi tiết:' in line:
                    context_parts.append(f"- {line}")
                    break
            
            context_parts.append(f"- Độ liên quan: {result['relevance_score']:.3f}")
            context_parts.append("")
    
    # Hiển thị các bệnh có thể liên quan
    if diseases_results:
        context_parts.append("=== CÁC BỆNH CÓ THỂ LIÊN QUAN ===")
        for i, result in enumerate(diseases_results, 1):
            metadata = result['metadata']
            
            context_parts.append(f"Bệnh {i}:")
            if metadata.get('entity_name'):
                context_parts.append(f"- Tên bệnh: {metadata['entity_name']}")
            if metadata.get('icd_code'):
                context_parts.append(f"- Mã ICD-11: {metadata['icd_code']}")
            if metadata.get('category_name'):
                context_parts.append(f"- Danh mục: {metadata['category_name']}")
            
            # Lấy thông tin quan trọng từ text
            text_lines = result['text'].split('\n')
            for line in text_lines:
                if any(keyword in line for keyword in ['Định nghĩa:', 'Bao gồm:', 'Triệu chứng:']):
                    context_parts.append(f"- {line}")
                    if len([l for l in context_parts if f"Bệnh {i}:" in l or l.startswith("- ")]) > 6:
                        break
            
            context_parts.append(f"- Độ liên quan: {result['relevance_score']:.3f}")
            context_parts.append("")
    
    # Hiển thị thông tin category nếu có
    if categories_results:
        context_parts.append("=== DANH MỤC Y TẾ LIÊN QUAN ===")
        for i, result in enumerate(categories_results, 1):
            metadata = result['metadata']
            
            if metadata.get('category_name'):
                context_parts.append(f"Danh mục {i}: {metadata['category_name']}")
                if metadata.get('category_id'):
                    context_parts.append(f"- Mã danh mục: {metadata['category_id']}")
                
                # Lấy definition từ text
                text_lines = result['text'].split('\n')
                for line in text_lines:
                    if 'Định nghĩa:' in line:
                        context_parts.append(f"- {line}")
                        break
                
                context_parts.append("")
    
    return "\n".join(context_parts)

def create_medical_consultation_context(search_results, consultation_type="general"):
    """
    Tạo context cho tư vấn y tế
    
    Args:
        search_results: Kết quả tìm kiếm
        consultation_type: Loại tư vấn (general, emergency, prevention, etc.)
    """
    if not search_results:
        return "Không có thông tin y tế liên quan được tìm thấy."
    
    context_parts = []
    context_parts.append("=== THÔNG TIN Y TẾ TÌM ĐƯỢC ===")
    
    for i, result in enumerate(search_results, 1):
        metadata = result['metadata']
        text = result['text']
        
        context_parts.append(f"\n--- Thông tin {i} ---")
        
        # Thông tin cơ bản
        if metadata.get('entity_name'):
            context_parts.append(f"Tên: {metadata['entity_name']}")
        
        if metadata.get('icd_code'):
            context_parts.append(f"Mã ICD-11: {metadata['icd_code']}")
        
        if metadata.get('category_name'):
            context_parts.append(f"Danh mục: {metadata['category_name']}")
        
        # Trích xuất thông tin quan trọng từ text
        text_lines = text.split('\n')
        important_info = []
        
        for line in text_lines:
            if any(keyword in line for keyword in [
                'Định nghĩa:', 'Định nghĩa chi tiết:', 'Bao gồm:', 
                'Loại trừ:', 'Từ đồng nghĩa:', 'Triệu chứng:'
            ]):
                important_info.append(line)
        
        if important_info:
            context_parts.append("Thông tin chi tiết:")
            for info in important_info[:3]:  # Giới hạn 3 dòng để tránh quá dài
                context_parts.append(f"  {info}")
        
        context_parts.append(f"Độ liên quan: {result['relevance_score']:.3f}")
    
    # Thêm disclaimer cho tư vấn y tế
    context_parts.append("\n=== LƯU Ý QUAN TRỌNG ===")
    context_parts.append("- Thông tin trên chỉ mang tính chất tham khảo")
    context_parts.append("- Không thay thế cho chẩn đoán và điều trị của bác sĩ")
    context_parts.append("- Nếu có triệu chứng nghiêm trọng, hãy đến cơ sở y tế ngay lập tức")
    
    return "\n".join(context_parts)

def get_medical_statistics():
    """Lấy thống kê về medical knowledge base"""
    try:
        # Đảm bảo tìm file trong thư mục chatbox
        current_dir = os.path.dirname(__file__)
        chunks_file = os.path.join(current_dir, "medical_chunks_with_metadata.pkl")
        
        with open(chunks_file, "rb") as f:
            chunks_data = pickle.load(f)
        
        metadata_list = chunks_data.get('metadata', [])
        
        stats = {
            'total_chunks': len(metadata_list),
            'total_categories': chunks_data.get('total_categories', 0),
            'categories': {},
            'entity_types': {},
            'has_icd_code': 0,
            'created_at': chunks_data.get('created_at'),
            'data_source': chunks_data.get('data_source', 'unknown')
        }
        
        # Thống kê chi tiết
        for metadata in metadata_list:
            # Category stats
            category_id = metadata.get('category_id')
            category_name = metadata.get('category_name')
            if category_id:
                if category_id not in stats['categories']:
                    stats['categories'][category_id] = {
                        'name': category_name,
                        'count': 0
                    }
                stats['categories'][category_id]['count'] += 1
            
            # Entity type stats
            entity_type = metadata.get('entity_type', 'unknown')
            stats['entity_types'][entity_type] = stats['entity_types'].get(entity_type, 0) + 1
            
            # ICD code stats
            if metadata.get('icd_code'):
                stats['has_icd_code'] += 1
        
        return stats
        
    except FileNotFoundError:
        return {"error": "Medical data not found. Please run setup_icd_rag.py first."}
    except Exception as e:
        return {"error": f"Error getting medical statistics: {str(e)}"}

def classify_medical_query_intent(query):
    """
    Phân loại intent của câu hỏi y tế
    
    Returns:
        - symptom_inquiry: Hỏi về triệu chứng
        - disease_inquiry: Hỏi về bệnh tật
        - treatment_inquiry: Hỏi về điều trị
        - prevention_inquiry: Hỏi về phòng ngừa
        - general_medical: Câu hỏi y tế chung
        - emergency: Tình huống khẩn cấp
    """
    query_lower = query.lower()
    
    # Từ khóa triệu chứng
    symptom_keywords = [
        'triệu chứng', 'dấu hiệu', 'biểu hiện', 'đau', 'sốt', 'ho', 'khó thở',
        'buồn nôn', 'nôn mửa', 'tiêu chảy', 'táo bón', 'chóng mặt', 'đau đầu',
        'mệt mỏi', 'ngứa', 'phát ban', 'sưng', 'tê', 'tại sao', 'vì sao',
        'bị', 'có', 'xuất hiện', 'cảm thấy'
    ]
    
    # Từ khóa bệnh tật
    disease_keywords = [
        'bệnh', 'chứng', 'hội chứng', 'rối loạn', 'viêm', 'nhiễm trùng',
        'ung thư', 'tim mạch', 'tiểu đường', 'cao huyết áp', 'đột quỵ',
        'gì là', 'là gì', 'định nghĩa', 'nguyên nhân'
    ]
    
    # Từ khóa điều trị
    treatment_keywords = [
        'điều trị', 'chữa', 'thuốc', 'uống thuốc', 'chữa trị', 'hỗ trợ',
        'phẫu thuật', 'thủ thuật', 'làm sao', 'cách nào', 'phương pháp'
    ]
    
    # Từ khóa phòng ngừa
    prevention_keywords = [
        'phòng ngừa', 'phòng tránh', 'ngăn ngừa', 'dự phòng', 'tránh',
        'làm gì để không', 'cách phòng', 'bảo vệ'
    ]
    
    # Từ khóa khẩn cấp
    emergency_keywords = [
        'cấp cứu', 'khẩn cấp', 'nguy hiểm', 'nghiêm trọng', 'gấp',
        'ngay lập tức', 'báo động', 'đau dữ dội', 'không thở được',
        'bất tỉnh', 'ngất', 'co giật'
    ]
    
    # Đếm số từ khóa phù hợp
    symptom_count = sum(1 for keyword in symptom_keywords if keyword in query_lower)
    disease_count = sum(1 for keyword in disease_keywords if keyword in query_lower)
    treatment_count = sum(1 for keyword in treatment_keywords if keyword in query_lower)
    prevention_count = sum(1 for keyword in prevention_keywords if keyword in query_lower)
    emergency_count = sum(1 for keyword in emergency_keywords if keyword in query_lower)
    
    # Ưu tiên emergency trước
    if emergency_count > 0:
        return "emergency"
    
    # Sau đó phân loại theo số lượng từ khóa
    max_count = max(symptom_count, disease_count, treatment_count, prevention_count)
    
    if max_count == 0:
        return "general_medical"
    elif symptom_count == max_count:
        return "symptom_inquiry"
    elif disease_count == max_count:
        return "disease_inquiry"
    elif treatment_count == max_count:
        return "treatment_inquiry"
    elif prevention_count == max_count:
        return "prevention_inquiry"
    else:
        return "general_medical"

# Test functions
def test_medical_search():
    """Test function để kiểm tra medical search"""
    test_queries = [
        "đau đầu và chóng mặt",
        "sốt cao và ho",
        "đau bụng và tiêu chảy",
        "khó thở và đau ngực",
        "mệt mỏi và sụt cân"
    ]
    
    print("🧪 Testing Medical Search...")
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        intent = classify_medical_query_intent(query)
        print(f"Intent: {intent}")
        
        results = search_medical_symptoms_and_diseases(query, top_k=3)
        if results:
            print("Top results:")
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                entity_name = metadata.get('entity_name', 'Unknown')
                icd_code = metadata.get('icd_code', 'N/A')
                relevance = result['relevance_score']
                print(f"  {i}. {entity_name} (ICD: {icd_code}) - Relevance: {relevance:.3f}")
        else:
            print("  No results found")

if __name__ == "__main__":
    # Test medical search functionality
    test_medical_search()
    
    # Display statistics
    print(f"\n📊 Medical Knowledge Base Statistics:")
    stats = get_medical_statistics()
    if 'error' not in stats:
        print(f"Total chunks: {stats['total_chunks']}")
        print(f"Total categories: {stats['total_categories']}")
        print(f"Chunks with ICD codes: {stats['has_icd_code']}")
        print(f"Data source: {stats['data_source']}")
        print(f"Created at: {stats['created_at']}")
    else:
        print(f"Error: {stats['error']}")

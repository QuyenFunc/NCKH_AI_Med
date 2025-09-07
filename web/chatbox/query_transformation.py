"""
Query Transformation Module for Medical RAG
Chuyển đổi và làm giàu câu hỏi của người dùng để tăng hiệu quả tìm kiếm
"""

from typing import List, Dict, Any, Optional
from config import client
import json
import re


class MedicalQueryTransformer:
    """
    Transforms user queries to improve RAG search results
    """
    
    def __init__(self):
        self.medical_context_patterns = [
            # Pattern cho triệu chứng
            r'(tôi bị|mình bị|có triệu chứng|triệu chứng là)',
            # Pattern cho bệnh
            r'(bệnh gì|loại bệnh|chứng bệnh|tình trạng)',
            # Pattern cho điều trị
            r'(điều trị|chữa|thuốc|cách chữa|phương pháp)',
            # Pattern cho phòng ngừa
            r'(phòng ngừa|phòng tránh|ngăn chặn|dự phòng)'
        ]
    
    def transform_query(self, original_query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Transform a single query into multiple sub-queries and enriched versions
        
        Args:
            original_query: The user's original query
            conversation_history: Previous conversation for context
            
        Returns:
            Dict containing transformed queries and metadata
        """
        try:
            # 1. Extract key medical entities
            entities = self._extract_medical_entities(original_query)
            
            # 2. Generate sub-queries
            sub_queries = self._generate_sub_queries(original_query, conversation_history)
            
            # 3. Create enriched query with medical context
            enriched_query = self._enrich_with_medical_context(original_query, entities)
            
            # 4. Generate alternative phrasings
            alternative_queries = self._generate_alternatives(original_query)
            
            return {
                'original_query': original_query,
                'enriched_query': enriched_query,
                'sub_queries': sub_queries,
                'alternative_queries': alternative_queries,
                'medical_entities': entities,
                'search_strategy': self._determine_search_strategy(original_query, entities)
            }
            
        except Exception as e:
            print(f"❌ Query transformation error: {e}")
            return {
                'original_query': original_query,
                'enriched_query': original_query,
                'sub_queries': [original_query],
                'alternative_queries': [],
                'medical_entities': {},
                'search_strategy': 'default'
            }
    
    def _extract_medical_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract medical entities from the query using LLM"""
        
        entity_extraction_prompt = f"""Phân tích câu hỏi y tế sau và trích xuất các thực thể y tế quan trọng.

Câu hỏi: "{query}"

Trả về JSON với các loại thực thể sau (chỉ bao gồm nếu có trong câu hỏi):
- "symptoms": [danh sách triệu chứng]  
- "diseases": [danh sách bệnh tật]
- "body_parts": [danh sách bộ phận cơ thể]
- "medications": [danh sách thuốc]
- "procedures": [danh sách quy trình y tế]
- "demographics": [tuổi, giới tính, nhóm đối tượng]

Ví dụ:
Input: "Tôi bị đau đầu và chóng mặt, có phải bệnh cao huyết áp không?"
Output: {{"symptoms": ["đau đầu", "chóng mặt"], "diseases": ["cao huyết áp"], "body_parts": ["đầu"]}}

Chỉ trả về JSON, không có text khác:"""

        try:
            response = client.chat.completions.create(
                model="deepseek/deepseek-chat-v3.1:free",
                messages=[{"role": "user", "content": entity_extraction_prompt}],
                max_tokens=800,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                entities = json.loads(json_match.group())
                return entities
            else:
                return {}
                
        except Exception as e:
            print(f"❌ Entity extraction error: {e}")
            return {}
    
    def _generate_sub_queries(self, query: str, conversation_history: List[Dict] = None) -> List[str]:
        """Generate focused sub-queries from a complex query"""
        
        # Build context from conversation history
        context = ""
        if conversation_history:
            recent_messages = conversation_history[-4:]  # Last 4 messages
            context = "\\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])
        
        sub_query_prompt = f"""Phân tích câu hỏi y tế phức tạp thành các câu hỏi con đơn giản và tập trung.

{"Ngữ cảnh cuộc trò chuyện trước:" + context if context else ""}

Câu hỏi chính: "{query}"

Hãy chia thành 2-4 câu hỏi con rõ ràng, mỗi câu tập trung vào một khía cạnh cụ thể:
- Triệu chứng/dấu hiệu
- Nguyên nhân/bệnh lý  
- Điều trị/thuốc
- Phòng ngừa/chăm sóc

Trả về dưới dạng JSON array của strings:
["câu hỏi con 1", "câu hỏi con 2", ...]

Ví dụ:
Input: "Tôi bị tiểu đường và cao huyết áp, nên ăn gì và uống thuốc gì?"
Output: ["triệu chứng tiểu đường và cao huyết áp", "chế độ ăn cho người tiểu đường cao huyết áp", "thuốc điều trị tiểu đường", "thuốc điều trị cao huyết áp an toàn cho người tiểu đường"]

Chỉ trả về JSON array:"""

        try:
            response = client.chat.completions.create(
                model="deepseek/deepseek-chat-v3.1:free",
                messages=[{"role": "user", "content": sub_query_prompt}],
                max_tokens=1000,
                temperature=0.2
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                sub_queries = json.loads(json_match.group())
                return sub_queries if isinstance(sub_queries, list) else [query]
            else:
                return [query]
                
        except Exception as e:
            print(f"❌ Sub-query generation error: {e}")
            return [query]
    
    def _enrich_with_medical_context(self, query: str, entities: Dict[str, List[str]]) -> str:
        """Enrich query with medical context and synonyms"""
        
        enriched_parts = [query]
        
        # Add medical synonyms and related terms
        if entities.get('symptoms'):
            symptom_terms = "triệu chứng dấu hiệu biểu hiện"
            enriched_parts.append(symptom_terms)
        
        if entities.get('diseases'):
            disease_terms = "bệnh tật chứng bệnh rối loạn hội chứng"
            enriched_parts.append(disease_terms)
        
        if entities.get('medications'):
            medication_terms = "thuốc điều trị dược phẩm"
            enriched_parts.append(medication_terms)
        
        # Add ICD-11 related terms for better matching
        medical_context = "chẩn đoán y tế WHO ICD-11 classification"
        enriched_parts.append(medical_context)
        
        return " ".join(enriched_parts)
    
    def _generate_alternatives(self, query: str) -> List[str]:
        """Generate alternative phrasings of the query"""
        
        alternative_prompt = f"""Tạo 2-3 cách diễn đạt khác nhau cho câu hỏi y tế sau, giữ nguyên ý nghĩa nhưng thay đổi từ ngữ:

Câu hỏi gốc: "{query}"

Tạo các phiên bản:
1. Sử dụng thuật ngữ y khoa chính thức hơn
2. Sử dụng ngôn ngữ đơn giản, dễ hiểu hơn  
3. Tập trung vào khía cạnh khác của vấn đề

Trả về JSON array:
["phiên bản 1", "phiên bản 2", "phiên bản 3"]

Ví dụ:
Input: "Tôi bị đau bụng"
Output: ["triệu chứng đau vùng bụng", "đau ở vùng bụng là bệnh gì", "nguyên nhân gây đau bụng"]

Chỉ trả về JSON array:"""

        try:
            response = client.chat.completions.create(
                model="deepseek/deepseek-chat-v3.1:free",
                messages=[{"role": "user", "content": alternative_prompt}],
                max_tokens=800,
                temperature=0.3
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON array from response
            json_match = re.search(r'\[.*\]', result, re.DOTALL)
            if json_match:
                alternatives = json.loads(json_match.group())
                return alternatives if isinstance(alternatives, list) else []
            else:
                return []
                
        except Exception as e:
            print(f"❌ Alternative generation error: {e}")
            return []
    
    def _determine_search_strategy(self, query: str, entities: Dict[str, List[str]]) -> str:
        """Determine the best search strategy based on query analysis"""
        
        query_lower = query.lower()
        
        # Emergency detection
        emergency_keywords = ['cấp cứu', 'khẩn cấp', 'nguy hiểm', 'nghiêm trọng', 
                            'co giật', 'ngất', 'bất tỉnh', 'khó thở nghiêm trọng']
        if any(keyword in query_lower for keyword in emergency_keywords):
            return 'emergency'
        
        # Symptom-focused search
        if entities.get('symptoms') and len(entities['symptoms']) >= 2:
            return 'multi_symptom'
        
        # Disease-focused search
        if entities.get('diseases'):
            return 'disease_focused'
        
        # Treatment-focused search
        treatment_keywords = ['điều trị', 'chữa', 'thuốc', 'phương pháp']
        if any(keyword in query_lower for keyword in treatment_keywords):
            return 'treatment_focused'
        
        # Prevention-focused search
        prevention_keywords = ['phòng ngừa', 'phòng tránh', 'dự phòng', 'ngăn chặn']
        if any(keyword in query_lower for keyword in prevention_keywords):
            return 'prevention_focused'
        
        return 'general'
    
    def get_search_weights(self, strategy: str) -> Dict[str, float]:
        """Get search weights based on strategy"""
        
        weight_configs = {
            'emergency': {'semantic': 0.8, 'keyword': 0.2},
            'multi_symptom': {'semantic': 0.6, 'keyword': 0.4},
            'disease_focused': {'semantic': 0.7, 'keyword': 0.3},
            'treatment_focused': {'semantic': 0.5, 'keyword': 0.5},
            'prevention_focused': {'semantic': 0.7, 'keyword': 0.3},
            'general': {'semantic': 0.7, 'keyword': 0.3}
        }
        
        return weight_configs.get(strategy, weight_configs['general'])


# Global instance
query_transformer = MedicalQueryTransformer()

def transform_medical_query(query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
    """
    Global function to transform medical queries
    """
    return query_transformer.transform_query(query, conversation_history)


# Test function
def test_query_transformation():
    """Test query transformation functionality"""
    
    test_queries = [
        "Tôi bị đau đầu và chóng mặt, có phải cao huyết áp không?",
        "Trẻ em bị sốt và ho nên làm gì?",
        "Tiểu đường type 2 nên ăn gì và uống thuốc gì?",
        "Cách phòng ngừa bệnh tim mạch",
        "Covid-19 có triệu chứng gì và điều trị thế nào?"
    ]
    
    transformer = MedicalQueryTransformer()
    
    print("\n🧪 Testing Query Transformation...")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Original Query: '{query}'")
        result = transformer.transform_query(query)
        
        print(f"📋 Strategy: {result['search_strategy']}")
        print(f"🎯 Medical Entities: {result['medical_entities']}")
        print(f"📝 Sub-queries: {len(result['sub_queries'])}")
        for i, sub_q in enumerate(result['sub_queries'], 1):
            print(f"   {i}. {sub_q}")
        
        if result['alternative_queries']:
            print(f"🔄 Alternatives: {len(result['alternative_queries'])}")
            for i, alt_q in enumerate(result['alternative_queries'], 1):
                print(f"   {i}. {alt_q}")
        print("-" * 40)

if __name__ == "__main__":
    test_query_transformation()

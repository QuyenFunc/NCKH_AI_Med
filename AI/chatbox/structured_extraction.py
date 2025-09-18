"""
Structured Data Extraction Module for Medical RAG
Trích xuất thông tin có cấu trúc từ LLM response để frontend hiển thị đẹp hơn
"""

from typing import Dict, List, Any, Optional, Union
from config import client
import json
import re
from datetime import datetime


class MedicalStructuredExtractor:
    """
    Extract structured medical information from search results and LLM responses
    """
    
    def __init__(self):
        self.response_schemas = {
            'disease_info': {
                'ten_benh': 'str',
                'ma_icd': 'str',
                'danh_muc': 'str', 
                'dinh_nghia': 'str',
                'trieu_chung_chinh': 'list',
                'nguyen_nhan': 'list',
                'yeu_to_nguy_co': 'list',
                'bien_chung': 'list',
                'chan_doan': 'str',
                'dieu_tri': 'str',
                'phong_ngua': 'str',
                'tien_luong': 'str'
            },
            
            'symptom_analysis': {
                'trieu_chung_mo_ta': 'str',
                'trieu_chung_chinh': 'list',
                'muc_do_nghiem_trong': 'str',  # 'nhẹ', 'trung bình', 'nặng', 'khẩn cấp'
                'benh_co_the_lien_quan': 'list',
                'khuyen_nghi_hanh_dong': 'str',
                'can_gap_bac_si': 'bool',
                'cap_cuu_ngay': 'bool',
                'theo_doi_trieu_chung': 'list'
            },
            
            'treatment_info': {
                'loai_dieu_tri': 'str',  # 'thuốc', 'thủ thuật', 'phẫu thuật', 'lối sống'
                'phuong_phap_chinh': 'str',
                'thuoc_dieu_tri': 'list',
                'lieu_luong': 'str',
                'tac_dung_phu': 'list',
                'luu_y_dac_biet': 'list',
                'thoi_gian_dieu_tri': 'str',
                'theo_doi_hieu_qua': 'str',
                'thay_doi_loi_song': 'list'
            },
            
            'prevention_info': {
                'bien_phap_phong_ngua': 'list',
                'thay_doi_loi_song': 'list',
                'che_do_an': 'list',
                'tap_the_duc': 'str',
                'kham_suc_khoe_dinh_ky': 'str',
                'vaccine': 'list',
                'tranh_yeu_to_nguy_co': 'list'
            },
            
            'emergency_response': {
                'tinh_huong_khan_cap': 'bool',
                'muc_do_nguy_hiem': 'str',  # 'cao', 'trung bình', 'thấp'
                'hanh_dong_ngay': 'list',
                'so_cuu_cap': 'str',
                'khong_nen_lam': 'list',
                'thong_tin_cap_cuu': 'str'
            }
        }
    
    def extract_structured_response(self, 
                                  search_results: List[Dict], 
                                  user_query: str, 
                                  intent_type: str,
                                  raw_llm_response: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract structured information based on intent type
        
        Args:
            search_results: Results from RAG search
            user_query: Original user query
            intent_type: Type of medical intent
            raw_llm_response: Raw response from LLM (optional)
            
        Returns:
            Structured response with metadata
        """
        
        try:
            # Determine response schema based on intent
            schema_type = self._map_intent_to_schema(intent_type)
            
            # Generate structured response
            structured_data = self._generate_structured_data(
                search_results, user_query, schema_type, raw_llm_response
            )
            
            # Add metadata and suggestions
            response = {
                'query': user_query,
                'intent_type': intent_type,
                'schema_type': schema_type,
                'timestamp': datetime.now().isoformat(),
                'data': structured_data,
                'source_info': self._extract_source_info(search_results),
                'follow_up_suggestions': self._generate_follow_up_suggestions(structured_data, intent_type),
                'confidence_score': self._calculate_confidence_score(search_results, structured_data),
                'disclaimer': self._get_medical_disclaimer(intent_type)
            }
            
            return response
            
        except Exception as e:
            print(f"❌ Structured extraction error: {e}")
            return self._get_fallback_response(user_query, intent_type, raw_llm_response)
    
    def _map_intent_to_schema(self, intent_type: str) -> str:
        """Map medical intent to response schema"""
        intent_mapping = {
            'disease_inquiry': 'disease_info',
            'symptom_inquiry': 'symptom_analysis', 
            'treatment_inquiry': 'treatment_info',
            'prevention_inquiry': 'prevention_info',
            'emergency': 'emergency_response'
        }
        
        return intent_mapping.get(intent_type, 'symptom_analysis')
    
    def _generate_structured_data(self, 
                                search_results: List[Dict], 
                                user_query: str, 
                                schema_type: str,
                                raw_llm_response: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured data using LLM"""
        
        # Build context from search results
        context_parts = []
        for i, result in enumerate(search_results[:5], 1):
            metadata = result.get('metadata', {})
            text = result.get('text', '')
            
            context_entry = f"=== THÔNG TIN {i} ===\\n"
            if metadata.get('entity_name'):
                context_entry += f"Tên: {metadata['entity_name']}\\n"
            if metadata.get('icd_code'):
                context_entry += f"Mã ICD-11: {metadata['icd_code']}\\n"
            if metadata.get('category_name'):
                context_entry += f"Danh mục: {metadata['category_name']}\\n"
            
            context_entry += f"Chi tiết: {text[:500]}...\\n\\n"
            context_parts.append(context_entry)
        
        context = "\\n".join(context_parts)
        
        # Get schema definition
        schema = self.response_schemas.get(schema_type, {})
        
        # Create structured extraction prompt
        extraction_prompt = self._create_extraction_prompt(
            user_query, context, schema_type, schema, raw_llm_response
        )
        
        try:
            response = client.chat.completions.create(
                model="deepseek/deepseek-chat-v3.1:free",
                messages=[{"role": "user", "content": extraction_prompt}],
                max_tokens=2000,
                temperature=0.1
            )
            
            result = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\\{.*\\}', result, re.DOTALL)
            if json_match:
                structured_data = json.loads(json_match.group())
                return self._validate_and_clean_data(structured_data, schema)
            else:
                return self._get_default_structure(schema_type)
                
        except Exception as e:
            print(f"❌ LLM extraction error: {e}")
            return self._get_default_structure(schema_type)
    
    def _create_extraction_prompt(self, 
                                user_query: str, 
                                context: str, 
                                schema_type: str, 
                                schema: Dict[str, str],
                                raw_llm_response: Optional[str] = None) -> str:
        """Create extraction prompt based on schema type"""
        
        base_prompt = f"""Bạn là chuyên gia y tế, hãy trích xuất thông tin có cấu trúc từ dữ liệu y tế dưới đây.

Câu hỏi của bệnh nhân: "{user_query}"

THÔNG TIN Y TẾ TỪ CƠ SỞ DỮ LIỆU:
{context}

{"PHÂN TÍCH TRƯỚC ĐÓ:" + raw_llm_response if raw_llm_response else ""}

Hãy trích xuất thông tin theo format JSON sau:"""
        
        if schema_type == 'disease_info':
            schema_example = """{
    "ten_benh": "Tên bệnh chính xác",
    "ma_icd": "Mã ICD-11 nếu có",
    "danh_muc": "Danh mục y tế",
    "dinh_nghia": "Định nghĩa ngắn gọn về bệnh",
    "trieu_chung_chinh": ["triệu chứng 1", "triệu chứng 2"],
    "nguyen_nhan": ["nguyên nhân 1", "nguyên nhân 2"],
    "yeu_to_nguy_co": ["yếu tố nguy cơ 1", "yếu tố nguy cơ 2"],
    "bien_chung": ["biến chứng 1", "biến chứng 2"],
    "chan_doan": "Phương pháp chẩn đoán",
    "dieu_tri": "Phương pháp điều trị chính",
    "phong_ngua": "Cách phòng ngừa",
    "tien_luong": "Tiên lượng và kết quả điều trị"
}"""
            
        elif schema_type == 'symptom_analysis':
            schema_example = """{
    "trieu_chung_mo_ta": "Mô tả tổng quan về các triệu chứng",
    "trieu_chung_chinh": ["triệu chứng chính 1", "triệu chứng chính 2"],
    "muc_do_nghiem_trong": "nhẹ|trung bình|nặng|khẩn cấp",
    "benh_co_the_lien_quan": ["bệnh có thể 1", "bệnh có thể 2"],
    "khuyen_nghi_hanh_dong": "Khuyến nghị hành động cụ thể",
    "can_gap_bac_si": true/false,
    "cap_cuu_ngay": true/false,
    "theo_doi_trieu_chung": ["triệu chứng cần theo dõi 1", "triệu chứng cần theo dõi 2"]
}"""
            
        elif schema_type == 'treatment_info':
            schema_example = """{
    "loai_dieu_tri": "thuốc|thủ thuật|phẫu thuật|lối sống",
    "phuong_phap_chinh": "Mô tả phương pháp điều trị chính",
    "thuoc_dieu_tri": ["thuốc 1", "thuốc 2"],
    "lieu_luong": "Hướng dẫn liều lượng chung",
    "tac_dung_phu": ["tác dụng phụ 1", "tác dụng phụ 2"],
    "luu_y_dac_biet": ["lưu ý 1", "lưu ý 2"],
    "thoi_gian_dieu_tri": "Thời gian điều trị dự kiến",
    "theo_doi_hieu_qua": "Cách theo dõi hiệu quả điều trị",
    "thay_doi_loi_song": ["thay đổi lối sống 1", "thay đổi lối sống 2"]
}"""
            
        elif schema_type == 'prevention_info':
            schema_example = """{
    "bien_phap_phong_ngua": ["biện pháp 1", "biện pháp 2"],
    "thay_doi_loi_song": ["thay đổi 1", "thay đổi 2"],
    "che_do_an": ["khuyến nghị dinh dưỡng 1", "khuyến nghị dinh dưỡng 2"],
    "tap_the_duc": "Khuyến nghị về tập thể dục",
    "kham_suc_khoe_dinh_ky": "Tần suất khám sức khỏe",
    "vaccine": ["vaccine 1", "vaccine 2"],
    "tranh_yeu_to_nguy_co": ["tránh yếu tố 1", "tránh yếu tố 2"]
}"""
            
        elif schema_type == 'emergency_response':
            schema_example = """{
    "tinh_huong_khan_cap": true/false,
    "muc_do_nguy_hiem": "cao|trung bình|thấp",
    "hanh_dong_ngay": ["hành động 1", "hành động 2"],
    "so_cuu_cap": "115 hoặc số cấp cứu địa phương",
    "khong_nen_lam": ["không nên làm 1", "không nên làm 2"],
    "thong_tin_cap_cuu": "Thông tin cần cung cấp cho cấp cứu"
}"""
        else:
            schema_example = "{}"
        
        return f"""{base_prompt}

{schema_example}

YÊU CẦU:
- Chỉ sử dụng thông tin có trong dữ liệu y tế được cung cấp
- Nếu không có thông tin, để trống ("") hoặc mảng rỗng ([])
- Sử dụng thuật ngữ y khoa chính xác
- Đảm bảo thông tin chính xác và đáng tin cậy
- KHÔNG thêm thông tin không có trong nguồn dữ liệu

Chỉ trả về JSON, không có text khác:"""
    
    def _validate_and_clean_data(self, data: Dict[str, Any], schema: Dict[str, str]) -> Dict[str, Any]:
        """Validate and clean extracted data according to schema"""
        
        cleaned_data = {}
        
        for field, expected_type in schema.items():
            if field in data:
                value = data[field]
                
                if expected_type == 'str':
                    cleaned_data[field] = str(value) if value else ""
                elif expected_type == 'list':
                    if isinstance(value, list):
                        cleaned_data[field] = [str(item) for item in value if item]
                    else:
                        cleaned_data[field] = []
                elif expected_type == 'bool':
                    cleaned_data[field] = bool(value)
                else:
                    cleaned_data[field] = value
            else:
                # Provide default values
                if expected_type == 'str':
                    cleaned_data[field] = ""
                elif expected_type == 'list':
                    cleaned_data[field] = []
                elif expected_type == 'bool':
                    cleaned_data[field] = False
        
        return cleaned_data
    
    def _extract_source_info(self, search_results: List[Dict]) -> List[Dict[str, Any]]:
        """Extract source information for citations"""
        
        sources = []
        for result in search_results[:3]:  # Top 3 sources
            metadata = result.get('metadata', {})
            
            source_info = {
                'entity_name': metadata.get('entity_name', 'Unknown'),
                'icd_code': metadata.get('icd_code'),
                'category_name': metadata.get('category_name'),
                'source_type': metadata.get('source_type', 'WHO ICD-11'),
                'relevance_score': result.get('relevance_score', result.get('hybrid_score', 0)),
                'url': self._generate_who_url(metadata.get('icd_code'))
            }
            
            sources.append(source_info)
        
        return sources
    
    def _generate_who_url(self, icd_code: Optional[str]) -> Optional[str]:
        """Generate WHO ICD-11 URL for the given code"""
        if icd_code:
            return f"https://icd.who.int/browse11/l-m/en#/http://id.who.int/icd/entity/{icd_code}"
        return None
    
    def _generate_follow_up_suggestions(self, structured_data: Dict[str, Any], intent_type: str) -> List[str]:
        """Generate follow-up question suggestions"""
        
        suggestions = []
        
        if intent_type == 'disease_inquiry':
            suggestions = [
                "Cách phòng ngừa bệnh này",
                "Triệu chứng cần theo dõi",
                "Phương pháp điều trị hiện đại",
                "Khi nào cần đi khám bác sĩ"
            ]
        elif intent_type == 'symptom_inquiry':
            suggestions = [
                "Các bệnh có thể gây ra triệu chứng này",
                "Cách giảm nhẹ triệu chứng tại nhà",
                "Khi nào cần đi cấp cứu",
                "Các xét nghiệm cần làm"
            ]
        elif intent_type == 'treatment_inquiry':
            suggestions = [
                "Tác dụng phụ của điều trị",
                "Thời gian điều trị dự kiến",
                "Cách theo dõi hiệu quả",
                "Các phương pháp điều trị thay thế"
            ]
        elif intent_type == 'prevention_inquiry':
            suggestions = [
                "Chế độ ăn phù hợp",
                "Bài tập thể dục khuyến nghị",
                "Tần suất khám sức khỏe",
                "Các yếu tố nguy cơ cần tránh"
            ]
        
        return suggestions
    
    def _calculate_confidence_score(self, search_results: List[Dict], structured_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on search results quality"""
        
        if not search_results:
            return 0.0
        
        # Average relevance score
        avg_relevance = sum(
            result.get('relevance_score', result.get('hybrid_score', 0)) 
            for result in search_results[:3]
        ) / min(len(search_results), 3)
        
        # Data completeness score
        non_empty_fields = sum(
            1 for value in structured_data.values() 
            if value and (isinstance(value, str) and value.strip()) or 
               (isinstance(value, list) and value) or
               (isinstance(value, bool))
        )
        total_fields = len(structured_data)
        completeness = non_empty_fields / total_fields if total_fields > 0 else 0
        
        # Combined confidence score
        confidence = (avg_relevance * 0.6 + completeness * 0.4)
        return min(confidence, 1.0)
    
    def _get_medical_disclaimer(self, intent_type: str) -> str:
        """Get appropriate medical disclaimer"""
        
        disclaimers = {
            'emergency': "⚠️ KHẨN CẤP: Thông tin này chỉ mang tính tham khảo. Nếu là tình huống khẩn cấp, hãy gọi 115 hoặc đến bệnh viện ngay lập tức!",
            'treatment_inquiry': "💊 LƯU Ý: Thông tin điều trị chỉ mang tính tham khảo. Không tự ý dùng thuốc. Hãy tham khảo ý kiến bác sĩ trước khi áp dụng bất kỳ phương pháp điều trị nào.",
            'default': "🩺 LƯU Ý: Thông tin này chỉ mang tính chất tham khảo từ WHO ICD-11. Không thay thế cho chẩn đoán và điều trị của bác sĩ. Nếu có triệu chứng bất thường, hãy đến cơ sở y tế."
        }
        
        return disclaimers.get(intent_type, disclaimers['default'])
    
    def _get_default_structure(self, schema_type: str) -> Dict[str, Any]:
        """Get default structure when extraction fails"""
        
        schema = self.response_schemas.get(schema_type, {})
        default_data = {}
        
        for field, field_type in schema.items():
            if field_type == 'str':
                default_data[field] = ""
            elif field_type == 'list':
                default_data[field] = []
            elif field_type == 'bool':
                default_data[field] = False
        
        return default_data
    
    def _get_fallback_response(self, user_query: str, intent_type: str, raw_response: Optional[str]) -> Dict[str, Any]:
        """Get fallback response when extraction completely fails"""
        
        return {
            'query': user_query,
            'intent_type': intent_type,
            'schema_type': 'fallback',
            'timestamp': datetime.now().isoformat(),
            'data': {
                'raw_response': raw_response or "Không thể trích xuất thông tin có cấu trúc.",
                'success': False
            },
            'source_info': [],
            'follow_up_suggestions': [
                "Hãy đặt câu hỏi cụ thể hơn",
                "Mô tả triệu chứng chi tiết hơn",
                "Tham khảo ý kiến bác sĩ"
            ],
            'confidence_score': 0.0,
            'disclaimer': self._get_medical_disclaimer(intent_type)
        }


# Global instance
structured_extractor = MedicalStructuredExtractor()

def extract_medical_structure(search_results: List[Dict], 
                            user_query: str, 
                            intent_type: str,
                            raw_llm_response: Optional[str] = None) -> Dict[str, Any]:
    """
    Global function to extract structured medical information
    """
    return structured_extractor.extract_structured_response(
        search_results, user_query, intent_type, raw_llm_response
    )


# Test function
def test_structured_extraction():
    """Test structured extraction functionality"""
    
    # Mock search results
    mock_results = [
        {
            'text': 'Cao huyết áp là tình trạng áp lực máu trong động mạch tăng cao. Triệu chứng bao gồm đau đầu, chóng mặt.',
            'metadata': {
                'entity_name': 'Tăng huyết áp',
                'icd_code': 'BA00',
                'category_name': 'Bệnh hệ tuần hoàn',
                'source_type': 'WHO ICD-11'
            },
            'relevance_score': 0.95
        }
    ]
    
    test_cases = [
        {
            'query': 'Cao huyết áp là gì?',
            'intent': 'disease_inquiry'
        },
        {
            'query': 'Tôi bị đau đầu và chóng mặt',
            'intent': 'symptom_inquiry'
        },
        {
            'query': 'Cách điều trị cao huyết áp',
            'intent': 'treatment_inquiry'
        }
    ]
    
    extractor = MedicalStructuredExtractor()
    
    print("\n🧪 Testing Structured Extraction...")
    print("=" * 60)
    
    for case in test_cases:
        print(f"\n🔍 Query: '{case['query']}'")
        print(f"📋 Intent: {case['intent']}")
        
        result = extractor.extract_structured_response(
            mock_results, case['query'], case['intent']
        )
        
        print(f"✅ Schema Type: {result['schema_type']}")
        print(f"🎯 Confidence: {result['confidence_score']:.2f}")
        print(f"📄 Data Fields: {len(result['data'])}")
        print(f"💡 Suggestions: {len(result['follow_up_suggestions'])}")
        print("-" * 40)

if __name__ == "__main__":
    test_structured_extraction()

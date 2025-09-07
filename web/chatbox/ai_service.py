#!/usr/bin/env python3
"""
AI Service Module - OpenRouter DeepSeek Integration
Tích hợp AI để phân tích intent và tạo response thông minh
"""
import json
import time
from typing import Dict, List, Any, Optional
from config import client

class MedicalAIService:
    """Medical AI Service using OpenRouter DeepSeek"""
    
    def __init__(self):
        self.client = client
        self.model = "deepseek/deepseek-chat-v3.1:free"  # Free model on OpenRouter
        self.max_tokens = 2000  # Reduce for faster response
        self.temperature = 0.7
        
        # Add caching to reduce API calls
        self.intent_cache = {}  # Cache intent classifications
        self.response_cache = {}  # Cache generated responses
        self.max_cache_size = 100
        
        self.stats = {
            'total_requests': 0,
            'intent_classifications': 0,
            'response_generations': 0,
            'avg_response_time': 0.0,
            'errors': 0,
            'cache_hits': 0
        }
    
    def classify_intent_with_ai(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Sử dụng AI để phân loại intent thông minh"""
        
        # Check cache first
        cache_key = f"intent_{hash(query)}"
        if cache_key in self.intent_cache:
            self.stats['cache_hits'] += 1
            cached_result = self.intent_cache[cache_key].copy()
            print(f"💾 AI Intent from cache: {cached_result['intent']}")
            return cached_result
        
        start_time = time.time()
        self.stats['total_requests'] += 1
        self.stats['intent_classifications'] += 1
        
        # Tạo context cho AI
        context_str = ""
        if context and context.get('mentioned_entities'):
            entities = ', '.join(context['mentioned_entities'][-3:])  # Last 3 entities
            context_str = f"Bối cảnh cuộc trình: đã đề cập đến {entities}. "
        
        system_prompt = """Bạn là chuyên gia y tế AI. Phân tích câu hỏi y tế của người dùng và trả về JSON với:
1. intent: một trong ["emergency", "symptom_analysis", "disease_inquiry", "treatment_advice", "prevention", "general_medical"]
2. confidence: độ tin cậy (0-1)
3. key_entities: danh sách thuật ngữ y tế quan trọng
4. urgency_level: mức độ khẩn cấp ["low", "medium", "high", "critical"]
5. analysis: phân tích ngắn gọn

Quy tắc phân loại:
- emergency: triệu chứng nguy hiểm, cần cấp cứu ngay
- symptom_analysis: mô tả triệu chứng, muốn hiểu nguyên nhân
- disease_inquiry: hỏi về bệnh cụ thể, thông tin bệnh lý
- treatment_advice: hỏi cách điều trị, thuốc, liệu pháp
- prevention: hỏi cách phòng ngừa bệnh
- general_medical: câu hỏi y tế chung

QUAN TRỌNG: Chỉ trả về JSON hợp lệ, không có text thêm."""

        user_prompt = f"""{context_str}Câu hỏi: "{query}"

Phân tích và trả về JSON:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.3  # Lower temperature for classification
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            try:
                # Look for JSON in the response
                if '{' in result_text and '}' in result_text:
                    start_idx = result_text.find('{')
                    end_idx = result_text.rfind('}') + 1
                    json_text = result_text[start_idx:end_idx]
                    result = json.loads(json_text)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ JSON parsing failed: {e}")
                print(f"Raw response: {result_text[:200]}...")
                raise Exception(f"Failed to parse AI response: {e}")
            
            # Validate and set defaults
            result['intent'] = result.get('intent', 'general_medical')
            result['confidence'] = min(max(result.get('confidence', 0.7), 0.0), 1.0)
            result['key_entities'] = result.get('key_entities', [])
            result['urgency_level'] = result.get('urgency_level', 'low')
            result['analysis'] = result.get('analysis', '')
            
            response_time = time.time() - start_time
            self._update_response_time(response_time)
            
            # Cache successful result
            if len(self.intent_cache) < self.max_cache_size:
                self.intent_cache[cache_key] = result.copy()
            
            print(f"🤖 AI Intent: {result['intent']} (confidence: {result['confidence']:.2f}) in {response_time:.2f}s")
            
            return result
            
        except Exception as e:
            print(f"⚠️ AI Intent classification failed: {e}")
            self.stats['errors'] += 1
            
            # Fallback to rule-based
            return self._fallback_intent_classification(query)
    
    def generate_medical_response(self, query: str, search_results: List[Dict], 
                                 intent_info: Dict, context: Dict = None, stream: bool = False):
        """Sử dụng AI để tạo response thông minh dựa trên search results"""
        
        start_time = time.time()
        self.stats['total_requests'] += 1
        self.stats['response_generations'] += 1
        
        # Chuẩn bị context cho AI
        context_str = ""
        if context and context.get('mentioned_entities'):
            entities = ', '.join(context['mentioned_entities'][-3:])
            context_str = f"Bối cảnh cuộc trò chuyện: đã thảo luận về {entities}. "
        
        # Chuẩn bị medical data
        medical_context = ""
        if search_results:
            medical_context = "Thông tin y tế từ cơ sở dữ liệu ICD-11:\n\n"
            for i, result in enumerate(search_results[:3], 1):
                entity_name = result.get('metadata', {}).get('entity_name', 'Unknown')
                text_snippet = result.get('text', '')[:300]
                medical_context += f"{i}. {entity_name}:\n{text_snippet}\n\n"
        
        # Tạo system prompt dựa trên intent
        intent = intent_info.get('intent', 'general_medical')
        urgency = intent_info.get('urgency_level', 'low')
        
        system_prompts = {
            'emergency': """Bạn là bác sĩ cấp cứu AI. Người dùng có tình huống khẩn cấp. 
- Đánh giá mức độ nghiêm trọng
- Đưa ra hướng dẫn cấp cứu ngay lập tức
- Khuyến nghị gọi 115 hoặc đến bệnh viện
- Sử dụng tone nghiêm túc, khẩn cấp
- Không chẩn đoán chính xác, chỉ đưa ra hướng dẫn an toàn""",

            'symptom_analysis': """Bạn là bác sĩ nội khoa AI chuyên phân tích triệu chứng.
- Phân tích các triệu chứng được mô tả
- Đưa ra các khả năng nguyên nhân (không chẩn đoán chắc chắn)
- Hỏi thêm thông tin nếu cần
- Khuyến nghị thăm khám y tế nếu cần thiết
- Sử dụng tone chuyên nghiệp, thân thiện""",

            'disease_inquiry': """Bạn là bác sĩ chuyên khoa AI cung cấp thông tin bệnh lý.
- Giải thích về bệnh một cách dễ hiểu
- Đưa ra thông tin về nguyên nhân, triệu chứng, điều trị
- Sử dụng thông tin y khoa chính xác
- Khuyến nghị tham khảo chuyên gia
- Sử dụng tone giáo dục, chuyên nghiệp""",

            'treatment_advice': """Bạn là dược sĩ/bác sĩ điều trị AI.
- Đưa ra thông tin về phương pháp điều trị
- Giải thích về thuốc, liệu pháp (không kê đơn cụ thể)
- Lưu ý về tác dụng phụ, chống chỉ định
- Nhấn mạnh tầm quan trọng của chỉ định y tế
- Sử dụng tone cẩn thận, chuyên nghiệp""",

            'prevention': """Bạn là bác sĩ y tế dự phòng AI.
- Đưa ra lời khuyên phòng ngừa bệnh
- Thảo luận về lối sống lành mạnh
- Đề xuất các biện pháp dự phòng cụ thể
- Khuyến nghị tầm soát định kỳ nếu cần
- Sử dụng tone tích cực, khuyến khích""",

            'general_medical': """Bạn là bác sĩ gia đình AI thân thiện.
- Trả lời câu hỏi y tế một cách dễ hiểu
- Cung cấp thông tin sức khỏe chung
- Khuyến khích lối sống lành mạnh
- Luôn nhắc nhở tham khảo ý kiến chuyên gia
- Sử dụng tone thân thiện, dễ gần"""
        }
        
        system_prompt = system_prompts.get(intent, system_prompts['general_medical'])
        
        # Thêm hướng dẫn chung
        system_prompt += """

QUAN TRỌNG:
- Sử dụng tiếng Việt tự nhiên, dễ hiểu
- Không đưa ra chẩn đoán chính xác hoặc kê đơn thuốc cụ thể
- Luôn khuyến nghị tham khảo ý kiến bác sĩ chuyên khoa
- Sử dụng thông tin y tế được cung cấp làm căn cứ
- Trả lời trong khoảng 200-400 từ
- Có thể sử dụng emoji phù hợp để thân thiện hơn"""

        user_prompt = f"""{context_str}

Câu hỏi của bệnh nhân: "{query}"

Intent phân tích: {intent} (mức độ khẩn cấp: {urgency})
Các thực thể y tế quan trọng: {', '.join(intent_info.get('key_entities', []))}

{medical_context}

Hãy đưa ra lời khuyên y tế phù hợp dựa trên thông tin trên:"""

        try:
            if stream:
                # STREAMING MODE - Return generator
                stream_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    stream=True  # Enable real streaming!
                )
                
                full_response = ""
                for chunk in stream_response:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield {
                            'type': 'chunk',
                            'content': content,
                            'full_response': full_response,
                            'intent': intent,
                            'urgency_level': urgency
                        }
                
                # Final response data
                response_time = time.time() - start_time
                self._update_response_time(response_time)
                
                print(f"🤖 AI Streaming completed in {response_time:.2f}s")
                
                yield {
                    'type': 'final',
                    'response': full_response,
                    'ai_generated': True,
                    'response_time': response_time,
                    'intent': intent,
                    'urgency_level': urgency,
                    'model': self.model
                }
                
            else:
                # NON-STREAMING MODE - Original blocking behavior
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=self.max_tokens,
                    temperature=self.temperature
                )
                
                ai_response = response.choices[0].message.content.strip()
                response_time = time.time() - start_time
                self._update_response_time(response_time)
                
                print(f"🤖 AI Response generated in {response_time:.2f}s")
                
                return {
                    'response': ai_response,
                    'ai_generated': True,
                    'response_time': response_time,
                    'intent': intent,
                    'urgency_level': urgency,
                    'model': self.model
                }
            
        except Exception as e:
            print(f"⚠️ AI Response generation failed: {e}")
            self.stats['errors'] += 1
            
            # Fallback to template response
            fallback_result = self._fallback_response_generation(query, search_results, intent_info)
            
            if stream:
                yield {
                    'type': 'final',
                    'response': fallback_result['response'],
                    'ai_generated': False,
                    'response_time': fallback_result.get('response_time', 0),
                    'intent': intent,
                    'urgency_level': urgency,
                    'error': str(e),
                    'model': self.model
                }
            else:
                return fallback_result
    
    def _fallback_intent_classification(self, query: str) -> Dict[str, Any]:
        """Fallback rule-based intent classification"""
        query_lower = query.lower()
        
        # Emergency keywords
        if any(keyword in query_lower for keyword in ['cấp cứu', 'nguy hiểm', 'nghiêm trọng', 'đau ngực', 'khó thở']):
            return {
                'intent': 'emergency',
                'confidence': 0.8,
                'key_entities': [],
                'urgency_level': 'high',
                'analysis': 'Rule-based emergency detection'
            }
        
        # Symptom analysis
        elif any(keyword in query_lower for keyword in ['đau', 'sốt', 'ho', 'buồn nôn', 'triệu chứng']):
            return {
                'intent': 'symptom_analysis',
                'confidence': 0.7,
                'key_entities': [],
                'urgency_level': 'medium',
                'analysis': 'Rule-based symptom detection'
            }
        
        # Disease inquiry
        elif any(keyword in query_lower for keyword in ['bệnh', 'hội chứng', 'rối loạn']):
            return {
                'intent': 'disease_inquiry',
                'confidence': 0.7,
                'key_entities': [],
                'urgency_level': 'low',
                'analysis': 'Rule-based disease inquiry'
            }
        
        # Treatment advice
        elif any(keyword in query_lower for keyword in ['điều trị', 'thuốc', 'chữa', 'cách']):
            return {
                'intent': 'treatment_advice',
                'confidence': 0.6,
                'key_entities': [],
                'urgency_level': 'low',
                'analysis': 'Rule-based treatment inquiry'
            }
        
        else:
            return {
                'intent': 'general_medical',
                'confidence': 0.5,
                'key_entities': [],
                'urgency_level': 'low',
                'analysis': 'Rule-based general classification'
            }
    
    def _fallback_response_generation(self, query: str, search_results: List[Dict], 
                                    intent_info: Dict) -> Dict[str, Any]:
        """Fallback template-based response generation"""
        
        intent = intent_info.get('intent', 'general_medical')
        
        if search_results:
            context = f"Dựa trên thông tin y tế từ ICD-11: {search_results[0].get('text', '')[:200]}..."
        else:
            context = "Không tìm thấy thông tin cụ thể trong cơ sở dữ liệu."
        
        templates = {
            'emergency': f"⚠️ **TÌNH HUỐNG KHẨN CẤP** - Nếu đây là tình huống nghiêm trọng, hãy gọi 115 ngay. {context} Vui lòng tham khảo ý kiến bác sĩ cấp cứu.",
            'symptom_analysis': f"🔍 **PHÂN TÍCH TRIỆU CHỨNG** - {context} Khuyến nghị theo dõi triệu chứng và tham khảo ý kiến bác sĩ nếu cần.",
            'disease_inquiry': f"📚 **THÔNG TIN BỆNH LÝ** - {context} Đây là thông tin tham khảo, vui lòng tham khảo chuyên gia y tế.",
            'treatment_advice': f"💊 **TƯ VẤN ĐIỀU TRỊ** - {context} Mọi quyết định điều trị cần được bác sĩ chỉ định.",
            'general_medical': f"🏥 **THÔNG TIN Y TẾ** - {context} Vui lòng tham khảo ý kiến chuyên gia y tế cho lời khuyên cụ thể."
        }
        
        return {
            'response': templates.get(intent, templates['general_medical']),
            'ai_generated': False,
            'response_time': 0.1,
            'intent': intent,
            'urgency_level': intent_info.get('urgency_level', 'low'),
            'model': 'template_fallback'
        }
    
    def _update_response_time(self, response_time: float):
        """Update average response time statistics"""
        total_requests = self.stats['total_requests']
        current_avg = self.stats['avg_response_time']
        
        self.stats['avg_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """Get AI service statistics"""
        return {
            'total_requests': self.stats['total_requests'],
            'intent_classifications': self.stats['intent_classifications'],
            'response_generations': self.stats['response_generations'],
            'avg_response_time': self.stats['avg_response_time'],
            'errors': self.stats['errors'],
            'error_rate': self.stats['errors'] / max(1, self.stats['total_requests']),
            'model': self.model,
            'status': 'active' if self.stats['errors'] < self.stats['total_requests'] * 0.5 else 'degraded'
        }

# Factory function
def get_medical_ai_service():
    """Get medical AI service instance"""
    return MedicalAIService()

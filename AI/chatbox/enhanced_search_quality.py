#!/usr/bin/env python3
"""
Enhanced Search Quality Module
Cải thiện chất lượng tìm kiếm với medical domain expertise
"""
import re
from typing import List, Dict, Any, Tuple
import numpy as np

class MedicalSearchQualityEnhancer:
    """Cải thiện chất lượng tìm kiếm y tế"""
    
    def __init__(self):
        self.medical_synonyms = self._load_medical_synonyms()
        self.medical_categories = self._load_medical_categories()
        self.relevance_filters = self._setup_relevance_filters()
    
    def _load_medical_synonyms(self) -> Dict[str, List[str]]:
        """Load Vietnamese medical synonyms"""
        return {
            # Diseases - Bệnh lý
            'tiểu đường': ['diabetes', 'đái tháo đường', 'bệnh đường huyết', 'diabetes mellitus'],
            'cao huyết áp': ['hypertension', 'huyết áp cao', 'tăng huyết áp', 'high blood pressure'],
            'viêm phổi': ['pneumonia', 'nhiễm trùng phổi', 'inflammation of lungs'],
            'viêm gan': ['hepatitis', 'nhiễm trùng gan', 'liver inflammation'],
            'ung thư': ['cancer', 'carcinoma', 'tumor', 'neoplasm', 'khối u'],
            'tim mạch': ['cardiovascular', 'cardiac', 'heart disease', 'bệnh tim'],
            'đột quỵ': ['stroke', 'cerebrovascular accident', 'CVA'],
            'hen suyễn': ['asthma', 'bronchial asthma', 'khó thở'],
            'dị ứng': ['allergy', 'allergic reaction', 'hypersensitivity'],
            
            # Symptoms - Triệu chứng  
            'đau đầu': ['headache', 'cephalgia', 'migraine', 'nhức đầu'],
            'sốt': ['fever', 'pyrexia', 'hyperthermia', 'nóng sốt'],
            'ho': ['cough', 'tussis', 'ho khan', 'ho có đờm'],
            'buồn nôn': ['nausea', 'queasiness', 'cảm giác nôn'],
            'nôn': ['vomiting', 'emesis', 'ói mửa'],
            'đau bụng': ['abdominal pain', 'stomach pain', 'belly ache'],
            'tiêu chảy': ['diarrhea', 'loose stool', 'đi lỏng'],
            'táo bón': ['constipation', 'hard stool', 'khó đi cầu'],
            'chóng mặt': ['dizziness', 'vertigo', 'lightheadedness'],
            'mệt mỏi': ['fatigue', 'weakness', 'exhaustion', 'tired'],
            'khó thở': ['dyspnea', 'shortness of breath', 'breathing difficulty'],
            'đau ngực': ['chest pain', 'thoracic pain', 'cardiac pain'],
            
            # Treatments - Điều trị
            'thuốc': ['medication', 'medicine', 'drug', 'pharmaceutical'],
            'điều trị': ['treatment', 'therapy', 'cure', 'medical care'],
            'phẫu thuật': ['surgery', 'operation', 'surgical procedure'],
            'xét nghiệm': ['test', 'examination', 'laboratory test', 'diagnostic test'],
            'vaccine': ['vaccination', 'immunization', 'tiêm chủng'],
            
            # Body parts - Bộ phận cơ thể
            'tim': ['heart', 'cardiac', 'cardio'],
            'gan': ['liver', 'hepatic'],
            'thận': ['kidney', 'renal', 'nephro'],
            'phổi': ['lung', 'pulmonary', 'respiratory'],
            'dạ dày': ['stomach', 'gastric', 'gastro'],
            'ruột': ['intestine', 'bowel', 'gut'],
            'não': ['brain', 'cerebral', 'neuro'],
            'xương': ['bone', 'skeletal', 'osteo']
        }
    
    def _load_medical_categories(self) -> Dict[str, List[str]]:
        """Load medical categories for filtering"""
        return {
            'infectious_diseases': ['virus', 'bacteria', 'infection', 'sepsis', 'pneumonia'],
            'chronic_diseases': ['diabetes', 'hypertension', 'cancer', 'heart disease'],
            'emergency_conditions': ['stroke', 'heart attack', 'trauma', 'poisoning'],
            'mental_health': ['depression', 'anxiety', 'psychiatric', 'mental'],
            'pediatric': ['children', 'infant', 'newborn', 'pediatric'],
            'geriatric': ['elderly', 'aging', 'geriatric', 'senior']
        }
    
    def _setup_relevance_filters(self) -> Dict[str, float]:
        """Setup relevance scoring filters"""
        return {
            'exact_match_boost': 2.0,
            'synonym_match_boost': 1.5,
            'category_match_boost': 1.3,
            'vietnamese_boost': 1.2,
            'medical_term_boost': 1.4,
            'irrelevant_penalty': 0.3
        }
    
    def enhance_query(self, query: str, intent: str = None) -> str:
        """Enhance query với medical synonyms và context"""
        enhanced_query = query.lower().strip()
        
        # Add synonyms for better matching
        query_tokens = enhanced_query.split()
        enhanced_tokens = []
        
        for token in query_tokens:
            enhanced_tokens.append(token)
            
            # Add synonyms if found
            for main_term, synonyms in self.medical_synonyms.items():
                if token in main_term or main_term in token:
                    enhanced_tokens.extend(synonyms[:2])  # Add top 2 synonyms
                    break
        
        # Add intent-specific terms
        if intent:
            intent_terms = {
                'symptom_analysis': ['symptoms', 'signs', 'triệu chứng', 'dấu hiệu'],
                'disease_inquiry': ['disease', 'condition', 'bệnh', 'rối loạn'],
                'emergency': ['urgent', 'emergency', 'cấp cứu', 'khẩn cấp'],
                'treatment': ['treatment', 'therapy', 'điều trị', 'chữa trị']
            }
            
            if intent in intent_terms:
                enhanced_tokens.extend(intent_terms[intent][:2])
        
        # Add medical domain terms
        enhanced_tokens.extend(['medical', 'health', 'clinical', 'y tế', 'sức khỏe'])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tokens = []
        for token in enhanced_tokens:
            if token not in seen:
                seen.add(token)
                unique_tokens.append(token)
        
        return ' '.join(unique_tokens)
    
    def calculate_medical_relevance(self, result: Dict[str, Any], query: str, intent: str = None) -> float:
        """Calculate medical relevance score for search result"""
        
        text = result.get('text', '').lower()
        metadata = result.get('metadata', {})
        entity_name = metadata.get('entity_name', '').lower()
        
        relevance_score = 0.0
        
        # 1. Exact term matching
        query_terms = set(query.lower().split())
        text_terms = set(text.split())
        entity_terms = set(entity_name.split())
        
        exact_matches = len(query_terms.intersection(text_terms.union(entity_terms)))
        relevance_score += exact_matches * self.relevance_filters['exact_match_boost']
        
        # 2. Synonym matching
        synonym_matches = 0
        for term in query_terms:
            for main_term, synonyms in self.medical_synonyms.items():
                if term in main_term or main_term in term:
                    for synonym in synonyms:
                        if synonym in text or synonym in entity_name:
                            synonym_matches += 1
                            break
        
        relevance_score += synonym_matches * self.relevance_filters['synonym_match_boost']
        
        # 3. Medical category matching
        category_score = 0
        for category, terms in self.medical_categories.items():
            for term in terms:
                if term in text or term in entity_name:
                    category_score += 1
        
        relevance_score += category_score * self.relevance_filters['category_match_boost']
        
        # 4. Vietnamese medical terms boost
        vietnamese_medical_terms = ['bệnh', 'triệu chứng', 'điều trị', 'thuốc', 'y tế', 'sức khỏe']
        vietnamese_score = sum(1 for term in vietnamese_medical_terms if term in text)
        relevance_score += vietnamese_score * self.relevance_filters['vietnamese_boost']
        
        # 5. Medical terminology boost
        medical_indicators = ['icd', 'who', 'medical', 'clinical', 'diagnosis', 'treatment']
        medical_score = sum(1 for indicator in medical_indicators if indicator in text.lower())
        relevance_score += medical_score * self.relevance_filters['medical_term_boost']
        
        # 6. Intent-specific scoring
        if intent:
            intent_keywords = {
                'symptom_analysis': ['symptom', 'sign', 'manifestation'],
                'disease_inquiry': ['disease', 'disorder', 'condition'],
                'emergency': ['acute', 'severe', 'critical', 'urgent'],
                'treatment': ['treatment', 'therapy', 'management', 'cure']
            }
            
            if intent in intent_keywords:
                intent_score = sum(1 for keyword in intent_keywords[intent] 
                                 if keyword in text or keyword in entity_name)
                relevance_score += intent_score * 1.2
        
        # 7. Penalty for clearly irrelevant results
        irrelevant_indicators = ['unrelated', 'non-medical', 'administrative']
        if any(indicator in text.lower() for indicator in irrelevant_indicators):
            relevance_score *= self.relevance_filters['irrelevant_penalty']
        
        # Normalize score (0-1 range)
        max_possible_score = 10.0  # Estimated max score
        normalized_score = min(relevance_score / max_possible_score, 1.0)
        
        return normalized_score
    
    def filter_and_rerank_results(self, results: List[Dict[str, Any]], 
                                 query: str, intent: str = None, 
                                 min_relevance: float = 0.1) -> List[Dict[str, Any]]:
        """Filter and re-rank search results based on medical relevance"""
        
        if not results:
            return results
        
        # Calculate medical relevance for each result
        enhanced_results = []
        for result in results:
            medical_relevance = self.calculate_medical_relevance(result, query, intent)
            
            # Only keep results above minimum relevance threshold
            if medical_relevance >= min_relevance:
                result['medical_relevance'] = medical_relevance
                
                # Combine with existing relevance score
                existing_relevance = result.get('relevance_score', result.get('semantic_score', 0))
                combined_score = (existing_relevance * 0.6) + (medical_relevance * 0.4)
                result['combined_relevance'] = combined_score
                
                enhanced_results.append(result)
        
        # Sort by combined relevance score
        enhanced_results.sort(key=lambda x: x['combined_relevance'], reverse=True)
        
        return enhanced_results
    
    def get_query_suggestions(self, query: str) -> List[str]:
        """Generate query suggestions for better search"""
        suggestions = []
        query_lower = query.lower()
        
        # Find related medical terms
        for main_term, synonyms in self.medical_synonyms.items():
            if any(word in query_lower for word in main_term.split()):
                suggestions.append(f"Tìm hiểu về {main_term}")
                suggestions.extend([f"Triệu chứng của {main_term}", 
                                  f"Điều trị {main_term}", 
                                  f"Nguyên nhân {main_term}"])
                break
        
        return suggestions[:5]  # Return top 5 suggestions

# Factory function
def get_search_quality_enhancer():
    """Get search quality enhancer instance"""
    return MedicalSearchQualityEnhancer()

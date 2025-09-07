#!/usr/bin/env python3
"""
Enhanced Confidence Scoring System
Cải thiện hệ thống tính điểm tin cậy cho medical chatbot
"""
from typing import List, Dict, Any, Optional
import numpy as np
from dataclasses import dataclass

@dataclass
class ConfidenceFactors:
    """Factors affecting confidence calculation"""
    search_relevance: float = 0.0
    intent_clarity: float = 0.0  
    context_usage: float = 0.0
    medical_domain_match: float = 0.0
    entity_extraction_quality: float = 0.0
    query_complexity: float = 0.0
    data_source_quality: float = 0.0

class EnhancedConfidenceCalculator:
    """Enhanced confidence calculation for medical responses"""
    
    def __init__(self):
        self.confidence_weights = self._setup_confidence_weights()
        self.intent_confidence_map = self._setup_intent_confidence_map()
        self.medical_domain_keywords = self._setup_medical_domain_keywords()
    
    def _setup_confidence_weights(self) -> Dict[str, float]:
        """Setup weights for different confidence factors"""
        return {
            'search_relevance': 0.35,      # Most important - quality of search results
            'intent_clarity': 0.20,        # How clear the user intent is
            'context_usage': 0.15,         # Whether conversation context was used
            'medical_domain_match': 0.15,  # How well it matches medical domain
            'entity_extraction': 0.10,     # Quality of extracted medical entities
            'data_source_quality': 0.05    # Quality of data sources
        }
    
    def _setup_intent_confidence_map(self) -> Dict[str, float]:
        """Setup base confidence scores for different intents"""
        return {
            'emergency': 0.95,              # High confidence for emergency responses
            'symptom_analysis': 0.80,       # Good confidence for symptom analysis
            'disease_inquiry': 0.85,        # Good confidence for disease info
            'medical_consultation': 0.75,   # Medium confidence for consultation
            'general_medical': 0.60         # Lower confidence for general queries
        }
    
    def _setup_medical_domain_keywords(self) -> Dict[str, List[str]]:
        """Setup medical domain keywords for domain matching"""
        return {
            'high_confidence': [
                'bệnh', 'disease', 'triệu chứng', 'symptom', 'điều trị', 'treatment',
                'chẩn đoán', 'diagnosis', 'thuốc', 'medication', 'bác sĩ', 'doctor'
            ],
            'medium_confidence': [
                'sức khỏe', 'health', 'y tế', 'medical', 'bệnh viện', 'hospital',
                'khám', 'examination', 'xét nghiệm', 'test'
            ],
            'low_confidence': [
                'cảm thấy', 'feel', 'có vẻ', 'seems', 'nghĩ', 'think',
                'có thể', 'maybe', 'không chắc', 'not sure'
            ]
        }
    
    def calculate_search_relevance_confidence(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on search result quality"""
        if not search_results:
            return 0.0
        
        # Get relevance scores
        relevance_scores = []
        for result in search_results:
            score = result.get('relevance_score', 
                             result.get('semantic_score', 
                             result.get('combined_relevance', 0.0)))
            relevance_scores.append(score)
        
        if not relevance_scores:
            return 0.0
        
        # Calculate weighted average (top results matter more)
        weights = [0.5, 0.3, 0.15, 0.05]  # Top 4 results
        weighted_score = 0.0
        total_weight = 0.0
        
        for i, score in enumerate(relevance_scores[:4]):
            weight = weights[i] if i < len(weights) else 0.01
            weighted_score += score * weight
            total_weight += weight
        
        average_score = weighted_score / total_weight if total_weight > 0 else 0.0
        
        # Adjust based on number of good results
        good_results = sum(1 for score in relevance_scores if score > 0.5)
        result_count_factor = min(good_results / 3.0, 1.0)  # Optimal is 3+ good results
        
        # Adjust based on score distribution (consistency)
        if len(relevance_scores) > 1:
            score_std = np.std(relevance_scores[:3])  # Top 3 results
            consistency_factor = max(0.5, 1.0 - score_std)  # Lower std = higher consistency
        else:
            consistency_factor = 1.0
        
        final_confidence = average_score * result_count_factor * consistency_factor
        return min(final_confidence, 1.0)
    
    def calculate_intent_clarity_confidence(self, query: str, intent: str, 
                                          extracted_entities: List[Any] = None) -> float:
        """Calculate confidence based on intent clarity"""
        base_confidence = self.intent_confidence_map.get(intent, 0.5)
        
        query_lower = query.lower()
        
        # Adjust based on query characteristics
        clarity_factors = 1.0
        
        # 1. Question words indicate clear intent
        question_words = ['gì', 'sao', 'như thế nào', 'tại sao', 'khi nào', 'ở đâu']
        if any(word in query_lower for word in question_words):
            clarity_factors *= 1.2
        
        # 2. Specific medical terms increase clarity
        high_conf_terms = sum(1 for term in self.medical_domain_keywords['high_confidence'] 
                             if term in query_lower)
        clarity_factors *= (1.0 + high_conf_terms * 0.1)
        
        # 3. Vague terms decrease clarity
        low_conf_terms = sum(1 for term in self.medical_domain_keywords['low_confidence'] 
                            if term in query_lower)
        clarity_factors *= max(0.5, 1.0 - low_conf_terms * 0.15)
        
        # 4. Query length factor (too short or too long reduces clarity)
        query_length = len(query.split())
        if query_length < 3:
            clarity_factors *= 0.7  # Too short
        elif query_length > 20:
            clarity_factors *= 0.8  # Too long
        else:
            clarity_factors *= 1.0  # Good length
        
        # 5. Entity extraction quality
        if extracted_entities:
            entity_count = len(extracted_entities)
            if entity_count >= 2:
                clarity_factors *= 1.1  # Good entity extraction
            elif entity_count == 0:
                clarity_factors *= 0.8  # No entities found
        
        final_confidence = base_confidence * min(clarity_factors, 1.5)
        return min(final_confidence, 1.0)
    
    def calculate_context_usage_confidence(self, context_used: bool, 
                                         context_quality: Optional[Dict[str, Any]] = None) -> float:
        """Calculate confidence based on conversation context usage"""
        if not context_used:
            return 0.5  # Neutral when no context used
        
        base_confidence = 0.8  # Good confidence when context is used
        
        if context_quality:
            # Adjust based on context quality
            entities_count = len(context_quality.get('mentioned_entities', []))
            if entities_count >= 3:
                base_confidence *= 1.2
            elif entities_count >= 1:
                base_confidence *= 1.1
            
            # Recency of context entities
            # (More recent context is more reliable)
            base_confidence *= 1.0  # Could be enhanced with temporal analysis
        
        return min(base_confidence, 1.0)
    
    def calculate_medical_domain_confidence(self, query: str, search_results: List[Dict[str, Any]],
                                          extracted_entities: List[Any] = None) -> float:
        """Calculate confidence based on medical domain matching"""
        query_lower = query.lower()
        domain_confidence = 0.0
        
        # 1. Query medical content
        high_conf_matches = sum(1 for term in self.medical_domain_keywords['high_confidence'] 
                               if term in query_lower)
        medium_conf_matches = sum(1 for term in self.medical_domain_keywords['medium_confidence'] 
                                 if term in query_lower)
        
        query_medical_score = (high_conf_matches * 0.3 + medium_conf_matches * 0.2) / 2.0
        domain_confidence += min(query_medical_score, 1.0) * 0.4
        
        # 2. Search results medical content
        if search_results:
            medical_results = 0
            for result in search_results[:5]:  # Top 5 results
                text = result.get('text', '').lower()
                metadata = result.get('metadata', {})
                
                # Check for medical indicators
                medical_indicators = ['icd', 'who', 'medical', 'diagnosis', 'treatment', 'disease']
                has_medical_content = any(indicator in text for indicator in medical_indicators)
                
                # Check metadata for medical source
                has_medical_source = any(key in metadata for key in ['entity_code', 'browser_url'])
                
                if has_medical_content or has_medical_source:
                    medical_results += 1
            
            results_medical_score = medical_results / min(len(search_results), 5)
            domain_confidence += results_medical_score * 0.4
        
        # 3. Extracted entities medical relevance
        if extracted_entities:
            medical_entity_types = ['diseases', 'symptoms', 'treatments', 'medications', 'body_parts']
            medical_entities = sum(1 for entity in extracted_entities 
                                  if hasattr(entity, 'entity_type') and 
                                  entity.entity_type in medical_entity_types)
            
            entity_medical_score = min(medical_entities / 3.0, 1.0)  # 3+ entities is optimal
            domain_confidence += entity_medical_score * 0.2
        
        return min(domain_confidence, 1.0)
    
    def calculate_entity_extraction_confidence(self, extracted_entities: List[Any]) -> float:
        """Calculate confidence based on entity extraction quality"""
        if not extracted_entities:
            return 0.3  # Low confidence if no entities extracted
        
        # Average entity confidence
        if hasattr(extracted_entities[0], 'confidence'):
            avg_entity_confidence = np.mean([entity.confidence for entity in extracted_entities])
        else:
            avg_entity_confidence = 0.7  # Default if no confidence scores
        
        # Number of entities factor
        entity_count = len(extracted_entities)
        count_factor = min(entity_count / 3.0, 1.0)  # Optimal is 3+ entities
        
        # Diversity of entity types
        if hasattr(extracted_entities[0], 'entity_type'):
            entity_types = set(entity.entity_type for entity in extracted_entities)
            diversity_factor = min(len(entity_types) / 2.0, 1.0)  # 2+ types is good
        else:
            diversity_factor = 0.8  # Default
        
        final_confidence = avg_entity_confidence * count_factor * diversity_factor
        return min(final_confidence, 1.0)
    
    def calculate_data_source_confidence(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence based on data source quality"""
        if not search_results:
            return 0.0
        
        total_quality = 0.0
        for result in search_results[:3]:  # Top 3 results matter most
            metadata = result.get('metadata', {})
            
            # Check for quality indicators
            quality_score = 0.5  # Base score
            
            # Has ICD code
            if metadata.get('entity_code'):
                quality_score += 0.2
            
            # Has WHO browser URL
            if metadata.get('browser_url') and 'who.int' in metadata.get('browser_url', ''):
                quality_score += 0.2
            
            # Has quality score metadata
            if metadata.get('quality_score'):
                quality_score += 0.1
            
            total_quality += min(quality_score, 1.0)
        
        average_quality = total_quality / min(len(search_results), 3)
        return average_quality
    
    def calculate_overall_confidence(self, 
                                   query: str,
                                   intent: str,
                                   search_results: List[Dict[str, Any]],
                                   context_used: bool = False,
                                   context_quality: Optional[Dict[str, Any]] = None,
                                   extracted_entities: List[Any] = None) -> Dict[str, float]:
        """Calculate overall confidence score with detailed breakdown"""
        
        # Calculate individual confidence factors
        factors = ConfidenceFactors()
        
        factors.search_relevance = self.calculate_search_relevance_confidence(search_results)
        factors.intent_clarity = self.calculate_intent_clarity_confidence(query, intent, extracted_entities)
        factors.context_usage = self.calculate_context_usage_confidence(context_used, context_quality)
        factors.medical_domain_match = self.calculate_medical_domain_confidence(query, search_results, extracted_entities)
        factors.entity_extraction_quality = self.calculate_entity_extraction_confidence(extracted_entities or [])
        factors.data_source_quality = self.calculate_data_source_confidence(search_results)
        
        # Calculate weighted overall confidence
        overall_confidence = (
            factors.search_relevance * self.confidence_weights['search_relevance'] +
            factors.intent_clarity * self.confidence_weights['intent_clarity'] +
            factors.context_usage * self.confidence_weights['context_usage'] +
            factors.medical_domain_match * self.confidence_weights['medical_domain_match'] +
            factors.entity_extraction_quality * self.confidence_weights['entity_extraction'] +
            factors.data_source_quality * self.confidence_weights['data_source_quality']
        )
        
        # Apply final adjustments
        overall_confidence = self._apply_final_adjustments(overall_confidence, factors, intent)
        
        return {
            'overall_confidence': min(overall_confidence, 1.0),
            'breakdown': {
                'search_relevance': factors.search_relevance,
                'intent_clarity': factors.intent_clarity,
                'context_usage': factors.context_usage,
                'medical_domain_match': factors.medical_domain_match,
                'entity_extraction_quality': factors.entity_extraction_quality,
                'data_source_quality': factors.data_source_quality
            },
            'confidence_level': self._get_confidence_level(overall_confidence)
        }
    
    def _apply_final_adjustments(self, base_confidence: float, factors: ConfidenceFactors, intent: str) -> float:
        """Apply final adjustments to confidence score"""
        adjusted_confidence = base_confidence
        
        # Emergency intent boost
        if intent == 'emergency' and factors.search_relevance > 0.6:
            adjusted_confidence = min(adjusted_confidence * 1.1, 1.0)
        
        # Low search relevance penalty
        if factors.search_relevance < 0.3:
            adjusted_confidence *= 0.8
        
        # High medical domain match boost
        if factors.medical_domain_match > 0.8:
            adjusted_confidence = min(adjusted_confidence * 1.05, 1.0)
        
        # Context usage boost
        if factors.context_usage > 0.8:
            adjusted_confidence = min(adjusted_confidence * 1.03, 1.0)
        
        return adjusted_confidence
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Get human-readable confidence level"""
        if confidence >= 0.8:
            return 'high'
        elif confidence >= 0.6:
            return 'medium'
        elif confidence >= 0.4:
            return 'low'
        else:
            return 'very_low'

# Factory function
def get_confidence_calculator():
    """Get enhanced confidence calculator instance"""
    return EnhancedConfidenceCalculator()

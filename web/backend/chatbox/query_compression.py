#!/usr/bin/env python3
"""
Query Compression Module
Giảm độ phức tạp query để tăng tốc search
"""
import re
import hashlib
from typing import List, Dict, Any, Set, Tuple
from functools import lru_cache
from dataclasses import dataclass

@dataclass
class CompressedQuery:
    """Compressed query with metadata"""
    original: str
    compressed: str
    keywords: List[str]
    intent_keywords: List[str]
    medical_terms: List[str]
    compression_ratio: float
    priority_terms: List[str]

class MedicalQueryCompressor:
    """Intelligent query compression for medical search"""
    
    def __init__(self):
        self.stop_words = self._build_stop_words()
        self.medical_synonyms = self._build_medical_synonyms()
        self.intent_patterns = self._build_intent_patterns()
        self.priority_terms = self._build_priority_terms()
        self.compression_cache = {}
    
    def _build_stop_words(self) -> Set[str]:
        """Build Vietnamese stop words for removal"""
        return {
            # Pronouns and articles
            'tôi', 'em', 'anh', 'chị', 'bạn', 'mình', 'ta', 'chúng ta',
            'của', 'cho', 'với', 'từ', 'trong', 'ngoài', 'trên', 'dưới', 'về',
            
            # Question fillers
            'có', 'là', 'không', 'thì', 'mà', 'rồi', 'đã', 'sẽ', 'đang',
            'ạ', 'ở', 'à', 'vậy', 'nha', 'nhé', 'hả', 'hở',
            
            # Polite expressions
            'xin chào', 'cảm ơn', 'xin lỗi', 'cho hỏi', 'cho em hỏi',
            'bác sĩ ơi', 'thưa bác sĩ',
            
            # Common fillers
            'có thể', 'có lẽ', 'có phải', 'có sao', 'thế nào', 'như thế nào',
            'bao giờ', 'khi nào', 'ở đâu', 'tại sao', 'vì sao'
        }
    
    def _build_medical_synonyms(self) -> Dict[str, str]:
        """Build medical synonym mapping for standardization"""
        return {
            # Standardize disease names
            'đái tháo đường': 'tiểu đường',
            'bệnh tiểu đường': 'tiểu đường',
            'huyết áp cao': 'cao huyết áp',
            'tăng huyết áp': 'cao huyết áp',
            'nhức đầu': 'đau đầu',
            'đau đầu nhức óc': 'đau đầu',
            
            # Standardize symptoms
            'buồn nôn muốn ói': 'buồn nôn',
            'cảm thấy buồn nôn': 'buồn nôn',
            'nóng sốt': 'sốt',
            'bị sốt': 'sốt',
            'ho khan': 'ho',
            'ho có đờm': 'ho',
            'bị ho': 'ho',
            
            # Standardize body parts
            'đầu óc': 'đầu',
            'bụng dưới': 'bụng',
            'bụng trên': 'bụng',
            'ngực trái': 'ngực',
            'ngực phải': 'ngực',
            
            # Common expressions
            'bị mắc': 'bị',
            'đang bị': 'bị',
            'có vẻ như': '',
            'có triệu chứng': 'triệu chứng',
            'xuất hiện triệu chứng': 'triệu chứng'
        }
    
    def _build_intent_patterns(self) -> Dict[str, List[str]]:
        """Build intent-specific keyword patterns"""
        return {
            'symptom_analysis': [
                'triệu chứng', 'dấu hiệu', 'biểu hiện', 'cảm giác', 'thấy'
            ],
            'disease_inquiry': [
                'bệnh', 'chứng', 'rối loạn', 'hội chứng', 'tình trạng'
            ],
            'treatment': [
                'điều trị', 'chữa', 'uống thuốc', 'dùng thuốc', 'thuốc', 'cách chữa'
            ],
            'emergency': [
                'cấp cứu', 'nguy hiểm', 'nghiêm trọng', 'gấp', 'khẩn cấp'
            ],
            'prevention': [
                'phòng ngừa', 'tránh', 'dự phòng', 'ngăn ngừa'
            ]
        }
    
    def _build_priority_terms(self) -> Set[str]:
        """Build high-priority medical terms that should never be removed"""
        return {
            # Critical symptoms
            'đau đầu', 'sốt', 'ho', 'buồn nôn', 'nôn', 'tiêu chảy', 'táo bón',
            'chóng mặt', 'khó thở', 'đau ngực', 'đau bụng', 'mệt mỏi',
            
            # Critical diseases
            'tiểu đường', 'cao huyết áp', 'ung thư', 'đột quỵ', 'tim mạch',
            'viêm gan', 'viêm phổi', 'hen suyễn', 'dị ứng', 'cúm',
            
            # Body parts
            'tim', 'gan', 'thận', 'phổi', 'não', 'dạ dày', 'ruột',
            
            # Treatments
            'thuốc', 'điều trị', 'phẫu thuật', 'xét nghiệm'
        }
    
    @lru_cache(maxsize=500)
    def compress_query(self, query: str, target_length: int = 50) -> CompressedQuery:
        """Compress query intelligently while preserving meaning"""
        
        original_query = query.strip()
        
        # Check cache first
        cache_key = hashlib.md5(f"{query}_{target_length}".encode()).hexdigest()
        if cache_key in self.compression_cache:
            return self.compression_cache[cache_key]
        
        # Step 1: Normalize and clean
        normalized = self._normalize_query(query)
        
        # Step 2: Extract and preserve critical terms
        critical_terms = self._extract_critical_terms(normalized)
        
        # Step 3: Apply medical synonym standardization
        standardized = self._apply_medical_synonyms(normalized)
        
        # Step 4: Remove stop words and fillers
        filtered = self._remove_stop_words(standardized)
        
        # Step 5: Extract keywords by importance
        keywords = self._extract_keywords_by_importance(filtered)
        
        # Step 6: Build compressed query
        compressed = self._build_compressed_query(keywords, critical_terms, target_length)
        
        # Step 7: Extract metadata
        intent_keywords = self._extract_intent_keywords(normalized)
        medical_terms = self._extract_medical_terms(compressed)
        
        # Calculate compression ratio
        compression_ratio = len(compressed) / len(original_query) if original_query else 1.0
        
        result = CompressedQuery(
            original=original_query,
            compressed=compressed,
            keywords=keywords,
            intent_keywords=intent_keywords,
            medical_terms=medical_terms,
            compression_ratio=compression_ratio,
            priority_terms=list(critical_terms)
        )
        
        # Cache result
        self.compression_cache[cache_key] = result
        
        return result
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query text"""
        # Convert to lowercase
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove special characters but keep Vietnamese
        normalized = re.sub(r'[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]', ' ', normalized)
        
        # Remove punctuation at start/end of words
        normalized = re.sub(r'\b[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+|[^\w\sàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]+\b', ' ', normalized)
        
        return normalized.strip()
    
    def _extract_critical_terms(self, query: str) -> Set[str]:
        """Extract critical medical terms that must be preserved"""
        critical_terms = set()
        words = query.split()
        
        # Single word critical terms
        for word in words:
            if word in self.priority_terms:
                critical_terms.add(word)
        
        # Multi-word critical terms
        for term in self.priority_terms:
            if ' ' in term and term in query:
                critical_terms.add(term)
        
        return critical_terms
    
    def _apply_medical_synonyms(self, query: str) -> str:
        """Apply medical synonym standardization"""
        result = query
        
        # Apply synonyms in order of length (longer first)
        for old_term, new_term in sorted(self.medical_synonyms.items(), 
                                       key=lambda x: len(x[0]), reverse=True):
            result = result.replace(old_term, new_term)
        
        return result
    
    def _remove_stop_words(self, query: str) -> str:
        """Remove stop words and fillers"""
        words = query.split()
        
        # Remove stop words
        filtered_words = []
        for word in words:
            if word not in self.stop_words and len(word) > 1:
                filtered_words.append(word)
        
        # Remove common phrases
        result = ' '.join(filtered_words)
        
        # Remove remaining filler phrases
        filler_phrases = [
            'có sao không', 'có nguy hiểm không', 'có gì không',
            'thế nào', 'ra sao', 'như thế nào', 'có phải không'
        ]
        
        for phrase in filler_phrases:
            result = result.replace(phrase, '')
        
        return re.sub(r'\s+', ' ', result).strip()
    
    def _extract_keywords_by_importance(self, query: str) -> List[str]:
        """Extract keywords ordered by medical importance"""
        words = query.split()
        
        # Score words by importance
        word_scores = {}
        for word in words:
            score = 0
            
            # Medical term bonus
            if word in self.priority_terms:
                score += 10
            
            # Length bonus (longer words often more specific)
            score += len(word) * 0.5
            
            # Medical context bonus
            if any(word in pattern for pattern in self.intent_patterns.values()):
                score += 5
            
            word_scores[word] = score
        
        # Sort by score
        sorted_words = sorted(word_scores.items(), key=lambda x: x[1], reverse=True)
        
        return [word for word, score in sorted_words if score > 0]
    
    def _build_compressed_query(self, keywords: List[str], critical_terms: Set[str], 
                               target_length: int) -> str:
        """Build compressed query from keywords"""
        # Always include critical terms first
        essential_terms = list(critical_terms)
        
        # Add high-priority keywords
        additional_terms = []
        for keyword in keywords:
            if keyword not in critical_terms:
                additional_terms.append(keyword)
        
        # Combine terms within target length
        compressed_terms = essential_terms.copy()
        current_length = len(' '.join(compressed_terms))
        
        for term in additional_terms:
            potential_length = current_length + len(term) + 1  # +1 for space
            if potential_length <= target_length:
                compressed_terms.append(term)
                current_length = potential_length
            else:
                break
        
        return ' '.join(compressed_terms)
    
    def _extract_intent_keywords(self, query: str) -> List[str]:
        """Extract intent-specific keywords"""
        intent_keywords = []
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in query:
                    intent_keywords.append(pattern)
        
        return intent_keywords
    
    def _extract_medical_terms(self, query: str) -> List[str]:
        """Extract medical terms from query"""
        medical_terms = []
        words = query.split()
        
        for word in words:
            if word in self.priority_terms:
                medical_terms.append(word)
        
        return medical_terms
    
    def get_compression_suggestions(self, query: str) -> Dict[str, Any]:
        """Get compression suggestions and analysis"""
        compressed = self.compress_query(query)
        
        return {
            'original_length': len(query),
            'compressed_length': len(compressed.compressed),
            'compression_ratio': compressed.compression_ratio,
            'bytes_saved': len(query.encode()) - len(compressed.compressed.encode()),
            'keywords_extracted': len(compressed.keywords),
            'medical_terms_found': len(compressed.medical_terms),
            'critical_terms_preserved': len(compressed.priority_terms),
            'intent_keywords': compressed.intent_keywords,
            'recommendations': self._get_compression_recommendations(compressed)
        }
    
    def _get_compression_recommendations(self, compressed: CompressedQuery) -> List[str]:
        """Get recommendations for compression optimization"""
        recommendations = []
        
        if compressed.compression_ratio > 0.8:
            recommendations.append("Query can be compressed further for faster search")
        
        if len(compressed.medical_terms) == 0:
            recommendations.append("No medical terms detected - consider adding specific medical keywords")
        
        if len(compressed.intent_keywords) == 0:
            recommendations.append("Query intent unclear - consider adding question words")
        
        if len(compressed.keywords) < 3:
            recommendations.append("Query very short - may need more context for accurate results")
        
        if compressed.compression_ratio < 0.3:
            recommendations.append("High compression achieved - verify important information preserved")
        
        return recommendations
    
    def batch_compress_queries(self, queries: List[str], target_length: int = 50) -> List[CompressedQuery]:
        """Compress multiple queries efficiently"""
        return [self.compress_query(query, target_length) for query in queries]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get compression cache statistics"""
        return {
            'cache_size': len(self.compression_cache),
            'cache_hit_rate': getattr(self, '_cache_hits', 0) / max(getattr(self, '_cache_attempts', 1), 1),
            'medical_synonyms': len(self.medical_synonyms),
            'priority_terms': len(self.priority_terms),
            'stop_words': len(self.stop_words)
        }

# Factory function
def get_query_compressor():
    """Get medical query compressor instance"""
    return MedicalQueryCompressor()

"""
Hybrid Search System for Medical RAG
Kết hợp Semantic Search (FAISS) với Keyword Search (BM25)
để tăng độ chính xác trong tìm kiếm y tế
"""

import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.preprocessing import MinMaxScaler
import nltk
import re
from typing import List, Dict, Any, Tuple
import pickle
import os
from medical_rag_utils import load_medical_data
import jieba  # For text segmentation

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    try:
        nltk.download('punkt', quiet=True)
    except:
        print("⚠️ Could not download NLTK punkt tokenizer")

class MedicalHybridSearch:
    """
    Hybrid Search System combining:
    1. Semantic Search (FAISS + SentenceTransformers)
    2. Keyword Search (BM25)
    3. Medical term boost
    """
    
    def __init__(self):
        self.faiss_index = None
        self.chunks_data = None
        self.embedder = None
        self.bm25_model = None
        self.tokenized_corpus = None
        self.medical_terms = set()
        self._load_data()
        self._prepare_bm25()
        self._load_medical_terms()
    
    def _load_data(self):
        """Load medical FAISS data"""
        try:
            self.faiss_index, self.chunks_data, self.embedder = load_medical_data()
            if not all([self.faiss_index, self.chunks_data, self.embedder]):
                raise ValueError("Failed to load medical data")
            print("✅ Medical data loaded successfully for hybrid search")
        except Exception as e:
            print(f"❌ Error loading medical data: {e}")
    
    def _tokenize_vietnamese_text(self, text: str) -> List[str]:
        """
        Improved Vietnamese text tokenization for BM25
        """
        # Normalize text
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize spaces
        
        # Extract medical keywords and common Vietnamese words
        words = text.split()
        
        # Enhanced tokenization for Vietnamese medical text
        enhanced_words = []
        for word in words:
            if len(word) >= 2:
                enhanced_words.append(word)
                
                # Add partial matches for compound Vietnamese words
                if len(word) > 4:
                    # Add prefix and suffix for better matching
                    enhanced_words.extend([word[:3], word[-3:]])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_words = []
        for word in enhanced_words:
            if word not in seen:
                seen.add(word)
                unique_words.append(word)
        
        return unique_words
    
    def _prepare_bm25(self):
        """Prepare BM25 model from medical corpus"""
        if not self.chunks_data:
            print("❌ No chunks data available for BM25")
            return
        
        print("🔄 Preparing BM25 model...")
        
        # Extract all text chunks
        texts = [chunk['text'] for chunk in self.chunks_data]
        
        # Tokenize all texts
        self.tokenized_corpus = [self._tokenize_vietnamese_text(text) for text in texts]
        
        # Create BM25 model
        self.bm25_model = BM25Okapi(self.tokenized_corpus)
        
        print(f"✅ BM25 model prepared with {len(texts)} documents")
    
    def _load_medical_terms(self):
        """Load important medical terms for boosting"""
        medical_terms_list = [
            # Vietnamese medical terms
            'triệu chứng', 'bệnh', 'điều trị', 'thuốc', 'nhiễm trùng', 'viêm',
            'đau', 'sốt', 'ho', 'khó thở', 'buồn nôn', 'chóng mặt', 'mệt mỏi',
            'tiểu đường', 'cao huyết áp', 'tim mạch', 'ung thư', 'rối loạn',
            'hội chứng', 'chẩn đoán', 'phòng ngừa', 'vaccine', 'kháng sinh',
            'virus', 'vi khuẩn', 'miễn dịch', 'dị ứng', 'gen', 'di truyền',
            
            # ICD-11 related terms
            'icd', 'who', 'classification', 'disease', 'disorder', 'syndrome',
            'condition', 'symptom', 'treatment', 'prevention', 'diagnosis',
            'medication', 'therapy', 'infection', 'inflammation', 'chronic',
            'acute', 'fever', 'pain', 'headache', 'respiratory', 'cardiac'
        ]
        
        self.medical_terms = set(term.lower() for term in medical_terms_list)
    
    def _calculate_medical_term_boost(self, text: str, query: str) -> float:
        """Calculate boost score based on medical terms overlap"""
        text_tokens = set(self._tokenize_vietnamese_text(text))
        query_tokens = set(self._tokenize_vietnamese_text(query))
        
        # Count medical terms in both text and query
        text_medical_terms = text_tokens.intersection(self.medical_terms)
        query_medical_terms = query_tokens.intersection(self.medical_terms)
        common_medical_terms = text_medical_terms.intersection(query_medical_terms)
        
        if not query_medical_terms:
            return 1.0
        
        # Boost based on medical term overlap
        overlap_ratio = len(common_medical_terms) / len(query_medical_terms)
        boost = 1.0 + (overlap_ratio * 0.3)  # Up to 30% boost
        
        return boost
    
    def hybrid_search(self, query: str, top_k: int = 10, semantic_weight: float = 0.9, 
                     keyword_weight: float = 0.1) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining semantic and keyword search
        
        Args:
            query: Search query
            top_k: Number of results to return
            semantic_weight: Weight for semantic search (0-1)
            keyword_weight: Weight for keyword search (0-1)
        
        Returns:
            List of search results with hybrid scores
        """
        if not all([self.faiss_index, self.chunks_data, self.embedder, self.bm25_model]):
            print("❌ Hybrid search not properly initialized")
            return []
        
        # Normalize weights
        total_weight = semantic_weight + keyword_weight
        semantic_weight = semantic_weight / total_weight
        keyword_weight = keyword_weight / total_weight
        
        # 1. Semantic Search with FAISS
        semantic_results = self._semantic_search(query, top_k * 2)  # Get more candidates
        
        # 2. Keyword Search with BM25
        keyword_results = self._keyword_search(query, top_k * 2)
        
        # If BM25 returns no results, return pure semantic with query enhancement
        if not keyword_results or all(r['bm25_score'] == 0 for r in keyword_results):
            print("⚠️ BM25 found no relevant results, using pure semantic search")
            
            # Apply Vietnamese query enhancement
            from medical_rag_utils import improve_vietnamese_query
            enhanced_query = improve_vietnamese_query(query)
            if enhanced_query != query:
                enhanced_results = self._semantic_search(enhanced_query, top_k)
                if enhanced_results:
                    semantic_results = enhanced_results
            
            # Return semantic results with relevance_score format
            for result in semantic_results:
                result['relevance_score'] = result['semantic_score']
                result['hybrid_score'] = result['semantic_score']
                result['search_method'] = 'semantic_enhanced'
            
            return semantic_results[:top_k]
        
        # 3. Combine and re-score results
        combined_results = self._combine_results(
            semantic_results, keyword_results, query,
            semantic_weight, keyword_weight
        )
        
        # 4. Sort by hybrid score and return top_k
        combined_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        return combined_results[:top_k]
    
    def _semantic_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform semantic search using same method as medical_rag_utils"""
        try:
            # Use the same search method as medical_rag_utils for consistency
            from medical_rag_utils import search_medical_symptoms_and_diseases
            
            results = search_medical_symptoms_and_diseases(query, top_k=top_k)
            
            # Convert to hybrid search format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'index': result.get('index', 0),
                    'text': result['text'],
                    'metadata': result['metadata'],
                    'semantic_score': result['relevance_score'],
                    'distance': 1.0 - result['relevance_score']  # Convert back to distance
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"❌ Semantic search error: {e}")
            return []
    
    def _keyword_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Perform keyword search using BM25"""
        try:
            # Tokenize query
            tokenized_query = self._tokenize_vietnamese_text(query)
            
            if not tokenized_query:
                return []
            
            # Get BM25 scores
            bm25_scores = self.bm25_model.get_scores(tokenized_query)
            
            # Get top indices
            top_indices = np.argsort(bm25_scores)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if idx < len(self.chunks_data) and bm25_scores[idx] > 0:
                    chunk_data = self.chunks_data[idx]
                    
                    results.append({
                        'index': int(idx),
                        'text': chunk_data['text'],
                        'metadata': chunk_data['metadata'],
                        'bm25_score': float(bm25_scores[idx])
                    })
            
            return results
            
        except Exception as e:
            print(f"❌ Keyword search error: {e}")
            return []
    
    def _combine_results(self, semantic_results: List[Dict], keyword_results: List[Dict], 
                        query: str, semantic_weight: float, keyword_weight: float) -> List[Dict[str, Any]]:
        """Combine semantic and keyword search results"""
        
        # Create dictionaries for easy lookup
        semantic_dict = {result['index']: result for result in semantic_results}
        keyword_dict = {result['index']: result for result in keyword_results}
        
        # Get all unique indices
        all_indices = set(semantic_dict.keys()) | set(keyword_dict.keys())
        
        combined_results = []
        
        # Normalize scores for fair combination
        if semantic_results:
            max_semantic = max(r['semantic_score'] for r in semantic_results)
            min_semantic = min(r['semantic_score'] for r in semantic_results)
            semantic_range = max_semantic - min_semantic if max_semantic != min_semantic else 1
        
        if keyword_results:
            max_bm25 = max(r['bm25_score'] for r in keyword_results)
            min_bm25 = min(r['bm25_score'] for r in keyword_results) 
            bm25_range = max_bm25 - min_bm25 if max_bm25 != min_bm25 else 1
        
        for idx in all_indices:
            # Get semantic score (normalized)
            semantic_score = 0
            if idx in semantic_dict and semantic_results:
                raw_score = semantic_dict[idx]['semantic_score']
                semantic_score = (raw_score - min_semantic) / semantic_range if semantic_range > 0 else raw_score
            
            # Get keyword score (normalized)
            keyword_score = 0
            if idx in keyword_dict and keyword_results:
                raw_score = keyword_dict[idx]['bm25_score']
                keyword_score = (raw_score - min_bm25) / bm25_range if bm25_range > 0 else raw_score
            
            # Get chunk data (prefer semantic result if available)
            chunk_info = semantic_dict.get(idx) or keyword_dict.get(idx)
            
            if chunk_info:
                # Calculate medical term boost
                medical_boost = self._calculate_medical_term_boost(chunk_info['text'], query)
                
                # Calculate hybrid score
                hybrid_score = (
                    semantic_weight * semantic_score + 
                    keyword_weight * keyword_score
                ) * medical_boost
                
                result = {
                    'index': idx,
                    'text': chunk_info['text'],
                    'metadata': chunk_info['metadata'],
                    'semantic_score': semantic_score,
                    'keyword_score': keyword_score,
                    'medical_boost': medical_boost,
                    'hybrid_score': hybrid_score,
                    'search_method': self._get_search_method(idx, semantic_dict, keyword_dict)
                }
                
                combined_results.append(result)
        
        return combined_results
    
    def _get_search_method(self, idx: int, semantic_dict: Dict, keyword_dict: Dict) -> str:
        """Determine which search method found this result"""
        in_semantic = idx in semantic_dict
        in_keyword = idx in keyword_dict
        
        if in_semantic and in_keyword:
            return "hybrid"
        elif in_semantic:
            return "semantic"
        else:
            return "keyword"


# Global instance for use in other modules
hybrid_search_engine = None

def initialize_hybrid_search():
    """Initialize global hybrid search engine"""
    global hybrid_search_engine
    try:
        hybrid_search_engine = MedicalHybridSearch()
        return True
    except Exception as e:
        print(f"❌ Failed to initialize hybrid search: {e}")
        return False

def get_hybrid_search_engine():
    """Get the global hybrid search engine instance"""
    global hybrid_search_engine
    if hybrid_search_engine is None:
        initialize_hybrid_search()
    return hybrid_search_engine

# Test function
def test_hybrid_search():
    """Test hybrid search functionality"""
    search_engine = MedicalHybridSearch()
    
    test_queries = [
        "đau đầu và chóng mặt",
        "triệu chứng tiểu đường",
        "cách điều trị cao huyết áp",
        "vaccine phòng covid-19",
        "viêm phổi ở trẻ em"
    ]
    
    print("\n🧪 Testing Hybrid Search System...")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        results = search_engine.hybrid_search(query, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                metadata = result['metadata']
                entity_name = metadata.get('entity_name', 'Unknown')
                hybrid_score = result['hybrid_score']
                search_method = result['search_method']
                
                print(f"  {i}. {entity_name}")
                print(f"     Hybrid Score: {hybrid_score:.3f} ({search_method})")
                print(f"     Semantic: {result['semantic_score']:.3f}, Keyword: {result['keyword_score']:.3f}")
        else:
            print("  ❌ No results found")

if __name__ == "__main__":
    test_hybrid_search()

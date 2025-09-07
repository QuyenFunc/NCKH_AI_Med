#!/usr/bin/env python3
"""
Optimized Hybrid Search - Target < 2s response time
Tối ưu hóa hybrid search để đạt thời gian phản hồi < 2s
"""
import time
import numpy as np
from typing import List, Dict, Any, Optional
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import pickle
from functools import lru_cache
from rank_bm25 import BM25Okapi
import jieba

class FastMedicalHybridSearch:
    """Optimized Medical Hybrid Search với performance focus"""
    
    def __init__(self, chunks_data: List[Dict], medical_rag_utils=None):
        self.chunks_data = chunks_data
        self.medical_rag_utils = medical_rag_utils
        
        # Performance optimizations
        self.bm25_model = None
        self.search_cache = {}  # Fast search cache
        self.max_cache_size = 500
        self.tokenized_cache = {}  # Cache for tokenized texts
        
        # Threading for parallel processing
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Pre-computed medical terms for faster matching
        self.medical_terms_set = self._precompute_medical_terms()
        
        # Initialize systems
        self._fast_prepare_bm25()
        print("✅ Fast hybrid search initialized")
    
    def _precompute_medical_terms(self) -> set:
        """Pre-compute medical terms set for O(1) lookup"""
        medical_terms = {
            # Vietnamese medical terms
            'bệnh', 'triệu chứng', 'điều trị', 'thuốc', 'y tế', 'sức khỏe',
            'đau', 'sốt', 'ho', 'buồn nôn', 'nôn', 'tiêu chảy', 'táo bón',
            'chóng mặt', 'mệt mỏi', 'khó thở', 'đau ngực', 'đau đầu',
            'tiểu đường', 'cao huyết áp', 'viêm gan', 'viêm phổi', 'ung thư',
            'tim mạch', 'đột quỵ', 'hen suyễn', 'dị ứng', 'cúm',
            
            # English medical terms
            'disease', 'symptom', 'treatment', 'medicine', 'medical', 'health',
            'pain', 'fever', 'cough', 'nausea', 'vomiting', 'diarrhea',
            'diabetes', 'hypertension', 'cancer', 'stroke', 'asthma'
        }
        return medical_terms
    
    def _fast_prepare_bm25(self):
        """Fast BM25 preparation với caching và optimization"""
        print("🔄 Fast preparing BM25 model...")
        start_time = time.time()
        
        # Check if we have cached tokenized corpus
        cache_key = f"bm25_corpus_{len(self.chunks_data)}"
        
        if cache_key in self.tokenized_cache:
            tokenized_corpus = self.tokenized_cache[cache_key]
        else:
            # Parallel tokenization for speed
            texts = [chunk.get('text', '') for chunk in self.chunks_data]
            
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(self._fast_tokenize, text) for text in texts]
                tokenized_corpus = [future.result() for future in futures]
            
            # Cache the result
            self.tokenized_cache[cache_key] = tokenized_corpus
        
        # Initialize BM25 with optimized parameters
        self.bm25_model = BM25Okapi(tokenized_corpus, k1=1.2, b=0.4)  # Tuned parameters
        
        prep_time = time.time() - start_time
        print(f"✅ Fast BM25 prepared in {prep_time:.2f}s with {len(self.chunks_data)} documents")
    
    @lru_cache(maxsize=1000)
    def _fast_tokenize(self, text: str) -> List[str]:
        """Fast tokenization với caching"""
        if not text:
            return []
        
        # Simple and fast tokenization
        text_lower = text.lower()
        
        # Split by common separators first (fastest)
        tokens = []
        for separator in [' ', '\n', '\t', '.', ',', ';', ':', '!', '?']:
            if separator in text_lower:
                parts = text_lower.split(separator)
                tokens.extend([part.strip() for part in parts if part.strip()])
            else:
                tokens.append(text_lower.strip())
        
        # Remove duplicates while preserving order (fast)
        seen = set()
        unique_tokens = []
        for token in tokens:
            if token and len(token) > 1 and token not in seen:
                seen.add(token)
                unique_tokens.append(token)
        
        return unique_tokens[:50]  # Limit tokens for performance
    
    def _fast_semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Fast semantic search với timeout"""
        try:
            if self.medical_rag_utils:
                # Use existing semantic search with timeout
                start_time = time.time()
                results = self.medical_rag_utils.search_medical_symptoms_and_diseases(query, top_k=top_k)
                search_time = time.time() - start_time
                
                # Add timing metadata
                for result in results:
                    result['search_time'] = search_time
                
                return results
            return []
        except Exception as e:
            print(f"⚠️ Fast semantic search failed: {e}")
            return []
    
    def _fast_keyword_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Fast BM25 keyword search"""
        if not self.bm25_model:
            return []
        
        try:
            start_time = time.time()
            
            # Fast query tokenization
            query_tokens = self._fast_tokenize(query)
            if not query_tokens:
                return []
            
            # BM25 scoring
            scores = self.bm25_model.get_scores(query_tokens)
            
            # Fast top-k selection using argpartition (faster than sort)
            if len(scores) > top_k:
                top_indices = np.argpartition(scores, -top_k)[-top_k:]
                top_indices = top_indices[np.argsort(scores[top_indices])[::-1]]
            else:
                top_indices = np.argsort(scores)[::-1]
            
            results = []
            for idx in top_indices:
                if idx < len(self.chunks_data) and scores[idx] > 0:
                    result = self.chunks_data[idx].copy()
                    result['keyword_score'] = float(scores[idx])
                    result['search_time'] = time.time() - start_time
                    results.append(result)
                    
                    if len(results) >= top_k:
                        break
            
            return results
            
        except Exception as e:
            print(f"⚠️ Fast keyword search failed: {e}")
            return []
    
    def _fast_combine_results(self, semantic_results: List[Dict], keyword_results: List[Dict],
                             semantic_weight: float = 0.7, keyword_weight: float = 0.3) -> List[Dict]:
        """Fast result combination với optimized algorithm"""
        
        if not semantic_results and not keyword_results:
            return []
        
        if not semantic_results:
            # Only keyword results - normalize scores
            for result in keyword_results:
                result['relevance_score'] = result.get('keyword_score', 0) * keyword_weight
            return keyword_results
        
        if not keyword_results:
            # Only semantic results
            for result in semantic_results:
                result['relevance_score'] = result.get('semantic_score', 0) * semantic_weight
            return semantic_results
        
        # Fast combination using hash map for O(1) lookup
        result_map = {}
        
        # Add semantic results
        for result in semantic_results:
            key = result.get('text', '')[:100]  # Use first 100 chars as key
            result_map[key] = result.copy()
            result_map[key]['semantic_score'] = result.get('semantic_score', 0)
            result_map[key]['keyword_score'] = 0.0
        
        # Merge keyword results
        for result in keyword_results:
            key = result.get('text', '')[:100]
            if key in result_map:
                result_map[key]['keyword_score'] = result.get('keyword_score', 0)
            else:
                new_result = result.copy()
                new_result['semantic_score'] = 0.0
                new_result['keyword_score'] = result.get('keyword_score', 0)
                result_map[key] = new_result
        
        # Calculate combined scores
        combined_results = []
        for result in result_map.values():
            # Normalize scores
            semantic_score = result.get('semantic_score', 0)
            keyword_score = result.get('keyword_score', 0)
            
            # Apply medical boost for better relevance
            medical_boost = self._calculate_medical_boost(result)
            
            combined_score = (semantic_score * semantic_weight + 
                            keyword_score * keyword_weight) * medical_boost
            
            result['relevance_score'] = combined_score
            result['medical_boost'] = medical_boost
            combined_results.append(result)
        
        # Fast sort and return top results
        combined_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return combined_results[:10]  # Return top 10
    
    def _calculate_medical_boost(self, result: Dict[str, Any]) -> float:
        """Fast medical relevance boost calculation"""
        text = result.get('text', '').lower()
        metadata = result.get('metadata', {})
        
        boost = 1.0
        
        # Fast medical term check using pre-computed set
        text_words = set(text.split()[:20])  # Only check first 20 words for speed
        medical_matches = len(text_words.intersection(self.medical_terms_set))
        
        if medical_matches > 0:
            boost += medical_matches * 0.1  # 10% boost per medical term
        
        # Quick metadata check
        if metadata.get('entity_code') or 'who.int' in metadata.get('browser_url', ''):
            boost += 0.2
        
        return min(boost, 2.0)  # Cap at 2x boost
    
    def fast_hybrid_search(self, query: str, top_k: int = 5, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Ultra-fast hybrid search với aggressive caching"""
        total_start_time = time.time()
        
        # Check cache first
        if use_cache:
            cache_key = hashlib.md5(f"{query}_{top_k}".encode()).hexdigest()
            if cache_key in self.search_cache:
                cached_result = self.search_cache[cache_key].copy()
                cached_result[0]['total_time'] = time.time() - total_start_time
                return cached_result
        
        # Enhanced query for better results
        enhanced_query = self._enhance_query_fast(query)
        
        # Parallel search execution
        semantic_future = self.executor.submit(self._fast_semantic_search, enhanced_query, top_k)
        keyword_future = self.executor.submit(self._fast_keyword_search, enhanced_query, top_k)
        
        try:
            # Get results with timeout
            semantic_results = semantic_future.result(timeout=1.5)  # 1.5s timeout
            keyword_results = keyword_future.result(timeout=0.5)   # 0.5s timeout
        except Exception as e:
            print(f"⚠️ Search timeout, using fallback: {e}")
            # Fallback to semantic only
            semantic_results = self._fast_semantic_search(enhanced_query, top_k)
            keyword_results = []
        
        # Fast result combination
        if semantic_results or keyword_results:
            combined_results = self._fast_combine_results(
                semantic_results, keyword_results,
                semantic_weight=0.8, keyword_weight=0.2  # Favor semantic for speed
            )
        else:
            # Ultimate fallback
            combined_results = self._fast_semantic_search(query, top_k)
        
        # Add timing metadata
        total_time = time.time() - total_start_time
        for result in combined_results:
            result['total_time'] = total_time
        
        # Cache successful results
        if use_cache and combined_results and len(self.search_cache) < self.max_cache_size:
            cache_key = hashlib.md5(f"{query}_{top_k}".encode()).hexdigest()
            self.search_cache[cache_key] = combined_results.copy()
        
        print(f"🚀 Fast hybrid search completed in {total_time:.2f}s")
        return combined_results
    
    @lru_cache(maxsize=200)
    def _enhance_query_fast(self, query: str) -> str:
        """Fast query enhancement với minimal processing"""
        query_lower = query.lower().strip()
        
        # Quick medical synonym replacement (only most common)
        quick_replacements = {
            'đái tháo đường': 'tiểu đường diabetes',
            'huyết áp cao': 'cao huyết áp hypertension',
            'nhức đầu': 'đau đầu headache',
            'có sao không': 'nguy hiểm',
            'làm sao': 'điều trị'
        }
        
        for old, new in quick_replacements.items():
            if old in query_lower:
                query_lower = query_lower.replace(old, new)
        
        return query_lower
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return {
            'cache_size': len(self.search_cache),
            'max_cache_size': self.max_cache_size,
            'cache_utilization': len(self.search_cache) / self.max_cache_size,
            'bm25_ready': self.bm25_model is not None,
            'medical_terms_count': len(self.medical_terms_set)
        }
    
    def clear_cache(self):
        """Clear search cache"""
        self.search_cache.clear()
        self.tokenized_cache.clear()
        print("✅ Search cache cleared")

# Factory function
def get_fast_hybrid_search_engine(chunks_data=None, medical_rag_utils=None):
    """Get optimized hybrid search engine"""
    if chunks_data is None:
        # Load data if not provided
        try:
            from medical_rag_utils import load_medical_data
            chunks_data = load_medical_data()
        except Exception as e:
            print(f"⚠️ Failed to load medical data: {e}")
            return None
    
    return FastMedicalHybridSearch(chunks_data, medical_rag_utils)

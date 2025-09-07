#!/usr/bin/env python3
"""
Performance Optimization Module
Tối ưu hóa performance cho medical chatbot để đạt < 3s response time
"""
import time
import asyncio
import threading
from typing import List, Dict, Any, Optional, Callable
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
import pickle
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    search_time: float = 0.0
    processing_time: float = 0.0
    total_time: float = 0.0
    cache_hit: bool = False
    query_hash: str = ""

class SmartCache:
    """Smart caching system với TTL và LRU"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}
        self.access_times = {}
        self.creation_times = {}
    
    def _generate_key(self, query: str, session_id: str = "", context_hash: str = "") -> str:
        """Generate cache key"""
        key_string = f"{query}:{session_id}:{context_hash}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        current_time = time.time()
        
        if key not in self.cache:
            return None
        
        # Check TTL
        if current_time - self.creation_times[key] > self.ttl_seconds:
            self._remove_key(key)
            return None
        
        # Update access time for LRU
        self.access_times[key] = current_time
        return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        current_time = time.time()
        
        # Clean expired entries
        self._cleanup_expired()
        
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._remove_oldest()
        
        self.cache[key] = value
        self.access_times[key] = current_time
        self.creation_times[key] = current_time
    
    def _remove_key(self, key: str) -> None:
        """Remove key from all caches"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
        self.creation_times.pop(key, None)
    
    def _remove_oldest(self) -> None:
        """Remove least recently used item"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        self._remove_key(oldest_key)
    
    def _cleanup_expired(self) -> None:
        """Remove expired entries"""
        current_time = time.time()
        expired_keys = [
            key for key, creation_time in self.creation_times.items()
            if current_time - creation_time > self.ttl_seconds
        ]
        
        for key in expired_keys:
            self._remove_key(key)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'utilization': len(self.cache) / self.max_size
        }

class AsyncSearchManager:
    """Async search manager for parallel processing"""
    
    def __init__(self, max_workers: int = 3):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    def parallel_search(self, search_functions: List[Callable], *args, **kwargs) -> List[Any]:
        """Execute multiple search functions in parallel"""
        futures = []
        
        for search_func in search_functions:
            future = self.executor.submit(search_func, *args, **kwargs)
            futures.append(future)
        
        results = []
        for future in as_completed(futures, timeout=5.0):  # 5s timeout
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                print(f"⚠️ Search function failed: {e}")
                results.append([])  # Empty result for failed search
        
        return results
    
    def async_hybrid_search(self, hybrid_engine, semantic_func, query: str, top_k: int = 5):
        """Async hybrid search với fallback"""
        def hybrid_search():
            try:
                return hybrid_engine.hybrid_search(query, top_k=top_k)
            except Exception as e:
                print(f"⚠️ Hybrid search failed: {e}")
                return []
        
        def semantic_search():
            try:
                return semantic_func(query, top_k=top_k)
            except Exception as e:
                print(f"⚠️ Semantic search failed: {e}")
                return []
        
        # Run both searches in parallel
        results = self.parallel_search([hybrid_search, semantic_search])
        
        # Return best non-empty result
        for result in results:
            if result:
                return result
        
        return []  # All searches failed

class QueryPreprocessor:
    """Fast query preprocessing"""
    
    def __init__(self):
        self.common_patterns = self._build_common_patterns()
        self.stop_words = self._build_stop_words()
    
    def _build_common_patterns(self) -> Dict[str, str]:
        """Build common query patterns for fast replacement"""
        return {
            # Common reference patterns
            'cái này': '{REFERENCE_THIS}',
            'cái đó': '{REFERENCE_THAT}',
            'nó': '{REFERENCE_IT}',
            'chúng': '{REFERENCE_THEM}',
            
            # Common question patterns
            'có sao không': 'có nguy hiểm không',
            'làm sao': 'như thế nào',
            'cần làm gì': 'nên điều trị như thế nào',
            
            # Medical synonyms (most common)
            'đái tháo đường': 'tiểu đường',
            'huyết áp cao': 'cao huyết áp',
            'nhức đầu': 'đau đầu'
        }
    
    def _build_stop_words(self) -> set:
        """Build Vietnamese stop words"""
        return {
            'và', 'hoặc', 'nhưng', 'mà', 'rồi', 'thì', 'nếu', 'vì', 'để',
            'của', 'cho', 'với', 'từ', 'trong', 'ngoài', 'trên', 'dưới',
            'tôi', 'bạn', 'chúng tôi', 'họ', 'nó'
        }
    
    @lru_cache(maxsize=500)
    def fast_preprocess(self, query: str) -> str:
        """Fast query preprocessing với caching"""
        # Basic normalization
        processed = query.lower().strip()
        
        # Apply common patterns
        for pattern, replacement in self.common_patterns.items():
            processed = processed.replace(pattern, replacement)
        
        return processed
    
    def extract_keywords(self, query: str) -> List[str]:
        """Fast keyword extraction"""
        words = self.fast_preprocess(query).split()
        keywords = [word for word in words if word not in self.stop_words and len(word) > 2]
        return keywords[:10]  # Top 10 keywords

class PerformanceOptimizer:
    """Main performance optimization class"""
    
    def __init__(self):
        self.smart_cache = SmartCache(max_size=2000, ttl_seconds=1800)  # 30 min TTL
        self.async_manager = AsyncSearchManager(max_workers=3)
        self.preprocessor = QueryPreprocessor()
        self.metrics = []
        self.performance_targets = {
            'search_time': 2.0,      # Target search time
            'processing_time': 0.8,  # Target processing time
            'total_time': 3.0        # Target total time
        }
    
    def optimize_search(self, search_func: Callable, query: str, 
                       session_id: str = "", context_hash: str = "", 
                       **kwargs) -> tuple:
        """Optimize search với caching và async"""
        start_time = time.time()
        
        # Generate cache key
        cache_key = self.smart_cache._generate_key(query, session_id, context_hash)
        
        # Check cache first
        cached_result = self.smart_cache.get(cache_key)
        if cached_result:
            search_time = time.time() - start_time
            metrics = PerformanceMetrics(
                search_time=search_time,
                total_time=search_time,
                cache_hit=True,
                query_hash=cache_key
            )
            return cached_result, metrics
        
        # Preprocess query for faster search
        preprocessed_query = self.preprocessor.fast_preprocess(query)
        
        # Execute search
        search_start = time.time()
        try:
            results = search_func(preprocessed_query, **kwargs)
            search_time = time.time() - search_start
            
            # Cache results
            self.smart_cache.set(cache_key, results)
            
        except Exception as e:
            print(f"⚠️ Optimized search failed: {e}")
            results = []
            search_time = time.time() - search_start
        
        total_time = time.time() - start_time
        metrics = PerformanceMetrics(
            search_time=search_time,
            total_time=total_time,
            cache_hit=False,
            query_hash=cache_key
        )
        
        return results, metrics
    
    def optimize_entity_extraction(self, ner_func: Callable, text: str) -> tuple:
        """Optimize entity extraction với caching"""
        # Cache key based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        cache_key = f"ner_{text_hash}"
        
        cached_entities = self.smart_cache.get(cache_key)
        if cached_entities:
            return cached_entities, True
        
        # Extract entities
        start_time = time.time()
        try:
            entities = ner_func(text)
            processing_time = time.time() - start_time
            
            # Cache if processing took significant time
            if processing_time > 0.1:
                self.smart_cache.set(cache_key, entities)
            
            return entities, False
            
        except Exception as e:
            print(f"⚠️ Entity extraction failed: {e}")
            return [], False
    
    def optimize_confidence_calculation(self, confidence_func: Callable, 
                                      use_simplified: bool = False, **kwargs) -> float:
        """Optimize confidence calculation"""
        if use_simplified:
            # Simplified confidence calculation for speed
            search_results = kwargs.get('search_results', [])
            if not search_results:
                return 0.0
            
            # Fast confidence based on top result only
            top_result = search_results[0]
            relevance = top_result.get('relevance_score', 
                                     top_result.get('semantic_score', 0.0))
            
            # Simple confidence = relevance * intent boost
            intent = kwargs.get('intent', 'general_medical')
            intent_boost = {
                'emergency': 1.2,
                'symptom_analysis': 1.1,
                'disease_inquiry': 1.0,
                'medical_consultation': 0.9,
                'general_medical': 0.8
            }
            
            return min(relevance * intent_boost.get(intent, 1.0), 1.0)
        else:
            # Full confidence calculation
            return confidence_func(**kwargs)
    
    def batch_process_queries(self, queries: List[str], process_func: Callable) -> List[Any]:
        """Batch process multiple queries for efficiency"""
        # Group similar queries
        query_groups = self._group_similar_queries(queries)
        
        all_results = []
        for group in query_groups:
            # Process group in parallel
            group_results = self.async_manager.parallel_search(
                [lambda q=query: process_func(q) for query in group]
            )
            all_results.extend(group_results)
        
        return all_results
    
    def _group_similar_queries(self, queries: List[str]) -> List[List[str]]:
        """Group similar queries for batch processing"""
        groups = []
        for query in queries:
            keywords = set(self.preprocessor.extract_keywords(query))
            
            # Find existing group with similar keywords
            placed = False
            for group in groups:
                if group:
                    group_keywords = set(self.preprocessor.extract_keywords(group[0]))
                    similarity = len(keywords.intersection(group_keywords)) / len(keywords.union(group_keywords))
                    
                    if similarity > 0.3:  # 30% similarity threshold
                        group.append(query)
                        placed = True
                        break
            
            if not placed:
                groups.append([query])
        
        return groups
    
    def preload_common_data(self, data_loader_func: Callable):
        """Preload commonly accessed data"""
        def preload_worker():
            try:
                # Preload medical synonyms, patterns, etc.
                common_queries = [
                    'đau đầu', 'sốt', 'ho', 'buồn nôn', 'tiểu đường', 'cao huyết áp'
                ]
                
                for query in common_queries:
                    data_loader_func(query)
                    
                print("✅ Common data preloaded")
            except Exception as e:
                print(f"⚠️ Preloading failed: {e}")
        
        # Run preloading in background
        thread = threading.Thread(target=preload_worker)
        thread.daemon = True
        thread.start()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.metrics:
            return {'status': 'no_data'}
        
        recent_metrics = self.metrics[-100:]  # Last 100 queries
        
        avg_search_time = sum(m.search_time for m in recent_metrics) / len(recent_metrics)
        avg_total_time = sum(m.total_time for m in recent_metrics) / len(recent_metrics)
        cache_hit_rate = sum(1 for m in recent_metrics if m.cache_hit) / len(recent_metrics)
        
        return {
            'avg_search_time': avg_search_time,
            'avg_total_time': avg_total_time,
            'cache_hit_rate': cache_hit_rate,
            'target_search_time': self.performance_targets['search_time'],
            'target_total_time': self.performance_targets['total_time'],
            'performance_score': self._calculate_performance_score(avg_total_time),
            'cache_stats': self.smart_cache.get_stats(),
            'recommendations': self._get_performance_recommendations(avg_total_time, cache_hit_rate)
        }
    
    def _calculate_performance_score(self, avg_total_time: float) -> float:
        """Calculate performance score (0-100)"""
        target_time = self.performance_targets['total_time']
        if avg_total_time <= target_time:
            return 100.0
        else:
            # Decreasing score for slower performance
            return max(0, 100 - (avg_total_time - target_time) * 20)
    
    def _get_performance_recommendations(self, avg_time: float, cache_rate: float) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        if avg_time > self.performance_targets['total_time']:
            recommendations.append("⚠️ Response time exceeds target - consider optimizing search algorithms")
        
        if cache_rate < 0.3:
            recommendations.append("💾 Low cache hit rate - review caching strategy")
        
        if avg_time > 5.0:
            recommendations.append("🚨 Very slow response - check system resources")
        
        if cache_rate > 0.8:
            recommendations.append("✅ Excellent cache performance")
        
        if avg_time <= self.performance_targets['total_time']:
            recommendations.append("🎯 Meeting performance targets")
        
        return recommendations
    
    def record_metrics(self, metrics: PerformanceMetrics):
        """Record performance metrics"""
        self.metrics.append(metrics)
        
        # Keep only recent metrics
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-500:]  # Keep last 500

# Factory function
def get_performance_optimizer():
    """Get performance optimizer instance"""
    return PerformanceOptimizer()

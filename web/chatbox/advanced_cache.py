#!/usr/bin/env python3
"""
Advanced Caching System
Hệ thống cache nâng cao cho medical chatbot
"""
import time
import pickle
import hashlib
import threading
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    created_at: float
    last_accessed: float
    access_count: int
    size_bytes: int
    ttl: float

class MultiLevelCache:
    """Multi-level caching system với intelligent eviction"""
    
    def __init__(self, l1_size: int = 200, l2_size: int = 1000, l3_size: int = 5000):
        # Level 1: Hot data (fastest access)
        self.l1_cache = {}
        self.l1_max_size = l1_size
        
        # Level 2: Warm data (medium access)
        self.l2_cache = {}
        self.l2_max_size = l2_size
        
        # Level 3: Cold data (slower but persistent)
        self.l3_cache = {}
        self.l3_max_size = l3_size
        
        # Cache statistics
        self.stats = {
            'l1_hits': 0, 'l1_misses': 0,
            'l2_hits': 0, 'l2_misses': 0,  
            'l3_hits': 0, 'l3_misses': 0,
            'promotions': 0, 'demotions': 0,
            'evictions': 0
        }
        
        # Thread safety
        self.lock = threading.RLock()
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        key_data = f"{args}_{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _estimate_size(self, data: Any) -> int:
        """Estimate size of data in bytes"""
        try:
            return len(pickle.dumps(data))
        except:
            return len(str(data).encode('utf-8'))
    
    def get(self, key: str) -> Tuple[Any, str]:
        """Get data from cache with level tracking"""
        with self.lock:
            current_time = time.time()
            
            # Check L1 (hottest)
            if key in self.l1_cache:
                entry = self.l1_cache[key]
                if current_time - entry.created_at < entry.ttl:
                    entry.last_accessed = current_time
                    entry.access_count += 1
                    self.stats['l1_hits'] += 1
                    return entry.data, 'L1'
                else:
                    del self.l1_cache[key]
            
            # Check L2 (warm)
            if key in self.l2_cache:
                entry = self.l2_cache[key]
                if current_time - entry.created_at < entry.ttl:
                    entry.last_accessed = current_time
                    entry.access_count += 1
                    self.stats['l2_hits'] += 1
                    
                    # Promote to L1 if frequently accessed
                    if entry.access_count >= 5:
                        self._promote_to_l1(key, entry)
                    
                    return entry.data, 'L2'
                else:
                    del self.l2_cache[key]
            
            # Check L3 (cold)
            if key in self.l3_cache:
                entry = self.l3_cache[key]
                if current_time - entry.created_at < entry.ttl:
                    entry.last_accessed = current_time
                    entry.access_count += 1
                    self.stats['l3_hits'] += 1
                    
                    # Promote to L2 if accessed
                    self._promote_to_l2(key, entry)
                    
                    return entry.data, 'L3'
                else:
                    del self.l3_cache[key]
            
            # Miss all levels
            self.stats['l1_misses'] += 1
            return None, 'MISS'
    
    def set(self, key: str, data: Any, ttl: float = 3600) -> None:
        """Set data in appropriate cache level"""
        with self.lock:
            current_time = time.time()
            size_bytes = self._estimate_size(data)
            
            entry = CacheEntry(
                data=data,
                created_at=current_time,
                last_accessed=current_time,
                access_count=1,
                size_bytes=size_bytes,
                ttl=ttl
            )
            
            # Start with L1 for new entries
            self._set_l1(key, entry)
    
    def _set_l1(self, key: str, entry: CacheEntry) -> None:
        """Set entry in L1 cache"""
        # Make space if needed
        while len(self.l1_cache) >= self.l1_max_size:
            self._evict_from_l1()
        
        self.l1_cache[key] = entry
    
    def _set_l2(self, key: str, entry: CacheEntry) -> None:
        """Set entry in L2 cache"""
        while len(self.l2_cache) >= self.l2_max_size:
            self._evict_from_l2()
        
        self.l2_cache[key] = entry
    
    def _set_l3(self, key: str, entry: CacheEntry) -> None:
        """Set entry in L3 cache"""
        while len(self.l3_cache) >= self.l3_max_size:
            self._evict_from_l3()
        
        self.l3_cache[key] = entry
    
    def _promote_to_l1(self, key: str, entry: CacheEntry) -> None:
        """Promote entry from L2 to L1"""
        if key in self.l2_cache:
            del self.l2_cache[key]
            self._set_l1(key, entry)
            self.stats['promotions'] += 1
    
    def _promote_to_l2(self, key: str, entry: CacheEntry) -> None:
        """Promote entry from L3 to L2"""
        if key in self.l3_cache:
            del self.l3_cache[key]
            self._set_l2(key, entry)
            self.stats['promotions'] += 1
    
    def _evict_from_l1(self) -> None:
        """Evict least valuable entry from L1"""
        if not self.l1_cache:
            return
        
        # Find least recently used with lowest access count
        lru_key = min(self.l1_cache.keys(),
                      key=lambda k: (self.l1_cache[k].access_count, self.l1_cache[k].last_accessed))
        
        entry = self.l1_cache[lru_key]
        del self.l1_cache[lru_key]
        
        # Demote to L2 if still valuable
        if entry.access_count > 1:
            self._set_l2(lru_key, entry)
            self.stats['demotions'] += 1
        else:
            self.stats['evictions'] += 1
    
    def _evict_from_l2(self) -> None:
        """Evict least valuable entry from L2"""
        if not self.l2_cache:
            return
        
        lru_key = min(self.l2_cache.keys(),
                      key=lambda k: (self.l2_cache[k].access_count, self.l2_cache[k].last_accessed))
        
        entry = self.l2_cache[lru_key]
        del self.l2_cache[lru_key]
        
        # Demote to L3 if still somewhat valuable
        if entry.access_count > 2:
            self._set_l3(lru_key, entry)
            self.stats['demotions'] += 1
        else:
            self.stats['evictions'] += 1
    
    def _evict_from_l3(self) -> None:
        """Evict least valuable entry from L3"""
        if not self.l3_cache:
            return
        
        lru_key = min(self.l3_cache.keys(),
                      key=lambda k: self.l3_cache[k].last_accessed)
        
        del self.l3_cache[lru_key]
        self.stats['evictions'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        with self.lock:
            total_hits = self.stats['l1_hits'] + self.stats['l2_hits'] + self.stats['l3_hits']
            total_misses = self.stats['l1_misses'] + self.stats['l2_misses'] + self.stats['l3_misses']
            total_requests = total_hits + total_misses
            
            return {
                'hit_rate': total_hits / total_requests if total_requests > 0 else 0,
                'l1_hit_rate': self.stats['l1_hits'] / total_requests if total_requests > 0 else 0,
                'l2_hit_rate': self.stats['l2_hits'] / total_requests if total_requests > 0 else 0,
                'l3_hit_rate': self.stats['l3_hits'] / total_requests if total_requests > 0 else 0,
                'total_requests': total_requests,
                'cache_sizes': {
                    'l1': len(self.l1_cache),
                    'l2': len(self.l2_cache),
                    'l3': len(self.l3_cache)
                },
                'utilization': {
                    'l1': len(self.l1_cache) / self.l1_max_size,
                    'l2': len(self.l2_cache) / self.l2_max_size,
                    'l3': len(self.l3_cache) / self.l3_max_size
                },
                'operations': {
                    'promotions': self.stats['promotions'],
                    'demotions': self.stats['demotions'],
                    'evictions': self.stats['evictions']
                }
            }

class SmartQueryCache:
    """Smart caching system specifically for medical queries"""
    
    def __init__(self):
        self.cache = MultiLevelCache(l1_size=100, l2_size=500, l3_size=2000)
        self.similarity_threshold = 0.8
        self.query_patterns = {}  # Track common query patterns
    
    def _normalize_query(self, query: str) -> str:
        """Normalize query for better cache hits"""
        normalized = query.lower().strip()
        
        # Common normalizations
        normalizations = {
            'đái tháo đường': 'tiểu đường',
            'huyết áp cao': 'cao huyết áp',
            'nhức đầu': 'đau đầu',
            'có sao không': '',
            'có nguy hiểm không': '',
            'tôi bị': '',
            'em bị': '',
            'anh bị': '',
            'chị bị': ''
        }
        
        for old, new in normalizations.items():
            normalized = normalized.replace(old, new)
        
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def _extract_query_pattern(self, query: str) -> str:
        """Extract query pattern for similarity matching"""
        normalized = self._normalize_query(query)
        words = normalized.split()
        
        # Extract medical keywords
        medical_keywords = []
        for word in words:
            if len(word) > 3:  # Skip short words
                medical_keywords.append(word)
        
        return ' '.join(sorted(medical_keywords))
    
    def get_cached_result(self, query: str, intent: str = None, context: Dict = None) -> Tuple[Any, str]:
        """Get cached result for query"""
        # Generate cache key
        cache_key = self._generate_cache_key(query, intent, context)
        
        # Try exact match first
        result, level = self.cache.get(cache_key)
        if result is not None:
            return result, f'EXACT_{level}'
        
        # Try pattern-based similarity matching
        pattern = self._extract_query_pattern(query)
        pattern_key = f"pattern_{hashlib.md5(pattern.encode()).hexdigest()}"
        
        result, level = self.cache.get(pattern_key)
        if result is not None:
            return result, f'PATTERN_{level}'
        
        return None, 'MISS'
    
    def cache_result(self, query: str, result: Any, intent: str = None, 
                    context: Dict = None, ttl: float = 1800) -> None:
        """Cache result with intelligent key generation"""
        # Cache exact match
        cache_key = self._generate_cache_key(query, intent, context)
        self.cache.set(cache_key, result, ttl)
        
        # Cache pattern match for similar queries
        pattern = self._extract_query_pattern(query)
        pattern_key = f"pattern_{hashlib.md5(pattern.encode()).hexdigest()}"
        self.cache.set(pattern_key, result, ttl * 2)  # Longer TTL for patterns
        
        # Track query patterns
        if pattern in self.query_patterns:
            self.query_patterns[pattern] += 1
        else:
            self.query_patterns[pattern] = 1
    
    def _generate_cache_key(self, query: str, intent: str = None, context: Dict = None) -> str:
        """Generate comprehensive cache key"""
        normalized_query = self._normalize_query(query)
        
        # Include intent if available
        intent_part = intent or 'unknown'
        
        # Include relevant context
        context_part = ''
        if context:
            # Only include stable context elements
            stable_context = {
                'has_history': bool(context.get('mentioned_entities')),
                'entity_count': len(context.get('mentioned_entities', [])),
                'domain': context.get('medical_domain', 'general')
            }
            context_part = str(sorted(stable_context.items()))
        
        key_string = f"{normalized_query}_{intent_part}_{context_part}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        base_stats = self.cache.get_stats()
        
        # Add query pattern stats
        top_patterns = sorted(self.query_patterns.items(), 
                            key=lambda x: x[1], reverse=True)[:10]
        
        base_stats['query_patterns'] = {
            'total_patterns': len(self.query_patterns),
            'top_patterns': top_patterns
        }
        
        return base_stats
    
    def clear_cache(self):
        """Clear all caches"""
        self.cache = MultiLevelCache(l1_size=100, l2_size=500, l3_size=2000)
        self.query_patterns.clear()

class ResultCache:
    """Specialized cache for search results"""
    
    def __init__(self):
        self.search_cache = {}
        self.entity_cache = {}
        self.confidence_cache = {}
        self.max_size = 1000
        self.lock = threading.RLock()
    
    def cache_search_results(self, query_hash: str, results: List[Dict], ttl: float = 1800):
        """Cache search results"""
        with self.lock:
            if len(self.search_cache) >= self.max_size:
                # Remove oldest entries
                self._cleanup_search_cache()
            
            self.search_cache[query_hash] = {
                'results': results,
                'cached_at': time.time(),
                'ttl': ttl,
                'access_count': 0
            }
    
    def get_search_results(self, query_hash: str) -> Optional[List[Dict]]:
        """Get cached search results"""
        with self.lock:
            if query_hash in self.search_cache:
                entry = self.search_cache[query_hash]
                
                # Check TTL
                if time.time() - entry['cached_at'] < entry['ttl']:
                    entry['access_count'] += 1
                    return entry['results']
                else:
                    del self.search_cache[query_hash]
            
            return None
    
    def cache_entities(self, text_hash: str, entities: List, ttl: float = 3600):
        """Cache extracted entities"""
        with self.lock:
            if len(self.entity_cache) >= self.max_size:
                self._cleanup_entity_cache()
            
            self.entity_cache[text_hash] = {
                'entities': entities,
                'cached_at': time.time(),
                'ttl': ttl
            }
    
    def get_entities(self, text_hash: str) -> Optional[List]:
        """Get cached entities"""
        with self.lock:
            if text_hash in self.entity_cache:
                entry = self.entity_cache[text_hash]
                
                if time.time() - entry['cached_at'] < entry['ttl']:
                    return entry['entities']
                else:
                    del self.entity_cache[text_hash]
            
            return None
    
    def _cleanup_search_cache(self):
        """Remove old search cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.search_cache.items()
            if current_time - entry['cached_at'] > entry['ttl']
        ]
        
        for key in expired_keys:
            del self.search_cache[key]
        
        # If still too many, remove least accessed
        if len(self.search_cache) >= self.max_size:
            sorted_items = sorted(self.search_cache.items(),
                                key=lambda x: x[1]['access_count'])
            
            for key, _ in sorted_items[:len(sorted_items)//4]:  # Remove 25%
                del self.search_cache[key]
    
    def _cleanup_entity_cache(self):
        """Remove old entity cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.entity_cache.items()
            if current_time - entry['cached_at'] > entry['ttl']
        ]
        
        for key in expired_keys:
            del self.entity_cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            'search_cache_size': len(self.search_cache),
            'entity_cache_size': len(self.entity_cache),
            'confidence_cache_size': len(self.confidence_cache),
            'max_size': self.max_size
        }

# Factory functions
def get_smart_query_cache():
    """Get smart query cache instance"""
    return SmartQueryCache()

def get_result_cache():
    """Get result cache instance"""
    return ResultCache()

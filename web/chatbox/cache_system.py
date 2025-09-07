import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import threading
from collections import defaultdict


try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis not available, using in-memory cache")


class TTLCache:
    """
    TTL (Time-To-Live) Cache implementation with Redis afallback to in-memory
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0, default_ttl=86400):
        self.default_ttl = default_ttl  # 24 hours in seconds
        
        # Try to connect to Redis first
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=redis_host, 
                    port=redis_port, 
                    db=redis_db,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                self.use_redis = True
                print("Connected to Redis for TTL caching")
            except Exception as e:
                print(f"Redis connection failed: {e}, using in-memory cache")
                self.use_redis = False
                self._init_memory_cache()
        else:
            self.use_redis = False
            self._init_memory_cache()
    
    def _init_memory_cache(self):
        """Initialize in-memory cache with TTL support"""
        self.cache = {}
        self.ttl_data = {}
        self.lock = threading.RLock()
        
        # Start cleanup thread for in-memory cache
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_memory, daemon=True)
        self.cleanup_thread.start()
    
    def _cleanup_expired_memory(self):
        """Background thread to cleanup expired in-memory cache entries"""
        while True:
            try:
                current_time = time.time()
                with self.lock:
                    expired_keys = [
                        key for key, expire_time in self.ttl_data.items() 
                        if current_time > expire_time
                    ]
                    
                    for key in expired_keys:
                        self.cache.pop(key, None)
                        self.ttl_data.pop(key, None)
                    
                    if expired_keys:
                        print(f"Cleaned up {len(expired_keys)} expired cache entries")
                
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"Error in cleanup thread: {e}")
                time.sleep(60)
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a value with TTL"""
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            if self.use_redis:
                # Redis TTL cache
                serialized_value = json.dumps(value, ensure_ascii=False)
                return self.redis_client.setex(key, ttl, serialized_value)
            else:
                # In-memory TTL cache
                with self.lock:
                    self.cache[key] = value
                    self.ttl_data[key] = time.time() + ttl
                return True
        except Exception as e:
            print(f"Error setting cache key {key}: {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from cache"""
        try:
            if self.use_redis:
                # Redis cache
                value = self.redis_client.get(key)
                if value is None:
                    return None
                return json.loads(value)
            else:
                # In-memory cache
                with self.lock:
                    if key not in self.cache:
                        return None
                    
                    # Check if expired
                    if time.time() > self.ttl_data.get(key, 0):
                        self.cache.pop(key, None)
                        self.ttl_data.pop(key, None)
                        return None
                    
                    return self.cache[key]
        except Exception as e:
            print(f"Error getting cache key {key}: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key from cache"""
        try:
            if self.use_redis:
                return bool(self.redis_client.delete(key))
            else:
                with self.lock:
                    self.cache.pop(key, None)
                    self.ttl_data.pop(key, None)
                return True
        except Exception as e:
            print(f"Error deleting cache key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired"""
        try:
            if self.use_redis:
                return bool(self.redis_client.exists(key))
            else:
                with self.lock:
                    if key not in self.cache:
                        return False
                    
                    # Check if expired
                    if time.time() > self.ttl_data.get(key, 0):
                        self.cache.pop(key, None)
                        self.ttl_data.pop(key, None)
                        return False
                    
                    return True
        except Exception as e:
            print(f"Error checking cache key {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """Get remaining TTL for a key"""
        try:
            if self.use_redis:
                return self.redis_client.ttl(key)
            else:
                with self.lock:
                    if key not in self.ttl_data:
                        return None
                    
                    remaining = int(self.ttl_data[key] - time.time())
                    return remaining if remaining > 0 else None
        except Exception as e:
            print(f"Error getting TTL for key {key}: {e}")
            return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self.use_redis:
                info = self.redis_client.info()
                return {
                    'cache_type': 'Redis',
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'hit_rate': round(info.get('keyspace_hits', 0) / max(1, info.get('keyspace_hits', 0) + info.get('keyspace_misses', 0)) * 100, 2)
                }
            else:
                with self.lock:
                    current_time = time.time()
                    active_keys = sum(1 for exp_time in self.ttl_data.values() if exp_time > current_time)
                    
                    return {
                        'cache_type': 'In-Memory',
                        'total_keys': len(self.cache),
                        'active_keys': active_keys,
                        'expired_keys': len(self.cache) - active_keys
                    }
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {'error': str(e)}

class ReviewSummaryTTLCache:
    """
    Review Summary Cache with TTL support
    """
    
    def __init__(self, cache_ttl=86400):  # 24 hours default
        self.cache = TTLCache(default_ttl=cache_ttl)
        self.cache_ttl = cache_ttl
        
        # Statistics
        self.stats = defaultdict(int)
        self.stats_lock = threading.Lock()
    
    def _generate_cache_key(self, product_id: str) -> str:
        """Generate cache key for product"""
        return f"review_summary:{product_id}"
    
    def _generate_hash_key(self, product_id: str) -> str:
        """Generate hash key for reviews content"""
        return f"review_hash:{product_id}"
    
    def _generate_reviews_hash(self, reviews: list) -> str:
        """Generate hash from reviews content"""
        if not reviews:
            return "empty"
        
        # Sort reviews by created_at and create hash from important content
        sorted_reviews = sorted(reviews, key=lambda x: str(x.get('created_at', '')))
        content_for_hash = []
        
        for review in sorted_reviews:
            content_for_hash.append({
                'review_id': review.get('review_id'),
                'rating': review.get('rating'),
                'comment': review.get('comment', ''),
                'created_at': str(review.get('created_at', '')),
                'is_verified': review.get('is_verified', False)
            })
        
        content_str = json.dumps(content_for_hash, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()[:16]  # Short hash
    
    def get_cached_summary(self, product_id: str, current_reviews: list) -> Optional[Dict[Any, Any]]:
        """Get cached summary if valid"""
        cache_key = self._generate_cache_key(product_id)
        hash_key = self._generate_hash_key(product_id)
        current_hash = self._generate_reviews_hash(current_reviews)
        
        try:
            # Check if summary exists
            cached_summary = self.cache.get(cache_key)
            if not cached_summary:
                with self.stats_lock:
                    self.stats['cache_miss'] += 1
                return None
            
            # Check if reviews hash matches
            cached_hash = self.cache.get(hash_key)
            if cached_hash != current_hash:
                # Reviews changed, invalidate cache
                self.cache.delete(cache_key)
                self.cache.delete(hash_key)
                with self.stats_lock:
                    self.stats['cache_invalidated'] += 1
                print(f"Cache invalidated for product {product_id} due to reviews change")
                return None
            
            # Cache hit
            with self.stats_lock:
                self.stats['cache_hit'] += 1
            
            # Add cache info to response
            cached_summary['cached'] = True
            cached_summary['cache_ttl'] = self.cache.get_ttl(cache_key)
            
            print(f"Cache hit for product {product_id}")
            return cached_summary
            
        except Exception as e:
            print(f"Error getting cached summary: {e}")
            with self.stats_lock:
                self.stats['cache_error'] += 1
            return None
    
    def save_summary_to_cache(self, product_id: str, summary_data: dict, reviews: list) -> bool:
        """Save summary to cache with TTL"""
        cache_key = self._generate_cache_key(product_id)
        hash_key = self._generate_hash_key(product_id)
        reviews_hash = self._generate_reviews_hash(reviews)
        
        try:
            # Save summary
            summary_success = self.cache.set(cache_key, summary_data, self.cache_ttl)
            
            # Save reviews hash
            hash_success = self.cache.set(hash_key, reviews_hash, self.cache_ttl)
            
            if summary_success and hash_success:
                with self.stats_lock:
                    self.stats['cache_saved'] += 1
                print(f"Saved summary to cache for product {product_id} (TTL: {self.cache_ttl}s)")
                return True
            else:
                with self.stats_lock:
                    self.stats['cache_save_error'] += 1
                return False
                
        except Exception as e:
            print(f"Error saving summary to cache: {e}")
            with self.stats_lock:
                self.stats['cache_save_error'] += 1
            return False
    
    def clear_product_cache(self, product_id: str) -> bool:
        """Clear cache for specific product"""
        cache_key = self._generate_cache_key(product_id)
        hash_key = self._generate_hash_key(product_id)
        
        try:
            summary_deleted = self.cache.delete(cache_key)
            hash_deleted = self.cache.delete(hash_key)
            
            if summary_deleted or hash_deleted:
                with self.stats_lock:
                    self.stats['cache_cleared'] += 1
                print(f"Cleared cache for product {product_id}")
                return True
            return False
            
        except Exception as e:
            print(f"Error clearing cache for product {product_id}: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        try:
            cache_stats = self.cache.get_stats()
            
            with self.stats_lock:
                app_stats = dict(self.stats)
            
            # Calculate hit rate
            total_requests = app_stats.get('cache_hit', 0) + app_stats.get('cache_miss', 0)
            hit_rate = round((app_stats.get('cache_hit', 0) / max(1, total_requests)) * 100, 2)
            
            return {
                'cache_system': cache_stats,
                'application_stats': {
                    **app_stats,
                    'hit_rate_percent': hit_rate,
                    'total_requests': total_requests
                },
                'ttl_seconds': self.cache_ttl,
                'ttl_hours': round(self.cache_ttl / 3600, 1)
            }
            
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {'error': str(e)}
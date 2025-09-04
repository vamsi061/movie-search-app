"""
Caching layer to reduce resource usage and improve performance
"""
import json
import time
from typing import List, Dict, Optional
import hashlib

class SimpleCache:
    """Simple in-memory cache with TTL"""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache = {}
        self.default_ttl = default_ttl
    
    def _generate_key(self, query: str, max_results: int) -> str:
        """Generate cache key from search parameters"""
        key_data = f"{query.lower().strip()}_{max_results}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, query: str, max_results: int) -> Optional[List[Dict]]:
        """Get cached results if available and not expired"""
        key = self._generate_key(query, max_results)
        
        if key in self.cache:
            cached_data, timestamp, ttl = self.cache[key]
            
            # Check if cache is still valid
            if time.time() - timestamp < ttl:
                print(f"🚀 Cache HIT for query: {query} (age: {int(time.time() - timestamp)}s)")
                return cached_data
            else:
                # Remove expired cache
                del self.cache[key]
                print(f"⏰ Cache EXPIRED for query: {query}")
        
        print(f"❌ Cache MISS for query: {query}")
        return None
    
    def set(self, query: str, max_results: int, results: List[Dict], ttl: Optional[int] = None) -> None:
        """Cache the results"""
        key = self._generate_key(query, max_results)
        cache_ttl = ttl or self.default_ttl
        
        self.cache[key] = (results, time.time(), cache_ttl)
        print(f"💾 Cached {len(results)} results for query: {query} (TTL: {cache_ttl}s)")
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        print("🗑️ Cache cleared")
    
    def stats(self) -> Dict:
        """Get cache statistics"""
        total_keys = len(self.cache)
        expired_keys = 0
        
        current_time = time.time()
        for cached_data, timestamp, ttl in self.cache.values():
            if current_time - timestamp >= ttl:
                expired_keys += 1
        
        return {
            "total_keys": total_keys,
            "active_keys": total_keys - expired_keys,
            "expired_keys": expired_keys
        }

# Global cache instance
movie_cache = SimpleCache(default_ttl=600)  # 10 minutes cache

async def get_cached_or_search(query: str, max_results: int, search_function) -> List[Dict]:
    """
    Get results from cache or perform search and cache the results
    """
    # Try to get from cache first
    cached_results = movie_cache.get(query, max_results)
    if cached_results is not None:
        return cached_results
    
    # Cache miss - perform actual search
    print(f"🔍 Performing fresh search for: {query}")
    results = await search_function(query, max_results)
    
    # Cache the results if we got any
    if results:
        movie_cache.set(query, max_results, results)
    
    return results
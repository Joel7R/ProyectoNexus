import time
from typing import Any, Dict, Optional

class CacheManager:
    """A simple in-memory cache with TTL support"""
    _instance = None
    _cache: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
        return cls._instance

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a value from cache if it exists and is not expired"""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() < entry['expiry']:
                print(f"[Cache] Hit for key: {key}")
                return entry['value']
            else:
                print(f"[Cache] Expired key: {key}")
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: int = 300):
        """Store a value in cache with a specific TTL (default 5 minutes)"""
        print(f"[Cache] Setting key: {key} (TTL: {ttl}s)")
        self._cache[key] = {
            'value': value,
            'expiry': time.time() + ttl
        }

    def clear(self):
        """Clear all cache entries"""
        self._cache.clear()

# Global instance
cache_manager = CacheManager()

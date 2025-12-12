"""
Quantum Cache - High-performance real-time data caching
"""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from collections import OrderedDict
from src.utils.logger import get_logger
from src.utils.config_manager import get_config

logger = get_logger(__name__)


class CacheEntry:
    """Single cache entry with expiration"""
    
    def __init__(self, key: str, value: Any, ttl_seconds: int = 60):
        self.key = key
        self.value = value
        self.timestamp = datetime.now()
        self.ttl = timedelta(seconds=ttl_seconds)
        self.access_count = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired"""
        return datetime.now() - self.timestamp > self.ttl
    
    def access(self) -> Any:
        """Access the cached value"""
        self.access_count += 1
        return self.value


class QuantumCache:
    """
    High-performance cache with TTL and LRU eviction
    Quantum-inspired name for fast real-time data access
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 60):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.logger = get_logger(__name__)
        self.hits = 0
        self.misses = 0
        self._lock = asyncio.Lock()
        
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        async with self._lock:
            entry = self.cache.get(key)
            
            if entry is None:
                self.misses += 1
                return None
            
            if entry.is_expired():
                self.logger.debug(f"Cache entry expired: {key}")
                del self.cache[key]
                self.misses += 1
                return None
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            self.hits += 1
            
            return entry.access()
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional)
        """
        async with self._lock:
            if ttl is None:
                ttl = self.default_ttl
            
            # Remove oldest if at capacity
            if len(self.cache) >= self.max_size and key not in self.cache:
                self.cache.popitem(last=False)
            
            entry = CacheEntry(key, value, ttl)
            self.cache[key] = entry
            self.cache.move_to_end(key)
    
    async def delete(self, key: str) -> bool:
        """
        Delete entry from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self.cache.clear()
            self.logger.info("Cache cleared")
    
    async def cleanup_expired(self):
        """Remove all expired entries"""
        async with self._lock:
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self.cache[key]
            
            if expired_keys:
                self.logger.debug(f"Cleaned up {len(expired_keys)} expired entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0.0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'usage_pct': (len(self.cache) / self.max_size * 100) if self.max_size > 0 else 0
        }
    
    def reset_stats(self):
        """Reset hit/miss statistics"""
        self.hits = 0
        self.misses = 0


class MultiLevelCache:
    """
    Multi-level cache with L1 (fast/small) and L2 (slower/larger)
    """
    
    def __init__(
        self,
        l1_size: int = 100,
        l2_size: int = 1000,
        l1_ttl: int = 30,
        l2_ttl: int = 300
    ):
        self.l1 = QuantumCache(max_size=l1_size, default_ttl=l1_ttl)
        self.l2 = QuantumCache(max_size=l2_size, default_ttl=l2_ttl)
        self.logger = get_logger(f"{__name__}.MultiLevelCache")
        self._cleanup_task = None
        self._running = False
    
    async def start(self):
        """Start the multi-level cache with cleanup task"""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.logger.info("Multi-level cache started")
    
    async def stop(self):
        """Stop the cache"""
        self._running = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        self.logger.info("Multi-level cache stopped")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (checks L1 then L2)
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        # Check L1 first
        value = await self.l1.get(key)
        if value is not None:
            return value
        
        # Check L2
        value = await self.l2.get(key)
        if value is not None:
            # Promote to L1
            await self.l1.set(key, value)
            return value
        
        return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Set value in both cache levels
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (optional)
        """
        # Set in both levels
        await self.l1.set(key, value, ttl)
        await self.l2.set(key, value, ttl if ttl else None)
    
    async def delete(self, key: str):
        """Delete from both cache levels"""
        await self.l1.delete(key)
        await self.l2.delete(key)
    
    async def clear(self):
        """Clear both cache levels"""
        await self.l1.clear()
        await self.l2.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for both cache levels"""
        return {
            'l1': self.l1.get_stats(),
            'l2': self.l2.get_stats()
        }
    
    async def _cleanup_loop(self):
        """Background task for periodic cleanup"""
        while self._running:
            try:
                await asyncio.sleep(60)  # Cleanup every minute
                await self.l1.cleanup_expired()
                await self.l2.cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")


# Global cache instances
_quantum_cache = None
_multi_level_cache = None


def get_quantum_cache() -> QuantumCache:
    """Get or create global quantum cache instance"""
    global _quantum_cache
    if _quantum_cache is None:
        cache_size = get_config('system', 'memory.cache_size_mb', 512)
        # Rough estimate: 1KB per entry, so cache_size_mb * 1024 entries
        max_entries = cache_size * 1024
        ttl = get_config('trading', 'market_data.cache_duration_seconds', 60)
        _quantum_cache = QuantumCache(max_size=max_entries, default_ttl=ttl)
    return _quantum_cache


def get_multi_level_cache() -> MultiLevelCache:
    """Get or create global multi-level cache instance"""
    global _multi_level_cache
    if _multi_level_cache is None:
        _multi_level_cache = MultiLevelCache()
    return _multi_level_cache

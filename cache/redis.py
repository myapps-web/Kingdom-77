"""
Redis Cache Module for Kingdom-77 Bot v3.0
===========================================
Provides caching layer for frequently accessed data to reduce database load.
"""

import os
import json
import logging
from typing import Optional, Any, Dict
import redis.asyncio as aioredis
from redis.asyncio import Redis

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache manager with async support."""
    
    def __init__(self, connection_string: str):
        """Initialize Redis connection.
        
        Args:
            connection_string: Redis connection URL
        """
        self.connection_string = connection_string
        self.client: Optional[Redis] = None
        self.connected = False
        
    async def connect(self) -> bool:
        """Establish connection to Redis.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Configure SSL for Upstash and other cloud Redis providers
            self.client = await aioredis.from_url(
                self.connection_string,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                ssl_cert_reqs=None  # Disable SSL verification for cloud providers
            )
            
            # Test connection
            await self.client.ping()
            self.connected = True
            logger.info("✅ Connected to Redis successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self.connected = False
            logger.info("Redis connection closed")
    
    # ========================================================================
    # BASIC OPERATIONS
    # ========================================================================
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.connected or not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
            else:
                logger.debug(f"Cache MISS: {key}")
            return value
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = 3600) -> bool:
        """Set value in cache with TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            return False
        
        try:
            await self.client.setex(key, ttl, value)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.connected or not self.client:
            return False
        
        try:
            await self.client.delete(key)
            logger.debug(f"Cache DELETE: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists, False otherwise
        """
        if not self.connected or not self.client:
            return False
        
        try:
            result = await self.client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Error checking cache existence: {e}")
            return False
    
    # ========================================================================
    # JSON OPERATIONS
    # ========================================================================
    
    async def get_json(self, key: str) -> Optional[Dict]:
        """Get JSON object from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Parsed JSON dict or None
        """
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON from cache: {e}")
                return None
        return None
    
    async def set_json(self, key: str, value: Dict, ttl: int = 3600) -> bool:
        """Set JSON object in cache.
        
        Args:
            key: Cache key
            value: Dict to cache as JSON
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            json_str = json.dumps(value, ensure_ascii=False)
            return await self.set(key, json_str, ttl)
        except Exception as e:
            logger.error(f"Error encoding JSON for cache: {e}")
            return False
    
    # ========================================================================
    # PATTERN OPERATIONS
    # ========================================================================
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.
        
        Args:
            pattern: Pattern to match (e.g., "guild:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.connected or not self.client:
            return 0
        
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                deleted = await self.client.delete(*keys)
                logger.info(f"Cache DELETE PATTERN: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error deleting pattern from cache: {e}")
            return 0
    
    async def get_keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern.
        
        Args:
            pattern: Pattern to match
            
        Returns:
            List of matching keys
        """
        if not self.connected or not self.client:
            return []
        
        try:
            keys = []
            async for key in self.client.scan_iter(match=pattern):
                keys.append(key)
            return keys
        except Exception as e:
            logger.error(f"Error getting keys from cache: {e}")
            return []
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dict with cache stats
        """
        if not self.connected or not self.client:
            return {"connected": False}
        
        try:
            info = await self.client.info("stats")
            return {
                "connected": True,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "instantaneous_ops": info.get("instantaneous_ops_per_sec", 0)
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"connected": True, "error": str(e)}
    
    async def clear_all(self) -> bool:
        """Clear all cache (use with caution).
        
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            return False
        
        try:
            await self.client.flushdb()
            logger.warning("⚠️ All cache cleared!")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False


# Global cache instance
cache: Optional[RedisCache] = None


async def init_cache(connection_string: str = None) -> bool:
    """Initialize global cache connection.
    
    Args:
        connection_string: Redis connection URL (optional, uses env if not provided)
        
    Returns:
        True if successful, False otherwise
    """
    global cache
    
    if not connection_string:
        connection_string = os.getenv('REDIS_URL') or os.getenv('REDIS_URI')
    
    if not connection_string:
        logger.warning("Redis connection string not found, cache disabled")
        cache = None
        return False
    
    cache = RedisCache(connection_string)
    success = await cache.connect()
    
    # If connection failed, set cache to None
    if not success:
        cache = None
        
    return success


async def close_cache():
    """Close global cache connection."""
    global cache
    if cache:
        await cache.disconnect()

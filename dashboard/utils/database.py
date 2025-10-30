"""
Database Connection Utilities
"""

from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from typing import Optional
from ..config import MONGODB_URI, MONGODB_DB, REDIS_URL

# Global connections
_mongodb_client: Optional[AsyncIOMotorClient] = None
_redis_client: Optional[Redis] = None

async def get_database():
    """Get MongoDB database connection"""
    global _mongodb_client
    
    if _mongodb_client is None:
        _mongodb_client = AsyncIOMotorClient(MONGODB_URI)
    
    return _mongodb_client[MONGODB_DB]

async def get_redis():
    """Get Redis connection"""
    global _redis_client
    
    if _redis_client is None:
        _redis_client = Redis.from_url(REDIS_URL, decode_responses=True)
    
    return _redis_client

async def close_connections():
    """Close database connections"""
    global _mongodb_client, _redis_client
    
    if _mongodb_client:
        _mongodb_client.close()
        _mongodb_client = None
    
    if _redis_client:
        await _redis_client.close()
        _redis_client = None

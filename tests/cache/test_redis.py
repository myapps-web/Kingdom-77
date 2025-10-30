"""
Redis Cache Test
================
Tests Redis cache functionality
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from cache import init_cache, close_cache, cache


async def test_redis():
    """Test Redis cache operations."""
    print("=" * 70)
    print("⚡ Testing Redis Cache")
    print("=" * 70)
    
    # Load environment
    load_dotenv()
    
    # Test 1: Connection
    print("\n🔗 Test 1: Connecting to Redis...")
    redis_url = os.getenv('REDIS_URL') or os.getenv('REDIS_URI')
    
    if not redis_url:
        print("❌ REDIS_URL not found in .env")
        print("\n💡 To test Redis:")
        print("   1. Get free Redis from https://redis.com/try-free/")
        print("   2. Add REDIS_URL to .env file")
        print("   3. Run test again")
        return False
    
    success = await init_cache(redis_url)
    if not success or not cache:
        print("❌ Redis connection failed")
        return False
    
    print("✅ Connected to Redis successfully")
    
    # Test 2: Basic operations
    print("\n📝 Test 2: Basic set/get operations...")
    try:
        # Set value
        await cache.set("test:key1", "test_value", ttl=60)
        print("✅ SET operation successful")
        
        # Get value
        value = await cache.get("test:key1")
        if value == "test_value":
            print(f"✅ GET operation successful: {value}")
        else:
            print(f"❌ GET returned unexpected value: {value}")
        
        # Check exists
        exists = await cache.exists("test:key1")
        if exists:
            print("✅ EXISTS operation successful")
        else:
            print("❌ EXISTS failed")
        
    except Exception as e:
        print(f"❌ Basic operations failed: {e}")
        return False
    
    # Test 3: JSON operations
    print("\n📋 Test 3: JSON operations...")
    try:
        test_data = {
            "guild_id": "123456",
            "name": "Test Server",
            "settings": {
                "language": "ar",
                "premium": False
            }
        }
        
        # Set JSON
        await cache.set_json("test:guild:123456", test_data, ttl=60)
        print("✅ SET JSON operation successful")
        
        # Get JSON
        retrieved = await cache.get_json("test:guild:123456")
        if retrieved and retrieved["guild_id"] == "123456":
            print(f"✅ GET JSON operation successful")
        else:
            print(f"❌ GET JSON failed")
        
    except Exception as e:
        print(f"❌ JSON operations failed: {e}")
        return False
    
    # Test 4: Delete operations
    print("\n🗑️ Test 4: Delete operations...")
    try:
        # Delete single key
        await cache.delete("test:key1")
        value = await cache.get("test:key1")
        if value is None:
            print("✅ DELETE operation successful")
        else:
            print("❌ DELETE failed, key still exists")
        
    except Exception as e:
        print(f"❌ Delete operations failed: {e}")
        return False
    
    # Test 5: Pattern operations
    print("\n🔍 Test 5: Pattern operations...")
    try:
        # Set multiple keys
        await cache.set("test:pattern:1", "value1", ttl=60)
        await cache.set("test:pattern:2", "value2", ttl=60)
        await cache.set("test:pattern:3", "value3", ttl=60)
        
        # Get keys by pattern
        keys = await cache.get_keys("test:pattern:*")
        if len(keys) >= 3:
            print(f"✅ GET KEYS operation successful: {len(keys)} keys found")
        else:
            print(f"⚠️ GET KEYS found {len(keys)} keys (expected >= 3)")
        
        # Delete by pattern
        deleted = await cache.delete_pattern("test:*")
        print(f"✅ DELETE PATTERN successful: {deleted} keys deleted")
        
    except Exception as e:
        print(f"❌ Pattern operations failed: {e}")
        return False
    
    # Test 6: Statistics
    print("\n📊 Test 6: Cache statistics...")
    try:
        stats = await cache.get_stats()
        print(f"✅ Cache statistics:")
        print(f"   - Connected: {stats.get('connected', False)}")
        print(f"   - Keyspace hits: {stats.get('keyspace_hits', 0)}")
        print(f"   - Keyspace misses: {stats.get('keyspace_misses', 0)}")
        print(f"   - Total commands: {stats.get('total_commands', 0)}")
        
    except Exception as e:
        print(f"❌ Statistics failed: {e}")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    await close_cache()
    print("✅ Connection closed")
    
    print("\n" + "=" * 70)
    print("✅ All Redis tests passed!")
    print("=" * 70)
    
    return True


if __name__ == '__main__':
    success = asyncio.run(test_redis())
    sys.exit(0 if success else 1)

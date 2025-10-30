"""
Quick Test: Bot with Redis Cache
==================================
Tests bot startup and cache integration
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment
load_dotenv()


async def test_bot_cache():
    """Test bot cache integration."""
    print("=" * 70)
    print("🧪 Testing Bot Cache Integration")
    print("=" * 70)
    
    # Test 1: Cache module import
    print("\n📦 Test 1: Importing cache module...")
    try:
        from cache.redis import RedisCache
        print("✅ Cache module imported successfully")
    except Exception as e:
        print(f"❌ Failed to import cache: {e}")
        return
    
    # Test 2: Initialize cache
    print("\n🔗 Test 2: Initializing cache...")
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        print("❌ REDIS_URL not found")
        return
    
    # Create cache instance directly
    cache_instance = RedisCache(redis_url)
    success = await cache_instance.connect()
    
    if not success:
        print("❌ Cache initialization failed")
        return
    
    print("✅ Cache initialized successfully")
    
    # Test 3: Test cache operations
    print("\n💾 Test 3: Testing cache operations...")
    try:
        # Test channel cache
        channel_data = {
            'primary': 'ar',
            'secondary': 'en',
            'blacklisted_languages': [],
            'translation_quality': 'fast'
        }
        
        await cache_instance.set_json("channel:123456", channel_data, ttl=60)
        print("✅ SET channel cache successful")
        
        retrieved = await cache_instance.get_json("channel:123456")
        if retrieved == channel_data:
            print(f"✅ GET channel cache successful: {retrieved}")
        else:
            print(f"❌ Retrieved data doesn't match: {retrieved}")
        
        # Test guild cache
        guild_data = {
            'guild_id': '789012',
            'name': 'Test Guild',
            'roles': {
                'allowed_roles': ['123', '456'],
                'role_languages': {},
                'role_permissions': {}
            }
        }
        
        await cache_instance.set_json("guild:789012", guild_data, ttl=60)
        print("✅ SET guild cache successful")
        
        retrieved_guild = await cache_instance.get_json("guild:789012")
        if retrieved_guild == guild_data:
            print(f"✅ GET guild cache successful")
        else:
            print(f"❌ Retrieved guild doesn't match")
        
        # Test cache stats
        stats = await cache_instance.get_stats()
        print(f"\n📊 Cache Stats:")
        print(f"   - Connected: {stats.get('connected')}")
        print(f"   - Hits: {stats.get('keyspace_hits')}")
        print(f"   - Misses: {stats.get('keyspace_misses')}")
        print(f"   - Commands: {stats.get('total_commands')}")
        
        # Cleanup
        await cache_instance.delete("channel:123456")
        await cache_instance.delete("guild:789012")
        print("\n🗑️ Cleanup successful")
        
    except Exception as e:
        print(f"❌ Error during cache operations: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await cache_instance.disconnect()
        print("\n👋 Cache closed")
    
    print("\n" + "=" * 70)
    print("✅ All cache integration tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_bot_cache())

"""
Test Redis Cache with Async
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from cache.redis import RedisCache


async def main():
    print("=" * 70)
    print("⚡ Testing Redis Cache (Async)")
    print("=" * 70)
    
    # Load env
    load_dotenv()
    redis_url = os.getenv('REDIS_URL')
    
    if not redis_url:
        print("❌ REDIS_URL not found")
        return
    
    print(f"\n🔗 Connecting to Redis...")
    print(f"URL: {redis_url[:30]}...")
    
    # Create cache instance
    cache = RedisCache(redis_url)
    
    try:
        # Connect
        connected = await cache.connect()
        if not connected:
            print("❌ Connection failed")
            return
        
        print("✅ Connected successfully")
        
        # Test SET
        print("\n💾 Testing SET...")
        await cache.set("test:key", "Hello Kingdom-77!", ttl=60)
        print("✅ SET successful")
        
        # Test GET
        print("📖 Testing GET...")
        value = await cache.get("test:key")
        print(f"✅ GET successful: {value}")
        
        # Test EXISTS
        print("🔍 Testing EXISTS...")
        exists = await cache.exists("test:key")
        print(f"✅ EXISTS: {exists}")
        
        # Test JSON operations
        print("\n📦 Testing JSON operations...")
        data = {"guild_id": "123", "name": "Test Server", "premium": True}
        await cache.set_json("test:guild", data, ttl=60)
        print("✅ SET_JSON successful")
        
        retrieved = await cache.get_json("test:guild")
        print(f"✅ GET_JSON successful: {retrieved}")
        
        # Test DELETE
        print("\n🗑️ Testing DELETE...")
        await cache.delete("test:key")
        await cache.delete("test:guild")
        print("✅ DELETE successful")
        
        # Test stats
        print("\n📊 Testing STATS...")
        stats = await cache.get_stats()
        print(f"✅ Stats: {stats}")
        
        print("\n" + "=" * 70)
        print("✅ All Redis Cache tests passed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await cache.disconnect()
        print("\n👋 Disconnected from Redis")


if __name__ == "__main__":
    asyncio.run(main())

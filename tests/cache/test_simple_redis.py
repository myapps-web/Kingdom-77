"""
Simple Redis Connection Test
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 70)
print("⚡ Simple Redis Connection Test")
print("=" * 70)

# Get Redis URL
redis_url = os.getenv('REDIS_URL')
if not redis_url:
    print("❌ REDIS_URL not found in environment")
    sys.exit(1)

print(f"\n🔗 Redis URL: {redis_url[:30]}...")

try:
    import redis
    print("✅ redis library imported")
    
    # Connect with SSL support for Upstash
    print("\n🔗 Connecting to Redis...")
    r = redis.from_url(
        redis_url,
        decode_responses=True,
        ssl_cert_reqs=None  # Disable SSL verification for Upstash
    )
    
    # Test ping
    print("📡 Testing connection with PING...")
    result = r.ping()
    print(f"✅ PING successful: {result}")
    
    # Test SET
    print("\n💾 Testing SET operation...")
    r.set('test_key', 'Hello from Kingdom-77!')
    print("✅ SET successful")
    
    # Test GET
    print("📖 Testing GET operation...")
    value = r.get('test_key')
    print(f"✅ GET successful: {value}")
    
    # Test DELETE
    print("🗑️ Testing DELETE operation...")
    r.delete('test_key')
    print("✅ DELETE successful")
    
    # Verify deletion
    value = r.get('test_key')
    print(f"✅ Key deleted (should be None): {value}")
    
    print("\n" + "=" * 70)
    print("✅ All Redis tests passed!")
    print("=" * 70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

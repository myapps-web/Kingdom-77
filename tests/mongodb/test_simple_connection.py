"""
Simple MongoDB Connection Test
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

async def test_simple_connection():
    """Test direct connection to MongoDB."""
    load_dotenv()
    
    mongodb_uri = os.getenv('MONGODB_URI')
    db_name = os.getenv('MONGODB_DB_NAME', 'kingdom77_bot')
    
    print("=" * 60)
    print("🔍 Simple MongoDB Connection Test")
    print("=" * 60)
    print(f"\n📋 Connection Details:")
    print(f"   URI: {mongodb_uri[:50]}...")
    print(f"   Database: {db_name}")
    
    try:
        print("\n📡 Connecting...")
        client = AsyncIOMotorClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        
        # Test connection
        await client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Get database
        db = client[db_name]
        
        # List collections
        collections = await db.list_collection_names()
        print(f"\n📊 Collections: {len(collections)}")
        if collections:
            for coll in collections:
                print(f"   - {coll}")
        else:
            print("   (Database is empty - no collections yet)")
        
        # Test write
        print("\n✍️ Testing write operation...")
        result = await db.test_collection.insert_one({"test": "connection", "timestamp": "now"})
        print(f"✅ Write successful! ID: {result.inserted_id}")
        
        # Test read
        print("\n📖 Testing read operation...")
        doc = await db.test_collection.find_one({"test": "connection"})
        if doc:
            print(f"✅ Read successful! Document: {doc}")
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        await db.test_collection.delete_one({"test": "connection"})
        print("✅ Cleanup done!")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
        client.close()
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"   Message: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check MONGODB_URI in .env file")
        print("   2. Verify username and password are correct")
        print("   3. Check IP whitelist in MongoDB Atlas")
        print("   4. Ensure internet connection is working")
        return False

if __name__ == '__main__':
    asyncio.run(test_simple_connection())

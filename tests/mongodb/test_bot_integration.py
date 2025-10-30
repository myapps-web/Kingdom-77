"""
Bot Integration Test
====================
Tests bot initialization and MongoDB integration without connecting to Discord
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

async def test_bot_mongodb_integration():
    """Test bot's MongoDB integration."""
    print("=" * 70)
    print("🤖 Testing Bot MongoDB Integration")
    print("=" * 70)
    
    # Load environment
    load_dotenv()
    
    # Test 1: Import bot modules
    print("\n📦 Test 1: Importing bot modules...")
    try:
        from database import init_database, close_database
        import database.mongodb as mongodb_module
        print("✅ Bot modules imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Test 2: Connect to MongoDB
    print("\n🔗 Test 2: Connecting to MongoDB...")
    try:
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ MONGODB_URI not found in .env")
            return False
        
        await init_database(mongodb_uri)
        
        if not mongodb_module.db or not mongodb_module.db.client:
            print("❌ MongoDB connection failed")
            return False
        
        print("✅ MongoDB connected successfully")
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 3: Load data from MongoDB
    print("\n📥 Test 3: Loading data from MongoDB...")
    try:
        # Test channel loading
        channels = await mongodb_module.db.db.channels.find().to_list(length=None)
        print(f"✅ Loaded {len(channels)} channels from MongoDB")
        
        # Test ratings loading
        ratings = await mongodb_module.db.db.ratings.find().to_list(length=None)
        print(f"✅ Loaded {len(ratings)} ratings from MongoDB")
        
        # Test guilds loading
        guilds = await mongodb_module.db.db.guilds.find().to_list(length=None)
        print(f"✅ Loaded {len(guilds)} guilds from MongoDB")
        
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        return False
    
    # Test 4: Test write operations
    print("\n📤 Test 4: Testing write operations...")
    try:
        # Test channel write
        test_channel = {
            "channel_id": "test_channel_123",
            "primary": "ar",
            "secondary": "en",
            "blacklisted_languages": [],
            "translation_quality": "fast"
        }
        
        await mongodb_module.db.db.channels.update_one(
            {"channel_id": "test_channel_123"},
            {"$set": test_channel},
            upsert=True
        )
        print("✅ Write operation successful")
        
        # Clean up test data
        await mongodb_module.db.db.channels.delete_one({"channel_id": "test_channel_123"})
        print("✅ Cleanup successful")
        
    except Exception as e:
        print(f"❌ Write operation error: {e}")
        return False
    
    # Test 5: Close connection
    print("\n🔌 Test 5: Closing MongoDB connection...")
    try:
        await close_database()
        print("✅ Connection closed successfully")
    except Exception as e:
        print(f"❌ Close error: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✅ All integration tests passed!")
    print("=" * 70)
    print("\n💡 Next step: Configure DISCORD_TOKEN in .env to run the bot")
    return True

if __name__ == '__main__':
    success = asyncio.run(test_bot_mongodb_integration())
    sys.exit(0 if success else 1)

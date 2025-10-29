"""
Quick MongoDB Connection Test
==============================
Tests MongoDB connection and displays basic info
"""

import asyncio
import os
from dotenv import load_dotenv
import database.mongodb as mongodb_module
from database import init_database, close_database


async def test_connection():
    """Test MongoDB connection."""
    print("=" * 60)
    print("🔍 Testing MongoDB Connection")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in .env file")
        print("Please add your MongoDB connection string to .env")
        return False
    
    # Connect
    print("\n📡 Connecting to MongoDB...")
    try:
        success = await init_database(mongodb_uri)
        print(f"   init_database returned: {success}")
        print(f"   db object: {mongodb_module.db}")
        print(f"   db.client: {mongodb_module.db.client if mongodb_module.db else 'None'}")
        
        if not success:
            print("❌ Connection failed - init_database returned False")
            return False
        if not mongodb_module.db:
            print("❌ Connection failed - db object is None")
            return False
        if not mongodb_module.db.client:
            print("❌ Connection failed - db.client is None")
            return False
    except Exception as e:
        print(f"❌ Connection failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✅ Connected successfully!")
    
    # Get collection counts
    try:
        print("\n📊 Database Statistics:")
        print("-" * 60)
        
        guilds_count = await mongodb_module.db.db.guilds.count_documents({})
        channels_count = await mongodb_module.db.db.channels.count_documents({})
        users_count = await mongodb_module.db.db.users.count_documents({})
        ratings_count = await mongodb_module.db.db.ratings.count_documents({})
        
        print(f"   Guilds:     {guilds_count}")
        print(f"   Channels:   {channels_count}")
        print(f"   Users:      {users_count}")
        print(f"   Ratings:    {ratings_count}")
        
        # List all collections
        print("\n📋 Collections:")
        print("-" * 60)
        collections = await mongodb_module.db.db.list_collection_names()
        if collections:
            for coll in collections:
                print(f"   - {coll}")
        else:
            print(f"   (No collections yet - database is empty)")
        
        print("\n" + "=" * 60)
        print("✅ Test completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        return False
    
    finally:
        await close_database()


if __name__ == '__main__':
    asyncio.run(test_connection())

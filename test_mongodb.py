"""
Quick MongoDB Connection Test
==============================
Tests MongoDB connection and displays basic info
"""

import asyncio
import os
from dotenv import load_dotenv
from database import init_database, close_database, db


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
    success = await init_database(mongodb_uri)
    
    if not success:
        print("❌ Connection failed")
        return False
    
    print("✅ Connected successfully!")
    
    # Get collection counts
    try:
        print("\n📊 Database Statistics:")
        print("-" * 60)
        
        guilds_count = await db.db.guilds.count_documents({})
        channels_count = await db.db.channels.count_documents({})
        users_count = await db.db.users.count_documents({})
        ratings_count = await db.db.ratings.count_documents({})
        
        print(f"   Guilds:     {guilds_count}")
        print(f"   Channels:   {channels_count}")
        print(f"   Users:      {users_count}")
        print(f"   Ratings:    {ratings_count}")
        
        # List all collections
        print("\n📋 Collections:")
        print("-" * 60)
        collections = await db.db.list_collection_names()
        for coll in collections:
            print(f"   - {coll}")
        
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

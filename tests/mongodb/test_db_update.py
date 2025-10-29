"""Test if db updates correctly"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

async def test():
    load_dotenv()
    uri = os.getenv('MONGODB_URI')
    
    print("Before import:")
    
    import database.mongodb as mongodb_module
    print(f"mongodb_module.db = {mongodb_module.db}")
    
    print("\nCalling init_database...")
    result = await mongodb_module.init_database(uri)
    print(f"Result: {result}")
    
    print(f"\nAfter init:")
    print(f"mongodb_module.db = {mongodb_module.db}")
    print(f"mongodb_module.db.client = {mongodb_module.db.client if mongodb_module.db else 'None'}")
    
    if mongodb_module.db:
        print("\n✅ db object was created successfully!")
        print(f"Database name: {mongodb_module.db.db.name if mongodb_module.db.db else 'None'}")
    else:
        print("\n❌ db object is still None!")

asyncio.run(test())

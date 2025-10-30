"""
Quick test to verify MongoDB imports work correctly
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def test_imports():
    """Test that all MongoDB modules can be imported"""
    print("Testing MongoDB imports...")
    
    try:
        from database import MongoDB, db, init_database, close_database
        print("✅ Successfully imported: MongoDB, db, init_database, close_database")
        
        from database.mongodb import MongoDB as MongoClass
        print("✅ Successfully imported: database.mongodb.MongoDB")
        
        from database.migration import DataMigration
        print("✅ Successfully imported: database.migration.DataMigration")
        
        print("\n✅ All MongoDB imports successful!")
        print("✅ Bot should start without import errors")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nMake sure you've installed dependencies:")
        print("  pip install motor pymongo dnspython")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

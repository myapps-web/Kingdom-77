"""
Script to fix type hints in database schema files
"""
import os
import re

# List of files to fix
files_to_fix = [
    "database/custom_commands_schema.py",
    "database/logging_schema.py",
    "database/economy_schema.py",
    "database/social_integration_schema.py",
    "database/level_cards_schema.py",
    "database/giveaway_schema.py",
    "database/automod_schema.py",
    "database/automessages_schema.py",
    "database/application_schema.py"
]

base_dir = r"c:\Users\Abdullah_QE\OneDrive\سطح المكتب\Kingdom-77"

for file_path in files_to_fix:
    full_path = os.path.join(base_dir, file_path)
    
    if not os.path.exists(full_path):
        print(f"⚠️ File not found: {file_path}")
        continue
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace AsyncIOMotorDatabase type hint with generic
        original_content = content
        content = re.sub(
            r'def __init__\(self, db: AsyncIOMotorDatabase\):',
            'def __init__(self, db):',
            content
        )
        
        # Also fix AsyncIOMotorClient if found
        content = re.sub(
            r'def __init__\(self, mongo_client: AsyncIOMotorClient, db_name: str = "kingdom77"\):',
            'def __init__(self, mongo_client, db_name: str = "kingdom77"):',
            content
        )
        
        if content != original_content:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed: {file_path}")
        else:
            print(f"ℹ️ No changes needed: {file_path}")
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")

print("\n✅ Type hints fix completed!")

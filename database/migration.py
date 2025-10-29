"""
Data Migration Script: JSON to MongoDB
=======================================
Migrates all existing JSON data to MongoDB Atlas
"""

import asyncio
import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.mongodb import MongoDB

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class DataMigration:
    """Handles migration from JSON files to MongoDB."""
    
    def __init__(self, mongodb_uri: str, data_dir: str = 'data'):
        self.mongodb_uri = mongodb_uri
        self.data_dir = data_dir
        self.db = MongoDB(mongodb_uri)
        self.stats = {
            'guilds': 0,
            'channels': 0,
            'roles': 0,
            'users': 0,
            'ratings': 0,
            'errors': 0
        }
    
    async def connect(self):
        """Connect to MongoDB."""
        success = await self.db.connect()
        if not success:
            logger.error("❌ Failed to connect to MongoDB")
            return False
        return True
    
    def load_json_file(self, filename: str) -> Dict[str, Any]:
        """Load data from JSON file."""
        filepath = os.path.join(self.data_dir, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"⚠️  File not found: {filename}")
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"✅ Loaded {filename}: {len(data)} entries")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parsing {filename}: {e}")
            return {}
        except Exception as e:
            logger.error(f"❌ Error loading {filename}: {e}")
            return {}
    
    async def migrate_channels(self):
        """Migrate channel language settings."""
        logger.info("\n📋 Migrating channel settings...")
        
        channels_data = self.load_json_file('channels.json')
        
        for channel_id, config in channels_data.items():
            try:
                # Prepare channel document
                channel_doc = {
                    "channel_id": channel_id,
                }
                
                # Handle both dict and string formats
                if isinstance(config, dict):
                    channel_doc["primary_language"] = config.get('primary')
                    channel_doc["secondary_language"] = config.get('secondary')
                    channel_doc["blacklisted_languages"] = config.get('blacklisted_languages', [])
                    channel_doc["translation_quality"] = config.get('translation_quality', 'fast')
                else:
                    # Legacy string format
                    channel_doc["primary_language"] = config
                    channel_doc["secondary_language"] = None
                    channel_doc["blacklisted_languages"] = []
                    channel_doc["translation_quality"] = 'fast'
                
                # Insert into MongoDB
                success = await self.db.update_channel_settings(int(channel_id), channel_doc)
                
                if success:
                    self.stats['channels'] += 1
                else:
                    self.stats['errors'] += 1
                    logger.error(f"Failed to migrate channel {channel_id}")
                    
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Error migrating channel {channel_id}: {e}")
        
        logger.info(f"✅ Migrated {self.stats['channels']} channels")
    
    async def migrate_roles(self):
        """Migrate role settings (allowed roles, languages, permissions)."""
        logger.info("\n🛡️  Migrating role settings...")
        
        # Load all role-related files
        allowed_roles = self.load_json_file('allowed_roles.json')
        role_languages = self.load_json_file('role_languages.json')
        role_permissions = self.load_json_file('role_permissions.json')
        
        # Combine by guild
        all_guilds = set(list(allowed_roles.keys()) + list(role_languages.keys()) + list(role_permissions.keys()))
        
        for guild_id in all_guilds:
            try:
                guild_doc = {
                    "guild_id": guild_id,
                    "allowed_roles": allowed_roles.get(guild_id, []),
                    "role_languages": role_languages.get(guild_id, {}),
                    "role_permissions": role_permissions.get(guild_id, {})
                }
                
                success = await self.db.update_guild_settings(int(guild_id), guild_doc)
                
                if success:
                    self.stats['guilds'] += 1
                else:
                    self.stats['errors'] += 1
                    
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Error migrating guild {guild_id}: {e}")
        
        logger.info(f"✅ Migrated {self.stats['guilds']} guilds")
    
    async def migrate_ratings(self):
        """Migrate user ratings."""
        logger.info("\n⭐ Migrating ratings...")
        
        ratings_data = self.load_json_file('ratings.json')
        
        for user_id, rating_info in ratings_data.items():
            try:
                rating_doc = {
                    "user_id": user_id,
                    "rating": rating_info.get('rating', 0),
                    "comment": rating_info.get('comment', ''),
                    "timestamp": rating_info.get('timestamp', '')
                }
                
                # Insert directly to ratings collection
                await self.db.db.ratings.insert_one(rating_doc)
                self.stats['ratings'] += 1
                
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Error migrating rating for user {user_id}: {e}")
        
        logger.info(f"✅ Migrated {self.stats['ratings']} ratings")
    
    async def migrate_servers(self):
        """Migrate server tracking data."""
        logger.info("\n🖥️  Migrating server data...")
        
        servers_data = self.load_json_file('servers.json')
        
        for guild_id, server_info in servers_data.items():
            try:
                # Update existing guild document with server info
                server_doc = {
                    "server_name": server_info.get('name', ''),
                    "active": server_info.get('active', True),
                    "joined_at": server_info.get('joined_at', ''),
                    "member_count": server_info.get('member_count', 0)
                }
                
                await self.db.update_guild_settings(int(guild_id), server_doc)
                
            except Exception as e:
                self.stats['errors'] += 1
                logger.error(f"Error migrating server {guild_id}: {e}")
        
        logger.info(f"✅ Updated server info for guilds")
    
    async def create_indexes(self):
        """Create database indexes for better performance."""
        logger.info("\n🔍 Creating database indexes...")
        
        try:
            # Guilds collection indexes
            await self.db.db.guilds.create_index("guild_id", unique=True)
            
            # Channels collection indexes
            await self.db.db.channels.create_index("channel_id", unique=True)
            
            # Users collection indexes
            await self.db.db.users.create_index([("user_id", 1), ("guild_id", 1)], unique=True)
            
            # Ratings collection indexes
            await self.db.db.ratings.create_index("user_id", unique=True)
            
            logger.info("✅ Indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    async def verify_migration(self):
        """Verify migrated data."""
        logger.info("\n🔍 Verifying migration...")
        
        try:
            guilds_count = await self.db.db.guilds.count_documents({})
            channels_count = await self.db.db.channels.count_documents({})
            ratings_count = await self.db.db.ratings.count_documents({})
            
            logger.info(f"📊 Migration Summary:")
            logger.info(f"   Guilds: {guilds_count}")
            logger.info(f"   Channels: {channels_count}")
            logger.info(f"   Ratings: {ratings_count}")
            logger.info(f"   Errors: {self.stats['errors']}")
            
        except Exception as e:
            logger.error(f"Error verifying migration: {e}")
    
    async def run(self):
        """Run complete migration."""
        logger.info("=" * 60)
        logger.info("🚀 Starting Data Migration: JSON → MongoDB")
        logger.info("=" * 60)
        
        # Connect to MongoDB
        if not await self.connect():
            return False
        
        try:
            # Run migrations
            await self.migrate_channels()
            await self.migrate_roles()
            await self.migrate_ratings()
            await self.migrate_servers()
            
            # Create indexes
            await self.create_indexes()
            
            # Verify
            await self.verify_migration()
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ Migration Completed Successfully!")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
        
        finally:
            await self.db.disconnect()


async def main():
    """Main migration entry point."""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri:
        logger.error("❌ MONGODB_URI not found in environment variables")
        logger.info("Please add MONGODB_URI to your .env file")
        return
    
    # Get data directory
    data_dir = os.getenv('DATA_DIR', 'data')
    
    # Run migration
    migration = DataMigration(mongodb_uri, data_dir)
    success = await migration.run()
    
    if success:
        logger.info("\n✨ You can now use MongoDB in your bot!")
        logger.info("💡 Remember to update main.py to use the database module")
    else:
        logger.error("\n❌ Migration failed. Please check errors above.")


if __name__ == '__main__':
    asyncio.run(main())

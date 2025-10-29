"""
MongoDB Database Module for Kingdom-77 Bot v3.0
================================================
Handles all database operations using MongoDB Atlas
"""

import os
import logging
from typing import Optional, Dict, List, Any
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB database manager with async support."""
    
    def __init__(self, connection_string: str):
        """Initialize MongoDB connection.
        
        Args:
            connection_string: MongoDB Atlas connection string
        """
        self.connection_string = connection_string
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000
            )
            # Test connection
            await self.client.admin.command('ping')
            
            # Get database name from environment or use default
            db_name = os.getenv('MONGODB_DB_NAME', 'kingdom77_bot')
            self.db = self.client[db_name]
            
            logger.info("✅ Successfully connected to MongoDB")
            return True
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error connecting to MongoDB: {e}")
            return False
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    # ========================================================================
    # GUILD SETTINGS
    # ========================================================================
    
    async def get_guild_settings(self, guild_id: int) -> Optional[Dict]:
        """Get guild settings from database.
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            Guild settings dictionary or None
        """
        try:
            guild = await self.db.guilds.find_one({"guild_id": str(guild_id)})
            return guild
        except Exception as e:
            logger.error(f"Error getting guild settings: {e}")
            return None
    
    async def update_guild_settings(self, guild_id: int, settings: Dict) -> bool:
        """Update guild settings in database.
        
        Args:
            guild_id: Discord guild ID
            settings: Settings dictionary to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.db.guilds.update_one(
                {"guild_id": str(guild_id)},
                {"$set": settings},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error updating guild settings: {e}")
            return False
    
    async def delete_guild(self, guild_id: int) -> bool:
        """Delete guild from database.
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = await self.db.guilds.delete_one({"guild_id": str(guild_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting guild: {e}")
            return False
    
    # ========================================================================
    # CHANNEL SETTINGS
    # ========================================================================
    
    async def get_channel_settings(self, channel_id: int) -> Optional[Dict]:
        """Get channel language settings."""
        try:
            channel = await self.db.channels.find_one({"channel_id": str(channel_id)})
            return channel
        except Exception as e:
            logger.error(f"Error getting channel settings: {e}")
            return None
    
    async def update_channel_settings(self, channel_id: int, settings: Dict) -> bool:
        """Update channel language settings."""
        try:
            result = await self.db.channels.update_one(
                {"channel_id": str(channel_id)},
                {"$set": settings},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error updating channel settings: {e}")
            return False
    
    async def delete_channel(self, channel_id: int) -> bool:
        """Delete channel settings."""
        try:
            result = await self.db.channels.delete_one({"channel_id": str(channel_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting channel: {e}")
            return False
    
    async def get_all_channels(self, guild_id: Optional[int] = None) -> List[Dict]:
        """Get all channel settings, optionally filtered by guild."""
        try:
            query = {}
            if guild_id:
                query["guild_id"] = str(guild_id)
            
            channels = await self.db.channels.find(query).to_list(length=None)
            return channels
        except Exception as e:
            logger.error(f"Error getting all channels: {e}")
            return []
    
    # ========================================================================
    # ROLE SETTINGS
    # ========================================================================
    
    async def get_allowed_roles(self, guild_id: int) -> List[str]:
        """Get allowed roles for a guild."""
        try:
            guild = await self.db.guilds.find_one({"guild_id": str(guild_id)})
            if guild and "allowed_roles" in guild:
                return guild["allowed_roles"]
            return []
        except Exception as e:
            logger.error(f"Error getting allowed roles: {e}")
            return []
    
    async def update_allowed_roles(self, guild_id: int, roles: List[str]) -> bool:
        """Update allowed roles for a guild."""
        try:
            result = await self.db.guilds.update_one(
                {"guild_id": str(guild_id)},
                {"$set": {"allowed_roles": roles}},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error updating allowed roles: {e}")
            return False
    
    async def get_role_language(self, guild_id: int, role_id: int) -> Optional[str]:
        """Get language for a specific role."""
        try:
            guild = await self.db.guilds.find_one({"guild_id": str(guild_id)})
            if guild and "role_languages" in guild:
                return guild["role_languages"].get(str(role_id))
            return None
        except Exception as e:
            logger.error(f"Error getting role language: {e}")
            return None
    
    async def update_role_language(self, guild_id: int, role_id: int, language: str) -> bool:
        """Set language for a role."""
        try:
            result = await self.db.guilds.update_one(
                {"guild_id": str(guild_id)},
                {"$set": {f"role_languages.{role_id}": language}},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error updating role language: {e}")
            return False
    
    async def delete_role_language(self, guild_id: int, role_id: int) -> bool:
        """Remove language from a role."""
        try:
            result = await self.db.guilds.update_one(
                {"guild_id": str(guild_id)},
                {"$unset": {f"role_languages.{role_id}": ""}}
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error deleting role language: {e}")
            return False
    
    # ========================================================================
    # USER DATA (for leveling, stats, etc.)
    # ========================================================================
    
    async def get_user_data(self, user_id: int, guild_id: int) -> Optional[Dict]:
        """Get user data for a specific guild."""
        try:
            user = await self.db.users.find_one({
                "user_id": str(user_id),
                "guild_id": str(guild_id)
            })
            return user
        except Exception as e:
            logger.error(f"Error getting user data: {e}")
            return None
    
    async def update_user_data(self, user_id: int, guild_id: int, data: Dict) -> bool:
        """Update user data."""
        try:
            result = await self.db.users.update_one(
                {"user_id": str(user_id), "guild_id": str(guild_id)},
                {"$set": data},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error updating user data: {e}")
            return False
    
    # ========================================================================
    # RATINGS
    # ========================================================================
    
    async def get_rating(self, user_id: int) -> Optional[Dict]:
        """Get user rating."""
        try:
            rating = await self.db.ratings.find_one({"user_id": str(user_id)})
            return rating
        except Exception as e:
            logger.error(f"Error getting rating: {e}")
            return None
    
    async def update_rating(self, user_id: int, rating: int, comment: str = "") -> bool:
        """Update user rating."""
        try:
            result = await self.db.ratings.update_one(
                {"user_id": str(user_id)},
                {
                    "$set": {
                        "rating": rating,
                        "comment": comment,
                        "timestamp": {"$currentDate": {"timestamp": True}}
                    }
                },
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error updating rating: {e}")
            return False
    
    async def get_all_ratings(self) -> List[Dict]:
        """Get all ratings."""
        try:
            ratings = await self.db.ratings.find().to_list(length=None)
            return ratings
        except Exception as e:
            logger.error(f"Error getting all ratings: {e}")
            return []
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    
    async def increment_translation_count(self, guild_id: int) -> bool:
        """Increment translation counter for a guild."""
        try:
            result = await self.db.guilds.update_one(
                {"guild_id": str(guild_id)},
                {"$inc": {"stats.translations": 1}},
                upsert=True
            )
            return result.acknowledged
        except Exception as e:
            logger.error(f"Error incrementing translation count: {e}")
            return False
    
    async def get_guild_stats(self, guild_id: int) -> Optional[Dict]:
        """Get guild statistics."""
        try:
            guild = await self.db.guilds.find_one({"guild_id": str(guild_id)})
            if guild and "stats" in guild:
                return guild["stats"]
            return {}
        except Exception as e:
            logger.error(f"Error getting guild stats: {e}")
            return {}


# Global database instance
db: Optional[MongoDB] = None


async def init_database(connection_string: str) -> bool:
    """Initialize global database connection.
    
    Args:
        connection_string: MongoDB connection string
        
    Returns:
        True if successful, False otherwise
    """
    global db
    db = MongoDB(connection_string)
    return await db.connect()


async def close_database():
    """Close global database connection."""
    global db
    if db:
        await db.disconnect()

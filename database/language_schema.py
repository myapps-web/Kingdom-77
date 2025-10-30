"""
Language Preferences Schema for Kingdom-77 Bot

This module handles language preference storage in MongoDB for users and guilds.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class LanguageSchema:
    """Manages language preferences in MongoDB"""
    
    def __init__(self, db):
        """
        Initialize the language schema
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.user_preferences = db.user_language_preferences
        self.guild_preferences = db.guild_language_preferences
        
        # Create indexes for better performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create database indexes"""
        try:
            self.user_preferences.create_index("user_id", unique=True)
            self.guild_preferences.create_index("guild_id", unique=True)
            logger.info("Language preferences indexes created")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # ==================== User Language Preferences ====================
    
    async def get_user_language(self, user_id: str) -> Optional[str]:
        """
        Get user's language preference
        
        Args:
            user_id: Discord user ID
        
        Returns:
            Language code or None if not set
        """
        try:
            result = await self.user_preferences.find_one({"user_id": user_id})
            return result.get("language") if result else None
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return None
    
    async def set_user_language(self, user_id: str, language: str) -> bool:
        """
        Set user's language preference
        
        Args:
            user_id: Discord user ID
            language: Language code (e.g., 'en', 'ar')
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.user_preferences.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "user_id": user_id,
                        "language": language,
                        "updated_at": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            logger.info(f"Set language for user {user_id}: {language}")
            return True
        except Exception as e:
            logger.error(f"Error setting user language: {e}")
            return False
    
    async def delete_user_language(self, user_id: str) -> bool:
        """
        Delete user's language preference (reset to default)
        
        Args:
            user_id: Discord user ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.user_preferences.delete_one({"user_id": user_id})
            logger.info(f"Deleted language preference for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting user language: {e}")
            return False
    
    async def get_all_user_languages(self) -> Dict[str, str]:
        """
        Get all user language preferences
        
        Returns:
            Dictionary of user_id -> language_code
        """
        try:
            result = {}
            async for doc in self.user_preferences.find({}):
                result[doc["user_id"]] = doc["language"]
            return result
        except Exception as e:
            logger.error(f"Error getting all user languages: {e}")
            return {}
    
    # ==================== Guild Language Preferences ====================
    
    async def get_guild_language(self, guild_id: str) -> Optional[str]:
        """
        Get guild's default language
        
        Args:
            guild_id: Discord guild ID
        
        Returns:
            Language code or None if not set
        """
        try:
            result = await self.guild_preferences.find_one({"guild_id": guild_id})
            return result.get("language") if result else None
        except Exception as e:
            logger.error(f"Error getting guild language: {e}")
            return None
    
    async def set_guild_language(self, guild_id: str, language: str, set_by: str) -> bool:
        """
        Set guild's default language
        
        Args:
            guild_id: Discord guild ID
            language: Language code (e.g., 'en', 'ar')
            set_by: User ID who set the language
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.guild_preferences.update_one(
                {"guild_id": guild_id},
                {
                    "$set": {
                        "guild_id": guild_id,
                        "language": language,
                        "set_by": set_by,
                        "updated_at": datetime.utcnow()
                    },
                    "$setOnInsert": {
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
            logger.info(f"Set language for guild {guild_id}: {language} (by {set_by})")
            return True
        except Exception as e:
            logger.error(f"Error setting guild language: {e}")
            return False
    
    async def delete_guild_language(self, guild_id: str) -> bool:
        """
        Delete guild's language preference (reset to default)
        
        Args:
            guild_id: Discord guild ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            await self.guild_preferences.delete_one({"guild_id": guild_id})
            logger.info(f"Deleted language preference for guild {guild_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting guild language: {e}")
            return False
    
    async def get_all_guild_languages(self) -> Dict[str, str]:
        """
        Get all guild language preferences
        
        Returns:
            Dictionary of guild_id -> language_code
        """
        try:
            result = {}
            async for doc in self.guild_preferences.find({}):
                result[doc["guild_id"]] = doc["language"]
            return result
        except Exception as e:
            logger.error(f"Error getting all guild languages: {e}")
            return {}
    
    # ==================== Statistics ====================
    
    async def get_language_statistics(self) -> Dict[str, Any]:
        """
        Get language usage statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            # User language stats
            user_pipeline = [
                {"$group": {"_id": "$language", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            user_stats = {}
            async for doc in self.user_preferences.aggregate(user_pipeline):
                user_stats[doc["_id"]] = doc["count"]
            
            # Guild language stats
            guild_pipeline = [
                {"$group": {"_id": "$language", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            
            guild_stats = {}
            async for doc in self.guild_preferences.aggregate(guild_pipeline):
                guild_stats[doc["_id"]] = doc["count"]
            
            total_users = await self.user_preferences.count_documents({})
            total_guilds = await self.guild_preferences.count_documents({})
            
            return {
                "total_users_with_preference": total_users,
                "total_guilds_with_preference": total_guilds,
                "user_language_breakdown": user_stats,
                "guild_language_breakdown": guild_stats
            }
        except Exception as e:
            logger.error(f"Error getting language statistics: {e}")
            return {}
    
    # ==================== Migration ====================
    
    async def migrate_user_languages_from_i18n(self, i18n_manager):
        """
        Migrate user language preferences from i18n_manager to database
        
        Args:
            i18n_manager: I18nManager instance
        
        Returns:
            Number of migrated preferences
        """
        try:
            count = 0
            for user_id, language in i18n_manager.user_languages.items():
                success = await self.set_user_language(user_id, language)
                if success:
                    count += 1
            
            logger.info(f"Migrated {count} user language preferences")
            return count
        except Exception as e:
            logger.error(f"Error migrating user languages: {e}")
            return 0
    
    async def migrate_guild_languages_from_i18n(self, i18n_manager):
        """
        Migrate guild language preferences from i18n_manager to database
        
        Args:
            i18n_manager: I18nManager instance
        
        Returns:
            Number of migrated preferences
        """
        try:
            count = 0
            for guild_id, language in i18n_manager.guild_languages.items():
                success = await self.set_guild_language(guild_id, language, "system")
                if success:
                    count += 1
            
            logger.info(f"Migrated {count} guild language preferences")
            return count
        except Exception as e:
            logger.error(f"Error migrating guild languages: {e}")
            return 0
    
    async def load_preferences_to_i18n(self, i18n_manager):
        """
        Load language preferences from database to i18n_manager
        
        Args:
            i18n_manager: I18nManager instance
        """
        try:
            # Load user preferences
            user_langs = await self.get_all_user_languages()
            i18n_manager.user_languages = user_langs
            
            # Load guild preferences
            guild_langs = await self.get_all_guild_languages()
            i18n_manager.guild_languages = guild_langs
            
            logger.info(f"Loaded {len(user_langs)} user and {len(guild_langs)} guild language preferences")
        except Exception as e:
            logger.error(f"Error loading preferences to i18n: {e}")

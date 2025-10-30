"""
Moderation System for Kingdom-77 Bot v3.0
==========================================
Core moderation functionality: warnings, mutes, kicks, bans
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import discord
from discord import Member, User, Guild

logger = logging.getLogger(__name__)


class ModerationSystem:
    """Handles all moderation actions and logging."""
    
    def __init__(self, db):
        """Initialize moderation system.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        
    # ========================================================================
    # WARNINGS SYSTEM
    # ========================================================================
    
    async def add_warning(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """Add a warning to a user.
        
        Args:
            guild_id: Server ID
            user_id: User being warned
            moderator_id: Moderator issuing warning
            reason: Warning reason
            
        Returns:
            Warning document
        """
        try:
            warning_id = f"warn_{uuid.uuid4().hex[:8]}"
            warning = {
                "guild_id": guild_id,
                "user_id": user_id,
                "moderator_id": moderator_id,
                "warning_id": warning_id,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "active": True,
                "cleared_by": None,
                "cleared_at": None
            }
            
            await self.db.warnings.insert_one(warning)
            logger.info(f"Warning {warning_id} added for user {user_id} in guild {guild_id}")
            
            return warning
            
        except Exception as e:
            logger.error(f"Error adding warning: {e}")
            raise
    
    async def get_user_warnings(
        self,
        guild_id: str,
        user_id: str,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all warnings for a user.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            active_only: Only return active warnings
            
        Returns:
            List of warning documents
        """
        try:
            query = {"guild_id": guild_id, "user_id": user_id}
            if active_only:
                query["active"] = True
            
            warnings = await self.db.warnings.find(query).sort("timestamp", -1).to_list(length=None)
            return warnings
            
        except Exception as e:
            logger.error(f"Error getting warnings: {e}")
            return []
    
    async def clear_warning(
        self,
        warning_id: str,
        moderator_id: str
    ) -> bool:
        """Clear a specific warning.
        
        Args:
            warning_id: Warning ID to clear
            moderator_id: Moderator clearing the warning
            
        Returns:
            True if successful
        """
        try:
            result = await self.db.warnings.update_one(
                {"warning_id": warning_id},
                {"$set": {
                    "active": False,
                    "cleared_by": moderator_id,
                    "cleared_at": datetime.utcnow().isoformat()
                }}
            )
            
            if result.modified_count > 0:
                logger.info(f"Warning {warning_id} cleared by {moderator_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error clearing warning: {e}")
            return False
    
    async def clear_all_warnings(
        self,
        guild_id: str,
        user_id: str,
        moderator_id: str
    ) -> int:
        """Clear all warnings for a user.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            moderator_id: Moderator clearing warnings
            
        Returns:
            Number of warnings cleared
        """
        try:
            result = await self.db.warnings.update_many(
                {
                    "guild_id": guild_id,
                    "user_id": user_id,
                    "active": True
                },
                {"$set": {
                    "active": False,
                    "cleared_by": moderator_id,
                    "cleared_at": datetime.utcnow().isoformat()
                }}
            )
            
            count = result.modified_count
            logger.info(f"Cleared {count} warnings for user {user_id} in guild {guild_id}")
            return count
            
        except Exception as e:
            logger.error(f"Error clearing all warnings: {e}")
            return 0
    
    # ========================================================================
    # MODERATION ACTIONS
    # ========================================================================
    
    async def log_action(
        self,
        guild_id: str,
        action_type: str,
        user_id: str,
        user_tag: str,
        moderator_id: str,
        moderator_tag: str,
        reason: str,
        duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """Log a moderation action.
        
        Args:
            guild_id: Server ID
            action_type: warn, mute, unmute, kick, ban, unban
            user_id: Target user ID
            user_tag: Target username
            moderator_id: Moderator ID
            moderator_tag: Moderator username
            reason: Action reason
            duration: Duration in seconds (for temporary actions)
            
        Returns:
            Action document
        """
        try:
            action_id = f"action_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.utcnow()
            
            action = {
                "guild_id": guild_id,
                "action_id": action_id,
                "action_type": action_type,
                "user_id": user_id,
                "user_tag": user_tag,
                "moderator_id": moderator_id,
                "moderator_tag": moderator_tag,
                "reason": reason,
                "duration": duration,
                "timestamp": timestamp.isoformat(),
                "active": True,
                "ended_by": None,
                "ended_at": None
            }
            
            # Add expiration for temporary actions
            if duration:
                expires_at = timestamp + timedelta(seconds=duration)
                action["expires_at"] = expires_at.isoformat()
            else:
                action["expires_at"] = None
            
            await self.db.mod_actions.insert_one(action)
            logger.info(f"Action {action_id} logged: {action_type} on user {user_id} in guild {guild_id}")
            
            return action
            
        except Exception as e:
            logger.error(f"Error logging action: {e}")
            raise
    
    async def get_user_actions(
        self,
        guild_id: str,
        user_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get moderation history for a user.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            limit: Max number of actions to return
            
        Returns:
            List of action documents
        """
        try:
            actions = await self.db.mod_actions.find({
                "guild_id": guild_id,
                "user_id": user_id
            }).sort("timestamp", -1).limit(limit).to_list(length=None)
            
            return actions
            
        except Exception as e:
            logger.error(f"Error getting user actions: {e}")
            return []
    
    async def get_guild_actions(
        self,
        guild_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent moderation actions for a guild.
        
        Args:
            guild_id: Server ID
            limit: Max number of actions to return
            
        Returns:
            List of action documents
        """
        try:
            actions = await self.db.mod_actions.find({
                "guild_id": guild_id
            }).sort("timestamp", -1).limit(limit).to_list(length=None)
            
            return actions
            
        except Exception as e:
            logger.error(f"Error getting guild actions: {e}")
            return []
    
    # ========================================================================
    # GUILD CONFIG
    # ========================================================================
    
    async def get_guild_config(self, guild_id: str) -> Dict[str, Any]:
        """Get moderation config for a guild.
        
        Args:
            guild_id: Server ID
            
        Returns:
            Config document or default config
        """
        try:
            config = await self.db.guild_mod_config.find_one({"guild_id": guild_id})
            
            if not config:
                # Return default config
                config = {
                    "guild_id": guild_id,
                    "mod_log_channel": None,
                    "auto_mod_enabled": False,
                    "warn_threshold": 3,
                    "warn_action": "mute",
                    "warn_action_duration": 3600,
                    "mute_role": None,
                    "mod_roles": [],
                    "settings": {
                        "log_warnings": True,
                        "log_mutes": True,
                        "log_kicks": True,
                        "log_bans": True,
                        "dm_on_action": True,
                        "require_reason": True
                    }
                }
            
            return config
            
        except Exception as e:
            logger.error(f"Error getting guild config: {e}")
            return {}
    
    async def update_guild_config(
        self,
        guild_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update guild moderation config.
        
        Args:
            guild_id: Server ID
            updates: Fields to update
            
        Returns:
            True if successful
        """
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db.guild_mod_config.update_one(
                {"guild_id": guild_id},
                {"$set": updates},
                upsert=True
            )
            
            logger.info(f"Updated mod config for guild {guild_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating guild config: {e}")
            return False
    
    async def set_mod_log_channel(
        self,
        guild_id: str,
        channel_id: str
    ) -> bool:
        """Set moderation log channel.
        
        Args:
            guild_id: Server ID
            channel_id: Channel ID for logs
            
        Returns:
            True if successful
        """
        return await self.update_guild_config(guild_id, {"mod_log_channel": channel_id})
    
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
    async def check_warn_threshold(
        self,
        guild_id: str,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Check if user exceeded warning threshold.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            
        Returns:
            Auto-action config if threshold exceeded, None otherwise
        """
        try:
            config = await self.get_guild_config(guild_id)
            threshold = config.get("warn_threshold", 3)
            
            warnings = await self.get_user_warnings(guild_id, user_id, active_only=True)
            
            if len(warnings) >= threshold:
                return {
                    "action": config.get("warn_action", "mute"),
                    "duration": config.get("warn_action_duration", 3600)
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking warn threshold: {e}")
            return None


# Global mod system instance
_mod_system: Optional[ModerationSystem] = None


def get_mod_system(db) -> ModerationSystem:
    """Get or create global moderation system instance.
    
    Args:
        db: MongoDB database instance
        
    Returns:
        ModerationSystem instance
    """
    global _mod_system
    if _mod_system is None:
        _mod_system = ModerationSystem(db)
    return _mod_system

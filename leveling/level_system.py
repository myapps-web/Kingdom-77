"""
Leveling System for Kingdom-77 Bot v3.0
========================================
Core leveling functionality: XP tracking, level calculation, leaderboards
"""

import os
import logging
import math
import random
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import discord

logger = logging.getLogger(__name__)


class LevelingSystem:
    """Handles XP tracking and leveling."""
    
    def __init__(self, db):
        """Initialize leveling system.
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        
    # ========================================================================
    # XP CALCULATION
    # ========================================================================
    
    @staticmethod
    def calculate_level_from_xp(xp: int) -> int:
        """Calculate level from total XP (Nova System).
        
        Formula: Level = floor(XP / 100)
        Each level requires 100 XP.
        
        Args:
            xp: Total XP
            
        Returns:
            Current level
        """
        return int(xp // 100)
    
    @staticmethod
    def calculate_xp_for_level(level: int) -> int:
        """Calculate XP required to reach a level (Nova System).
        
        Formula: XP = Level × 100
        
        Args:
            level: Target level
            
        Returns:
            XP required
        """
        return level * 100
    
    @staticmethod
    def calculate_xp_for_next_level(current_level: int) -> int:
        """Calculate XP needed for next level.
        
        Args:
            current_level: Current level
            
        Returns:
            XP needed for next level
        """
        return LevelingSystem.calculate_xp_for_level(current_level + 1)
    
    @staticmethod
    def calculate_progress(current_xp: int, current_level: int) -> Dict[str, Any]:
        """Calculate progress to next level (Nova System).
        
        Args:
            current_xp: Current total XP
            current_level: Current level
            
        Returns:
            Dict with progress information
        """
        current_level_xp = LevelingSystem.calculate_xp_for_level(current_level)
        next_level_xp = LevelingSystem.calculate_xp_for_level(current_level + 1)
        
        xp_in_current_level = current_xp - current_level_xp
        xp_needed_for_level = 100  # Always 100 XP per level in Nova system
        
        percentage = (xp_in_current_level / xp_needed_for_level) * 100 if xp_needed_for_level > 0 else 100
        
        return {
            "current_xp": xp_in_current_level,
            "needed_xp": xp_needed_for_level,
            "next_level_xp": next_level_xp,
            "percentage": min(100, max(0, percentage)),
            "level": current_level
        }
    
    # ========================================================================
    # USER LEVEL MANAGEMENT
    # ========================================================================
    
    async def get_user_level(self, guild_id: str, user_id: str) -> Dict[str, Any]:
        """Get user's level data.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            
        Returns:
            User level document or new user data
        """
        try:
            user_data = await self.db.user_levels.find_one({
                "guild_id": guild_id,
                "user_id": user_id
            })
            
            if not user_data:
                # Create new user
                user_data = {
                    "guild_id": guild_id,
                    "user_id": user_id,
                    "xp": 0,
                    "level": 0,
                    "messages": 0,
                    "last_xp_time": None,
                    "total_xp": 0,
                    "rank_card_color": "#5865F2",  # Discord blurple
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            
            return user_data
            
        except Exception as e:
            logger.error(f"Error getting user level: {e}")
            return {}
    
    async def add_xp(
        self,
        guild_id: str,
        user_id: str,
        xp_amount: int,
        reason: str = "message",
        bot=None
    ) -> Tuple[bool, Optional[int], Dict[str, Any]]:
        """Add XP to a user.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            xp_amount: Amount of XP to add
            reason: Reason for XP gain
            bot: Bot instance for premium check (optional)
            
        Returns:
            Tuple of (leveled_up, new_level, user_data)
        """
        try:
            user_data = await self.get_user_level(guild_id, user_id)
            
            old_level = user_data.get("level", 0)
            old_xp = user_data.get("xp", 0)
            
            # Apply Premium XP Boost if available
            final_xp = xp_amount
            if bot and hasattr(bot, 'premium_system') and bot.premium_system:
                try:
                    final_xp = await bot.premium_system.apply_xp_boost(guild_id, xp_amount)
                    if final_xp > xp_amount:
                        logger.debug(f"Premium XP boost applied: {xp_amount} -> {final_xp}")
                except Exception as e:
                    logger.warning(f"Could not apply XP boost: {e}")
                    final_xp = xp_amount
            
            # Add XP
            user_data["xp"] = old_xp + final_xp
            user_data["messages"] = user_data.get("messages", 0) + 1
            user_data["total_xp"] = user_data.get("total_xp", 0) + final_xp
            user_data["last_xp_time"] = datetime.utcnow().isoformat()
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Calculate new level
            new_level = self.calculate_level_from_xp(user_data["xp"])
            user_data["level"] = new_level
            
            # Save to database
            await self.db.user_levels.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {"$set": user_data},
                upsert=True
            )
            
            # Check if leveled up
            leveled_up = new_level > old_level
            
            logger.debug(f"Added {final_xp} XP to {user_id} in {guild_id}. Level: {old_level} -> {new_level}")
            
            return leveled_up, new_level if leveled_up else None, user_data
            
        except Exception as e:
            logger.error(f"Error adding XP: {e}")
            return False, None, {}
    
    async def remove_xp(
        self,
        guild_id: str,
        user_id: str,
        xp_amount: int
    ) -> Dict[str, Any]:
        """Remove XP from a user.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            xp_amount: Amount of XP to remove
            
        Returns:
            Updated user data
        """
        try:
            user_data = await self.get_user_level(guild_id, user_id)
            
            # Remove XP (don't go below 0)
            user_data["xp"] = max(0, user_data.get("xp", 0) - xp_amount)
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Recalculate level
            user_data["level"] = self.calculate_level_from_xp(user_data["xp"])
            
            # Save to database
            await self.db.user_levels.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {"$set": user_data},
                upsert=True
            )
            
            return user_data
            
        except Exception as e:
            logger.error(f"Error removing XP: {e}")
            return {}
    
    async def reset_user_xp(self, guild_id: str, user_id: str) -> bool:
        """Reset user's XP to 0.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            result = await self.db.user_levels.update_one(
                {"guild_id": guild_id, "user_id": user_id},
                {"$set": {
                    "xp": 0,
                    "level": 0,
                    "messages": 0,
                    "updated_at": datetime.utcnow().isoformat()
                }}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error resetting XP: {e}")
            return False
    
    # ========================================================================
    # LEADERBOARD
    # ========================================================================
    
    async def get_leaderboard(
        self,
        guild_id: str,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get server leaderboard.
        
        Args:
            guild_id: Server ID
            limit: Number of users to return
            offset: Starting position
            
        Returns:
            List of user data sorted by XP
        """
        try:
            leaderboard = await self.db.user_levels.find({
                "guild_id": guild_id
            }).sort("xp", -1).skip(offset).limit(limit).to_list(length=None)
            
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error getting leaderboard: {e}")
            return []
    
    async def get_user_rank(self, guild_id: str, user_id: str) -> Optional[int]:
        """Get user's rank in server.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            
        Returns:
            Rank position (1-based) or None
        """
        try:
            user_data = await self.get_user_level(guild_id, user_id)
            user_xp = user_data.get("xp", 0)
            
            # Count users with more XP
            higher_count = await self.db.user_levels.count_documents({
                "guild_id": guild_id,
                "xp": {"$gt": user_xp}
            })
            
            return higher_count + 1
            
        except Exception as e:
            logger.error(f"Error getting user rank: {e}")
            return None
    
    # ========================================================================
    # GUILD CONFIG
    # ========================================================================
    
    async def get_guild_config(self, guild_id: str) -> Dict[str, Any]:
        """Get guild leveling config.
        
        Args:
            guild_id: Server ID
            
        Returns:
            Config document or default config
        """
        try:
            config = await self.db.guild_level_config.find_one({"guild_id": guild_id})
            
            if not config:
                # Return default config
                config = {
                    "guild_id": guild_id,
                    "enabled": True,
                    "xp_rate": 1.0,
                    "xp_per_message": [15, 25],
                    "cooldown": 60,
                    "level_up_channel": None,
                    "level_up_message": "🎉 {user} leveled up to **Level {level}**!",
                    "no_xp_roles": [],
                    "no_xp_channels": [],
                    "double_xp_roles": [],
                    "level_roles": {},
                    "stack_roles": False,
                    "announce_level_up": True
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
        """Update guild leveling config.
        
        Args:
            guild_id: Server ID
            updates: Fields to update
            
        Returns:
            True if successful
        """
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db.guild_level_config.update_one(
                {"guild_id": guild_id},
                {"$set": updates},
                upsert=True
            )
            
            logger.info(f"Updated level config for guild {guild_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating guild config: {e}")
            return False
    
    async def check_cooldown(
        self,
        guild_id: str,
        user_id: str,
        cooldown_seconds: int = 60
    ) -> bool:
        """Check if user is on XP cooldown.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            cooldown_seconds: Cooldown duration
            
        Returns:
            True if on cooldown, False if can earn XP
        """
        try:
            user_data = await self.get_user_level(guild_id, user_id)
            last_xp_time = user_data.get("last_xp_time")
            
            if not last_xp_time:
                return False
            
            last_time = datetime.fromisoformat(last_xp_time)
            now = datetime.utcnow()
            
            time_diff = (now - last_time).total_seconds()
            
            return time_diff < cooldown_seconds
            
        except Exception as e:
            logger.error(f"Error checking cooldown: {e}")
            return False
    
    async def calculate_xp_gain(
        self,
        guild_id: str,
        user_id: str,
        member: discord.Member
    ) -> int:
        """Calculate XP gain for a message.
        
        Args:
            guild_id: Server ID
            user_id: User ID
            member: Discord member object
            
        Returns:
            XP amount to add
        """
        try:
            config = await self.get_guild_config(guild_id)
            
            # Base XP
            min_xp, max_xp = config.get("xp_per_message", [15, 25])
            base_xp = random.randint(min_xp, max_xp)
            
            # Apply multiplier
            xp_rate = config.get("xp_rate", 1.0)
            xp = int(base_xp * xp_rate)
            
            # Check for double XP roles
            double_xp_roles = config.get("double_xp_roles", [])
            if any(str(role.id) in double_xp_roles for role in member.roles):
                xp *= 2
            
            return xp
            
        except Exception as e:
            logger.error(f"Error calculating XP gain: {e}")
            return 0


# Global leveling system instance
_leveling_system: Optional[LevelingSystem] = None


def get_leveling_system(db) -> LevelingSystem:
    """Get or create global leveling system instance.
    
    Args:
        db: MongoDB database instance
        
    Returns:
        LevelingSystem instance
    """
    global _leveling_system
    if _leveling_system is None:
        _leveling_system = LevelingSystem(db)
    return _leveling_system

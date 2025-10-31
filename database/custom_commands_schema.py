"""
Kingdom-77 Bot - Custom Commands System Database Schema
Allows users to create custom commands with variables, embeds, and auto-responses
Premium limits: 10 free commands, unlimited for premium users
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import discord


class CustomCommandsSchema:
    """Database schema for Custom Commands System"""
    
    def __init__(self, db):
        self.db = db
        self.commands = db["custom_commands"]
        self.auto_responses = db["auto_responses"]
        self.command_usage = db["command_usage"]
        self.command_settings = db["command_settings"]
    
    async def setup_indexes(self):
        """Create database indexes for performance"""
        # Commands indexes
        await self.commands.create_index([("guild_id", 1), ("name", 1)], unique=True)
        await self.commands.create_index([("guild_id", 1), ("enabled", 1)])
        await self.commands.create_index([("guild_id", 1), ("created_at", -1)])
        
        # Auto-responses indexes
        await self.auto_responses.create_index([("guild_id", 1), ("trigger", 1)])
        await self.auto_responses.create_index([("guild_id", 1), ("enabled", 1)])
        
        # Usage indexes
        await self.command_usage.create_index([("guild_id", 1), ("command_name", 1)])
        await self.command_usage.create_index([("guild_id", 1), ("timestamp", -1)])
        await self.command_usage.create_index([("timestamp", 1)], expireAfterSeconds=2592000)  # 30 days
        
        # Settings indexes
        await self.command_settings.create_index("guild_id", unique=True)
    
    # ==================== Settings ====================
    
    async def get_settings(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get command settings for a guild"""
        return await self.command_settings.find_one({"guild_id": guild_id})
    
    async def create_default_settings(self, guild_id: int) -> Dict[str, Any]:
        """Create default settings"""
        settings = {
            "guild_id": guild_id,
            "enabled": True,
            "prefix": "!",  # Legacy prefix support
            "allow_mentions": True,
            "require_roles": [],  # Roles that can create commands
            "blacklisted_users": [],
            "blacklisted_channels": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        await self.command_settings.insert_one(settings)
        return settings
    
    async def update_settings(self, guild_id: int, updates: Dict[str, Any]) -> bool:
        """Update command settings"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.command_settings.update_one(
            {"guild_id": guild_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    # ==================== Custom Commands ====================
    
    async def create_command(
        self,
        guild_id: int,
        name: str,
        creator_id: int,
        response_type: str,  # text, embed, both
        response_content: Optional[str] = None,
        embed_data: Optional[Dict[str, Any]] = None,
        aliases: Optional[List[str]] = None,
        cooldown: int = 0,
        required_roles: Optional[List[int]] = None,
        allowed_channels: Optional[List[int]] = None,
        delete_trigger: bool = False
    ) -> str:
        """Create a custom command"""
        command = {
            "guild_id": guild_id,
            "name": name.lower(),
            "creator_id": creator_id,
            "enabled": True,
            "response_type": response_type,
            "response_content": response_content,
            "embed_data": embed_data,
            "aliases": aliases or [],
            "cooldown": cooldown,  # seconds
            "required_roles": required_roles or [],
            "allowed_channels": allowed_channels or [],
            "delete_trigger": delete_trigger,
            "use_count": 0,
            "last_used": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.commands.insert_one(command)
        return str(result.inserted_id)
    
    async def get_command(self, guild_id: int, name: str) -> Optional[Dict[str, Any]]:
        """Get a custom command by name or alias"""
        # Try exact name match
        command = await self.commands.find_one({
            "guild_id": guild_id,
            "name": name.lower()
        })
        
        if command:
            return command
        
        # Try alias match
        command = await self.commands.find_one({
            "guild_id": guild_id,
            "aliases": name.lower()
        })
        
        return command
    
    async def get_all_commands(
        self,
        guild_id: int,
        enabled_only: bool = True,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all custom commands for a guild"""
        query = {"guild_id": guild_id}
        if enabled_only:
            query["enabled"] = True
        
        cursor = self.commands.find(query).sort("name", 1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def update_command(
        self,
        guild_id: int,
        name: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update a custom command"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.commands.update_one(
            {"guild_id": guild_id, "name": name.lower()},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_command(self, guild_id: int, name: str) -> bool:
        """Delete a custom command"""
        result = await self.commands.delete_one({
            "guild_id": guild_id,
            "name": name.lower()
        })
        return result.deleted_count > 0
    
    async def increment_usage(self, guild_id: int, name: str) -> bool:
        """Increment command usage count"""
        result = await self.commands.update_one(
            {"guild_id": guild_id, "name": name.lower()},
            {
                "$inc": {"use_count": 1},
                "$set": {"last_used": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    async def get_command_count(self, guild_id: int, creator_id: Optional[int] = None) -> int:
        """Get total command count for a guild or user"""
        query = {"guild_id": guild_id}
        if creator_id:
            query["creator_id"] = creator_id
        return await self.commands.count_documents(query)
    
    async def toggle_command(self, guild_id: int, name: str, enabled: bool) -> bool:
        """Enable or disable a command"""
        result = await self.commands.update_one(
            {"guild_id": guild_id, "name": name.lower()},
            {"$set": {"enabled": enabled, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    # ==================== Auto-Responses ====================
    
    async def create_auto_response(
        self,
        guild_id: int,
        trigger: str,
        response: str,
        creator_id: int,
        match_type: str = "exact",  # exact, contains, starts_with, ends_with, regex
        case_sensitive: bool = False,
        delete_trigger: bool = False,
        cooldown: int = 0
    ) -> str:
        """Create an auto-response"""
        auto_response = {
            "guild_id": guild_id,
            "trigger": trigger if case_sensitive else trigger.lower(),
            "response": response,
            "creator_id": creator_id,
            "enabled": True,
            "match_type": match_type,
            "case_sensitive": case_sensitive,
            "delete_trigger": delete_trigger,
            "cooldown": cooldown,
            "use_count": 0,
            "last_used": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await self.auto_responses.insert_one(auto_response)
        return str(result.inserted_id)
    
    async def get_auto_response(self, guild_id: int, trigger: str) -> Optional[Dict[str, Any]]:
        """Get an auto-response by trigger"""
        return await self.auto_responses.find_one({
            "guild_id": guild_id,
            "trigger": trigger.lower()
        })
    
    async def get_all_auto_responses(
        self,
        guild_id: int,
        enabled_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all auto-responses for a guild"""
        query = {"guild_id": guild_id}
        if enabled_only:
            query["enabled"] = True
        
        cursor = self.auto_responses.find(query).sort("trigger", 1)
        return await cursor.to_list(length=None)
    
    async def update_auto_response(
        self,
        guild_id: int,
        trigger: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update an auto-response"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.auto_responses.update_one(
            {"guild_id": guild_id, "trigger": trigger.lower()},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_auto_response(self, guild_id: int, trigger: str) -> bool:
        """Delete an auto-response"""
        result = await self.auto_responses.delete_one({
            "guild_id": guild_id,
            "trigger": trigger.lower()
        })
        return result.deleted_count > 0
    
    async def increment_auto_response_usage(self, guild_id: int, trigger: str) -> bool:
        """Increment auto-response usage count"""
        result = await self.auto_responses.update_one(
            {"guild_id": guild_id, "trigger": trigger.lower()},
            {
                "$inc": {"use_count": 1},
                "$set": {"last_used": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    async def toggle_auto_response(self, guild_id: int, trigger: str, enabled: bool) -> bool:
        """Enable or disable an auto-response"""
        result = await self.auto_responses.update_one(
            {"guild_id": guild_id, "trigger": trigger.lower()},
            {"$set": {"enabled": enabled, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    # ==================== Usage Tracking ====================
    
    async def log_command_usage(
        self,
        guild_id: int,
        command_name: str,
        user_id: int,
        channel_id: int,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> str:
        """Log command usage"""
        usage = {
            "guild_id": guild_id,
            "command_name": command_name,
            "user_id": user_id,
            "channel_id": channel_id,
            "success": success,
            "error_message": error_message,
            "timestamp": datetime.utcnow()
        }
        result = await self.command_usage.insert_one(usage)
        return str(result.inserted_id)
    
    async def get_command_stats(
        self,
        guild_id: int,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get command usage statistics"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total usage
        total_usage = await self.command_usage.count_documents({
            "guild_id": guild_id,
            "timestamp": {"$gte": start_date}
        })
        
        # Most used commands
        pipeline = [
            {"$match": {
                "guild_id": guild_id,
                "timestamp": {"$gte": start_date}
            }},
            {"$group": {
                "_id": "$command_name",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        most_used = await self.command_usage.aggregate(pipeline).to_list(length=10)
        
        # Most active users
        pipeline = [
            {"$match": {
                "guild_id": guild_id,
                "timestamp": {"$gte": start_date}
            }},
            {"$group": {
                "_id": "$user_id",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        most_active_users = await self.command_usage.aggregate(pipeline).to_list(length=10)
        
        # Success rate
        success_count = await self.command_usage.count_documents({
            "guild_id": guild_id,
            "timestamp": {"$gte": start_date},
            "success": True
        })
        
        success_rate = (success_count / total_usage * 100) if total_usage > 0 else 0
        
        return {
            "total_usage": total_usage,
            "success_rate": round(success_rate, 2),
            "most_used_commands": most_used,
            "most_active_users": most_active_users,
            "period_days": days
        }
    
    async def get_user_command_history(
        self,
        guild_id: int,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get command usage history for a user"""
        cursor = self.command_usage.find({
            "guild_id": guild_id,
            "user_id": user_id
        }).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    # ==================== Premium Limits ====================
    
    async def check_command_limit(
        self,
        guild_id: int,
        is_premium: bool
    ) -> Dict[str, Any]:
        """Check if guild can create more commands"""
        count = await self.get_command_count(guild_id)
        limit = float('inf') if is_premium else 10
        
        return {
            "current": count,
            "limit": limit,
            "can_create": count < limit,
            "remaining": limit - count if not is_premium else float('inf')
        }
    
    async def get_premium_features(self, is_premium: bool) -> Dict[str, Any]:
        """Get available features based on premium status"""
        if is_premium:
            return {
                "max_commands": float('inf'),
                "max_aliases": 10,
                "max_embed_fields": 25,
                "cooldown_bypass": True,
                "advanced_variables": True,
                "regex_support": True,
                "custom_embeds": True,
                "auto_responses": float('inf')
            }
        else:
            return {
                "max_commands": 10,
                "max_aliases": 3,
                "max_embed_fields": 5,
                "cooldown_bypass": False,
                "advanced_variables": False,
                "regex_support": False,
                "custom_embeds": True,
                "auto_responses": 5
            }
    
    # ==================== Search & Filter ====================
    
    async def search_commands(
        self,
        guild_id: int,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search commands by name or content"""
        cursor = self.commands.find({
            "guild_id": guild_id,
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"response_content": {"$regex": query, "$options": "i"}},
                {"aliases": {"$regex": query, "$options": "i"}}
            ]
        }).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_commands_by_creator(
        self,
        guild_id: int,
        creator_id: int
    ) -> List[Dict[str, Any]]:
        """Get all commands created by a specific user"""
        cursor = self.commands.find({
            "guild_id": guild_id,
            "creator_id": creator_id
        }).sort("name", 1)
        return await cursor.to_list(length=None)
    
    async def get_popular_commands(
        self,
        guild_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get most used commands"""
        cursor = self.commands.find({
            "guild_id": guild_id
        }).sort("use_count", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    # ==================== Bulk Operations ====================
    
    async def bulk_delete_commands(
        self,
        guild_id: int,
        creator_id: Optional[int] = None
    ) -> int:
        """Delete multiple commands"""
        query = {"guild_id": guild_id}
        if creator_id:
            query["creator_id"] = creator_id
        
        result = await self.commands.delete_many(query)
        return result.deleted_count
    
    async def bulk_toggle_commands(
        self,
        guild_id: int,
        enabled: bool,
        command_names: Optional[List[str]] = None
    ) -> int:
        """Enable or disable multiple commands"""
        query = {"guild_id": guild_id}
        if command_names:
            query["name"] = {"$in": [n.lower() for n in command_names]}
        
        result = await self.commands.update_many(
            query,
            {"$set": {"enabled": enabled, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count
    
    async def export_commands(self, guild_id: int) -> List[Dict[str, Any]]:
        """Export all commands for backup"""
        cursor = self.commands.find({"guild_id": guild_id})
        return await cursor.to_list(length=None)
    
    async def import_commands(
        self,
        guild_id: int,
        commands_data: List[Dict[str, Any]],
        overwrite: bool = False
    ) -> int:
        """Import commands from backup"""
        imported = 0
        
        for cmd_data in commands_data:
            cmd_data["guild_id"] = guild_id
            cmd_data["created_at"] = datetime.utcnow()
            cmd_data["updated_at"] = datetime.utcnow()
            
            if overwrite:
                await self.commands.update_one(
                    {"guild_id": guild_id, "name": cmd_data["name"]},
                    {"$set": cmd_data},
                    upsert=True
                )
                imported += 1
            else:
                # Only import if doesn't exist
                existing = await self.get_command(guild_id, cmd_data["name"])
                if not existing:
                    await self.commands.insert_one(cmd_data)
                    imported += 1
        
        return imported

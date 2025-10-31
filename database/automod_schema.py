"""
AutoMod System Database Schema
Handles automatic moderation rules, actions, trust scores, and logs.

Collections:
- automod_rules: Moderation rules configuration
- automod_logs: Action logs and violations
- user_trust_scores: User trust and behavior scores
- guild_automod_settings: Guild-specific AutoMod settings
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger('automod_schema')


class AutoModSchema:
    """AutoMod Database Schema Manager"""
    
    def __init__(self, db):
        self.db = db
        self.rules = db.automod_rules
        self.logs = db.automod_logs
        self.trust_scores = db.user_trust_scores
        self.settings = db.guild_automod_settings
    
    async def ensure_indexes(self):
        """Create necessary indexes for performance"""
        try:
            # AutoMod Rules indexes
            await self.rules.create_index([("guild_id", 1), ("enabled", 1)])
            await self.rules.create_index([("guild_id", 1), ("rule_type", 1)])
            
            # AutoMod Logs indexes
            await self.logs.create_index([("guild_id", 1), ("timestamp", -1)])
            await self.logs.create_index([("guild_id", 1), ("user_id", 1)])
            await self.logs.create_index([("guild_id", 1), ("action", 1)])
            await self.logs.create_index([("timestamp", -1)])
            
            # Trust Scores indexes
            await self.trust_scores.create_index([("guild_id", 1), ("user_id", 1)], unique=True)
            await self.trust_scores.create_index([("guild_id", 1), ("score", -1)])
            await self.trust_scores.create_index([("last_updated", 1)])
            
            # Settings indexes
            await self.settings.create_index("guild_id", unique=True)
            
            logger.info("AutoMod indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating AutoMod indexes: {e}")
    
    # ==================== AutoMod Rules ====================
    
    async def create_rule(self, guild_id: int, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new AutoMod rule.
        
        Rule types:
        - spam: Duplicate messages
        - links: URL detection
        - invites: Discord invite links
        - mentions: Mass mentions
        - caps: Excessive caps lock
        - emojis: Emoji spam
        - rate_limit: Message rate limiting
        - blacklist: Blacklisted words/phrases
        
        Actions:
        - delete: Delete message
        - warn: Add warning
        - mute: Timeout user
        - kick: Kick user
        - ban: Ban user
        """
        rule = {
            "guild_id": guild_id,
            "rule_type": rule_data["rule_type"],
            "enabled": rule_data.get("enabled", True),
            "action": rule_data["action"],  # delete, warn, mute, kick, ban
            "duration": rule_data.get("duration", 3600),  # For mute/ban
            "threshold": rule_data.get("threshold"),  # Rule-specific threshold
            "whitelist_roles": rule_data.get("whitelist_roles", []),
            "whitelist_channels": rule_data.get("whitelist_channels", []),
            "custom_message": rule_data.get("custom_message"),
            "log_channel_id": rule_data.get("log_channel_id"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Rule-specific settings
        if rule_data["rule_type"] == "spam":
            rule["duplicate_count"] = rule_data.get("duplicate_count", 3)
            rule["time_window"] = rule_data.get("time_window", 10)  # seconds
        
        elif rule_data["rule_type"] == "links":
            rule["allow_whitelist"] = rule_data.get("allow_whitelist", [])
            rule["block_all_links"] = rule_data.get("block_all_links", False)
        
        elif rule_data["rule_type"] == "mentions":
            rule["max_mentions"] = rule_data.get("max_mentions", 5)
            rule["include_roles"] = rule_data.get("include_roles", True)
        
        elif rule_data["rule_type"] == "caps":
            rule["percentage"] = rule_data.get("percentage", 70)
            rule["min_length"] = rule_data.get("min_length", 10)
        
        elif rule_data["rule_type"] == "emojis":
            rule["max_emojis"] = rule_data.get("max_emojis", 10)
        
        elif rule_data["rule_type"] == "rate_limit":
            rule["messages_count"] = rule_data.get("messages_count", 5)
            rule["time_window"] = rule_data.get("time_window", 5)  # seconds
        
        elif rule_data["rule_type"] == "blacklist":
            rule["words"] = rule_data.get("words", [])
            rule["case_sensitive"] = rule_data.get("case_sensitive", False)
        
        result = await self.rules.insert_one(rule)
        rule["_id"] = result.inserted_id
        return rule
    
    async def get_rule(self, guild_id: int, rule_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific rule"""
        from bson import ObjectId
        return await self.rules.find_one({"_id": ObjectId(rule_id), "guild_id": guild_id})
    
    async def get_guild_rules(self, guild_id: int, enabled_only: bool = False) -> List[Dict[str, Any]]:
        """Get all rules for a guild"""
        query = {"guild_id": guild_id}
        if enabled_only:
            query["enabled"] = True
        
        cursor = self.rules.find(query).sort("created_at", -1)
        return await cursor.to_list(length=None)
    
    async def get_rules_by_type(self, guild_id: int, rule_type: str) -> List[Dict[str, Any]]:
        """Get rules by type"""
        cursor = self.rules.find({
            "guild_id": guild_id,
            "rule_type": rule_type,
            "enabled": True
        })
        return await cursor.to_list(length=None)
    
    async def update_rule(self, guild_id: int, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update a rule"""
        from bson import ObjectId
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.rules.update_one(
            {"_id": ObjectId(rule_id), "guild_id": guild_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def toggle_rule(self, guild_id: int, rule_id: str, enabled: bool) -> bool:
        """Enable/disable a rule"""
        return await self.update_rule(guild_id, rule_id, {"enabled": enabled})
    
    async def delete_rule(self, guild_id: int, rule_id: str) -> bool:
        """Delete a rule"""
        from bson import ObjectId
        result = await self.rules.delete_one({"_id": ObjectId(rule_id), "guild_id": guild_id})
        return result.deleted_count > 0
    
    # ==================== AutoMod Logs ====================
    
    async def log_action(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log an AutoMod action.
        
        Actions:
        - message_deleted
        - user_warned
        - user_muted
        - user_kicked
        - user_banned
        """
        log = {
            "guild_id": log_data["guild_id"],
            "user_id": log_data["user_id"],
            "moderator_id": log_data.get("moderator_id"),  # Bot ID for auto-actions
            "action": log_data["action"],
            "rule_type": log_data["rule_type"],
            "reason": log_data["reason"],
            "message_content": log_data.get("message_content"),
            "channel_id": log_data.get("channel_id"),
            "duration": log_data.get("duration"),
            "timestamp": datetime.utcnow(),
            "metadata": log_data.get("metadata", {})
        }
        
        result = await self.logs.insert_one(log)
        log["_id"] = result.inserted_id
        return log
    
    async def get_user_logs(
        self,
        guild_id: int,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get logs for a specific user"""
        cursor = self.logs.find({
            "guild_id": guild_id,
            "user_id": user_id
        }).sort("timestamp", -1).limit(limit)
        
        return await cursor.to_list(length=None)
    
    async def get_guild_logs(
        self,
        guild_id: int,
        limit: int = 100,
        action: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get logs for a guild"""
        query = {"guild_id": guild_id}
        if action:
            query["action"] = action
        
        cursor = self.logs.find(query).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=None)
    
    async def get_recent_violations(
        self,
        guild_id: int,
        user_id: int,
        minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get recent violations for progressive penalties"""
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        cursor = self.logs.find({
            "guild_id": guild_id,
            "user_id": user_id,
            "timestamp": {"$gte": since}
        }).sort("timestamp", -1)
        
        return await cursor.to_list(length=None)
    
    async def count_user_violations(
        self,
        guild_id: int,
        user_id: int,
        days: int = 7
    ) -> int:
        """Count user violations in last N days"""
        since = datetime.utcnow() - timedelta(days=days)
        
        return await self.logs.count_documents({
            "guild_id": guild_id,
            "user_id": user_id,
            "timestamp": {"$gte": since}
        })
    
    async def get_statistics(self, guild_id: int, days: int = 30) -> Dict[str, Any]:
        """Get AutoMod statistics"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Total actions
        total = await self.logs.count_documents({
            "guild_id": guild_id,
            "timestamp": {"$gte": since}
        })
        
        # Actions by type
        pipeline = [
            {"$match": {"guild_id": guild_id, "timestamp": {"$gte": since}}},
            {"$group": {"_id": "$action", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        actions_by_type = await self.logs.aggregate(pipeline).to_list(length=None)
        
        # Rules triggered
        pipeline = [
            {"$match": {"guild_id": guild_id, "timestamp": {"$gte": since}}},
            {"$group": {"_id": "$rule_type", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        rules_triggered = await self.logs.aggregate(pipeline).to_list(length=None)
        
        # Top violators
        pipeline = [
            {"$match": {"guild_id": guild_id, "timestamp": {"$gte": since}}},
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        top_violators = await self.logs.aggregate(pipeline).to_list(length=None)
        
        return {
            "total_actions": total,
            "actions_by_type": {item["_id"]: item["count"] for item in actions_by_type},
            "rules_triggered": {item["_id"]: item["count"] for item in rules_triggered},
            "top_violators": [{"user_id": item["_id"], "count": item["count"]} for item in top_violators]
        }
    
    # ==================== User Trust Scores ====================
    
    async def get_trust_score(self, guild_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user trust score"""
        return await self.trust_scores.find_one({"guild_id": guild_id, "user_id": user_id})
    
    async def create_trust_score(self, guild_id: int, user_id: int, account_age_days: int) -> Dict[str, Any]:
        """Create initial trust score for a user"""
        # Calculate initial score based on account age
        if account_age_days < 7:
            initial_score = 30  # New account
        elif account_age_days < 30:
            initial_score = 50  # Young account
        elif account_age_days < 180:
            initial_score = 70  # Established account
        else:
            initial_score = 100  # Old account
        
        score_data = {
            "guild_id": guild_id,
            "user_id": user_id,
            "score": initial_score,
            "account_age_days": account_age_days,
            "violations_count": 0,
            "messages_sent": 0,
            "last_violation": None,
            "join_date": datetime.utcnow(),
            "last_updated": datetime.utcnow(),
            "history": []
        }
        
        await self.trust_scores.insert_one(score_data)
        return score_data
    
    async def update_trust_score(
        self,
        guild_id: int,
        user_id: int,
        score_change: int,
        reason: str
    ) -> bool:
        """Update user trust score"""
        score_doc = await self.get_trust_score(guild_id, user_id)
        
        if not score_doc:
            return False
        
        new_score = max(0, min(100, score_doc["score"] + score_change))
        
        await self.trust_scores.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {
                "$set": {
                    "score": new_score,
                    "last_updated": datetime.utcnow()
                },
                "$push": {
                    "history": {
                        "change": score_change,
                        "reason": reason,
                        "timestamp": datetime.utcnow()
                    }
                }
            }
        )
        
        return True
    
    async def increment_violations(self, guild_id: int, user_id: int) -> bool:
        """Increment violation count and decrease trust score"""
        result = await self.trust_scores.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {
                "$inc": {"violations_count": 1, "score": -5},
                "$set": {"last_violation": datetime.utcnow(), "last_updated": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    async def increment_messages(self, guild_id: int, user_id: int) -> bool:
        """Increment message count (for activity tracking)"""
        result = await self.trust_scores.update_one(
            {"guild_id": guild_id, "user_id": user_id},
            {
                "$inc": {"messages_sent": 1},
                "$set": {"last_updated": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    async def get_suspicious_users(self, guild_id: int, threshold: int = 30) -> List[Dict[str, Any]]:
        """Get users with low trust scores"""
        cursor = self.trust_scores.find({
            "guild_id": guild_id,
            "score": {"$lte": threshold}
        }).sort("score", 1).limit(20)
        
        return await cursor.to_list(length=None)
    
    # ==================== Guild Settings ====================
    
    async def get_settings(self, guild_id: int) -> Optional[Dict[str, Any]]:
        """Get guild AutoMod settings"""
        return await self.settings.find_one({"guild_id": guild_id})
    
    async def create_settings(self, guild_id: int) -> Dict[str, Any]:
        """Create default AutoMod settings"""
        settings = {
            "guild_id": guild_id,
            "enabled": False,
            "log_channel_id": None,
            "dm_users": True,
            "progressive_penalties": True,
            "trusted_roles": [],
            "immune_roles": [],
            "ignored_channels": [],
            "raid_protection": {
                "enabled": True,
                "joins_threshold": 5,  # 5 joins
                "time_window": 10,  # in 10 seconds
                "action": "kick"  # kick, ban
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.settings.insert_one(settings)
        return settings
    
    async def update_settings(self, guild_id: int, updates: Dict[str, Any]) -> bool:
        """Update guild settings"""
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.settings.update_one(
            {"guild_id": guild_id},
            {"$set": updates},
            upsert=True
        )
        
        return result.modified_count > 0 or result.upserted_id is not None
    
    async def toggle_automod(self, guild_id: int, enabled: bool) -> bool:
        """Enable/disable AutoMod for guild"""
        return await self.update_settings(guild_id, {"enabled": enabled})


# Export
__all__ = ["AutoModSchema"]

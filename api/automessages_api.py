"""
Auto-Messages API
=================
RESTful API endpoints for Auto-Messages System management.

Endpoints:
- GET    /api/automessages/guilds/{guild_id}/messages - List all messages
- GET    /api/automessages/guilds/{guild_id}/messages/{message_id} - Get message details
- POST   /api/automessages/guilds/{guild_id}/messages - Create message
- PUT    /api/automessages/guilds/{guild_id}/messages/{message_id} - Update message
- DELETE /api/automessages/guilds/{guild_id}/messages/{message_id} - Delete message
- PATCH  /api/automessages/guilds/{guild_id}/messages/{message_id}/toggle - Toggle message
- GET    /api/automessages/guilds/{guild_id}/settings - Get settings
- PUT    /api/automessages/guilds/{guild_id}/settings - Update settings
- GET    /api/automessages/guilds/{guild_id}/stats - Get statistics
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)


class AutoMessagesAPI:
    """Dashboard API for Auto-Messages System"""
    
    def __init__(self, mongo_client):
        """Initialize Auto-Messages API
        
        Args:
            mongo_client: MongoDB client instance
        """
        self.db = mongo_client.kingdom77
        self.messages_collection = self.db.auto_messages
        self.settings_collection = self.db.auto_messages_settings
    
    # ==================== MESSAGES MANAGEMENT ====================
    
    async def list_messages(
        self,
        guild_id: str,
        trigger_type: Optional[str] = None,
        enabled_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all auto-messages for a guild
        
        Args:
            guild_id: Discord guild ID
            trigger_type: Filter by trigger type (keyword/button/dropdown/slash_command)
            enabled_only: Filter enabled messages only
            
        Returns:
            List of message documents
        """
        try:
            query = {"guild_id": guild_id}
            if trigger_type:
                query["trigger_type"] = trigger_type
            if enabled_only:
                query["enabled"] = True
            
            messages = await self.messages_collection.find(query).to_list(length=None)
            
            # Convert ObjectId to string
            for msg in messages:
                msg["_id"] = str(msg["_id"])
            
            return messages
        except Exception as e:
            logger.error(f"Error listing auto-messages: {e}")
            return []
    
    async def get_message(
        self,
        guild_id: str,
        message_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get auto-message details
        
        Args:
            guild_id: Discord guild ID
            message_id: Message ID
            
        Returns:
            Message document or None
        """
        try:
            message = await self.messages_collection.find_one({
                "guild_id": guild_id,
                "message_id": message_id
            })
            
            if message:
                message["_id"] = str(message["_id"])
            
            return message
        except Exception as e:
            logger.error(f"Error getting auto-message: {e}")
            return None
    
    async def create_message(
        self,
        guild_id: str,
        message_data: Dict[str, Any],
        creator_id: str
    ) -> tuple[bool, str, Optional[str]]:
        """Create new auto-message
        
        Args:
            guild_id: Discord guild ID
            message_data: Message configuration
            creator_id: User ID who created the message
            
        Returns:
            (success, message, message_id)
        """
        try:
            # Generate message ID
            import uuid
            message_id = str(uuid.uuid4())[:8]
            
            # Prepare document
            doc = {
                "guild_id": guild_id,
                "message_id": message_id,
                "name": message_data.get("name"),
                "trigger_type": message_data.get("trigger_type"),
                "trigger_value": message_data.get("trigger_value"),
                "response_type": message_data.get("response_type", "text"),
                "response_content": message_data.get("response_content"),
                "embed": message_data.get("embed"),
                "buttons": message_data.get("buttons", []),
                "dropdown": message_data.get("dropdown"),
                "allowed_roles": message_data.get("allowed_roles", []),
                "allowed_channels": message_data.get("allowed_channels", []),
                "enabled": True,
                "created_at": datetime.utcnow(),
                "created_by": creator_id,
                "statistics": {
                    "total_triggers": 0,
                    "last_triggered": None
                }
            }
            
            await self.messages_collection.insert_one(doc)
            
            return True, f"✅ تم إنشاء الرسالة: {message_data.get('name')}", message_id
        except Exception as e:
            logger.error(f"Error creating auto-message: {e}")
            return False, f"❌ فشل إنشاء الرسالة: {str(e)}", None
    
    async def update_message(
        self,
        guild_id: str,
        message_id: str,
        updates: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Update auto-message configuration
        
        Args:
            guild_id: Discord guild ID
            message_id: Message ID
            updates: Fields to update
            
        Returns:
            (success, message)
        """
        try:
            result = await self.messages_collection.update_one(
                {"guild_id": guild_id, "message_id": message_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                return True, "✅ تم تحديث الرسالة بنجاح"
            else:
                return False, "❌ الرسالة غير موجودة"
        except Exception as e:
            logger.error(f"Error updating auto-message: {e}")
            return False, f"❌ فشل التحديث: {str(e)}"
    
    async def delete_message(
        self,
        guild_id: str,
        message_id: str
    ) -> tuple[bool, str]:
        """Delete auto-message
        
        Args:
            guild_id: Discord guild ID
            message_id: Message ID
            
        Returns:
            (success, message)
        """
        try:
            result = await self.messages_collection.delete_one({
                "guild_id": guild_id,
                "message_id": message_id
            })
            
            if result.deleted_count > 0:
                return True, "✅ تم حذف الرسالة"
            else:
                return False, "❌ الرسالة غير موجودة"
        except Exception as e:
            logger.error(f"Error deleting auto-message: {e}")
            return False, f"❌ فشل الحذف: {str(e)}"
    
    async def toggle_message(
        self,
        guild_id: str,
        message_id: str
    ) -> tuple[bool, str, bool]:
        """Toggle message enabled status
        
        Args:
            guild_id: Discord guild ID
            message_id: Message ID
            
        Returns:
            (success, message, new_state)
        """
        try:
            message = await self.get_message(guild_id, message_id)
            if not message:
                return False, "❌ الرسالة غير موجودة", False
            
            new_state = not message.get("enabled", True)
            
            await self.messages_collection.update_one(
                {"guild_id": guild_id, "message_id": message_id},
                {"$set": {"enabled": new_state}}
            )
            
            status = "مفعّلة" if new_state else "معطّلة"
            return True, f"✅ الرسالة الآن {status}", new_state
        except Exception as e:
            logger.error(f"Error toggling auto-message: {e}")
            return False, f"❌ فشل التبديل: {str(e)}", False
    
    # ==================== SETTINGS MANAGEMENT ====================
    
    async def get_settings(
        self,
        guild_id: str
    ) -> Dict[str, Any]:
        """Get auto-messages settings for guild
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            Settings document
        """
        try:
            settings = await self.settings_collection.find_one({
                "guild_id": guild_id
            })
            
            if not settings:
                # Return default settings
                settings = {
                    "guild_id": guild_id,
                    "cooldown_seconds": 5,
                    "auto_delete_seconds": 0,
                    "dm_response": False,
                    "case_sensitive": False,
                    "exact_match": False
                }
            else:
                settings["_id"] = str(settings["_id"])
            
            return settings
        except Exception as e:
            logger.error(f"Error getting settings: {e}")
            return {}
    
    async def update_settings(
        self,
        guild_id: str,
        settings: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Update auto-messages settings
        
        Args:
            guild_id: Discord guild ID
            settings: Settings to update
            
        Returns:
            (success, message)
        """
        try:
            await self.settings_collection.update_one(
                {"guild_id": guild_id},
                {"$set": settings},
                upsert=True
            )
            
            return True, "✅ تم تحديث الإعدادات بنجاح"
        except Exception as e:
            logger.error(f"Error updating settings: {e}")
            return False, f"❌ فشل تحديث الإعدادات: {str(e)}"
    
    # ==================== STATISTICS ====================
    
    async def get_statistics(
        self,
        guild_id: str
    ) -> Dict[str, Any]:
        """Get auto-messages statistics for guild
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            Statistics dictionary
        """
        try:
            # Count messages by type
            total_messages = await self.messages_collection.count_documents({
                "guild_id": guild_id
            })
            
            active_messages = await self.messages_collection.count_documents({
                "guild_id": guild_id,
                "enabled": True
            })
            
            # Count by trigger type
            keyword_count = await self.messages_collection.count_documents({
                "guild_id": guild_id,
                "trigger_type": "keyword"
            })
            
            button_count = await self.messages_collection.count_documents({
                "guild_id": guild_id,
                "trigger_type": "button"
            })
            
            dropdown_count = await self.messages_collection.count_documents({
                "guild_id": guild_id,
                "trigger_type": "dropdown"
            })
            
            # Get total triggers
            pipeline = [
                {"$match": {"guild_id": guild_id}},
                {"$group": {
                    "_id": None,
                    "total_triggers": {"$sum": "$statistics.total_triggers"}
                }}
            ]
            
            result = await self.messages_collection.aggregate(pipeline).to_list(1)
            total_triggers = result[0]["total_triggers"] if result else 0
            
            # Get top 5 most triggered messages
            top_messages = await self.messages_collection.find({
                "guild_id": guild_id
            }).sort("statistics.total_triggers", -1).limit(5).to_list(5)
            
            top_messages_list = []
            for msg in top_messages:
                top_messages_list.append({
                    "message_id": msg["message_id"],
                    "name": msg["name"],
                    "triggers": msg["statistics"]["total_triggers"]
                })
            
            return {
                "guild_id": guild_id,
                "messages": {
                    "total": total_messages,
                    "active": active_messages,
                    "inactive": total_messages - active_messages
                },
                "by_trigger_type": {
                    "keyword": keyword_count,
                    "button": button_count,
                    "dropdown": dropdown_count
                },
                "total_triggers": total_triggers,
                "top_messages": top_messages_list
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "guild_id": guild_id,
                "error": str(e)
            }

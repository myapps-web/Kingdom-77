"""
Kingdom-77 Bot - Advanced Logging System Schema
نظام سجلات شامل لتتبع جميع أحداث السيرفر
مثل Nova Bot - يتتبع كل شيء!

Collections:
- server_logs_settings: إعدادات السجلات لكل سيرفر
- message_logs: سجلات الرسائل (edit/delete)
- member_logs: سجلات الأعضاء (join/leave/update)
- channel_logs: سجلات القنوات (create/delete/update)
- role_logs: سجلات الرتب (create/delete/update/assign)
- voice_logs: سجلات الصوت (join/leave/move)
- server_change_logs: سجلات تغييرات السيرفر
- message_cache: كاش الرسائل لحفظ المحذوفة
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import discord


class LoggingSchema:
    """Schema for Advanced Logging System"""
    
    def __init__(self, db):
        self.db = db
        self.settings = db.server_logs_settings
        self.message_logs = db.message_logs
        self.member_logs = db.member_logs
        self.channel_logs = db.channel_logs
        self.role_logs = db.role_logs
        self.voice_logs = db.voice_logs
        self.server_logs = db.server_change_logs
        self.message_cache = db.message_cache
    
    async def create_indexes(self):
        """إنشاء الـ indexes للأداء الأفضل"""
        # Settings indexes
        await self.settings.create_index("guild_id", unique=True)
        
        # Message logs indexes
        await self.message_logs.create_index([("guild_id", 1), ("timestamp", -1)])
        await self.message_logs.create_index([("guild_id", 1), ("user_id", 1)])
        await self.message_logs.create_index([("guild_id", 1), ("channel_id", 1)])
        await self.message_logs.create_index([("guild_id", 1), ("log_type", 1)])
        
        # Member logs indexes
        await self.member_logs.create_index([("guild_id", 1), ("timestamp", -1)])
        await self.member_logs.create_index([("guild_id", 1), ("user_id", 1)])
        await self.member_logs.create_index([("guild_id", 1), ("log_type", 1)])
        
        # Channel logs indexes
        await self.channel_logs.create_index([("guild_id", 1), ("timestamp", -1)])
        await self.channel_logs.create_index([("guild_id", 1), ("channel_id", 1)])
        
        # Role logs indexes
        await self.role_logs.create_index([("guild_id", 1), ("timestamp", -1)])
        await self.role_logs.create_index([("guild_id", 1), ("role_id", 1)])
        
        # Voice logs indexes
        await self.voice_logs.create_index([("guild_id", 1), ("timestamp", -1)])
        await self.voice_logs.create_index([("guild_id", 1), ("user_id", 1)])
        
        # Server logs indexes
        await self.server_logs.create_index([("guild_id", 1), ("timestamp", -1)])
        
        # Message cache indexes
        await self.message_cache.create_index([("message_id", 1)], unique=True)
        await self.message_cache.create_index([("timestamp", 1)], expireAfterSeconds=86400)  # 24 ساعة
    
    # ==================== Server Logs Settings ====================
    
    async def get_server_settings(self, guild_id: int) -> Optional[Dict]:
        """الحصول على إعدادات السجلات للسيرفر"""
        return await self.settings.find_one({"guild_id": guild_id})
    
    async def create_default_settings(self, guild_id: int) -> Dict:
        """إنشاء إعدادات افتراضية"""
        settings = {
            "guild_id": guild_id,
            "enabled": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            
            # قنوات السجلات (منفصلة لكل نوع)
            "channels": {
                "message_logs": None,      # قناة سجلات الرسائل
                "member_logs": None,       # قناة سجلات الأعضاء
                "channel_logs": None,      # قناة سجلات القنوات
                "role_logs": None,         # قناة سجلات الرتب
                "voice_logs": None,        # قناة سجلات الصوت
                "server_logs": None,       # قناة سجلات السيرفر
                "moderation_logs": None,   # قناة سجلات المراقبة
                "automod_logs": None       # قناة سجلات AutoMod
            },
            
            # تفعيل/تعطيل كل نوع
            "log_types": {
                "message_edit": True,
                "message_delete": True,
                "member_join": True,
                "member_leave": True,
                "member_update": True,
                "member_ban": True,
                "member_unban": True,
                "channel_create": True,
                "channel_delete": True,
                "channel_update": True,
                "role_create": True,
                "role_delete": True,
                "role_update": True,
                "role_given": True,
                "role_removed": True,
                "voice_join": True,
                "voice_leave": True,
                "voice_move": True,
                "voice_mute": True,
                "voice_deafen": True,
                "server_update": True,
                "emoji_create": True,
                "emoji_delete": True,
                "sticker_create": True,
                "sticker_delete": True
            },
            
            # قنوات/رتب مستثناة من السجلات
            "ignored_channels": [],
            "ignored_roles": [],
            "ignored_users": [],
            
            # إعدادات متقدمة
            "settings": {
                "cache_messages": True,           # حفظ الرسائل في الكاش
                "cache_duration": 24,             # مدة الحفظ بالساعات
                "log_bots": False,                # تسجيل أفعال البوتات
                "use_webhooks": True,             # استخدام Webhooks للسجلات
                "compact_mode": False,            # وضع مضغوط للـ Embeds
                "show_attachments": True,         # عرض المرفقات
                "log_invites": True,              # تسجيل الروابط
                "max_logs_per_day": 10000        # حد أقصى للسجلات يومياً
            },
            
            # إحصائيات
            "stats": {
                "total_logs": 0,
                "logs_today": 0,
                "last_log": None,
                "most_active_user": None,
                "most_active_channel": None
            }
        }
        
        await self.settings.insert_one(settings)
        return settings
    
    async def update_server_settings(self, guild_id: int, updates: Dict) -> bool:
        """تحديث إعدادات السيرفر"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.settings.update_one(
            {"guild_id": guild_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def set_log_channel(self, guild_id: int, log_type: str, channel_id: Optional[int]) -> bool:
        """تحديد قناة لنوع معين من السجلات"""
        return await self.update_server_settings(
            guild_id,
            {f"channels.{log_type}": channel_id}
        )
    
    async def toggle_log_type(self, guild_id: int, log_type: str, enabled: bool) -> bool:
        """تفعيل/تعطيل نوع معين من السجلات"""
        return await self.update_server_settings(
            guild_id,
            {f"log_types.{log_type}": enabled}
        )
    
    # ==================== Message Logs ====================
    
    async def log_message_edit(
        self,
        guild_id: int,
        message_id: int,
        channel_id: int,
        user_id: int,
        before_content: str,
        after_content: str,
        before_embeds: List[Dict],
        after_embeds: List[Dict]
    ) -> str:
        """تسجيل تعديل رسالة"""
        log = {
            "guild_id": guild_id,
            "log_type": "message_edit",
            "message_id": message_id,
            "channel_id": channel_id,
            "user_id": user_id,
            "before": {
                "content": before_content,
                "embeds": before_embeds,
                "length": len(before_content)
            },
            "after": {
                "content": after_content,
                "embeds": after_embeds,
                "length": len(after_content)
            },
            "timestamp": datetime.utcnow()
        }
        
        result = await self.message_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_message_delete(
        self,
        guild_id: int,
        message_id: int,
        channel_id: int,
        user_id: int,
        content: str,
        embeds: List[Dict],
        attachments: List[Dict],
        deleted_by: Optional[int] = None
    ) -> str:
        """تسجيل حذف رسالة"""
        log = {
            "guild_id": guild_id,
            "log_type": "message_delete",
            "message_id": message_id,
            "channel_id": channel_id,
            "user_id": user_id,
            "deleted_by": deleted_by,  # من حذف الرسالة (admin/mod)
            "content": content,
            "embeds": embeds,
            "attachments": attachments,
            "length": len(content),
            "timestamp": datetime.utcnow()
        }
        
        result = await self.message_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_bulk_delete(
        self,
        guild_id: int,
        channel_id: int,
        messages_count: int,
        deleted_by: int,
        messages_data: List[Dict]
    ) -> str:
        """تسجيل حذف جماعي للرسائل"""
        log = {
            "guild_id": guild_id,
            "log_type": "bulk_delete",
            "channel_id": channel_id,
            "deleted_by": deleted_by,
            "count": messages_count,
            "messages": messages_data,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.message_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    # ==================== Member Logs ====================
    
    async def log_member_join(
        self,
        guild_id: int,
        user_id: int,
        username: str,
        discriminator: str,
        avatar_url: str,
        account_age_days: int,
        is_bot: bool
    ) -> str:
        """تسجيل انضمام عضو"""
        log = {
            "guild_id": guild_id,
            "log_type": "member_join",
            "user_id": user_id,
            "username": username,
            "discriminator": discriminator,
            "avatar_url": avatar_url,
            "account_age_days": account_age_days,
            "is_bot": is_bot,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.member_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_member_leave(
        self,
        guild_id: int,
        user_id: int,
        username: str,
        roles: List[int],
        joined_at: datetime,
        reason: Optional[str] = None
    ) -> str:
        """تسجيل مغادرة عضو"""
        duration_days = (datetime.utcnow() - joined_at).days if joined_at else 0
        
        log = {
            "guild_id": guild_id,
            "log_type": "member_leave",
            "user_id": user_id,
            "username": username,
            "roles": roles,
            "joined_at": joined_at,
            "duration_days": duration_days,
            "reason": reason,  # kick, ban, or None
            "timestamp": datetime.utcnow()
        }
        
        result = await self.member_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_member_update(
        self,
        guild_id: int,
        user_id: int,
        update_type: str,  # nickname, roles, avatar, etc
        before: Any,
        after: Any
    ) -> str:
        """تسجيل تحديث معلومات عضو"""
        log = {
            "guild_id": guild_id,
            "log_type": "member_update",
            "user_id": user_id,
            "update_type": update_type,
            "before": before,
            "after": after,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.member_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_member_ban(
        self,
        guild_id: int,
        user_id: int,
        username: str,
        banned_by: int,
        reason: Optional[str]
    ) -> str:
        """تسجيل حظر عضو"""
        log = {
            "guild_id": guild_id,
            "log_type": "member_ban",
            "user_id": user_id,
            "username": username,
            "banned_by": banned_by,
            "reason": reason,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.member_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_member_unban(
        self,
        guild_id: int,
        user_id: int,
        username: str,
        unbanned_by: int,
        reason: Optional[str]
    ) -> str:
        """تسجيل إلغاء حظر عضو"""
        log = {
            "guild_id": guild_id,
            "log_type": "member_unban",
            "user_id": user_id,
            "username": username,
            "unbanned_by": unbanned_by,
            "reason": reason,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.member_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    # ==================== Channel Logs ====================
    
    async def log_channel_create(
        self,
        guild_id: int,
        channel_id: int,
        channel_name: str,
        channel_type: str,
        created_by: int,
        category: Optional[int] = None
    ) -> str:
        """تسجيل إنشاء قناة"""
        log = {
            "guild_id": guild_id,
            "log_type": "channel_create",
            "channel_id": channel_id,
            "channel_name": channel_name,
            "channel_type": channel_type,
            "category": category,
            "created_by": created_by,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.channel_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_channel_delete(
        self,
        guild_id: int,
        channel_id: int,
        channel_name: str,
        channel_type: str,
        deleted_by: int
    ) -> str:
        """تسجيل حذف قناة"""
        log = {
            "guild_id": guild_id,
            "log_type": "channel_delete",
            "channel_id": channel_id,
            "channel_name": channel_name,
            "channel_type": channel_type,
            "deleted_by": deleted_by,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.channel_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_channel_update(
        self,
        guild_id: int,
        channel_id: int,
        update_type: str,
        before: Any,
        after: Any,
        updated_by: Optional[int] = None
    ) -> str:
        """تسجيل تحديث قناة"""
        log = {
            "guild_id": guild_id,
            "log_type": "channel_update",
            "channel_id": channel_id,
            "update_type": update_type,
            "before": before,
            "after": after,
            "updated_by": updated_by,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.channel_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    # ==================== Role Logs ====================
    
    async def log_role_create(
        self,
        guild_id: int,
        role_id: int,
        role_name: str,
        color: int,
        permissions: int,
        created_by: int
    ) -> str:
        """تسجيل إنشاء رتبة"""
        log = {
            "guild_id": guild_id,
            "log_type": "role_create",
            "role_id": role_id,
            "role_name": role_name,
            "color": color,
            "permissions": permissions,
            "created_by": created_by,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.role_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_role_delete(
        self,
        guild_id: int,
        role_id: int,
        role_name: str,
        deleted_by: int
    ) -> str:
        """تسجيل حذف رتبة"""
        log = {
            "guild_id": guild_id,
            "log_type": "role_delete",
            "role_id": role_id,
            "role_name": role_name,
            "deleted_by": deleted_by,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.role_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_role_update(
        self,
        guild_id: int,
        role_id: int,
        update_type: str,
        before: Any,
        after: Any,
        updated_by: Optional[int] = None
    ) -> str:
        """تسجيل تحديث رتبة"""
        log = {
            "guild_id": guild_id,
            "log_type": "role_update",
            "role_id": role_id,
            "update_type": update_type,
            "before": before,
            "after": after,
            "updated_by": updated_by,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.role_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_role_given(
        self,
        guild_id: int,
        user_id: int,
        role_id: int,
        role_name: str,
        given_by: Optional[int] = None
    ) -> str:
        """تسجيل منح رتبة لعضو"""
        log = {
            "guild_id": guild_id,
            "log_type": "role_given",
            "user_id": user_id,
            "role_id": role_id,
            "role_name": role_name,
            "given_by": given_by,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.role_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_role_removed(
        self,
        guild_id: int,
        user_id: int,
        role_id: int,
        role_name: str,
        removed_by: Optional[int] = None
    ) -> str:
        """تسجيل إزالة رتبة من عضو"""
        log = {
            "guild_id": guild_id,
            "log_type": "role_removed",
            "user_id": user_id,
            "role_id": role_id,
            "role_name": role_name,
            "removed_by": removed_by,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.role_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    # ==================== Voice Logs ====================
    
    async def log_voice_join(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        channel_name: str
    ) -> str:
        """تسجيل دخول عضو لقناة صوتية"""
        log = {
            "guild_id": guild_id,
            "log_type": "voice_join",
            "user_id": user_id,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.voice_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_voice_leave(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        channel_name: str,
        duration_seconds: int
    ) -> str:
        """تسجيل خروج عضو من قناة صوتية"""
        log = {
            "guild_id": guild_id,
            "log_type": "voice_leave",
            "user_id": user_id,
            "channel_id": channel_id,
            "channel_name": channel_name,
            "duration_seconds": duration_seconds,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.voice_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    async def log_voice_move(
        self,
        guild_id: int,
        user_id: int,
        before_channel_id: int,
        after_channel_id: int,
        before_channel_name: str,
        after_channel_name: str
    ) -> str:
        """تسجيل انتقال عضو بين قنوات صوتية"""
        log = {
            "guild_id": guild_id,
            "log_type": "voice_move",
            "user_id": user_id,
            "before_channel": {
                "id": before_channel_id,
                "name": before_channel_name
            },
            "after_channel": {
                "id": after_channel_id,
                "name": after_channel_name
            },
            "timestamp": datetime.utcnow()
        }
        
        result = await self.voice_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    # ==================== Server Logs ====================
    
    async def log_server_update(
        self,
        guild_id: int,
        update_type: str,
        before: Any,
        after: Any,
        updated_by: Optional[int] = None
    ) -> str:
        """تسجيل تحديث إعدادات السيرفر"""
        log = {
            "guild_id": guild_id,
            "log_type": "server_update",
            "update_type": update_type,
            "before": before,
            "after": after,
            "updated_by": updated_by,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.server_logs.insert_one(log)
        await self._increment_log_count(guild_id)
        return str(result.inserted_id)
    
    # ==================== Message Cache ====================
    
    async def cache_message(
        self,
        message: discord.Message
    ) -> bool:
        """حفظ رسالة في الكاش"""
        try:
            cached = {
                "message_id": message.id,
                "guild_id": message.guild.id if message.guild else None,
                "channel_id": message.channel.id,
                "user_id": message.author.id,
                "content": message.content,
                "embeds": [e.to_dict() for e in message.embeds],
                "attachments": [
                    {
                        "filename": a.filename,
                        "url": a.url,
                        "size": a.size
                    } for a in message.attachments
                ],
                "timestamp": datetime.utcnow()
            }
            
            await self.message_cache.update_one(
                {"message_id": message.id},
                {"$set": cached},
                upsert=True
            )
            return True
        except Exception:
            return False
    
    async def get_cached_message(self, message_id: int) -> Optional[Dict]:
        """الحصول على رسالة من الكاش"""
        return await self.message_cache.find_one({"message_id": message_id})
    
    # ==================== Query & Search ====================
    
    async def get_logs(
        self,
        guild_id: int,
        log_category: str,  # message, member, channel, role, voice, server
        log_type: Optional[str] = None,
        user_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """البحث في السجلات مع فلاتر متقدمة"""
        # اختيار Collection حسب النوع
        collection_map = {
            "message": self.message_logs,
            "member": self.member_logs,
            "channel": self.channel_logs,
            "role": self.role_logs,
            "voice": self.voice_logs,
            "server": self.server_logs
        }
        
        collection = collection_map.get(log_category)
        if not collection:
            return []
        
        # بناء الفلاتر
        filters = {"guild_id": guild_id}
        
        if log_type:
            filters["log_type"] = log_type
        
        if user_id:
            filters["user_id"] = user_id
        
        if channel_id:
            filters["channel_id"] = channel_id
        
        if start_date or end_date:
            filters["timestamp"] = {}
            if start_date:
                filters["timestamp"]["$gte"] = start_date
            if end_date:
                filters["timestamp"]["$lte"] = end_date
        
        # البحث
        cursor = collection.find(filters).sort("timestamp", -1).skip(offset).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def search_logs(
        self,
        guild_id: int,
        query: str,
        search_in: str = "all"  # all, message, member, channel, role
    ) -> List[Dict]:
        """البحث النصي في السجلات"""
        results = []
        
        # البحث في سجلات الرسائل
        if search_in in ["all", "message"]:
            message_results = await self.message_logs.find({
                "guild_id": guild_id,
                "$or": [
                    {"content": {"$regex": query, "$options": "i"}},
                    {"before.content": {"$regex": query, "$options": "i"}},
                    {"after.content": {"$regex": query, "$options": "i"}}
                ]
            }).limit(50).to_list(length=50)
            results.extend(message_results)
        
        # البحث في سجلات الأعضاء
        if search_in in ["all", "member"]:
            member_results = await self.member_logs.find({
                "guild_id": guild_id,
                "username": {"$regex": query, "$options": "i"}
            }).limit(50).to_list(length=50)
            results.extend(member_results)
        
        return results
    
    async def get_user_history(
        self,
        guild_id: int,
        user_id: int,
        limit: int = 100
    ) -> Dict[str, List]:
        """الحصول على تاريخ عضو كامل"""
        history = {
            "messages": [],
            "member_events": [],
            "roles": [],
            "voice": []
        }
        
        # سجلات الرسائل
        history["messages"] = await self.message_logs.find({
            "guild_id": guild_id,
            "user_id": user_id
        }).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # سجلات الأعضاء
        history["member_events"] = await self.member_logs.find({
            "guild_id": guild_id,
            "user_id": user_id
        }).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # سجلات الرتب
        history["roles"] = await self.role_logs.find({
            "guild_id": guild_id,
            "user_id": user_id
        }).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        # سجلات الصوت
        history["voice"] = await self.voice_logs.find({
            "guild_id": guild_id,
            "user_id": user_id
        }).sort("timestamp", -1).limit(limit).to_list(length=limit)
        
        return history
    
    # ==================== Statistics ====================
    
    async def get_stats(self, guild_id: int, days: int = 7) -> Dict:
        """إحصائيات السجلات"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        stats = {
            "total_logs": 0,
            "by_type": {},
            "most_active_users": [],
            "most_active_channels": [],
            "daily_breakdown": []
        }
        
        # عد السجلات حسب النوع
        for collection_name, collection in [
            ("message", self.message_logs),
            ("member", self.member_logs),
            ("channel", self.channel_logs),
            ("role", self.role_logs),
            ("voice", self.voice_logs),
            ("server", self.server_logs)
        ]:
            count = await collection.count_documents({
                "guild_id": guild_id,
                "timestamp": {"$gte": start_date}
            })
            stats["by_type"][collection_name] = count
            stats["total_logs"] += count
        
        # أكثر الأعضاء نشاطاً
        pipeline = [
            {"$match": {"guild_id": guild_id, "timestamp": {"$gte": start_date}}},
            {"$group": {"_id": "$user_id", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        stats["most_active_users"] = await self.message_logs.aggregate(pipeline).to_list(length=10)
        
        return stats
    
    # ==================== Utility ====================
    
    async def _increment_log_count(self, guild_id: int):
        """زيادة عداد السجلات"""
        await self.settings.update_one(
            {"guild_id": guild_id},
            {
                "$inc": {
                    "stats.total_logs": 1,
                    "stats.logs_today": 1
                },
                "$set": {
                    "stats.last_log": datetime.utcnow()
                }
            }
        )
    
    async def cleanup_old_logs(self, guild_id: int, days: int = 30):
        """حذف السجلات القديمة"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = 0
        for collection in [
            self.message_logs,
            self.member_logs,
            self.channel_logs,
            self.role_logs,
            self.voice_logs,
            self.server_logs
        ]:
            result = await collection.delete_many({
                "guild_id": guild_id,
                "timestamp": {"$lt": cutoff_date}
            })
            deleted += result.deleted_count
        
        return deleted

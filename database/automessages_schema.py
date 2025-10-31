"""
🤖 Auto-Messages System Database Schema
Kingdom-77 Bot v3.9 - Phase 5.7

نظام الرسائل التلقائية (مثل Nova Bot)
يدعم:
- Keywords triggers
- Button triggers
- Dropdown menu triggers
- Embed builder
- Multiple messages per trigger
"""

from datetime import datetime, timezone
from typing import Optional, Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase


# ===== Auto Messages Schema =====
AUTO_MESSAGES_SCHEMA = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["message_id", "guild_id", "trigger_type", "created_at"],
            "properties": {
                "message_id": {
                    "bsonType": "string",
                    "description": "معرف فريد للرسالة"
                },
                "guild_id": {
                    "bsonType": "string",
                    "description": "معرف السيرفر"
                },
                "name": {
                    "bsonType": "string",
                    "description": "اسم الرسالة",
                    "maxLength": 100
                },
                "trigger_type": {
                    "bsonType": "string",
                    "enum": ["keyword", "button", "dropdown", "slash_command"],
                    "description": "نوع المُطلق"
                },
                "trigger_value": {
                    "bsonType": ["string", "array"],
                    "description": "قيمة المُطلق (كلمة مفتاحية أو custom_id)"
                },
                "response": {
                    "bsonType": "object",
                    "description": "محتوى الرد",
                    "properties": {
                        "content": {
                            "bsonType": ["string", "null"],
                            "description": "نص الرسالة"
                        },
                        "embed": {
                            "bsonType": ["object", "null"],
                            "description": "Embed object",
                            "properties": {
                                "title": {"bsonType": "string"},
                                "description": {"bsonType": "string"},
                                "color": {"bsonType": "string"},
                                "thumbnail": {"bsonType": "string"},
                                "image": {"bsonType": "string"},
                                "footer": {"bsonType": "string"},
                                "fields": {"bsonType": "array"}
                            }
                        },
                        "buttons": {
                            "bsonType": "array",
                            "description": "أزرار الرسالة",
                            "items": {
                                "bsonType": "object",
                                "properties": {
                                    "label": {"bsonType": "string"},
                                    "style": {"bsonType": "string"},
                                    "custom_id": {"bsonType": "string"},
                                    "url": {"bsonType": ["string", "null"]},
                                    "emoji": {"bsonType": ["string", "null"]}
                                }
                            }
                        },
                        "dropdown": {
                            "bsonType": ["object", "null"],
                            "description": "قائمة منسدلة",
                            "properties": {
                                "placeholder": {"bsonType": "string"},
                                "options": {
                                    "bsonType": "array",
                                    "items": {
                                        "bsonType": "object",
                                        "properties": {
                                            "label": {"bsonType": "string"},
                                            "value": {"bsonType": "string"},
                                            "description": {"bsonType": "string"},
                                            "emoji": {"bsonType": ["string", "null"]}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "channel_id": {
                    "bsonType": ["string", "null"],
                    "description": "قناة محددة للرد (null = any channel)"
                },
                "allowed_roles": {
                    "bsonType": "array",
                    "description": "رتب مسموح لها باستخدام الرسالة (empty = all)",
                    "items": {"bsonType": "string"}
                },
                "cooldown_seconds": {
                    "bsonType": "int",
                    "description": "فترة انتظار بين الاستخدامات",
                    "minimum": 0
                },
                "delete_after_seconds": {
                    "bsonType": ["int", "null"],
                    "description": "حذف الرسالة بعد X ثانية",
                    "minimum": 1
                },
                "case_sensitive": {
                    "bsonType": "bool",
                    "description": "حساسية الأحرف للكلمات المفتاحية"
                },
                "exact_match": {
                    "bsonType": "bool",
                    "description": "مطابقة دقيقة للكلمات المفتاحية"
                },
                "is_active": {
                    "bsonType": "bool",
                    "description": "هل الرسالة نشطة"
                },
                "usage_count": {
                    "bsonType": "int",
                    "description": "عدد مرات الاستخدام"
                },
                "created_by": {
                    "bsonType": "string",
                    "description": "معرف المُنشئ"
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "تاريخ الإنشاء"
                },
                "updated_at": {
                    "bsonType": "date",
                    "description": "تاريخ آخر تحديث"
                }
            }
        }
    }
}


# ===== Auto Messages Settings Schema =====
AUTO_MESSAGES_SETTINGS_SCHEMA = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["guild_id"],
            "properties": {
                "guild_id": {
                    "bsonType": "string",
                    "description": "معرف السيرفر"
                },
                "enabled": {
                    "bsonType": "bool",
                    "description": "هل النظام مفعل"
                },
                "ignore_bots": {
                    "bsonType": "bool",
                    "description": "تجاهل رسائل البوتات"
                },
                "ignore_channels": {
                    "bsonType": "array",
                    "description": "قنوات مستثناة",
                    "items": {"bsonType": "string"}
                },
                "stats": {
                    "bsonType": "object",
                    "properties": {
                        "total_messages": {"bsonType": "int"},
                        "total_triggers": {"bsonType": "int"}
                    }
                }
            }
        }
    }
}


class AutoMessagesDatabase:
    """إدارة قاعدة بيانات الرسائل التلقائية"""
    
    def __init__(self, db):
        self.db = db
        self.messages = db.auto_messages
        self.settings = db.auto_messages_settings
    
    async def setup_indexes(self):
        """إنشاء indexes"""
        await self.messages.create_index("message_id", unique=True)
        await self.messages.create_index("guild_id")
        await self.messages.create_index([("guild_id", 1), ("trigger_type", 1)])
        await self.messages.create_index([("guild_id", 1), ("is_active", 1)])
        await self.settings.create_index("guild_id", unique=True)
    
    async def create_message(self, message_data: Dict) -> Dict:
        """إنشاء رسالة تلقائية جديدة"""
        await self.messages.insert_one(message_data)
        return message_data
    
    async def get_message(self, message_id: str) -> Optional[Dict]:
        """جلب رسالة"""
        return await self.messages.find_one({"message_id": message_id})
    
    async def get_guild_messages(
        self,
        guild_id: str,
        trigger_type: Optional[str] = None,
        active_only: bool = True
    ) -> List[Dict]:
        """جلب رسائل السيرفر"""
        query = {"guild_id": guild_id}
        if trigger_type:
            query["trigger_type"] = trigger_type
        if active_only:
            query["is_active"] = True
        
        cursor = self.messages.find(query)
        return await cursor.to_list(length=100)
    
    async def update_message(self, message_id: str, updates: Dict) -> bool:
        """تحديث رسالة"""
        updates["updated_at"] = datetime.now(timezone.utc)
        result = await self.messages.update_one(
            {"message_id": message_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_message(self, message_id: str) -> bool:
        """حذف رسالة"""
        result = await self.messages.delete_one({"message_id": message_id})
        return result.deleted_count > 0
    
    async def increment_usage(self, message_id: str):
        """زيادة عداد الاستخدام"""
        await self.messages.update_one(
            {"message_id": message_id},
            {"$inc": {"usage_count": 1}}
        )
    
    async def get_settings(self, guild_id: str) -> Optional[Dict]:
        """جلب إعدادات السيرفر"""
        return await self.settings.find_one({"guild_id": guild_id})
    
    async def create_settings(self, guild_id: str) -> Dict:
        """إنشاء إعدادات جديدة"""
        settings_doc = {
            "guild_id": guild_id,
            "enabled": True,
            "ignore_bots": True,
            "ignore_channels": [],
            "stats": {
                "total_messages": 0,
                "total_triggers": 0
            }
        }
        await self.settings.insert_one(settings_doc)
        return settings_doc
    
    async def update_settings(self, guild_id: str, updates: Dict) -> bool:
        """تحديث الإعدادات"""
        result = await self.settings.update_one(
            {"guild_id": guild_id},
            {"$set": updates}
        )
        return result.modified_count > 0


async def init_automessages_schema(db: AsyncIOMotorDatabase):
    """تهيئة schema"""
    try:
        await db.create_collection("auto_messages", **AUTO_MESSAGES_SCHEMA)
    except Exception:
        pass
    
    try:
        await db.create_collection("auto_messages_settings", **AUTO_MESSAGES_SETTINGS_SCHEMA)
    except Exception:
        pass
    
    auto_db = AutoMessagesDatabase(db)
    await auto_db.setup_indexes()
    return auto_db

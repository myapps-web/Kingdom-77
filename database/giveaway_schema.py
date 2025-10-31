"""
🎁 Giveaway System Database Schema
Kingdom-77 Bot v4.0 - Phase 5.7

نظام القرعة الشامل مع نظام Entities (النقاط)
يدعم:
- قرعات متعددة مع تخصيص كامل
- نظام Entities لزيادة حظ الفوز حسب الرتب
- وضعين لحساب النقاط: إجمالي أو أعلى رتبة
- Requirements متعددة (roles, level, credits, etc.)
- Winners management & history
"""

from datetime import datetime, timezone
from typing import Optional, Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase


# ===== Giveaways Schema =====
GIVEAWAYS_SCHEMA = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["giveaway_id", "guild_id", "prize", "host_id", "created_at"],
            "properties": {
                "giveaway_id": {
                    "bsonType": "string",
                    "description": "معرف فريد للقرعة"
                },
                "guild_id": {
                    "bsonType": "string",
                    "description": "معرف السيرفر"
                },
                "channel_id": {
                    "bsonType": "string",
                    "description": "قناة القرعة"
                },
                "message_id": {
                    "bsonType": ["string", "null"],
                    "description": "معرف رسالة القرعة"
                },
                "prize": {
                    "bsonType": "string",
                    "description": "الجائزة",
                    "maxLength": 256
                },
                "description": {
                    "bsonType": ["string", "null"],
                    "description": "وصف القرعة",
                    "maxLength": 1000
                },
                "thumbnail_url": {
                    "bsonType": ["string", "null"],
                    "description": "صورة مصغرة"
                },
                "image_url": {
                    "bsonType": ["string", "null"],
                    "description": "صورة كبيرة"
                },
                "color": {
                    "bsonType": "string",
                    "description": "لون Embed",
                    "pattern": "^#[0-9A-Fa-f]{6}$"
                },
                "host_id": {
                    "bsonType": "string",
                    "description": "معرف المنظّم"
                },
                "winners_count": {
                    "bsonType": "int",
                    "description": "عدد الفائزين",
                    "minimum": 1,
                    "maximum": 50
                },
                "duration_seconds": {
                    "bsonType": "int",
                    "description": "مدة القرعة بالثواني",
                    "minimum": 60
                },
                "end_time": {
                    "bsonType": "date",
                    "description": "وقت انتهاء القرعة"
                },
                "status": {
                    "bsonType": "string",
                    "enum": ["active", "ended", "cancelled", "rerolling"],
                    "description": "حالة القرعة"
                },
                
                # ===== نظام Entities (النقاط) =====
                "entities_enabled": {
                    "bsonType": "bool",
                    "description": "هل نظام Entities مفعّل"
                },
                "entities_mode": {
                    "bsonType": "string",
                    "enum": ["cumulative", "highest"],
                    "description": "وضع حساب Entities: cumulative (إجمالي) أو highest (أعلى رتبة)"
                },
                "role_entities": {
                    "bsonType": "array",
                    "description": "قائمة الرتب مع نقاطها",
                    "items": {
                        "bsonType": "object",
                        "required": ["role_id", "points"],
                        "properties": {
                            "role_id": {
                                "bsonType": "string",
                                "description": "معرف الرتبة"
                            },
                            "points": {
                                "bsonType": "int",
                                "description": "عدد النقاط (1 point = 1% زيادة في الحظ)",
                                "minimum": 1,
                                "maximum": 100
                            }
                        }
                    }
                },
                
                # ===== Requirements =====
                "requirements": {
                    "bsonType": "object",
                    "description": "شروط الدخول",
                    "properties": {
                        "required_roles": {
                            "bsonType": "array",
                            "description": "رتب مطلوبة (ANY)",
                            "items": {"bsonType": "string"}
                        },
                        "required_all_roles": {
                            "bsonType": "array",
                            "description": "رتب مطلوبة (ALL)",
                            "items": {"bsonType": "string"}
                        },
                        "blacklisted_roles": {
                            "bsonType": "array",
                            "description": "رتب محظورة",
                            "items": {"bsonType": "string"}
                        },
                        "min_level": {
                            "bsonType": ["int", "null"],
                            "description": "مستوى أدنى مطلوب"
                        },
                        "min_credits": {
                            "bsonType": ["int", "null"],
                            "description": "حد أدنى من الكريديت"
                        },
                        "min_account_age_days": {
                            "bsonType": ["int", "null"],
                            "description": "عمر الحساب بالأيام"
                        },
                        "min_server_join_days": {
                            "bsonType": ["int", "null"],
                            "description": "مدة العضوية في السيرفر"
                        }
                    }
                },
                
                # ===== Entries & Winners =====
                "entries": {
                    "bsonType": "array",
                    "description": "قائمة المشاركين",
                    "items": {
                        "bsonType": "object",
                        "required": ["user_id", "joined_at"],
                        "properties": {
                            "user_id": {
                                "bsonType": "string",
                                "description": "معرف المستخدم"
                            },
                            "joined_at": {
                                "bsonType": "date",
                                "description": "وقت الانضمام"
                            },
                            "entities_points": {
                                "bsonType": "int",
                                "description": "مجموع نقاط Entities للمستخدم"
                            },
                            "bonus_entries": {
                                "bsonType": "int",
                                "description": "إدخالات إضافية بناءً على النقاط",
                                "minimum": 0
                            }
                        }
                    }
                },
                "winners": {
                    "bsonType": "array",
                    "description": "قائمة الفائزين",
                    "items": {
                        "bsonType": "object",
                        "properties": {
                            "user_id": {"bsonType": "string"},
                            "won_at": {"bsonType": "date"},
                            "entities_points": {"bsonType": "int"},
                            "claimed": {"bsonType": "bool"}
                        }
                    }
                },
                
                # ===== Settings =====
                "settings": {
                    "bsonType": "object",
                    "properties": {
                        "emoji": {
                            "bsonType": "string",
                            "description": "إيموجي التفاعل"
                        },
                        "ping_role_id": {
                            "bsonType": ["string", "null"],
                            "description": "رتبة للإشارة عند البدء"
                        },
                        "dm_winner": {
                            "bsonType": "bool",
                            "description": "إرسال DM للفائز"
                        },
                        "show_participants": {
                            "bsonType": "bool",
                            "description": "عرض عدد المشاركين"
                        },
                        "show_entities_info": {
                            "bsonType": "bool",
                            "description": "عرض معلومات Entities في الرسالة"
                        }
                    }
                },
                
                # ===== Timestamps =====
                "created_at": {
                    "bsonType": "date",
                    "description": "تاريخ الإنشاء"
                },
                "ended_at": {
                    "bsonType": ["date", "null"],
                    "description": "تاريخ الانتهاء"
                },
                "cancelled_at": {
                    "bsonType": ["date", "null"],
                    "description": "تاريخ الإلغاء"
                },
                
                # ===== Stats =====
                "stats": {
                    "bsonType": "object",
                    "properties": {
                        "total_entries": {"bsonType": "int"},
                        "total_bonus_entries": {"bsonType": "int"},
                        "avg_entities_points": {"bsonType": "double"},
                        "max_entities_points": {"bsonType": "int"}
                    }
                }
            }
        }
    }
}


# ===== Giveaway Templates Schema =====
GIVEAWAY_TEMPLATES_SCHEMA = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["template_id", "guild_id", "name", "created_by"],
            "properties": {
                "template_id": {
                    "bsonType": "string",
                    "description": "معرف فريد للقالب"
                },
                "guild_id": {
                    "bsonType": "string",
                    "description": "معرف السيرفر"
                },
                "name": {
                    "bsonType": "string",
                    "description": "اسم القالب",
                    "maxLength": 100
                },
                "description": {
                    "bsonType": ["string", "null"],
                    "description": "وصف القالب",
                    "maxLength": 500
                },
                "created_by": {
                    "bsonType": "string",
                    "description": "منشئ القالب"
                },
                
                # ===== Giveaway Configuration =====
                "prize": {
                    "bsonType": "string",
                    "description": "الجائزة الافتراضية",
                    "maxLength": 256
                },
                "giveaway_description": {
                    "bsonType": ["string", "null"],
                    "description": "وصف القرعة",
                    "maxLength": 1000
                },
                "winners_count": {
                    "bsonType": "int",
                    "description": "عدد الفائزين",
                    "minimum": 1,
                    "maximum": 50
                },
                "default_duration_seconds": {
                    "bsonType": "int",
                    "description": "المدة الافتراضية بالثواني",
                    "minimum": 60
                },
                
                # ===== Visual Settings =====
                "color": {
                    "bsonType": "string",
                    "description": "لون Embed",
                    "pattern": "^#[0-9A-Fa-f]{6}$"
                },
                "thumbnail_url": {
                    "bsonType": ["string", "null"],
                    "description": "صورة مصغرة"
                },
                "image_url": {
                    "bsonType": ["string", "null"],
                    "description": "صورة كبيرة"
                },
                "footer_text": {
                    "bsonType": ["string", "null"],
                    "description": "نص الذيل",
                    "maxLength": 200
                },
                "footer_icon_url": {
                    "bsonType": ["string", "null"],
                    "description": "أيقونة الذيل"
                },
                "emoji": {
                    "bsonType": "string",
                    "description": "إيموجي التفاعل"
                },
                
                # ===== Entities Configuration =====
                "entities_enabled": {
                    "bsonType": "bool",
                    "description": "هل Entities مفعّل"
                },
                "entities_mode": {
                    "bsonType": "string",
                    "enum": ["cumulative", "highest"],
                    "description": "وضع Entities"
                },
                "role_entities": {
                    "bsonType": "array",
                    "description": "رتب Entities",
                    "items": {
                        "bsonType": "object",
                        "required": ["role_id", "points"],
                        "properties": {
                            "role_id": {"bsonType": "string"},
                            "points": {"bsonType": "int", "minimum": 1, "maximum": 100}
                        }
                    }
                },
                
                # ===== Requirements =====
                "requirements": {
                    "bsonType": "object",
                    "description": "شروط الدخول",
                    "properties": {
                        "required_roles": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "required_all_roles": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "blacklisted_roles": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"}
                        },
                        "min_level": {"bsonType": ["int", "null"]},
                        "min_credits": {"bsonType": ["int", "null"]},
                        "min_account_age_days": {"bsonType": ["int", "null"]},
                        "min_server_join_days": {"bsonType": ["int", "null"]}
                    }
                },
                
                # ===== Notification Settings =====
                "ping_role_id": {
                    "bsonType": ["string", "null"],
                    "description": "رتبة للإشارة"
                },
                "dm_winner": {
                    "bsonType": "bool",
                    "description": "إرسال DM للفائز"
                },
                "show_participants": {
                    "bsonType": "bool",
                    "description": "عرض عدد المشاركين"
                },
                "show_entities_info": {
                    "bsonType": "bool",
                    "description": "عرض معلومات Entities"
                },
                
                # ===== Scheduling (Optional) =====
                "schedule_enabled": {
                    "bsonType": "bool",
                    "description": "هل الجدولة مفعّلة"
                },
                "schedule_datetime": {
                    "bsonType": ["date", "null"],
                    "description": "وقت بدء القرعة المجدولة"
                },
                
                # ===== Stats & Timestamps =====
                "usage_count": {
                    "bsonType": "int",
                    "description": "عدد مرات الاستخدام"
                },
                "is_favorite": {
                    "bsonType": "bool",
                    "description": "قالب مفضل"
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "تاريخ الإنشاء"
                },
                "updated_at": {
                    "bsonType": "date",
                    "description": "آخر تحديث"
                },
                "last_used_at": {
                    "bsonType": ["date", "null"],
                    "description": "آخر استخدام"
                }
            }
        }
    }
}


# ===== Giveaway Settings Schema =====
GIVEAWAY_SETTINGS_SCHEMA = {
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
                    "description": "هل نظام القرعات مفعّل"
                },
                "default_emoji": {
                    "bsonType": "string",
                    "description": "إيموجي افتراضي للقرعات"
                },
                "default_color": {
                    "bsonType": "string",
                    "description": "لون افتراضي",
                    "pattern": "^#[0-9A-Fa-f]{6}$"
                },
                "log_channel_id": {
                    "bsonType": ["string", "null"],
                    "description": "قناة سجلات القرعات"
                },
                "manager_roles": {
                    "bsonType": "array",
                    "description": "رتب مديري القرعات",
                    "items": {"bsonType": "string"}
                },
                "blacklisted_users": {
                    "bsonType": "array",
                    "description": "مستخدمون محظورون من جميع القرعات",
                    "items": {"bsonType": "string"}
                },
                
                # ===== إعدادات Entities الافتراضية =====
                "default_entities_enabled": {
                    "bsonType": "bool",
                    "description": "تفعيل Entities افتراضياً"
                },
                "default_entities_mode": {
                    "bsonType": "string",
                    "enum": ["cumulative", "highest"],
                    "description": "وضع Entities الافتراضي"
                },
                "default_role_entities": {
                    "bsonType": "array",
                    "description": "إعدادات Entities افتراضية للسيرفر",
                    "items": {
                        "bsonType": "object",
                        "properties": {
                            "role_id": {"bsonType": "string"},
                            "points": {"bsonType": "int"}
                        }
                    }
                },
                
                # ===== Stats =====
                "stats": {
                    "bsonType": "object",
                    "properties": {
                        "total_giveaways": {"bsonType": "int"},
                        "total_winners": {"bsonType": "int"},
                        "total_entries": {"bsonType": "int"}
                    }
                },
                "created_at": {
                    "bsonType": "date"
                },
                "updated_at": {
                    "bsonType": "date"
                }
            }
        }
    }
}


class GiveawayDatabase:
    """إدارة قاعدة بيانات القرعات"""
    
    def __init__(self, db):
        self.db = db
        self.giveaways = db.giveaways
        self.settings = db.giveaway_settings
        self.templates = db.giveaway_templates
    
    async def setup_indexes(self):
        """إنشاء indexes"""
        # Giveaways
        await self.giveaways.create_index("giveaway_id", unique=True)
        await self.giveaways.create_index("guild_id")
        await self.giveaways.create_index([("guild_id", 1), ("status", 1)])
        await self.giveaways.create_index("message_id")
        await self.giveaways.create_index("end_time")
        await self.giveaways.create_index([("status", 1), ("end_time", 1)])
        
        # Settings
        await self.settings.create_index("guild_id", unique=True)
        
        # Templates
        await self.templates.create_index("template_id", unique=True)
        await self.templates.create_index("guild_id")
        await self.templates.create_index([("guild_id", 1), ("created_by", 1)])
        await self.templates.create_index([("guild_id", 1), ("is_favorite", 1)])
    
    # ===== Giveaways CRUD =====
    async def create_giveaway(self, giveaway_data: Dict) -> Dict:
        """إنشاء قرعة جديدة"""
        await self.giveaways.insert_one(giveaway_data)
        
        # Update guild stats
        await self.settings.update_one(
            {"guild_id": giveaway_data["guild_id"]},
            {"$inc": {"stats.total_giveaways": 1}}
        )
        
        return giveaway_data
    
    async def get_giveaway(self, giveaway_id: str) -> Optional[Dict]:
        """جلب قرعة"""
        return await self.giveaways.find_one({"giveaway_id": giveaway_id})
    
    async def get_giveaway_by_message(self, message_id: str) -> Optional[Dict]:
        """جلب قرعة من خلال معرف الرسالة"""
        return await self.giveaways.find_one({"message_id": message_id})
    
    async def get_guild_giveaways(
        self,
        guild_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """جلب قرعات السيرفر"""
        query = {"guild_id": guild_id}
        if status:
            query["status"] = status
        
        cursor = self.giveaways.find(query).sort("created_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_active_giveaways(self) -> List[Dict]:
        """جلب جميع القرعات النشطة للتحقق"""
        cursor = self.giveaways.find({
            "status": "active",
            "end_time": {"$exists": True}
        }).sort("end_time", 1)
        return await cursor.to_list(length=1000)
    
    async def update_giveaway(self, giveaway_id: str, updates: Dict) -> bool:
        """تحديث قرعة"""
        result = await self.giveaways.update_one(
            {"giveaway_id": giveaway_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_giveaway(self, giveaway_id: str) -> bool:
        """حذف قرعة"""
        result = await self.giveaways.delete_one({"giveaway_id": giveaway_id})
        return result.deleted_count > 0
    
    # ===== Entries Management =====
    async def add_entry(
        self,
        giveaway_id: str,
        user_id: str,
        entities_points: int = 0
    ) -> bool:
        """إضافة مشارك"""
        # Calculate bonus entries (1 point = 1% = 1 extra entry per 100 points)
        bonus_entries = entities_points  # 1:1 ratio for simplicity
        
        entry = {
            "user_id": user_id,
            "joined_at": datetime.now(timezone.utc),
            "entities_points": entities_points,
            "bonus_entries": bonus_entries
        }
        
        result = await self.giveaways.update_one(
            {"giveaway_id": giveaway_id},
            {
                "$push": {"entries": entry},
                "$inc": {
                    "stats.total_entries": 1,
                    "stats.total_bonus_entries": bonus_entries
                }
            }
        )
        
        # Update avg and max entities points
        if entities_points > 0:
            giveaway = await self.get_giveaway(giveaway_id)
            if giveaway:
                entries = giveaway.get("entries", [])
                total_points = sum(e.get("entities_points", 0) for e in entries)
                avg_points = total_points / len(entries) if entries else 0
                max_points = max((e.get("entities_points", 0) for e in entries), default=0)
                
                await self.giveaways.update_one(
                    {"giveaway_id": giveaway_id},
                    {
                        "$set": {
                            "stats.avg_entities_points": avg_points,
                            "stats.max_entities_points": max_points
                        }
                    }
                )
        
        return result.modified_count > 0
    
    async def remove_entry(self, giveaway_id: str, user_id: str) -> bool:
        """إزالة مشارك"""
        # Get entry to update stats
        giveaway = await self.get_giveaway(giveaway_id)
        if not giveaway:
            return False
        
        entry = next((e for e in giveaway.get("entries", []) if e["user_id"] == user_id), None)
        if not entry:
            return False
        
        bonus_entries = entry.get("bonus_entries", 0)
        
        result = await self.giveaways.update_one(
            {"giveaway_id": giveaway_id},
            {
                "$pull": {"entries": {"user_id": user_id}},
                "$inc": {
                    "stats.total_entries": -1,
                    "stats.total_bonus_entries": -bonus_entries
                }
            }
        )
        
        return result.modified_count > 0
    
    async def is_entered(self, giveaway_id: str, user_id: str) -> bool:
        """التحقق من دخول المستخدم"""
        result = await self.giveaways.find_one({
            "giveaway_id": giveaway_id,
            "entries.user_id": user_id
        })
        return result is not None
    
    # ===== Winners Management =====
    async def add_winners(self, giveaway_id: str, winners: List[Dict]) -> bool:
        """إضافة فائزين"""
        result = await self.giveaways.update_one(
            {"giveaway_id": giveaway_id},
            {
                "$set": {
                    "winners": winners,
                    "status": "ended",
                    "ended_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Update guild stats
        if result.modified_count > 0:
            giveaway = await self.get_giveaway(giveaway_id)
            if giveaway:
                await self.settings.update_one(
                    {"guild_id": giveaway["guild_id"]},
                    {"$inc": {"stats.total_winners": len(winners)}}
                )
        
        return result.modified_count > 0
    
    # ===== Settings CRUD =====
    async def get_settings(self, guild_id: str) -> Optional[Dict]:
        """جلب إعدادات السيرفر"""
        return await self.settings.find_one({"guild_id": guild_id})
    
    async def create_settings(self, guild_id: str) -> Dict:
        """إنشاء إعدادات جديدة"""
        settings_doc = {
            "guild_id": guild_id,
            "enabled": True,
            "default_emoji": "🎉",
            "default_color": "#FF00FF",
            "log_channel_id": None,
            "manager_roles": [],
            "blacklisted_users": [],
            "default_entities_enabled": False,
            "default_entities_mode": "cumulative",
            "default_role_entities": [],
            "stats": {
                "total_giveaways": 0,
                "total_winners": 0,
                "total_entries": 0
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await self.settings.insert_one(settings_doc)
        return settings_doc
    
    async def update_settings(self, guild_id: str, updates: Dict) -> bool:
        """تحديث الإعدادات"""
        updates["updated_at"] = datetime.now(timezone.utc)
        result = await self.settings.update_one(
            {"guild_id": guild_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    # ===== Templates CRUD =====
    async def create_template(self, template_data: Dict) -> Dict:
        """إنشاء قالب جديد"""
        template_data["created_at"] = datetime.now(timezone.utc)
        template_data["updated_at"] = datetime.now(timezone.utc)
        template_data["usage_count"] = 0
        template_data["last_used_at"] = None
        template_data["is_favorite"] = False
        
        await self.templates.insert_one(template_data)
        return template_data
    
    async def get_template(self, template_id: str) -> Optional[Dict]:
        """جلب قالب"""
        return await self.templates.find_one({"template_id": template_id})
    
    async def get_guild_templates(
        self,
        guild_id: str,
        created_by: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """جلب قوالب السيرفر"""
        query = {"guild_id": guild_id}
        if created_by:
            query["created_by"] = created_by
        
        cursor = self.templates.find(query).sort([
            ("is_favorite", -1),  # المفضلة أولاً
            ("usage_count", -1),  # الأكثر استخداماً
            ("created_at", -1)    # الأحدث
        ]).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def update_template(self, template_id: str, updates: Dict) -> bool:
        """تحديث قالب"""
        updates["updated_at"] = datetime.now(timezone.utc)
        result = await self.templates.update_one(
            {"template_id": template_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_template(self, template_id: str) -> bool:
        """حذف قالب"""
        result = await self.templates.delete_one({"template_id": template_id})
        return result.deleted_count > 0
    
    async def increment_template_usage(self, template_id: str) -> bool:
        """زيادة عداد الاستخدام"""
        result = await self.templates.update_one(
            {"template_id": template_id},
            {
                "$inc": {"usage_count": 1},
                "$set": {
                    "last_used_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        return result.modified_count > 0
    
    async def toggle_template_favorite(self, template_id: str) -> bool:
        """تبديل حالة المفضلة"""
        template = await self.get_template(template_id)
        if not template:
            return False
        
        new_status = not template.get("is_favorite", False)
        return await self.update_template(template_id, {"is_favorite": new_status})


async def init_giveaway_schema(db: AsyncIOMotorDatabase):
    """تهيئة schema"""
    try:
        await db.create_collection("giveaways", **GIVEAWAYS_SCHEMA)
    except Exception:
        pass
    
    try:
        await db.create_collection("giveaway_settings", **GIVEAWAY_SETTINGS_SCHEMA)
    except Exception:
        pass
    
    try:
        await db.create_collection("giveaway_templates", **GIVEAWAY_TEMPLATES_SCHEMA)
    except Exception:
        pass
    
    giveaway_db = GiveawayDatabase(db)
    await giveaway_db.setup_indexes()
    return giveaway_db

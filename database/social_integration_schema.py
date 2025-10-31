"""
🌐 Social Media Integration Database Schema
Kingdom-77 Bot v4.0 - Phase 5.7

نظام التكامل مع وسائل التواصل الاجتماعي (مثل Pingcord)
يدعم: YouTube, Twitch, Kick, Twitter, Instagram, TikTok, Snapchat

الميزات:
- 2 روابط مجانية لكل سيرفر
- شراء روابط إضافية (200 ❄️ دائم)
- إشعارات تلقائية عند النشر
- Embed مخصص مع صورة الغلاف
"""

from datetime import datetime, timezone
from typing import Optional, Dict, List
from motor.motor_asyncio import AsyncIOMotorDatabase


# ===== Social Links Schema =====
SOCIAL_LINKS_SCHEMA = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["link_id", "guild_id", "user_id", "platform", "channel_url"],
            "properties": {
                "link_id": {
                    "bsonType": "string",
                    "description": "معرف فريد للرابط"
                },
                "guild_id": {
                    "bsonType": "string",
                    "description": "معرف السيرفر"
                },
                "user_id": {
                    "bsonType": "string",
                    "description": "معرف المستخدم صاحب الرابط"
                },
                "platform": {
                    "bsonType": "string",
                    "enum": ["youtube", "twitch", "kick", "twitter", "instagram", "tiktok", "snapchat"],
                    "description": "المنصة"
                },
                "channel_url": {
                    "bsonType": "string",
                    "description": "رابط القناة/الحساب"
                },
                "channel_id": {
                    "bsonType": "string",
                    "description": "معرف القناة على المنصة"
                },
                "channel_name": {
                    "bsonType": "string",
                    "description": "اسم القناة/الحساب"
                },
                "notification_channel_id": {
                    "bsonType": "string",
                    "description": "قناة Discord للإشعارات"
                },
                "role_mention_id": {
                    "bsonType": ["string", "null"],
                    "description": "رتبة للإشارة عند النشر"
                },
                "custom_message": {
                    "bsonType": ["string", "null"],
                    "description": "رسالة مخصصة",
                    "maxLength": 500
                },
                "embed_color": {
                    "bsonType": "string",
                    "description": "لون Embed",
                    "pattern": "^#[0-9A-Fa-f]{6}$"
                },
                "last_post_id": {
                    "bsonType": ["string", "null"],
                    "description": "آخر منشور تم التحقق منه"
                },
                "last_checked_at": {
                    "bsonType": ["date", "null"],
                    "description": "آخر فحص"
                },
                "is_active": {
                    "bsonType": "bool",
                    "description": "هل الرابط نشط"
                },
                "is_purchased": {
                    "bsonType": "bool",
                    "description": "هل تم شراء الرابط (مقابل 200 ❄️)"
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "تاريخ الإنشاء"
                },
                "updated_at": {
                    "bsonType": "date",
                    "description": "تاريخ آخر تحديث"
                },
                "stats": {
                    "bsonType": "object",
                    "properties": {
                        "total_posts_notified": {"bsonType": "int"},
                        "last_notification_at": {"bsonType": ["date", "null"]}
                    }
                }
            }
        }
    }
}


# ===== Social Posts Schema =====
SOCIAL_POSTS_SCHEMA = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["post_id", "link_id", "platform", "post_url", "published_at"],
            "properties": {
                "post_id": {
                    "bsonType": "string",
                    "description": "معرف فريد للمنشور"
                },
                "link_id": {
                    "bsonType": "string",
                    "description": "معرف الرابط المرتبط"
                },
                "platform": {
                    "bsonType": "string",
                    "enum": ["youtube", "twitch", "kick", "twitter", "instagram", "tiktok"]
                },
                "platform_post_id": {
                    "bsonType": "string",
                    "description": "معرف المنشور على المنصة"
                },
                "post_title": {
                    "bsonType": "string",
                    "description": "عنوان المنشور"
                },
                "post_description": {
                    "bsonType": ["string", "null"],
                    "description": "وصف المنشور"
                },
                "post_thumbnail": {
                    "bsonType": ["string", "null"],
                    "description": "صورة الغلاف"
                },
                "post_url": {
                    "bsonType": "string",
                    "description": "رابط المنشور"
                },
                "author_name": {
                    "bsonType": "string",
                    "description": "اسم المنشئ"
                },
                "author_avatar": {
                    "bsonType": ["string", "null"],
                    "description": "صورة المنشئ"
                },
                "published_at": {
                    "bsonType": "date",
                    "description": "تاريخ النشر على المنصة"
                },
                "notified_at": {
                    "bsonType": ["date", "null"],
                    "description": "تاريخ الإشعار في Discord"
                },
                "notification_message_id": {
                    "bsonType": ["string", "null"],
                    "description": "معرف رسالة Discord"
                }
            }
        }
    }
}


# ===== Social Settings Schema =====
SOCIAL_SETTINGS_SCHEMA = {
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
                "free_links_used": {
                    "bsonType": "int",
                    "description": "عدد الروابط المجانية المستخدمة (max: 2)",
                    "minimum": 0,
                    "maximum": 2
                },
                "additional_links_purchased": {
                    "bsonType": "int",
                    "description": "عدد الروابط المشتراة",
                    "minimum": 0
                },
                "check_interval_minutes": {
                    "bsonType": "int",
                    "description": "فترة الفحص بالدقائق",
                    "minimum": 1,
                    "maximum": 60
                },
                "default_embed_color": {
                    "bsonType": "string",
                    "description": "لون Embed افتراضي",
                    "pattern": "^#[0-9A-Fa-f]{6}$"
                },
                "stats": {
                    "bsonType": "object",
                    "properties": {
                        "total_links": {"bsonType": "int"},
                        "total_posts_notified": {"bsonType": "int"},
                        "total_credits_spent": {"bsonType": "int"}
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


class SocialIntegrationDatabase:
    """إدارة قاعدة بيانات Social Integration"""
    
    def __init__(self, db):
        self.db = db
        self.links = db.social_links
        self.posts = db.social_posts
        self.settings = db.social_settings
    
    async def setup_indexes(self):
        """إنشاء indexes"""
        # Links
        await self.links.create_index("link_id", unique=True)
        await self.links.create_index("guild_id")
        await self.links.create_index([("guild_id", 1), ("is_active", 1)])
        await self.links.create_index("user_id")
        await self.links.create_index([("platform", 1), ("channel_id", 1)])
        
        # Posts
        await self.posts.create_index("post_id", unique=True)
        await self.posts.create_index("link_id")
        await self.posts.create_index([("link_id", 1), ("published_at", -1)])
        await self.posts.create_index("platform_post_id")
        
        # Settings
        await self.settings.create_index("guild_id", unique=True)
    
    # ===== Links CRUD =====
    async def create_link(self, link_data: Dict) -> Dict:
        """إنشاء رابط جديد"""
        await self.links.insert_one(link_data)
        
        # Update guild stats
        await self.settings.update_one(
            {"guild_id": link_data["guild_id"]},
            {"$inc": {"stats.total_links": 1}}
        )
        
        return link_data
    
    async def get_link(self, link_id: str) -> Optional[Dict]:
        """جلب رابط"""
        return await self.links.find_one({"link_id": link_id})
    
    async def get_user_links(
        self,
        user_id: str,
        guild_id: Optional[str] = None
    ) -> List[Dict]:
        """جلب روابط المستخدم"""
        query = {"user_id": user_id}
        if guild_id:
            query["guild_id"] = guild_id
        
        cursor = self.links.find(query).sort("created_at", -1)
        return await cursor.to_list(length=100)
    
    async def get_guild_links(
        self,
        guild_id: str,
        active_only: bool = True
    ) -> List[Dict]:
        """جلب روابط السيرفر"""
        query = {"guild_id": guild_id}
        if active_only:
            query["is_active"] = True
        
        cursor = self.links.find(query).sort("created_at", -1)
        return await cursor.to_list(length=100)
    
    async def get_active_links_for_check(self) -> List[Dict]:
        """جلب جميع الروابط النشطة للفحص"""
        cursor = self.links.find({"is_active": True})
        return await cursor.to_list(length=1000)
    
    async def update_link(self, link_id: str, updates: Dict) -> bool:
        """تحديث رابط"""
        updates["updated_at"] = datetime.now(timezone.utc)
        result = await self.links.update_one(
            {"link_id": link_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_link(self, link_id: str) -> bool:
        """حذف رابط"""
        # Get link info first
        link = await self.get_link(link_id)
        if not link:
            return False
        
        # Delete link
        result = await self.links.delete_one({"link_id": link_id})
        
        if result.deleted_count > 0:
            # Update guild stats
            await self.settings.update_one(
                {"guild_id": link["guild_id"]},
                {"$inc": {"stats.total_links": -1}}
            )
            
            # Delete associated posts
            await self.posts.delete_many({"link_id": link_id})
            
            return True
        
        return False
    
    async def update_last_check(self, link_id: str, last_post_id: Optional[str] = None):
        """تحديث آخر فحص"""
        updates = {
            "last_checked_at": datetime.now(timezone.utc)
        }
        if last_post_id:
            updates["last_post_id"] = last_post_id
        
        await self.update_link(link_id, updates)
    
    # ===== Posts CRUD =====
    async def create_post(self, post_data: Dict) -> Dict:
        """حفظ منشور جديد"""
        await self.posts.insert_one(post_data)
        
        # Update link stats
        await self.links.update_one(
            {"link_id": post_data["link_id"]},
            {
                "$inc": {"stats.total_posts_notified": 1},
                "$set": {"stats.last_notification_at": datetime.now(timezone.utc)}
            }
        )
        
        return post_data
    
    async def get_post(self, post_id: str) -> Optional[Dict]:
        """جلب منشور"""
        return await self.posts.find_one({"post_id": post_id})
    
    async def get_post_by_platform_id(
        self,
        link_id: str,
        platform_post_id: str
    ) -> Optional[Dict]:
        """التحقق من وجود منشور"""
        return await self.posts.find_one({
            "link_id": link_id,
            "platform_post_id": platform_post_id
        })
    
    async def get_link_posts(
        self,
        link_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """جلب منشورات رابط"""
        cursor = self.posts.find({"link_id": link_id}).sort("published_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def get_guild_recent_posts(
        self,
        guild_id: str,
        limit: int = 50
    ) -> List[Dict]:
        """جلب آخر منشورات السيرفر"""
        # Get all guild links
        links = await self.get_guild_links(guild_id, active_only=False)
        link_ids = [link["link_id"] for link in links]
        
        cursor = self.posts.find({"link_id": {"$in": link_ids}}).sort("published_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    # ===== Settings CRUD =====
    async def get_settings(self, guild_id: str) -> Optional[Dict]:
        """جلب إعدادات السيرفر"""
        return await self.settings.find_one({"guild_id": guild_id})
    
    async def create_settings(self, guild_id: str) -> Dict:
        """إنشاء إعدادات جديدة"""
        settings_doc = {
            "guild_id": guild_id,
            "enabled": True,
            "free_links_used": 0,
            "additional_links_purchased": 0,
            "check_interval_minutes": 5,
            "default_embed_color": "#5865F2",
            "stats": {
                "total_links": 0,
                "total_posts_notified": 0,
                "total_credits_spent": 0
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
    
    async def can_add_free_link(self, guild_id: str) -> bool:
        """التحقق من إمكانية إضافة رابط مجاني"""
        settings = await self.get_settings(guild_id)
        if not settings:
            settings = await self.create_settings(guild_id)
        
        return settings["free_links_used"] < 2
    
    async def increment_free_links(self, guild_id: str):
        """زيادة عداد الروابط المجانية"""
        await self.settings.update_one(
            {"guild_id": guild_id},
            {"$inc": {"free_links_used": 1}}
        )
    
    async def increment_purchased_links(self, guild_id: str):
        """زيادة عداد الروابط المشتراة"""
        await self.settings.update_one(
            {"guild_id": guild_id},
            {
                "$inc": {
                    "additional_links_purchased": 1,
                    "stats.total_credits_spent": 200
                }
            }
        )
    
    async def get_available_slots(self, guild_id: str) -> Dict:
        """حساب الحدود المتاحة"""
        settings = await self.get_settings(guild_id)
        if not settings:
            settings = await self.create_settings(guild_id)
        
        current_links = await self.links.count_documents({"guild_id": guild_id})
        max_links = 2 + settings["additional_links_purchased"]
        
        return {
            "current": current_links,
            "max": max_links,
            "free_used": settings["free_links_used"],
            "purchased": settings["additional_links_purchased"],
            "can_add_free": settings["free_links_used"] < 2,
            "available": max(0, max_links - current_links)
        }


async def init_social_integration_schema(db: AsyncIOMotorDatabase):
    """تهيئة schema"""
    try:
        await db.create_collection("social_links", **SOCIAL_LINKS_SCHEMA)
    except Exception:
        pass
    
    try:
        await db.create_collection("social_posts", **SOCIAL_POSTS_SCHEMA)
    except Exception:
        pass
    
    try:
        await db.create_collection("social_settings", **SOCIAL_SETTINGS_SCHEMA)
    except Exception:
        pass
    
    social_db = SocialIntegrationDatabase(db)
    await social_db.setup_indexes()
    return social_db

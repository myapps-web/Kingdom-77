"""
Kingdom-77 Bot - Welcome System Schema
نظام ترحيب متقدم للأعضاء الجدد

Collections:
- welcome_settings: إعدادات الترحيب لكل سيرفر
- welcome_cards: تصاميم بطاقات الترحيب المخصصة
- captcha_verifications: سجل التحققات من Captcha
- join_history: تاريخ انضمام الأعضاء
"""

from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, TYPE_CHECKING
import discord

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase


class WelcomeSchema:
    """Schema for Welcome System"""
    
    def __init__(self, db: "AsyncIOMotorDatabase"):
        self.db = db
        self.settings = db.welcome_settings
        self.cards = db.welcome_cards
        self.captcha = db.captcha_verifications
        self.join_history = db.join_history
    
    async def create_indexes(self):
        """إنشاء الـ indexes للأداء الأفضل"""
        # Settings indexes
        await self.settings.create_index("guild_id", unique=True)
        
        # Cards indexes
        await self.cards.create_index([("guild_id", 1), ("is_active", 1)])
        
        # Captcha indexes
        await self.captcha.create_index([("guild_id", 1), ("user_id", 1)])
        await self.captcha.create_index([("guild_id", 1), ("verified", 1)])
        await self.captcha.create_index([("timestamp", 1)], expireAfterSeconds=3600)  # 1 ساعة
        
        # Join history indexes
        await self.join_history.create_index([("guild_id", 1), ("timestamp", -1)])
        await self.join_history.create_index([("guild_id", 1), ("user_id", 1)])
    
    # ==================== Welcome Settings ====================
    
    async def get_settings(self, guild_id: int) -> Optional[Dict]:
        """الحصول على إعدادات الترحيب"""
        return await self.settings.find_one({"guild_id": guild_id})
    
    async def create_default_settings(self, guild_id: int) -> Dict:
        """إنشاء إعدادات افتراضية"""
        settings = {
            "guild_id": guild_id,
            "enabled": False,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            
            # قنوات الترحيب
            "channels": {
                "welcome_channel": None,      # قناة رسالة الترحيب
                "goodbye_channel": None,      # قناة رسالة المغادرة
                "log_channel": None          # قناة السجلات
            },
            
            # رسائل الترحيب
            "welcome_message": {
                "enabled": True,
                "type": "embed",  # text, embed, card
                "title": "مرحباً {user.name}! 👋",
                "description": "أهلاً بك في **{server.name}**!\n\nأنت العضو رقم **{member.count}**",
                "color": "#5865F2",
                "thumbnail": "user_avatar",  # user_avatar, server_icon, custom
                "image": None,
                "footer": "نتمنى لك إقامة ممتعة!",
                "timestamp": True
            },
            
            # رسائل المغادرة
            "goodbye_message": {
                "enabled": False,
                "type": "embed",
                "title": "وداعاً {user.name} 👋",
                "description": "**{user.name}** غادر السيرفر\n\nكان معنا لمدة **{duration}**",
                "color": "#ED4245",
                "thumbnail": "user_avatar",
                "image": None,
                "footer": "نتمنى أن نراك قريباً!",
                "timestamp": True
            },
            
            # رسائل DM
            "dm_message": {
                "enabled": False,
                "content": "مرحباً {user.mention}! 👋\n\nشكراً لانضمامك إلى **{server.name}**!",
                "embed": None
            },
            
            # بطاقة الترحيب (Welcome Card)
            "welcome_card": {
                "enabled": False,
                "template": "classic",  # classic, modern, minimal, fancy, custom
                "background_url": None,
                "background_color": "#2B2D31",
                "text_color": "#FFFFFF",
                "accent_color": "#5865F2",
                "show_avatar": True,
                "show_username": True,
                "show_discriminator": True,
                "show_member_count": True,
                "show_join_date": False,
                "custom_text": "Welcome to {server.name}!"
            },
            
            # Auto-Role عند الانضمام
            "auto_role": {
                "enabled": False,
                "roles": [],  # قائمة IDs الرتب
                "delay": 0,   # تأخير بالثواني
                "remove_on_leave": False
            },
            
            # Captcha Verification
            "captcha": {
                "enabled": False,
                "difficulty": "medium",  # easy, medium, hard
                "timeout": 300,  # 5 دقائق
                "max_attempts": 3,
                "kick_on_fail": False,
                "unverified_role": None,  # رتبة لغير المُتحقق منهم
                "verified_role": None,     # رتبة بعد التحقق
                "verification_channel": None
            },
            
            # Multiple Channels (إرسال في عدة قنوات)
            "multi_channel": {
                "enabled": False,
                "channels": []  # قائمة قنوات إضافية
            },
            
            # إعدادات متقدمة
            "settings": {
                "mention_user": True,
                "ping_role": None,  # رتبة للـ ping
                "delete_after": None,  # حذف الرسالة بعد X ثواني
                "ignore_bots": True,
                "test_mode": False,  # وضع اختبار (لا يرسل رسائل حقيقية)
                "log_joins": True,
                "log_leaves": True,
                "anti_raid": {
                    "enabled": False,
                    "max_joins_per_minute": 10,
                    "action": "captcha"  # captcha, kick, ban
                }
            },
            
            # إحصائيات
            "stats": {
                "total_welcomes": 0,
                "total_goodbyes": 0,
                "captcha_passed": 0,
                "captcha_failed": 0,
                "last_welcome": None,
                "last_goodbye": None
            }
        }
        
        await self.settings.insert_one(settings)
        return settings
    
    async def update_settings(self, guild_id: int, updates: Dict) -> bool:
        """تحديث الإعدادات"""
        updates["updated_at"] = datetime.utcnow()
        result = await self.settings.update_one(
            {"guild_id": guild_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def enable_welcome(self, guild_id: int, enabled: bool) -> bool:
        """تفعيل/تعطيل الترحيب"""
        return await self.update_settings(guild_id, {"enabled": enabled})
    
    async def set_welcome_channel(self, guild_id: int, channel_id: Optional[int]) -> bool:
        """تحديد قناة الترحيب"""
        return await self.update_settings(
            guild_id,
            {"channels.welcome_channel": channel_id}
        )
    
    async def set_goodbye_channel(self, guild_id: int, channel_id: Optional[int]) -> bool:
        """تحديد قناة المغادرة"""
        return await self.update_settings(
            guild_id,
            {"channels.goodbye_channel": channel_id}
        )
    
    # ==================== Welcome Cards ====================
    
    async def get_card_design(self, guild_id: int) -> Optional[Dict]:
        """الحصول على تصميم البطاقة النشط"""
        return await self.cards.find_one({
            "guild_id": guild_id,
            "is_active": True
        })
    
    async def create_card_design(
        self,
        guild_id: int,
        template: str,
        settings: Dict
    ) -> str:
        """إنشاء تصميم بطاقة جديد"""
        # إلغاء تفعيل البطاقات السابقة
        await self.cards.update_many(
            {"guild_id": guild_id},
            {"$set": {"is_active": False}}
        )
        
        card = {
            "guild_id": guild_id,
            "template": template,
            "settings": settings,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        result = await self.cards.insert_one(card)
        return str(result.inserted_id)
    
    async def get_all_card_designs(self, guild_id: int) -> List[Dict]:
        """الحصول على جميع تصاميم البطاقات"""
        cursor = self.cards.find({"guild_id": guild_id}).sort("created_at", -1)
        return await cursor.to_list(length=50)
    
    async def activate_card_design(self, guild_id: int, card_id: str) -> bool:
        """تفعيل تصميم بطاقة معين"""
        from bson import ObjectId
        
        # إلغاء تفعيل جميع البطاقات
        await self.cards.update_many(
            {"guild_id": guild_id},
            {"$set": {"is_active": False}}
        )
        
        # تفعيل البطاقة المختارة
        result = await self.cards.update_one(
            {"_id": ObjectId(card_id), "guild_id": guild_id},
            {"$set": {"is_active": True}}
        )
        
        return result.modified_count > 0
    
    # ==================== Captcha Verification ====================
    
    async def create_captcha(
        self,
        guild_id: int,
        user_id: int,
        code: str,
        image_url: str
    ) -> str:
        """إنشاء captcha جديد"""
        captcha = {
            "guild_id": guild_id,
            "user_id": user_id,
            "code": code,
            "image_url": image_url,
            "verified": False,
            "attempts": 0,
            "timestamp": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=5)
        }
        
        result = await self.captcha.insert_one(captcha)
        return str(result.inserted_id)
    
    async def get_pending_captcha(
        self,
        guild_id: int,
        user_id: int
    ) -> Optional[Dict]:
        """الحصول على captcha معلق"""
        return await self.captcha.find_one({
            "guild_id": guild_id,
            "user_id": user_id,
            "verified": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
    
    async def verify_captcha(
        self,
        guild_id: int,
        user_id: int,
        code: str
    ) -> tuple[bool, str]:
        """التحقق من captcha"""
        captcha = await self.get_pending_captcha(guild_id, user_id)
        
        if not captcha:
            return False, "لا يوجد captcha معلق أو انتهت صلاحيته"
        
        # زيادة عدد المحاولات
        attempts = captcha.get("attempts", 0) + 1
        await self.captcha.update_one(
            {"_id": captcha["_id"]},
            {"$set": {"attempts": attempts}}
        )
        
        # التحقق من الكود
        if code.lower() == captcha["code"].lower():
            await self.captcha.update_one(
                {"_id": captcha["_id"]},
                {"$set": {"verified": True}}
            )
            
            # تحديث الإحصائيات
            await self.settings.update_one(
                {"guild_id": guild_id},
                {"$inc": {"stats.captcha_passed": 1}}
            )
            
            return True, "✅ تم التحقق بنجاح!"
        
        # فشل التحقق
        settings = await self.get_settings(guild_id)
        max_attempts = settings.get("captcha", {}).get("max_attempts", 3)
        
        if attempts >= max_attempts:
            await self.settings.update_one(
                {"guild_id": guild_id},
                {"$inc": {"stats.captcha_failed": 1}}
            )
            return False, f"❌ فشل التحقق! تم استخدام جميع المحاولات ({max_attempts})"
        
        remaining = max_attempts - attempts
        return False, f"❌ كود خاطئ! المحاولات المتبقية: {remaining}"
    
    async def get_captcha_stats(self, guild_id: int, days: int = 7) -> Dict:
        """إحصائيات Captcha"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        total = await self.captcha.count_documents({
            "guild_id": guild_id,
            "timestamp": {"$gte": start_date}
        })
        
        verified = await self.captcha.count_documents({
            "guild_id": guild_id,
            "verified": True,
            "timestamp": {"$gte": start_date}
        })
        
        failed = await self.captcha.count_documents({
            "guild_id": guild_id,
            "verified": False,
            "attempts": {"$gte": 3},
            "timestamp": {"$gte": start_date}
        })
        
        return {
            "total": total,
            "verified": verified,
            "failed": failed,
            "success_rate": (verified / total * 100) if total > 0 else 0
        }
    
    # ==================== Join History ====================
    
    async def log_join(
        self,
        guild_id: int,
        user_id: int,
        username: str,
        discriminator: str,
        avatar_url: str,
        account_age_days: int,
        is_bot: bool,
        welcome_sent: bool,
        captcha_required: bool
    ) -> str:
        """تسجيل انضمام عضو"""
        join = {
            "guild_id": guild_id,
            "user_id": user_id,
            "username": username,
            "discriminator": discriminator,
            "avatar_url": avatar_url,
            "account_age_days": account_age_days,
            "is_bot": is_bot,
            "welcome_sent": welcome_sent,
            "captcha_required": captcha_required,
            "captcha_verified": False if captcha_required else None,
            "auto_roles_given": False,
            "timestamp": datetime.utcnow()
        }
        
        result = await self.join_history.insert_one(join)
        
        # تحديث الإحصائيات
        await self.settings.update_one(
            {"guild_id": guild_id},
            {
                "$inc": {"stats.total_welcomes": 1},
                "$set": {"stats.last_welcome": datetime.utcnow()}
            }
        )
        
        return str(result.inserted_id)
    
    async def log_leave(
        self,
        guild_id: int,
        user_id: int,
        username: str,
        duration_days: int
    ) -> bool:
        """تسجيل مغادرة عضو"""
        # البحث عن سجل الانضمام
        join_record = await self.join_history.find_one({
            "guild_id": guild_id,
            "user_id": user_id
        }, sort=[("timestamp", -1)])
        
        if join_record:
            await self.join_history.update_one(
                {"_id": join_record["_id"]},
                {"$set": {
                    "left_at": datetime.utcnow(),
                    "duration_days": duration_days
                }}
            )
        
        # تحديث الإحصائيات
        await self.settings.update_one(
            {"guild_id": guild_id},
            {
                "$inc": {"stats.total_goodbyes": 1},
                "$set": {"stats.last_goodbye": datetime.utcnow()}
            }
        )
        
        return True
    
    async def get_recent_joins(
        self,
        guild_id: int,
        limit: int = 50,
        minutes: Optional[int] = None
    ) -> List[Dict]:
        """الحصول على الانضمامات الأخيرة"""
        filters = {"guild_id": guild_id}
        
        if minutes:
            start_time = datetime.utcnow() - timedelta(minutes=minutes)
            filters["timestamp"] = {"$gte": start_time}
        
        cursor = self.join_history.find(filters).sort("timestamp", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def check_raid_pattern(
        self,
        guild_id: int,
        threshold: int = 10,
        window_minutes: int = 1
    ) -> Dict:
        """فحص نمط الغارة (Raid Detection)"""
        recent_joins = await self.get_recent_joins(
            guild_id,
            limit=100,
            minutes=window_minutes
        )
        
        joins_count = len(recent_joins)
        
        # حساب متوسط عمر الحسابات
        if recent_joins:
            avg_account_age = sum(j.get("account_age_days", 0) for j in recent_joins) / len(recent_joins)
            new_accounts = sum(1 for j in recent_joins if j.get("account_age_days", 0) < 7)
        else:
            avg_account_age = 0
            new_accounts = 0
        
        is_raid = joins_count >= threshold
        
        return {
            "is_raid": is_raid,
            "joins_in_window": joins_count,
            "threshold": threshold,
            "window_minutes": window_minutes,
            "avg_account_age_days": round(avg_account_age, 1),
            "new_accounts_count": new_accounts,
            "risk_level": "high" if is_raid else ("medium" if joins_count >= threshold // 2 else "low")
        }
    
    # ==================== Statistics ====================
    
    async def get_stats(self, guild_id: int, days: int = 30) -> Dict:
        """إحصائيات الترحيب"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # عدد الانضمامات
        total_joins = await self.join_history.count_documents({
            "guild_id": guild_id,
            "timestamp": {"$gte": start_date}
        })
        
        # عدد المغادرات
        total_leaves = await self.join_history.count_documents({
            "guild_id": guild_id,
            "left_at": {"$gte": start_date}
        })
        
        # إحصائيات Captcha
        captcha_stats = await self.get_captcha_stats(guild_id, days)
        
        # توزيع الانضمامات حسب اليوم
        pipeline = [
            {
                "$match": {
                    "guild_id": guild_id,
                    "timestamp": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$timestamp"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        
        daily_joins = await self.join_history.aggregate(pipeline).to_list(length=days)
        
        # الحصول على الإعدادات
        settings = await self.get_settings(guild_id)
        stats = settings.get("stats", {}) if settings else {}
        
        return {
            "period_days": days,
            "total_joins": total_joins,
            "total_leaves": total_leaves,
            "net_growth": total_joins - total_leaves,
            "captcha": captcha_stats,
            "daily_breakdown": daily_joins,
            "all_time": {
                "total_welcomes": stats.get("total_welcomes", 0),
                "total_goodbyes": stats.get("total_goodbyes", 0),
                "captcha_passed": stats.get("captcha_passed", 0),
                "captcha_failed": stats.get("captcha_failed", 0)
            }
        }
    
    # ==================== Utility ====================
    
    async def cleanup_old_data(self, guild_id: int, days: int = 90):
        """حذف البيانات القديمة"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # حذف سجلات الانضمام القديمة
        join_result = await self.join_history.delete_many({
            "guild_id": guild_id,
            "timestamp": {"$lt": cutoff_date}
        })
        
        # حذف captcha منتهية الصلاحية
        captcha_result = await self.captcha.delete_many({
            "guild_id": guild_id,
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        return {
            "join_history_deleted": join_result.deleted_count,
            "captcha_deleted": captcha_result.deleted_count
        }

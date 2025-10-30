"""
نظام التذاكر (Tickets System)
Kingdom-77 Bot v3.0

هذا الملف يحتوي على جميع عمليات نظام التذاكر
"""

import discord
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from database.tickets_schema import (
    create_ticket_document,
    create_ticket_category_document,
    create_guild_ticket_config_document,
    create_ticket_transcript_document,
    format_transcript_message,
    get_user_open_tickets_query,
    get_ticket_by_channel_query,
    get_active_tickets_query,
    validate_ticket_config
)


class TicketSystem:
    """نظام إدارة التذاكر"""
    
    def __init__(self, db):
        """
        تهيئة نظام التذاكر
        
        Args:
            db: قاعدة البيانات MongoDB
        """
        self.db = db
        self.tickets = db.tickets
        self.categories = db.ticket_categories
        self.config = db.guild_ticket_config
        self.transcripts = db.ticket_transcripts
    
    # ====================================
    # إدارة إعدادات السيرفر
    # ====================================
    
    async def get_guild_config(self, guild_id: int) -> Dict[str, Any]:
        """
        الحصول على إعدادات التذاكر للسيرفر
        
        Args:
            guild_id: معرف السيرفر
        
        Returns:
            إعدادات السيرفر
        """
        config = await self.config.find_one({"guild_id": guild_id})
        
        if not config:
            # إنشاء إعدادات افتراضية
            config = create_guild_ticket_config_document(guild_id)
            await self.config.insert_one(config)
        
        return config
    
    async def update_guild_config(
        self,
        guild_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        تحديث إعدادات التذاكر للسيرفر
        
        Args:
            guild_id: معرف السيرفر
            updates: التحديثات المطلوبة
        
        Returns:
            True إذا نجح التحديث
        """
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.config.update_one(
            {"guild_id": guild_id},
            {"$set": updates}
        )
        
        return result.modified_count > 0
    
    async def toggle_ticket_system(
        self,
        guild_id: int,
        enabled: bool
    ) -> bool:
        """تفعيل/تعطيل نظام التذاكر"""
        return await self.update_guild_config(
            guild_id,
            {"enabled": enabled}
        )
    
    # ====================================
    # إدارة الفئات (Categories)
    # ====================================
    
    async def create_category(
        self,
        guild_id: int,
        category_id: str,
        name: str,
        description: str,
        emoji: str,
        discord_category_id: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        إنشاء فئة تذاكر جديدة
        
        Args:
            guild_id: معرف السيرفر
            category_id: معرف فريد للفئة
            name: اسم الفئة
            description: وصف الفئة
            emoji: إيموجي الفئة
            discord_category_id: معرف الكاتيجوري (اختياري)
            **kwargs: معاملات إضافية
        
        Returns:
            مستند الفئة
        """
        category_doc = create_ticket_category_document(
            guild_id, category_id, name, description, emoji, discord_category_id
        )
        
        # إضافة المعاملات الإضافية
        category_doc.update(kwargs)
        
        await self.categories.insert_one(category_doc)
        return category_doc
    
    async def get_category(
        self,
        guild_id: int,
        category_id: str
    ) -> Optional[Dict[str, Any]]:
        """الحصول على فئة معينة"""
        return await self.categories.find_one({
            "guild_id": guild_id,
            "category_id": category_id
        })
    
    async def get_all_categories(
        self,
        guild_id: int,
        enabled_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        الحصول على كل فئات التذاكر
        
        Args:
            guild_id: معرف السيرفر
            enabled_only: إرجاع المفعلة فقط
        
        Returns:
            قائمة الفئات
        """
        query = {"guild_id": guild_id}
        if enabled_only:
            query["enabled"] = True
        
        return await self.categories.find(query).to_list(length=None)
    
    async def update_category(
        self,
        guild_id: int,
        category_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """تحديث فئة"""
        result = await self.categories.update_one(
            {"guild_id": guild_id, "category_id": category_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_category(
        self,
        guild_id: int,
        category_id: str
    ) -> bool:
        """حذف فئة"""
        result = await self.categories.delete_one({
            "guild_id": guild_id,
            "category_id": category_id
        })
        return result.deleted_count > 0
    
    # ====================================
    # إدارة التذاكر
    # ====================================
    
    async def create_ticket(
        self,
        guild_id: int,
        user_id: int,
        channel_id: int,
        category: str
    ) -> Dict[str, Any]:
        """
        إنشاء تذكرة جديدة
        
        Args:
            guild_id: معرف السيرفر
            user_id: معرف المستخدم
            channel_id: معرف قناة التذكرة
            category: فئة التذكرة
        
        Returns:
            مستند التذكرة
        """
        # الحصول على رقم التذكرة التالي
        config = await self.get_guild_config(guild_id)
        ticket_number = config.get("next_ticket_number", 1)
        
        # إنشاء التذكرة
        ticket_doc = create_ticket_document(
            guild_id, user_id, channel_id, category, ticket_number
        )
        
        await self.tickets.insert_one(ticket_doc)
        
        # تحديث رقم التذكرة التالي والإحصائيات
        await self.config.update_one(
            {"guild_id": guild_id},
            {
                "$inc": {
                    "next_ticket_number": 1,
                    "total_tickets_created": 1
                }
            }
        )
        
        # تحديث عداد الفئة
        await self.categories.update_one(
            {"guild_id": guild_id, "category_id": category},
            {"$inc": {"ticket_count": 1}}
        )
        
        return ticket_doc
    
    async def get_ticket(
        self,
        guild_id: int,
        channel_id: int
    ) -> Optional[Dict[str, Any]]:
        """الحصول على تذكرة من خلال معرف القناة"""
        return await self.tickets.find_one(
            get_ticket_by_channel_query(guild_id, channel_id)
        )
    
    async def get_ticket_by_number(
        self,
        guild_id: int,
        ticket_number: int
    ) -> Optional[Dict[str, Any]]:
        """الحصول على تذكرة من خلال رقمها"""
        return await self.tickets.find_one({
            "guild_id": guild_id,
            "ticket_number": ticket_number
        })
    
    async def get_user_tickets(
        self,
        guild_id: int,
        user_id: int,
        include_closed: bool = False
    ) -> List[Dict[str, Any]]:
        """
        الحصول على تذاكر المستخدم
        
        Args:
            guild_id: معرف السيرفر
            user_id: معرف المستخدم
            include_closed: تضمين التذاكر المغلقة
        
        Returns:
            قائمة التذاكر
        """
        if include_closed:
            query = {"guild_id": guild_id, "user_id": user_id}
        else:
            query = get_user_open_tickets_query(guild_id, user_id)
        
        return await self.tickets.find(query).to_list(length=None)
    
    async def count_user_open_tickets(
        self,
        guild_id: int,
        user_id: int
    ) -> int:
        """عد التذاكر المفتوحة للمستخدم"""
        return await self.tickets.count_documents(
            get_user_open_tickets_query(guild_id, user_id)
        )
    
    async def update_ticket(
        self,
        guild_id: int,
        channel_id: int,
        updates: Dict[str, Any]
    ) -> bool:
        """
        تحديث تذكرة
        
        Args:
            guild_id: معرف السيرفر
            channel_id: معرف قناة التذكرة
            updates: التحديثات
        
        Returns:
            True إذا نجح التحديث
        """
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.tickets.update_one(
            get_ticket_by_channel_query(guild_id, channel_id),
            {"$set": updates}
        )
        
        return result.modified_count > 0
    
    async def close_ticket(
        self,
        guild_id: int,
        channel_id: int,
        closed_by: int,
        reason: Optional[str] = None
    ) -> bool:
        """
        إغلاق تذكرة
        
        Args:
            guild_id: معرف السيرفر
            channel_id: معرف القناة
            closed_by: معرف من أغلق التذكرة
            reason: سبب الإغلاق (اختياري)
        
        Returns:
            True إذا نجح الإغلاق
        """
        now = datetime.utcnow()
        
        result = await self.tickets.update_one(
            get_ticket_by_channel_query(guild_id, channel_id),
            {
                "$set": {
                    "status": "closed",
                    "closed_at": now,
                    "closed_by": closed_by,
                    "close_reason": reason,
                    "updated_at": now
                }
            }
        )
        
        if result.modified_count > 0:
            # تحديث إحصائيات السيرفر
            await self.config.update_one(
                {"guild_id": guild_id},
                {"$inc": {"total_tickets_closed": 1}}
            )
        
        return result.modified_count > 0
    
    async def add_participant(
        self,
        guild_id: int,
        channel_id: int,
        user_id: int
    ) -> bool:
        """إضافة مشارك إلى التذكرة"""
        result = await self.tickets.update_one(
            get_ticket_by_channel_query(guild_id, channel_id),
            {
                "$addToSet": {"participants": user_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    async def remove_participant(
        self,
        guild_id: int,
        channel_id: int,
        user_id: int
    ) -> bool:
        """إزالة مشارك من التذكرة"""
        result = await self.tickets.update_one(
            get_ticket_by_channel_query(guild_id, channel_id),
            {
                "$pull": {"participants": user_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    
    # ====================================
    # نظام النصوص (Transcripts)
    # ====================================
    
    async def save_transcript(
        self,
        guild_id: int,
        ticket: Dict[str, Any],
        messages: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        حفظ نص محادثة التذكرة
        
        Args:
            guild_id: معرف السيرفر
            ticket: مستند التذكرة
            messages: قائمة الرسائل
        
        Returns:
            مستند النص المحفوظ
        """
        transcript_doc = create_ticket_transcript_document(
            guild_id=guild_id,
            ticket_id=str(ticket["_id"]),
            ticket_number=ticket["ticket_number"],
            user_id=ticket["user_id"],
            category=ticket["category"],
            messages=messages
        )
        
        # حساب مدة التذكرة
        if ticket.get("closed_at") and ticket.get("created_at"):
            duration = ticket["closed_at"] - ticket["created_at"]
            transcript_doc["duration_hours"] = duration.total_seconds() / 3600
        
        await self.transcripts.insert_one(transcript_doc)
        return transcript_doc
    
    async def get_transcript(
        self,
        guild_id: int,
        ticket_number: int
    ) -> Optional[Dict[str, Any]]:
        """الحصول على نص محادثة محفوظ"""
        return await self.transcripts.find_one({
            "guild_id": guild_id,
            "ticket_number": ticket_number
        })
    
    async def collect_messages_for_transcript(
        self,
        channel: discord.TextChannel,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        جمع الرسائل من قناة التذكرة
        
        Args:
            channel: قناة التذكرة
            limit: الحد الأقصى للرسائل
        
        Returns:
            قائمة الرسائل المنسقة
        """
        messages = []
        
        async for message in channel.history(limit=limit, oldest_first=True):
            # تجاهل رسائل البوت الإدارية
            if message.author.bot and not message.content:
                continue
            
            msg_data = format_transcript_message(
                author_id=message.author.id,
                author_name=str(message.author),
                content=message.content,
                timestamp=message.created_at,
                attachments=[att.url for att in message.attachments]
            )
            messages.append(msg_data)
        
        return messages
    
    # ====================================
    # دوال مساعدة
    # ====================================
    
    async def can_user_create_ticket(
        self,
        guild_id: int,
        user_id: int,
        bot=None
    ) -> tuple[bool, str]:
        """
        التحقق إذا كان المستخدم يستطيع إنشاء تذكرة
        
        Args:
            guild_id: Server ID
            user_id: User ID
            bot: Bot instance for premium check (optional)
        
        Returns:
            (يستطيع/لا يستطيع, رسالة)
        """
        config = await self.get_guild_config(guild_id)
        
        if not config.get("enabled"):
            return False, "نظام التذاكر غير مفعل في هذا السيرفر"
        
        # التحقق من عدد التذاكر المفتوحة
        open_count = await self.count_user_open_tickets(guild_id, user_id)
        
        # Check if guild has unlimited tickets (premium feature)
        has_unlimited = False
        if bot and hasattr(bot, 'premium_system') and bot.premium_system:
            try:
                has_unlimited = await bot.premium_system.has_feature(str(guild_id), "unlimited_tickets")
            except Exception:
                pass
        
        if has_unlimited:
            return True, "يمكن إنشاء تذكرة (Unlimited Tickets - Premium)"
        
        max_tickets = config.get("max_tickets_per_user", 3)
        
        if open_count >= max_tickets:
            return False, f"لديك بالفعل {open_count} تذاكر مفتوحة. الحد الأقصى هو {max_tickets} (قم بالترقية لـ Premium للحصول على عدد غير محدود)"
        
        return True, "يمكن إنشاء تذكرة"
    
    async def get_ticket_statistics(
        self,
        guild_id: int
    ) -> Dict[str, Any]:
        """الحصول على إحصائيات التذاكر"""
        config = await self.get_guild_config(guild_id)
        
        # عد التذاكر النشطة
        active_tickets = await self.tickets.count_documents(
            get_active_tickets_query(guild_id)
        )
        
        return {
            "total_created": config.get("total_tickets_created", 0),
            "total_closed": config.get("total_tickets_closed", 0),
            "currently_open": active_tickets,
            "avg_close_time_hours": config.get("average_close_time_hours", 0.0)
        }

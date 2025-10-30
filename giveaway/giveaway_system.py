"""
🎁 Giveaway System Core Logic
Kingdom-77 Bot v4.0 - Phase 5.7

نظام القرعة الشامل مع Entities System (نظام النقاط)

الميزات:
- إنشاء قرعات مخصصة بالكامل
- نظام Entities لزيادة فرص الفوز حسب الرتب
- وضعين لحساب النقاط: Cumulative (إجمالي) أو Highest (أعلى رتبة)
- شروط دخول متعددة
- إدارة الفائزين
- إحصائيات شاملة
"""

import discord
import random
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Tuple
from database.giveaway_schema import GiveawayDatabase


class GiveawaySystem:
    """نظام القرعات مع Entities"""
    
    def __init__(self, db: GiveawayDatabase, bot: discord.Client):
        self.db = db
        self.bot = bot
    
    # ===== Template Management =====
    async def create_giveaway_from_template(
        self,
        template_id: str,
        channel_id: str,
        host_id: str,
        duration_seconds: Optional[int] = None,
        schedule_datetime: Optional[datetime] = None
    ) -> Dict:
        """
        إنشاء قرعة من قالب
        
        Args:
            template_id: معرف القالب
            channel_id: قناة القرعة
            host_id: المنظّم
            duration_seconds: المدة (يستخدم من القالب إذا None)
            schedule_datetime: وقت البدء المجدول (اختياري)
        """
        # جلب القالب
        template = await self.db.get_template(template_id)
        if not template:
            raise ValueError("القالب غير موجود")
        
        # استخدام المدة من القالب إذا لم تُحدد
        if duration_seconds is None:
            duration_seconds = template.get("default_duration_seconds", 86400)
        
        # زيادة عداد الاستخدام
        await self.db.increment_template_usage(template_id)
        
        # إنشاء القرعة باستخدام بيانات القالب
        settings = {
            "emoji": template.get("emoji", "🎉"),
            "ping_role_id": template.get("ping_role_id"),
            "dm_winner": template.get("dm_winner", True),
            "show_participants": template.get("show_participants", True),
            "show_entities_info": template.get("show_entities_info", template.get("entities_enabled", False))
        }
        
        return await self.create_giveaway(
            guild_id=template["guild_id"],
            channel_id=channel_id,
            host_id=host_id,
            prize=template["prize"],
            duration_seconds=duration_seconds,
            winners_count=template["winners_count"],
            description=template.get("giveaway_description"),
            thumbnail_url=template.get("thumbnail_url"),
            image_url=template.get("image_url"),
            color=template.get("color", "#FF00FF"),
            emoji=template.get("emoji", "🎉"),
            requirements=template.get("requirements", {}),
            entities_enabled=template.get("entities_enabled", False),
            entities_mode=template.get("entities_mode", "cumulative"),
            role_entities=template.get("role_entities", []),
            settings=settings,
            footer_text=template.get("footer_text"),
            footer_icon_url=template.get("footer_icon_url")
        )
    
    # ===== Giveaway Creation =====
    async def create_giveaway(
        self,
        guild_id: str,
        channel_id: str,
        host_id: str,
        prize: str,
        duration_seconds: int,
        winners_count: int = 1,
        description: Optional[str] = None,
        thumbnail_url: Optional[str] = None,
        image_url: Optional[str] = None,
        color: str = "#FF00FF",
        emoji: str = "🎉",
        requirements: Optional[Dict] = None,
        entities_enabled: bool = False,
        entities_mode: str = "cumulative",
        role_entities: Optional[List[Dict]] = None,
        settings: Optional[Dict] = None,
        footer_text: Optional[str] = None,
        footer_icon_url: Optional[str] = None
    ) -> Dict:
        """
        إنشاء قرعة جديدة
        
        Args:
            entities_enabled: تفعيل نظام Entities
            entities_mode: وضع حساب النقاط
                - "cumulative": إجمالي نقاط جميع الرتب
                - "highest": نقاط أعلى رتبة فقط
            role_entities: قائمة الرتب مع نقاطها
                [{"role_id": "123", "points": 5}, ...]
        """
        import uuid
        
        giveaway_id = str(uuid.uuid4())
        end_time = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
        
        giveaway_data = {
            "giveaway_id": giveaway_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "message_id": None,
            "prize": prize,
            "description": description,
            "thumbnail_url": thumbnail_url,
            "image_url": image_url,
            "color": color,
            "host_id": host_id,
            "winners_count": winners_count,
            "duration_seconds": duration_seconds,
            "end_time": end_time,
            "status": "active",
            
            # Entities System
            "entities_enabled": entities_enabled,
            "entities_mode": entities_mode,
            "role_entities": role_entities or [],
            
            # Requirements
            "requirements": requirements or {},
            
            # Entries & Winners
            "entries": [],
            "winners": [],
            
            # Settings
            "settings": settings or {
                "emoji": emoji,
                "ping_role_id": None,
                "dm_winner": True,
                "show_participants": True,
                "show_entities_info": entities_enabled
            },
            
            # Timestamps
            "created_at": datetime.now(timezone.utc),
            "ended_at": None,
            "cancelled_at": None,
            
            # Stats
            "stats": {
                "total_entries": 0,
                "total_bonus_entries": 0,
                "avg_entities_points": 0.0,
                "max_entities_points": 0
            }
        }
        
        return await self.db.create_giveaway(giveaway_data)
    
    # ===== Entities Calculation =====
    def calculate_user_entities(
        self,
        member: discord.Member,
        role_entities: List[Dict],
        mode: str = "cumulative"
    ) -> int:
        """
        حساب نقاط Entities للمستخدم
        
        Args:
            member: عضو Discord
            role_entities: قائمة [{"role_id": "123", "points": 5}, ...]
            mode: "cumulative" (إجمالي) أو "highest" (أعلى رتبة)
        
        Returns:
            عدد النقاط
        """
        if not role_entities:
            return 0
        
        user_role_ids = {str(role.id) for role in member.roles}
        matching_entities = [
            re["points"]
            for re in role_entities
            if re["role_id"] in user_role_ids
        ]
        
        if not matching_entities:
            return 0
        
        if mode == "cumulative":
            # إجمالي النقاط لكل الرتب
            return sum(matching_entities)
        else:  # highest
            # أعلى نقاط رتبة واحدة فقط
            return max(matching_entities)
    
    def calculate_win_chance(self, entities_points: int) -> float:
        """
        حساب نسبة الحظ الإضافية
        
        1 نقطة = 1% زيادة في الحظ
        
        Returns:
            نسبة الحظ (0.0 - 1.0)
        """
        return min(entities_points / 100.0, 1.0)  # Max 100% bonus
    
    # ===== Entry Management =====
    async def can_user_enter(
        self,
        giveaway: Dict,
        member: discord.Member
    ) -> Tuple[bool, Optional[str]]:
        """
        التحقق من إمكانية دخول المستخدم
        
        Returns:
            (can_enter: bool, reason: str)
        """
        requirements = giveaway.get("requirements", {})
        
        # Check blacklist (guild level)
        settings = await self.db.get_settings(str(member.guild.id))
        if settings and str(member.id) in settings.get("blacklisted_users", []):
            return False, "أنت محظور من المشاركة في القرعات"
        
        # Check required roles (ANY)
        required_roles = requirements.get("required_roles", [])
        if required_roles:
            user_role_ids = {str(role.id) for role in member.roles}
            if not any(role_id in user_role_ids for role_id in required_roles):
                return False, "لا تمتلك أي من الرتب المطلوبة"
        
        # Check required roles (ALL)
        required_all_roles = requirements.get("required_all_roles", [])
        if required_all_roles:
            user_role_ids = {str(role.id) for role in member.roles}
            if not all(role_id in user_role_ids for role_id in required_all_roles):
                return False, "يجب أن تمتلك جميع الرتب المطلوبة"
        
        # Check blacklisted roles
        blacklisted_roles = requirements.get("blacklisted_roles", [])
        if blacklisted_roles:
            user_role_ids = {str(role.id) for role in member.roles}
            if any(role_id in user_role_ids for role_id in blacklisted_roles):
                return False, "لديك رتبة محظورة من المشاركة"
        
        # Check minimum level
        min_level = requirements.get("min_level")
        if min_level:
            # Get user level from leveling system
            level_data = await self.bot.db.user_levels.find_one({
                "guild_id": str(member.guild.id),
                "user_id": str(member.id)
            })
            user_level = level_data.get("level", 0) if level_data else 0
            if user_level < min_level:
                return False, f"مستواك الحالي {user_level}، يجب أن تكون مستوى {min_level} على الأقل"
        
        # Check minimum credits
        min_credits = requirements.get("min_credits")
        if min_credits:
            # Get user credits
            credits_data = await self.bot.db.user_credits.find_one({"user_id": str(member.id)})
            user_credits = credits_data.get("balance", 0) if credits_data else 0
            if user_credits < min_credits:
                return False, f"لديك {user_credits} ❄️، يجب أن تمتلك {min_credits} ❄️ على الأقل"
        
        # Check account age
        min_account_age_days = requirements.get("min_account_age_days")
        if min_account_age_days:
            account_age = (datetime.now(timezone.utc) - member.created_at).days
            if account_age < min_account_age_days:
                return False, f"عمر حسابك {account_age} يوم، يجب أن يكون {min_account_age_days} يوم على الأقل"
        
        # Check server join age
        min_server_join_days = requirements.get("min_server_join_days")
        if min_server_join_days and member.joined_at:
            join_age = (datetime.now(timezone.utc) - member.joined_at).days
            if join_age < min_server_join_days:
                return False, f"مضى {join_age} يوم على انضمامك، يجب {min_server_join_days} يوم على الأقل"
        
        return True, None
    
    async def add_entry(
        self,
        giveaway_id: str,
        member: discord.Member
    ) -> Tuple[bool, Optional[str]]:
        """
        إضافة مشارك للقرعة
        
        Returns:
            (success: bool, message: str)
        """
        giveaway = await self.db.get_giveaway(giveaway_id)
        if not giveaway:
            return False, "القرعة غير موجودة"
        
        # Check if already entered
        if await self.db.is_entered(giveaway_id, str(member.id)):
            return False, "أنت مشارك بالفعل"
        
        # Check if can enter
        can_enter, reason = await self.can_user_enter(giveaway, member)
        if not can_enter:
            return False, reason
        
        # Calculate entities points
        entities_points = 0
        if giveaway.get("entities_enabled", False):
            role_entities = giveaway.get("role_entities", [])
            entities_mode = giveaway.get("entities_mode", "cumulative")
            entities_points = self.calculate_user_entities(member, role_entities, entities_mode)
        
        # Add entry
        success = await self.db.add_entry(giveaway_id, str(member.id), entities_points)
        
        if success:
            if entities_points > 0:
                bonus_percent = entities_points
                return True, f"تم تسجيل دخولك بنجاح! 🎉\n**مكافأة Entities:** +{bonus_percent}% فرصة فوز إضافية! ⭐"
            else:
                return True, "تم تسجيل دخولك بنجاح! 🎉"
        
        return False, "حدث خطأ أثناء التسجيل"
    
    async def remove_entry(
        self,
        giveaway_id: str,
        user_id: str
    ) -> bool:
        """إزالة مشارك"""
        return await self.db.remove_entry(giveaway_id, user_id)
    
    # ===== Winner Selection =====
    def select_winners_with_entities(
        self,
        entries: List[Dict],
        winners_count: int,
        entities_enabled: bool = False
    ) -> List[Dict]:
        """
        اختيار الفائزين مع احتساب Entities
        
        كل 1 نقطة = 1 إدخال إضافي (1% فرصة أكبر)
        """
        if not entries:
            return []
        
        # إنشاء pool of entries مع bonus entries
        weighted_pool = []
        for entry in entries:
            user_id = entry["user_id"]
            # كل user له إدخال أساسي واحد
            weighted_pool.append(entry)
            
            # إذا كان entities مفعّل، أضف bonus entries
            if entities_enabled:
                bonus_entries = entry.get("bonus_entries", 0)
                # أضف نسخ إضافية من الإدخال
                for _ in range(bonus_entries):
                    weighted_pool.append(entry)
        
        # اختيار فائزين عشوائيين من الـ pool
        winners_count = min(winners_count, len(entries))  # لا يمكن اختيار أكثر من عدد المشاركين الفريدين
        
        selected_winners = []
        selected_user_ids = set()
        
        # Shuffle the pool
        random.shuffle(weighted_pool)
        
        # اختيار فائزين بدون تكرار
        for entry in weighted_pool:
            user_id = entry["user_id"]
            if user_id not in selected_user_ids:
                selected_winners.append({
                    "user_id": user_id,
                    "won_at": datetime.now(timezone.utc),
                    "entities_points": entry.get("entities_points", 0),
                    "claimed": False
                })
                selected_user_ids.add(user_id)
                
                if len(selected_winners) >= winners_count:
                    break
        
        return selected_winners
    
    async def end_giveaway(
        self,
        giveaway_id: str,
        reroll: bool = False
    ) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        إنهاء القرعة واختيار الفائزين
        
        Returns:
            (success: bool, winners: List[Dict], error_msg: str)
        """
        giveaway = await self.db.get_giveaway(giveaway_id)
        if not giveaway:
            return False, None, "القرعة غير موجودة"
        
        if not reroll and giveaway["status"] != "active":
            return False, None, "القرعة غير نشطة"
        
        entries = giveaway.get("entries", [])
        if not entries:
            return False, None, "لا يوجد مشاركون"
        
        # اختيار الفائزين
        winners = self.select_winners_with_entities(
            entries,
            giveaway["winners_count"],
            giveaway.get("entities_enabled", False)
        )
        
        if not winners:
            return False, None, "فشل اختيار الفائزين"
        
        # حفظ الفائزين
        await self.db.add_winners(giveaway_id, winners)
        
        return True, winners, None
    
    async def reroll_giveaway(
        self,
        giveaway_id: str,
        winners_count: Optional[int] = None
    ) -> Tuple[bool, Optional[List[Dict]], Optional[str]]:
        """
        إعادة اختيار الفائزين
        """
        giveaway = await self.db.get_giveaway(giveaway_id)
        if not giveaway:
            return False, None, "القرعة غير موجودة"
        
        if giveaway["status"] != "ended":
            return False, None, "لا يمكن إعادة السحب إلا للقرعات المنتهية"
        
        # استخدم عدد فائزين جديد أو الأصلي
        if winners_count:
            await self.db.update_giveaway(giveaway_id, {"winners_count": winners_count})
            giveaway["winners_count"] = winners_count
        
        # تحديث الحالة
        await self.db.update_giveaway(giveaway_id, {"status": "rerolling"})
        
        # إعادة السحب
        success, winners, error = await self.end_giveaway(giveaway_id, reroll=True)
        
        return success, winners, error
    
    # ===== Embed Builders =====
    def create_giveaway_embed(self, giveaway: Dict) -> discord.Embed:
        """إنشاء embed للقرعة"""
        color = int(giveaway.get("color", "#FF00FF").replace("#", ""), 16)
        embed = discord.Embed(
            title=f"🎉 {giveaway['prize']}",
            description=giveaway.get("description", ""),
            color=color,
            timestamp=giveaway["end_time"]
        )
        
        # Host
        embed.add_field(
            name="المنظّم",
            value=f"<@{giveaway['host_id']}>",
            inline=True
        )
        
        # Winners count
        embed.add_field(
            name="عدد الفائزين",
            value=f"{giveaway['winners_count']} فائز",
            inline=True
        )
        
        # Participants (if enabled)
        if giveaway.get("settings", {}).get("show_participants", True):
            total_entries = giveaway.get("stats", {}).get("total_entries", 0)
            embed.add_field(
                name="المشاركون",
                value=f"{total_entries} مشارك",
                inline=True
            )
        
        # Entities info (if enabled)
        if giveaway.get("entities_enabled", False) and giveaway.get("settings", {}).get("show_entities_info", True):
            role_entities = giveaway.get("role_entities", [])
            mode = giveaway.get("entities_mode", "cumulative")
            
            mode_text = "إجمالي النقاط" if mode == "cumulative" else "أعلى رتبة"
            
            entities_text = f"**نظام Entities مفعّل!** ⭐\n"
            entities_text += f"**الوضع:** {mode_text}\n"
            entities_text += f"**1 نقطة = 1% فرصة إضافية**\n\n"
            
            if role_entities:
                entities_text += "**الرتب المحددة:**\n"
                for re in role_entities[:5]:  # أول 5 رتب فقط
                    entities_text += f"<@&{re['role_id']}>: **{re['points']}** نقطة\n"
                
                if len(role_entities) > 5:
                    entities_text += f"*و {len(role_entities) - 5} رتبة إضافية...*"
            
            embed.add_field(
                name="⭐ Entities System",
                value=entities_text,
                inline=False
            )
        
        # Requirements
        requirements = giveaway.get("requirements", {})
        if any(requirements.values()):
            req_text = ""
            
            if requirements.get("required_roles"):
                req_text += "• رتبة مطلوبة (واحدة على الأقل)\n"
            if requirements.get("required_all_roles"):
                req_text += "• جميع الرتب المطلوبة\n"
            if requirements.get("min_level"):
                req_text += f"• مستوى {requirements['min_level']}+\n"
            if requirements.get("min_credits"):
                req_text += f"• {requirements['min_credits']} ❄️+\n"
            if requirements.get("min_account_age_days"):
                req_text += f"• عمر الحساب {requirements['min_account_age_days']} يوم+\n"
            if requirements.get("min_server_join_days"):
                req_text += f"• عضوية {requirements['min_server_join_days']} يوم+\n"
            
            embed.add_field(
                name="📋 الشروط",
                value=req_text,
                inline=False
            )
        
        # Thumbnail
        if giveaway.get("thumbnail_url"):
            embed.set_thumbnail(url=giveaway["thumbnail_url"])
        
        # Image
        if giveaway.get("image_url"):
            embed.set_image(url=giveaway["image_url"])
        
        # Footer
        footer_text = giveaway.get("footer_text")
        footer_icon_url = giveaway.get("footer_icon_url")
        
        if footer_text:
            embed.set_footer(text=footer_text, icon_url=footer_icon_url)
        else:
            emoji = giveaway.get("settings", {}).get("emoji", "🎉")
            embed.set_footer(text=f"تفاعل بـ {emoji} للدخول • تنتهي")
        
        return embed
    
    def create_winner_embed(self, giveaway: Dict, winners: List[Dict]) -> discord.Embed:
        """إنشاء embed للفائزين"""
        color = int(giveaway.get("color", "#FF00FF").replace("#", ""), 16)
        embed = discord.Embed(
            title=f"🎊 انتهت القرعة!",
            description=f"**الجائزة:** {giveaway['prize']}",
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Winners list
        winners_text = ""
        for i, winner in enumerate(winners, 1):
            winners_text += f"{i}. <@{winner['user_id']}>"
            
            # Show entities points if enabled
            if giveaway.get("entities_enabled", False):
                points = winner.get("entities_points", 0)
                if points > 0:
                    winners_text += f" (⭐ {points} نقطة)"
            
            winners_text += "\n"
        
        embed.add_field(
            name=f"🎉 الفائزون ({len(winners)})",
            value=winners_text,
            inline=False
        )
        
        # Stats
        stats = giveaway.get("stats", {})
        if giveaway.get("entities_enabled", False):
            stats_text = f"**المشاركون:** {stats.get('total_entries', 0)}\n"
            stats_text += f"**إدخالات إضافية:** {stats.get('total_bonus_entries', 0)}\n"
            stats_text += f"**متوسط النقاط:** {stats.get('avg_entities_points', 0):.1f}\n"
            stats_text += f"**أعلى نقاط:** {stats.get('max_entities_points', 0)}"
            
            embed.add_field(
                name="📊 إحصائيات",
                value=stats_text,
                inline=False
            )
        
        embed.set_footer(text=f"المنظّم: {giveaway['host_id']}")
        
        return embed

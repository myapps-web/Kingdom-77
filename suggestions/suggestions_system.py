"""
Kingdom-77 Bot - Suggestions System Core
نظام الاقتراحات المتقدم - المنطق الأساسي

Features:
- Create, edit, delete suggestions
- Voting system (upvote, downvote, neutral)
- Staff review and status management
- Comments system
- Anonymous suggestions
- Notifications
"""

import discord
from discord import Embed, Color
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any, Tuple

from database.suggestions_schema import SuggestionsSchema, SuggestionStatus


class SuggestionsSystem:
    """Core system for managing suggestions"""
    
    def __init__(self, db, bot):
        self.db = db
        self.bot = bot
        self.schema = SuggestionsSchema(db)
        
        # Cooldown tracking (in-memory)
        self.cooldowns: Dict[str, datetime] = {}
    
    async def initialize(self):
        """تهيئة النظام"""
        await self.schema.setup_indexes()
    
    # ============= Suggestion Creation =============
    
    async def create_suggestion(
        self,
        guild: discord.Guild,
        user: discord.Member,
        title: str,
        description: str,
        anonymous: bool = False,
        attachments: List[str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """إنشاء اقتراح جديد"""
        
        # الحصول على الإعدادات
        settings = await self.schema.get_settings(guild.id)
        
        if not settings["enabled"]:
            return False, "❌ نظام الاقتراحات معطل في هذا السيرفر", None
        
        # التحقق من Cooldown
        cooldown_key = f"{guild.id}:{user.id}"
        if cooldown_key in self.cooldowns:
            time_left = (self.cooldowns[cooldown_key] - datetime.utcnow()).total_seconds()
            if time_left > 0:
                minutes = int(time_left / 60)
                return False, f"⏰ يرجى الانتظار {minutes} دقيقة قبل تقديم اقتراح آخر", None
        
        # التحقق من عدد الاقتراحات
        user_count = await self.schema.get_user_suggestions_count(guild.id, user.id)
        
        # Check premium status
        is_premium = False
        if hasattr(self.bot, 'premium_system'):
            is_premium = await self.bot.premium_system.check_premium(guild.id)
        
        max_suggestions = settings["max_suggestions_per_user"]
        if is_premium:
            max_suggestions = 999  # Unlimited for premium
        
        if user_count >= max_suggestions:
            return False, f"❌ لقد وصلت للحد الأقصى ({max_suggestions} اقتراح)", None
        
        # التحقق من طول الاقتراح
        if len(description) < settings["min_suggestion_length"]:
            return False, f"❌ الوصف قصير جداً (الحد الأدنى {settings['min_suggestion_length']} حرف)", None
        
        if len(description) > settings["max_suggestion_length"]:
            return False, f"❌ الوصف طويل جداً (الحد الأقصى {settings['max_suggestion_length']} حرف)", None
        
        # إنشاء الاقتراح
        suggestion = await self.schema.create_suggestion(
            guild_id=guild.id,
            user_id=user.id,
            title=title,
            description=description,
            anonymous=anonymous,
            attachments=attachments
        )
        
        # تحديث Cooldown
        if settings["cooldown_minutes"] > 0:
            self.cooldowns[cooldown_key] = datetime.utcnow() + timedelta(minutes=settings["cooldown_minutes"])
        
        # إرسال الاقتراح إلى القناة
        if settings["suggestions_channel_id"]:
            try:
                channel = guild.get_channel(int(settings["suggestions_channel_id"]))
                if channel:
                    embed = self._create_suggestion_embed(suggestion, user, settings, anonymous)
                    message = await channel.send(embed=embed)
                    
                    # إضافة ريأكشنز التصويت
                    if settings["allow_voting"]:
                        await message.add_reaction(settings["voting_emojis"]["upvote"])
                        await message.add_reaction(settings["voting_emojis"]["downvote"])
                        await message.add_reaction(settings["voting_emojis"]["neutral"])
                    
                    # تحديث معلومات الرسالة
                    await self.schema.update_suggestion_message(
                        guild.id,
                        suggestion["suggestion_id"],
                        message.id,
                        channel.id
                    )
            except Exception as e:
                print(f"Error posting suggestion: {e}")
        
        # إرسال إشعار للمستخدم
        if settings["dm_notifications"]:
            try:
                await user.send(
                    f"✅ تم إرسال اقتراحك #{suggestion['suggestion_id']} بنجاح!\n"
                    f"**العنوان:** {title}\n"
                    f"ستتم مراجعته من قبل الإدارة قريباً."
                )
            except:
                pass  # User has DMs disabled
        
        return True, f"✅ تم إرسال اقتراحك بنجاح! (#{suggestion['suggestion_id']})", suggestion
    
    def _create_suggestion_embed(
        self,
        suggestion: Dict[str, Any],
        user: discord.Member,
        settings: Dict[str, Any],
        anonymous: bool = False
    ) -> Embed:
        """إنشاء embed للاقتراح"""
        
        # اللون حسب الحالة
        color_map = {
            "pending": Color.yellow(),
            "approved": Color.green(),
            "denied": Color.red(),
            "implemented": Color.blue(),
            "duplicate": Color.orange(),
            "considering": Color.purple()
        }
        
        status_emoji = {
            "pending": "⏳",
            "approved": "✅",
            "denied": "❌",
            "implemented": "🎉",
            "duplicate": "🔁",
            "considering": "🤔"
        }
        
        status = suggestion["status"]
        color = color_map.get(status, Color.blurple())
        
        embed = Embed(
            title=f"اقتراح #{suggestion['suggestion_id']}: {suggestion['title']}",
            description=suggestion['description'],
            color=color,
            timestamp=suggestion['created_at']
        )
        
        # إضافة معلومات المُقترح
        if not anonymous and settings["show_author"]:
            embed.set_author(
                name=user.display_name,
                icon_url=user.display_avatar.url
            )
        elif anonymous:
            embed.set_author(name="عضو مجهول")
        
        # إضافة الحالة
        status_text = {
            "pending": "قيد المراجعة",
            "approved": "موافق عليه",
            "denied": "مرفوض",
            "implemented": "تم التنفيذ",
            "duplicate": "مكرر",
            "considering": "قيد النظر"
        }
        
        embed.add_field(
            name="الحالة",
            value=f"{status_emoji[status]} {status_text[status]}",
            inline=True
        )
        
        # إضافة عدد الأصوات
        if settings["show_vote_count"]:
            votes_text = (
                f"👍 {suggestion['upvotes']} | "
                f"👎 {suggestion['downvotes']} | "
                f"🤷 {suggestion['neutral_votes']}"
            )
            embed.add_field(
                name="التصويت",
                value=votes_text,
                inline=True
            )
        
        # إضافة رد الإدارة
        if suggestion.get("staff_response"):
            embed.add_field(
                name="📝 رد الإدارة",
                value=suggestion["staff_response"],
                inline=False
            )
        
        # إضافة المرفقات
        if suggestion.get("attachments"):
            attachments_text = "\n".join([f"[مرفق {i+1}]({url})" for i, url in enumerate(suggestion["attachments"])])
            embed.add_field(
                name="📎 المرفقات",
                value=attachments_text,
                inline=False
            )
        
        embed.set_footer(text=f"السيرفر: {suggestion['guild_id']}")
        
        return embed
    
    # ============= Voting System =============
    
    async def vote(
        self,
        guild_id: int,
        suggestion_id: int,
        user_id: int,
        vote_type: str
    ) -> Tuple[bool, str]:
        """التصويت على اقتراح"""
        
        # التحقق من الإعدادات
        settings = await self.schema.get_settings(guild_id)
        if not settings["allow_voting"]:
            return False, "❌ التصويت معطل في هذا السيرفر"
        
        # التحقق من وجود الاقتراح
        suggestion = await self.schema.get_suggestion(guild_id, suggestion_id)
        if not suggestion:
            return False, "❌ الاقتراح غير موجود"
        
        # لا يمكن التصويت على الاقتراحات المنتهية
        if suggestion["status"] in ["denied", "duplicate"]:
            return False, "❌ لا يمكن التصويت على اقتراح مرفوض أو مكرر"
        
        # إضافة/تحديث الصوت
        result = await self.schema.add_vote(guild_id, suggestion_id, user_id, vote_type)
        
        vote_emoji = settings["voting_emojis"].get(vote_type, "✅")
        
        if result["changed"]:
            if result["old_vote"]:
                return True, f"{vote_emoji} تم تحديث صوتك"
            else:
                return True, f"{vote_emoji} تم تسجيل صوتك"
        
        return False, "❌ حدث خطأ أثناء التصويت"
    
    # ============= Staff Management =============
    
    async def review_suggestion(
        self,
        guild_id: int,
        suggestion_id: int,
        staff_id: int,
        status: str,
        response: Optional[str] = None
    ) -> Tuple[bool, str]:
        """مراجعة اقتراح من الإدارة"""
        
        # التحقق من صحة الحالة
        valid_statuses = [s.value for s in SuggestionStatus]
        if status not in valid_statuses:
            return False, f"❌ حالة غير صحيحة. الحالات المتاحة: {', '.join(valid_statuses)}"
        
        # التحقق من وجود الاقتراح
        suggestion = await self.schema.get_suggestion(guild_id, suggestion_id)
        if not suggestion:
            return False, "❌ الاقتراح غير موجود"
        
        # تحديث الحالة
        success = await self.schema.update_suggestion_status(
            guild_id,
            suggestion_id,
            status,
            staff_id,
            response
        )
        
        if not success:
            return False, "❌ فشل تحديث الاقتراح"
        
        # إرسال إشعار للمستخدم
        settings = await self.schema.get_settings(guild_id)
        if settings["dm_notifications"] and not suggestion["anonymous"]:
            try:
                guild = self.bot.get_guild(guild_id)
                user = guild.get_member(int(suggestion["user_id"]))
                
                if user:
                    status_text = {
                        "approved": "تمت الموافقة عليه ✅",
                        "denied": "تم رفضه ❌",
                        "implemented": "تم تنفيذه 🎉",
                        "duplicate": "تم اعتباره مكرراً 🔁",
                        "considering": "قيد النظر 🤔"
                    }
                    
                    message = f"📢 تحديث حالة اقتراحك #{suggestion_id}:\n"
                    message += f"**الحالة الجديدة:** {status_text.get(status, status)}\n"
                    
                    if response:
                        message += f"\n**رد الإدارة:**\n{response}"
                    
                    await user.send(message)
            except:
                pass
        
        # تحديث رسالة الاقتراح
        if suggestion.get("message_id") and suggestion.get("channel_id"):
            try:
                guild = self.bot.get_guild(guild_id)
                channel = guild.get_channel(int(suggestion["channel_id"]))
                
                if channel:
                    message = await channel.fetch_message(int(suggestion["message_id"]))
                    
                    # تحديث الـ embed
                    updated_suggestion = await self.schema.get_suggestion(guild_id, suggestion_id)
                    user = guild.get_member(int(suggestion["user_id"]))
                    
                    if user:
                        embed = self._create_suggestion_embed(
                            updated_suggestion,
                            user,
                            settings,
                            suggestion["anonymous"]
                        )
                        await message.edit(embed=embed)
            except:
                pass
        
        return True, f"✅ تم تحديث حالة الاقتراح #{suggestion_id} إلى: {status}"
    
    # ============= Comments =============
    
    async def add_comment(
        self,
        guild_id: int,
        suggestion_id: int,
        user_id: int,
        content: str
    ) -> Tuple[bool, str]:
        """إضافة تعليق"""
        
        # التحقق من وجود الاقتراح
        suggestion = await self.schema.get_suggestion(guild_id, suggestion_id)
        if not suggestion:
            return False, "❌ الاقتراح غير موجود"
        
        # إضافة التعليق
        comment = await self.schema.add_comment(guild_id, suggestion_id, user_id, content)
        
        return True, "✅ تم إضافة تعليقك"
    
    # ============= Utilities =============
    
    async def get_suggestion_with_details(
        self,
        guild_id: int,
        suggestion_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """الحصول على اقتراح مع تفاصيل إضافية"""
        
        suggestion = await self.schema.get_suggestion(guild_id, suggestion_id)
        if not suggestion:
            return None
        
        # إضافة صوت المستخدم
        if user_id:
            user_vote = await self.schema.get_user_vote(guild_id, suggestion_id, user_id)
            suggestion["user_vote"] = user_vote
        
        # إضافة التعليقات
        comments = await self.schema.get_comments(guild_id, suggestion_id)
        suggestion["comments"] = comments
        suggestion["comments_count"] = len(comments)
        
        return suggestion
    
    async def check_staff_permission(
        self,
        guild: discord.Guild,
        member: discord.Member
    ) -> bool:
        """التحقق من صلاحيات الإدارة"""
        
        # Administrators always have permission
        if member.guild_permissions.administrator:
            return True
        
        # Check staff roles
        settings = await self.schema.get_settings(guild.id)
        staff_role_ids = settings.get("staff_role_ids", [])
        
        member_role_ids = [str(role.id) for role in member.roles]
        
        return any(role_id in member_role_ids for role_id in staff_role_ids)
    
    async def get_suggestions_summary(
        self,
        guild_id: int
    ) -> str:
        """ملخص الاقتراحات"""
        
        stats = await self.schema.get_statistics(guild_id)
        
        summary = "📊 **ملخص الاقتراحات:**\n\n"
        summary += f"📝 **إجمالي الاقتراحات:** {stats['total_suggestions']}\n"
        summary += f"🗳️ **إجمالي الأصوات:** {stats['total_votes']}\n\n"
        
        summary += "**التوزيع حسب الحالة:**\n"
        status_names = {
            "pending": "⏳ قيد المراجعة",
            "approved": "✅ موافق عليه",
            "denied": "❌ مرفوض",
            "implemented": "🎉 تم التنفيذ",
            "duplicate": "🔁 مكرر",
            "considering": "🤔 قيد النظر"
        }
        
        for status, count in stats["status_breakdown"].items():
            status_name = status_names.get(status, status)
            summary += f"{status_name}: {count}\n"
        
        return summary

"""
Kingdom-77 Bot - Suggestions Cog
Discord Slash Commands for Suggestions System

Commands:
- /suggest - إرسال اقتراح جديد
- /suggestion view - عرض اقتراح محدد
- /suggestion delete - حذف اقتراح
- /suggestion vote - التصويت على اقتراح
- /suggestion comment - إضافة تعليق
- /suggestion list - عرض قائمة الاقتراحات
- /suggestion leaderboard - لوحة المتصدرين
- /suggestion stats - إحصائيات الاقتراحات

Staff Commands:
- /suggestion review - مراجعة اقتراح
- /suggestion approve - الموافقة على اقتراح
- /suggestion deny - رفض اقتراح
- /suggestion implement - وضع علامة "تم التنفيذ"

Admin Commands:
- /suggestion setup - إعداد النظام
- /suggestion config - تعديل الإعدادات
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
from datetime import datetime

from suggestions.suggestions_system import SuggestionsSystem
from database.suggestions_schema import SuggestionStatus


class SuggestModal(discord.ui.Modal):
    """Modal لإرسال اقتراح جديد"""
    
    def __init__(self, suggestion_system: SuggestionsSystem, anonymous: bool = False):
        super().__init__(title="إرسال اقتراح جديد")
        self.suggestion_system = suggestion_system
        self.anonymous = anonymous
        
        self.title_input = discord.ui.TextInput(
            label="عنوان الاقتراح",
            placeholder="عنوان قصير وواضح للاقتراح",
            max_length=100,
            required=True
        )
        self.add_item(self.title_input)
        
        self.description_input = discord.ui.TextInput(
            label="وصف الاقتراح",
            placeholder="اشرح اقتراحك بالتفصيل...",
            style=discord.TextStyle.paragraph,
            max_length=2000,
            required=True
        )
        self.add_item(self.description_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        title = self.title_input.value
        description = self.description_input.value
        
        success, message, suggestion = await self.suggestion_system.create_suggestion(
            guild=interaction.guild,
            user=interaction.user,
            title=title,
            description=description,
            anonymous=self.anonymous
        )
        
        if success:
            embed = discord.Embed(
                title="✅ تم إرسال الاقتراح",
                description=message,
                color=discord.Color.green()
            )
            embed.add_field(name="العنوان", value=title, inline=False)
            embed.add_field(name="رقم الاقتراح", value=f"#{suggestion['suggestion_id']}", inline=True)
            
            if self.anonymous:
                embed.add_field(name="وضع الاقتراح", value="🕵️ مجهول", inline=True)
        else:
            embed = discord.Embed(
                title="❌ فشل إرسال الاقتراح",
                description=message,
                color=discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)


class ReviewModal(discord.ui.Modal):
    """Modal لمراجعة اقتراح"""
    
    def __init__(self, suggestion_system: SuggestionsSystem, guild_id: int, suggestion_id: int, status: str):
        super().__init__(title=f"مراجعة الاقتراح #{suggestion_id}")
        self.suggestion_system = suggestion_system
        self.guild_id = guild_id
        self.suggestion_id = suggestion_id
        self.status = status
        
        self.response_input = discord.ui.TextInput(
            label="رد الإدارة",
            placeholder="اكتب رداً على الاقتراح (اختياري)",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=False
        )
        self.add_item(self.response_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        response = self.response_input.value or None
        
        success, message = await self.suggestion_system.review_suggestion(
            guild_id=self.guild_id,
            suggestion_id=self.suggestion_id,
            staff_id=interaction.user.id,
            status=self.status,
            response=response
        )
        
        color = discord.Color.green() if success else discord.Color.red()
        embed = discord.Embed(
            title="مراجعة الاقتراح",
            description=message,
            color=color
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)


class SuggestionsCog(commands.Cog):
    """Suggestions System Commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.suggestion_system: Optional[SuggestionsSystem] = None
    
    async def cog_load(self):
        """تهيئة النظام عند تحميل الـ Cog"""
        if hasattr(self.bot, 'db'):
            self.suggestion_system = SuggestionsSystem(self.bot.db, self.bot)
            await self.suggestion_system.initialize()
    
    # ============= User Commands =============
    
    @app_commands.command(name="suggest", description="إرسال اقتراح جديد")
    @app_commands.describe(
        anonymous="إرسال الاقتراح بشكل مجهول"
    )
    async def suggest(
        self,
        interaction: discord.Interaction,
        anonymous: bool = False
    ):
        """إرسال اقتراح جديد"""
        
        modal = SuggestModal(self.suggestion_system, anonymous)
        await interaction.response.send_modal(modal)
    
    suggestion_group = app_commands.Group(name="suggestion", description="إدارة الاقتراحات")
    
    @suggestion_group.command(name="view", description="عرض اقتراح محدد")
    @app_commands.describe(suggestion_id="رقم الاقتراح")
    async def view_suggestion(
        self,
        interaction: discord.Interaction,
        suggestion_id: int
    ):
        """عرض تفاصيل اقتراح"""
        await interaction.response.defer()
        
        suggestion = await self.suggestion_system.get_suggestion_with_details(
            interaction.guild.id,
            suggestion_id,
            interaction.user.id
        )
        
        if not suggestion:
            embed = discord.Embed(
                title="❌ اقتراح غير موجود",
                description=f"لا يوجد اقتراح برقم #{suggestion_id}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # إنشاء Embed للاقتراح
        settings = await self.suggestion_system.schema.get_settings(interaction.guild.id)
        
        # الحصول على المستخدم
        user = interaction.guild.get_member(int(suggestion["user_id"]))
        
        embed = self.suggestion_system._create_suggestion_embed(
            suggestion,
            user if user else interaction.guild.me,
            settings,
            suggestion["anonymous"]
        )
        
        # إضافة معلومات إضافية
        if suggestion.get("user_vote"):
            vote_emoji = {"upvote": "👍", "downvote": "👎", "neutral": "🤷"}
            embed.add_field(
                name="صوتك",
                value=vote_emoji.get(suggestion["user_vote"], ""),
                inline=True
            )
        
        if suggestion.get("comments_count", 0) > 0:
            embed.add_field(
                name="التعليقات",
                value=f"💬 {suggestion['comments_count']} تعليق",
                inline=True
            )
        
        await interaction.followup.send(embed=embed)
    
    @suggestion_group.command(name="delete", description="حذف اقتراحك")
    @app_commands.describe(suggestion_id="رقم الاقتراح")
    async def delete_suggestion(
        self,
        interaction: discord.Interaction,
        suggestion_id: int
    ):
        """حذف اقتراح"""
        await interaction.response.defer(ephemeral=True)
        
        # التحقق من ملكية الاقتراح
        suggestion = await self.suggestion_system.schema.get_suggestion(
            interaction.guild.id,
            suggestion_id
        )
        
        if not suggestion:
            await interaction.followup.send("❌ الاقتراح غير موجود", ephemeral=True)
            return
        
        # التحقق من الصلاحيات
        is_owner = str(interaction.user.id) == suggestion["user_id"]
        is_staff = await self.suggestion_system.check_staff_permission(
            interaction.guild,
            interaction.user
        )
        
        if not (is_owner or is_staff):
            await interaction.followup.send("❌ ليس لديك صلاحية حذف هذا الاقتراح", ephemeral=True)
            return
        
        # حذف الاقتراح
        success = await self.suggestion_system.schema.delete_suggestion(
            interaction.guild.id,
            suggestion_id
        )
        
        if success:
            embed = discord.Embed(
                title="✅ تم الحذف",
                description=f"تم حذف الاقتراح #{suggestion_id}",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ فشل الحذف",
                description="حدث خطأ أثناء حذف الاقتراح",
                color=discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @suggestion_group.command(name="vote", description="التصويت على اقتراح")
    @app_commands.describe(
        suggestion_id="رقم الاقتراح",
        vote="نوع التصويت"
    )
    @app_commands.choices(vote=[
        app_commands.Choice(name="👍 موافق", value="upvote"),
        app_commands.Choice(name="👎 غير موافق", value="downvote"),
        app_commands.Choice(name="🤷 محايد", value="neutral")
    ])
    async def vote_suggestion(
        self,
        interaction: discord.Interaction,
        suggestion_id: int,
        vote: str
    ):
        """التصويت على اقتراح"""
        await interaction.response.defer(ephemeral=True)
        
        success, message = await self.suggestion_system.vote(
            interaction.guild.id,
            suggestion_id,
            interaction.user.id,
            vote
        )
        
        color = discord.Color.green() if success else discord.Color.red()
        embed = discord.Embed(
            title="التصويت",
            description=message,
            color=color
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @suggestion_group.command(name="comment", description="إضافة تعليق على اقتراح")
    @app_commands.describe(
        suggestion_id="رقم الاقتراح",
        comment="التعليق"
    )
    async def comment_suggestion(
        self,
        interaction: discord.Interaction,
        suggestion_id: int,
        comment: str
    ):
        """إضافة تعليق"""
        await interaction.response.defer(ephemeral=True)
        
        if len(comment) < 5:
            await interaction.followup.send("❌ التعليق قصير جداً (الحد الأدنى 5 أحرف)", ephemeral=True)
            return
        
        success, message = await self.suggestion_system.add_comment(
            interaction.guild.id,
            suggestion_id,
            interaction.user.id,
            comment
        )
        
        color = discord.Color.green() if success else discord.Color.red()
        embed = discord.Embed(
            title="تعليق",
            description=message,
            color=color
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @suggestion_group.command(name="list", description="عرض قائمة الاقتراحات")
    @app_commands.describe(
        status="تصفية حسب الحالة",
        user="عرض اقتراحات عضو محدد"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="⏳ قيد المراجعة", value="pending"),
        app_commands.Choice(name="✅ موافق عليه", value="approved"),
        app_commands.Choice(name="❌ مرفوض", value="denied"),
        app_commands.Choice(name="🎉 تم التنفيذ", value="implemented"),
        app_commands.Choice(name="🔁 مكرر", value="duplicate"),
        app_commands.Choice(name="🤔 قيد النظر", value="considering")
    ])
    async def list_suggestions(
        self,
        interaction: discord.Interaction,
        status: Optional[str] = None,
        user: Optional[discord.Member] = None
    ):
        """عرض قائمة الاقتراحات"""
        await interaction.response.defer()
        
        user_id = user.id if user else None
        
        suggestions = await self.suggestion_system.schema.list_suggestions(
            interaction.guild.id,
            status=status,
            user_id=user_id,
            limit=25
        )
        
        if not suggestions:
            embed = discord.Embed(
                title="📝 قائمة الاقتراحات",
                description="لا توجد اقتراحات",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # إنشاء Embed للقائمة
        embed = discord.Embed(
            title="📝 قائمة الاقتراحات",
            color=discord.Color.blue()
        )
        
        if status:
            status_names = {
                "pending": "⏳ قيد المراجعة",
                "approved": "✅ موافق عليه",
                "denied": "❌ مرفوض",
                "implemented": "🎉 تم التنفيذ",
                "duplicate": "🔁 مكرر",
                "considering": "🤔 قيد النظر"
            }
            embed.description = f"الحالة: {status_names.get(status, status)}"
        
        if user:
            embed.description = f"اقتراحات {user.mention}"
        
        # إضافة الاقتراحات
        for suggestion in suggestions[:10]:  # أول 10 فقط
            status_emoji = {
                "pending": "⏳",
                "approved": "✅",
                "denied": "❌",
                "implemented": "🎉",
                "duplicate": "🔁",
                "considering": "🤔"
            }
            
            votes = f"👍 {suggestion['upvotes']} 👎 {suggestion['downvotes']}"
            
            embed.add_field(
                name=f"{status_emoji.get(suggestion['status'], '')} #{suggestion['suggestion_id']}: {suggestion['title'][:50]}",
                value=f"{votes}\n{suggestion['description'][:100]}...",
                inline=False
            )
        
        if len(suggestions) > 10:
            embed.set_footer(text=f"عرض 10 من {len(suggestions)} اقتراح")
        
        await interaction.followup.send(embed=embed)
    
    @suggestion_group.command(name="leaderboard", description="لوحة متصدري الاقتراحات")
    @app_commands.describe(sort_by="الترتيب حسب")
    @app_commands.choices(sort_by=[
        app_commands.Choice(name="📝 عدد الاقتراحات", value="suggestions"),
        app_commands.Choice(name="👍 عدد الأصوات", value="upvotes")
    ])
    async def leaderboard(
        self,
        interaction: discord.Interaction,
        sort_by: str = "suggestions"
    ):
        """لوحة المتصدرين"""
        await interaction.response.defer()
        
        leaderboard = await self.suggestion_system.schema.get_leaderboard(
            interaction.guild.id,
            sort_by=sort_by,
            limit=10
        )
        
        if not leaderboard:
            embed = discord.Embed(
                title="🏆 لوحة المتصدرين",
                description="لا توجد بيانات بعد",
                color=discord.Color.gold()
            )
            await interaction.followup.send(embed=embed)
            return
        
        # إنشاء Embed
        embed = discord.Embed(
            title="🏆 لوحة متصدري الاقتراحات",
            color=discord.Color.gold(),
            timestamp=datetime.utcnow()
        )
        
        sort_name = "عدد الاقتراحات" if sort_by == "suggestions" else "عدد الأصوات الموافقة"
        embed.description = f"**الترتيب حسب:** {sort_name}"
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, entry in enumerate(leaderboard[:10], 1):
            user = interaction.guild.get_member(int(entry["user_id"]))
            user_name = user.mention if user else f"User {entry['user_id']}"
            
            medal = medals[i-1] if i <= 3 else f"**{i}.**"
            
            value = (
                f"📝 {entry['suggestions_count']} اقتراح\n"
                f"👍 {entry['total_upvotes']} | 👎 {entry['total_downvotes']}\n"
                f"✅ {entry['approved_count']} موافق | "
                f"🎉 {entry['implemented_count']} منفذ\n"
                f"💯 النقاط: {entry['score']}"
            )
            
            embed.add_field(
                name=f"{medal} {user_name}",
                value=value,
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
    
    @suggestion_group.command(name="stats", description="إحصائيات الاقتراحات")
    async def stats(self, interaction: discord.Interaction):
        """عرض إحصائيات شاملة"""
        await interaction.response.defer()
        
        summary = await self.suggestion_system.get_suggestions_summary(interaction.guild.id)
        
        embed = discord.Embed(
            title="📊 إحصائيات الاقتراحات",
            description=summary,
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        await interaction.followup.send(embed=embed)
    
    # ============= Staff Commands =============
    
    @suggestion_group.command(name="review", description="[إدارة] مراجعة اقتراح")
    @app_commands.describe(
        suggestion_id="رقم الاقتراح",
        status="الحالة الجديدة"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="✅ موافق عليه", value="approved"),
        app_commands.Choice(name="❌ مرفوض", value="denied"),
        app_commands.Choice(name="🎉 تم التنفيذ", value="implemented"),
        app_commands.Choice(name="🔁 مكرر", value="duplicate"),
        app_commands.Choice(name="🤔 قيد النظر", value="considering")
    ])
    @app_commands.checks.has_permissions(manage_guild=True)
    async def review(
        self,
        interaction: discord.Interaction,
        suggestion_id: int,
        status: str
    ):
        """مراجعة اقتراح"""
        
        # التحقق من صلاحيات الإدارة
        is_staff = await self.suggestion_system.check_staff_permission(
            interaction.guild,
            interaction.user
        )
        
        if not is_staff:
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية مراجعة الاقتراحات",
                ephemeral=True
            )
            return
        
        modal = ReviewModal(
            self.suggestion_system,
            interaction.guild.id,
            suggestion_id,
            status
        )
        await interaction.response.send_modal(modal)
    
    # ============= Admin Commands =============
    
    @suggestion_group.command(name="setup", description="[مدير] إعداد نظام الاقتراحات")
    @app_commands.describe(
        suggestions_channel="قناة الاقتراحات",
        review_channel="قناة المراجعة (للإدارة)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(
        self,
        interaction: discord.Interaction,
        suggestions_channel: discord.TextChannel,
        review_channel: Optional[discord.TextChannel] = None
    ):
        """إعداد النظام"""
        await interaction.response.defer(ephemeral=True)
        
        settings_data = {
            "enabled": True,
            "suggestions_channel_id": str(suggestions_channel.id),
        }
        
        if review_channel:
            settings_data["review_channel_id"] = str(review_channel.id)
        
        success = await self.suggestion_system.schema.update_settings(
            interaction.guild.id,
            settings_data
        )
        
        if success:
            embed = discord.Embed(
                title="✅ تم إعداد النظام",
                description=(
                    f"**قناة الاقتراحات:** {suggestions_channel.mention}\n"
                    f"**قناة المراجعة:** {review_channel.mention if review_channel else 'غير محددة'}"
                ),
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="❌ فشل الإعداد",
                description="حدث خطأ أثناء إعداد النظام",
                color=discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @suggestion_group.command(name="config", description="[مدير] تعديل إعدادات النظام")
    @app_commands.describe(
        allow_voting="السماح بالتصويت",
        allow_anonymous="السماح بالاقتراحات المجهولة",
        cooldown_minutes="مدة الانتظار بين الاقتراحات (بالدقائق)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def config(
        self,
        interaction: discord.Interaction,
        allow_voting: Optional[bool] = None,
        allow_anonymous: Optional[bool] = None,
        cooldown_minutes: Optional[int] = None
    ):
        """تعديل الإعدادات"""
        await interaction.response.defer(ephemeral=True)
        
        settings_data = {}
        
        if allow_voting is not None:
            settings_data["allow_voting"] = allow_voting
        
        if allow_anonymous is not None:
            settings_data["allow_anonymous"] = allow_anonymous
        
        if cooldown_minutes is not None:
            settings_data["cooldown_minutes"] = cooldown_minutes
        
        if not settings_data:
            await interaction.followup.send("❌ لم تقم بتحديد أي إعدادات", ephemeral=True)
            return
        
        success = await self.suggestion_system.schema.update_settings(
            interaction.guild.id,
            settings_data
        )
        
        if success:
            embed = discord.Embed(
                title="✅ تم تحديث الإعدادات",
                color=discord.Color.green()
            )
            
            for key, value in settings_data.items():
                embed.add_field(name=key, value=str(value), inline=False)
        else:
            embed = discord.Embed(
                title="❌ فشل التحديث",
                description="حدث خطأ أثناء تحديث الإعدادات",
                color=discord.Color.red()
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    """تحميل الـ Cog"""
    await bot.add_cog(SuggestionsCog(bot))

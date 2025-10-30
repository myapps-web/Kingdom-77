"""
🎁 Giveaway Commands
Kingdom-77 Bot v4.0 - Phase 5.7

أوامر Discord لنظام القرعات مع Entities System
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
from datetime import datetime, timedelta, timezone
from typing import Optional, List
import asyncio

from giveaway.giveaway_system import GiveawaySystem
from database.giveaway_schema import GiveawayDatabase


class TemplateCreateModal(discord.ui.Modal, title="إنشاء قالب قرعة 📋"):
    """Modal لإنشاء قالب"""
    
    name = discord.ui.TextInput(
        label="اسم القالب",
        placeholder="مثال: قرعة Nitro أسبوعية",
        max_length=100,
        required=True
    )
    
    prize = discord.ui.TextInput(
        label="الجائزة",
        placeholder="مثال: Nitro Classic لمدة شهر",
        max_length=256,
        required=True
    )
    
    winners = discord.ui.TextInput(
        label="عدد الفائزين",
        placeholder="1",
        default="1",
        max_length=2,
        required=True
    )
    
    duration = discord.ui.TextInput(
        label="المدة الافتراضية",
        placeholder="مثال: 1d, 12h, 30m",
        max_length=20,
        required=True
    )
    
    description = discord.ui.TextInput(
        label="وصف القالب (اختياري)",
        placeholder="وصف للقالب...",
        style=discord.TextStyle.paragraph,
        max_length=500,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class TemplateEditModal(discord.ui.Modal, title="تعديل قالب 📝"):
    """Modal لتعديل قالب"""
    
    prize = discord.ui.TextInput(
        label="الجائزة",
        placeholder="مثال: Nitro Classic لمدة شهر",
        max_length=256,
        required=False
    )
    
    giveaway_description = discord.ui.TextInput(
        label="وصف القرعة (اختياري)",
        placeholder="وصف الجائزة...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=False
    )
    
    footer_text = discord.ui.TextInput(
        label="نص الذيل (اختياري)",
        placeholder="مثال: حظاً موفقاً للجميع!",
        max_length=200,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class GiveawayModal(discord.ui.Modal, title="إنشاء قرعة جديدة 🎁"):
    """Modal لإنشاء قرعة"""
    
    prize = discord.ui.TextInput(
        label="الجائزة",
        placeholder="مثال: Nitro Classic لمدة شهر",
        max_length=256,
        required=True
    )
    
    duration = discord.ui.TextInput(
        label="المدة",
        placeholder="مثال: 1d, 12h, 30m (يوم، ساعة، دقيقة)",
        max_length=20,
        required=True
    )
    
    winners = discord.ui.TextInput(
        label="عدد الفائزين",
        placeholder="1",
        default="1",
        max_length=2,
        required=True
    )
    
    description = discord.ui.TextInput(
        label="الوصف (اختياري)",
        placeholder="وصف الجائزة...",
        style=discord.TextStyle.paragraph,
        max_length=1000,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class EntitiesSetupModal(discord.ui.Modal, title="إعداد Entities للرتب ⭐"):
    """Modal لإعداد نقاط Entities للرتب"""
    
    mode = discord.ui.TextInput(
        label="وضع الحساب",
        placeholder="cumulative (إجمالي) أو highest (أعلى رتبة)",
        default="cumulative",
        max_length=20,
        required=True
    )
    
    role1 = discord.ui.TextInput(
        label="الرتبة الأولى (mention أو ID)",
        placeholder="@VIP أو 123456789",
        required=False
    )
    
    points1 = discord.ui.TextInput(
        label="نقاط الرتبة الأولى (1-100)",
        placeholder="5",
        max_length=3,
        required=False
    )
    
    role2 = discord.ui.TextInput(
        label="الرتبة الثانية (اختياري)",
        placeholder="@Admin",
        required=False
    )
    
    points2 = discord.ui.TextInput(
        label="نقاط الرتبة الثانية",
        placeholder="10",
        max_length=3,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class EntitiesView(discord.ui.View):
    """View لإضافة رتب Entities إضافية"""
    
    def __init__(self, role_entities: List[dict]):
        super().__init__(timeout=300)
        self.role_entities = role_entities
        self.done = False
    
    @discord.ui.button(label="إضافة رتبة أخرى", style=discord.ButtonStyle.primary, emoji="➕")
    async def add_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        """إضافة رتبة إضافية"""
        modal = AddRoleEntityModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        if modal.role_id and modal.points:
            self.role_entities.append({
                "role_id": modal.role_id,
                "points": modal.points
            })
            await interaction.followup.send(
                f"✅ تمت الإضافة: <@&{modal.role_id}> = **{modal.points}** نقطة",
                ephemeral=True
            )
    
    @discord.ui.button(label="إنهاء", style=discord.ButtonStyle.success, emoji="✅")
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        """إنهاء الإضافة"""
        self.done = True
        await interaction.response.edit_message(
            content=f"✅ تم إضافة {len(self.role_entities)} رتبة بنجاح!",
            view=None
        )
        self.stop()


class AddRoleEntityModal(discord.ui.Modal, title="إضافة رتبة Entities"):
    """Modal لإضافة رتبة إضافية"""
    
    role = discord.ui.TextInput(
        label="الرتبة (mention أو ID)",
        placeholder="@Moderator أو 123456789",
        required=True
    )
    
    points = discord.ui.TextInput(
        label="عدد النقاط (1-100)",
        placeholder="15",
        max_length=3,
        required=True
    )
    
    def __init__(self):
        super().__init__()
        self.role_id = None
        self.points = None
    
    async def on_submit(self, interaction: discord.Interaction):
        # Parse role
        role_text = str(self.role.value).strip()
        if role_text.startswith("<@&") and role_text.endswith(">"):
            self.role_id = role_text[3:-1]
        else:
            self.role_id = role_text
        
        # Parse points
        try:
            self.points = int(self.points.value)
            if not 1 <= self.points <= 100:
                raise ValueError()
        except:
            await interaction.response.send_message("❌ النقاط يجب أن تكون رقم من 1 إلى 100", ephemeral=True)
            return
        
        await interaction.response.defer()


class TemplateSelectView(discord.ui.View):
    """View لاختيار قالب أو إنشاء قرعة جديدة"""
    
    def __init__(self, templates: List[dict], channel: discord.TextChannel, cog):
        super().__init__(timeout=180)
        self.channel = channel
        self.cog = cog
        
        # إضافة Select Menu للقوالب
        options = []
        
        # خيار إنشاء بدون قالب
        options.append(discord.SelectOption(
            label="⚡ إنشاء بدون قالب",
            value="no_template",
            description="إنشاء قرعة جديدة بدون استخدام قالب",
            emoji="🆕"
        ))
        
        # إضافة القوالب
        for template in templates[:24]:  # Max 25 options (1 reserved)
            fav_emoji = "⭐" if template.get("is_favorite", False) else "📋"
            options.append(discord.SelectOption(
                label=template["name"][:100],
                value=template["template_id"],
                description=f"استخدم {template.get('usage_count', 0)} مرة",
                emoji=fav_emoji
            ))
        
        select = discord.ui.Select(
            placeholder="اختر قالب أو أنشئ بدون قالب...",
            options=options
        )
        select.callback = self.select_callback
        self.add_item(select)
    
    async def select_callback(self, interaction: discord.Interaction):
        """معالجة اختيار القالب"""
        selected = interaction.data["values"][0]
        
        if selected == "no_template":
            # إنشاء بدون قالب
            modal = GiveawayModal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            
            # نفس المعالجة القديمة
            duration_seconds = self.cog.parse_duration(str(modal.duration.value))
            if not duration_seconds or duration_seconds < 60:
                await interaction.followup.send("❌ المدة غير صحيحة!", ephemeral=True)
                return
            
            try:
                winners_count = int(modal.winners.value)
                if not 1 <= winners_count <= 50:
                    raise ValueError()
            except:
                await interaction.followup.send("❌ عدد الفائزين يجب أن يكون من 1 إلى 50", ephemeral=True)
                return
            
            # سؤال عن Entities
            await interaction.followup.send(
                "هل تريد تفعيل **نظام Entities** (النقاط) لهذه القرعة؟\n\n"
                "**ما هو Entities؟**\n"
                "• نظام يعطي فرص فوز إضافية للأعضاء حسب رتبهم\n"
                "• 1 نقطة = 1% فرصة فوز إضافية\n\n"
                "اختر:",
                view=EntitiesChoiceView(
                    modal.prize.value,
                    str(modal.description.value) if modal.description.value else None,
                    duration_seconds,
                    winners_count,
                    self.channel,
                    self.cog
                ),
                ephemeral=True
            )
        else:
            # إنشاء من قالب
            template_id = selected
            
            # سؤال عن المدة (استخدام Modal)
            duration_modal = TemplateDurationModal()
            await interaction.response.send_modal(duration_modal)
            await duration_modal.wait()
            
            # Parse duration
            duration_input = str(duration_modal.duration.value).strip()
            duration_seconds = None
            
            if duration_input:
                duration_seconds = self.cog.parse_duration(duration_input)
                if not duration_seconds or duration_seconds < 60:
                    await interaction.followup.send("❌ المدة غير صحيحة!", ephemeral=True)
                    return
            
            # إنشاء القرعة من القالب
            try:
                giveaway = await self.cog.giveaway_system.create_giveaway_from_template(
                    template_id=template_id,
                    channel_id=str(self.channel.id),
                    host_id=str(interaction.user.id),
                    duration_seconds=duration_seconds
                )
                
                # إنشاء Embed و Button
                embed = self.cog.giveaway_system.create_giveaway_embed(giveaway)
                button_view = GiveawayButton(giveaway["giveaway_id"], giveaway["settings"]["emoji"])
                
                # إرسال الرسالة
                message = await self.channel.send(embed=embed, view=button_view)
                
                # حفظ message_id
                await self.cog.giveaway_db.update_giveaway(
                    giveaway["giveaway_id"],
                    {"message_id": str(message.id)}
                )
                
                await interaction.followup.send(
                    f"✅ تم إنشاء القرعة من القالب في {self.channel.mention}!",
                    ephemeral=True
                )
            
            except Exception as e:
                await interaction.followup.send(f"❌ حدث خطأ: {str(e)}", ephemeral=True)


class TemplateDurationModal(discord.ui.Modal, title="تحديد مدة القرعة ⏰"):
    """Modal لتحديد مدة القرعة من قالب"""
    
    duration = discord.ui.TextInput(
        label="المدة",
        placeholder="مثال: 1d, 12h, 30m (اتركه فارغاً للمدة الافتراضية)",
        max_length=20,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()


class GiveawayButton(discord.ui.View):
    """Button للدخول في القرعة"""
    
    def __init__(self, giveaway_id: str, emoji: str = "🎉"):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id
        
        # Custom button
        button = discord.ui.Button(
            label="دخول القرعة",
            style=discord.ButtonStyle.success,
            emoji=emoji,
            custom_id=f"giveaway_enter_{giveaway_id}"
        )
        button.callback = self.enter_callback
        self.add_item(button)
    
    async def enter_callback(self, interaction: discord.Interaction):
        """معالجة دخول المستخدم"""
        # سيتم المعالجة في on_interaction في Cog
        pass


class Giveaway(commands.Cog):
    """نظام القرعات مع Entities"""
    
    def __init__(self, bot):
        self.bot = bot
        self.giveaway_db = GiveawayDatabase(bot.db)
        self.giveaway_system = GiveawaySystem(self.giveaway_db, bot)
        
        # Start background task
        self.check_giveaways_task.start()
    
    def cog_unload(self):
        self.check_giveaways_task.cancel()
    
    # ===== Background Task =====
    @tasks.loop(seconds=30)
    async def check_giveaways_task(self):
        """فحص القرعات المنتهية"""
        try:
            active_giveaways = await self.giveaway_db.get_active_giveaways()
            now = datetime.now(timezone.utc)
            
            for giveaway in active_giveaways:
                if giveaway["end_time"] <= now:
                    # انتهت القرعة
                    await self.end_giveaway_automatically(giveaway)
        
        except Exception as e:
            print(f"Error in check_giveaways_task: {e}")
    
    @check_giveaways_task.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()
    
    async def end_giveaway_automatically(self, giveaway: dict):
        """إنهاء القرعة تلقائياً"""
        try:
            # اختيار الفائزين
            success, winners, error = await self.giveaway_system.end_giveaway(giveaway["giveaway_id"])
            
            if not success:
                # لا يوجد مشاركون
                channel = self.bot.get_channel(int(giveaway["channel_id"]))
                if channel and giveaway["message_id"]:
                    try:
                        message = await channel.fetch_message(int(giveaway["message_id"]))
                        embed = discord.Embed(
                            title="❌ انتهت القرعة",
                            description=f"**الجائزة:** {giveaway['prize']}\n\nلم يدخل أحد في القرعة!",
                            color=discord.Color.red()
                        )
                        await message.edit(embed=embed, view=None)
                    except:
                        pass
                return
            
            # إرسال رسالة الفائزين
            channel = self.bot.get_channel(int(giveaway["channel_id"]))
            if not channel:
                return
            
            # تحديث رسالة القرعة
            if giveaway["message_id"]:
                try:
                    message = await channel.fetch_message(int(giveaway["message_id"]))
                    winner_embed = self.giveaway_system.create_winner_embed(giveaway, winners)
                    await message.edit(embed=winner_embed, view=None)
                except:
                    pass
            
            # إرسال إعلان الفائزين
            winners_mentions = " ".join([f"<@{w['user_id']}>" for w in winners])
            
            announce_embed = discord.Embed(
                title="🎊 مبروك للفائزين!",
                description=f"**الجائزة:** {giveaway['prize']}\n\n**الفائزون:**\n{winners_mentions}",
                color=discord.Color.gold()
            )
            
            # Show entities info if enabled
            if giveaway.get("entities_enabled", False):
                entities_text = ""
                for winner in winners:
                    points = winner.get("entities_points", 0)
                    if points > 0:
                        entities_text += f"<@{winner['user_id']}>: **{points}** نقطة ⭐\n"
                
                if entities_text:
                    announce_embed.add_field(
                        name="⭐ Entities Points",
                        value=entities_text,
                        inline=False
                    )
            
            await channel.send(content=winners_mentions, embed=announce_embed)
            
            # DM winners
            if giveaway.get("settings", {}).get("dm_winner", True):
                for winner in winners:
                    try:
                        user = await self.bot.fetch_user(int(winner["user_id"]))
                        dm_embed = discord.Embed(
                            title="🎉 مبروك! فزت في قرعة!",
                            description=f"**الجائزة:** {giveaway['prize']}\n**السيرفر:** {channel.guild.name}",
                            color=discord.Color.gold()
                        )
                        dm_embed.add_field(
                            name="📬 الخطوة التالية",
                            value=f"تواصل مع <@{giveaway['host_id']}> لاستلام جائزتك!",
                            inline=False
                        )
                        await user.send(embed=dm_embed)
                    except:
                        pass
        
        except Exception as e:
            print(f"Error ending giveaway {giveaway['giveaway_id']}: {e}")
    
    # ===== Helper Functions =====
    def parse_duration(self, duration_str: str) -> Optional[int]:
        """تحويل النص إلى ثواني (1d, 12h, 30m)"""
        duration_str = duration_str.strip().lower()
        
        try:
            if duration_str.endswith('d'):
                return int(duration_str[:-1]) * 86400
            elif duration_str.endswith('h'):
                return int(duration_str[:-1]) * 3600
            elif duration_str.endswith('m'):
                return int(duration_str[:-1]) * 60
            elif duration_str.endswith('s'):
                return int(duration_str[:-1])
            else:
                return int(duration_str) * 60  # افتراضي: دقائق
        except:
            return None
    
    def parse_role_id(self, role_text: str) -> Optional[str]:
        """استخراج role ID من mention أو نص"""
        role_text = role_text.strip()
        if role_text.startswith("<@&") and role_text.endswith(">"):
            return role_text[3:-1]
        return role_text if role_text.isdigit() else None
    
    # ===== Commands =====
    giveaway_group = app_commands.Group(
        name="giveaway",
        description="نظام القرعات مع Entities"
    )
    
    @giveaway_group.command(name="create", description="إنشاء قرعة جديدة 🎁")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_create(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        """إنشاء قرعة جديدة"""
        # جلب قوالب السيرفر
        templates = await self.giveaway_db.get_guild_templates(
            str(interaction.guild.id),
            limit=25
        )
        
        if templates:
            # عرض قائمة القوالب
            view = TemplateSelectView(templates, channel, self)
            
            embed = discord.Embed(
                title="📋 إنشاء قرعة جديدة",
                description="اختر قالب موجود أو أنشئ قرعة جديدة بدون قالب:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name=f"📚 القوالب المتاحة ({len(templates)})",
                value="استخدم القائمة المنسدلة أدناه لاختيار قالب",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            # لا توجد قوالب، افتح Modal مباشرة
            modal = GiveawayModal()
            await interaction.response.send_modal(modal)
            await modal.wait()
        
        # Parse duration
        duration_seconds = self.parse_duration(str(modal.duration.value))
        if not duration_seconds or duration_seconds < 60:
            await interaction.followup.send("❌ المدة غير صحيحة! استخدم: 1d, 12h, 30m", ephemeral=True)
            return
        
        # Parse winners count
        try:
            winners_count = int(modal.winners.value)
            if not 1 <= winners_count <= 50:
                raise ValueError()
        except:
            await interaction.followup.send("❌ عدد الفائزين يجب أن يكون من 1 إلى 50", ephemeral=True)
            return
        
        # سؤال عن Entities
        await interaction.followup.send(
            "هل تريد تفعيل **نظام Entities** (النقاط) لهذه القرعة؟\n\n"
            "**ما هو Entities؟**\n"
            "• نظام يعطي فرص فوز إضافية للأعضاء حسب رتبهم\n"
            "• 1 نقطة = 1% فرصة فوز إضافية\n"
            "• يمكنك تحديد نقاط لكل رتبة (1-100 نقطة)\n\n"
            "**مثال:**\n"
            "• رتبة VIP: 5 نقاط = +5% فرصة فوز\n"
            "• رتبة Admin: 10 نقاط = +10% فرصة فوز\n\n"
            "**وضعان للحساب:**\n"
            "• **Cumulative (إجمالي):** جمع نقاط كل الرتب للعضو\n"
            "• **Highest (أعلى رتبة):** احتساب أعلى رتبة فقط\n\n"
            "اختر:",
            view=EntitiesChoiceView(
                modal.prize.value,
                str(modal.description.value) if modal.description.value else None,
                duration_seconds,
                winners_count,
                channel,
                self
            ),
            ephemeral=True
        )


class EntitiesChoiceView(discord.ui.View):
    """View لاختيار تفعيل Entities"""
    
    def __init__(self, prize, description, duration, winners_count, channel, cog):
        super().__init__(timeout=180)
        self.prize = prize
        self.description = description
        self.duration = duration
        self.winners_count = winners_count
        self.channel = channel
        self.cog = cog
    
    @discord.ui.button(label="نعم، تفعيل Entities", style=discord.ButtonStyle.primary, emoji="⭐")
    async def enable_entities(self, interaction: discord.Interaction, button: discord.ui.Button):
        """تفعيل Entities"""
        # فتح Modal لإعداد Entities
        modal = EntitiesSetupModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        # Parse mode
        mode = str(modal.mode.value).strip().lower()
        if mode not in ["cumulative", "highest"]:
            await interaction.followup.send("❌ الوضع يجب أن يكون `cumulative` أو `highest`", ephemeral=True)
            return
        
        # Parse roles
        role_entities = []
        
        # Role 1
        if modal.role1.value and modal.points1.value:
            role_id = self.cog.parse_role_id(str(modal.role1.value))
            try:
                points = int(modal.points1.value)
                if 1 <= points <= 100:
                    role_entities.append({"role_id": role_id, "points": points})
            except:
                pass
        
        # Role 2
        if modal.role2.value and modal.points2.value:
            role_id = self.cog.parse_role_id(str(modal.role2.value))
            try:
                points = int(modal.points2.value)
                if 1 <= points <= 100:
                    role_entities.append({"role_id": role_id, "points": points})
            except:
                pass
        
        if not role_entities:
            await interaction.followup.send("❌ يجب إضافة رتبة واحدة على الأقل", ephemeral=True)
            return
        
        # سؤال عن رتب إضافية
        view = EntitiesView(role_entities)
        await interaction.followup.send(
            f"✅ تم إضافة {len(role_entities)} رتبة\n\nهل تريد إضافة المزيد من الرتب؟",
            view=view,
            ephemeral=True
        )
        await view.wait()
        
        # إنشاء القرعة
        await self.create_giveaway_final(
            interaction,
            entities_enabled=True,
            entities_mode=mode,
            role_entities=role_entities
        )
    
    @discord.ui.button(label="لا، بدون Entities", style=discord.ButtonStyle.secondary, emoji="❌")
    async def disable_entities(self, interaction: discord.Interaction, button: discord.ui.Button):
        """بدون Entities"""
        await self.create_giveaway_final(interaction, entities_enabled=False)
    
    async def create_giveaway_final(
        self,
        interaction: discord.Interaction,
        entities_enabled: bool = False,
        entities_mode: str = "cumulative",
        role_entities: Optional[List[dict]] = None
    ):
        """إنشاء القرعة النهائي"""
        await interaction.response.defer(ephemeral=True)
        
        # إنشاء القرعة
        giveaway = await self.cog.giveaway_system.create_giveaway(
            guild_id=str(interaction.guild.id),
            channel_id=str(self.channel.id),
            host_id=str(interaction.user.id),
            prize=self.prize,
            duration_seconds=self.duration,
            winners_count=self.winners_count,
            description=self.description,
            entities_enabled=entities_enabled,
            entities_mode=entities_mode,
            role_entities=role_entities or []
        )
        
        # إنشاء Embed و Button
        embed = self.cog.giveaway_system.create_giveaway_embed(giveaway)
        button_view = GiveawayButton(giveaway["giveaway_id"], giveaway["settings"]["emoji"])
        
        # إرسال الرسالة
        message = await self.channel.send(embed=embed, view=button_view)
        
        # حفظ message_id
        await self.cog.giveaway_db.update_giveaway(
            giveaway["giveaway_id"],
            {"message_id": str(message.id)}
        )
        
        await interaction.followup.send(
            f"✅ تم إنشاء القرعة بنجاح في {self.channel.mention}!",
            ephemeral=True
        )


    @giveaway_group.command(name="end", description="إنهاء قرعة مبكراً 🎊")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_end(
        self,
        interaction: discord.Interaction,
        giveaway_id: str
    ):
        """إنهاء قرعة مبكراً"""
        await interaction.response.defer()
        
        giveaway = await self.giveaway_db.get_giveaway(giveaway_id)
        if not giveaway:
            await interaction.followup.send("❌ القرعة غير موجودة", ephemeral=True)
            return
        
        if giveaway["guild_id"] != str(interaction.guild.id):
            await interaction.followup.send("❌ هذه القرعة ليست في هذا السيرفر", ephemeral=True)
            return
        
        if giveaway["status"] != "active":
            await interaction.followup.send("❌ هذه القرعة غير نشطة", ephemeral=True)
            return
        
        # إنهاء القرعة
        success, winners, error = await self.giveaway_system.end_giveaway(giveaway_id)
        
        if not success:
            await interaction.followup.send(f"❌ {error}", ephemeral=True)
            return
        
        # تحديث الرسالة
        channel = self.bot.get_channel(int(giveaway["channel_id"]))
        if channel and giveaway["message_id"]:
            try:
                message = await channel.fetch_message(int(giveaway["message_id"]))
                winner_embed = self.giveaway_system.create_winner_embed(giveaway, winners)
                await message.edit(embed=winner_embed, view=None)
            except:
                pass
        
        # إعلان الفائزين
        winners_mentions = " ".join([f"<@{w['user_id']}>" for w in winners])
        
        embed = discord.Embed(
            title="🎊 انتهت القرعة مبكراً!",
            description=f"**الجائزة:** {giveaway['prize']}\n\n**الفائزون:**\n{winners_mentions}",
            color=discord.Color.gold()
        )
        
        await interaction.followup.send(content=winners_mentions, embed=embed)
    
    @giveaway_group.command(name="reroll", description="إعادة سحب الفائزين 🔄")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_reroll(
        self,
        interaction: discord.Interaction,
        giveaway_id: str,
        new_winners_count: Optional[int] = None
    ):
        """إعادة سحب الفائزين"""
        await interaction.response.defer()
        
        success, winners, error = await self.giveaway_system.reroll_giveaway(
            giveaway_id,
            new_winners_count
        )
        
        if not success:
            await interaction.followup.send(f"❌ {error}", ephemeral=True)
            return
        
        giveaway = await self.giveaway_db.get_giveaway(giveaway_id)
        
        # تحديث الرسالة
        channel = self.bot.get_channel(int(giveaway["channel_id"]))
        if channel and giveaway["message_id"]:
            try:
                message = await channel.fetch_message(int(giveaway["message_id"]))
                winner_embed = self.giveaway_system.create_winner_embed(giveaway, winners)
                await message.edit(embed=winner_embed, view=None)
            except:
                pass
        
        # إعلان الفائزين الجدد
        winners_mentions = " ".join([f"<@{w['user_id']}>" for w in winners])
        
        embed = discord.Embed(
            title="🔄 إعادة سحب الفائزين!",
            description=f"**الجائزة:** {giveaway['prize']}\n\n**الفائزون الجدد:**\n{winners_mentions}",
            color=discord.Color.blue()
        )
        
        await interaction.followup.send(content=winners_mentions, embed=embed)
    
    @giveaway_group.command(name="cancel", description="إلغاء قرعة ❌")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_cancel(
        self,
        interaction: discord.Interaction,
        giveaway_id: str
    ):
        """إلغاء قرعة"""
        await interaction.response.defer()
        
        giveaway = await self.giveaway_db.get_giveaway(giveaway_id)
        if not giveaway:
            await interaction.followup.send("❌ القرعة غير موجودة", ephemeral=True)
            return
        
        if giveaway["status"] != "active":
            await interaction.followup.send("❌ هذه القرعة غير نشطة", ephemeral=True)
            return
        
        # إلغاء القرعة
        await self.giveaway_db.update_giveaway(
            giveaway_id,
            {
                "status": "cancelled",
                "cancelled_at": datetime.now(timezone.utc)
            }
        )
        
        # تحديث الرسالة
        channel = self.bot.get_channel(int(giveaway["channel_id"]))
        if channel and giveaway["message_id"]:
            try:
                message = await channel.fetch_message(int(giveaway["message_id"]))
                embed = discord.Embed(
                    title="❌ تم إلغاء القرعة",
                    description=f"**الجائزة:** {giveaway['prize']}\n\nتم إلغاء هذه القرعة بواسطة المنظم.",
                    color=discord.Color.red()
                )
                await message.edit(embed=embed, view=None)
            except:
                pass
        
        await interaction.followup.send("✅ تم إلغاء القرعة بنجاح")
    
    @giveaway_group.command(name="list", description="عرض القرعات النشطة 📋")
    async def giveaway_list(
        self,
        interaction: discord.Interaction,
        status: Optional[str] = "active"
    ):
        """عرض قائمة القرعات"""
        await interaction.response.defer()
        
        giveaways = await self.giveaway_db.get_guild_giveaways(
            str(interaction.guild.id),
            status=status,
            limit=10
        )
        
        if not giveaways:
            await interaction.followup.send(f"❌ لا توجد قرعات {status}", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📋 القرعات - {status}",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        for giveaway in giveaways[:10]:
            value_text = f"**ID:** `{giveaway['giveaway_id'][:8]}...`\n"
            value_text += f"**المنظّم:** <@{giveaway['host_id']}>\n"
            value_text += f"**الفائزون:** {giveaway['winners_count']}\n"
            value_text += f"**المشاركون:** {len(giveaway.get('entries', []))}\n"
            
            if giveaway.get("entities_enabled", False):
                value_text += "**Entities:** ⭐ مفعّل\n"
            
            if status == "active":
                time_left = giveaway["end_time"] - datetime.now(timezone.utc)
                hours = int(time_left.total_seconds() // 3600)
                minutes = int((time_left.total_seconds() % 3600) // 60)
                value_text += f"**المتبقي:** {hours}h {minutes}m"
            
            embed.add_field(
                name=f"🎁 {giveaway['prize']}",
                value=value_text,
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
    
    @giveaway_group.command(name="info", description="معلومات قرعة معينة ℹ️")
    async def giveaway_info(
        self,
        interaction: discord.Interaction,
        giveaway_id: str
    ):
        """عرض معلومات قرعة"""
        await interaction.response.defer()
        
        giveaway = await self.giveaway_db.get_giveaway(giveaway_id)
        if not giveaway:
            await interaction.followup.send("❌ القرعة غير موجودة", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"🎁 {giveaway['prize']}",
            description=giveaway.get("description", ""),
            color=int(giveaway.get("color", "#FF00FF").replace("#", ""), 16),
            timestamp=giveaway["created_at"]
        )
        
        # Basic info
        embed.add_field(name="ID", value=f"`{giveaway['giveaway_id']}`", inline=False)
        embed.add_field(name="المنظّم", value=f"<@{giveaway['host_id']}>", inline=True)
        embed.add_field(name="الحالة", value=giveaway["status"], inline=True)
        embed.add_field(name="الفائزون", value=giveaway["winners_count"], inline=True)
        
        # Participants
        total_entries = len(giveaway.get("entries", []))
        embed.add_field(name="المشاركون", value=total_entries, inline=True)
        
        # Entities info
        if giveaway.get("entities_enabled", False):
            mode_text = "إجمالي" if giveaway["entities_mode"] == "cumulative" else "أعلى رتبة"
            entities_text = f"**الوضع:** {mode_text}\n"
            entities_text += f"**الرتب:** {len(giveaway.get('role_entities', []))}\n"
            
            stats = giveaway.get("stats", {})
            entities_text += f"**متوسط النقاط:** {stats.get('avg_entities_points', 0):.1f}\n"
            entities_text += f"**أعلى نقاط:** {stats.get('max_entities_points', 0)}"
            
            embed.add_field(
                name="⭐ Entities System",
                value=entities_text,
                inline=False
            )
            
            # Role entities details
            role_entities = giveaway.get("role_entities", [])
            if role_entities:
                roles_text = ""
                for re in role_entities[:10]:
                    roles_text += f"<@&{re['role_id']}>: **{re['points']}** نقطة\n"
                
                embed.add_field(
                    name="الرتب المحددة",
                    value=roles_text,
                    inline=False
                )
        
        # Winners
        winners = giveaway.get("winners", [])
        if winners:
            winners_text = ""
            for i, winner in enumerate(winners[:10], 1):
                winners_text += f"{i}. <@{winner['user_id']}>"
                if giveaway.get("entities_enabled", False):
                    points = winner.get("entities_points", 0)
                    if points > 0:
                        winners_text += f" (⭐ {points})"
                winners_text += "\n"
            
            embed.add_field(
                name="🏆 الفائزون",
                value=winners_text,
                inline=False
            )
        
        # Time info
        if giveaway["status"] == "active":
            time_left = giveaway["end_time"] - datetime.now(timezone.utc)
            hours = int(time_left.total_seconds() // 3600)
            minutes = int((time_left.total_seconds() % 3600) // 60)
            embed.add_field(name="⏰ المتبقي", value=f"{hours}h {minutes}m", inline=True)
        
        embed.set_footer(text=f"تم الإنشاء")
        
        await interaction.followup.send(embed=embed)
    
    @giveaway_group.command(name="entries", description="عرض المشاركين في قرعة 👥")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_entries(
        self,
        interaction: discord.Interaction,
        giveaway_id: str
    ):
        """عرض المشاركين"""
        await interaction.response.defer()
        
        giveaway = await self.giveaway_db.get_giveaway(giveaway_id)
        if not giveaway:
            await interaction.followup.send("❌ القرعة غير موجودة", ephemeral=True)
            return
        
        entries = giveaway.get("entries", [])
        if not entries:
            await interaction.followup.send("❌ لا يوجد مشاركون", ephemeral=True)
            return
        
        # Sort by entities points
        if giveaway.get("entities_enabled", False):
            entries.sort(key=lambda e: e.get("entities_points", 0), reverse=True)
        
        embed = discord.Embed(
            title=f"👥 المشاركون في: {giveaway['prize']}",
            description=f"**إجمالي المشاركين:** {len(entries)}",
            color=discord.Color.blue()
        )
        
        # Show top 20 entries
        entries_text = ""
        for i, entry in enumerate(entries[:20], 1):
            entries_text += f"{i}. <@{entry['user_id']}>"
            
            if giveaway.get("entities_enabled", False):
                points = entry.get("entities_points", 0)
                bonus = entry.get("bonus_entries", 0)
                if points > 0:
                    entries_text += f" - ⭐ {points} نقطة (+{bonus} إدخال)"
            
            entries_text += "\n"
        
        if len(entries) > 20:
            entries_text += f"\n*و {len(entries) - 20} مشارك آخر...*"
        
        embed.add_field(
            name="المشاركون",
            value=entries_text,
            inline=False
        )
        
        # Stats
        if giveaway.get("entities_enabled", False):
            stats = giveaway.get("stats", {})
            stats_text = f"**إجمالي الإدخالات:** {stats.get('total_entries', 0) + stats.get('total_bonus_entries', 0)}\n"
            stats_text += f"**إدخالات عادية:** {stats.get('total_entries', 0)}\n"
            stats_text += f"**إدخالات إضافية:** {stats.get('total_bonus_entries', 0)}\n"
            stats_text += f"**متوسط النقاط:** {stats.get('avg_entities_points', 0):.1f}\n"
            stats_text += f"**أعلى نقاط:** {stats.get('max_entities_points', 0)}"
            
            embed.add_field(
                name="📊 إحصائيات",
                value=stats_text,
                inline=False
            )
        
        await interaction.followup.send(embed=embed)
    
    # ===== Template Commands =====
    template_group = app_commands.Group(
        name="gtemplate",
        description="إدارة قوالب القرعات 📋",
        parent=giveaway_group
    )
    
    @template_group.command(name="create", description="إنشاء قالب قرعة جديد 📋")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def template_create(self, interaction: discord.Interaction):
        """إنشاء قالب جديد"""
        modal = TemplateCreateModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        # Parse duration
        duration_seconds = self.parse_duration(str(modal.duration.value))
        if not duration_seconds or duration_seconds < 60:
            await interaction.followup.send("❌ المدة غير صحيحة!", ephemeral=True)
            return
        
        # Parse winners
        try:
            winners_count = int(modal.winners.value)
            if not 1 <= winners_count <= 50:
                raise ValueError()
        except:
            await interaction.followup.send("❌ عدد الفائزين يجب أن يكون من 1 إلى 50", ephemeral=True)
            return
        
        # إنشاء template_id
        import uuid
        template_id = str(uuid.uuid4())
        
        # إنشاء القالب
        template_data = {
            "template_id": template_id,
            "guild_id": str(interaction.guild.id),
            "name": str(modal.name.value),
            "description": str(modal.description.value) if modal.description.value else None,
            "created_by": str(interaction.user.id),
            "prize": str(modal.prize.value),
            "giveaway_description": None,
            "winners_count": winners_count,
            "default_duration_seconds": duration_seconds,
            "color": "#FF00FF",
            "thumbnail_url": None,
            "image_url": None,
            "footer_text": None,
            "footer_icon_url": None,
            "emoji": "🎉",
            "entities_enabled": False,
            "entities_mode": "cumulative",
            "role_entities": [],
            "requirements": {},
            "ping_role_id": None,
            "dm_winner": True,
            "show_participants": True,
            "show_entities_info": False,
            "schedule_enabled": False,
            "schedule_datetime": None
        }
        
        await self.giveaway_db.create_template(template_data)
        
        embed = discord.Embed(
            title="✅ تم إنشاء القالب بنجاح!",
            description=f"**اسم القالب:** {modal.name.value}\n**الجائزة:** {modal.prize.value}",
            color=discord.Color.green()
        )
        
        embed.add_field(name="الفائزون", value=winners_count, inline=True)
        embed.add_field(name="المدة الافتراضية", value=modal.duration.value, inline=True)
        embed.add_field(
            name="📝 الخطوة التالية",
            value=f"استخدم `/giveaway gtemplate edit` لتخصيص القالب بالكامل\n"
                  f"(ألوان، صور، Entities، شروط، إلخ)",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @template_group.command(name="list", description="عرض قوالب القرعات 📋")
    async def template_list(
        self,
        interaction: discord.Interaction,
        show_all: bool = False
    ):
        """عرض قوالب السيرفر"""
        await interaction.response.defer(ephemeral=True)
        
        # جلب القوالب
        if show_all or interaction.user.guild_permissions.manage_guild:
            templates = await self.giveaway_db.get_guild_templates(
                str(interaction.guild.id),
                limit=25
            )
        else:
            # فقط قوالب المستخدم
            templates = await self.giveaway_db.get_guild_templates(
                str(interaction.guild.id),
                created_by=str(interaction.user.id),
                limit=25
            )
        
        if not templates:
            await interaction.followup.send("❌ لا توجد قوالب", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=f"📋 قوالب القرعات ({len(templates)})",
            color=discord.Color.blue(),
            timestamp=datetime.now(timezone.utc)
        )
        
        for template in templates[:10]:
            fav = "⭐ " if template.get("is_favorite", False) else ""
            entities = "⭐ Entities" if template.get("entities_enabled", False) else "عادي"
            
            value = f"**المنشئ:** <@{template['created_by']}>\n"
            value += f"**الجائزة:** {template['prize']}\n"
            value += f"**الفائزون:** {template['winners_count']}\n"
            value += f"**النوع:** {entities}\n"
            value += f"**الاستخدامات:** {template.get('usage_count', 0)}\n"
            value += f"**ID:** `{template['template_id'][:12]}...`"
            
            embed.add_field(
                name=f"{fav}{template['name']}",
                value=value,
                inline=False
            )
        
        if len(templates) > 10:
            embed.set_footer(text=f"و {len(templates) - 10} قالب آخر...")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @template_group.command(name="delete", description="حذف قالب 🗑️")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def template_delete(
        self,
        interaction: discord.Interaction,
        template_id: str
    ):
        """حذف قالب"""
        await interaction.response.defer(ephemeral=True)
        
        template = await self.giveaway_db.get_template(template_id)
        if not template:
            await interaction.followup.send("❌ القالب غير موجود", ephemeral=True)
            return
        
        if template["guild_id"] != str(interaction.guild.id):
            await interaction.followup.send("❌ هذا القالب ليس في هذا السيرفر", ephemeral=True)
            return
        
        # حذف القالب
        await self.giveaway_db.delete_template(template_id)
        
        await interaction.followup.send(
            f"✅ تم حذف القالب **{template['name']}** بنجاح",
            ephemeral=True
        )
    
    @template_group.command(name="favorite", description="تفضيل/إلغاء تفضيل قالب ⭐")
    async def template_favorite(
        self,
        interaction: discord.Interaction,
        template_id: str
    ):
        """تبديل حالة المفضلة"""
        await interaction.response.defer(ephemeral=True)
        
        template = await self.giveaway_db.get_template(template_id)
        if not template:
            await interaction.followup.send("❌ القالب غير موجود", ephemeral=True)
            return
        
        # تبديل المفضلة
        await self.giveaway_db.toggle_template_favorite(template_id)
        
        new_status = not template.get("is_favorite", False)
        emoji = "⭐" if new_status else "❌"
        action = "إضافة إلى" if new_status else "إزالة من"
        
        await interaction.followup.send(
            f"{emoji} تم {action} المفضلة: **{template['name']}**",
            ephemeral=True
        )
    
    # ===== Interaction Handler =====
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """معالجة button clicks"""
        if interaction.type != discord.InteractionType.component:
            return
        
        if not interaction.data.get("custom_id", "").startswith("giveaway_enter_"):
            return
        
        # Parse giveaway_id
        giveaway_id = interaction.data["custom_id"].replace("giveaway_enter_", "")
        
        # Add entry
        success, message = await self.giveaway_system.add_entry(
            giveaway_id,
            interaction.user
        )
        
        if success:
            await interaction.response.send_message(message, ephemeral=True)
            
            # Update embed participants count
            giveaway = await self.giveaway_db.get_giveaway(giveaway_id)
            if giveaway and giveaway.get("settings", {}).get("show_participants", True):
                try:
                    embed = self.giveaway_system.create_giveaway_embed(giveaway)
                    await interaction.message.edit(embed=embed)
                except:
                    pass
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Giveaway(bot))

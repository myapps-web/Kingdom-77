"""
Tickets Cog - أوامر نظام التذاكر
Kingdom-77 Bot v3.0

الأوامر:
- /ticket create - إنشاء تذكرة جديدة
- /ticket close - إغلاق تذكرة
- /ticket add - إضافة عضو للتذكرة
- /ticket remove - إزالة عضو من التذكرة
- /ticket claim - المطالبة بالتذكرة
- /ticket transcript - حفظ نص المحادثة
- /ticketsetup - إعداد نظام التذاكر (الإدارة)
- /ticketcategory - إدارة فئات التذاكر (الإدارة)
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
from datetime import datetime, timedelta
import asyncio

from tickets import TicketSystem
from database import get_db


class TicketCategoryModal(discord.ui.Modal, title="اختر فئة التذكرة"):
    """نموذج اختيار فئة التذكرة"""
    
    subject = discord.ui.TextInput(
        label="موضوع التذكرة",
        placeholder="اكتب موضوع تذكرتك هنا...",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    description = discord.ui.TextInput(
        label="الوصف",
        placeholder="اشرح مشكلتك أو استفسارك بالتفصيل...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    
    def __init__(self, ticket_system: TicketSystem, category_id: str):
        super().__init__()
        self.ticket_system = ticket_system
        self.category_id = category_id
    
    async def on_submit(self, interaction: discord.Interaction):
        """عند إرسال النموذج"""
        await interaction.response.defer(ephemeral=True)
        
        # التحقق من قدرة المستخدم على إنشاء تذكرة
        can_create, message = await self.ticket_system.can_user_create_ticket(
            interaction.guild.id,
            interaction.user.id
        )
        
        if not can_create:
            await interaction.followup.send(
                f"❌ {message}",
                ephemeral=True
            )
            return
        
        # الحصول على الإعدادات والفئة
        config = await self.ticket_system.get_guild_config(interaction.guild.id)
        category = await self.ticket_system.get_category(
            interaction.guild.id,
            self.category_id
        )
        
        if not category:
            await interaction.followup.send(
                "❌ الفئة غير موجودة",
                ephemeral=True
            )
            return
        
        # إنشاء قناة التذكرة
        try:
            # الحصول على الكاتيجوري
            discord_category = None
            if category.get("discord_category_id"):
                discord_category = interaction.guild.get_channel(
                    category["discord_category_id"]
                )
            elif config.get("ticket_category_id"):
                discord_category = interaction.guild.get_channel(
                    config["ticket_category_id"]
                )
            
            # تنسيق اسم القناة
            ticket_number = config.get("next_ticket_number", 1)
            channel_name = config.get("ticket_name_format", "ticket-{number}").format(
                number=ticket_number
            )
            
            # الأذونات
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(
                    view_channel=False
                ),
                interaction.user: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                ),
                interaction.guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    manage_channels=True,
                    manage_messages=True,
                    read_message_history=True,
                    attach_files=True,
                    embed_links=True
                )
            }
            
            # إضافة رتب الدعم
            support_roles = config.get("support_roles", [])
            for role_id in support_roles:
                role = interaction.guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        view_channel=True,
                        send_messages=True,
                        read_message_history=True
                    )
            
            # إنشاء القناة
            channel = await interaction.guild.create_text_channel(
                name=channel_name,
                category=discord_category,
                overwrites=overwrites,
                topic=f"تذكرة #{ticket_number} - {interaction.user.name} - {category['name']}"
            )
            
            # حفظ التذكرة في قاعدة البيانات
            ticket = await self.ticket_system.create_ticket(
                guild_id=interaction.guild.id,
                user_id=interaction.user.id,
                channel_id=channel.id,
                category=self.category_id
            )
            
            # تحديث الموضوع
            await self.ticket_system.update_ticket(
                interaction.guild.id,
                channel.id,
                {"subject": self.subject.value}
            )
            
            # رسالة الترحيب
            welcome_message = category.get(
                "welcome_message",
                "مرحباً {user}! شكراً لتواصلك معنا. سيتم الرد عليك قريباً."
            ).format(user=interaction.user.mention)
            
            embed = discord.Embed(
                title=f"{category['emoji']} {category['name']}",
                description=welcome_message,
                color=category.get("color", 0x5865F2),
                timestamp=datetime.utcnow()
            )
            embed.add_field(
                name="📝 الموضوع",
                value=self.subject.value,
                inline=False
            )
            embed.add_field(
                name="📄 الوصف",
                value=self.description.value,
                inline=False
            )
            embed.add_field(
                name="👤 المستخدم",
                value=interaction.user.mention,
                inline=True
            )
            embed.add_field(
                name="🎫 رقم التذكرة",
                value=f"#{ticket['ticket_number']}",
                inline=True
            )
            embed.set_footer(text=f"Ticket #{ticket['ticket_number']}")
            
            # أزرار التحكم
            view = TicketControlView(self.ticket_system)
            
            await channel.send(embed=embed, view=view)
            
            # منشن للرتب المطلوبة
            ping_roles = category.get("ping_roles", []) or config.get("ping_roles", [])
            if ping_roles:
                mentions = " ".join(
                    f"<@&{role_id}>" for role_id in ping_roles
                )
                await channel.send(f"🔔 {mentions}")
            
            # الرد على المستخدم
            await interaction.followup.send(
                f"✅ تم إنشاء تذكرتك بنجاح!\n{channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ حدث خطأ أثناء إنشاء التذكرة: {str(e)}",
                ephemeral=True
            )


class TicketCategorySelect(discord.ui.Select):
    """قائمة اختيار فئة التذكرة"""
    
    def __init__(self, ticket_system: TicketSystem, categories: list):
        self.ticket_system = ticket_system
        
        options = []
        for cat in categories[:25]:  # Discord limit
            options.append(
                discord.SelectOption(
                    label=cat["name"],
                    description=cat["description"][:100],
                    emoji=cat["emoji"],
                    value=cat["category_id"]
                )
            )
        
        super().__init__(
            placeholder="اختر فئة تذكرتك...",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        """عند اختيار فئة"""
        category_id = self.values[0]
        
        # فتح النموذج
        modal = TicketCategoryModal(self.ticket_system, category_id)
        await interaction.response.send_modal(modal)


class TicketCategoryView(discord.ui.View):
    """واجهة اختيار فئة التذكرة"""
    
    def __init__(self, ticket_system: TicketSystem, categories: list):
        super().__init__(timeout=None)
        self.add_item(TicketCategorySelect(ticket_system, categories))


class TicketControlView(discord.ui.View):
    """أزرار التحكم في التذكرة"""
    
    def __init__(self, ticket_system: TicketSystem):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
    
    @discord.ui.button(
        label="إغلاق التذكرة",
        style=discord.ButtonStyle.red,
        emoji="🔒",
        custom_id="ticket_close"
    )
    async def close_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        """زر إغلاق التذكرة"""
        # التحقق من الصلاحيات
        ticket = await self.ticket_system.get_ticket(
            interaction.guild.id,
            interaction.channel.id
        )
        
        if not ticket:
            await interaction.response.send_message(
                "❌ هذه ليست قناة تذكرة صحيحة",
                ephemeral=True
            )
            return
        
        # التحقق: صاحب التذكرة أو لديه صلاحيات
        is_owner = interaction.user.id == ticket["user_id"]
        has_perms = interaction.user.guild_permissions.manage_channels
        
        config = await self.ticket_system.get_guild_config(interaction.guild.id)
        support_roles = config.get("support_roles", [])
        is_support = any(
            role.id in support_roles
            for role in interaction.user.roles
        )
        
        if not (is_owner or has_perms or is_support):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية لإغلاق هذه التذكرة",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # إغلاق التذكرة
        await self.ticket_system.close_ticket(
            interaction.guild.id,
            interaction.channel.id,
            interaction.user.id,
            "مغلقة بواسطة زر الإغلاق"
        )
        
        # حفظ النص
        if config.get("save_transcripts", True):
            messages = await self.ticket_system.collect_messages_for_transcript(
                interaction.channel
            )
            await self.ticket_system.save_transcript(
                interaction.guild.id,
                ticket,
                messages
            )
        
        # رسالة الإغلاق
        embed = discord.Embed(
            title="🔒 تم إغلاق التذكرة",
            description=f"تم إغلاق التذكرة بواسطة {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        if config.get("delete_on_close", False):
            delete_after = config.get("delete_after_minutes", 5)
            embed.add_field(
                name="⏱️ الحذف",
                value=f"سيتم حذف القناة بعد {delete_after} دقيقة",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            
            # حذف القناة
            await asyncio.sleep(delete_after * 60)
            await interaction.channel.delete(reason="تذكرة مغلقة")
        else:
            # قفل القناة
            await interaction.channel.set_permissions(
                interaction.guild.default_role,
                send_messages=False
            )
            
            # إزالة الأزرار
            self.clear_items()
            self.add_item(discord.ui.Button(
                label="تذكرة مغلقة",
                style=discord.ButtonStyle.gray,
                emoji="🔒",
                disabled=True
            ))
            
            await interaction.followup.send(embed=embed, view=self)
        
        # إرسال DM للمستخدم
        if config.get("dm_user_on_close", True):
            try:
                user = interaction.guild.get_member(ticket["user_id"])
                if user:
                    dm_embed = discord.Embed(
                        title="🔒 تم إغلاق تذكرتك",
                        description=f"تم إغلاق تذكرتك #{ticket['ticket_number']} في سيرفر **{interaction.guild.name}**",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    await user.send(embed=dm_embed)
            except:
                pass
    
    @discord.ui.button(
        label="حفظ النص",
        style=discord.ButtonStyle.gray,
        emoji="📄",
        custom_id="ticket_transcript"
    )
    async def transcript_button(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        """زر حفظ نص المحادثة"""
        await interaction.response.defer(ephemeral=True)
        
        ticket = await self.ticket_system.get_ticket(
            interaction.guild.id,
            interaction.channel.id
        )
        
        if not ticket:
            await interaction.followup.send(
                "❌ هذه ليست قناة تذكرة صحيحة",
                ephemeral=True
            )
            return
        
        # جمع الرسائل
        messages = await self.ticket_system.collect_messages_for_transcript(
            interaction.channel
        )
        
        # حفظ النص
        transcript = await self.ticket_system.save_transcript(
            interaction.guild.id,
            ticket,
            messages
        )
        
        await interaction.followup.send(
            f"✅ تم حفظ نص المحادثة ({len(messages)} رسالة)",
            ephemeral=True
        )


class TicketsCog(commands.Cog):
    """نظام التذاكر"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = None
        self.ticket_system = None
    
    async def cog_load(self):
        """تحميل الـ Cog"""
        self.db = await get_db()
        self.ticket_system = TicketSystem(self.db)
        print("✅ Tickets Cog loaded successfully")
    
    # مجموعة أوامر ticket
    ticket_group = app_commands.Group(
        name="ticket",
        description="أوامر نظام التذاكر"
    )
    
    @ticket_group.command(
        name="create",
        description="إنشاء تذكرة دعم جديدة"
    )
    async def ticket_create(self, interaction: discord.Interaction):
        """إنشاء تذكرة جديدة"""
        # التحقق من قدرة المستخدم
        can_create, message = await self.ticket_system.can_user_create_ticket(
            interaction.guild.id,
            interaction.user.id
        )
        
        if not can_create:
            await interaction.response.send_message(
                f"❌ {message}",
                ephemeral=True
            )
            return
        
        # الحصول على الفئات
        categories = await self.ticket_system.get_all_categories(
            interaction.guild.id,
            enabled_only=True
        )
        
        if not categories:
            await interaction.response.send_message(
                "❌ لا توجد فئات تذاكر متاحة. يرجى التواصل مع الإدارة.",
                ephemeral=True
            )
            return
        
        # إنشاء القائمة المنسدلة
        view = TicketCategoryView(self.ticket_system, categories)
        
        embed = discord.Embed(
            title="🎫 إنشاء تذكرة دعم",
            description="اختر فئة تذكرتك من القائمة أدناه:",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )
    
    @ticket_group.command(
        name="close",
        description="إغلاق التذكرة الحالية"
    )
    @app_commands.describe(
        reason="سبب إغلاق التذكرة (اختياري)"
    )
    async def ticket_close(
        self,
        interaction: discord.Interaction,
        reason: Optional[str] = None
    ):
        """إغلاق تذكرة"""
        ticket = await self.ticket_system.get_ticket(
            interaction.guild.id,
            interaction.channel.id
        )
        
        if not ticket:
            await interaction.response.send_message(
                "❌ هذه ليست قناة تذكرة",
                ephemeral=True
            )
            return
        
        # التحقق من الصلاحيات (نفس المنطق من الزر)
        is_owner = interaction.user.id == ticket["user_id"]
        has_perms = interaction.user.guild_permissions.manage_channels
        
        config = await self.ticket_system.get_guild_config(interaction.guild.id)
        support_roles = config.get("support_roles", [])
        is_support = any(
            role.id in support_roles
            for role in interaction.user.roles
        )
        
        if not (is_owner or has_perms or is_support):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية لإغلاق هذه التذكرة",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # إغلاق التذكرة (نفس المنطق من الزر)
        await self.ticket_system.close_ticket(
            interaction.guild.id,
            interaction.channel.id,
            interaction.user.id,
            reason or "مغلقة بواسطة الأمر"
        )
        
        # حفظ النص
        if config.get("save_transcripts", True):
            messages = await self.ticket_system.collect_messages_for_transcript(
                interaction.channel
            )
            await self.ticket_system.save_transcript(
                interaction.guild.id,
                ticket,
                messages
            )
        
        # رسالة الإغلاق
        embed = discord.Embed(
            title="🔒 تم إغلاق التذكرة",
            description=f"تم إغلاق التذكرة بواسطة {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        
        if reason:
            embed.add_field(name="📝 السبب", value=reason, inline=False)
        
        if config.get("delete_on_close", False):
            delete_after = config.get("delete_after_minutes", 5)
            embed.add_field(
                name="⏱️ الحذف",
                value=f"سيتم حذف القناة بعد {delete_after} دقيقة",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
            await asyncio.sleep(delete_after * 60)
            await interaction.channel.delete(reason="تذكرة مغلقة")
        else:
            await interaction.channel.set_permissions(
                interaction.guild.default_role,
                send_messages=False
            )
            await interaction.followup.send(embed=embed)
        
        # DM للمستخدم
        if config.get("dm_user_on_close", True):
            try:
                user = interaction.guild.get_member(ticket["user_id"])
                if user:
                    dm_embed = discord.Embed(
                        title="🔒 تم إغلاق تذكرتك",
                        description=f"تم إغلاق تذكرتك #{ticket['ticket_number']} في سيرفر **{interaction.guild.name}**",
                        color=discord.Color.blue()
                    )
                    if reason:
                        dm_embed.add_field(name="السبب", value=reason)
                    await user.send(embed=dm_embed)
            except:
                pass
    
    @ticket_group.command(
        name="add",
        description="إضافة عضو إلى التذكرة"
    )
    @app_commands.describe(
        user="العضو المراد إضافته"
    )
    async def ticket_add(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """إضافة عضو للتذكرة"""
        ticket = await self.ticket_system.get_ticket(
            interaction.guild.id,
            interaction.channel.id
        )
        
        if not ticket:
            await interaction.response.send_message(
                "❌ هذه ليست قناة تذكرة",
                ephemeral=True
            )
            return
        
        # التحقق من الصلاحيات
        is_owner = interaction.user.id == ticket["user_id"]
        has_perms = interaction.user.guild_permissions.manage_channels
        
        config = await self.ticket_system.get_guild_config(interaction.guild.id)
        support_roles = config.get("support_roles", [])
        is_support = any(
            role.id in support_roles
            for role in interaction.user.roles
        )
        
        if not (is_owner or has_perms or is_support):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية لإضافة أعضاء لهذه التذكرة",
                ephemeral=True
            )
            return
        
        # إضافة الأذونات للقناة
        await interaction.channel.set_permissions(
            user,
            view_channel=True,
            send_messages=True,
            read_message_history=True,
            attach_files=True,
            embed_links=True
        )
        
        # إضافة للمشاركين في قاعدة البيانات
        await self.ticket_system.add_participant(
            interaction.guild.id,
            interaction.channel.id,
            user.id
        )
        
        embed = discord.Embed(
            title="✅ تمت الإضافة",
            description=f"تمت إضافة {user.mention} إلى التذكرة",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @ticket_group.command(
        name="remove",
        description="إزالة عضو من التذكرة"
    )
    @app_commands.describe(
        user="العضو المراد إزالته"
    )
    async def ticket_remove(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """إزالة عضو من التذكرة"""
        ticket = await self.ticket_system.get_ticket(
            interaction.guild.id,
            interaction.channel.id
        )
        
        if not ticket:
            await interaction.response.send_message(
                "❌ هذه ليست قناة تذكرة",
                ephemeral=True
            )
            return
        
        # التحقق من الصلاحيات
        is_owner = interaction.user.id == ticket["user_id"]
        has_perms = interaction.user.guild_permissions.manage_channels
        
        config = await self.ticket_system.get_guild_config(interaction.guild.id)
        support_roles = config.get("support_roles", [])
        is_support = any(
            role.id in support_roles
            for role in interaction.user.roles
        )
        
        if not (is_owner or has_perms or is_support):
            await interaction.response.send_message(
                "❌ ليس لديك صلاحية لإزالة أعضاء من هذه التذكرة",
                ephemeral=True
            )
            return
        
        # منع إزالة صاحب التذكرة
        if user.id == ticket["user_id"]:
            await interaction.response.send_message(
                "❌ لا يمكن إزالة صاحب التذكرة",
                ephemeral=True
            )
            return
        
        # إزالة الأذونات من القناة
        await interaction.channel.set_permissions(
            user,
            overwrite=None
        )
        
        # إزالة من المشاركين في قاعدة البيانات
        await self.ticket_system.remove_participant(
            interaction.guild.id,
            interaction.channel.id,
            user.id
        )
        
        embed = discord.Embed(
            title="✅ تمت الإزالة",
            description=f"تمت إزالة {user.mention} من التذكرة",
            color=discord.Color.orange()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @ticket_group.command(
        name="claim",
        description="المطالبة بالتذكرة (للدعم الفني)"
    )
    async def ticket_claim(self, interaction: discord.Interaction):
        """المطالبة بالتذكرة"""
        ticket = await self.ticket_system.get_ticket(
            interaction.guild.id,
            interaction.channel.id
        )
        
        if not ticket:
            await interaction.response.send_message(
                "❌ هذه ليست قناة تذكرة",
                ephemeral=True
            )
            return
        
        # التحقق من أن المستخدم من فريق الدعم
        config = await self.ticket_system.get_guild_config(interaction.guild.id)
        support_roles = config.get("support_roles", [])
        is_support = any(
            role.id in support_roles
            for role in interaction.user.roles
        )
        
        if not is_support and not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(
                "❌ يجب أن تكون من فريق الدعم لاستخدام هذا الأمر",
                ephemeral=True
            )
            return
        
        # التحقق إذا كانت التذكرة محجوزة بالفعل
        if ticket.get("assigned_to"):
            assigned_user = interaction.guild.get_member(ticket["assigned_to"])
            if assigned_user:
                await interaction.response.send_message(
                    f"❌ هذه التذكرة محجوزة بالفعل من قبل {assigned_user.mention}",
                    ephemeral=True
                )
                return
        
        # حجز التذكرة
        await self.ticket_system.update_ticket(
            interaction.guild.id,
            interaction.channel.id,
            {
                "assigned_to": interaction.user.id,
                "status": "in_progress"
            }
        )
        
        embed = discord.Embed(
            title="✅ تم حجز التذكرة",
            description=f"{interaction.user.mention} يعمل الآن على هذه التذكرة",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed)
    
    @ticket_group.command(
        name="transcript",
        description="حفظ نص محادثة التذكرة"
    )
    async def ticket_transcript(self, interaction: discord.Interaction):
        """حفظ نص المحادثة"""
        await interaction.response.defer(ephemeral=True)
        
        ticket = await self.ticket_system.get_ticket(
            interaction.guild.id,
            interaction.channel.id
        )
        
        if not ticket:
            await interaction.followup.send(
                "❌ هذه ليست قناة تذكرة",
                ephemeral=True
            )
            return
        
        # جمع الرسائل
        messages = await self.ticket_system.collect_messages_for_transcript(
            interaction.channel
        )
        
        # حفظ النص
        transcript = await self.ticket_system.save_transcript(
            interaction.guild.id,
            ticket,
            messages
        )
        
        embed = discord.Embed(
            title="✅ تم حفظ النص",
            description=f"تم حفظ نص المحادثة بنجاح",
            color=discord.Color.green()
        )
        embed.add_field(name="عدد الرسائل", value=str(len(messages)))
        embed.add_field(
            name="رقم التذكرة",
            value=f"#{ticket['ticket_number']}"
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # إرسال النص لقناة النصوص إن وجدت
        config = await self.ticket_system.get_guild_config(interaction.guild.id)
        transcript_channel_id = config.get("transcript_channel_id")
        
        if transcript_channel_id:
            transcript_channel = interaction.guild.get_channel(transcript_channel_id)
            if transcript_channel:
                log_embed = discord.Embed(
                    title=f"📄 نص التذكرة #{ticket['ticket_number']}",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                log_embed.add_field(
                    name="المستخدم",
                    value=f"<@{ticket['user_id']}>",
                    inline=True
                )
                log_embed.add_field(
                    name="الفئة",
                    value=ticket['category'],
                    inline=True
                )
                log_embed.add_field(
                    name="عدد الرسائل",
                    value=str(len(messages)),
                    inline=True
                )
                
                await transcript_channel.send(embed=log_embed)
    
    # ====================================
    # أوامر الإعداد (Admin Only)
    # ====================================
    
    @app_commands.command(
        name="ticketsetup",
        description="إعداد نظام التذاكر (للإدارة)"
    )
    @app_commands.describe(
        enabled="تفعيل أو تعطيل نظام التذاكر",
        ticket_category="الكاتيجوري الذي ستُنشأ فيه التذاكر",
        transcript_channel="قناة حفظ نصوص المحادثات",
        logs_channel="قناة سجلات التذاكر",
        max_tickets="الحد الأقصى للتذاكر المفتوحة لكل مستخدم",
        delete_on_close="حذف القناة عند الإغلاق"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def ticketsetup(
        self,
        interaction: discord.Interaction,
        enabled: Optional[bool] = None,
        ticket_category: Optional[discord.CategoryChannel] = None,
        transcript_channel: Optional[discord.TextChannel] = None,
        logs_channel: Optional[discord.TextChannel] = None,
        max_tickets: Optional[int] = None,
        delete_on_close: Optional[bool] = None
    ):
        """إعداد نظام التذاكر"""
        await interaction.response.defer(ephemeral=True)
        
        config = await self.ticket_system.get_guild_config(interaction.guild.id)
        updates = {}
        
        if enabled is not None:
            updates["enabled"] = enabled
        
        if ticket_category:
            updates["ticket_category_id"] = ticket_category.id
        
        if transcript_channel:
            updates["transcript_channel_id"] = transcript_channel.id
        
        if logs_channel:
            updates["logs_channel_id"] = logs_channel.id
        
        if max_tickets is not None:
            if max_tickets < 1 or max_tickets > 10:
                await interaction.followup.send(
                    "❌ الحد الأقصى للتذاكر يجب أن يكون بين 1-10",
                    ephemeral=True
                )
                return
            updates["max_tickets_per_user"] = max_tickets
        
        if delete_on_close is not None:
            updates["delete_on_close"] = delete_on_close
        
        if not updates:
            # عرض الإعدادات الحالية
            embed = discord.Embed(
                title="⚙️ إعدادات نظام التذاكر",
                description="الإعدادات الحالية:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="الحالة",
                value="🟢 مفعل" if config.get("enabled") else "🔴 معطل",
                inline=True
            )
            
            cat_id = config.get("ticket_category_id")
            cat_text = f"<#{cat_id}>" if cat_id else "غير محدد"
            embed.add_field(
                name="كاتيجوري التذاكر",
                value=cat_text,
                inline=True
            )
            
            trans_id = config.get("transcript_channel_id")
            trans_text = f"<#{trans_id}>" if trans_id else "غير محدد"
            embed.add_field(
                name="قناة النصوص",
                value=trans_text,
                inline=True
            )
            
            logs_id = config.get("logs_channel_id")
            logs_text = f"<#{logs_id}>" if logs_id else "غير محدد"
            embed.add_field(
                name="قناة السجلات",
                value=logs_text,
                inline=True
            )
            
            embed.add_field(
                name="أقصى تذاكر لكل مستخدم",
                value=str(config.get("max_tickets_per_user", 3)),
                inline=True
            )
            
            embed.add_field(
                name="حذف عند الإغلاق",
                value="نعم" if config.get("delete_on_close") else "لا",
                inline=True
            )
            
            # الإحصائيات
            stats = await self.ticket_system.get_ticket_statistics(interaction.guild.id)
            embed.add_field(
                name="📊 الإحصائيات",
                value=f"**إجمالي التذاكر:** {stats['total_created']}\n"
                      f"**المغلقة:** {stats['total_closed']}\n"
                      f"**المفتوحة حالياً:** {stats['currently_open']}",
                inline=False
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # تطبيق التحديثات
        await self.ticket_system.update_guild_config(
            interaction.guild.id,
            updates
        )
        
        embed = discord.Embed(
            title="✅ تم تحديث الإعدادات",
            description="تم تحديث إعدادات نظام التذاكر بنجاح",
            color=discord.Color.green()
        )
        
        for key, value in updates.items():
            if key == "enabled":
                embed.add_field(
                    name="الحالة",
                    value="🟢 مفعل" if value else "🔴 معطل"
                )
            elif key == "ticket_category_id":
                embed.add_field(
                    name="كاتيجوري التذاكر",
                    value=f"<#{value}>"
                )
            elif key == "transcript_channel_id":
                embed.add_field(
                    name="قناة النصوص",
                    value=f"<#{value}>"
                )
            elif key == "logs_channel_id":
                embed.add_field(
                    name="قناة السجلات",
                    value=f"<#{value}>"
                )
            elif key == "max_tickets_per_user":
                embed.add_field(
                    name="أقصى تذاكر",
                    value=str(value)
                )
            elif key == "delete_on_close":
                embed.add_field(
                    name="حذف عند الإغلاق",
                    value="نعم" if value else "لا"
                )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # مجموعة أوامر ticketcategory
    category_group = app_commands.Group(
        name="ticketcategory",
        description="إدارة فئات التذاكر (للإدارة)"
    )
    
    @category_group.command(
        name="create",
        description="إنشاء فئة تذاكر جديدة"
    )
    @app_commands.describe(
        category_id="معرف فريد للفئة (بالإنجليزية بدون مسافات)",
        name="اسم الفئة",
        description="وصف الفئة",
        emoji="إيموجي الفئة",
        discord_category="الكاتيجوري الخاص بهذه الفئة (اختياري)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def category_create(
        self,
        interaction: discord.Interaction,
        category_id: str,
        name: str,
        description: str,
        emoji: str,
        discord_category: Optional[discord.CategoryChannel] = None
    ):
        """إنشاء فئة جديدة"""
        # التحقق من أن المعرف غير موجود
        existing = await self.ticket_system.get_category(
            interaction.guild.id,
            category_id
        )
        
        if existing:
            await interaction.response.send_message(
                f"❌ الفئة `{category_id}` موجودة بالفعل",
                ephemeral=True
            )
            return
        
        # إنشاء الفئة
        await self.ticket_system.create_category(
            guild_id=interaction.guild.id,
            category_id=category_id,
            name=name,
            description=description,
            emoji=emoji,
            discord_category_id=discord_category.id if discord_category else None
        )
        
        embed = discord.Embed(
            title="✅ تم إنشاء الفئة",
            description=f"{emoji} **{name}**",
            color=discord.Color.green()
        )
        embed.add_field(name="المعرف", value=f"`{category_id}`", inline=True)
        embed.add_field(name="الوصف", value=description, inline=False)
        
        if discord_category:
            embed.add_field(
                name="الكاتيجوري",
                value=discord_category.mention,
                inline=True
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @category_group.command(
        name="list",
        description="عرض جميع فئات التذاكر"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def category_list(self, interaction: discord.Interaction):
        """عرض جميع الفئات"""
        categories = await self.ticket_system.get_all_categories(
            interaction.guild.id,
            enabled_only=False
        )
        
        if not categories:
            await interaction.response.send_message(
                "❌ لا توجد فئات تذاكر",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📋 فئات التذاكر",
            description=f"إجمالي الفئات: {len(categories)}",
            color=discord.Color.blue()
        )
        
        for cat in categories:
            status = "🟢" if cat.get("enabled") else "🔴"
            embed.add_field(
                name=f"{status} {cat['emoji']} {cat['name']}",
                value=f"**المعرف:** `{cat['category_id']}`\n"
                      f"**الوصف:** {cat['description']}\n"
                      f"**عدد التذاكر:** {cat.get('ticket_count', 0)}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @category_group.command(
        name="toggle",
        description="تفعيل/تعطيل فئة تذاكر"
    )
    @app_commands.describe(
        category_id="معرف الفئة",
        enabled="التفعيل (نعم/لا)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def category_toggle(
        self,
        interaction: discord.Interaction,
        category_id: str,
        enabled: bool
    ):
        """تفعيل/تعطيل فئة"""
        success = await self.ticket_system.update_category(
            interaction.guild.id,
            category_id,
            {"enabled": enabled}
        )
        
        if not success:
            await interaction.response.send_message(
                f"❌ لم يتم العثور على الفئة `{category_id}`",
                ephemeral=True
            )
            return
        
        status = "مفعلة" if enabled else "معطلة"
        await interaction.response.send_message(
            f"✅ الفئة `{category_id}` الآن **{status}**",
            ephemeral=True
        )
    
    @category_group.command(
        name="delete",
        description="حذف فئة تذاكر"
    )
    @app_commands.describe(
        category_id="معرف الفئة المراد حذفها"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def category_delete(
        self,
        interaction: discord.Interaction,
        category_id: str
    ):
        """حذف فئة"""
        success = await self.ticket_system.delete_category(
            interaction.guild.id,
            category_id
        )
        
        if not success:
            await interaction.response.send_message(
                f"❌ لم يتم العثور على الفئة `{category_id}`",
                ephemeral=True
            )
            return
        
        await interaction.response.send_message(
            f"✅ تم حذف الفئة `{category_id}` بنجاح",
            ephemeral=True
        )
    
    @app_commands.command(
        name="ticketpanel",
        description="إنشاء لوحة التذاكر (زر إنشاء تذكرة)"
    )
    @app_commands.describe(
        channel="القناة التي ستُنشأ فيها اللوحة"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def ticketpanel(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None
    ):
        """إنشاء لوحة التذاكر"""
        await interaction.response.defer(ephemeral=True)
        
        target_channel = channel or interaction.channel
        
        # التحقق من أن النظام مفعل
        config = await self.ticket_system.get_guild_config(interaction.guild.id)
        if not config.get("enabled"):
            await interaction.followup.send(
                "❌ نظام التذاكر غير مفعل. استخدم `/ticketsetup enabled:True` لتفعيله",
                ephemeral=True
            )
            return
        
        # الحصول على الفئات
        categories = await self.ticket_system.get_all_categories(
            interaction.guild.id,
            enabled_only=True
        )
        
        if not categories:
            await interaction.followup.send(
                "❌ لا توجد فئات مفعلة. أنشئ فئة أولاً باستخدام `/ticketcategory create`",
                ephemeral=True
            )
            return
        
        # إنشاء Embed اللوحة
        embed = discord.Embed(
            title="🎫 نظام التذاكر",
            description="مرحباً بك في نظام الدعم الفني!\n\n"
                       "لإنشاء تذكرة دعم جديدة، اضغط على الزر أدناه واختر فئة تذكرتك.\n"
                       "سيتم إنشاء قناة خاصة لك للتواصل مع فريق الدعم.",
            color=discord.Color.blue()
        )
        
        # إضافة الفئات للعرض
        categories_text = "\n".join(
            f"{cat['emoji']} **{cat['name']}** - {cat['description']}"
            for cat in categories
        )
        embed.add_field(
            name="📋 الفئات المتاحة",
            value=categories_text,
            inline=False
        )
        
        embed.set_footer(text=f"{interaction.guild.name} Support System")
        
        # زر إنشاء التذكرة
        class CreateTicketButton(discord.ui.Button):
            def __init__(self, ticket_system: TicketSystem):
                super().__init__(
                    label="إنشاء تذكرة",
                    style=discord.ButtonStyle.green,
                    emoji="🎫",
                    custom_id="create_ticket_button"
                )
                self.ticket_system = ticket_system
            
            async def callback(self, interaction: discord.Interaction):
                # نفس منطق /ticket create
                can_create, message = await self.ticket_system.can_user_create_ticket(
                    interaction.guild.id,
                    interaction.user.id
                )
                
                if not can_create:
                    await interaction.response.send_message(
                        f"❌ {message}",
                        ephemeral=True
                    )
                    return
                
                categories = await self.ticket_system.get_all_categories(
                    interaction.guild.id,
                    enabled_only=True
                )
                
                view = TicketCategoryView(self.ticket_system, categories)
                
                panel_embed = discord.Embed(
                    title="🎫 إنشاء تذكرة دعم",
                    description="اختر فئة تذكرتك من القائمة أدناه:",
                    color=discord.Color.blue()
                )
                
                await interaction.response.send_message(
                    embed=panel_embed,
                    view=view,
                    ephemeral=True
                )
        
        view = discord.ui.View(timeout=None)
        view.add_item(CreateTicketButton(self.ticket_system))
        
        # إرسال اللوحة
        panel_message = await target_channel.send(embed=embed, view=view)
        
        # حفظ معرف اللوحة
        await self.ticket_system.update_guild_config(
            interaction.guild.id,
            {
                "panel_channel_id": target_channel.id,
                "panel_message_id": panel_message.id
            }
        )
        
        await interaction.followup.send(
            f"✅ تم إنشاء لوحة التذاكر في {target_channel.mention}",
            ephemeral=True
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketsCog(bot))

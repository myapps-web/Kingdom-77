"""
Auto-Messages Cog for Kingdom-77 Bot

Discord commands for managing automatic message responses.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
from datetime import datetime

# UI Components
from discord import ui


class AutoMessageModal(ui.Modal, title="إنشاء رسالة تلقائية"):
    """Modal for creating auto-message"""
    
    name = ui.TextInput(
        label="اسم الرسالة",
        placeholder="welcome_message",
        required=True,
        max_length=50
    )
    
    trigger_value = ui.TextInput(
        label="القيمة المحفزة (Keyword/Custom ID)",
        placeholder="مثال: مرحبا أو welcome_button",
        required=True,
        max_length=100
    )
    
    response_content = ui.TextInput(
        label="محتوى الرد (اختياري)",
        style=discord.TextStyle.paragraph,
        placeholder="أهلاً بك في السيرفر! 👋",
        required=False,
        max_length=2000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)


class EmbedBuilderModal(ui.Modal, title="Embed Builder - Nova Style"):
    """Modal for building rich embeds"""
    
    title = ui.TextInput(
        label="العنوان",
        placeholder="عنوان الEmbed",
        required=False,
        max_length=256
    )
    
    description = ui.TextInput(
        label="الوصف",
        style=discord.TextStyle.paragraph,
        placeholder="وصف الEmbed",
        required=False,
        max_length=4000
    )
    
    color = ui.TextInput(
        label="اللون (Hex)",
        placeholder="#5865F2",
        required=False,
        max_length=7
    )
    
    thumbnail = ui.TextInput(
        label="رابط الصورة المصغرة (اختياري)",
        placeholder="https://...",
        required=False,
        max_length=500
    )
    
    image = ui.TextInput(
        label="رابط الصورة الكبيرة (اختياري)",
        placeholder="https://...",
        required=False,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)


class ButtonBuilderModal(ui.Modal, title="إضافة زر"):
    """Modal for adding buttons"""
    
    label = ui.TextInput(
        label="نص الزر",
        placeholder="اضغط هنا",
        required=True,
        max_length=80
    )
    
    custom_id = ui.TextInput(
        label="Custom ID (أو URL للروابط)",
        placeholder="button_click_1",
        required=True,
        max_length=100
    )
    
    emoji = ui.TextInput(
        label="Emoji (اختياري)",
        placeholder="👋 أو :wave:",
        required=False,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)


class DropdownBuilderModal(ui.Modal, title="إضافة قائمة منسدلة"):
    """Modal for adding dropdown menus"""
    
    custom_id = ui.TextInput(
        label="Custom ID",
        placeholder="dropdown_menu_1",
        required=True,
        max_length=100
    )
    
    placeholder = ui.TextInput(
        label="النص الافتراضي",
        placeholder="اختر خياراً",
        required=True,
        max_length=150
    )
    
    options = ui.TextInput(
        label="الخيارات (سطر لكل خيار)",
        style=discord.TextStyle.paragraph,
        placeholder="Option 1:value1:وصف\nOption 2:value2:وصف",
        required=True,
        max_length=1000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)


class ConfirmDeleteView(ui.View):
    """Confirmation view for deletions"""
    
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.value = None
    
    @ui.button(label="✅ نعم، احذف", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا الزر ليس لك!", ephemeral=True)
            return
        
        self.value = True
        self.stop()
        await interaction.response.defer()
    
    @ui.button(label="❌ لا، إلغاء", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ هذا الزر ليس لك!", ephemeral=True)
            return
        
        self.value = False
        self.stop()
        await interaction.response.defer()


class AutoMessages(commands.Cog):
    """Auto-Messages System"""
    
    def __init__(self, bot):
        self.bot = bot
        self.automessage_system = None
    
    async def cog_load(self):
        """Initialize auto-message system"""
        self.automessage_system = self.bot.automessage_system
    
    # Group: /automessage
    automessage_group = app_commands.Group(
        name="automessage",
        description="إدارة الرسائل التلقائية"
    )
    
    # ==================== CREATE ====================
    
    @automessage_group.command(name="create", description="إنشاء رسالة تلقائية جديدة")
    @app_commands.describe(
        trigger_type="نوع المحفز (keyword: كلمة، button: زر، dropdown: قائمة)",
        response_type="نوع الرد (text: نص، embed: Embed، buttons: أزرار)"
    )
    async def automessage_create(
        self,
        interaction: discord.Interaction,
        trigger_type: Literal["keyword", "button", "dropdown"],
        response_type: Literal["text", "embed", "buttons", "dropdowns"]
    ):
        """Create a new auto-message"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server** لاستخدام هذا الأمر!",
                ephemeral=True
            )
            return
        
        # Show modal
        modal = AutoMessageModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        # Get values
        name = modal.name.value
        trigger_value = modal.trigger_value.value
        response_content = modal.response_content.value if modal.response_content.value else None
        
        # Create message
        try:
            message_data = await self.automessage_system.create_message(
                guild_id=str(interaction.guild.id),
                name=name,
                trigger_type=trigger_type,
                trigger_value=trigger_value,
                response_type=response_type,
                response_content=response_content,
                settings={
                    "case_sensitive": False,
                    "exact_match": False,
                    "cooldown_seconds": 0,
                    "auto_delete_after": 0,
                    "dm_response": False
                }
            )
            
            embed = discord.Embed(
                title="✅ تم إنشاء الرسالة التلقائية",
                description=f"**الاسم:** `{name}`\n"
                           f"**نوع المحفز:** {trigger_type}\n"
                           f"**قيمة المحفز:** `{trigger_value}`\n"
                           f"**نوع الرد:** {response_type}",
                color=discord.Color.green()
            )
            
            if response_type in ["embed", "buttons", "dropdowns"]:
                embed.add_field(
                    name="📝 الخطوة التالية",
                    value=f"استخدم `/automessage builder` لإنشاء Embed\n"
                          f"أو `/automessage add-button` لإضافة أزرار",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ فشل إنشاء الرسالة: {str(e)}",
                ephemeral=True
            )
    
    # ==================== BUILDER ====================
    
    @automessage_group.command(name="builder", description="Embed Builder (Nova Style)")
    @app_commands.describe(
        message_name="اسم الرسالة التلقائية"
    )
    async def automessage_builder(
        self,
        interaction: discord.Interaction,
        message_name: str
    ):
        """Open Embed Builder"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        # Check if message exists
        message = await self.automessage_system.get_message(
            str(interaction.guild.id),
            message_name
        )
        
        if not message:
            await interaction.response.send_message(
                f"❌ الرسالة `{message_name}` غير موجودة!",
                ephemeral=True
            )
            return
        
        # Show modal
        modal = EmbedBuilderModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        # Build embed data
        embed_data = {
            "title": modal.title.value if modal.title.value else None,
            "description": modal.description.value if modal.description.value else None,
            "color": modal.color.value if modal.color.value else "#5865F2",
            "thumbnail": modal.thumbnail.value if modal.thumbnail.value else None,
            "image": modal.image.value if modal.image.value else None,
            "fields": [],
            "timestamp": True
        }
        
        # Update message
        success = await self.automessage_system.update_message(
            str(interaction.guild.id),
            message_name,
            {"response.embed": embed_data}
        )
        
        if success:
            # Show preview
            preview_embed = self.automessage_system.build_embed(embed_data)
            
            await interaction.followup.send(
                content=f"✅ تم تحديث Embed للرسالة `{message_name}`\n**المعاينة:**",
                embed=preview_embed,
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ فشل تحديث الEmbed!",
                ephemeral=True
            )
    
    # ==================== ADD BUTTON ====================
    
    @automessage_group.command(name="add-button", description="إضافة زر للرسالة")
    @app_commands.describe(
        message_name="اسم الرسالة التلقائية",
        style="نمط الزر (primary: أزرق، success: أخضر، danger: أحمر، link: رابط)"
    )
    async def automessage_add_button(
        self,
        interaction: discord.Interaction,
        message_name: str,
        style: Literal["primary", "secondary", "success", "danger", "link"]
    ):
        """Add button to auto-message"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        # Check if message exists
        message = await self.automessage_system.get_message(
            str(interaction.guild.id),
            message_name
        )
        
        if not message:
            await interaction.response.send_message(
                f"❌ الرسالة `{message_name}` غير موجودة!",
                ephemeral=True
            )
            return
        
        # Check button limit
        current_buttons = message["response"].get("buttons", [])
        if len(current_buttons) >= 25:
            await interaction.response.send_message(
                "❌ الحد الأقصى 25 زر للرسالة الواحدة!",
                ephemeral=True
            )
            return
        
        # Show modal
        modal = ButtonBuilderModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        # Build button data
        button_data = {
            "label": modal.label.value,
            "style": style,
            "custom_id": modal.custom_id.value if style != "link" else None,
            "url": modal.custom_id.value if style == "link" else None,
            "emoji": modal.emoji.value if modal.emoji.value else None,
            "disabled": False
        }
        
        # Add button
        current_buttons.append(button_data)
        success = await self.automessage_system.update_message(
            str(interaction.guild.id),
            message_name,
            {"response.buttons": current_buttons}
        )
        
        if success:
            await interaction.followup.send(
                f"✅ تم إضافة الزر للرسالة `{message_name}`\n"
                f"**الزر:** {modal.label.value} ({style})\n"
                f"**عدد الأزرار:** {len(current_buttons)}",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ فشل إضافة الزر!",
                ephemeral=True
            )
    
    # ==================== ADD DROPDOWN ====================
    
    @automessage_group.command(name="add-dropdown", description="إضافة قائمة منسدلة")
    @app_commands.describe(
        message_name="اسم الرسالة التلقائية"
    )
    async def automessage_add_dropdown(
        self,
        interaction: discord.Interaction,
        message_name: str
    ):
        """Add dropdown menu to auto-message"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        # Check if message exists
        message = await self.automessage_system.get_message(
            str(interaction.guild.id),
            message_name
        )
        
        if not message:
            await interaction.response.send_message(
                f"❌ الرسالة `{message_name}` غير موجودة!",
                ephemeral=True
            )
            return
        
        # Check dropdown limit
        current_dropdowns = message["response"].get("dropdowns", [])
        if len(current_dropdowns) >= 5:
            await interaction.response.send_message(
                "❌ الحد الأقصى 5 قوائم منسدلة للرسالة الواحدة!",
                ephemeral=True
            )
            return
        
        # Show modal
        modal = DropdownBuilderModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        # Parse options (format: label:value:description)
        options = []
        for line in modal.options.value.strip().split("\n"):
            if not line.strip():
                continue
            
            parts = line.split(":", 2)
            option = {
                "label": parts[0].strip(),
                "value": parts[1].strip() if len(parts) > 1 else parts[0].strip(),
                "description": parts[2].strip() if len(parts) > 2 else None,
                "default": False
            }
            options.append(option)
        
        if len(options) == 0:
            await interaction.followup.send(
                "❌ يجب إضافة خيار واحد على الأقل!",
                ephemeral=True
            )
            return
        
        if len(options) > 25:
            await interaction.followup.send(
                "❌ الحد الأقصى 25 خيار للقائمة الواحدة!",
                ephemeral=True
            )
            return
        
        # Build dropdown data
        dropdown_data = {
            "custom_id": modal.custom_id.value,
            "placeholder": modal.placeholder.value,
            "min_values": 1,
            "max_values": 1,
            "options": options
        }
        
        # Add dropdown
        current_dropdowns.append(dropdown_data)
        success = await self.automessage_system.update_message(
            str(interaction.guild.id),
            message_name,
            {"response.dropdowns": current_dropdowns}
        )
        
        if success:
            await interaction.followup.send(
                f"✅ تم إضافة القائمة المنسدلة للرسالة `{message_name}`\n"
                f"**Custom ID:** `{modal.custom_id.value}`\n"
                f"**عدد الخيارات:** {len(options)}",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ فشل إضافة القائمة!",
                ephemeral=True
            )
    
    # ==================== LIST ====================
    
    @automessage_group.command(name="list", description="عرض جميع الرسائل التلقائية")
    @app_commands.describe(
        show_disabled="عرض الرسائل المعطلة أيضاً"
    )
    async def automessage_list(
        self,
        interaction: discord.Interaction,
        show_disabled: bool = False
    ):
        """List all auto-messages"""
        await interaction.response.defer(ephemeral=True)
        
        messages = await self.automessage_system.get_all_messages(
            str(interaction.guild.id),
            enabled_only=not show_disabled
        )
        
        if not messages:
            await interaction.followup.send(
                "📭 لا توجد رسائل تلقائية في هذا السيرفر!",
                ephemeral=True
            )
            return
        
        # Build embed
        embed = discord.Embed(
            title=f"📋 الرسائل التلقائية ({len(messages)})",
            description=f"السيرفر: **{interaction.guild.name}**",
            color=discord.Color.blue()
        )
        
        for message in messages[:10]:  # Limit to 10
            status = "✅" if message["settings"]["enabled"] else "❌"
            trigger_type = message["trigger"]["type"]
            trigger_value = message["trigger"]["value"]
            total_triggers = message["statistics"]["total_triggers"]
            
            embed.add_field(
                name=f"{status} {message['name']}",
                value=f"**المحفز:** {trigger_type} (`{trigger_value}`)\n"
                      f"**الاستخدامات:** {total_triggers} مرة",
                inline=True
            )
        
        if len(messages) > 10:
            embed.set_footer(text=f"يتم عرض 10 من أصل {len(messages)} رسالة")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ==================== VIEW ====================
    
    @automessage_group.command(name="view", description="عرض تفاصيل رسالة معينة")
    @app_commands.describe(
        message_name="اسم الرسالة"
    )
    async def automessage_view(
        self,
        interaction: discord.Interaction,
        message_name: str
    ):
        """View auto-message details"""
        await interaction.response.defer(ephemeral=True)
        
        message = await self.automessage_system.get_message(
            str(interaction.guild.id),
            message_name
        )
        
        if not message:
            await interaction.followup.send(
                f"❌ الرسالة `{message_name}` غير موجودة!",
                ephemeral=True
            )
            return
        
        # Build embed
        status = "✅ مفعّلة" if message["settings"]["enabled"] else "❌ معطّلة"
        
        embed = discord.Embed(
            title=f"📄 {message['name']}",
            description=f"**الحالة:** {status}",
            color=discord.Color.green() if message["settings"]["enabled"] else discord.Color.red()
        )
        
        # Trigger info
        trigger = message["trigger"]
        embed.add_field(
            name="🎯 المحفز",
            value=f"**النوع:** {trigger['type']}\n"
                  f"**القيمة:** `{trigger['value']}`\n"
                  f"**Case Sensitive:** {'نعم' if trigger.get('case_sensitive') else 'لا'}\n"
                  f"**Exact Match:** {'نعم' if trigger.get('exact_match') else 'لا'}",
            inline=False
        )
        
        # Response info
        response = message["response"]
        response_info = f"**النوع:** {response['type']}\n"
        
        if response.get("content"):
            response_info += f"**النص:** {response['content'][:100]}...\n"
        
        if response.get("embed"):
            response_info += "**Embed:** نعم ✅\n"
        
        if response.get("buttons"):
            response_info += f"**الأزرار:** {len(response['buttons'])}\n"
        
        if response.get("dropdowns"):
            response_info += f"**القوائم:** {len(response['dropdowns'])}\n"
        
        embed.add_field(
            name="💬 الرد",
            value=response_info,
            inline=False
        )
        
        # Settings
        settings = message["settings"]
        settings_info = ""
        
        if settings.get("cooldown_seconds", 0) > 0:
            settings_info += f"**Cooldown:** {settings['cooldown_seconds']}s\n"
        
        if settings.get("auto_delete_after", 0) > 0:
            settings_info += f"**Auto-Delete:** {settings['auto_delete_after']}s\n"
        
        if settings.get("dm_response"):
            settings_info += "**DM Response:** نعم ✅\n"
        
        if settings.get("allowed_roles"):
            settings_info += f"**الرتب المسموحة:** {len(settings['allowed_roles'])}\n"
        
        if settings.get("allowed_channels"):
            settings_info += f"**القنوات المسموحة:** {len(settings['allowed_channels'])}\n"
        
        if settings_info:
            embed.add_field(
                name="⚙️ الإعدادات",
                value=settings_info,
                inline=False
            )
        
        # Statistics
        stats = message["statistics"]
        embed.add_field(
            name="📊 الإحصائيات",
            value=f"**الاستخدامات:** {stats['total_triggers']} مرة\n"
                  f"**آخر استخدام:** {stats.get('last_triggered', 'لم يُستخدم بعد')}",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ==================== TOGGLE ====================
    
    @automessage_group.command(name="toggle", description="تفعيل/تعطيل رسالة تلقائية")
    @app_commands.describe(
        message_name="اسم الرسالة"
    )
    async def automessage_toggle(
        self,
        interaction: discord.Interaction,
        message_name: str
    ):
        """Toggle auto-message enabled/disabled"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        success, new_state = await self.automessage_system.toggle_message(
            str(interaction.guild.id),
            message_name
        )
        
        if success:
            status = "✅ تم التفعيل" if new_state else "❌ تم التعطيل"
            await interaction.followup.send(
                f"{status} للرسالة `{message_name}`",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ فشل تعديل الرسالة! تأكد من وجود الرسالة `{message_name}`",
                ephemeral=True
            )
    
    # ==================== DELETE ====================
    
    @automessage_group.command(name="delete", description="حذف رسالة تلقائية")
    @app_commands.describe(
        message_name="اسم الرسالة"
    )
    async def automessage_delete(
        self,
        interaction: discord.Interaction,
        message_name: str
    ):
        """Delete an auto-message"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        # Check if exists
        message = await self.automessage_system.get_message(
            str(interaction.guild.id),
            message_name
        )
        
        if not message:
            await interaction.response.send_message(
                f"❌ الرسالة `{message_name}` غير موجودة!",
                ephemeral=True
            )
            return
        
        # Confirmation
        view = ConfirmDeleteView(interaction.user.id)
        await interaction.response.send_message(
            f"⚠️ هل أنت متأكد من حذف الرسالة `{message_name}`؟\n"
            f"**سيتم حذف:** الEmbed، الأزرار، القوائم، والإحصائيات!",
            view=view,
            ephemeral=True
        )
        
        await view.wait()
        
        if view.value:
            success = await self.automessage_system.delete_message(
                str(interaction.guild.id),
                message_name
            )
            
            if success:
                await interaction.edit_original_response(
                    content=f"✅ تم حذف الرسالة `{message_name}` بنجاح!",
                    view=None
                )
            else:
                await interaction.edit_original_response(
                    content="❌ فشل حذف الرسالة!",
                    view=None
                )
        else:
            await interaction.edit_original_response(
                content="❌ تم إلغاء الحذف",
                view=None
            )
    
    # ==================== TEST ====================
    
    @automessage_group.command(name="test", description="اختبار رسالة تلقائية")
    @app_commands.describe(
        message_name="اسم الرسالة"
    )
    async def automessage_test(
        self,
        interaction: discord.Interaction,
        message_name: str
    ):
        """Test an auto-message"""
        await interaction.response.defer(ephemeral=True)
        
        message = await self.automessage_system.get_message(
            str(interaction.guild.id),
            message_name
        )
        
        if not message:
            await interaction.followup.send(
                f"❌ الرسالة `{message_name}` غير موجودة!",
                ephemeral=True
            )
            return
        
        # Send test response
        await interaction.followup.send(
            f"🧪 **اختبار الرسالة:** `{message_name}`\n"
            f"**النوع:** {message['trigger']['type']} → {message['response']['type']}",
            ephemeral=True
        )
        
        # Send actual message
        sent = await self.automessage_system.send_auto_response(
            message,
            interaction.channel,
            interaction.user
        )
        
        if not sent:
            await interaction.followup.send(
                "❌ فشل إرسال الرسالة! تحقق من الإعدادات",
                ephemeral=True
            )
    
    # ==================== STATS ====================
    
    @automessage_group.command(name="stats", description="إحصائيات الرسائل التلقائية")
    async def automessage_stats(self, interaction: discord.Interaction):
        """View auto-messages statistics"""
        await interaction.response.defer(ephemeral=True)
        
        stats = await self.automessage_system.get_statistics(str(interaction.guild.id))
        
        embed = discord.Embed(
            title="📊 إحصائيات الرسائل التلقائية",
            description=f"السيرفر: **{interaction.guild.name}**",
            color=discord.Color.blue()
        )
        
        # Overall stats
        embed.add_field(
            name="📈 إجمالي",
            value=f"**الرسائل:** {stats['total_messages']}\n"
                  f"**المفعّلة:** {stats['enabled_messages']}\n"
                  f"**المعطّلة:** {stats['disabled_messages']}\n"
                  f"**الاستخدامات:** {stats['total_triggers']}",
            inline=False
        )
        
        # By type
        if stats.get("by_type"):
            type_text = "\n".join([
                f"**{t}:** {count}"
                for t, count in stats["by_type"].items()
            ])
            embed.add_field(
                name="📋 حسب النوع",
                value=type_text,
                inline=False
            )
        
        # Most used
        if stats.get("most_used"):
            most_used_text = "\n".join([
                f"**{m['name']}** - {m['triggers']} ({m['type']})"
                for m in stats["most_used"][:5]
            ])
            embed.add_field(
                name="🔥 الأكثر استخداماً",
                value=most_used_text,
                inline=False
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ==================== SETTINGS ====================
    
    @automessage_group.command(name="settings", description="تعديل إعدادات رسالة")
    @app_commands.describe(
        message_name="اسم الرسالة",
        cooldown="Cooldown بالثواني (0 = بدون)",
        auto_delete="حذف تلقائي بعد X ثواني (0 = بدون)",
        dm_response="إرسال في DM بدلاً من القناة"
    )
    async def automessage_settings(
        self,
        interaction: discord.Interaction,
        message_name: str,
        cooldown: Optional[int] = None,
        auto_delete: Optional[int] = None,
        dm_response: Optional[bool] = None
    ):
        """Update auto-message settings"""
        # Check permissions
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ تحتاج صلاحية **Manage Server**!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Check if exists
        message = await self.automessage_system.get_message(
            str(interaction.guild.id),
            message_name
        )
        
        if not message:
            await interaction.followup.send(
                f"❌ الرسالة `{message_name}` غير موجودة!",
                ephemeral=True
            )
            return
        
        # Build updates
        updates = {}
        changes = []
        
        if cooldown is not None:
            updates["settings.cooldown_seconds"] = cooldown
            changes.append(f"**Cooldown:** {cooldown}s")
        
        if auto_delete is not None:
            updates["settings.auto_delete_after"] = auto_delete
            changes.append(f"**Auto-Delete:** {auto_delete}s")
        
        if dm_response is not None:
            updates["settings.dm_response"] = dm_response
            changes.append(f"**DM Response:** {'نعم' if dm_response else 'لا'}")
        
        if not updates:
            await interaction.followup.send(
                "❌ لم تحدد أي إعدادات للتعديل!",
                ephemeral=True
            )
            return
        
        # Apply updates
        success = await self.automessage_system.update_message(
            str(interaction.guild.id),
            message_name,
            updates
        )
        
        if success:
            changes_text = "\n".join(changes)
            await interaction.followup.send(
                f"✅ تم تحديث إعدادات الرسالة `{message_name}`\n\n{changes_text}",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                "❌ فشل تحديث الإعدادات!",
                ephemeral=True
            )
    
    # ==================== EVENT LISTENERS ====================
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Handle keyword triggers"""
        # Ignore bots and DMs
        if message.author.bot or not message.guild:
            return
        
        # Find matching keyword
        await self.automessage_system.handle_keyword_trigger(
            str(message.guild.id),
            message.content,
            message.channel,
            message.author
        )
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle button and dropdown triggers"""
        if interaction.type not in [
            discord.InteractionType.component,
        ]:
            return
        
        if not interaction.guild:
            return
        
        # Button click
        if interaction.data.get("component_type") == 2:  # Button
            custom_id = interaction.data.get("custom_id")
            if custom_id:
                await self.automessage_system.handle_button_trigger(
                    str(interaction.guild.id),
                    custom_id,
                    interaction
                )
        
        # Dropdown selection
        elif interaction.data.get("component_type") == 3:  # Select menu
            custom_id = interaction.data.get("custom_id")
            values = interaction.data.get("values", [])
            
            if custom_id and values:
                await self.automessage_system.handle_dropdown_trigger(
                    str(interaction.guild.id),
                    custom_id,
                    values[0],
                    interaction
                )


async def setup(bot):
    await bot.add_cog(AutoMessages(bot))

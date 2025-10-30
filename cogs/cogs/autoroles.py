"""
Auto-Roles Cog - أوامر نظام الرتب التلقائية
Kingdom-77 Bot v3.0

الأوامر:
- /reactionrole create/add/remove/edit/delete/list/refresh
- /levelrole add/remove/list
- /joinrole add/remove/list
- /autoroles config
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
from datetime import datetime
import re

from autoroles import AutoRoleSystem
from database import get_db


class ReactionRoleModal(discord.ui.Modal, title="إنشاء Reaction Role"):
    """نموذج إنشاء Reaction Role"""
    
    title_input = discord.ui.TextInput(
        label="العنوان",
        placeholder="اختر أدوارك",
        style=discord.TextStyle.short,
        required=True,
        max_length=100
    )
    
    description_input = discord.ui.TextInput(
        label="الوصف",
        placeholder="اضغط على الإيموجي للحصول على الرتبة المناسبة",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )
    
    def __init__(self, autorole_system: AutoRoleSystem, channel: discord.TextChannel, mode: str):
        super().__init__()
        self.autorole_system = autorole_system
        self.channel = channel
        self.mode = mode
    
    async def on_submit(self, interaction: discord.Interaction):
        """عند إرسال النموذج"""
        await interaction.response.defer(ephemeral=True)
        
        # إنشاء الرسالة
        embed = discord.Embed(
            title=self.title_input.value,
            description=self.description_input.value,
            color=discord.Color.blue()
        )
        embed.set_footer(text="اضغط على الإيموجي للحصول على الرتبة")
        
        try:
            message = await self.channel.send(embed=embed)
            
            # حفظ في قاعدة البيانات
            await self.autorole_system.create_reaction_role(
                guild_id=interaction.guild.id,
                message_id=message.id,
                channel_id=self.channel.id,
                title=self.title_input.value,
                description=self.description_input.value,
                mode=self.mode
            )
            
            await interaction.followup.send(
                f"✅ تم إنشاء Reaction Role بنجاح!\n"
                f"📍 {message.jump_url}\n\n"
                f"استخدم `/reactionrole add` لإضافة رتب",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ حدث خطأ: {str(e)}",
                ephemeral=True
            )


class AutoRolesCog(commands.Cog):
    """نظام الرتب التلقائية"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = None
        self.autorole_system = None
    
    async def cog_load(self):
        """تحميل الـ Cog"""
        self.db = await get_db()
        self.autorole_system = AutoRoleSystem(self.db)
        print("✅ Auto-Roles Cog loaded successfully")
    
    # ====================================
    # Reaction Roles Commands
    # ====================================
    
    reaction_group = app_commands.Group(
        name="reactionrole",
        description="أوامر Reaction Roles"
    )
    
    @reaction_group.command(
        name="create",
        description="إنشاء Reaction Role جديد"
    )
    @app_commands.describe(
        channel="القناة التي ستُنشأ فيها الرسالة",
        mode="نمط العمل (toggle: تشغيل/إيقاف، unique: رتبة واحدة فقط)"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_create(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        mode: Literal["toggle", "unique", "multiple"] = "toggle"
    ):
        """إنشاء Reaction Role جديد"""
        # فتح النموذج
        modal = ReactionRoleModal(self.autorole_system, channel, mode)
        await interaction.response.send_modal(modal)
    
    @reaction_group.command(
        name="add",
        description="إضافة رتبة إلى Reaction Role"
    )
    @app_commands.describe(
        message_id="معرف الرسالة",
        emoji="الإيموجي",
        role="الرتبة",
        label="التسمية (اختياري)",
        description="الوصف (اختياري)"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_add(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str,
        role: discord.Role,
        label: Optional[str] = None,
        description: Optional[str] = None
    ):
        """إضافة رتبة إلى Reaction Role"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.followup.send(
                "❌ معرف الرسالة غير صحيح",
                ephemeral=True
            )
            return
        
        # التحقق من وجود الـ Reaction Role
        rr = await self.autorole_system.get_reaction_role(
            interaction.guild.id,
            msg_id
        )
        
        if not rr:
            await interaction.followup.send(
                "❌ لم يتم العثور على Reaction Role لهذه الرسالة",
                ephemeral=True
            )
            return
        
        # التحقق من عدم وجود الإيموجي بالفعل
        from database.autoroles_schema import parse_emoji, emojis_match
        parsed_emoji = parse_emoji(emoji)
        
        for r in rr.get("roles", []):
            if emojis_match(r["emoji"], parsed_emoji):
                await interaction.followup.send(
                    "❌ هذا الإيموجي مستخدم بالفعل",
                    ephemeral=True
                )
                return
        
        # إضافة الرتبة
        success = await self.autorole_system.add_role_to_reaction(
            interaction.guild.id,
            msg_id,
            emoji,
            role.id,
            label or role.name,
            description
        )
        
        if not success:
            await interaction.followup.send(
                "❌ فشلت إضافة الرتبة",
                ephemeral=True
            )
            return
        
        # إضافة رد الفعل على الرسالة
        try:
            channel = interaction.guild.get_channel(rr["channel_id"])
            if channel:
                message = await channel.fetch_message(msg_id)
                await message.add_reaction(emoji)
        except:
            pass
        
        await interaction.followup.send(
            f"✅ تم إضافة {emoji} → {role.mention} بنجاح!",
            ephemeral=True
        )
    
    @reaction_group.command(
        name="remove",
        description="إزالة رتبة من Reaction Role"
    )
    @app_commands.describe(
        message_id="معرف الرسالة",
        emoji="الإيموجي"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_remove(
        self,
        interaction: discord.Interaction,
        message_id: str,
        emoji: str
    ):
        """إزالة رتبة من Reaction Role"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.followup.send(
                "❌ معرف الرسالة غير صحيح",
                ephemeral=True
            )
            return
        
        # إزالة الرتبة
        success = await self.autorole_system.remove_role_from_reaction(
            interaction.guild.id,
            msg_id,
            emoji
        )
        
        if not success:
            await interaction.followup.send(
                "❌ فشلت إزالة الرتبة أو الإيموجي غير موجود",
                ephemeral=True
            )
            return
        
        # إزالة رد الفعل من الرسالة
        try:
            rr = await self.autorole_system.get_reaction_role(
                interaction.guild.id,
                msg_id
            )
            if rr:
                channel = interaction.guild.get_channel(rr["channel_id"])
                if channel:
                    message = await channel.fetch_message(msg_id)
                    await message.clear_reaction(emoji)
        except:
            pass
        
        await interaction.followup.send(
            f"✅ تم إزالة {emoji} بنجاح!",
            ephemeral=True
        )
    
    @reaction_group.command(
        name="list",
        description="عرض جميع Reaction Roles"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_list(self, interaction: discord.Interaction):
        """عرض جميع Reaction Roles"""
        await interaction.response.defer(ephemeral=True)
        
        rrs = await self.autorole_system.get_all_reaction_roles(
            interaction.guild.id,
            enabled_only=False
        )
        
        if not rrs:
            await interaction.followup.send(
                "❌ لا توجد Reaction Roles في هذا السيرفر",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📋 Reaction Roles",
            description=f"إجمالي: {len(rrs)}",
            color=discord.Color.blue()
        )
        
        for rr in rrs[:10]:  # أول 10 فقط
            status = "🟢" if rr.get("enabled") else "🔴"
            mode_text = {
                "toggle": "تشغيل/إيقاف",
                "unique": "رتبة واحدة",
                "multiple": "عدة رتب"
            }.get(rr.get("mode"), "غير معروف")
            
            roles_count = len(rr.get("roles", []))
            
            try:
                channel = interaction.guild.get_channel(rr["channel_id"])
                message = await channel.fetch_message(rr["message_id"])
                link = message.jump_url
            except:
                link = "غير متوفر"
            
            embed.add_field(
                name=f"{status} {rr['title']}",
                value=f"**النمط:** {mode_text}\n"
                      f"**الرتب:** {roles_count}\n"
                      f"**الرابط:** [اضغط هنا]({link})",
                inline=False
            )
        
        if len(rrs) > 10:
            embed.set_footer(text=f"يتم عرض 10 من {len(rrs)}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @reaction_group.command(
        name="delete",
        description="حذف Reaction Role"
    )
    @app_commands.describe(
        message_id="معرف الرسالة"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_delete(
        self,
        interaction: discord.Interaction,
        message_id: str
    ):
        """حذف Reaction Role"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.followup.send(
                "❌ معرف الرسالة غير صحيح",
                ephemeral=True
            )
            return
        
        # حذف من قاعدة البيانات
        success = await self.autorole_system.delete_reaction_role(
            interaction.guild.id,
            msg_id
        )
        
        if not success:
            await interaction.followup.send(
                "❌ لم يتم العثور على Reaction Role",
                ephemeral=True
            )
            return
        
        await interaction.followup.send(
            "✅ تم حذف Reaction Role بنجاح!",
            ephemeral=True
        )
    
    @reaction_group.command(
        name="refresh",
        description="تحديث رسالة Reaction Role"
    )
    @app_commands.describe(
        message_id="معرف الرسالة"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def rr_refresh(
        self,
        interaction: discord.Interaction,
        message_id: str
    ):
        """تحديث رسالة Reaction Role"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg_id = int(message_id)
        except ValueError:
            await interaction.followup.send(
                "❌ معرف الرسالة غير صحيح",
                ephemeral=True
            )
            return
        
        # الحصول على البيانات
        rr = await self.autorole_system.get_reaction_role(
            interaction.guild.id,
            msg_id
        )
        
        if not rr:
            await interaction.followup.send(
                "❌ لم يتم العثور على Reaction Role",
                ephemeral=True
            )
            return
        
        # تحديث الرسالة
        try:
            channel = interaction.guild.get_channel(rr["channel_id"])
            message = await channel.fetch_message(msg_id)
            
            # إنشاء Embed جديد
            embed = discord.Embed(
                title=rr["title"],
                description=rr["description"],
                color=rr.get("color", 0x5865F2)
            )
            
            # إضافة الرتب
            roles_text = ""
            for r in rr.get("roles", []):
                role = interaction.guild.get_role(r["role_id"])
                if role:
                    roles_text += f"{r['emoji']} → {role.mention}\n"
            
            if roles_text:
                embed.add_field(name="الرتب المتاحة", value=roles_text, inline=False)
            
            embed.set_footer(text="اضغط على الإيموجي للحصول على الرتبة")
            
            await message.edit(embed=embed)
            
            # إضافة جميع الردود
            await message.clear_reactions()
            for r in rr.get("roles", []):
                try:
                    await message.add_reaction(r["emoji"])
                except:
                    pass
            
            await interaction.followup.send(
                "✅ تم تحديث Reaction Role بنجاح!",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ حدث خطأ: {str(e)}",
                ephemeral=True
            )
    
    # ====================================
    # Level Roles Commands
    # ====================================
    
    levelrole_group = app_commands.Group(
        name="levelrole",
        description="أوامر Level Roles"
    )
    
    @levelrole_group.command(
        name="add",
        description="إضافة رتبة لمستوى معين"
    )
    @app_commands.describe(
        level="المستوى المطلوب",
        role="الرتبة",
        remove_previous="إزالة رتب المستويات السابقة"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def lr_add(
        self,
        interaction: discord.Interaction,
        level: int,
        role: discord.Role,
        remove_previous: bool = False
    ):
        """إضافة Level Role"""
        await interaction.response.defer(ephemeral=True)
        
        # التحقق من المستوى
        if level < 1:
            await interaction.followup.send(
                "❌ المستوى يجب أن يكون 1 أو أكثر",
                ephemeral=True
            )
            return
        
        if level > 1000:
            await interaction.followup.send(
                "❌ المستوى لا يمكن أن يكون أكثر من 1000",
                ephemeral=True
            )
            return
        
        # التحقق من عدم وجود نفس الرتبة لنفس المستوى
        existing_roles = await self.autorole_system.get_roles_for_level(
            interaction.guild.id,
            level
        )
        
        for lr in existing_roles:
            if lr["role_id"] == role.id:
                await interaction.followup.send(
                    f"❌ الرتبة {role.mention} موجودة بالفعل للمستوى {level}",
                    ephemeral=True
                )
                return
        
        # إضافة Level Role
        try:
            await self.autorole_system.add_level_role(
                interaction.guild.id,
                level,
                role.id,
                remove_previous
            )
            
            remove_text = " (ستُزال الرتب السابقة)" if remove_previous else ""
            await interaction.followup.send(
                f"✅ تم إضافة {role.mention} للمستوى **{level}** بنجاح!{remove_text}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ حدث خطأ: {str(e)}",
                ephemeral=True
            )
    
    @levelrole_group.command(
        name="remove",
        description="إزالة رتبة من مستوى"
    )
    @app_commands.describe(
        level="المستوى",
        role="الرتبة (اختياري - لإزالة كل رتب المستوى اترك هذا فارغاً)"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def lr_remove(
        self,
        interaction: discord.Interaction,
        level: int,
        role: Optional[discord.Role] = None
    ):
        """إزالة Level Role"""
        await interaction.response.defer(ephemeral=True)
        
        success = await self.autorole_system.remove_level_role(
            interaction.guild.id,
            level,
            role.id if role else None
        )
        
        if not success:
            await interaction.followup.send(
                "❌ لم يتم العثور على Level Role",
                ephemeral=True
            )
            return
        
        if role:
            await interaction.followup.send(
                f"✅ تم إزالة {role.mention} من المستوى **{level}**",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"✅ تم إزالة جميع رتب المستوى **{level}**",
                ephemeral=True
            )
    
    @levelrole_group.command(
        name="list",
        description="عرض جميع Level Roles"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def lr_list(self, interaction: discord.Interaction):
        """عرض جميع Level Roles"""
        await interaction.response.defer(ephemeral=True)
        
        level_roles = await self.autorole_system.get_level_roles(
            interaction.guild.id,
            enabled_only=False
        )
        
        if not level_roles:
            await interaction.followup.send(
                "❌ لا توجد Level Roles في هذا السيرفر",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="📊 Level Roles",
            description=f"إجمالي: {len(level_roles)}",
            color=discord.Color.green()
        )
        
        # تجميع حسب المستوى
        from collections import defaultdict
        levels_dict = defaultdict(list)
        
        for lr in level_roles:
            levels_dict[lr["level"]].append(lr)
        
        # عرض كل مستوى
        for level in sorted(levels_dict.keys())[:20]:  # أول 20 مستوى
            roles_list = []
            for lr in levels_dict[level]:
                role = interaction.guild.get_role(lr["role_id"])
                if role:
                    status = "🟢" if lr.get("enabled") else "🔴"
                    remove_mark = " 🔄" if lr.get("remove_previous") else ""
                    roles_list.append(f"{status} {role.mention}{remove_mark}")
            
            if roles_list:
                embed.add_field(
                    name=f"المستوى {level}",
                    value="\n".join(roles_list),
                    inline=False
                )
        
        if len(levels_dict) > 20:
            embed.set_footer(text=f"يتم عرض 20 من {len(levels_dict)} مستوى")
        else:
            embed.set_footer(text="🔄 = يزيل الرتب السابقة")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ====================================
    # Join Roles Commands
    # ====================================
    
    joinrole_group = app_commands.Group(
        name="joinrole",
        description="أوامر Join Roles"
    )
    
    @joinrole_group.command(
        name="add",
        description="إضافة رتبة انضمام تلقائية"
    )
    @app_commands.describe(
        role="الرتبة",
        target="من سيحصل على الرتبة",
        delay="تأخير بالثواني (0 = فوري)"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def jr_add(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        target: Literal["all", "humans", "bots"] = "all",
        delay: int = 0
    ):
        """إضافة Join Role"""
        await interaction.response.defer(ephemeral=True)
        
        # التحقق من التأخير
        if delay < 0 or delay > 3600:
            await interaction.followup.send(
                "❌ التأخير يجب أن يكون بين 0-3600 ثانية",
                ephemeral=True
            )
            return
        
        # التحقق من عدم وجود نفس الرتبة
        existing = await self.autorole_system.get_join_roles(
            interaction.guild.id,
            enabled_only=False
        )
        
        for jr in existing:
            if jr["role_id"] == role.id:
                await interaction.followup.send(
                    f"❌ الرتبة {role.mention} موجودة بالفعل كـ Join Role",
                    ephemeral=True
                )
                return
        
        # إضافة Join Role
        try:
            await self.autorole_system.add_join_role(
                interaction.guild.id,
                role.id,
                target,
                delay
            )
            
            target_text = {
                "all": "الجميع",
                "humans": "المستخدمين فقط",
                "bots": "البوتات فقط"
            }.get(target, target)
            
            delay_text = f" (بعد {delay} ثانية)" if delay > 0 else ""
            
            await interaction.followup.send(
                f"✅ تم إضافة {role.mention} كـ Join Role\n"
                f"**الهدف:** {target_text}{delay_text}",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ حدث خطأ: {str(e)}",
                ephemeral=True
            )
    
    @joinrole_group.command(
        name="remove",
        description="إزالة رتبة انضمام"
    )
    @app_commands.describe(
        role="الرتبة"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def jr_remove(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):
        """إزالة Join Role"""
        await interaction.response.defer(ephemeral=True)
        
        success = await self.autorole_system.remove_join_role(
            interaction.guild.id,
            role.id
        )
        
        if not success:
            await interaction.followup.send(
                f"❌ الرتبة {role.mention} ليست Join Role",
                ephemeral=True
            )
            return
        
        await interaction.followup.send(
            f"✅ تم إزالة {role.mention} من Join Roles",
            ephemeral=True
        )
    
    @joinrole_group.command(
        name="list",
        description="عرض جميع Join Roles"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def jr_list(self, interaction: discord.Interaction):
        """عرض جميع Join Roles"""
        await interaction.response.defer(ephemeral=True)
        
        join_roles = await self.autorole_system.get_join_roles(
            interaction.guild.id,
            enabled_only=False
        )
        
        if not join_roles:
            await interaction.followup.send(
                "❌ لا توجد Join Roles في هذا السيرفر",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="👋 Join Roles",
            description=f"إجمالي: {len(join_roles)}",
            color=discord.Color.purple()
        )
        
        for jr in join_roles:
            role = interaction.guild.get_role(jr["role_id"])
            if not role:
                continue
            
            status = "🟢" if jr.get("enabled") else "🔴"
            
            target_text = {
                "all": "الجميع",
                "humans": "المستخدمين",
                "bots": "البوتات"
            }.get(jr.get("target_type"), "غير معروف")
            
            delay = jr.get("delay_seconds", 0)
            delay_text = f"{delay}s" if delay > 0 else "فوري"
            
            embed.add_field(
                name=f"{status} {role.name}",
                value=f"**الهدف:** {target_text}\n"
                      f"**التأخير:** {delay_text}",
                inline=True
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ====================================
    # Config Command
    # ====================================
    
    @app_commands.command(
        name="autoroles",
        description="عرض إحصائيات وإعدادات الرتب التلقائية"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def autoroles_config(self, interaction: discord.Interaction):
        """عرض إحصائيات الرتب التلقائية"""
        await interaction.response.defer(ephemeral=True)
        
        config = await self.autorole_system.get_guild_config(interaction.guild.id)
        stats = await self.autorole_system.get_statistics(interaction.guild.id)
        
        embed = discord.Embed(
            title="⚙️ نظام الرتب التلقائية",
            description="الإعدادات والإحصائيات",
            color=discord.Color.gold()
        )
        
        # الحالة
        rr_status = "🟢 مفعل" if config.get("reaction_roles_enabled") else "🔴 معطل"
        lr_status = "🟢 مفعل" if config.get("level_roles_enabled") else "🔴 معطل"
        jr_status = "🟢 مفعل" if config.get("join_roles_enabled") else "🔴 معطل"
        
        embed.add_field(
            name="📊 الحالة",
            value=f"**Reaction Roles:** {rr_status}\n"
                  f"**Level Roles:** {lr_status}\n"
                  f"**Join Roles:** {jr_status}",
            inline=False
        )
        
        # الإحصائيات
        embed.add_field(
            name="📈 الإحصائيات",
            value=f"**Reaction Roles:** {stats['total_reaction_roles']}\n"
                  f"**Level Roles:** {stats['total_level_roles']}\n"
                  f"**Join Roles:** {stats['total_join_roles']}\n"
                  f"**رتب ممنوحة:** {stats['total_roles_given']}\n"
                  f"**رتب مزالة:** {stats['total_roles_removed']}",
            inline=False
        )
        
        # الأوامر
        embed.add_field(
            name="💡 الأوامر",
            value="`/reactionrole` - إدارة Reaction Roles\n"
                  "`/levelrole` - إدارة Level Roles\n"
                  "`/joinrole` - إدارة Join Roles",
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoRolesCog(bot))

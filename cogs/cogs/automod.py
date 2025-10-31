"""
AutoMod Commands Cog
Slash commands for managing the AutoMod system.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
import logging
from datetime import datetime

from automod.automod_system import AutoModSystem
from database.automod_schema import AutoModSchema

logger = logging.getLogger('automod_cog')


class AutoModCog(commands.Cog):
    """AutoMod Management Commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.automod: Optional[AutoModSystem] = None
        logger.info("AutoMod Cog loaded")
    
    async def cog_load(self):
        """Initialize AutoMod system when cog loads"""
        if hasattr(self.bot, 'db') and hasattr(self.bot, 'redis'):
            self.automod = AutoModSystem(self.bot, self.bot.db, self.bot.redis)
            await self.automod.initialize()
            logger.info("AutoMod system initialized")
    
    # ==================== Event Handlers ====================
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Check messages for AutoMod violations"""
        if not self.automod or not message.guild or message.author.bot:
            return
        
        try:
            # Check message
            should_action, rule_type, reason = await self.automod.check_message(message)
            
            if should_action and rule_type and reason:
                # Get the triggered rule
                rules = await self.automod.get_guild_rules(message.guild.id, rule_type)
                if rules:
                    rule = rules[0]  # Get first matching rule
                    await self.automod.execute_action(message, rule, rule_type, reason)
        
        except Exception as e:
            logger.error(f"Error checking message: {e}")
    
    # ==================== Setup Commands ====================
    
    @app_commands.command(name="automod-setup", description="⚙️ إعداد نظام AutoMod للسيرفر")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_setup(self, interaction: discord.Interaction):
        """Setup AutoMod for the server"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            
            # Create default settings
            settings = await self.automod.get_guild_settings(guild_id, force_refresh=True)
            
            if settings:
                embed = discord.Embed(
                    title="✅ تم إعداد AutoMod",
                    description="تم إعداد نظام AutoMod بنجاح للسيرفر!",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(
                    name="📊 الحالة",
                    value=f"{'✅ مفعّل' if settings.get('enabled') else '❌ معطّل'}",
                    inline=True
                )
                embed.add_field(
                    name="📝 السجلات",
                    value=f"<#{settings['log_channel_id']}>" if settings.get('log_channel_id') else "❌ غير محددة",
                    inline=True
                )
                embed.add_field(
                    name="🔧 الخطوات التالية",
                    value=(
                        "1. `/automod-config` - تفعيل/تعطيل النظام\n"
                        "2. `/automod-rule-add` - إضافة قواعد\n"
                        "3. `/automod-logs` - عرض السجلات"
                    ),
                    inline=False
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send("❌ حدث خطأ في إعداد AutoMod", ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in automod_setup: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {str(e)}", ephemeral=True)
    
    # ==================== Configuration Commands ====================
    
    @app_commands.command(name="automod-config", description="⚙️ إعدادات AutoMod")
    @app_commands.describe(
        action="الإجراء",
        log_channel="قناة السجلات",
        dm_users="إرسال رسائل خاصة للمستخدمين",
        progressive_penalties="عقوبات تدريجية"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_config(
        self,
        interaction: discord.Interaction,
        action: Literal["enable", "disable", "status", "update"],
        log_channel: Optional[discord.TextChannel] = None,
        dm_users: Optional[bool] = None,
        progressive_penalties: Optional[bool] = None
    ):
        """Configure AutoMod settings"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            
            if action == "enable":
                success = await self.automod.update_guild_settings(guild_id, {"enabled": True})
                if success:
                    await interaction.followup.send("✅ تم تفعيل AutoMod", ephemeral=True)
                else:
                    await interaction.followup.send("❌ فشل تفعيل AutoMod", ephemeral=True)
            
            elif action == "disable":
                success = await self.automod.update_guild_settings(guild_id, {"enabled": False})
                if success:
                    await interaction.followup.send("✅ تم تعطيل AutoMod", ephemeral=True)
                else:
                    await interaction.followup.send("❌ فشل تعطيل AutoMod", ephemeral=True)
            
            elif action == "update":
                updates = {}
                if log_channel:
                    updates["log_channel_id"] = log_channel.id
                if dm_users is not None:
                    updates["dm_users"] = dm_users
                if progressive_penalties is not None:
                    updates["progressive_penalties"] = progressive_penalties
                
                if updates:
                    success = await self.automod.update_guild_settings(guild_id, updates)
                    if success:
                        await interaction.followup.send("✅ تم تحديث الإعدادات", ephemeral=True)
                    else:
                        await interaction.followup.send("❌ فشل تحديث الإعدادات", ephemeral=True)
                else:
                    await interaction.followup.send("❌ لم يتم تحديد أي إعدادات للتحديث", ephemeral=True)
            
            elif action == "status":
                settings = await self.automod.get_guild_settings(guild_id)
                
                embed = discord.Embed(
                    title="⚙️ إعدادات AutoMod",
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                embed.add_field(
                    name="📊 الحالة",
                    value=f"{'✅ مفعّل' if settings.get('enabled') else '❌ معطّل'}",
                    inline=True
                )
                embed.add_field(
                    name="📝 قناة السجلات",
                    value=f"<#{settings['log_channel_id']}>" if settings.get('log_channel_id') else "❌ غير محددة",
                    inline=True
                )
                embed.add_field(
                    name="💬 إرسال رسائل خاصة",
                    value="✅ نعم" if settings.get('dm_users', True) else "❌ لا",
                    inline=True
                )
                embed.add_field(
                    name="📈 العقوبات التدريجية",
                    value="✅ نعم" if settings.get('progressive_penalties', True) else "❌ لا",
                    inline=True
                )
                embed.add_field(
                    name="🛡️ القنوات المتجاهلة",
                    value=str(len(settings.get('ignored_channels', []))),
                    inline=True
                )
                embed.add_field(
                    name="👥 الأدوار المحصنة",
                    value=str(len(settings.get('immune_roles', []))),
                    inline=True
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in automod_config: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {str(e)}", ephemeral=True)
    
    # ==================== Rule Management Commands ====================
    
    @app_commands.command(name="automod-rule-add", description="➕ إضافة قاعدة AutoMod")
    @app_commands.describe(
        rule_type="نوع القاعدة",
        action="الإجراء عند المخالفة",
        name="اسم القاعدة",
        duration="المدة (بالثواني) - للـ Mute فقط"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_rule_add(
        self,
        interaction: discord.Interaction,
        rule_type: Literal["spam", "rate_limit", "links", "invites", "mentions", "caps", "emojis", "blacklist"],
        action: Literal["delete", "warn", "mute", "kick", "ban"],
        name: str,
        duration: Optional[int] = None
    ):
        """Add a new AutoMod rule"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            
            # Default rule settings based on type
            rule_settings = {
                "spam": {"duplicate_count": 3, "time_window": 10},
                "rate_limit": {"messages_count": 5, "time_window": 5},
                "links": {"block_all_links": False, "allow_whitelist": []},
                "invites": {},
                "mentions": {"max_mentions": 5, "include_roles": True},
                "caps": {"percentage": 70, "min_length": 10},
                "emojis": {"max_emojis": 10},
                "blacklist": {"words": [], "case_sensitive": False}
            }
            
            rule_data = {
                "name": name,
                "rule_type": rule_type,
                "action": action,
                "enabled": True,
                "settings": rule_settings.get(rule_type, {}),
                "whitelist_roles": [],
                "custom_message": None
            }
            
            if duration and action == "mute":
                rule_data["duration"] = duration
            
            # Create rule
            schema = AutoModSchema(self.bot.db)
            rule = await schema.create_rule(guild_id, rule_data)
            
            if rule:
                # Refresh cache
                await self.automod.refresh_rules_cache(guild_id)
                
                embed = discord.Embed(
                    title="✅ تم إضافة القاعدة",
                    description=f"**الاسم:** {name}\n**النوع:** {rule_type}\n**الإجراء:** {action}",
                    color=discord.Color.green(),
                    timestamp=datetime.utcnow()
                )
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send("❌ فشل إضافة القاعدة", ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in automod_rule_add: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="automod-rule-list", description="📋 عرض قواعد AutoMod")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_rule_list(self, interaction: discord.Interaction):
        """List all AutoMod rules"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            schema = AutoModSchema(self.bot.db)
            rules = await schema.get_guild_rules(guild_id, enabled_only=False)
            
            if not rules:
                await interaction.followup.send("❌ لا توجد قواعد محددة", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="📋 قواعد AutoMod",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            for rule in rules[:25]:  # Discord embed limit
                status = "✅" if rule.get("enabled") else "❌"
                value = (
                    f"**النوع:** {rule['rule_type']}\n"
                    f"**الإجراء:** {rule['action']}\n"
                    f"**الحالة:** {status}"
                )
                embed.add_field(
                    name=rule['name'],
                    value=value,
                    inline=True
                )
            
            if len(rules) > 25:
                embed.set_footer(text=f"عرض 25 من {len(rules)} قاعدة")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in automod_rule_list: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="automod-rule-remove", description="🗑️ حذف قاعدة AutoMod")
    @app_commands.describe(rule_name="اسم القاعدة")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_rule_remove(self, interaction: discord.Interaction, rule_name: str):
        """Remove an AutoMod rule"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            schema = AutoModSchema(self.bot.db)
            
            # Find rule by name
            rules = await schema.get_guild_rules(guild_id, enabled_only=False)
            rule = next((r for r in rules if r['name'] == rule_name), None)
            
            if not rule:
                await interaction.followup.send(f"❌ لم يتم العثور على قاعدة باسم: {rule_name}", ephemeral=True)
                return
            
            # Delete rule
            success = await schema.delete_rule(str(rule['_id']))
            
            if success:
                # Refresh cache
                await self.automod.refresh_rules_cache(guild_id)
                await interaction.followup.send(f"✅ تم حذف القاعدة: {rule_name}", ephemeral=True)
            else:
                await interaction.followup.send("❌ فشل حذف القاعدة", ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in automod_rule_remove: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {str(e)}", ephemeral=True)
    
    # ==================== Whitelist/Blacklist Commands ====================
    
    @app_commands.command(name="automod-whitelist", description="⚪ إدارة القائمة البيضاء")
    @app_commands.describe(
        action="الإجراء",
        rule_name="اسم القاعدة",
        role="الدور"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_whitelist(
        self,
        interaction: discord.Interaction,
        action: Literal["add", "remove", "list"],
        rule_name: str,
        role: Optional[discord.Role] = None
    ):
        """Manage rule whitelists"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            schema = AutoModSchema(self.bot.db)
            
            # Find rule
            rules = await schema.get_guild_rules(guild_id, enabled_only=False)
            rule = next((r for r in rules if r['name'] == rule_name), None)
            
            if not rule:
                await interaction.followup.send(f"❌ لم يتم العثور على قاعدة: {rule_name}", ephemeral=True)
                return
            
            if action == "add":
                if not role:
                    await interaction.followup.send("❌ يجب تحديد دور", ephemeral=True)
                    return
                
                whitelist = rule.get('whitelist_roles', [])
                if role.id not in whitelist:
                    whitelist.append(role.id)
                    success = await schema.update_rule(str(rule['_id']), {"whitelist_roles": whitelist})
                    
                    if success:
                        await self.automod.refresh_rules_cache(guild_id)
                        await interaction.followup.send(f"✅ تمت إضافة {role.mention} للقائمة البيضاء", ephemeral=True)
                    else:
                        await interaction.followup.send("❌ فشل التحديث", ephemeral=True)
                else:
                    await interaction.followup.send(f"⚠️ {role.mention} موجود بالفعل", ephemeral=True)
            
            elif action == "remove":
                if not role:
                    await interaction.followup.send("❌ يجب تحديد دور", ephemeral=True)
                    return
                
                whitelist = rule.get('whitelist_roles', [])
                if role.id in whitelist:
                    whitelist.remove(role.id)
                    success = await schema.update_rule(str(rule['_id']), {"whitelist_roles": whitelist})
                    
                    if success:
                        await self.automod.refresh_rules_cache(guild_id)
                        await interaction.followup.send(f"✅ تمت إزالة {role.mention} من القائمة البيضاء", ephemeral=True)
                    else:
                        await interaction.followup.send("❌ فشل التحديث", ephemeral=True)
                else:
                    await interaction.followup.send(f"⚠️ {role.mention} غير موجود", ephemeral=True)
            
            elif action == "list":
                whitelist = rule.get('whitelist_roles', [])
                if whitelist:
                    roles_text = "\n".join([f"<@&{role_id}>" for role_id in whitelist])
                    embed = discord.Embed(
                        title=f"⚪ القائمة البيضاء - {rule_name}",
                        description=roles_text,
                        color=discord.Color.blue()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send("❌ القائمة البيضاء فارغة", ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in automod_whitelist: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {str(e)}", ephemeral=True)
    
    # ==================== Logs & Statistics Commands ====================
    
    @app_commands.command(name="automod-logs", description="📝 عرض سجلات AutoMod")
    @app_commands.describe(
        user="المستخدم (اختياري)",
        limit="عدد السجلات"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_logs(
        self,
        interaction: discord.Interaction,
        user: Optional[discord.Member] = None,
        limit: int = 10
    ):
        """View AutoMod logs"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            schema = AutoModSchema(self.bot.db)
            
            if user:
                logs = await schema.get_user_logs(guild_id, user.id, limit=limit)
            else:
                logs = await schema.get_guild_logs(guild_id, limit=limit)
            
            if not logs:
                await interaction.followup.send("❌ لا توجد سجلات", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="📝 سجلات AutoMod",
                color=discord.Color.orange(),
                timestamp=datetime.utcnow()
            )
            
            for log in logs[:25]:
                timestamp = log.get('timestamp', datetime.utcnow())
                value = (
                    f"**المستخدم:** <@{log['user_id']}>\n"
                    f"**الإجراء:** {log['action']}\n"
                    f"**القاعدة:** {log['rule_type']}\n"
                    f"**السبب:** {log['reason']}\n"
                    f"**الوقت:** <t:{int(timestamp.timestamp())}:R>"
                )
                embed.add_field(
                    name=f"#{logs.index(log) + 1}",
                    value=value,
                    inline=False
                )
            
            if len(logs) > 25:
                embed.set_footer(text=f"عرض 25 من {len(logs)} سجل")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in automod_logs: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="automod-stats", description="📊 إحصائيات AutoMod")
    @app_commands.describe(days="عدد الأيام")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def automod_stats(self, interaction: discord.Interaction, days: int = 7):
        """View AutoMod statistics"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild_id = interaction.guild.id
            stats = await self.automod.get_statistics(guild_id, days=days)
            
            embed = discord.Embed(
                title=f"📊 إحصائيات AutoMod - آخر {days} يوم",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            # Total actions
            total = stats.get('total_actions', 0)
            embed.add_field(name="📌 إجمالي الإجراءات", value=str(total), inline=True)
            
            # By action type
            by_action = stats.get('by_action', {})
            if by_action:
                actions_text = "\n".join([f"{action}: {count}" for action, count in by_action.items()])
                embed.add_field(name="🎯 حسب الإجراء", value=actions_text, inline=True)
            
            # By rule type
            by_rule = stats.get('by_rule_type', {})
            if by_rule:
                rules_text = "\n".join([f"{rule}: {count}" for rule, count in by_rule.items()])
                embed.add_field(name="📋 حسب نوع القاعدة", value=rules_text, inline=True)
            
            # Top violators
            top_users = stats.get('top_users', [])
            if top_users:
                users_text = "\n".join([f"<@{user_id}>: {count}" for user_id, count in top_users[:5]])
                embed.add_field(name="👥 أكثر المخالفين", value=users_text, inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in automod_stats: {e}")
            await interaction.followup.send(f"❌ حدث خطأ: {str(e)}", ephemeral=True)


async def setup(bot: commands.Bot):
    """Load the AutoMod cog"""
    await bot.add_cog(AutoModCog(bot))

"""
Kingdom-77 Bot - Logging Commands Cog
Slash commands for managing the Advanced Logging System
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
from datetime import datetime, timedelta
import json
from io import BytesIO

from database.logging_schema import LoggingSchema
# Import from logging module (custom module, not built-in)
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from logging.logging_system import LoggingSystem
except ImportError:
    # Fallback if import fails
    LoggingSystem = None


class LoggingCog(commands.Cog):
    """Advanced Logging System Commands"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db: LoggingSchema = bot.db.logging
        self.logging_system: LoggingSystem = bot.logging_system
    
    logs_group = app_commands.Group(
        name="logs",
        description="Advanced Logging System commands"
    )
    
    # ==================== Setup Command ====================
    
    @logs_group.command(name="setup", description="Setup the logging system for your server")
    @app_commands.checks.has_permissions(administrator=True)
    async def logs_setup(self, interaction: discord.Interaction):
        """Setup logging system with default settings"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        
        # Check if already exists
        existing = await self.db.get_server_settings(guild_id)
        if existing:
            embed = discord.Embed(
                title="⚠️ Already Setup",
                description="Logging system is already configured for this server.\nUse `/logs channel` to set logging channels.",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Create default settings
        await self.db.create_default_settings(guild_id)
        
        embed = discord.Embed(
            title="✅ Logging System Setup Complete",
            description="The logging system has been initialized with default settings.",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📌 Next Steps",
            value=(
                "1. Use `/logs channel` to set logging channels\n"
                "2. Use `/logs toggle` to enable/disable specific log types\n"
                "3. Logs will start recording immediately!"
            ),
            inline=False
        )
        embed.add_field(
            name="📊 Available Log Types",
            value=(
                "• Message Logs (edit/delete)\n"
                "• Member Logs (join/leave/update)\n"
                "• Channel Logs (create/delete/update)\n"
                "• Role Logs (create/delete/update)\n"
                "• Voice Logs (join/leave/move)\n"
                "• Server Logs (settings changes)"
            ),
            inline=False
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ==================== Channel Command ====================
    
    @logs_group.command(name="channel", description="Set logging channel for a specific type")
    @app_commands.describe(
        log_type="Type of logs to send to this channel",
        channel="The channel to send logs to (leave empty to disable)"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logs_channel(
        self,
        interaction: discord.Interaction,
        log_type: Literal[
            "message_logs", "member_logs", "channel_logs",
            "role_logs", "voice_logs", "server_logs",
            "moderation_logs", "automod_logs"
        ],
        channel: Optional[discord.TextChannel] = None
    ):
        """Set or remove logging channel for a specific type"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        
        # Check if setup
        settings = await self.db.get_server_settings(guild_id)
        if not settings:
            embed = discord.Embed(
                title="❌ Not Setup",
                description="Please run `/logs setup` first to initialize the logging system.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Update channel
        channel_id = channel.id if channel else None
        await self.db.set_log_channel(guild_id, log_type, channel_id)
        
        if channel:
            embed = discord.Embed(
                title="✅ Logging Channel Set",
                description=f"**{log_type.replace('_', ' ').title()}** will now be sent to {channel.mention}",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="✅ Logging Channel Disabled",
                description=f"**{log_type.replace('_', ' ').title()}** logging has been disabled.",
                color=discord.Color.orange()
            )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ==================== Toggle Command ====================
    
    @logs_group.command(name="toggle", description="Enable or disable a specific log type")
    @app_commands.describe(
        log_type="Type of log to toggle",
        enabled="Enable or disable this log type"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logs_toggle(
        self,
        interaction: discord.Interaction,
        log_type: Literal[
            "message_edit", "message_delete", "member_join", "member_leave",
            "member_update", "member_ban", "member_unban", "channel_create",
            "channel_delete", "channel_update", "role_create", "role_delete",
            "role_update", "voice_join", "voice_leave", "voice_move",
            "server_update"
        ],
        enabled: bool
    ):
        """Enable or disable a specific log type"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        
        # Check if setup
        settings = await self.db.get_server_settings(guild_id)
        if not settings:
            embed = discord.Embed(
                title="❌ Not Setup",
                description="Please run `/logs setup` first to initialize the logging system.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Toggle log type
        await self.db.toggle_log_type(guild_id, log_type, enabled)
        
        status = "enabled" if enabled else "disabled"
        color = discord.Color.green() if enabled else discord.Color.red()
        
        embed = discord.Embed(
            title=f"✅ Log Type {status.title()}",
            description=f"**{log_type.replace('_', ' ').title()}** logging has been **{status}**.",
            color=color
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ==================== Config Command ====================
    
    @logs_group.command(name="config", description="View current logging configuration")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logs_config(self, interaction: discord.Interaction):
        """View current logging configuration"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        
        # Get settings
        settings = await self.db.get_server_settings(guild_id)
        if not settings:
            embed = discord.Embed(
                title="❌ Not Setup",
                description="Please run `/logs setup` first to initialize the logging system.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Build config embed
        embed = discord.Embed(
            title="⚙️ Logging Configuration",
            description=f"Configuration for {interaction.guild.name}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Show channels
        channels = settings.get("channels", {})
        channel_text = ""
        for log_type, channel_id in channels.items():
            if channel_id:
                channel = interaction.guild.get_channel(channel_id)
                channel_text += f"• **{log_type.replace('_', ' ').title()}**: {channel.mention if channel else 'Unknown'}\n"
            else:
                channel_text += f"• **{log_type.replace('_', ' ').title()}**: Not set\n"
        
        if channel_text:
            embed.add_field(name="📢 Log Channels", value=channel_text, inline=False)
        
        # Show enabled log types
        log_types = settings.get("log_types", {})
        enabled_types = [k.replace('_', ' ').title() for k, v in log_types.items() if v]
        disabled_types = [k.replace('_', ' ').title() for k, v in log_types.items() if not v]
        
        if enabled_types:
            embed.add_field(
                name="✅ Enabled Types",
                value=", ".join(enabled_types[:10]),
                inline=False
            )
        
        if disabled_types:
            embed.add_field(
                name="❌ Disabled Types",
                value=", ".join(disabled_types[:10]),
                inline=False
            )
        
        # Show stats
        stats = settings.get("stats", {})
        stats_text = (
            f"• Total Logs: {stats.get('total_logs', 0):,}\n"
            f"• Logs Today: {stats.get('logs_today', 0):,}\n"
        )
        embed.add_field(name="📊 Statistics", value=stats_text, inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ==================== Search Command ====================
    
    @logs_group.command(name="search", description="Search logs by content or user")
    @app_commands.describe(
        query="Search term to look for",
        log_category="Category of logs to search",
        limit="Number of results (max 50)"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logs_search(
        self,
        interaction: discord.Interaction,
        query: str,
        log_category: Literal["message", "member", "channel", "role", "voice", "server"] = "message",
        limit: int = 10
    ):
        """Search through logs"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        
        # Validate limit
        if limit > 50:
            limit = 50
        if limit < 1:
            limit = 1
        
        # Search logs
        results = await self.db.search_logs(guild_id, query, log_category)
        
        if not results:
            embed = discord.Embed(
                title="🔍 No Results",
                description=f"No logs found matching `{query}` in {log_category} logs.",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Build results embed
        embed = discord.Embed(
            title=f"🔍 Search Results: {query}",
            description=f"Found {len(results)} result(s) in {log_category} logs",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Show results
        for i, log in enumerate(results[:limit], 1):
            log_type = log.get("log_type", "unknown")
            timestamp = log.get("timestamp", datetime.utcnow())
            
            if log_category == "message":
                user_id = log.get("user_id")
                channel_id = log.get("channel_id")
                content = log.get("content", log.get("after", {}).get("content", ""))[:100]
                
                value = f"<@{user_id}> in <#{channel_id}>\n`{content}`\n<t:{int(timestamp.timestamp())}:R>"
            elif log_category == "member":
                user_id = log.get("user_id")
                username = log.get("username", "Unknown")
                value = f"<@{user_id}> ({username})\n<t:{int(timestamp.timestamp())}:R>"
            else:
                value = f"Type: {log_type}\n<t:{int(timestamp.timestamp())}:R>"
            
            embed.add_field(
                name=f"{i}. {log_type.replace('_', ' ').title()}",
                value=value,
                inline=False
            )
        
        embed.set_footer(text=f"Showing {min(len(results), limit)} of {len(results)} results")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ==================== User Command ====================
    
    @logs_group.command(name="user", description="View all logs for a specific user")
    @app_commands.describe(
        user="The user to view logs for",
        limit="Number of logs to show (max 100)"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logs_user(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        limit: int = 25
    ):
        """View all logs for a specific user"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        
        # Validate limit
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1
        
        # Get user history
        history = await self.db.get_user_history(guild_id, user.id, limit)
        
        # Count total logs
        total_logs = (
            len(history["messages"]) +
            len(history["member_events"]) +
            len(history["roles"]) +
            len(history["voice"])
        )
        
        if total_logs == 0:
            embed = discord.Embed(
                title="📋 No Logs Found",
                description=f"No logs found for {user.mention}",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Build history embed
        embed = discord.Embed(
            title=f"📋 User Log History: {user.name}",
            description=f"Showing recent activity for {user.mention}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Message logs
        if history["messages"]:
            message_text = ""
            for log in history["messages"][:5]:
                log_type = log.get("log_type", "unknown")
                timestamp = log.get("timestamp")
                message_text += f"• {log_type.replace('_', ' ').title()} - <t:{int(timestamp.timestamp())}:R>\n"
            embed.add_field(name=f"💬 Message Logs ({len(history['messages'])})", value=message_text, inline=False)
        
        # Member events
        if history["member_events"]:
            member_text = ""
            for log in history["member_events"][:5]:
                log_type = log.get("log_type", "unknown")
                timestamp = log.get("timestamp")
                member_text += f"• {log_type.replace('_', ' ').title()} - <t:{int(timestamp.timestamp())}:R>\n"
            embed.add_field(name=f"👤 Member Events ({len(history['member_events'])})", value=member_text, inline=False)
        
        # Role changes
        if history["roles"]:
            role_text = ""
            for log in history["roles"][:5]:
                log_type = log.get("log_type", "unknown")
                role_name = log.get("role_name", "Unknown")
                timestamp = log.get("timestamp")
                role_text += f"• {log_type.replace('_', ' ').title()}: {role_name} - <t:{int(timestamp.timestamp())}:R>\n"
            embed.add_field(name=f"🎭 Role Changes ({len(history['roles'])})", value=role_text, inline=False)
        
        # Voice activity
        if history["voice"]:
            voice_text = ""
            for log in history["voice"][:5]:
                log_type = log.get("log_type", "unknown")
                timestamp = log.get("timestamp")
                voice_text += f"• {log_type.replace('_', ' ').title()} - <t:{int(timestamp.timestamp())}:R>\n"
            embed.add_field(name=f"🔊 Voice Activity ({len(history['voice'])})", value=voice_text, inline=False)
        
        embed.set_footer(text=f"Total Logs: {total_logs} | User ID: {user.id}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ==================== Export Command ====================
    
    @logs_group.command(name="export", description="Export logs to JSON file")
    @app_commands.describe(
        log_category="Category of logs to export",
        days="Number of days to export (max 30)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def logs_export(
        self,
        interaction: discord.Interaction,
        log_category: Literal["message", "member", "channel", "role", "voice", "server", "all"],
        days: int = 7
    ):
        """Export logs to a JSON file"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        
        # Validate days
        if days > 30:
            days = 30
        if days < 1:
            days = 1
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get logs
        logs = {}
        
        if log_category == "all":
            # Export all categories
            for category in ["message", "member", "channel", "role", "voice", "server"]:
                category_logs = await self.db.get_logs(
                    guild_id=guild_id,
                    log_category=category,
                    limit=1000,
                    start_date=start_date,
                    end_date=end_date
                )
                logs[category] = category_logs
        else:
            # Export single category
            logs[log_category] = await self.db.get_logs(
                guild_id=guild_id,
                log_category=log_category,
                limit=1000,
                start_date=start_date,
                end_date=end_date
            )
        
        # Convert to JSON (handle datetime objects)
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")
        
        json_data = json.dumps(logs, indent=2, default=json_serializer)
        
        # Create file
        file_buffer = BytesIO(json_data.encode('utf-8'))
        file_buffer.seek(0)
        
        filename = f"logs_{interaction.guild.id}_{log_category}_{days}days.json"
        file = discord.File(file_buffer, filename=filename)
        
        # Count total logs
        total_logs = sum(len(v) for v in logs.values())
        
        embed = discord.Embed(
            title="📦 Logs Exported",
            description=f"Exported {total_logs} log entries from the last {days} day(s)",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Category", value=log_category, inline=True)
        embed.add_field(name="Date Range", value=f"{days} days", inline=True)
        embed.add_field(name="Total Logs", value=str(total_logs), inline=True)
        
        await interaction.followup.send(embed=embed, file=file, ephemeral=True)
    
    # ==================== Stats Command ====================
    
    @logs_group.command(name="stats", description="View logging statistics for your server")
    @app_commands.describe(
        days="Number of days to show stats for (max 30)"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def logs_stats(self, interaction: discord.Interaction, days: int = 7):
        """View logging statistics"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        
        # Validate days
        if days > 30:
            days = 30
        if days < 1:
            days = 1
        
        # Get stats
        stats = await self.db.get_stats(guild_id, days)
        
        # Build stats embed
        embed = discord.Embed(
            title="📊 Logging Statistics",
            description=f"Statistics for the last {days} day(s)",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        # Total logs
        embed.add_field(
            name="📈 Total Logs",
            value=f"{stats['total_logs']:,}",
            inline=True
        )
        
        # Logs by type
        by_type_text = ""
        for log_type, count in stats.get("by_type", {}).items():
            if count > 0:
                by_type_text += f"• {log_type.title()}: {count:,}\n"
        
        if by_type_text:
            embed.add_field(name="📋 By Type", value=by_type_text, inline=False)
        
        # Most active users
        most_active = stats.get("most_active_users", [])
        if most_active:
            active_text = ""
            for i, user_data in enumerate(most_active[:5], 1):
                user_id = user_data.get("_id")
                count = user_data.get("count", 0)
                active_text += f"{i}. <@{user_id}>: {count:,} logs\n"
            embed.add_field(name="👥 Most Active Users", value=active_text, inline=False)
        
        embed.set_footer(text=f"Server ID: {guild_id}")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    # ==================== Clear Command ====================
    
    @logs_group.command(name="clear", description="Clear old logs from the database")
    @app_commands.describe(
        days="Delete logs older than this many days (min 7, max 90)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def logs_clear(self, interaction: discord.Interaction, days: int = 30):
        """Clear old logs from the database"""
        await interaction.response.defer(ephemeral=True)
        
        guild_id = interaction.guild.id
        
        # Validate days
        if days < 7:
            days = 7
        if days > 90:
            days = 90
        
        # Confirm action
        embed = discord.Embed(
            title="⚠️ Confirm Log Deletion",
            description=f"This will **permanently delete** all logs older than {days} days.\n\nAre you sure?",
            color=discord.Color.red()
        )
        
        view = ConfirmView(interaction.user)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        await view.wait()
        
        if not view.value:
            embed = discord.Embed(
                title="❌ Cancelled",
                description="Log deletion cancelled.",
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed, view=None)
            return
        
        # Delete logs
        deleted_count = await self.db.cleanup_old_logs(guild_id, days)
        
        embed = discord.Embed(
            title="✅ Logs Cleared",
            description=f"Successfully deleted {deleted_count:,} log entries older than {days} days.",
            color=discord.Color.green()
        )
        
        await interaction.edit_original_response(embed=embed, view=None)


# ==================== Confirm View ====================

class ConfirmView(discord.ui.View):
    """Confirmation view for destructive actions"""
    
    def __init__(self, user: discord.User):
        super().__init__(timeout=60)
        self.user = user
        self.value = None
    
    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Only the command user can confirm this action.", ephemeral=True)
            return
        
        self.value = True
        self.stop()
        await interaction.response.defer()
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Only the command user can cancel this action.", ephemeral=True)
            return
        
        self.value = False
        self.stop()
        await interaction.response.defer()


async def setup(bot: commands.Bot):
    """Setup function for the cog"""
    await bot.add_cog(LoggingCog(bot))

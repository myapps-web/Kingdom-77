"""
Moderation Cog for Kingdom-77 Bot v3.0
=======================================
Slash commands for moderation: warnings, mutes, kicks, bans
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional
from datetime import datetime, timedelta

from moderation.mod_system import get_mod_system
from database import db

logger = logging.getLogger(__name__)


class ModerationCog(commands.Cog):
    """Moderation commands for server management."""
    
    def __init__(self, bot):
        self.bot = bot
        self.mod_system = None
        
    async def cog_load(self):
        """Initialize mod system when cog loads."""
        if db and db.client:
            self.mod_system = get_mod_system(db.db)
            logger.info("✅ Moderation system initialized")
        else:
            logger.warning("⚠️ MongoDB not available, moderation disabled")
    
    def make_embed(self, title: str, description: str, color: discord.Color) -> discord.Embed:
        """Create a standard embed."""
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=f"Kingdom-77 Bot v3.0 • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        return embed
    
    async def check_permissions(self, interaction: discord.Interaction) -> bool:
        """Check if user has moderation permissions."""
        if not interaction.guild:
            return False
        
        member = interaction.guild.get_member(interaction.user.id)
        if not member:
            return False
        
        # Check if user has moderate members permission
        return member.guild_permissions.moderate_members or member.guild_permissions.administrator
    
    async def send_mod_log(
        self,
        guild: discord.Guild,
        action_type: str,
        user: discord.User,
        moderator: discord.User,
        reason: str,
        duration: Optional[str] = None
    ):
        """Send moderation action to log channel."""
        try:
            if not self.mod_system:
                return
            
            config = await self.mod_system.get_guild_config(str(guild.id))
            channel_id = config.get("mod_log_channel")
            
            if not channel_id:
                return
            
            channel = guild.get_channel(int(channel_id))
            if not channel:
                return
            
            # Create log embed
            color_map = {
                "warn": discord.Color.yellow(),
                "mute": discord.Color.orange(),
                "unmute": discord.Color.green(),
                "kick": discord.Color.red(),
                "ban": discord.Color.dark_red(),
                "unban": discord.Color.blue()
            }
            
            embed = discord.Embed(
                title=f"🛡️ {action_type.upper()} Action",
                color=color_map.get(action_type, discord.Color.gray()),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="👤 User", value=f"{user.mention} ({user.id})", inline=True)
            embed.add_field(name="👮 Moderator", value=f"{moderator.mention}", inline=True)
            
            if duration:
                embed.add_field(name="⏱️ Duration", value=duration, inline=True)
            
            embed.add_field(name="📝 Reason", value=reason or "No reason provided", inline=False)
            embed.set_footer(text=f"Action ID: {action_type}_{guild.id}_{user.id}")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending mod log: {e}")
    
    # ========================================================================
    # WARNING COMMANDS
    # ========================================================================
    
    @app_commands.command(name="warn", description="⚠️ Issue a warning to a user")
    @app_commands.describe(
        user="The user to warn",
        reason="Reason for the warning"
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: str
    ):
        """Warn a user."""
        # Check permissions
        if not await self.check_permissions(interaction):
            embed = self.make_embed(
                title='❌ Permission Denied',
                description='You need **Moderate Members** permission to use this command.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not self.mod_system:
            embed = self.make_embed(
                title='❌ Error',
                description='Moderation system is not available.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Can't warn bots or yourself
        if user.bot:
            embed = self.make_embed(
                title='❌ Error',
                description='You cannot warn bots.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user.id == interaction.user.id:
            embed = self.make_embed(
                title='❌ Error',
                description='You cannot warn yourself.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Add warning
            warning = await self.mod_system.add_warning(
                guild_id=str(interaction.guild.id),
                user_id=str(user.id),
                moderator_id=str(interaction.user.id),
                reason=reason
            )
            
            # Log action
            await self.mod_system.log_action(
                guild_id=str(interaction.guild.id),
                action_type="warn",
                user_id=str(user.id),
                user_tag=str(user),
                moderator_id=str(interaction.user.id),
                moderator_tag=str(interaction.user),
                reason=reason
            )
            
            # Get total warnings
            warnings = await self.mod_system.get_user_warnings(
                str(interaction.guild.id),
                str(user.id)
            )
            
            # Send response
            embed = self.make_embed(
                title='⚠️ Warning Issued',
                description=f'{user.mention} has been warned.',
                color=discord.Color.yellow()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Total Warnings", value=f"{len(warnings)}/3", inline=True)
            embed.add_field(name="Warning ID", value=warning['warning_id'], inline=True)
            
            await interaction.response.send_message(embed=embed)
            
            # Send mod log
            await self.send_mod_log(
                interaction.guild,
                "warn",
                user,
                interaction.user,
                reason
            )
            
            # DM user
            try:
                dm_embed = self.make_embed(
                    title=f'⚠️ Warning in {interaction.guild.name}',
                    description=f'You have been warned by {interaction.user.mention}',
                    color=discord.Color.yellow()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Total Warnings", value=f"{len(warnings)}/3", inline=False)
                
                await user.send(embed=dm_embed)
            except:
                pass  # User has DMs disabled
            
            # Check threshold
            threshold = await self.mod_system.check_warn_threshold(
                str(interaction.guild.id),
                str(user.id)
            )
            
            if threshold:
                warning_embed = self.make_embed(
                    title='⚠️ Warning Threshold Reached',
                    description=f'{user.mention} has reached {len(warnings)} warnings!',
                    color=discord.Color.orange()
                )
                warning_embed.add_field(
                    name="Auto-Action",
                    value=f"Consider taking action: {threshold['action']}",
                    inline=False
                )
                await interaction.followup.send(embed=warning_embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in warn command: {e}")
            embed = self.make_embed(
                title='❌ Error',
                description=f'An error occurred: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="warnings", description="📋 View warnings for a user")
    @app_commands.describe(user="The user to check warnings for")
    async def warnings(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """View user warnings."""
        if not self.mod_system:
            embed = self.make_embed(
                title='❌ Error',
                description='Moderation system is not available.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            warnings = await self.mod_system.get_user_warnings(
                str(interaction.guild.id),
                str(user.id),
                active_only=False
            )
            
            if not warnings:
                embed = self.make_embed(
                    title='📋 Warnings',
                    description=f'{user.mention} has no warnings.',
                    color=discord.Color.green()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Count active warnings
            active = [w for w in warnings if w.get('active')]
            
            embed = self.make_embed(
                title=f'📋 Warnings for {user.name}',
                description=f'**Active:** {len(active)} | **Total:** {len(warnings)}',
                color=discord.Color.yellow()
            )
            
            # Show last 5 warnings
            for i, warning in enumerate(warnings[:5], 1):
                status = "🟢 Active" if warning.get('active') else "⚪ Cleared"
                timestamp = warning.get('timestamp', 'Unknown')[:10]  # Date only
                
                embed.add_field(
                    name=f"{i}. {status} - {timestamp}",
                    value=f"**Reason:** {warning.get('reason')}\n**ID:** `{warning.get('warning_id')}`",
                    inline=False
                )
            
            if len(warnings) > 5:
                embed.set_footer(text=f"Showing 5 of {len(warnings)} warnings")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error in warnings command: {e}")
            embed = self.make_embed(
                title='❌ Error',
                description=f'An error occurred: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="clearwarnings", description="🗑️ Clear all warnings for a user")
    @app_commands.describe(user="The user to clear warnings for")
    async def clearwarnings(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """Clear all warnings for a user."""
        # Check permissions
        if not await self.check_permissions(interaction):
            embed = self.make_embed(
                title='❌ Permission Denied',
                description='You need **Moderate Members** permission to use this command.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not self.mod_system:
            embed = self.make_embed(
                title='❌ Error',
                description='Moderation system is not available.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            count = await self.mod_system.clear_all_warnings(
                str(interaction.guild.id),
                str(user.id),
                str(interaction.user.id)
            )
            
            if count == 0:
                embed = self.make_embed(
                    title='ℹ️ No Warnings',
                    description=f'{user.mention} has no active warnings to clear.',
                    color=discord.Color.blue()
                )
            else:
                embed = self.make_embed(
                    title='✅ Warnings Cleared',
                    description=f'Cleared {count} warning(s) for {user.mention}',
                    color=discord.Color.green()
                )
            
            await interaction.response.send_message(embed=embed)
            
            # Send mod log
            if count > 0:
                await self.send_mod_log(
                    interaction.guild,
                    "warn",
                    user,
                    interaction.user,
                    f"Cleared {count} warnings"
                )
            
        except Exception as e:
            logger.error(f"Error in clearwarnings command: {e}")
            embed = self.make_embed(
                title='❌ Error',
                description=f'An error occurred: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)


    # ========================================================================
    # MODERATION ACTIONS
    # ========================================================================
    
    @app_commands.command(name="mute", description="🔇 Temporarily mute a user")
    @app_commands.describe(
        user="The user to mute",
        duration="Duration (e.g., 10m, 1h, 1d)",
        reason="Reason for the mute"
    )
    async def mute(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        duration: str,
        reason: Optional[str] = "No reason provided"
    ):
        """Mute a user temporarily."""
        # Check permissions
        if not await self.check_permissions(interaction):
            embed = self.make_embed(
                title='❌ Permission Denied',
                description='You need **Moderate Members** permission to use this command.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user.bot or user.id == interaction.user.id:
            embed = self.make_embed(
                title='❌ Error',
                description='Invalid target user.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Parse duration
            duration_seconds = self.parse_duration(duration)
            if not duration_seconds:
                embed = self.make_embed(
                    title='❌ Invalid Duration',
                    description='Use format: 10m, 1h, 2d (minutes/hours/days)',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Apply timeout (Discord native timeout)
            timeout_until = datetime.utcnow() + timedelta(seconds=duration_seconds)
            await user.timeout(timeout_until, reason=reason)
            
            # Log action
            if self.mod_system:
                await self.mod_system.log_action(
                    guild_id=str(interaction.guild.id),
                    action_type="mute",
                    user_id=str(user.id),
                    user_tag=str(user),
                    moderator_id=str(interaction.user.id),
                    moderator_tag=str(interaction.user),
                    reason=reason,
                    duration=duration_seconds
                )
            
            embed = self.make_embed(
                title='🔇 User Muted',
                description=f'{user.mention} has been muted for {duration}.',
                color=discord.Color.orange()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            embed.add_field(name="Duration", value=duration, inline=True)
            embed.add_field(name="Expires", value=f"<t:{int(timeout_until.timestamp())}:R>", inline=True)
            
            await interaction.response.send_message(embed=embed)
            
            # Send mod log
            await self.send_mod_log(
                interaction.guild,
                "mute",
                user,
                interaction.user,
                reason,
                duration
            )
            
            # DM user
            try:
                dm_embed = self.make_embed(
                    title=f'🔇 Muted in {interaction.guild.name}',
                    description=f'You have been muted by {interaction.user.mention}',
                    color=discord.Color.orange()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                dm_embed.add_field(name="Duration", value=duration, inline=False)
                await user.send(embed=dm_embed)
            except:
                pass
            
        except discord.Forbidden:
            embed = self.make_embed(
                title='❌ Permission Error',
                description='I don\'t have permission to timeout this user.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in mute command: {e}")
            embed = self.make_embed(
                title='❌ Error',
                description=f'An error occurred: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unmute", description="🔊 Unmute a user")
    @app_commands.describe(user="The user to unmute")
    async def unmute(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):
        """Unmute a user."""
        if not await self.check_permissions(interaction):
            embed = self.make_embed(
                title='❌ Permission Denied',
                description='You need **Moderate Members** permission to use this command.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            await user.timeout(None, reason=f"Unmuted by {interaction.user}")
            
            if self.mod_system:
                await self.mod_system.log_action(
                    guild_id=str(interaction.guild.id),
                    action_type="unmute",
                    user_id=str(user.id),
                    user_tag=str(user),
                    moderator_id=str(interaction.user.id),
                    moderator_tag=str(interaction.user),
                    reason="Unmuted"
                )
            
            embed = self.make_embed(
                title='🔊 User Unmuted',
                description=f'{user.mention} has been unmuted.',
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
            
            await self.send_mod_log(
                interaction.guild,
                "unmute",
                user,
                interaction.user,
                "Unmuted"
            )
            
        except Exception as e:
            logger.error(f"Error in unmute command: {e}")
            embed = self.make_embed(
                title='❌ Error',
                description=f'An error occurred: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="kick", description="👢 Kick a user from the server")
    @app_commands.describe(
        user="The user to kick",
        reason="Reason for the kick"
    )
    async def kick(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: Optional[str] = "No reason provided"
    ):
        """Kick a user."""
        if not await self.check_permissions(interaction):
            embed = self.make_embed(
                title='❌ Permission Denied',
                description='You need **Kick Members** permission to use this command.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user.bot or user.id == interaction.user.id:
            embed = self.make_embed(
                title='❌ Error',
                description='Invalid target user.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # DM before kick
            try:
                dm_embed = self.make_embed(
                    title=f'👢 Kicked from {interaction.guild.name}',
                    description=f'You have been kicked by {interaction.user.mention}',
                    color=discord.Color.red()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                await user.send(embed=dm_embed)
            except:
                pass
            
            # Kick user
            await user.kick(reason=f"{reason} | By: {interaction.user}")
            
            if self.mod_system:
                await self.mod_system.log_action(
                    guild_id=str(interaction.guild.id),
                    action_type="kick",
                    user_id=str(user.id),
                    user_tag=str(user),
                    moderator_id=str(interaction.user.id),
                    moderator_tag=str(interaction.user),
                    reason=reason
                )
            
            embed = self.make_embed(
                title='👢 User Kicked',
                description=f'{user.mention} has been kicked.',
                color=discord.Color.red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            await self.send_mod_log(
                interaction.guild,
                "kick",
                user,
                interaction.user,
                reason
            )
            
        except discord.Forbidden:
            embed = self.make_embed(
                title='❌ Permission Error',
                description='I don\'t have permission to kick this user.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in kick command: {e}")
            embed = self.make_embed(
                title='❌ Error',
                description=f'An error occurred: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="ban", description="🔨 Ban a user from the server")
    @app_commands.describe(
        user="The user to ban",
        reason="Reason for the ban",
        delete_messages="Delete user's messages (days, 0-7)"
    )
    async def ban(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: Optional[str] = "No reason provided",
        delete_messages: Optional[int] = 0
    ):
        """Ban a user."""
        if not await self.check_permissions(interaction):
            embed = self.make_embed(
                title='❌ Permission Denied',
                description='You need **Ban Members** permission to use this command.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if user.bot or user.id == interaction.user.id:
            embed = self.make_embed(
                title='❌ Error',
                description='Invalid target user.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # DM before ban
            try:
                dm_embed = self.make_embed(
                    title=f'🔨 Banned from {interaction.guild.name}',
                    description=f'You have been banned by {interaction.user.mention}',
                    color=discord.Color.dark_red()
                )
                dm_embed.add_field(name="Reason", value=reason, inline=False)
                await user.send(embed=dm_embed)
            except:
                pass
            
            # Ban user
            await user.ban(
                reason=f"{reason} | By: {interaction.user}",
                delete_message_days=max(0, min(7, delete_messages))
            )
            
            if self.mod_system:
                await self.mod_system.log_action(
                    guild_id=str(interaction.guild.id),
                    action_type="ban",
                    user_id=str(user.id),
                    user_tag=str(user),
                    moderator_id=str(interaction.user.id),
                    moderator_tag=str(interaction.user),
                    reason=reason
                )
            
            embed = self.make_embed(
                title='🔨 User Banned',
                description=f'{user.mention} has been banned.',
                color=discord.Color.dark_red()
            )
            embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            await self.send_mod_log(
                interaction.guild,
                "ban",
                user,
                interaction.user,
                reason
            )
            
        except discord.Forbidden:
            embed = self.make_embed(
                title='❌ Permission Error',
                description='I don\'t have permission to ban this user.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in ban command: {e}")
            embed = self.make_embed(
                title='❌ Error',
                description=f'An error occurred: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="unban", description="✅ Unban a user")
    @app_commands.describe(user_id="The user ID to unban")
    async def unban(
        self,
        interaction: discord.Interaction,
        user_id: str
    ):
        """Unban a user by ID."""
        if not await self.check_permissions(interaction):
            embed = self.make_embed(
                title='❌ Permission Denied',
                description='You need **Ban Members** permission to use this command.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            user_id_int = int(user_id)
            user = await self.bot.fetch_user(user_id_int)
            
            await interaction.guild.unban(user, reason=f"Unbanned by {interaction.user}")
            
            if self.mod_system:
                await self.mod_system.log_action(
                    guild_id=str(interaction.guild.id),
                    action_type="unban",
                    user_id=str(user.id),
                    user_tag=str(user),
                    moderator_id=str(interaction.user.id),
                    moderator_tag=str(interaction.user),
                    reason="Unbanned"
                )
            
            embed = self.make_embed(
                title='✅ User Unbanned',
                description=f'{user.mention} (`{user.id}`) has been unbanned.',
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
            
            await self.send_mod_log(
                interaction.guild,
                "unban",
                user,
                interaction.user,
                "Unbanned"
            )
            
        except ValueError:
            embed = self.make_embed(
                title='❌ Invalid User ID',
                description='Please provide a valid user ID (numbers only).',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except discord.NotFound:
            embed = self.make_embed(
                title='❌ User Not Found',
                description='This user is not banned.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in unban command: {e}")
            embed = self.make_embed(
                title='❌ Error',
                description=f'An error occurred: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ========================================================================
    # MOD LOG CONFIG
    # ========================================================================
    
    @app_commands.command(name="setmodlog", description="📋 Set moderation log channel")
    @app_commands.describe(channel="The channel for moderation logs")
    async def setmodlog(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        """Set mod log channel."""
        if not await self.check_permissions(interaction):
            embed = self.make_embed(
                title='❌ Permission Denied',
                description='You need **Administrator** permission to use this command.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not self.mod_system:
            embed = self.make_embed(
                title='❌ Error',
                description='Moderation system is not available.',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            success = await self.mod_system.set_mod_log_channel(
                str(interaction.guild.id),
                str(channel.id)
            )
            
            if success:
                embed = self.make_embed(
                    title='✅ Mod Log Channel Set',
                    description=f'Moderation logs will be sent to {channel.mention}',
                    color=discord.Color.green()
                )
            else:
                embed = self.make_embed(
                    title='❌ Error',
                    description='Failed to set mod log channel.',
                    color=discord.Color.red()
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in setmodlog command: {e}")
            embed = self.make_embed(
                title='❌ Error',
                description=f'An error occurred: {str(e)}',
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse duration string to seconds.
        
        Args:
            duration_str: Duration string (e.g., "10m", "1h", "2d")
            
        Returns:
            Duration in seconds or None if invalid
        """
        try:
            if duration_str.endswith('m'):
                return int(duration_str[:-1]) * 60
            elif duration_str.endswith('h'):
                return int(duration_str[:-1]) * 3600
            elif duration_str.endswith('d'):
                return int(duration_str[:-1]) * 86400
            else:
                return int(duration_str) * 60  # Default to minutes
        except:
            return None


async def setup(bot):
    """Setup function to add cog to bot."""
    await bot.add_cog(ModerationCog(bot))
    logger.info("✅ Moderation cog loaded")

"""
Welcome System Commands - Kingdom-77 Bot
Slash commands for welcome system configuration.
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
from datetime import datetime

from welcome.welcome_system import WelcomeSystem


class WelcomeCommands(commands.Cog):
    """Welcome System Slash Commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.welcome_system = WelcomeSystem(bot.db)
    
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle member join"""
        await self.welcome_system.on_member_join(member)
    
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Handle member leave"""
        await self.welcome_system.on_member_remove(member)
    
    # Welcome Setup Command Group
    welcome_group = app_commands.Group(name="welcome", description="Welcome system commands")
    
    @welcome_group.command(name="setup", description="Setup welcome system")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_setup(self, interaction: discord.Interaction):
        """Initial setup for welcome system"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Check if already configured
            settings = await self.welcome_system.schema.get_settings(interaction.guild.id)
            
            if settings:
                embed = discord.Embed(
                    title="⚙️ Welcome System",
                    description="Welcome system is already configured.\nUse other commands to modify settings.",
                    color=discord.Color.blue()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Create default settings
            await self.welcome_system.schema.create_or_update_settings(
                interaction.guild.id,
                {
                    "enabled": True,
                    "welcome_type": "embed",
                    "welcome_message": "Welcome {user} to {server}! 🎉",
                    "welcome_channels": [],
                    "embed_title": "Welcome!",
                    "embed_description": "Welcome {user} to {server}!\n\nYou are member #{count}",
                    "embed_fields": [],
                    "goodbye_enabled": False,
                    "dm_enabled": False,
                    "captcha_enabled": False,
                    "auto_role_enabled": False,
                    "anti_raid_enabled": False
                }
            )
            
            embed = discord.Embed(
                title="✅ Welcome System Setup Complete",
                description="Welcome system has been initialized with default settings.\n\n"
                           "**Next Steps:**\n"
                           "1. `/welcome channel` - Set welcome channel\n"
                           "2. `/welcome message` - Customize message\n"
                           "3. `/welcome card` - Design welcome card\n"
                           "4. `/welcome test` - Test the system",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @welcome_group.command(name="channel", description="Set welcome/goodbye channels")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        welcome_channel="Channel for welcome messages",
        goodbye_channel="Channel for goodbye messages (optional)"
    )
    async def welcome_channel(
        self, 
        interaction: discord.Interaction,
        welcome_channel: discord.TextChannel,
        goodbye_channel: Optional[discord.TextChannel] = None
    ):
        """Set welcome and goodbye channels"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            updates = {
                "welcome_channels": [welcome_channel.id]
            }
            
            if goodbye_channel:
                updates["goodbye_channel"] = goodbye_channel.id
                updates["goodbye_enabled"] = True
            
            await self.welcome_system.schema.create_or_update_settings(
                interaction.guild.id,
                updates
            )
            
            embed = discord.Embed(
                title="✅ Channels Updated",
                description=f"**Welcome Channel:** {welcome_channel.mention}\n" +
                           (f"**Goodbye Channel:** {goodbye_channel.mention}" if goodbye_channel else ""),
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @welcome_group.command(name="message", description="Customize welcome message")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_message(self, interaction: discord.Interaction):
        """Open modal to customize welcome message"""
        modal = WelcomeMessageModal(self.welcome_system)
        await interaction.response.send_modal(modal)
    
    @welcome_group.command(name="card", description="Design welcome card")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        template="Card template style",
        background_color="Background color (hex code)",
        text_color="Text color (hex code)",
        accent_color="Accent color (hex code)"
    )
    async def welcome_card(
        self,
        interaction: discord.Interaction,
        template: Literal["classic", "modern", "minimal", "fancy"] = "classic",
        background_color: Optional[str] = None,
        text_color: Optional[str] = None,
        accent_color: Optional[str] = None
    ):
        """Design welcome card"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Create card design
            design = {
                "template": template,
                "background_color": background_color or "#2C2F33",
                "text_color": text_color or "#FFFFFF",
                "accent_color": accent_color or "#7289DA"
            }
            
            card = await self.welcome_system.schema.create_card_design(
                interaction.guild.id,
                f"{template}_card",
                design
            )
            
            # Update settings to use this card
            await self.welcome_system.schema.create_or_update_settings(
                interaction.guild.id,
                {
                    "welcome_type": "card",
                    "card_id": card.inserted_id
                }
            )
            
            embed = discord.Embed(
                title="✅ Welcome Card Designed",
                description=f"**Template:** {template.title()}\n"
                           f"**Background:** {design['background_color']}\n"
                           f"**Text:** {design['text_color']}\n"
                           f"**Accent:** {design['accent_color']}\n\n"
                           f"Use `/welcome test` to preview the card!",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @welcome_group.command(name="test", description="Test welcome message")
    @app_commands.checks.has_permissions(administrator=True)
    async def welcome_test(self, interaction: discord.Interaction):
        """Test welcome message with current settings"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            await self.welcome_system.test_welcome(interaction.user)
            
            embed = discord.Embed(
                title="✅ Test Sent",
                description="Check the welcome channel for the test message!",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @welcome_group.command(name="autorole", description="Configure auto-role")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        role="Role to assign automatically",
        enabled="Enable or disable auto-role",
        delay="Delay in seconds before assigning (0 for instant)"
    )
    async def welcome_autorole(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        enabled: bool = True,
        delay: int = 0
    ):
        """Configure auto-role assignment"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Check if bot can assign this role
            if role >= interaction.guild.me.top_role:
                await interaction.followup.send(
                    "❌ I cannot assign this role. It's higher than my highest role!",
                    ephemeral=True
                )
                return
            
            await self.welcome_system.schema.create_or_update_settings(
                interaction.guild.id,
                {
                    "auto_role_enabled": enabled,
                    "auto_roles": [role.id],
                    "auto_role_delay": delay
                }
            )
            
            embed = discord.Embed(
                title="✅ Auto-Role Configured",
                description=f"**Role:** {role.mention}\n"
                           f"**Enabled:** {'Yes' if enabled else 'No'}\n"
                           f"**Delay:** {delay} seconds",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @welcome_group.command(name="captcha", description="Configure captcha verification")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        enabled="Enable or disable captcha",
        difficulty="Captcha difficulty level",
        timeout="Time limit in seconds (default: 300)",
        unverified_role="Role for unverified members (optional)"
    )
    async def welcome_captcha(
        self,
        interaction: discord.Interaction,
        enabled: bool,
        difficulty: Literal["easy", "medium", "hard"] = "medium",
        timeout: int = 300,
        unverified_role: Optional[discord.Role] = None
    ):
        """Configure captcha verification"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            updates = {
                "captcha_enabled": enabled,
                "captcha_difficulty": difficulty,
                "captcha_timeout": timeout,
                "captcha_max_attempts": 3
            }
            
            if unverified_role:
                updates["unverified_role"] = unverified_role.id
            
            await self.welcome_system.schema.create_or_update_settings(
                interaction.guild.id,
                updates
            )
            
            embed = discord.Embed(
                title="✅ Captcha Configured",
                description=f"**Enabled:** {'Yes' if enabled else 'No'}\n"
                           f"**Difficulty:** {difficulty.title()}\n"
                           f"**Timeout:** {timeout} seconds\n" +
                           (f"**Unverified Role:** {unverified_role.mention}" if unverified_role else ""),
                color=discord.Color.green()
            )
            
            if enabled:
                embed.add_field(
                    name="ℹ️ How it works",
                    value="New members will receive a captcha in DM that they must solve to get access to the server.",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @welcome_group.command(name="stats", description="View welcome statistics")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        days="Number of days to show stats for (default: 7)"
    )
    async def welcome_stats(
        self,
        interaction: discord.Interaction,
        days: int = 7
    ):
        """View welcome statistics"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            stats = await self.welcome_system.schema.get_join_statistics(
                interaction.guild.id,
                days
            )
            
            embed = discord.Embed(
                title=f"📊 Welcome Statistics (Last {days} days)",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👥 New Members",
                value=f"{stats.get('joins', 0)} joined\n{stats.get('leaves', 0)} left",
                inline=True
            )
            
            embed.add_field(
                name="📈 Net Change",
                value=f"+{stats.get('joins', 0) - stats.get('leaves', 0)}",
                inline=True
            )
            
            embed.add_field(
                name="📅 Daily Average",
                value=f"{stats.get('joins', 0) / days:.1f} joins/day",
                inline=True
            )
            
            if stats.get('captcha_enabled'):
                embed.add_field(
                    name="🛡️ Captcha",
                    value=f"{stats.get('captcha_passed', 0)} passed\n"
                          f"{stats.get('captcha_failed', 0)} failed",
                    inline=True
                )
            
            embed.set_footer(text=f"Requested by {interaction.user.name}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @welcome_group.command(name="toggle", description="Enable/disable welcome system")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(enabled="Enable or disable the system")
    async def welcome_toggle(self, interaction: discord.Interaction, enabled: bool):
        """Toggle welcome system on/off"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            await self.welcome_system.schema.create_or_update_settings(
                interaction.guild.id,
                {"enabled": enabled}
            )
            
            embed = discord.Embed(
                title=f"✅ Welcome System {'Enabled' if enabled else 'Disabled'}",
                description=f"The welcome system is now **{'active' if enabled else 'inactive'}**.",
                color=discord.Color.green() if enabled else discord.Color.red()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)
    
    @welcome_group.command(name="antiraid", description="Configure anti-raid protection")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        enabled="Enable or disable anti-raid",
        threshold="Max joins per minute before raid is detected"
    )
    async def welcome_antiraid(
        self,
        interaction: discord.Interaction,
        enabled: bool,
        threshold: int = 10
    ):
        """Configure anti-raid protection"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            await self.welcome_system.schema.create_or_update_settings(
                interaction.guild.id,
                {
                    "anti_raid_enabled": enabled,
                    "anti_raid_threshold": threshold
                }
            )
            
            embed = discord.Embed(
                title="✅ Anti-Raid Configured",
                description=f"**Enabled:** {'Yes' if enabled else 'No'}\n"
                           f"**Threshold:** {threshold} joins/minute\n\n"
                           f"When a raid is detected, welcome messages will be temporarily disabled.",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


class WelcomeMessageModal(discord.ui.Modal, title="Welcome Message Configuration"):
    """Modal for configuring welcome message"""
    
    def __init__(self, welcome_system: WelcomeSystem):
        super().__init__()
        self.welcome_system = welcome_system
    
    message_type = discord.ui.TextInput(
        label="Message Type (text/embed/card)",
        placeholder="embed",
        default="embed",
        max_length=10,
        required=True
    )
    
    title = discord.ui.TextInput(
        label="Title (for embed)",
        placeholder="Welcome!",
        max_length=256,
        required=False
    )
    
    message = discord.ui.TextInput(
        label="Message",
        style=discord.TextStyle.paragraph,
        placeholder="Welcome {user} to {server}! You are member #{count}",
        max_length=2000,
        required=True
    )
    
    dm_message = discord.ui.TextInput(
        label="DM Message (optional)",
        style=discord.TextStyle.paragraph,
        placeholder="Welcome to {server}! Please read the rules.",
        max_length=1000,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg_type = self.message_type.value.lower()
            
            updates = {
                "welcome_type": msg_type
            }
            
            if msg_type == "text":
                updates["welcome_message"] = self.message.value
            elif msg_type == "embed":
                updates["embed_title"] = self.title.value or "Welcome!"
                updates["embed_description"] = self.message.value
            
            if self.dm_message.value:
                updates["dm_enabled"] = True
                updates["dm_message"] = self.dm_message.value
            
            await self.welcome_system.schema.create_or_update_settings(
                interaction.guild.id,
                updates
            )
            
            embed = discord.Embed(
                title="✅ Welcome Message Updated",
                description=f"**Type:** {msg_type.title()}\n\n"
                           f"Use `/welcome test` to preview!",
                color=discord.Color.green()
            )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(WelcomeCommands(bot))

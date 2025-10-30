"""
Kingdom-77 Bot v3.8 - Branding Commands

Discord commands for Custom Bot Branding (Premium Feature).

Commands:
- /branding setup - Set up custom branding (Premium)
- /branding preview - Preview current branding
- /branding reset - Reset to default branding
- /branding status - View branding status and settings

Author: Kingdom-77 Team
Date: 2024
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from datetime import datetime

# Import systems
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from branding.branding_system import BrandingSystem


class BrandingModal(discord.ui.Modal, title="🎨 Custom Bot Branding"):
    """Modal for setting up custom branding."""
    
    bot_nickname = discord.ui.TextInput(
        label="Bot Nickname (Server-specific)",
        placeholder="e.g., Kingdom Helper",
        required=False,
        max_length=32
    )
    
    embed_color = discord.ui.TextInput(
        label="Embed Color (Hex Code)",
        placeholder="e.g., #5865F2 or 5865F2",
        required=False,
        max_length=7
    )
    
    footer_text = discord.ui.TextInput(
        label="Custom Footer Text",
        placeholder="e.g., Powered by Kingdom-77",
        required=False,
        max_length=100
    )
    
    welcome_message = discord.ui.TextInput(
        label="Custom Welcome Message Template",
        placeholder="Use {user} for username, {server} for server name",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=500
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Handle modal submission."""
        # Data will be processed by the command
        await interaction.response.defer()


class BrandingCog(commands.Cog, name="Branding"):
    """Commands for Custom Bot Branding (Premium Feature)."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.branding_system = BrandingSystem(bot)
    
    async def cog_load(self):
        """Initialize branding system when cog loads."""
        await self.branding_system.initialize()
    
    # ============================================================
    # BRANDING GROUP
    # ============================================================
    
    branding_group = app_commands.Group(
        name="branding",
        description="🎨 Customize bot appearance (Premium)"
    )
    
    # ============================================================
    # SETUP COMMAND
    # ============================================================
    
    @branding_group.command(
        name="setup",
        description="Set up custom bot branding for your server (Premium)"
    )
    @app_commands.default_permissions(administrator=True)
    async def branding_setup(self, interaction: discord.Interaction):
        """Set up custom branding (Premium)."""
        
        # Check if user has permission
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need Administrator permission to use this command.",
                ephemeral=True
            )
            return
        
        # Check if guild has premium
        if hasattr(self.bot, 'premium_system'):
            has_premium = await self.bot.premium_system.has_feature(
                str(interaction.guild.id),
                "custom_branding"
            )
            
            if not has_premium:
                embed = discord.Embed(
                    title="💎 Premium Feature",
                    description=(
                        "**Custom Bot Branding** is a Premium feature!\n\n"
                        "With Premium, you can:\n"
                        "• Custom bot nickname in your server\n"
                        "• Custom embed colors\n"
                        "• Custom footer text\n"
                        "• Custom welcome messages\n"
                        "• Custom logo and banner\n\n"
                        "Use `/premium info` to learn more!"
                    ),
                    color=discord.Color.gold()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Show setup modal
        modal = BrandingModal()
        await interaction.response.send_modal(modal)
        
        # Wait for modal submission
        await modal.wait()
        
        # Get values
        branding_data = {
            "guild_id": str(interaction.guild.id),
            "bot_nickname": modal.bot_nickname.value or None,
            "embed_color": modal.embed_color.value or None,
            "footer_text": modal.footer_text.value or None,
            "welcome_message": modal.welcome_message.value or None
        }
        
        # Validate and save
        try:
            success = await self.branding_system.set_branding(
                guild_id=str(interaction.guild.id),
                **branding_data
            )
            
            if success:
                # Apply bot nickname if provided
                if branding_data["bot_nickname"]:
                    try:
                        await interaction.guild.me.edit(nick=branding_data["bot_nickname"])
                    except:
                        pass
                
                embed = discord.Embed(
                    title="✅ Branding Updated!",
                    description="Your custom branding has been saved successfully.",
                    color=discord.Color.green()
                )
                
                if branding_data["bot_nickname"]:
                    embed.add_field(
                        name="Bot Nickname",
                        value=branding_data["bot_nickname"],
                        inline=True
                    )
                
                if branding_data["embed_color"]:
                    embed.add_field(
                        name="Embed Color",
                        value=branding_data["embed_color"],
                        inline=True
                    )
                
                if branding_data["footer_text"]:
                    embed.add_field(
                        name="Footer Text",
                        value=branding_data["footer_text"],
                        inline=False
                    )
                
                embed.set_footer(text="Use /branding preview to see your changes")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Failed to save branding settings. Please try again.",
                    ephemeral=True
                )
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # PREVIEW COMMAND
    # ============================================================
    
    @branding_group.command(
        name="preview",
        description="Preview your current custom branding"
    )
    async def branding_preview(self, interaction: discord.Interaction):
        """Preview current branding."""
        await interaction.response.defer()
        
        try:
            # Get branding
            branding = await self.branding_system.get_branding(str(interaction.guild.id))
            
            if not branding or not branding.get('enabled', True):
                embed = discord.Embed(
                    title="ℹ️ No Custom Branding",
                    description="This server is using default bot branding.",
                    color=discord.Color.blue()
                )
                embed.set_footer(text="Use /branding setup to customize (Premium)")
                await interaction.followup.send(embed=embed)
                return
            
            # Create preview embed with custom branding
            embed = discord.Embed(
                title="🎨 Custom Branding Preview",
                description="This is how embeds will look with your custom branding.",
                timestamp=datetime.utcnow()
            )
            
            # Apply custom color
            if branding.get('embed_color'):
                try:
                    color_hex = branding['embed_color'].replace('#', '')
                    embed.color = discord.Color(int(color_hex, 16))
                except:
                    embed.color = discord.Color.blue()
            else:
                embed.color = discord.Color.blue()
            
            # Show settings
            if branding.get('bot_nickname'):
                embed.add_field(
                    name="Bot Nickname",
                    value=branding['bot_nickname'],
                    inline=True
                )
            
            if branding.get('embed_color'):
                embed.add_field(
                    name="Embed Color",
                    value=branding['embed_color'],
                    inline=True
                )
            
            if branding.get('logo_url'):
                embed.set_thumbnail(url=branding['logo_url'])
                embed.add_field(
                    name="Custom Logo",
                    value="✅ Set",
                    inline=True
                )
            
            if branding.get('banner_url'):
                embed.set_image(url=branding['banner_url'])
            
            # Apply custom footer
            footer_text = branding.get('footer_text', f"Kingdom-77 Bot • {interaction.guild.name}")
            embed.set_footer(
                text=footer_text,
                icon_url=interaction.guild.icon.url if interaction.guild.icon else None
            )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # STATUS COMMAND
    # ============================================================
    
    @branding_group.command(
        name="status",
        description="View current branding settings and status"
    )
    @app_commands.default_permissions(administrator=True)
    async def branding_status(self, interaction: discord.Interaction):
        """View branding status."""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Get branding
            branding = await self.branding_system.get_branding(str(interaction.guild.id))
            
            embed = discord.Embed(
                title="🎨 Branding Status",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            if not branding:
                embed.description = "❌ No custom branding configured.\n\nUse `/branding setup` to get started (Premium)."
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
            
            # Status
            status = "✅ Active" if branding.get('enabled', True) else "❌ Disabled"
            embed.add_field(
                name="Status",
                value=status,
                inline=True
            )
            
            # Settings
            settings = []
            
            if branding.get('bot_nickname'):
                settings.append(f"✅ Bot Nickname: `{branding['bot_nickname']}`")
            else:
                settings.append("❌ Bot Nickname: Not set")
            
            if branding.get('embed_color'):
                settings.append(f"✅ Embed Color: `{branding['embed_color']}`")
            else:
                settings.append("❌ Embed Color: Not set")
            
            if branding.get('footer_text'):
                settings.append(f"✅ Footer Text: `{branding['footer_text'][:50]}...`" if len(branding['footer_text']) > 50 else f"✅ Footer Text: `{branding['footer_text']}`")
            else:
                settings.append("❌ Footer Text: Not set")
            
            if branding.get('logo_url'):
                settings.append("✅ Custom Logo: Set")
            else:
                settings.append("❌ Custom Logo: Not set")
            
            if branding.get('banner_url'):
                settings.append("✅ Custom Banner: Set")
            else:
                settings.append("❌ Custom Banner: Not set")
            
            embed.add_field(
                name="Current Settings",
                value="\n".join(settings),
                inline=False
            )
            
            # Created date
            if branding.get('created_at'):
                created_timestamp = int(branding['created_at'].timestamp())
                embed.add_field(
                    name="Created",
                    value=f"<t:{created_timestamp}:R>",
                    inline=True
                )
            
            # Updated date
            if branding.get('updated_at'):
                updated_timestamp = int(branding['updated_at'].timestamp())
                embed.add_field(
                    name="Last Updated",
                    value=f"<t:{updated_timestamp}:R>",
                    inline=True
                )
            
            embed.set_footer(text="Use /branding preview to see how it looks")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # ============================================================
    # RESET COMMAND
    # ============================================================
    
    @branding_group.command(
        name="reset",
        description="Reset branding to default settings"
    )
    @app_commands.default_permissions(administrator=True)
    async def branding_reset(self, interaction: discord.Interaction):
        """Reset branding to default."""
        
        # Check permission
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You need Administrator permission to use this command.",
                ephemeral=True
            )
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Reset branding
            success = await self.branding_system.reset_branding(str(interaction.guild.id))
            
            if success:
                # Reset bot nickname
                try:
                    await interaction.guild.me.edit(nick=None)
                except:
                    pass
                
                embed = discord.Embed(
                    title="✅ Branding Reset",
                    description="Bot branding has been reset to default settings.",
                    color=discord.Color.green()
                )
                embed.set_footer(text="Use /branding setup to customize again")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Failed to reset branding. Please try again.",
                    ephemeral=True
                )
        
        except Exception as e:
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    """Load the Branding cog."""
    await bot.add_cog(BrandingCog(bot))

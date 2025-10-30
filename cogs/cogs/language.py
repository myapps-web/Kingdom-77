"""
Language Cog for Kingdom-77 Bot

Provides language selection and management commands.
"""

import discord
from discord import app_commands
from discord.ext import commands
import logging
from typing import Optional

from localization import i18n_manager, t
from database.language_schema import LanguageSchema

logger = logging.getLogger(__name__)


class Language(commands.Cog):
    """Language management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.language_schema = LanguageSchema(bot.mongodb_client.db)
        
        # Load preferences from database on startup
        bot.loop.create_task(self._load_preferences())
    
    async def _load_preferences(self):
        """Load language preferences from database"""
        try:
            await self.language_schema.load_preferences_to_i18n(i18n_manager)
            logger.info("Language preferences loaded from database")
        except Exception as e:
            logger.error(f"Error loading language preferences: {e}")
    
    language_group = app_commands.Group(
        name="language",
        description="Language management commands"
    )
    
    @language_group.command(
        name="set",
        description="Set your preferred language"
    )
    @app_commands.describe(
        language="The language you want to use"
    )
    @app_commands.choices(language=[
        app_commands.Choice(name="🇬🇧 English", value="en"),
        app_commands.Choice(name="🇸🇦 العربية (Arabic)", value="ar"),
        app_commands.Choice(name="🇪🇸 Español (Spanish)", value="es"),
        app_commands.Choice(name="🇫🇷 Français (French)", value="fr"),
        app_commands.Choice(name="🇩🇪 Deutsch (German)", value="de")
    ])
    async def language_set(
        self,
        interaction: discord.Interaction,
        language: str
    ):
        """Set user's preferred language"""
        try:
            user_id = str(interaction.user.id)
            
            # Set in i18n manager
            i18n_manager.set_user_language(user_id, language)
            
            # Save to database
            success = await self.language_schema.set_user_language(user_id, language)
            
            if success:
                # Get language info
                lang_info = i18n_manager.SUPPORTED_LANGUAGES[language]
                lang_display = f"{lang_info['flag']} {lang_info['native']}"
                
                # Send confirmation in new language
                message = t(
                    "commands.language.set.success",
                    lang_code=language,
                    language=lang_display
                )
                
                embed = discord.Embed(
                    title=t("general.success", lang_code=language),
                    description=message,
                    color=discord.Color.green()
                )
                embed.set_footer(text=t("embeds.footer", lang_code=language))
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                # Error message in current language
                current_lang = i18n_manager.get_user_language(user_id)
                error_msg = t(
                    "commands.language.set.error",
                    lang_code=current_lang
                )
                
                embed = discord.Embed(
                    title=t("general.error", lang_code=current_lang),
                    description=error_msg,
                    color=discord.Color.red()
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in language set command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred. Please try again.",
                ephemeral=True
            )
    
    @language_group.command(
        name="list",
        description="View all supported languages"
    )
    async def language_list(self, interaction: discord.Interaction):
        """List all supported languages"""
        try:
            user_id = str(interaction.user.id)
            guild_id = str(interaction.guild_id) if interaction.guild_id else None
            
            # Get user's current language
            current_lang = i18n_manager.get_user_language(user_id, guild_id)
            
            # Create embed
            embed = discord.Embed(
                title=t("commands.language.list.title", lang_code=current_lang),
                description=t(
                    "commands.language.list.current",
                    lang_code=current_lang,
                    language=i18n_manager.SUPPORTED_LANGUAGES[current_lang]['native']
                ),
                color=discord.Color.blue()
            )
            
            # Add languages
            lang_list = i18n_manager.format_language_list(current_lang)
            embed.add_field(
                name="Available Languages",
                value=lang_list,
                inline=False
            )
            
            # Add usage instructions
            embed.add_field(
                name="📝 How to change language",
                value=f"`/language set` - Choose your preferred language",
                inline=False
            )
            
            embed.set_footer(text=t("embeds.footer", lang_code=current_lang))
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in language list command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred. Please try again.",
                ephemeral=True
            )
    
    @language_group.command(
        name="server",
        description="Set server default language (Admin only)"
    )
    @app_commands.describe(
        language="The default language for this server"
    )
    @app_commands.choices(language=[
        app_commands.Choice(name="🇬🇧 English", value="en"),
        app_commands.Choice(name="🇸🇦 العربية (Arabic)", value="ar"),
        app_commands.Choice(name="🇪🇸 Español (Spanish)", value="es"),
        app_commands.Choice(name="🇫🇷 Français (French)", value="fr"),
        app_commands.Choice(name="🇩🇪 Deutsch (German)", value="de")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def language_server(
        self,
        interaction: discord.Interaction,
        language: str
    ):
        """Set server's default language (Admin only)"""
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "❌ This command can only be used in a server.",
                    ephemeral=True
                )
                return
            
            guild_id = str(interaction.guild_id)
            user_id = str(interaction.user.id)
            
            # Set in i18n manager
            i18n_manager.set_guild_language(guild_id, language)
            
            # Save to database
            success = await self.language_schema.set_guild_language(
                guild_id,
                language,
                user_id
            )
            
            if success:
                # Get language info
                lang_info = i18n_manager.SUPPORTED_LANGUAGES[language]
                lang_display = f"{lang_info['flag']} {lang_info['native']}"
                
                # Send confirmation in new language
                message = t(
                    "commands.language.server.success",
                    lang_code=language,
                    language=lang_display
                )
                
                embed = discord.Embed(
                    title=t("general.success", lang_code=language),
                    description=message,
                    color=discord.Color.green()
                )
                embed.add_field(
                    name="ℹ️ Note",
                    value="Users can still set their own language preference with `/language set`",
                    inline=False
                )
                embed.set_footer(text=t("embeds.footer", lang_code=language))
                
                await interaction.response.send_message(embed=embed)
            else:
                # Error message
                current_lang = i18n_manager.get_user_language(user_id, guild_id)
                error_msg = t(
                    "commands.language.server.error",
                    lang_code=current_lang
                )
                
                embed = discord.Embed(
                    title=t("general.error", lang_code=current_lang),
                    description=error_msg,
                    color=discord.Color.red()
                )
                
                await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in language server command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred. Please try again.",
                ephemeral=True
            )
    
    @language_server.error
    async def language_server_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        """Handle language server command errors"""
        if isinstance(error, app_commands.errors.MissingPermissions):
            user_id = str(interaction.user.id)
            guild_id = str(interaction.guild_id) if interaction.guild_id else None
            current_lang = i18n_manager.get_user_language(user_id, guild_id)
            
            message = t(
                "commands.language.server.no_permission",
                lang_code=current_lang
            )
            
            embed = discord.Embed(
                title=t("general.error", lang_code=current_lang),
                description=message,
                color=discord.Color.red()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(
                "❌ An error occurred. Please try again.",
                ephemeral=True
            )
    
    @language_group.command(
        name="stats",
        description="View language usage statistics (Admin only)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def language_stats(self, interaction: discord.Interaction):
        """View language usage statistics"""
        try:
            user_id = str(interaction.user.id)
            guild_id = str(interaction.guild_id) if interaction.guild_id else None
            current_lang = i18n_manager.get_user_language(user_id, guild_id)
            
            # Get statistics
            stats = await self.language_schema.get_language_statistics()
            
            # Create embed
            embed = discord.Embed(
                title="📊 Language Usage Statistics",
                color=discord.Color.blue()
            )
            
            # User statistics
            user_breakdown = stats.get("user_language_breakdown", {})
            if user_breakdown:
                user_stats_text = "\n".join([
                    f"{i18n_manager.SUPPORTED_LANGUAGES[lang]['flag']} **{lang.upper()}**: {count} users"
                    for lang, count in user_breakdown.items()
                ])
                embed.add_field(
                    name=f"👥 User Preferences ({stats.get('total_users_with_preference', 0)} total)",
                    value=user_stats_text or "No data",
                    inline=False
                )
            
            # Guild statistics
            guild_breakdown = stats.get("guild_language_breakdown", {})
            if guild_breakdown:
                guild_stats_text = "\n".join([
                    f"{i18n_manager.SUPPORTED_LANGUAGES[lang]['flag']} **{lang.upper()}**: {count} servers"
                    for lang, count in guild_breakdown.items()
                ])
                embed.add_field(
                    name=f"🏰 Server Preferences ({stats.get('total_guilds_with_preference', 0)} total)",
                    value=guild_stats_text or "No data",
                    inline=False
                )
            
            embed.set_footer(text=t("embeds.footer", lang_code=current_lang))
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        
        except Exception as e:
            logger.error(f"Error in language stats command: {e}")
            await interaction.response.send_message(
                "❌ An error occurred. Please try again.",
                ephemeral=True
            )


async def setup(bot):
    """Load the Language cog"""
    await bot.add_cog(Language(bot))
    logger.info("Language cog loaded")

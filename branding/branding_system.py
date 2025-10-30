"""
Custom Bot Branding System
===========================
Premium feature: Manage and apply custom branding to bot embeds and messages
"""

import discord
import logging
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class BrandingSystem:
    """System for managing custom bot branding (Premium feature)"""
    
    def __init__(self, mongodb_client: AsyncIOMotorClient):
        """Initialize branding system"""
        from database.branding_schema import BrandingSchema
        
        self.schema = BrandingSchema(mongodb_client)
        self._cache = {}  # Simple cache for branding settings
    
    async def initialize(self):
        """Initialize branding system"""
        await self.schema.initialize()
        logger.info("✅ Branding system initialized")
    
    # ==================== Branding Management ====================
    
    async def get_guild_branding(
        self,
        guild_id: str,
        use_cache: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Get custom branding for guild
        
        Args:
            guild_id: Discord guild ID
            use_cache: Whether to use cached branding
            
        Returns:
            Branding settings or None
        """
        # Check cache first
        if use_cache and guild_id in self._cache:
            return self._cache[guild_id]
        
        # Get from database
        branding = await self.schema.get_branding(guild_id)
        
        # Cache if found
        if branding:
            self._cache[guild_id] = branding
        
        return branding
    
    async def set_guild_branding(
        self,
        guild_id: str,
        guild_name: str,
        settings: Dict[str, Any],
        created_by: str
    ) -> Dict[str, Any]:
        """
        Set custom branding for guild
        
        Args:
            guild_id: Discord guild ID
            guild_name: Guild name
            settings: Branding settings
            created_by: User who created branding
            
        Returns:
            Created/updated branding
        """
        # Validate settings
        is_valid, error = self.schema.validate_branding_settings(settings)
        if not is_valid:
            raise ValueError(error)
        
        # Add creator
        settings["created_by"] = created_by
        
        # Check if exists
        existing = await self.schema.get_branding(guild_id)
        
        if existing:
            # Update
            await self.schema.update_branding(guild_id, settings)
            branding = await self.schema.get_branding(guild_id)
        else:
            # Create
            branding = await self.schema.create_branding(guild_id, guild_name, settings)
        
        # Update cache
        self._cache[guild_id] = branding
        
        return branding
    
    async def reset_guild_branding(self, guild_id: str) -> bool:
        """
        Reset guild branding to default
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            True if successful
        """
        success = await self.schema.delete_branding(guild_id)
        
        # Clear cache
        if guild_id in self._cache:
            del self._cache[guild_id]
        
        return success
    
    async def apply_preset(
        self,
        guild_id: str,
        guild_name: str,
        preset_name: str,
        created_by: str
    ) -> Dict[str, Any]:
        """
        Apply a branding preset
        
        Args:
            guild_id: Discord guild ID
            guild_name: Guild name
            preset_name: Preset name
            created_by: User who applied preset
            
        Returns:
            Applied branding
        """
        branding = await self.schema.apply_preset(guild_id, guild_name, preset_name, created_by)
        
        # Update cache
        self._cache[guild_id] = branding
        
        return branding
    
    def clear_cache(self, guild_id: Optional[str] = None):
        """Clear branding cache"""
        if guild_id:
            if guild_id in self._cache:
                del self._cache[guild_id]
        else:
            self._cache.clear()
    
    # ==================== Embed Branding ====================
    
    async def apply_branding_to_embed(
        self,
        embed: discord.Embed,
        guild_id: str,
        show_logo: bool = True,
        show_footer: bool = True
    ) -> discord.Embed:
        """
        Apply custom branding to embed
        
        Args:
            embed: Discord embed to brand
            guild_id: Discord guild ID
            show_logo: Whether to show guild logo
            show_footer: Whether to show custom footer
            
        Returns:
            Branded embed
        """
        branding = await self.get_guild_branding(guild_id)
        
        if not branding or not branding.get("enabled", True):
            # Use default branding
            embed.color = discord.Color.from_rgb(102, 126, 234)  # Kingdom-77 purple
            if show_footer:
                embed.set_footer(text="Kingdom-77 Bot")
            return embed
        
        # Apply custom color
        if "embed_color" in branding:
            color_hex = branding["embed_color"].replace("#", "")
            embed.color = discord.Color(int(color_hex, 16))
        
        # Apply logo/thumbnail
        if show_logo and branding.get("show_logo_in_embeds", True):
            if branding.get("logo_url"):
                position = branding.get("embed_thumbnail_position", "right")
                if position == "right":
                    embed.set_thumbnail(url=branding["logo_url"])
                elif position == "left":
                    embed.set_image(url=branding["logo_url"])
        
        # Apply banner
        if branding.get("show_banner_in_embeds", False) and branding.get("banner_url"):
            embed.set_image(url=branding["banner_url"])
        
        # Apply custom footer
        if show_footer:
            footer_text = branding.get("footer_text", "Kingdom-77 Bot")
            footer_icon = branding.get("footer_icon_url")
            
            if footer_icon:
                embed.set_footer(text=footer_text, icon_url=footer_icon)
            else:
                embed.set_footer(text=footer_text)
        
        return embed
    
    def create_branded_embed(
        self,
        guild_id: str,
        title: str = None,
        description: str = None,
        **kwargs
    ) -> discord.Embed:
        """
        Create a new branded embed (sync version - for use in commands)
        
        Args:
            guild_id: Discord guild ID
            title: Embed title
            description: Embed description
            **kwargs: Additional embed parameters
            
        Returns:
            New embed (will be branded when sent)
        """
        # Get cached branding if available
        branding = self._cache.get(guild_id)
        
        # Determine color
        if branding and branding.get("enabled", True):
            color_hex = branding.get("embed_color", "#667eea").replace("#", "")
            color = discord.Color(int(color_hex, 16))
        else:
            color = discord.Color.from_rgb(102, 126, 234)
        
        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            **kwargs
        )
        
        return embed
    
    # ==================== Message Formatting ====================
    
    async def format_welcome_message(
        self,
        guild_id: str,
        user: discord.Member,
        guild: discord.Guild
    ) -> str:
        """
        Format welcome message with custom branding
        
        Args:
            guild_id: Discord guild ID
            user: Member who joined
            guild: Discord guild
            
        Returns:
            Formatted welcome message
        """
        branding = await self.get_guild_branding(guild_id)
        
        if not branding or not branding.get("enabled", True):
            template = "Welcome to {guild_name}, {user}!"
        else:
            template = branding.get("welcome_message", "Welcome to {guild_name}, {user}!")
        
        return template.format(
            guild_name=guild.name,
            user=user.mention,
            username=user.name,
            member_count=guild.member_count
        )
    
    async def format_level_up_message(
        self,
        guild_id: str,
        user: discord.Member,
        level: int
    ) -> str:
        """
        Format level up message with custom branding
        
        Args:
            guild_id: Discord guild ID
            user: Member who leveled up
            level: New level
            
        Returns:
            Formatted level up message
        """
        branding = await self.get_guild_branding(guild_id)
        
        if not branding or not branding.get("enabled", True):
            template = "🎉 Congratulations {user}! You've reached level {level}!"
        else:
            template = branding.get("level_up_message", "🎉 Congratulations {user}! You've reached level {level}!")
        
        return template.format(
            user=user.mention,
            username=user.name,
            level=level
        )
    
    # ==================== Bot Nickname Management ====================
    
    async def apply_bot_nickname(
        self,
        guild: discord.Guild,
        bot_member: discord.Member
    ) -> bool:
        """
        Apply custom bot nickname in guild
        
        Args:
            guild: Discord guild
            bot_member: Bot member object
            
        Returns:
            True if successful
        """
        try:
            branding = await self.get_guild_branding(str(guild.id))
            
            if not branding or not branding.get("enabled", True):
                return False
            
            nickname = branding.get("bot_nickname")
            
            if nickname and nickname != bot_member.display_name:
                await bot_member.edit(nick=nickname)
                logger.info(f"Applied bot nickname '{nickname}' in guild {guild.id}")
                return True
            
            return False
            
        except discord.Forbidden:
            logger.warning(f"No permission to change nickname in guild {guild.id}")
            return False
        except Exception as e:
            logger.error(f"Failed to apply bot nickname in guild {guild.id}: {e}")
            return False
    
    # ==================== Validation & Preview ====================
    
    async def preview_branding(
        self,
        settings: Dict[str, Any]
    ) -> discord.Embed:
        """
        Create a preview embed with proposed branding settings
        
        Args:
            settings: Proposed branding settings
            
        Returns:
            Preview embed
        """
        # Validate first
        is_valid, error = self.schema.validate_branding_settings(settings)
        if not is_valid:
            raise ValueError(error)
        
        # Create preview embed
        color_hex = settings.get("embed_color", "#667eea").replace("#", "")
        color = discord.Color(int(color_hex, 16))
        
        embed = discord.Embed(
            title="🎨 Branding Preview",
            description="This is how your custom branding will look!",
            color=color
        )
        
        # Add fields showing settings
        if "bot_nickname" in settings:
            embed.add_field(name="Bot Nickname", value=settings["bot_nickname"], inline=True)
        
        embed.add_field(name="Embed Color", value=settings.get("embed_color", "#667eea"), inline=True)
        
        if "logo_url" in settings and settings["logo_url"]:
            embed.set_thumbnail(url=settings["logo_url"])
            embed.add_field(name="Logo", value="✅ Shown in thumbnail", inline=True)
        
        # Footer
        footer_text = settings.get("footer_text", "Kingdom-77 Bot")
        footer_icon = settings.get("footer_icon_url")
        
        if footer_icon:
            embed.set_footer(text=footer_text, icon_url=footer_icon)
        else:
            embed.set_footer(text=footer_text)
        
        # Example messages
        if "welcome_message" in settings:
            embed.add_field(
                name="Welcome Message Example",
                value=settings["welcome_message"].format(
                    guild_name="Your Server",
                    user="@User",
                    username="User",
                    member_count=100
                ),
                inline=False
            )
        
        if "level_up_message" in settings:
            embed.add_field(
                name="Level Up Message Example",
                value=settings["level_up_message"].format(
                    user="@User",
                    username="User",
                    level=10
                ),
                inline=False
            )
        
        return embed
    
    # ==================== Statistics ====================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get branding usage statistics"""
        return await self.schema.get_branding_stats()
    
    def get_available_presets(self) -> Dict[str, Dict[str, Any]]:
        """Get available branding presets"""
        return self.schema.get_branding_presets()

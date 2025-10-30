"""
Custom Bot Branding Database Schema
====================================
Premium feature: Allows guilds to customize bot appearance and identity

Collections:
- guild_branding: Custom branding settings per guild
"""

from typing import Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)


class BrandingSchema:
    """Database schema for custom bot branding (Premium feature)"""
    
    def __init__(self, mongodb_client: AsyncIOMotorClient):
        """Initialize branding schema"""
        self.db = mongodb_client.kingdom77_bot
        self.branding = self.db.guild_branding
    
    async def initialize(self):
        """Create indexes for branding collection"""
        try:
            # Create indexes
            await self.branding.create_index("guild_id", unique=True)
            await self.branding.create_index("created_at")
            
            logger.info("✅ Branding schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize branding schema: {e}")
    
    # ==================== CRUD Operations ====================
    
    async def get_branding(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """
        Get custom branding for guild
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            Branding settings or None
        """
        try:
            branding = await self.branding.find_one({"guild_id": guild_id})
            return branding
        except Exception as e:
            logger.error(f"Failed to get branding for guild {guild_id}: {e}")
            return None
    
    async def create_branding(
        self,
        guild_id: str,
        guild_name: str,
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create custom branding for guild
        
        Args:
            guild_id: Discord guild ID
            guild_name: Guild name
            settings: Branding settings
            
        Returns:
            Created branding document
        """
        try:
            branding_doc = {
                "guild_id": guild_id,
                "guild_name": guild_name,
                
                # Bot Identity
                "bot_nickname": settings.get("bot_nickname", "Kingdom-77"),
                "bot_avatar_url": settings.get("bot_avatar_url"),  # Custom avatar per guild (if Discord supports)
                
                # Visual Settings
                "embed_color": settings.get("embed_color", "#667eea"),  # Hex color
                "accent_color": settings.get("accent_color", "#764ba2"),  # Secondary color
                
                # Branding Assets
                "logo_url": settings.get("logo_url"),  # Guild logo
                "banner_url": settings.get("banner_url"),  # Guild banner
                "icon_url": settings.get("icon_url"),  # Small icon
                
                # Custom Messages
                "welcome_message": settings.get("welcome_message", "Welcome to {guild_name}!"),
                "level_up_message": settings.get("level_up_message", "🎉 Congratulations {user}! You've reached level {level}!"),
                "footer_text": settings.get("footer_text", "Kingdom-77 Bot"),
                "footer_icon_url": settings.get("footer_icon_url"),
                
                # Custom Prefix (for text commands if any)
                "custom_prefix": settings.get("custom_prefix", "!"),
                
                # Embed Templates
                "show_logo_in_embeds": settings.get("show_logo_in_embeds", True),
                "show_banner_in_embeds": settings.get("show_banner_in_embeds", False),
                "embed_thumbnail_position": settings.get("embed_thumbnail_position", "right"),  # left, right, none
                
                # Typography (future)
                "font_style": settings.get("font_style", "default"),  # default, bold, modern
                
                # Status
                "enabled": settings.get("enabled", True),
                
                # Metadata
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_by": settings.get("created_by")
            }
            
            await self.branding.insert_one(branding_doc)
            logger.info(f"Created branding for guild {guild_id}")
            
            return branding_doc
            
        except Exception as e:
            logger.error(f"Failed to create branding for guild {guild_id}: {e}")
            raise
    
    async def update_branding(
        self,
        guild_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update custom branding settings
        
        Args:
            guild_id: Discord guild ID
            updates: Fields to update
            
        Returns:
            True if successful
        """
        try:
            # Add updated_at timestamp
            updates["updated_at"] = datetime.utcnow()
            
            result = await self.branding.update_one(
                {"guild_id": guild_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated branding for guild {guild_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update branding for guild {guild_id}: {e}")
            return False
    
    async def delete_branding(self, guild_id: str) -> bool:
        """
        Delete custom branding (reset to default)
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            True if successful
        """
        try:
            result = await self.branding.delete_one({"guild_id": guild_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted branding for guild {guild_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete branding for guild {guild_id}: {e}")
            return False
    
    async def toggle_branding(self, guild_id: str, enabled: bool) -> bool:
        """
        Enable or disable custom branding
        
        Args:
            guild_id: Discord guild ID
            enabled: True to enable, False to disable
            
        Returns:
            True if successful
        """
        return await self.update_branding(guild_id, {"enabled": enabled})
    
    # ==================== Branding Presets ====================
    
    @staticmethod
    def get_default_branding() -> Dict[str, Any]:
        """Get default Kingdom-77 branding"""
        return {
            "bot_nickname": "Kingdom-77",
            "embed_color": "#667eea",
            "accent_color": "#764ba2",
            "footer_text": "Kingdom-77 Bot",
            "custom_prefix": "!",
            "show_logo_in_embeds": True,
            "enabled": True
        }
    
    @staticmethod
    def get_branding_presets() -> Dict[str, Dict[str, Any]]:
        """Get pre-made branding presets"""
        return {
            "gaming": {
                "name": "Gaming Theme",
                "description": "Perfect for gaming communities",
                "embed_color": "#FF0000",
                "accent_color": "#CC0000",
                "welcome_message": "🎮 Welcome to {guild_name}! Ready to game?",
                "level_up_message": "🎮 GG {user}! You leveled up to {level}!",
                "footer_text": "Gaming Paradise",
                "emoji": "🎮"
            },
            "educational": {
                "name": "Educational Theme",
                "description": "Perfect for study groups and schools",
                "embed_color": "#4CAF50",
                "accent_color": "#388E3C",
                "welcome_message": "📚 Welcome to {guild_name}! Happy learning!",
                "level_up_message": "📚 Well done {user}! You reached level {level}!",
                "footer_text": "Study Zone",
                "emoji": "📚"
            },
            "business": {
                "name": "Business Theme",
                "description": "Professional look for business servers",
                "embed_color": "#2196F3",
                "accent_color": "#1976D2",
                "welcome_message": "💼 Welcome to {guild_name}",
                "level_up_message": "💼 Congratulations {user}! Level {level} achieved!",
                "footer_text": "Professional Network",
                "emoji": "💼"
            },
            "community": {
                "name": "Community Theme",
                "description": "Friendly and welcoming",
                "embed_color": "#9C27B0",
                "accent_color": "#7B1FA2",
                "welcome_message": "👋 Welcome to {guild_name}! We're glad you're here!",
                "level_up_message": "🎉 Amazing {user}! You're now level {level}!",
                "footer_text": "Community Hub",
                "emoji": "👋"
            },
            "anime": {
                "name": "Anime Theme",
                "description": "For anime and manga communities",
                "embed_color": "#E91E63",
                "accent_color": "#C2185B",
                "welcome_message": "🌸 Welcome to {guild_name}! Enjoy your stay~",
                "level_up_message": "✨ Sugoi {user}! You're level {level} now!",
                "footer_text": "Anime Paradise",
                "emoji": "🌸"
            },
            "tech": {
                "name": "Tech Theme",
                "description": "For developers and tech enthusiasts",
                "embed_color": "#00BCD4",
                "accent_color": "#0097A7",
                "welcome_message": "💻 Welcome to {guild_name}! <Code.Hello();>",
                "level_up_message": "💻 System.LevelUp({user}, {level});",
                "footer_text": "Tech Hub",
                "emoji": "💻"
            },
            "dark": {
                "name": "Dark Theme",
                "description": "Sleek dark theme",
                "embed_color": "#424242",
                "accent_color": "#212121",
                "welcome_message": "🌙 Welcome to {guild_name}",
                "level_up_message": "⚡ {user} has reached level {level}!",
                "footer_text": "Dark Mode",
                "emoji": "🌙"
            },
            "light": {
                "name": "Light Theme",
                "description": "Clean light theme",
                "embed_color": "#EEEEEE",
                "accent_color": "#E0E0E0",
                "welcome_message": "☀️ Welcome to {guild_name}!",
                "level_up_message": "✨ {user} reached level {level}!",
                "footer_text": "Light Mode",
                "emoji": "☀️"
            }
        }
    
    async def apply_preset(
        self,
        guild_id: str,
        guild_name: str,
        preset_name: str,
        created_by: str
    ) -> Dict[str, Any]:
        """
        Apply a branding preset to guild
        
        Args:
            guild_id: Discord guild ID
            guild_name: Guild name
            preset_name: Preset name (gaming, educational, etc.)
            created_by: User who applied preset
            
        Returns:
            Created branding document
        """
        presets = self.get_branding_presets()
        
        if preset_name not in presets:
            raise ValueError(f"Unknown preset: {preset_name}")
        
        preset = presets[preset_name]
        
        # Remove name, description, emoji from preset
        settings = {k: v for k, v in preset.items() if k not in ["name", "description", "emoji"]}
        settings["created_by"] = created_by
        settings["preset_applied"] = preset_name
        
        # Check if branding exists
        existing = await self.get_branding(guild_id)
        
        if existing:
            # Update existing
            await self.update_branding(guild_id, settings)
            return await self.get_branding(guild_id)
        else:
            # Create new
            return await self.create_branding(guild_id, guild_name, settings)
    
    # ==================== Statistics ====================
    
    async def get_branding_stats(self) -> Dict[str, Any]:
        """Get branding usage statistics"""
        try:
            total = await self.branding.count_documents({})
            enabled = await self.branding.count_documents({"enabled": True})
            
            # Count preset usage
            presets = self.get_branding_presets()
            preset_usage = {}
            
            for preset_name in presets.keys():
                count = await self.branding.count_documents({"preset_applied": preset_name})
                preset_usage[preset_name] = count
            
            # Custom (no preset)
            custom_count = await self.branding.count_documents({"preset_applied": {"$exists": False}})
            
            return {
                "total_guilds_with_branding": total,
                "enabled_branding": enabled,
                "disabled_branding": total - enabled,
                "preset_usage": preset_usage,
                "custom_branding": custom_count,
                "most_popular_preset": max(preset_usage, key=preset_usage.get) if preset_usage else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get branding stats: {e}")
            return {}
    
    async def get_all_guilds_with_branding(self) -> list:
        """Get all guilds that have custom branding"""
        try:
            cursor = self.branding.find({"enabled": True})
            return await cursor.to_list(length=None)
        except Exception as e:
            logger.error(f"Failed to get guilds with branding: {e}")
            return []
    
    # ==================== Validation ====================
    
    @staticmethod
    def validate_branding_settings(settings: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate branding settings
        
        Args:
            settings: Branding settings to validate
            
        Returns:
            (is_valid, error_message)
        """
        # Validate bot nickname
        if "bot_nickname" in settings:
            nickname = settings["bot_nickname"]
            if len(nickname) > 32:
                return False, "Bot nickname must be 32 characters or less"
            if len(nickname) < 2:
                return False, "Bot nickname must be at least 2 characters"
        
        # Validate colors (hex format)
        color_fields = ["embed_color", "accent_color"]
        for field in color_fields:
            if field in settings:
                color = settings[field]
                if not color.startswith("#") or len(color) != 7:
                    return False, f"{field} must be in hex format (#RRGGBB)"
                try:
                    int(color[1:], 16)  # Validate hex
                except ValueError:
                    return False, f"{field} is not a valid hex color"
        
        # Validate URLs
        url_fields = ["logo_url", "banner_url", "icon_url", "footer_icon_url", "bot_avatar_url"]
        for field in url_fields:
            if field in settings and settings[field]:
                url = settings[field]
                if not url.startswith(("http://", "https://")):
                    return False, f"{field} must be a valid URL (http:// or https://)"
        
        # Validate message length
        message_fields = ["welcome_message", "level_up_message", "footer_text"]
        for field in message_fields:
            if field in settings:
                message = settings[field]
                if len(message) > 500:
                    return False, f"{field} must be 500 characters or less"
        
        # Validate custom prefix
        if "custom_prefix" in settings:
            prefix = settings["custom_prefix"]
            if len(prefix) > 5:
                return False, "Custom prefix must be 5 characters or less"
        
        return True, None


# Default branding constants
DEFAULT_EMBED_COLOR = 0x667eea  # Kingdom-77 purple
DEFAULT_ACCENT_COLOR = 0x764ba2
DEFAULT_FOOTER_TEXT = "Kingdom-77 Bot"
DEFAULT_BOT_NICKNAME = "Kingdom-77"

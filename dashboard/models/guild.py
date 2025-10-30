"""
Guild (Server) Models
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Guild(BaseModel):
    """Guild basic info"""
    id: str
    name: str
    icon: Optional[str] = None
    owner: bool = False
    permissions: int = 0
    features: List[str] = []
    
    @property
    def icon_url(self) -> Optional[str]:
        """Get guild icon URL"""
        if self.icon:
            return f"https://cdn.discordapp.com/icons/{self.id}/{self.icon}.png"
        return None
    
    @property
    def has_bot(self) -> bool:
        """Check if bot is in guild (will be populated by API)"""
        return getattr(self, '_has_bot', False)

class GuildSettings(BaseModel):
    """Guild settings from database"""
    guild_id: str
    
    # Moderation
    log_channel: Optional[str] = None
    mod_role: Optional[str] = None
    mute_role: Optional[str] = None
    
    # Leveling
    leveling_enabled: bool = True
    level_up_channel: Optional[str] = None
    level_up_message: str = "🎉 {user} has leveled up to **Level {level}**!"
    xp_rate: float = 1.0
    
    # Tickets
    ticket_category: Optional[str] = None
    ticket_log_channel: Optional[str] = None
    support_role: Optional[str] = None
    
    # Auto-translate
    auto_translate_enabled: bool = False
    
    # General
    prefix: str = "/"
    language: str = "en"
    timezone: str = "UTC"
    
    updated_at: datetime = datetime.utcnow()

class GuildStats(BaseModel):
    """Guild statistics"""
    guild_id: str
    member_count: int
    online_count: int
    total_messages: int
    total_commands: int
    active_tickets: int
    moderation_actions: int
    top_level_users: List[dict] = []

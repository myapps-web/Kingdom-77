"""
User Models
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class User(BaseModel):
    """User model"""
    id: str
    username: str
    discriminator: str
    avatar: Optional[str] = None
    email: Optional[str] = None
    verified: bool = False
    
    @property
    def avatar_url(self) -> str:
        """Get user avatar URL"""
        if self.avatar:
            return f"https://cdn.discordapp.com/avatars/{self.id}/{self.avatar}.png"
        # Default avatar
        return f"https://cdn.discordapp.com/embed/avatars/{int(self.discriminator) % 5}.png"

class UserInDB(User):
    """User in database with additional fields"""
    access_token: str
    refresh_token: str
    token_expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)

class UserResponse(BaseModel):
    """User response model"""
    user: User
    access_token: str
    token_type: str = "Bearer"

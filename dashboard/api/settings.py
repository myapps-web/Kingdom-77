"""
Settings API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from ..models.user import User
from ..models.response import APIResponse
from ..utils.auth import get_current_user
from ..utils.database import get_database

router = APIRouter()

class GuildSettingsUpdate(BaseModel):
    """Settings update model"""
    # Moderation
    log_channel: Optional[str] = None
    mod_role: Optional[str] = None
    mute_role: Optional[str] = None
    
    # Leveling
    leveling_enabled: Optional[bool] = None
    level_up_channel: Optional[str] = None
    level_up_message: Optional[str] = None
    xp_rate: Optional[float] = None
    
    # Tickets
    ticket_category: Optional[str] = None
    ticket_log_channel: Optional[str] = None
    support_role: Optional[str] = None
    
    # Auto-translate
    auto_translate_enabled: Optional[bool] = None
    
    # General
    prefix: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

@router.get("/{guild_id}")
async def get_settings(
    guild_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all guild settings"""
    try:
        db = await get_database()
        
        settings = await db.guild_settings.find_one({'guild_id': guild_id})
        
        if not settings:
            # Return default settings
            return {
                'guild_id': guild_id,
                'leveling_enabled': True,
                'xp_rate': 1.0,
                'level_up_message': "🎉 {user} has leveled up to **Level {level}**!",
                'prefix': '/',
                'language': 'en',
                'timezone': 'UTC',
                'auto_translate_enabled': False
            }
        
        # Remove _id from response
        settings.pop('_id', None)
        return settings
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{guild_id}")
async def update_settings(
    guild_id: str,
    settings: GuildSettingsUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update guild settings"""
    try:
        db = await get_database()
        
        # Only update non-None fields
        update_data = {k: v for k, v in settings.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No settings to update")
        
        await db.guild_settings.update_one(
            {'guild_id': guild_id},
            {'$set': update_data},
            upsert=True
        )
        
        return APIResponse(
            success=True,
            message="Settings updated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{guild_id}/reset")
async def reset_settings(
    guild_id: str,
    current_user: User = Depends(get_current_user)
):
    """Reset settings to defaults"""
    try:
        db = await get_database()
        
        await db.guild_settings.delete_one({'guild_id': guild_id})
        
        return APIResponse(
            success=True,
            message="Settings reset to defaults"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

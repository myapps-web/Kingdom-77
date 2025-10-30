"""
Servers API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.user import User
from ..models.guild import Guild, GuildSettings
from ..models.response import APIResponse
from ..utils.auth import get_current_user, verify_token
from ..utils.discord import DiscordAPI
from ..utils.database import get_database

router = APIRouter()

@router.get("/", response_model=List[Guild])
async def get_user_servers(current_user: User = Depends(get_current_user)):
    """Get user's servers where they have admin permissions"""
    try:
        # Get user's Discord access token from JWT
        from fastapi import Request
        # This will be handled by dependency injection
        
        # For now, get from database
        db = await get_database()
        user_doc = await db.dashboard_users.find_one({'id': current_user.id})
        
        if not user_doc or 'access_token' not in user_doc:
            raise HTTPException(status_code=401, detail="Discord token not found")
        
        # Get user's guilds
        guilds = await DiscordAPI.get_user_guilds(user_doc['access_token'])
        
        # Get bot's guilds
        bot_guilds = await DiscordAPI.get_bot_guilds()
        
        # Filter guilds where user has admin permissions
        admin_guilds = []
        ADMINISTRATOR = 0x8
        MANAGE_GUILD = 0x20
        
        for guild in guilds:
            permissions = int(guild.get('permissions', 0))
            
            # Check if user is owner or has admin/manage permissions
            if guild.get('owner') or (permissions & (ADMINISTRATOR | MANAGE_GUILD)):
                guild_obj = Guild(
                    id=guild['id'],
                    name=guild['name'],
                    icon=guild.get('icon'),
                    owner=guild.get('owner', False),
                    permissions=permissions,
                    features=guild.get('features', [])
                )
                
                # Check if bot is in guild
                guild_obj._has_bot = guild['id'] in bot_guilds
                admin_guilds.append(guild_obj)
        
        return admin_guilds
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{guild_id}", response_model=Guild)
async def get_server(guild_id: str, current_user: User = Depends(get_current_user)):
    """Get specific server info"""
    try:
        # Get guild from Discord API
        guild_data = await DiscordAPI.get_guild(guild_id)
        
        if not guild_data:
            raise HTTPException(status_code=404, detail="Server not found")
        
        guild = Guild(
            id=guild_data['id'],
            name=guild_data['name'],
            icon=guild_data.get('icon'),
            owner=False,  # Will be determined by user guilds
            permissions=0,
            features=guild_data.get('features', [])
        )
        
        return guild
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{guild_id}/settings", response_model=GuildSettings)
async def get_server_settings(guild_id: str, current_user: User = Depends(get_current_user)):
    """Get server settings"""
    try:
        db = await get_database()
        
        # Get settings from database
        settings_doc = await db.guild_settings.find_one({'guild_id': guild_id})
        
        if not settings_doc:
            # Return default settings
            return GuildSettings(guild_id=guild_id)
        
        return GuildSettings(**settings_doc)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{guild_id}/settings", response_model=APIResponse)
async def update_server_settings(
    guild_id: str,
    settings: GuildSettings,
    current_user: User = Depends(get_current_user)
):
    """Update server settings"""
    try:
        db = await get_database()
        
        # Update settings
        await db.guild_settings.update_one(
            {'guild_id': guild_id},
            {'$set': settings.dict()},
            upsert=True
        )
        
        return APIResponse(
            success=True,
            message="Settings updated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

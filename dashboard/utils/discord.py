"""
Discord API Client
"""

import aiohttp
from typing import Optional, List
from ..config import (
    DISCORD_API_BASE,
    DISCORD_OAUTH_TOKEN,
    DISCORD_USER_ENDPOINT,
    DISCORD_GUILDS_ENDPOINT,
    DISCORD_BOT_TOKEN
)

class DiscordAPI:
    """Discord API client"""
    
    @staticmethod
    async def exchange_code(code: str, client_id: str, client_secret: str, redirect_uri: str) -> dict:
        """Exchange OAuth2 code for access token"""
        data = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_OAUTH_TOKEN, data=data, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to exchange code: {await response.text()}")
                return await response.json()
    
    @staticmethod
    async def get_user(access_token: str) -> dict:
        """Get user info from Discord"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(DISCORD_USER_ENDPOINT, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get user: {await response.text()}")
                return await response.json()
    
    @staticmethod
    async def get_user_guilds(access_token: str) -> List[dict]:
        """Get user's guilds"""
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(DISCORD_GUILDS_ENDPOINT, headers=headers) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get guilds: {await response.text()}")
                return await response.json()
    
    @staticmethod
    async def get_bot_guilds() -> List[str]:
        """Get guilds the bot is in"""
        headers = {
            'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{DISCORD_API_BASE}/users/@me/guilds", headers=headers) as response:
                if response.status != 200:
                    return []
                guilds = await response.json()
                return [guild['id'] for guild in guilds]
    
    @staticmethod
    async def get_guild(guild_id: str) -> Optional[dict]:
        """Get guild info"""
        headers = {
            'Authorization': f'Bot {DISCORD_BOT_TOKEN}'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{DISCORD_API_BASE}/guilds/{guild_id}", headers=headers) as response:
                if response.status != 200:
                    return None
                return await response.json()

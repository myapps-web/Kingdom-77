"""
Authentication API Endpoints
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from ..models.user import User, UserResponse
from ..models.response import APIResponse
from ..utils.auth import create_access_token
from ..utils.discord import DiscordAPI
from ..utils.database import get_database
from ..config import (
    DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET,
    DISCORD_REDIRECT_URI,
    DISCORD_OAUTH_AUTHORIZE
)
from datetime import datetime

router = APIRouter()

class LoginRequest(BaseModel):
    """Login request"""
    code: str

@router.get("/login-url")
async def get_login_url():
    """Get Discord OAuth2 login URL"""
    params = {
        'client_id': DISCORD_CLIENT_ID,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'response_type': 'code',
        'scope': 'identify email guilds'
    }
    
    url = DISCORD_OAUTH_AUTHORIZE + '?' + '&'.join([f'{k}={v}' for k, v in params.items()])
    
    return APIResponse(
        success=True,
        data={"url": url}
    )

@router.post("/login", response_model=UserResponse)
async def login(request: LoginRequest):
    """Login with Discord OAuth2 code"""
    try:
        # Exchange code for access token
        token_data = await DiscordAPI.exchange_code(
            request.code,
            DISCORD_CLIENT_ID,
            DISCORD_CLIENT_SECRET,
            DISCORD_REDIRECT_URI
        )
        
        # Get user info
        user_data = await DiscordAPI.get_user(token_data['access_token'])
        
        # Create user object
        user = User(
            id=user_data['id'],
            username=user_data['username'],
            discriminator=user_data['discriminator'],
            avatar=user_data.get('avatar'),
            email=user_data.get('email'),
            verified=user_data.get('verified', False)
        )
        
        # Save to database
        db = await get_database()
        await db.dashboard_users.update_one(
            {'id': user.id},
            {
                '$set': {
                    'username': user.username,
                    'discriminator': user.discriminator,
                    'avatar': user.avatar,
                    'email': user.email,
                    'verified': user.verified,
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data['refresh_token'],
                    'last_login': datetime.utcnow()
                },
                '$setOnInsert': {
                    'created_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Create JWT token
        jwt_token = create_access_token({
            'user': user.dict(),
            'discord_token': token_data['access_token']
        })
        
        return UserResponse(
            user=user,
            access_token=jwt_token
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/logout")
async def logout():
    """Logout (client should delete token)"""
    return APIResponse(
        success=True,
        message="Logged out successfully"
    )

@router.get("/me", response_model=User)
async def get_me(current_user: User = None):
    """Get current user info"""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    return current_user

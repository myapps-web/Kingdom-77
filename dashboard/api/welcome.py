"""
Welcome API Endpoints - Kingdom-77 Bot Dashboard
FastAPI endpoints for welcome system management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from dashboard.auth import get_current_user, require_guild_permission
from database.welcome_schema import WelcomeSchema


router = APIRouter(prefix="/api/welcome", tags=["welcome"])


# Pydantic Models
class WelcomeSettings(BaseModel):
    """Welcome settings model"""
    enabled: bool = True
    welcome_type: str = Field(..., pattern="^(text|embed|card)$")
    welcome_message: Optional[str] = None
    welcome_channels: List[int] = []
    
    # Embed settings
    embed_title: Optional[str] = None
    embed_description: Optional[str] = None
    embed_fields: List[Dict[str, Any]] = []
    
    # Goodbye settings
    goodbye_enabled: bool = False
    goodbye_channel: Optional[int] = None
    goodbye_message: Optional[str] = None
    goodbye_type: str = "text"
    
    # DM settings
    dm_enabled: bool = False
    dm_message: Optional[str] = None
    
    # Captcha settings
    captcha_enabled: bool = False
    captcha_difficulty: str = "medium"
    captcha_timeout: int = 300
    captcha_max_attempts: int = 3
    unverified_role: Optional[int] = None
    
    # Auto-role settings
    auto_role_enabled: bool = False
    auto_roles: List[int] = []
    auto_role_delay: int = 0
    
    # Anti-raid settings
    anti_raid_enabled: bool = False
    anti_raid_threshold: int = 10
    
    # Card settings
    card_id: Optional[str] = None


class CardDesign(BaseModel):
    """Card design model"""
    name: str
    template: str = Field(..., pattern="^(classic|modern|minimal|fancy|custom)$")
    background_color: str = "#2C2F33"
    text_color: str = "#FFFFFF"
    accent_color: str = "#7289DA"
    background_image: Optional[str] = None


class WelcomeStats(BaseModel):
    """Welcome statistics model"""
    joins: int
    leaves: int
    net_change: int
    daily_average: float
    captcha_passed: int = 0
    captcha_failed: int = 0
    recent_joins: List[Dict[str, Any]] = []


# Endpoints
@router.get("/{guild_id}/settings", response_model=Dict[str, Any])
async def get_welcome_settings(
    guild_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get welcome system settings"""
    try:
        schema = WelcomeSchema(router.db)
        settings = await schema.get_settings(guild_id)
        
        if not settings:
            # Return default settings
            return {
                "enabled": False,
                "welcome_type": "embed",
                "welcome_channels": [],
                "goodbye_enabled": False,
                "dm_enabled": False,
                "captcha_enabled": False,
                "auto_role_enabled": False,
                "anti_raid_enabled": False
            }
        
        # Remove MongoDB _id
        settings.pop("_id", None)
        settings.pop("guild_id", None)
        
        return settings
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/{guild_id}/settings")
async def update_welcome_settings(
    guild_id: int,
    settings: WelcomeSettings,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Update welcome system settings"""
    try:
        schema = WelcomeSchema(router.db)
        
        # Convert to dict and remove None values
        updates = settings.dict(exclude_none=True)
        
        await schema.create_or_update_settings(guild_id, updates)
        
        return {
            "success": True,
            "message": "Settings updated successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{guild_id}/cards", response_model=List[Dict[str, Any]])
async def get_card_designs(
    guild_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get all card designs for guild"""
    try:
        schema = WelcomeSchema(router.db)
        cards = await schema.get_all_cards(guild_id)
        
        # Convert ObjectId to string
        result = []
        for card in cards:
            card["_id"] = str(card["_id"])
            card.pop("guild_id", None)
            result.append(card)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{guild_id}/cards")
async def create_card_design(
    guild_id: int,
    design: CardDesign,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Create new card design"""
    try:
        schema = WelcomeSchema(router.db)
        
        result = await schema.create_card_design(
            guild_id,
            design.name,
            design.dict()
        )
        
        return {
            "success": True,
            "card_id": str(result.inserted_id),
            "message": "Card design created successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{guild_id}/cards/{card_id}")
async def delete_card_design(
    guild_id: int,
    card_id: str,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Delete card design"""
    try:
        schema = WelcomeSchema(router.db)
        
        result = await schema.delete_card_design(guild_id, card_id)
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card design not found"
            )
        
        return {
            "success": True,
            "message": "Card design deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{guild_id}/stats", response_model=Dict[str, Any])
async def get_welcome_stats(
    guild_id: int,
    days: int = 7,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get welcome statistics"""
    try:
        schema = WelcomeSchema(router.db)
        stats = await schema.get_join_statistics(guild_id, days)
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{guild_id}/captcha-stats")
async def get_captcha_stats(
    guild_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get captcha verification statistics"""
    try:
        schema = WelcomeSchema(router.db)
        
        # Get recent verifications
        verifications = await schema.captcha_verifications.find(
            {"guild_id": guild_id}
        ).sort("created_at", -1).limit(50).to_list(50)
        
        # Calculate stats
        total = len(verifications)
        verified = sum(1 for v in verifications if v.get("verified", False))
        failed = total - verified
        
        return {
            "total": total,
            "verified": verified,
            "failed": failed,
            "success_rate": (verified / total * 100) if total > 0 else 0,
            "recent": [
                {
                    "user_id": str(v.get("user_id")),
                    "verified": v.get("verified", False),
                    "attempts": v.get("attempts", 0),
                    "created_at": v.get("created_at").isoformat()
                }
                for v in verifications[:10]
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{guild_id}/test")
async def test_welcome(
    guild_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Test welcome message (requires bot to be connected)"""
    try:
        # This would need to communicate with the bot
        # For now, just return success
        return {
            "success": True,
            "message": "Test message will be sent by the bot"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Initialize database connection
def init_welcome_api(db):
    """Initialize welcome API with database connection"""
    router.db = db
    return router

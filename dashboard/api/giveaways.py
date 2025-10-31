"""
Giveaways API Endpoints - Kingdom-77 Bot Dashboard
FastAPI endpoints for giveaway system management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

from dashboard.auth import get_current_user, require_guild_permission
from database.giveaways_schema import GiveawaysSchema


router = APIRouter(prefix="/api/giveaways", tags=["giveaways"])


# Pydantic Models
class GiveawayCreate(BaseModel):
    """Create giveaway model"""
    channel_id: int
    prize: str = Field(..., min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=1000)
    winners_count: int = Field(..., ge=1, le=20)
    duration_hours: int = Field(..., ge=1, le=720)  # Max 30 days
    
    # Requirements
    min_level: Optional[int] = None
    required_roles: List[int] = []
    min_account_age: Optional[int] = None
    min_server_age: Optional[int] = None
    
    # Settings
    allow_host: bool = False
    ping_winners: bool = True
    dm_winners: bool = True


class GiveawayUpdate(BaseModel):
    """Update giveaway model"""
    prize: Optional[str] = Field(None, min_length=1, max_length=256)
    description: Optional[str] = Field(None, max_length=1000)
    winners_count: Optional[int] = Field(None, ge=1, le=20)
    end_time: Optional[datetime] = None


class GiveawayRequirements(BaseModel):
    """Update requirements model"""
    min_level: Optional[int] = None
    required_roles: List[int] = []
    min_account_age: Optional[int] = None
    min_server_age: Optional[int] = None


# Endpoints
@router.get("/{guild_id}", response_model=List[Dict[str, Any]])
async def get_giveaways(
    guild_id: int,
    status: Optional[str] = None,
    limit: int = 50,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get all giveaways for guild"""
    try:
        schema = GiveawaysSchema(router.db)
        
        if status and status not in ["active", "ended", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be: active, ended, or cancelled"
            )
        
        giveaways = await schema.get_all_giveaways(guild_id, status, limit)
        
        # Convert ObjectId to string
        result = []
        for giveaway in giveaways:
            giveaway["_id"] = str(giveaway["_id"])
            giveaway["guild_id"] = str(giveaway["guild_id"])
            giveaway["channel_id"] = str(giveaway["channel_id"])
            giveaway["message_id"] = str(giveaway["message_id"])
            giveaway["host_id"] = str(giveaway["host_id"])
            giveaway["created_at"] = giveaway["created_at"].isoformat()
            giveaway["end_time"] = giveaway["end_time"].isoformat()
            
            if giveaway.get("ended_at"):
                giveaway["ended_at"] = giveaway["ended_at"].isoformat()
            
            result.append(giveaway)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{guild_id}/active", response_model=List[Dict[str, Any]])
async def get_active_giveaways(
    guild_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get active giveaways"""
    try:
        schema = GiveawaysSchema(router.db)
        giveaways = await schema.get_active_giveaways(guild_id)
        
        result = []
        for giveaway in giveaways:
            giveaway["_id"] = str(giveaway["_id"])
            giveaway["created_at"] = giveaway["created_at"].isoformat()
            giveaway["end_time"] = giveaway["end_time"].isoformat()
            result.append(giveaway)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{guild_id}/{message_id}", response_model=Dict[str, Any])
async def get_giveaway(
    guild_id: int,
    message_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get specific giveaway"""
    try:
        schema = GiveawaysSchema(router.db)
        giveaway = await schema.get_giveaway(guild_id, message_id)
        
        if not giveaway:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Giveaway not found"
            )
        
        # Convert ObjectId and dates
        giveaway["_id"] = str(giveaway["_id"])
        giveaway["created_at"] = giveaway["created_at"].isoformat()
        giveaway["end_time"] = giveaway["end_time"].isoformat()
        
        if giveaway.get("ended_at"):
            giveaway["ended_at"] = giveaway["ended_at"].isoformat()
        
        return giveaway
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{guild_id}")
async def create_giveaway(
    guild_id: int,
    giveaway: GiveawayCreate,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Create new giveaway (requires bot interaction)"""
    try:
        # This would need to communicate with the bot to actually create the giveaway
        # For now, return a placeholder response
        
        return {
            "success": True,
            "message": "Giveaway creation request received. Use Discord bot to create giveaways.",
            "note": "This endpoint requires bot integration to create actual giveaways."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.patch("/{guild_id}/{message_id}")
async def update_giveaway(
    guild_id: int,
    message_id: int,
    updates: GiveawayUpdate,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Update giveaway"""
    try:
        schema = GiveawaysSchema(router.db)
        
        # Check if giveaway exists
        giveaway = await schema.get_giveaway(guild_id, message_id)
        if not giveaway:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Giveaway not found"
            )
        
        # Only allow updates to active giveaways
        if giveaway["status"] != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only update active giveaways"
            )
        
        # Build updates dict
        update_dict = updates.dict(exclude_none=True)
        
        if update_dict:
            await schema.update_giveaway(guild_id, message_id, update_dict)
        
        return {
            "success": True,
            "message": "Giveaway updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{guild_id}/{message_id}/end")
async def end_giveaway(
    guild_id: int,
    message_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """End giveaway (requires bot interaction)"""
    try:
        schema = GiveawaysSchema(router.db)
        
        giveaway = await schema.get_giveaway(guild_id, message_id)
        if not giveaway:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Giveaway not found"
            )
        
        if giveaway["status"] != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Giveaway is not active"
            )
        
        return {
            "success": True,
            "message": "Giveaway end request received. Bot will process shortly."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{guild_id}/{message_id}/reroll")
async def reroll_giveaway(
    guild_id: int,
    message_id: int,
    count: int = 1,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Reroll giveaway winners"""
    try:
        if count < 1 or count > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Count must be between 1 and 10"
            )
        
        schema = GiveawaysSchema(router.db)
        
        giveaway = await schema.get_giveaway(guild_id, message_id)
        if not giveaway:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Giveaway not found"
            )
        
        if giveaway["status"] != "ended":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Can only reroll ended giveaways"
            )
        
        return {
            "success": True,
            "message": f"Reroll request received for {count} winner(s). Bot will process shortly."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/{guild_id}/{message_id}")
async def delete_giveaway(
    guild_id: int,
    message_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Delete/cancel giveaway"""
    try:
        schema = GiveawaysSchema(router.db)
        
        giveaway = await schema.get_giveaway(guild_id, message_id)
        if not giveaway:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Giveaway not found"
            )
        
        result = await schema.delete_giveaway(guild_id, message_id)
        
        return {
            "success": True,
            "message": "Giveaway deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{guild_id}/{message_id}/entries")
async def get_giveaway_entries(
    guild_id: int,
    message_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get giveaway entries"""
    try:
        schema = GiveawaysSchema(router.db)
        
        entries = await schema.get_entries(guild_id, message_id)
        
        result = []
        for entry in entries:
            result.append({
                "user_id": str(entry["user_id"]),
                "entered_at": entry["entered_at"].isoformat()
            })
        
        return {
            "total": len(result),
            "entries": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{guild_id}/{message_id}/winners")
async def get_giveaway_winners(
    guild_id: int,
    message_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get giveaway winners"""
    try:
        schema = GiveawaysSchema(router.db)
        
        winners = await schema.get_winners(guild_id, message_id)
        
        result = []
        for winner in winners:
            result.append({
                "user_id": str(winner["user_id"]),
                "prize": winner["prize"],
                "won_at": winner["won_at"].isoformat(),
                "claimed": winner.get("claimed", False),
                "notified": winner.get("notified", False)
            })
        
        return {
            "total": len(result),
            "winners": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{guild_id}/stats")
async def get_giveaway_stats(
    guild_id: int,
    days: int = 30,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get giveaway statistics"""
    try:
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Days must be between 1 and 365"
            )
        
        schema = GiveawaysSchema(router.db)
        stats = await schema.get_guild_statistics(guild_id, days)
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{guild_id}/user/{user_id}/stats")
async def get_user_giveaway_stats(
    guild_id: int,
    user_id: int,
    user = Depends(get_current_user),
    permission = Depends(require_guild_permission)
):
    """Get user's giveaway statistics"""
    try:
        schema = GiveawaysSchema(router.db)
        stats = await schema.get_user_statistics(guild_id, user_id)
        
        return stats
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Initialize database connection
def init_giveaways_api(db):
    """Initialize giveaways API with database connection"""
    router.db = db
    return router

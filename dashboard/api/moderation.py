"""
Moderation API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from ..models.user import User
from ..models.response import APIResponse
from ..utils.auth import get_current_user
from ..utils.database import get_database

router = APIRouter()

class ModerationAction(BaseModel):
    """Moderation action model"""
    user_id: str
    action: str
    reason: Optional[str] = None
    duration: Optional[int] = None

@router.get("/{guild_id}/logs")
async def get_moderation_logs(
    guild_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get moderation logs"""
    try:
        db = await get_database()
        
        logs = await db.moderation_logs.find(
            {'guild_id': guild_id}
        ).sort('timestamp', -1).skip(offset).limit(limit).to_list(limit)
        
        return {
            'logs': [
                {
                    'id': str(log['_id']),
                    'action': log['action'],
                    'user_id': log['user_id'],
                    'moderator_id': log['moderator_id'],
                    'reason': log.get('reason'),
                    'duration': log.get('duration'),
                    'timestamp': log['timestamp'].isoformat()
                }
                for log in logs
            ],
            'total': await db.moderation_logs.count_documents({'guild_id': guild_id})
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{guild_id}/warnings/{user_id}")
async def get_user_warnings(
    guild_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user warnings"""
    try:
        db = await get_database()
        
        warnings = await db.warnings.find(
            {'guild_id': guild_id, 'user_id': user_id}
        ).sort('timestamp', -1).to_list(None)
        
        return {
            'warnings': [
                {
                    'id': str(warn['_id']),
                    'reason': warn['reason'],
                    'moderator_id': warn['moderator_id'],
                    'timestamp': warn['timestamp'].isoformat()
                }
                for warn in warnings
            ],
            'total': len(warnings)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{guild_id}/warnings/{warning_id}")
async def delete_warning(
    guild_id: str,
    warning_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a warning"""
    try:
        db = await get_database()
        from bson import ObjectId
        
        result = await db.warnings.delete_one({
            '_id': ObjectId(warning_id),
            'guild_id': guild_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Warning not found")
        
        return APIResponse(
            success=True,
            message="Warning deleted successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

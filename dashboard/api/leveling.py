"""
Leveling API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from ..models.user import User
from ..models.response import APIResponse
from ..utils.auth import get_current_user
from ..utils.database import get_database

router = APIRouter()

class RoleReward(BaseModel):
    """Role reward model"""
    level: int
    role_id: str

@router.get("/{guild_id}/leaderboard")
async def get_leaderboard(
    guild_id: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get server leaderboard"""
    try:
        db = await get_database()
        
        users = await db.user_levels.find(
            {'guild_id': guild_id}
        ).sort('xp', -1).limit(limit).to_list(limit)
        
        leaderboard = []
        for i, user in enumerate(users, 1):
            leaderboard.append({
                'rank': i,
                'user_id': user['user_id'],
                'level': user['level'],
                'xp': user['xp'],
                'total_xp': user.get('total_xp', user['xp']),
                'messages': user.get('messages', 0)
            })
        
        return {'leaderboard': leaderboard}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{guild_id}/user/{user_id}")
async def get_user_level(
    guild_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user level info"""
    try:
        db = await get_database()
        
        user = await db.user_levels.find_one({
            'guild_id': guild_id,
            'user_id': user_id
        })
        
        if not user:
            return {
                'level': 0,
                'xp': 0,
                'total_xp': 0,
                'messages': 0,
                'rank': None
            }
        
        # Get rank
        rank = await db.user_levels.count_documents({
            'guild_id': guild_id,
            'xp': {'$gt': user['xp']}
        }) + 1
        
        return {
            'level': user['level'],
            'xp': user['xp'],
            'total_xp': user.get('total_xp', user['xp']),
            'messages': user.get('messages', 0),
            'rank': rank
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{guild_id}/rewards")
async def get_role_rewards(
    guild_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get role rewards"""
    try:
        db = await get_database()
        
        rewards = await db.level_roles.find(
            {'guild_id': guild_id}
        ).sort('level', 1).to_list(None)
        
        return {
            'rewards': [
                {
                    'level': reward['level'],
                    'role_id': reward['role_id']
                }
                for reward in rewards
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{guild_id}/rewards")
async def add_role_reward(
    guild_id: str,
    reward: RoleReward,
    current_user: User = Depends(get_current_user)
):
    """Add role reward"""
    try:
        db = await get_database()
        
        await db.level_roles.update_one(
            {'guild_id': guild_id, 'level': reward.level},
            {'$set': {'role_id': reward.role_id}},
            upsert=True
        )
        
        return APIResponse(
            success=True,
            message="Role reward added successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{guild_id}/rewards/{level}")
async def delete_role_reward(
    guild_id: str,
    level: int,
    current_user: User = Depends(get_current_user)
):
    """Delete role reward"""
    try:
        db = await get_database()
        
        result = await db.level_roles.delete_one({
            'guild_id': guild_id,
            'level': level
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Reward not found")
        
        return APIResponse(
            success=True,
            message="Role reward deleted successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

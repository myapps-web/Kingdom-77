"""
Statistics API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from datetime import datetime, timedelta
from ..models.user import User
from ..models.guild import GuildStats
from ..models.response import APIResponse
from ..utils.auth import get_current_user
from ..utils.database import get_database, get_redis

router = APIRouter()

@router.get("/{guild_id}/overview")
async def get_server_overview(guild_id: str, current_user: User = Depends(get_current_user)):
    """Get server overview statistics"""
    try:
        db = await get_database()
        redis = await get_redis()
        
        # Try to get from cache first
        cache_key = f"stats:overview:{guild_id}"
        cached = await redis.get(cache_key)
        
        if cached:
            import json
            return json.loads(cached)
        
        # Get statistics from database
        stats = {
            'total_members': 0,
            'total_messages': 0,
            'total_commands': 0,
            'active_tickets': 0,
            'moderation_actions': 0,
            'leveling_users': 0
        }
        
        # Count members with XP (leveling users)
        stats['leveling_users'] = await db.user_levels.count_documents({
            'guild_id': guild_id
        })
        
        # Count active tickets
        stats['active_tickets'] = await db.tickets.count_documents({
            'guild_id': guild_id,
            'status': 'open'
        })
        
        # Count moderation actions (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        stats['moderation_actions'] = await db.moderation_logs.count_documents({
            'guild_id': guild_id,
            'timestamp': {'$gte': thirty_days_ago}
        })
        
        # Cache for 5 minutes
        import json
        await redis.setex(cache_key, 300, json.dumps(stats))
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{guild_id}/leveling")
async def get_leveling_stats(guild_id: str, current_user: User = Depends(get_current_user)):
    """Get leveling statistics"""
    try:
        db = await get_database()
        
        # Get top 10 users by XP
        top_users = await db.user_levels.find(
            {'guild_id': guild_id}
        ).sort('xp', -1).limit(10).to_list(10)
        
        # Format response
        leaderboard = []
        for i, user in enumerate(top_users, 1):
            leaderboard.append({
                'rank': i,
                'user_id': user['user_id'],
                'level': user['level'],
                'xp': user['xp'],
                'total_xp': user.get('total_xp', user['xp'])
            })
        
        # Get total stats
        total_users = await db.user_levels.count_documents({'guild_id': guild_id})
        
        return {
            'total_users': total_users,
            'leaderboard': leaderboard
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{guild_id}/moderation")
async def get_moderation_stats(guild_id: str, current_user: User = Depends(get_current_user)):
    """Get moderation statistics"""
    try:
        db = await get_database()
        
        # Get stats by action type
        pipeline = [
            {'$match': {'guild_id': guild_id}},
            {'$group': {
                '_id': '$action',
                'count': {'$sum': 1}
            }}
        ]
        
        action_counts = await db.moderation_logs.aggregate(pipeline).to_list(None)
        
        stats = {
            'total': sum(item['count'] for item in action_counts),
            'by_action': {item['_id']: item['count'] for item in action_counts}
        }
        
        # Get recent actions
        recent = await db.moderation_logs.find(
            {'guild_id': guild_id}
        ).sort('timestamp', -1).limit(10).to_list(10)
        
        stats['recent'] = [
            {
                'action': log['action'],
                'user_id': log['user_id'],
                'moderator_id': log['moderator_id'],
                'reason': log.get('reason'),
                'timestamp': log['timestamp'].isoformat()
            }
            for log in recent
        ]
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{guild_id}/tickets")
async def get_ticket_stats(guild_id: str, current_user: User = Depends(get_current_user)):
    """Get ticket statistics"""
    try:
        db = await get_database()
        
        # Get stats by status
        pipeline = [
            {'$match': {'guild_id': guild_id}},
            {'$group': {
                '_id': '$status',
                'count': {'$sum': 1}
            }}
        ]
        
        status_counts = await db.tickets.aggregate(pipeline).to_list(None)
        
        stats = {
            'total': sum(item['count'] for item in status_counts),
            'by_status': {item['_id']: item['count'] for item in status_counts}
        }
        
        # Get recent tickets
        recent = await db.tickets.find(
            {'guild_id': guild_id}
        ).sort('created_at', -1).limit(10).to_list(10)
        
        stats['recent'] = [
            {
                'ticket_id': ticket['ticket_id'],
                'user_id': ticket['user_id'],
                'status': ticket['status'],
                'subject': ticket.get('subject', 'No subject'),
                'created_at': ticket['created_at'].isoformat()
            }
            for ticket in recent
        ]
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

"""
Tickets API Endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models.user import User
from ..models.response import APIResponse
from ..utils.auth import get_current_user
from ..utils.database import get_database

router = APIRouter()

@router.get("/{guild_id}/tickets")
async def get_tickets(
    guild_id: str,
    status: str = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get tickets"""
    try:
        db = await get_database()
        
        query = {'guild_id': guild_id}
        if status:
            query['status'] = status
        
        tickets = await db.tickets.find(query).sort(
            'created_at', -1
        ).limit(limit).to_list(limit)
        
        return {
            'tickets': [
                {
                    'ticket_id': ticket['ticket_id'],
                    'user_id': ticket['user_id'],
                    'channel_id': ticket['channel_id'],
                    'status': ticket['status'],
                    'subject': ticket.get('subject', 'No subject'),
                    'priority': ticket.get('priority', 'normal'),
                    'created_at': ticket['created_at'].isoformat(),
                    'closed_at': ticket.get('closed_at').isoformat() if ticket.get('closed_at') else None
                }
                for ticket in tickets
            ],
            'total': await db.tickets.count_documents(query)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{guild_id}/tickets/{ticket_id}")
async def get_ticket(
    guild_id: str,
    ticket_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific ticket"""
    try:
        db = await get_database()
        
        ticket = await db.tickets.find_one({
            'guild_id': guild_id,
            'ticket_id': ticket_id
        })
        
        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket not found")
        
        return {
            'ticket_id': ticket['ticket_id'],
            'user_id': ticket['user_id'],
            'channel_id': ticket['channel_id'],
            'status': ticket['status'],
            'subject': ticket.get('subject', 'No subject'),
            'priority': ticket.get('priority', 'normal'),
            'created_at': ticket['created_at'].isoformat(),
            'closed_at': ticket.get('closed_at').isoformat() if ticket.get('closed_at') else None,
            'claimed_by': ticket.get('claimed_by')
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

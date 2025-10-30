"""
Email Preferences API Endpoints
Handles user email notification preferences and unsubscribe
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

from ..auth import get_current_user
from database.mongodb import db
from database.email_schema import EmailSchema

logger = logging.getLogger(__name__)
router = APIRouter()

# ==================== Pydantic Models ====================

class EmailPreferencesUpdate(BaseModel):
    """Model for updating email preferences"""
    enabled: Optional[bool] = None
    subscription_emails: Optional[bool] = None
    payment_emails: Optional[bool] = None
    trial_emails: Optional[bool] = None
    weekly_summary: Optional[bool] = None
    marketing_emails: Optional[bool] = None


class UnsubscribeRequest(BaseModel):
    """Model for unsubscribe request"""
    user_id: str
    reason: Optional[str] = None


# ==================== API Endpoints ====================

@router.get("/{user_id}/preferences")
async def get_email_preferences(
    user_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get user's email preferences
    
    Returns current notification settings for the user.
    """
    try:
        # Check authorization (user can only view their own preferences)
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        email_schema = EmailSchema(db)
        preferences = await email_schema.get_user_preferences(user_id)
        
        return preferences
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting email preferences for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/preferences")
async def update_email_preferences(
    user_id: str,
    preferences: EmailPreferencesUpdate,
    current_user_id: str = Depends(get_current_user)
):
    """
    Update user's email preferences
    
    Allows users to enable/disable specific types of email notifications.
    """
    try:
        # Check authorization
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        email_schema = EmailSchema(db)
        
        # Update preferences
        update_data = preferences.model_dump(exclude_none=True)
        success = await email_schema.update_preferences(user_id, **update_data)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to update preferences")
        
        # Return updated preferences
        updated_preferences = await email_schema.get_user_preferences(user_id)
        
        return {
            'success': True,
            'preferences': updated_preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating email preferences for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/unsubscribe")
async def unsubscribe_from_emails(
    user_id: str,
    request: Optional[UnsubscribeRequest] = None
):
    """
    Unsubscribe user from all emails
    
    This endpoint does not require authentication for easy unsubscribe.
    Can be called from email unsubscribe links.
    """
    try:
        email_schema = EmailSchema(db)
        
        success = await email_schema.unsubscribe_user(user_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to unsubscribe")
        
        # Log unsubscribe reason if provided
        if request and request.reason:
            logger.info(f"User {user_id} unsubscribed with reason: {request.reason}")
        
        return {
            'success': True,
            'message': 'You have been unsubscribed from all email notifications'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsubscribing user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/resubscribe")
async def resubscribe_to_emails(
    user_id: str,
    current_user_id: str = Depends(get_current_user)
):
    """
    Resubscribe user to emails
    
    Re-enables email notifications after unsubscribing.
    """
    try:
        # Check authorization
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        email_schema = EmailSchema(db)
        
        # Enable all email preferences
        success = await email_schema.update_preferences(
            user_id,
            enabled=True,
            subscription_emails=True,
            payment_emails=True,
            trial_emails=True,
            weekly_summary=True
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to resubscribe")
        
        logger.info(f"User {user_id} resubscribed to emails")
        
        return {
            'success': True,
            'message': 'You have been resubscribed to email notifications'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resubscribing user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}/history")
async def get_email_history(
    user_id: str,
    limit: int = 50,
    current_user_id: str = Depends(get_current_user)
):
    """
    Get user's email history
    
    Returns list of emails sent to the user.
    """
    try:
        # Check authorization
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        email_schema = EmailSchema(db)
        
        # Get user's email address
        prefs = await email_schema.get_user_preferences(user_id)
        user_email = prefs.get('email')
        
        if not user_email:
            return {'emails': []}
        
        # Get email history
        emails = await email_schema.get_email_history(user_email, limit=limit)
        
        # Format response
        formatted_emails = [
            {
                'subject': email.get('subject'),
                'type': email.get('email_type'),
                'status': email.get('status'),
                'sent_at': email.get('sent_at').isoformat() if email.get('sent_at') else None
            }
            for email in emails
        ]
        
        return {
            'total': len(formatted_emails),
            'emails': formatted_emails
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting email history for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Admin Endpoints ====================

@router.get("/admin/stats")
async def get_email_stats(
    current_user_id: str = Depends(get_current_user)
):
    """
    Admin: Get email statistics
    
    Returns overall email delivery stats.
    """
    try:
        # TODO: Add admin permission check
        
        email_schema = EmailSchema(db)
        
        # Get counts from collections
        total_sent = await db['email_log'].count_documents({'status': 'sent'})
        total_failed = await db['email_log'].count_documents({'status': 'failed'})
        total_queued = await db['email_queue'].count_documents({'status': 'pending'})
        total_unsubscribed = await db['email_preferences'].count_documents({'enabled': False})
        
        # Get email types breakdown
        pipeline = [
            {'$group': {
                '_id': '$email_type',
                'count': {'$sum': 1}
            }},
            {'$sort': {'count': -1}}
        ]
        
        types_breakdown = await db['email_log'].aggregate(pipeline).to_list(100)
        
        return {
            'total_sent': total_sent,
            'total_failed': total_failed,
            'total_queued': total_queued,
            'total_unsubscribed': total_unsubscribed,
            'success_rate': round((total_sent / (total_sent + total_failed)) * 100, 2) if (total_sent + total_failed) > 0 else 0,
            'types_breakdown': {
                item['_id']: item['count']
                for item in types_breakdown
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting email stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/admin/cleanup")
async def cleanup_old_emails(
    days: int = 90,
    current_user_id: str = Depends(get_current_user)
):
    """
    Admin: Clean up old emails
    
    Deletes emails older than specified days from queue and log.
    """
    try:
        # TODO: Add admin permission check
        
        email_schema = EmailSchema(db)
        deleted_count = await email_schema.cleanup_old_emails(days=days)
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'message': f'Cleaned up {deleted_count} old emails'
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up old emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

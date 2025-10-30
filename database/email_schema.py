"""
Email Notifications Schema for Kingdom-77 Bot
==============================================
Handles email queue, tracking, and user preferences
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class EmailSchema:
    """Schema for email notifications system"""
    
    def __init__(self, db):
        """
        Initialize email schema
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.email_queue = db['email_queue']
        self.email_log = db['email_log']
        self.email_preferences = db['email_preferences']
        
    # ==================== Email Queue ====================
    
    async def queue_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        email_type: str,
        priority: int = 5,
        scheduled_for: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add email to queue
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content
            email_type: Type of email (subscription, payment, trial, etc.)
            priority: Priority (1=highest, 10=lowest)
            scheduled_for: When to send (None = send now)
            metadata: Additional metadata
            
        Returns:
            Email queue ID
        """
        try:
            email_doc = {
                'to_email': to_email,
                'subject': subject,
                'html_content': html_content,
                'email_type': email_type,
                'priority': priority,
                'status': 'pending',
                'scheduled_for': scheduled_for or datetime.utcnow(),
                'attempts': 0,
                'max_attempts': 3,
                'metadata': metadata or {},
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = await self.email_queue.insert_one(email_doc)
            
            logger.info(f"Email queued: {email_type} to {to_email} (ID: {result.inserted_id})")
            
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error queuing email: {e}")
            return None
    
    async def get_pending_emails(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get pending emails ready to be sent
        
        Args:
            limit: Maximum number of emails to return
            
        Returns:
            List of pending emails
        """
        try:
            now = datetime.utcnow()
            
            cursor = self.email_queue.find({
                'status': 'pending',
                'scheduled_for': {'$lte': now},
                'attempts': {'$lt': 3}
            }).sort([
                ('priority', 1),  # Lower priority number = higher priority
                ('scheduled_for', 1)
            ]).limit(limit)
            
            emails = await cursor.to_list(length=limit)
            
            return emails
            
        except Exception as e:
            logger.error(f"Error getting pending emails: {e}")
            return []
    
    async def mark_email_sent(self, email_id: str, resend_id: Optional[str] = None) -> bool:
        """
        Mark email as sent
        
        Args:
            email_id: Email queue ID
            resend_id: Resend message ID
            
        Returns:
            True if successful
        """
        try:
            result = await self.email_queue.update_one(
                {'_id': email_id},
                {
                    '$set': {
                        'status': 'sent',
                        'sent_at': datetime.utcnow(),
                        'resend_id': resend_id,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error marking email as sent: {e}")
            return False
    
    async def mark_email_failed(
        self,
        email_id: str,
        error_message: str,
        retry: bool = True
    ) -> bool:
        """
        Mark email as failed
        
        Args:
            email_id: Email queue ID
            error_message: Error message
            retry: Whether to retry sending
            
        Returns:
            True if successful
        """
        try:
            update_data = {
                '$inc': {'attempts': 1},
                '$set': {
                    'last_error': error_message,
                    'updated_at': datetime.utcnow()
                }
            }
            
            # Check if we should retry
            email = await self.email_queue.find_one({'_id': email_id})
            if not email or not retry or email.get('attempts', 0) >= 2:
                update_data['$set']['status'] = 'failed'
            
            result = await self.email_queue.update_one(
                {'_id': email_id},
                update_data
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error marking email as failed: {e}")
            return False
    
    # ==================== Email Log ====================
    
    async def log_email(
        self,
        to_email: str,
        subject: str,
        email_type: str,
        status: str,
        resend_id: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log sent email
        
        Args:
            to_email: Recipient email
            subject: Email subject
            email_type: Type of email
            status: Status (sent/failed)
            resend_id: Resend message ID
            error_message: Error if failed
            metadata: Additional metadata
            
        Returns:
            True if successful
        """
        try:
            log_doc = {
                'to_email': to_email,
                'subject': subject,
                'email_type': email_type,
                'status': status,
                'resend_id': resend_id,
                'error_message': error_message,
                'metadata': metadata or {},
                'sent_at': datetime.utcnow()
            }
            
            await self.email_log.insert_one(log_doc)
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging email: {e}")
            return False
    
    async def get_email_history(
        self,
        user_email: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get email history for a user
        
        Args:
            user_email: User's email address
            limit: Maximum number of emails to return
            
        Returns:
            List of sent emails
        """
        try:
            cursor = self.email_log.find({
                'to_email': user_email
            }).sort('sent_at', -1).limit(limit)
            
            emails = await cursor.to_list(length=limit)
            
            return emails
            
        except Exception as e:
            logger.error(f"Error getting email history: {e}")
            return []
    
    # ==================== Email Preferences ====================
    
    async def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's email preferences
        
        Args:
            user_id: Discord user ID
            
        Returns:
            User preferences dict
        """
        try:
            prefs = await self.email_preferences.find_one({'user_id': user_id})
            
            if not prefs:
                # Return default preferences
                return {
                    'user_id': user_id,
                    'enabled': True,
                    'subscription_emails': True,
                    'payment_emails': True,
                    'trial_emails': True,
                    'weekly_summary': True,
                    'marketing_emails': False,
                    'unsubscribed_at': None,
                    'created_at': datetime.utcnow()
                }
            
            return prefs
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return {}
    
    async def update_preferences(
        self,
        user_id: str,
        **preferences
    ) -> bool:
        """
        Update user's email preferences
        
        Args:
            user_id: Discord user ID
            **preferences: Preferences to update
            
        Returns:
            True if successful
        """
        try:
            # Allowed preference keys
            allowed_keys = [
                'enabled',
                'subscription_emails',
                'payment_emails',
                'trial_emails',
                'weekly_summary',
                'marketing_emails'
            ]
            
            # Filter to only allowed keys
            update_data = {
                k: v for k, v in preferences.items()
                if k in allowed_keys
            }
            
            update_data['updated_at'] = datetime.utcnow()
            
            result = await self.email_preferences.update_one(
                {'user_id': user_id},
                {
                    '$set': update_data,
                    '$setOnInsert': {
                        'user_id': user_id,
                        'created_at': datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            return result.modified_count > 0 or result.upserted_id is not None
            
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return False
    
    async def unsubscribe_user(self, user_id: str) -> bool:
        """
        Unsubscribe user from all emails
        
        Args:
            user_id: Discord user ID
            
        Returns:
            True if successful
        """
        try:
            result = await self.email_preferences.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'enabled': False,
                        'subscription_emails': False,
                        'payment_emails': False,
                        'trial_emails': False,
                        'weekly_summary': False,
                        'marketing_emails': False,
                        'unsubscribed_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    },
                    '$setOnInsert': {
                        'user_id': user_id,
                        'created_at': datetime.utcnow()
                    }
                },
                upsert=True
            )
            
            logger.info(f"User {user_id} unsubscribed from all emails")
            
            return True
            
        except Exception as e:
            logger.error(f"Error unsubscribing user: {e}")
            return False
    
    async def can_send_email(
        self,
        user_id: str,
        email_type: str
    ) -> bool:
        """
        Check if we can send email to user
        
        Args:
            user_id: Discord user ID
            email_type: Type of email
            
        Returns:
            True if email can be sent
        """
        try:
            prefs = await self.get_user_preferences(user_id)
            
            # Check if emails are globally disabled
            if not prefs.get('enabled', True):
                return False
            
            # Check specific email type
            type_mapping = {
                'subscription': 'subscription_emails',
                'payment': 'payment_emails',
                'trial': 'trial_emails',
                'weekly_summary': 'weekly_summary',
                'marketing': 'marketing_emails'
            }
            
            pref_key = type_mapping.get(email_type.split('_')[0], 'enabled')
            
            return prefs.get(pref_key, True)
            
        except Exception as e:
            logger.error(f"Error checking if can send email: {e}")
            return True  # Default to allowing if error
    
    # ==================== Cleanup ====================
    
    async def cleanup_old_emails(self, days: int = 90) -> int:
        """
        Clean up old emails from queue and log
        
        Args:
            days: Delete emails older than this many days
            
        Returns:
            Number of emails deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete from queue
            queue_result = await self.email_queue.delete_many({
                'created_at': {'$lt': cutoff_date},
                'status': {'$in': ['sent', 'failed']}
            })
            
            # Delete from log
            log_result = await self.email_log.delete_many({
                'sent_at': {'$lt': cutoff_date}
            })
            
            total_deleted = queue_result.deleted_count + log_result.deleted_count
            
            logger.info(f"Cleaned up {total_deleted} old emails")
            
            return total_deleted
            
        except Exception as e:
            logger.error(f"Error cleaning up old emails: {e}")
            return 0

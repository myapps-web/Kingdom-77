"""
Email Scheduler for Kingdom-77 Bot
===================================
Handles scheduled email notifications like renewal reminders and trial endings
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class EmailScheduler:
    """Scheduler for automated email notifications"""
    
    def __init__(self, db, email_service, premium_schema):
        """
        Initialize email scheduler
        
        Args:
            db: MongoDB database instance
            email_service: EmailService instance
            premium_schema: PremiumSchema instance
        """
        self.db = db
        self.email_service = email_service
        self.premium_schema = premium_schema
        self.running = False
        
    async def start(self):
        """Start the email scheduler"""
        self.running = True
        logger.info("Email scheduler started")
        
        # Start background tasks
        asyncio.create_task(self._renewal_reminders_task())
        asyncio.create_task(self._trial_ending_task())
        asyncio.create_task(self._process_email_queue())
        
    async def stop(self):
        """Stop the email scheduler"""
        self.running = False
        logger.info("Email scheduler stopped")
    
    # ==================== Renewal Reminders ====================
    
    async def _renewal_reminders_task(self):
        """Background task to send renewal reminders"""
        while self.running:
            try:
                await self._send_renewal_reminders()
            except Exception as e:
                logger.error(f"Error in renewal reminders task: {e}")
            
            # Run every 12 hours
            await asyncio.sleep(12 * 60 * 60)
    
    async def _send_renewal_reminders(self):
        """Send renewal reminders for subscriptions ending soon"""
        try:
            # Find subscriptions ending in 3 days
            three_days = datetime.utcnow() + timedelta(days=3)
            three_days_start = datetime.utcnow() + timedelta(days=2, hours=23)
            
            subscriptions = await self.premium_schema.subscriptions.find({
                'status': 'active',
                'end_date': {
                    '$gte': three_days_start,
                    '$lte': three_days
                },
                'metadata.is_trial': {'$ne': True},
                'metadata.renewal_reminder_sent': {'$ne': True}
            }).to_list(length=100)
            
            logger.info(f"Found {len(subscriptions)} subscriptions to send renewal reminders")
            
            for sub in subscriptions:
                try:
                    # Get user and guild info
                    user_id = sub.get('user_id')
                    guild_id = sub.get('guild_id')
                    
                    # TODO: Get user email, name, guild name from Discord API or database
                    # For now, skip if we don't have email
                    user_email = sub.get('metadata', {}).get('user_email')
                    user_name = sub.get('metadata', {}).get('user_name', 'User')
                    guild_name = sub.get('metadata', {}).get('guild_name', 'Your Server')
                    
                    if not user_email:
                        continue
                    
                    # Check email preferences
                    from database.email_schema import EmailSchema
                    email_schema = EmailSchema(self.db)
                    can_send = await email_schema.can_send_email(user_id, 'subscription')
                    
                    if not can_send:
                        continue
                    
                    # Calculate days until renewal
                    end_date = sub.get('end_date')
                    days_remaining = (end_date - datetime.utcnow()).days if isinstance(end_date, datetime) else 3
                    
                    # Get amount from tier
                    from database.premium_schema import PREMIUM_TIERS
                    tier = sub.get('tier', 'premium')
                    tier_info = PREMIUM_TIERS.get(tier, {})
                    amount = tier_info.get('price_monthly', 4.99)
                    
                    # Format renewal date
                    renewal_date = end_date.strftime('%B %d, %Y') if isinstance(end_date, datetime) else 'soon'
                    
                    # Send email
                    success = await self.email_service.send_renewal_reminder(
                        to_email=user_email,
                        user_name=user_name,
                        guild_name=guild_name,
                        amount=amount,
                        renewal_date=renewal_date,
                        days_until_renewal=days_remaining
                    )
                    
                    if success:
                        # Mark as sent
                        await self.premium_schema.subscriptions.update_one(
                            {'_id': sub['_id']},
                            {'$set': {'metadata.renewal_reminder_sent': True}}
                        )
                        
                        logger.info(f"Sent renewal reminder to {user_email} for guild {guild_id}")
                    
                except Exception as e:
                    logger.error(f"Error sending renewal reminder for subscription {sub.get('_id')}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in _send_renewal_reminders: {e}")
    
    # ==================== Trial Ending Reminders ====================
    
    async def _trial_ending_task(self):
        """Background task to send trial ending reminders"""
        while self.running:
            try:
                await self._send_trial_ending_reminders()
            except Exception as e:
                logger.error(f"Error in trial ending task: {e}")
            
            # Run every 12 hours
            await asyncio.sleep(12 * 60 * 60)
    
    async def _send_trial_ending_reminders(self):
        """Send reminders for trials ending soon"""
        try:
            # Find trials ending in 2 days
            two_days = datetime.utcnow() + timedelta(days=2)
            two_days_start = datetime.utcnow() + timedelta(days=1, hours=23)
            
            trials = await self.premium_schema.subscriptions.find({
                'status': 'active',
                'end_date': {
                    '$gte': two_days_start,
                    '$lte': two_days
                },
                'metadata.is_trial': True,
                'metadata.trial_ending_reminder_sent': {'$ne': True}
            }).to_list(length=100)
            
            logger.info(f"Found {len(trials)} trials to send ending reminders")
            
            for trial in trials:
                try:
                    # Get user and guild info
                    user_id = trial.get('user_id')
                    guild_id = trial.get('guild_id')
                    
                    # Get email info
                    user_email = trial.get('metadata', {}).get('user_email')
                    user_name = trial.get('metadata', {}).get('user_name', 'User')
                    guild_name = trial.get('metadata', {}).get('guild_name', 'Your Server')
                    
                    if not user_email:
                        continue
                    
                    # Check email preferences
                    from database.email_schema import EmailSchema
                    email_schema = EmailSchema(self.db)
                    can_send = await email_schema.can_send_email(user_id, 'trial')
                    
                    if not can_send:
                        continue
                    
                    # Calculate days remaining
                    end_date = trial.get('end_date')
                    days_remaining = (end_date - datetime.utcnow()).days if isinstance(end_date, datetime) else 2
                    
                    # Format trial end date
                    trial_end_date = end_date.strftime('%B %d, %Y') if isinstance(end_date, datetime) else 'soon'
                    
                    # Send email
                    success = await self.email_service.send_trial_ending(
                        to_email=user_email,
                        user_name=user_name,
                        guild_name=guild_name,
                        days_remaining=days_remaining,
                        trial_end_date=trial_end_date
                    )
                    
                    if success:
                        # Mark as sent
                        await self.premium_schema.subscriptions.update_one(
                            {'_id': trial['_id']},
                            {'$set': {'metadata.trial_ending_reminder_sent': True}}
                        )
                        
                        logger.info(f"Sent trial ending reminder to {user_email} for guild {guild_id}")
                    
                except Exception as e:
                    logger.error(f"Error sending trial ending reminder for trial {trial.get('_id')}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in _send_trial_ending_reminders: {e}")
    
    # ==================== Email Queue Processor ====================
    
    async def _process_email_queue(self):
        """Background task to process email queue"""
        while self.running:
            try:
                from database.email_schema import EmailSchema
                email_schema = EmailSchema(self.db)
                
                # Get pending emails
                pending_emails = await email_schema.get_pending_emails(limit=50)
                
                if pending_emails:
                    logger.info(f"Processing {len(pending_emails)} pending emails")
                
                for email in pending_emails:
                    try:
                        # Send email
                        success = await self.email_service.send_email(
                            to_email=email['to_email'],
                            subject=email['subject'],
                            html_content=email['html_content']
                        )
                        
                        if success:
                            # Mark as sent
                            await email_schema.mark_email_sent(
                                email_id=str(email['_id']),
                                resend_id=None  # Would get from Resend response
                            )
                            
                            # Log email
                            await email_schema.log_email(
                                to_email=email['to_email'],
                                subject=email['subject'],
                                email_type=email['email_type'],
                                status='sent',
                                metadata=email.get('metadata', {})
                            )
                        else:
                            # Mark as failed
                            await email_schema.mark_email_failed(
                                email_id=str(email['_id']),
                                error_message="Failed to send email",
                                retry=True
                            )
                            
                    except Exception as e:
                        logger.error(f"Error processing email {email.get('_id')}: {e}")
                        
                        # Mark as failed
                        await email_schema.mark_email_failed(
                            email_id=str(email['_id']),
                            error_message=str(e),
                            retry=True
                        )
                
            except Exception as e:
                logger.error(f"Error in email queue processor: {e}")
            
            # Process queue every 5 minutes
            await asyncio.sleep(5 * 60)
    
    # ==================== Weekly Summary ====================
    
    async def send_weekly_summary(
        self,
        user_id: str,
        guild_id: str,
        user_email: str,
        user_name: str,
        guild_name: str
    ) -> bool:
        """
        Send weekly summary email to user
        
        This should be called by a weekly cron job or scheduled task
        """
        try:
            from database.email_schema import EmailSchema
            email_schema = EmailSchema(self.db)
            
            # Check email preferences
            can_send = await email_schema.can_send_email(user_id, 'weekly_summary')
            
            if not can_send:
                return False
            
            # Gather stats for the week
            # TODO: Implement actual stats gathering from database
            stats = {
                'guild_id': guild_id,
                'new_members': 15,  # Placeholder
                'messages': 1234,  # Placeholder
                'level_ups': 23,  # Placeholder
                'tickets': 8,  # Placeholder
                'top_members': [  # Placeholder
                    'User1#1234',
                    'User2#5678',
                    'User3#9012',
                    'User4#3456',
                    'User5#7890'
                ]
            }
            
            # Send email
            success = await self.email_service.send_weekly_summary(
                to_email=user_email,
                user_name=user_name,
                guild_name=guild_name,
                stats=stats
            )
            
            if success:
                logger.info(f"Sent weekly summary to {user_email} for guild {guild_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending weekly summary: {e}")
            return False

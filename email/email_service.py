"""
Email Service for Kingdom-77 Bot
=================================
Handles all email notifications using Resend with multi-language support
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import resend
from email_templates_i18n import get_email_template, get_supported_languages

logger = logging.getLogger(__name__)

# Initialize Resend
resend.api_key = os.getenv("RESEND_API_KEY")

# Email configuration
FROM_EMAIL = os.getenv("FROM_EMAIL", "Kingdom-77 <notifications@kingdom77.com>")
REPLY_TO_EMAIL = os.getenv("REPLY_TO_EMAIL", "support@kingdom77.com")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "https://kingdom77.com")


class EmailService:
    """Service for sending transactional emails with multi-language support"""
    
    def __init__(self):
        """Initialize email service"""
        self.from_email = FROM_EMAIL
        self.reply_to = REPLY_TO_EMAIL
        self.dashboard_url = DASHBOARD_URL
        self.supported_languages = get_supported_languages()
    
    def detect_user_language(self, user_id: str = None, guild_id: str = None) -> str:
        """
        Detect user's preferred language
        
        Args:
            user_id: Discord user ID
            guild_id: Discord guild ID
            
        Returns:
            Language code (defaults to 'en')
        """
        # TODO: Integrate with database language_schema.py to get user preference
        # For now, return default language
        # Future: Check user_language_preferences collection in MongoDB
        return "en"
        
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        tags: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """
        Send an email using Resend
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text fallback (optional)
            tags: Email tags for tracking (optional)
            
        Returns:
            True if email sent successfully
        """
        try:
            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            }
            
            if text_content:
                params["text"] = text_content
                
            if tags:
                params["tags"] = tags
            
            response = resend.Emails.send(params)
            
            logger.info(f"Email sent to {to_email}: {subject} (ID: {response.get('id')})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def build_email_html(
        self,
        template: Dict[str, Any],
        variables: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """
        Build HTML email content from template
        
        Args:
            template: Email template dictionary
            variables: Variables to fill in template
            language: Language code
            
        Returns:
            HTML email content
        """
        # Direction for RTL languages (Arabic)
        direction = "rtl" if language == "ar" else "ltr"
        text_align = "right" if language == "ar" else "left"
        
        # Format template strings with variables
        subject = template.get("subject", "").format(**variables)
        greeting = template.get("greeting", "").format(**variables)
        title = template.get("title", "").format(**variables)
        message = template.get("message", "").format(**variables)
        cta = template.get("cta", "").format(**variables)
        footer = template.get("footer", "").format(**variables)
        
        # Build features list if exists
        features_html = ""
        if "features" in template:
            features_html = "<ul style='text-align: {text_align};'>"
            for feature in template["features"]:
                features_html += f"<li style='margin: 10px 0;'>{feature}</li>"
            features_html += "</ul>"
        
        # Build HTML
        html = f"""
        <!DOCTYPE html>
        <html dir="{direction}">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; direction: {direction}; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; text-align: {text_align}; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; }}
                .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background: #333; color: #fff; padding: 20px; text-align: center; border-radius: 0 0 10px 10px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                </div>
                <div class="content">
                    <p>{greeting}</p>
                    <p>{message}</p>
                    {features_html}
                    <div style="text-align: center;">
                        <a href="{variables.get('dashboard_url', '#')}" class="button">{cta}</a>
                    </div>
                </div>
                <div class="footer">
                    <p>{footer}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    # ==================== Subscription Emails (Multi-Language) ====================
    
    async def send_subscription_confirmation(
        self,
        to_email: str,
        user_name: str,
        guild_name: str,
        tier: str,
        amount: float,
        interval: str,
        next_billing_date: str,
        user_id: str = None,
        language: str = None
    ) -> bool:
        """
        Send subscription confirmation email in user's language
        
        Args:
            to_email: Recipient email
            user_name: User's name
            guild_name: Server name
            tier: Subscription tier
            amount: Subscription amount
            interval: Billing interval
            next_billing_date: Next billing date
            user_id: Discord user ID (for language detection)
            language: Override language (optional)
        
        Returns:
            True if email sent successfully
        """
        # Detect language if not provided
        if not language:
            language = self.detect_user_language(user_id)
        
        # Get template
        template = get_email_template(language, "subscription_confirmation")
        
        # Variables for template
        variables = {
            "user_name": user_name,
            "guild_name": guild_name,
            "tier": tier,
            "amount": amount,
            "interval": interval,
            "next_billing_date": next_billing_date,
            "dashboard_url": self.dashboard_url
        }
        
        # Build email
        subject = template.get("subject", "✅ Welcome to Kingdom-77 Premium!")
        html_content = self.build_email_html(template, variables, language)
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags=[{"name": "category", "value": "subscription_confirmation"}]
        )
    
    async def send_renewal_reminder(
        self,
        to_email: str,
        user_name: str,
        guild_name: str,
        amount: float,
        renewal_date: str,
        days_until_renewal: int
    ) -> bool:
        """Send subscription renewal reminder"""
        
        subject = f"⏰ Your Kingdom-77 Premium subscription renews in {days_until_renewal} days"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .info-box {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Renewal Reminder</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>This is a friendly reminder that your Kingdom-77 Premium subscription for <strong>{guild_name}</strong> will automatically renew in <strong>{days_until_renewal} days</strong>.</p>
                    
                    <div class="info-box">
                        <h3>📋 Renewal Details</h3>
                        <p><strong>Amount:</strong> ${amount:.2f}</p>
                        <p><strong>Renewal Date:</strong> {renewal_date}</p>
                        <p><strong>Payment Method:</strong> Card on file</p>
                    </div>
                    
                    <p>No action is needed - we'll automatically charge your payment method on file.</p>
                    
                    <p>If you need to update your payment method or billing information:</p>
                    
                    <p style="text-align: center;">
                        <a href="{self.dashboard_url}/billing" class="button">
                            Manage Billing
                        </a>
                    </p>
                    
                    <p>Want to cancel? You can do so at any time from your dashboard, and you'll retain access until the end of your billing period.</p>
                    
                    <p>Best regards,<br>The Kingdom-77 Team 👑</p>
                </div>
                <div class="footer">
                    <p>Kingdom-77 Bot | <a href="{self.dashboard_url}/settings/emails">Email Preferences</a> | <a href="{self.dashboard_url}/unsubscribe">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags=[{"name": "category", "value": "renewal_reminder"}]
        )
    
    async def send_payment_success(
        self,
        to_email: str,
        user_name: str,
        guild_name: str,
        amount: float,
        invoice_url: str,
        next_billing_date: str
    ) -> bool:
        """Send payment success notification"""
        
        subject = f"✅ Payment Received - Kingdom-77 Premium"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .info-box {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #10b981; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Payment Received</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>Thank you! We've successfully processed your payment for Kingdom-77 Premium.</p>
                    
                    <div class="info-box">
                        <h3>💳 Payment Details</h3>
                        <p><strong>Server:</strong> {guild_name}</p>
                        <p><strong>Amount Paid:</strong> ${amount:.2f}</p>
                        <p><strong>Next Billing Date:</strong> {next_billing_date}</p>
                    </div>
                    
                    <p style="text-align: center;">
                        <a href="{invoice_url}" class="button">
                            Download Invoice
                        </a>
                    </p>
                    
                    <p>Your Premium features continue uninterrupted. Thank you for supporting Kingdom-77!</p>
                    
                    <p>Best regards,<br>The Kingdom-77 Team 👑</p>
                </div>
                <div class="footer">
                    <p>Kingdom-77 Bot | <a href="{self.dashboard_url}/settings/emails">Email Preferences</a> | <a href="{self.dashboard_url}/unsubscribe">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags=[{"name": "category", "value": "payment_success"}]
        )
    
    async def send_payment_failed(
        self,
        to_email: str,
        user_name: str,
        guild_name: str,
        amount: float,
        retry_date: str
    ) -> bool:
        """Send payment failure notification"""
        
        subject = f"⚠️ Payment Failed - Action Required"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #ef4444; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .warning-box {{ background: #fef3c7; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Payment Failed</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>We were unable to process your payment for Kingdom-77 Premium subscription.</p>
                    
                    <div class="warning-box">
                        <h3>📋 Payment Details</h3>
                        <p><strong>Server:</strong> {guild_name}</p>
                        <p><strong>Amount:</strong> ${amount:.2f}</p>
                        <p><strong>Next Retry:</strong> {retry_date}</p>
                    </div>
                    
                    <p><strong>What happens now?</strong></p>
                    <ul>
                        <li>We'll automatically retry charging your payment method on {retry_date}</li>
                        <li>Your Premium features remain active for now</li>
                        <li>If payment continues to fail, your subscription may be cancelled</li>
                    </ul>
                    
                    <p><strong>How to fix this:</strong></p>
                    <ol>
                        <li>Check that your payment method has sufficient funds</li>
                        <li>Update your payment method if needed</li>
                        <li>Contact your bank if you're having issues</li>
                    </ol>
                    
                    <p style="text-align: center;">
                        <a href="{self.dashboard_url}/billing" class="button">
                            Update Payment Method
                        </a>
                    </p>
                    
                    <p>Need help? Contact our support team and we'll assist you!</p>
                    
                    <p>Best regards,<br>The Kingdom-77 Team 👑</p>
                </div>
                <div class="footer">
                    <p>Kingdom-77 Bot | <a href="{self.dashboard_url}/settings/emails">Email Preferences</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags=[{"name": "category", "value": "payment_failed"}]
        )
    
    async def send_trial_started(
        self,
        to_email: str,
        user_name: str,
        guild_name: str,
        trial_end_date: str
    ) -> bool:
        """Send trial started notification"""
        
        subject = f"🎉 Your 7-Day Premium Trial Has Started!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #8b5cf6; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .info-box {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #8b5cf6; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Trial Started!</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>Great news! Your 7-day Premium trial for <strong>{guild_name}</strong> has started!</p>
                    
                    <div class="info-box">
                        <h3>📅 Trial Details</h3>
                        <p><strong>Trial Period:</strong> 7 days (FREE)</p>
                        <p><strong>Ends:</strong> {trial_end_date}</p>
                        <p><strong>No payment required during trial</strong></p>
                    </div>
                    
                    <h3>✨ Explore Premium Features:</h3>
                    <ul>
                        <li>🎨 Custom Level Cards with 8 templates</li>
                        <li>⚡ 2x XP Boost</li>
                        <li>🎭 Unlimited Custom Commands</li>
                        <li>🎯 Unlimited Auto-Roles</li>
                        <li>📊 Advanced Analytics</li>
                        <li>💎 Premium Badge</li>
                        <li>And much more!</li>
                    </ul>
                    
                    <p style="text-align: center;">
                        <a href="{self.dashboard_url}/servers" class="button">
                            Start Exploring
                        </a>
                    </p>
                    
                    <p><strong>After your trial:</strong> You can choose to subscribe or cancel at any time. No charges until you decide to continue.</p>
                    
                    <p>Enjoy your trial!</p>
                    
                    <p>Best regards,<br>The Kingdom-77 Team 👑</p>
                </div>
                <div class="footer">
                    <p>Kingdom-77 Bot | <a href="{self.dashboard_url}/settings/emails">Email Preferences</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags=[{"name": "category", "value": "trial_started"}]
        )
    
    async def send_trial_ending(
        self,
        to_email: str,
        user_name: str,
        guild_name: str,
        days_remaining: int,
        trial_end_date: str
    ) -> bool:
        """Send trial ending reminder"""
        
        subject = f"⏰ Your Premium Trial Ends in {days_remaining} Days"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #f59e0b; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .info-box {{ background: white; padding: 20px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #f59e0b; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Trial Ending Soon</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>Your 7-day Premium trial for <strong>{guild_name}</strong> ends in <strong>{days_remaining} days</strong> on {trial_end_date}.</p>
                    
                    <div class="info-box">
                        <h3>💎 Love Premium?</h3>
                        <p>Subscribe now to keep all these amazing features:</p>
                        <ul>
                            <li>Custom Level Cards</li>
                            <li>2x XP Boost</li>
                            <li>Unlimited Commands & Roles</li>
                            <li>Advanced Analytics</li>
                            <li>Premium Support</li>
                        </ul>
                    </div>
                    
                    <p><strong>Pricing:</strong></p>
                    <ul>
                        <li>💎 Monthly: $4.99/month</li>
                        <li>💎 Yearly: $49.99/year (Save 17%!)</li>
                    </ul>
                    
                    <p style="text-align: center;">
                        <a href="{self.dashboard_url}/premium" class="button">
                            Subscribe Now
                        </a>
                    </p>
                    
                    <p>Don't want to continue? No worries - no action needed. Your trial will simply expire and you'll return to the free plan.</p>
                    
                    <p>Best regards,<br>The Kingdom-77 Team 👑</p>
                </div>
                <div class="footer">
                    <p>Kingdom-77 Bot | <a href="{self.dashboard_url}/settings/emails">Email Preferences</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags=[{"name": "category", "value": "trial_ending"}]
        )
    
    # ==================== Report Emails ====================
    
    async def send_weekly_summary(
        self,
        to_email: str,
        user_name: str,
        guild_name: str,
        stats: Dict[str, Any]
    ) -> bool:
        """Send weekly server summary"""
        
        subject = f"📊 Weekly Summary for {guild_name}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }}
                .stat-card {{ background: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .stat-number {{ font-size: 32px; font-weight: bold; color: #3b82f6; }}
                .stat-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: #3b82f6; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Weekly Summary</h1>
                    <p>{guild_name}</p>
                </div>
                <div class="content">
                    <p>Hi {user_name},</p>
                    
                    <p>Here's what happened in <strong>{guild_name}</strong> this week:</p>
                    
                    <div class="stat-grid">
                        <div class="stat-card">
                            <div class="stat-number">{stats.get('new_members', 0)}</div>
                            <div class="stat-label">New Members</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{stats.get('messages', 0)}</div>
                            <div class="stat-label">Messages Sent</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{stats.get('level_ups', 0)}</div>
                            <div class="stat-label">Level Ups</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">{stats.get('tickets', 0)}</div>
                            <div class="stat-label">Tickets Created</div>
                        </div>
                    </div>
                    
                    <h3>🏆 Top Members:</h3>
                    <ol>
                        {"".join(f"<li>{member}</li>" for member in stats.get('top_members', [])[:5])}
                    </ol>
                    
                    <p style="text-align: center;">
                        <a href="{self.dashboard_url}/servers/{stats.get('guild_id')}/stats" class="button">
                            View Full Report
                        </a>
                    </p>
                    
                    <p>Keep up the great work!</p>
                    
                    <p>Best regards,<br>The Kingdom-77 Team 👑</p>
                </div>
                <div class="footer">
                    <p>Kingdom-77 Bot | <a href="{self.dashboard_url}/settings/emails">Email Preferences</a> | <a href="{self.dashboard_url}/unsubscribe">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            tags=[{"name": "category", "value": "weekly_summary"}]
        )


# Global email service instance
email_service = EmailService()

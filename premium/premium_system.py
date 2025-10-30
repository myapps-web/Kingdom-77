"""
Premium System Core
Handles subscription management, multi-provider payment integration, and feature access
Supports: Stripe (international), Moyasar (Saudi Arabia/GCC)
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

class PremiumSystem:
    """Premium subscription and feature management system with multi-provider support"""
    
    def __init__(self, mongodb_client: AsyncIOMotorClient):
        from database.premium_schema import PremiumSchema
        from database.email_schema import EmailSchema
        from email.email_service import email_service
        
        self.schema = PremiumSchema(mongodb_client)
        self.email_schema = EmailSchema(mongodb_client.db)
        self.email_service = email_service
        self.mongodb_client = mongodb_client
        
        # Payment provider configuration
        self.payment_provider_name = os.getenv("PAYMENT_PROVIDER", "stripe").lower()
        self.payment_provider = None
        self._initialize_payment_provider()
        
        # Credits system (lazy load)
        self._credits_system = None
    
    def _initialize_payment_provider(self):
        """Initialize the configured payment provider"""
        if self.payment_provider_name == "moyasar":
            try:
                from premium.moyasar_system import MoyasarProvider
                self.payment_provider = MoyasarProvider()
                if self.payment_provider.is_configured():
                    logger.info("✅ Moyasar payment provider initialized")
                else:
                    logger.warning("⚠️ Moyasar provider selected but not configured")
                    self.payment_provider = None
            except Exception as e:
                logger.error(f"Failed to initialize Moyasar provider: {e}")
                self.payment_provider = None
        
        elif self.payment_provider_name == "stripe":
            try:
                import stripe
                stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
                if stripe.api_key:
                    self.stripe = stripe
                    logger.info("✅ Stripe payment provider initialized")
                else:
                    logger.warning("⚠️ Stripe provider selected but STRIPE_SECRET_KEY not set")
                    self.stripe = None
            except Exception as e:
                logger.error(f"Failed to initialize Stripe provider: {e}")
                self.stripe = None
        
        else:
            logger.warning(f"Unknown payment provider: {self.payment_provider_name}. Defaulting to Stripe.")
            self.payment_provider_name = "stripe"
            self._initialize_payment_provider()
    
    async def initialize(self):
        """Initialize premium system"""
        await self.schema.initialize()
    
    # Subscription Management
    
    async def create_subscription(
        self,
        user_id: str,
        guild_id: str,
        tier: str,
        duration_days: int = 30,
        payment_method: str = "stripe",
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
        guild_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new subscription"""
        # Create subscription in database
        subscription = await self.schema.create_subscription(
            user_id=user_id,
            guild_id=guild_id,
            tier=tier,
            duration_days=duration_days
        )
        
        # Send subscription confirmation email
        if user_email and user_name and guild_name:
            try:
                # Check if user wants subscription emails
                can_send = await self.email_schema.can_send_email(user_id, 'subscription')
                
                if can_send:
                    from database.premium_schema import PREMIUM_TIERS
                    tier_info = PREMIUM_TIERS.get(tier, {})
                    
                    # Determine amount and interval
                    if duration_days <= 31:
                        amount = tier_info.get('price_monthly', 4.99)
                        interval = 'month'
                    else:
                        amount = tier_info.get('price_yearly', 49.99)
                        interval = 'year'
                    
                    # Calculate next billing date
                    next_billing = subscription.get('end_date', datetime.utcnow() + timedelta(days=duration_days))
                    next_billing_str = next_billing.strftime('%B %d, %Y') if isinstance(next_billing, datetime) else next_billing
                    
                    await self.email_service.send_subscription_confirmation(
                        to_email=user_email,
                        user_name=user_name,
                        guild_name=guild_name,
                        tier=tier,
                        amount=amount,
                        interval=interval,
                        next_billing_date=next_billing_str
                    )
                    
                    logger.info(f"Sent subscription confirmation email to {user_email}")
            except Exception as e:
                logger.error(f"Failed to send subscription confirmation email: {e}")
        
        return subscription
    
    async def get_subscription(
        self,
        user_id: Optional[str] = None,
        guild_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get active subscription"""
        if user_id and guild_id:
            return await self.schema.get_subscription(user_id, guild_id)
        elif guild_id:
            return await self.schema.get_guild_subscription(guild_id)
        return None
    
    async def is_premium(self, guild_id: str) -> bool:
        """Check if guild has active premium subscription"""
        subscription = await self.schema.get_guild_subscription(guild_id)
        return subscription is not None
    
    async def get_tier(self, guild_id: str) -> Optional[str]:
        """Get subscription tier for guild"""
        subscription = await self.schema.get_guild_subscription(guild_id)
        return subscription["tier"] if subscription else None
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """Cancel a subscription"""
        return await self.schema.cancel_subscription(subscription_id)
    
    async def renew_subscription(
        self,
        subscription_id: str,
        duration_days: int = 30
    ) -> bool:
        """Renew a subscription"""
        return await self.schema.renew_subscription(subscription_id, duration_days)
    
    # Feature Access Control
    
    async def has_feature(self, guild_id: str, feature_id: str) -> bool:
        """Check if guild has access to a premium feature"""
        return await self.schema.has_feature(guild_id, feature_id)
    
    async def get_guild_features(self, guild_id: str) -> List[str]:
        """Get all features available to a guild"""
        subscription = await self.schema.get_guild_subscription(guild_id)
        if not subscription:
            return []
        return subscription.get("features", [])
    
    async def get_tier_features(self, tier: str) -> List[str]:
        """Get all features for a tier"""
        return await self.schema.get_tier_features(tier)
    
    async def get_all_features(self) -> List[Dict[str, Any]]:
        """Get all available premium features"""
        return await self.schema.get_all_features()
    
    # Feature Usage Tracking
    
    async def track_usage(
        self,
        guild_id: str,
        feature_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Track feature usage"""
        await self.schema.track_feature_usage(
            guild_id=guild_id,
            feature_id=feature_id,
            user_id=user_id,
            metadata=metadata
        )
    
    async def get_usage_stats(self, guild_id: str, days: int = 30) -> Dict[str, int]:
        """Get feature usage statistics"""
        return await self.schema.get_feature_usage_stats(guild_id, days)
    
    # Stripe Integration
    
    async def create_checkout_session(
        self,
        user_id: str,
        guild_id: str,
        tier: str,
        billing_period: str = "monthly",
        success_url: str = None,
        cancel_url: str = None
    ) -> Optional[str]:
        """Create checkout session using configured payment provider"""
        from database.premium_schema import PREMIUM_TIERS
        
        tier_info = PREMIUM_TIERS.get(tier)
        if not tier_info:
            logger.error(f"Unknown tier: {tier}")
            return None
        
        price = tier_info[f"price_{billing_period}"]
        
        # Route to appropriate payment provider
        if self.payment_provider_name == "moyasar" and self.payment_provider:
            try:
                return await self.payment_provider.create_checkout_session(
                    user_id=user_id,
                    guild_id=guild_id,
                    tier=tier,
                    amount=price,
                    billing_period=billing_period,
                    success_url=success_url,
                    cancel_url=cancel_url
                )
            except Exception as e:
                logger.error(f"Error creating Moyasar checkout session: {e}")
                return None
        
        elif self.payment_provider_name == "stripe" and hasattr(self, 'stripe') and self.stripe:
            try:
                session = self.stripe.checkout.Session.create(
                    payment_method_types=["card"],
                    line_items=[{
                        "price_data": {
                            "currency": "usd",
                            "unit_amount": int(price * 100),  # Convert to cents
                            "product_data": {
                                "name": f"Kingdom-77 {tier_info['name']} - {billing_period.title()}",
                                "description": f"Premium subscription for server {guild_id}"
                            },
                            "recurring": {
                                "interval": "month" if billing_period == "monthly" else "year"
                            }
                        },
                        "quantity": 1
                    }],
                    mode="subscription",
                    success_url=success_url or "https://your-domain.com/success",
                    cancel_url=cancel_url or "https://your-domain.com/cancel",
                    metadata={
                        "user_id": user_id,
                        "guild_id": guild_id,
                        "tier": tier
                    }
                )
                
                return session.url
            except Exception as e:
                logger.error(f"Error creating Stripe checkout session: {e}")
                return None
        
        else:
            logger.error(f"Payment provider not configured: {self.payment_provider_name}")
            return None
    
    async def handle_webhook(
        self,
        event: Dict[str, Any],
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
        guild_name: Optional[str] = None
    ) -> bool:
        """Handle webhook event from configured payment provider"""
        
        # Route to appropriate payment provider
        if self.payment_provider_name == "moyasar" and self.payment_provider:
            try:
                return await self.payment_provider.handle_webhook(event, self)
            except Exception as e:
                logger.error(f"Error handling Moyasar webhook: {e}")
                return False
        
        elif self.payment_provider_name == "stripe" and hasattr(self, 'stripe') and self.stripe:
            return await self._handle_stripe_webhook(event, user_email, user_name, guild_name)
        
        else:
            logger.error(f"Payment provider not configured for webhooks: {self.payment_provider_name}")
            return False
    
    async def _handle_stripe_webhook(
        self,
        event: Dict[str, Any],
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
        guild_name: Optional[str] = None
    ) -> bool:
        """Handle Stripe-specific webhook event"""
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        
        if event_type == "checkout.session.completed":
            # Payment successful - create subscription
            metadata = data.get("metadata", {})
            user_id = metadata.get("user_id")
            guild_id = metadata.get("guild_id")
            tier = metadata.get("tier")
            
            if user_id and guild_id and tier:
                duration = 30 if data.get("mode") == "subscription" else 365
                await self.create_subscription(
                    user_id=user_id,
                    guild_id=guild_id,
                    tier=tier,
                    duration_days=duration,
                    user_email=user_email,
                    user_name=user_name,
                    guild_name=guild_name
                )
                
                # Record payment
                amount = data.get("amount_total", 0) / 100
                await self.schema.record_payment(
                    user_id=user_id,
                    guild_id=guild_id,
                    amount=amount,
                    currency=data.get("currency", "usd"),
                    tier=tier,
                    stripe_payment_id=data.get("payment_intent", ""),
                    status="completed"
                )
                
                # Send payment success email
                if user_email and user_name and guild_name:
                    try:
                        can_send = await self.email_schema.can_send_email(user_id, 'payment')
                        
                        if can_send:
                            # Get subscription for next billing date
                            subscription = await self.schema.get_guild_subscription(guild_id)
                            next_billing = subscription.get('end_date', datetime.utcnow() + timedelta(days=duration))
                            next_billing_str = next_billing.strftime('%B %d, %Y') if isinstance(next_billing, datetime) else next_billing
                            
                            # Get invoice URL from Stripe
                            invoice_url = data.get("invoice", "")
                            if not invoice_url:
                                invoice_url = f"https://dashboard.stripe.com/invoices/{data.get('payment_intent', '')}"
                            
                            await self.email_service.send_payment_success(
                                to_email=user_email,
                                user_name=user_name,
                                guild_name=guild_name,
                                amount=amount,
                                invoice_url=invoice_url,
                                next_billing_date=next_billing_str
                            )
                            
                            logger.info(f"Sent payment success email to {user_email}")
                    except Exception as e:
                        logger.error(f"Failed to send payment success email: {e}")
        
        elif event_type == "invoice.payment_failed":
            # Payment failed
            metadata = data.get("metadata", {})
            user_id = metadata.get("user_id")
            guild_id = metadata.get("guild_id")
            amount = data.get("amount_due", 0) / 100
            
            if user_email and user_name and guild_name:
                try:
                    can_send = await self.email_schema.can_send_email(user_id, 'payment')
                    
                    if can_send:
                        # Calculate retry date (usually 3 days)
                        retry_date = (datetime.utcnow() + timedelta(days=3)).strftime('%B %d, %Y')
                        
                        await self.email_service.send_payment_failed(
                            to_email=user_email,
                            user_name=user_name,
                            guild_name=guild_name,
                            amount=amount,
                            retry_date=retry_date
                        )
                        
                        logger.info(f"Sent payment failed email to {user_email}")
                except Exception as e:
                    logger.error(f"Failed to send payment failed email: {e}")
        
        elif event_type == "customer.subscription.deleted":
            # Subscription cancelled
            subscription_id = data.get("metadata", {}).get("subscription_id")
            if subscription_id:
                await self.cancel_subscription(subscription_id)
        
        return True
    
    # XP Boost System
    
    async def get_xp_multiplier(self, guild_id: str) -> float:
        """Get XP multiplier for guild"""
        if await self.has_feature(guild_id, "xp_boost"):
            return 2.0
        return 1.0
    
    async def apply_xp_boost(self, guild_id: str, base_xp: int) -> int:
        """Apply XP boost if available"""
        multiplier = await self.get_xp_multiplier(guild_id)
        return int(base_xp * multiplier)
    
    # Limits & Quotas
    
    async def get_limit(self, guild_id: str, limit_name: str) -> int:
        """Get limit for a specific feature"""
        from database.premium_schema import PREMIUM_TIERS
        
        tier = await self.get_tier(guild_id)
        if not tier:
            # Free tier limits
            limits = {
                "max_custom_commands": 5,
                "max_autoroles": 10,
                "max_tickets": 50
            }
            return limits.get(limit_name, 0)
        
        tier_info = PREMIUM_TIERS.get(tier, {})
        limits = tier_info.get("limits", {})
        return limits.get(limit_name, 0)
    
    async def check_limit(
        self,
        guild_id: str,
        limit_name: str,
        current_usage: int
    ) -> bool:
        """Check if guild has reached limit"""
        limit = await self.get_limit(guild_id, limit_name)
        if limit == -1:  # Unlimited
            return True
        return current_usage < limit
    
    # Statistics
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get premium system statistics"""
        return await self.schema.get_subscription_stats()
    
    async def cleanup_expired(self) -> int:
        """Cleanup expired subscriptions"""
        return await self.schema.cleanup_expired_subscriptions()
    
    # Trial System
    
    async def start_trial(
        self,
        user_id: str,
        guild_id: str,
        tier: str = "premium",
        trial_days: int = 7,
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
        guild_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a free trial"""
        # Check if guild already had a trial
        existing = await self.schema.subscriptions.find_one({
            "guild_id": guild_id,
            "metadata.is_trial": True
        })
        
        if existing:
            raise Exception("Guild already used trial")
        
        subscription = await self.schema.create_subscription(
            user_id=user_id,
            guild_id=guild_id,
            tier=tier,
            duration_days=trial_days
        )
        
        # Mark as trial
        await self.schema.subscriptions.update_one(
            {"_id": subscription["_id"]},
            {"$set": {"metadata.is_trial": True}}
        )
        
        # Send trial started email
        if user_email and user_name and guild_name:
            try:
                can_send = await self.email_schema.can_send_email(user_id, 'trial')
                
                if can_send:
                    trial_end = subscription.get('end_date', datetime.utcnow() + timedelta(days=trial_days))
                    trial_end_str = trial_end.strftime('%B %d, %Y') if isinstance(trial_end, datetime) else trial_end
                    
                    await self.email_service.send_trial_started(
                        to_email=user_email,
                        user_name=user_name,
                        guild_name=guild_name,
                        trial_end_date=trial_end_str
                    )
                    
                    logger.info(f"Sent trial started email to {user_email}")
            except Exception as e:
                logger.error(f"Failed to send trial started email: {e}")
        
        return subscription
    
    # Gifting System
    
    async def gift_subscription(
        self,
        gifter_user_id: str,
        recipient_guild_id: str,
        tier: str,
        duration_days: int = 30
    ) -> Dict[str, Any]:
        """Gift a subscription to another guild"""
        subscription = await self.schema.create_subscription(
            user_id=gifter_user_id,
            guild_id=recipient_guild_id,
            tier=tier,
            duration_days=duration_days
        )
        
        # Mark as gift
        await self.schema.subscriptions.update_one(
            {"_id": subscription["_id"]},
            {"$set": {
                "metadata.is_gift": True,
                "metadata.gifted_by": gifter_user_id
            }}
        )
        
        return subscription
    
    # Promo Codes
    
    async def apply_promo_code(
        self,
        code: str,
        user_id: str,
        guild_id: str
    ) -> Optional[Dict[str, Any]]:
        """Apply promo code for discount or free subscription"""
        # This would integrate with a promo codes collection
        # For now, return None
        # TODO: Implement promo code system
        return None
    
    # Credits Payment System
    
    @property
    def credits_system(self):
        """Lazy load credits system"""
        if self._credits_system is None:
            from economy.credits_system import CreditsSystem
            self._credits_system = CreditsSystem(self.mongodb_client)
        return self._credits_system
    
    async def purchase_with_credits(
        self,
        user_id: str,
        guild_id: str,
        tier: str,
        billing_period: str = "monthly",
        user_email: Optional[str] = None,
        user_name: Optional[str] = None,
        guild_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Purchase premium subscription using K77 Credits
        
        Pricing:
        - Monthly: 500 ❄️ credits
        - Yearly: 5000 ❄️ credits (save 1000 vs monthly * 12)
        
        Args:
            user_id: User making the purchase
            guild_id: Guild to activate premium for
            tier: Premium tier (only "premium" supported for credits)
            billing_period: "monthly" or "yearly"
            user_email: User's email for notifications
            user_name: User's name for notifications
            guild_name: Guild's name for notifications
        
        Returns:
            Dict with subscription details and transaction info
        
        Raises:
            ValueError: If invalid tier or billing period
            Exception: If insufficient credits or purchase fails
        """
        from database.premium_schema import PREMIUM_TIERS
        
        # Validate tier
        if tier not in PREMIUM_TIERS:
            raise ValueError(f"Invalid tier: {tier}")
        
        # Credits pricing
        CREDITS_PRICING = {
            "monthly": 500,  # 500 ❄️ per month
            "yearly": 5000   # 5000 ❄️ per year (save 1000)
        }
        
        if billing_period not in CREDITS_PRICING:
            raise ValueError(f"Invalid billing period: {billing_period}. Must be 'monthly' or 'yearly'")
        
        credits_cost = CREDITS_PRICING[billing_period]
        
        # Check user's balance
        balance = await self.credits_system.get_balance(user_id)
        if balance < credits_cost:
            raise Exception(
                f"Insufficient credits! You need {credits_cost} ❄️ but have {balance} ❄️. "
                f"Use `/credits packages` to purchase more credits."
            )
        
        # Spend credits
        success = await self.credits_system.spend_credits(
            user_id=user_id,
            amount=credits_cost,
            reason=f"Premium subscription - {billing_period}",
            metadata={
                "guild_id": guild_id,
                "tier": tier,
                "billing_period": billing_period,
                "purchase_type": "premium_subscription"
            }
        )
        
        if not success:
            raise Exception("Failed to process credits payment. Please try again.")
        
        # Create subscription
        duration_days = 30 if billing_period == "monthly" else 365
        subscription = await self.create_subscription(
            user_id=user_id,
            guild_id=guild_id,
            tier=tier,
            duration_days=duration_days,
            payment_method="credits",
            user_email=user_email,
            user_name=user_name,
            guild_name=guild_name
        )
        
        # Record payment in premium system
        await self.schema.record_payment(
            user_id=user_id,
            guild_id=guild_id,
            amount=credits_cost,
            currency="K77_CREDITS",
            tier=tier,
            stripe_payment_id=f"credits_{user_id}_{datetime.utcnow().timestamp()}",
            status="completed",
            metadata={
                "payment_method": "credits",
                "billing_period": billing_period
            }
        )
        
        logger.info(
            f"✅ Premium subscription purchased with credits: "
            f"user={user_id}, guild={guild_id}, cost={credits_cost} ❄️, period={billing_period}"
        )
        
        return {
            "success": True,
            "subscription": subscription,
            "credits_spent": credits_cost,
            "new_balance": await self.credits_system.get_balance(user_id),
            "billing_period": billing_period,
            "duration_days": duration_days
        }
    
    async def get_credits_pricing(self) -> Dict[str, int]:
        """Get premium subscription pricing in credits"""
        return {
            "monthly": 500,   # 500 ❄️
            "yearly": 5000    # 5000 ❄️ (save 1000 vs monthly * 12)
        }


# Feature Decorators

def require_premium(feature_id: str):
    """Decorator to require premium feature"""
    def decorator(func):
        async def wrapper(self, ctx, *args, **kwargs):
            guild_id = str(ctx.guild.id)
            premium_system = self.bot.premium_system
            
            if not await premium_system.has_feature(guild_id, feature_id):
                await ctx.respond(
                    "❌ This feature requires a premium subscription!\n"
                    f"Use `/premium` to learn more.",
                    ephemeral=True
                )
                return
            
            # Track usage
            await premium_system.track_usage(
                guild_id=guild_id,
                feature_id=feature_id,
                user_id=str(ctx.author.id)
            )
            
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator


def check_limit(limit_name: str):
    """Decorator to check usage limits"""
    def decorator(func):
        async def wrapper(self, ctx, *args, **kwargs):
            guild_id = str(ctx.guild.id)
            premium_system = self.bot.premium_system
            
            # Get current usage (would need to be implemented per feature)
            current_usage = 0  # TODO: Implement usage counting
            
            if not await premium_system.check_limit(guild_id, limit_name, current_usage):
                limit = await premium_system.get_limit(guild_id, limit_name)
                await ctx.respond(
                    f"❌ You've reached your limit of {limit} for this feature!\n"
                    f"Upgrade to premium for more. Use `/premium` to learn more.",
                    ephemeral=True
                )
                return
            
            return await func(self, ctx, *args, **kwargs)
        return wrapper
    return decorator

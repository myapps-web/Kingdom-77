"""
Premium API Endpoints
Manage premium subscriptions, features, and billing
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.response import APIResponse
from ..utils.auth import get_current_user
from ..utils.database import get_database
import os
import stripe

router = APIRouter()

# Initialize Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Pydantic Models
class SubscriptionInfo(BaseModel):
    """Subscription information"""
    guild_id: str
    tier: str
    status: str
    start_date: datetime
    end_date: Optional[datetime]
    auto_renew: bool
    trial_used: bool
    features: List[str]

class CreateSubscriptionRequest(BaseModel):
    """Create subscription request"""
    tier: str = "premium"
    billing_cycle: str = "monthly"  # monthly or yearly

class FeatureInfo(BaseModel):
    """Feature information"""
    name: str
    enabled: bool
    description: str
    premium_only: bool

class BillingHistory(BaseModel):
    """Billing history entry"""
    invoice_id: str
    amount: float
    currency: str
    status: str
    date: datetime
    description: str
    invoice_url: Optional[str]

@router.get("/{guild_id}")
async def get_subscription(
    guild_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get guild's premium subscription status
    
    Returns subscription information including:
    - Current tier (basic/premium)
    - Subscription status (active/expired/trial)
    - Features enabled
    - Renewal date
    """
    try:
        db = await get_database()
        
        # Get subscription from database
        subscription = await db.premium_subscriptions.find_one({"guild_id": guild_id})
        
        if not subscription:
            # No subscription = Basic tier
            return APIResponse(
                success=True,
                data={
                    "guild_id": guild_id,
                    "tier": "basic",
                    "status": "active",
                    "features": [
                        "unlimited_level_roles",
                        "unlimited_tickets",
                        "advanced_dashboard",
                        "priority_support"
                    ],
                    "trial_used": False,
                    "auto_renew": False
                }
            )
        
        # Check if subscription is active
        now = datetime.utcnow()
        is_active = (
            subscription.get("status") == "active" and
            subscription.get("end_date") and
            subscription["end_date"] > now
        )
        
        return APIResponse(
            success=True,
            data={
                "guild_id": guild_id,
                "tier": subscription.get("tier", "basic"),
                "status": "active" if is_active else "expired",
                "start_date": subscription.get("start_date"),
                "end_date": subscription.get("end_date"),
                "auto_renew": subscription.get("auto_renew", False),
                "trial_used": subscription.get("trial_used", False),
                "stripe_subscription_id": subscription.get("stripe_subscription_id"),
                "features": subscription.get("features", [])
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching subscription: {str(e)}"
        )

@router.post("/{guild_id}/subscribe")
async def create_subscription(
    guild_id: str,
    request: CreateSubscriptionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Create Stripe checkout session for premium subscription
    
    Creates a Stripe checkout session and returns the URL
    User will be redirected to Stripe to complete payment
    """
    try:
        # Verify user has admin permissions for this guild
        # (Add permission check here)
        
        # Define prices based on billing cycle
        prices = {
            "monthly": os.getenv("STRIPE_PRICE_MONTHLY", "price_monthly_id"),
            "yearly": os.getenv("STRIPE_PRICE_YEARLY", "price_yearly_id")
        }
        
        price_id = prices.get(request.billing_cycle)
        if not price_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid billing cycle"
            )
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=os.getenv("DASHBOARD_URL") + f"/servers/{guild_id}/premium?success=true",
            cancel_url=os.getenv("DASHBOARD_URL") + f"/servers/{guild_id}/premium?canceled=true",
            metadata={
                'guild_id': guild_id,
                'user_id': current_user.get('id'),
                'tier': 'premium'
            },
            client_reference_id=guild_id
        )
        
        return APIResponse(
            success=True,
            data={
                "checkout_url": checkout_session.url,
                "session_id": checkout_session.id
            }
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating subscription: {str(e)}"
        )

@router.post("/{guild_id}/subscribe-with-credits")
async def subscribe_with_credits(
    guild_id: str,
    request: CreateSubscriptionRequest,
    current_user: Dict = Depends(get_current_user)
):
    """
    Purchase premium subscription using K77 Credits
    
    Pricing:
    - Monthly: 500 ❄️ credits
    - Yearly: 5000 ❄️ credits (save 1000)
    """
    try:
        from premium.premium_system import PremiumSystem
        from ..utils.database import get_mongo_client
        
        # Verify user has admin permissions for this guild
        # (Add permission check here)
        
        user_id = current_user.get('id')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        # Initialize premium system
        mongo_client = await get_mongo_client()
        premium_system = PremiumSystem(mongo_client)
        await premium_system.initialize()
        
        # Purchase with credits
        result = await premium_system.purchase_with_credits(
            user_id=user_id,
            guild_id=guild_id,
            tier=request.tier,
            billing_period=request.billing_cycle,
            user_email=current_user.get('email'),
            user_name=current_user.get('username'),
            guild_name=None  # Could fetch from guild cache
        )
        
        return APIResponse(
            success=True,
            data={
                "message": "Premium subscription activated successfully!",
                "subscription": {
                    "guild_id": guild_id,
                    "tier": request.tier,
                    "status": "active",
                    "billing_period": request.billing_cycle,
                    "duration_days": result['duration_days'],
                    "expires_at": result['subscription']['expires_at'].isoformat()
                },
                "payment": {
                    "method": "credits",
                    "credits_spent": result['credits_spent'],
                    "new_balance": result['new_balance']
                }
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error purchasing with credits: {str(e)}"
        )

@router.get("/{guild_id}/credits-pricing")
async def get_credits_pricing(
    guild_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get premium subscription pricing in K77 Credits
    
    Returns:
    - monthly: Credits cost for monthly subscription
    - yearly: Credits cost for yearly subscription
    """
    try:
        from premium.premium_system import PremiumSystem
        from ..utils.database import get_mongo_client
        
        # Initialize premium system
        mongo_client = await get_mongo_client()
        premium_system = PremiumSystem(mongo_client)
        await premium_system.initialize()
        
        pricing = await premium_system.get_credits_pricing()
        
        return APIResponse(
            success=True,
            data={
                "pricing": pricing,
                "currency": "K77_CREDITS",
                "symbol": "❄️"
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching credits pricing: {str(e)}"
        )

@router.post("/{guild_id}/cancel")
async def cancel_subscription(
    guild_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Cancel premium subscription
    
    Cancels the Stripe subscription
    Subscription remains active until end of billing period
    """
    try:
        db = await get_database()
        
        # Get subscription
        subscription = await db.premium_subscriptions.find_one({"guild_id": guild_id})
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        stripe_subscription_id = subscription.get("stripe_subscription_id")
        if not stripe_subscription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No Stripe subscription ID found"
            )
        
        # Cancel Stripe subscription
        stripe_subscription = stripe.Subscription.modify(
            stripe_subscription_id,
            cancel_at_period_end=True
        )
        
        # Update database
        await db.premium_subscriptions.update_one(
            {"guild_id": guild_id},
            {
                "$set": {
                    "auto_renew": False,
                    "cancel_at_period_end": True,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return APIResponse(
            success=True,
            message="Subscription will be cancelled at the end of the billing period",
            data={
                "end_date": subscription.get("end_date"),
                "cancel_at_period_end": True
            }
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling subscription: {str(e)}"
        )

@router.get("/{guild_id}/billing")
async def get_billing_history(
    guild_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get billing history for guild
    
    Returns all payment history including:
    - Invoices
    - Payment status
    - Amounts
    - Dates
    """
    try:
        db = await get_database()
        
        # Get payment history from database
        payments = await db.payment_history.find(
            {"guild_id": guild_id}
        ).sort("date", -1).limit(50).to_list(50)
        
        billing_history = []
        for payment in payments:
            billing_history.append({
                "invoice_id": payment.get("stripe_invoice_id", "N/A"),
                "amount": payment.get("amount", 0),
                "currency": payment.get("currency", "usd"),
                "status": payment.get("status", "unknown"),
                "date": payment.get("date"),
                "description": payment.get("description", "Premium Subscription"),
                "invoice_url": payment.get("invoice_url")
            })
        
        return APIResponse(
            success=True,
            data={
                "guild_id": guild_id,
                "billing_history": billing_history,
                "total_payments": len(billing_history)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching billing history: {str(e)}"
        )

@router.get("/{guild_id}/features")
async def get_features(
    guild_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get all available features and their status for this guild
    
    Returns:
    - All features (basic + premium)
    - Whether each feature is enabled
    - Premium-only features
    """
    try:
        db = await get_database()
        
        # Get subscription
        subscription = await db.premium_subscriptions.find_one({"guild_id": guild_id})
        is_premium = subscription and subscription.get("status") == "active"
        
        # Define all features
        all_features = {
            "basic": [
                {
                    "name": "unlimited_level_roles",
                    "display_name": "Unlimited Level Roles",
                    "description": "Create unlimited role rewards for leveling",
                    "enabled": True,
                    "premium_only": False
                },
                {
                    "name": "unlimited_tickets",
                    "display_name": "Unlimited Tickets",
                    "description": "Create unlimited support tickets",
                    "enabled": True,
                    "premium_only": False
                },
                {
                    "name": "advanced_dashboard",
                    "display_name": "Advanced Dashboard",
                    "description": "Access to web dashboard",
                    "enabled": True,
                    "premium_only": False
                },
                {
                    "name": "priority_support",
                    "display_name": "Priority Support",
                    "description": "Get priority support from our team",
                    "enabled": True,
                    "premium_only": False
                }
            ],
            "premium": [
                {
                    "name": "xp_boost",
                    "display_name": "XP Boost (2x)",
                    "description": "Double XP for all members",
                    "enabled": is_premium,
                    "premium_only": True
                },
                {
                    "name": "custom_level_cards",
                    "display_name": "Custom Level Cards",
                    "description": "Customize level up cards with your branding",
                    "enabled": is_premium,
                    "premium_only": True
                },
                {
                    "name": "advanced_automod",
                    "display_name": "Advanced Auto-Mod (AI)",
                    "description": "AI-powered content moderation",
                    "enabled": is_premium,
                    "premium_only": True
                },
                {
                    "name": "custom_mod_actions",
                    "display_name": "Custom Mod Actions",
                    "description": "Create custom moderation actions",
                    "enabled": is_premium,
                    "premium_only": True
                },
                {
                    "name": "ticket_analytics",
                    "display_name": "Ticket Analytics",
                    "description": "Advanced analytics for tickets",
                    "enabled": is_premium,
                    "premium_only": True
                },
                {
                    "name": "custom_branding",
                    "display_name": "Custom Branding",
                    "description": "Add your server branding to bot messages",
                    "enabled": is_premium,
                    "premium_only": True
                },
                {
                    "name": "unlimited_commands",
                    "display_name": "Unlimited Custom Commands",
                    "description": "Create unlimited custom commands",
                    "enabled": is_premium,
                    "premium_only": True
                },
                {
                    "name": "unlimited_autoroles",
                    "display_name": "Unlimited Auto-Roles",
                    "description": "Create unlimited auto-role configurations",
                    "enabled": is_premium,
                    "premium_only": True
                },
                {
                    "name": "api_access",
                    "display_name": "API Access",
                    "description": "Access to Kingdom-77 API",
                    "enabled": is_premium,
                    "premium_only": True
                },
                {
                    "name": "dedicated_support",
                    "display_name": "Dedicated Support",
                    "description": "24/7 dedicated support channel",
                    "enabled": is_premium,
                    "premium_only": True
                }
            ]
        }
        
        return APIResponse(
            success=True,
            data={
                "guild_id": guild_id,
                "tier": "premium" if is_premium else "basic",
                "features": all_features
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching features: {str(e)}"
        )

@router.post("/{guild_id}/portal")
async def create_portal_session(
    guild_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Create Stripe Customer Portal session
    
    Allows user to manage:
    - Payment methods
    - Billing information
    - Invoices
    - Subscription
    """
    try:
        db = await get_database()
        
        # Get subscription
        subscription = await db.premium_subscriptions.find_one({"guild_id": guild_id})
        
        if not subscription or not subscription.get("stripe_customer_id"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active subscription found"
            )
        
        # Create portal session
        portal_session = stripe.billing_portal.Session.create(
            customer=subscription["stripe_customer_id"],
            return_url=os.getenv("DASHBOARD_URL") + f"/servers/{guild_id}/premium"
        )
        
        return APIResponse(
            success=True,
            data={
                "portal_url": portal_session.url
            }
        )
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating portal session: {str(e)}"
        )

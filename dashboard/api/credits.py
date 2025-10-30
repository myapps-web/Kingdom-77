"""
Kingdom-77 Bot v3.8 - Credits API Endpoints

FastAPI endpoints for credits system and shop management.

Endpoints:
- GET /api/credits/{user_id}/balance - Get user balance
- GET /api/credits/{user_id}/transactions - Get transaction history
- POST /api/credits/{user_id}/daily-claim - Claim daily credits
- GET /api/credits/packages - Get credit packages
- POST /api/credits/purchase - Purchase credits package
- POST /api/credits/{user_id}/transfer - Transfer credits to another user

Author: Kingdom-77 Team
Date: 2024
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import random

# Import database
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.credits_schema import (
    UserCredits,
    CreditTransaction,
    CreditPackage,
    DAILY_CLAIM_MIN,
    DAILY_CLAIM_MAX,
    DAILY_CLAIM_COOLDOWN_HOURS
)

router = APIRouter(prefix="/api/credits", tags=["Credits"])


# ============================================================
# PYDANTIC MODELS
# ============================================================

class UserBalanceResponse(BaseModel):
    user_id: int
    username: str
    balance: int
    total_earned: int
    total_spent: int
    total_purchased: int
    daily_claim_streak: int
    last_daily_claim: Optional[datetime]
    can_claim_daily: bool
    next_claim_time: Optional[datetime]


class TransactionResponse(BaseModel):
    user_id: int
    transaction_type: str
    amount: int
    description: str
    metadata: Dict[str, Any]
    created_at: datetime


class DailyClaimRequest(BaseModel):
    user_id: int
    username: str


class DailyClaimResponse(BaseModel):
    success: bool
    amount: int
    new_balance: int
    streak: int
    next_claim_time: datetime
    message: str


class CreditPackageResponse(BaseModel):
    package_id: str
    name: str
    name_ar: str
    base_credits: int
    bonus_credits: int
    total_credits: int
    price_usd: float
    price_sar: float
    popular: bool
    emoji: str
    badge: Optional[str] = None


class PurchaseCreditsRequest(BaseModel):
    user_id: int
    username: str
    package_id: str
    payment_method: str = "moyasar"  # moyasar, stripe


class PurchaseCreditsResponse(BaseModel):
    success: bool
    payment_url: Optional[str]
    transaction_id: Optional[str]
    message: str


class TransferCreditsRequest(BaseModel):
    from_user_id: int
    to_user_id: int
    to_username: str
    amount: int
    note: Optional[str] = None


class TransferCreditsResponse(BaseModel):
    success: bool
    from_balance: int
    to_balance: int
    message: str


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/{user_id}/balance", response_model=UserBalanceResponse)
async def get_user_balance(user_id: int, username: str = "Unknown"):
    """
    Get user's credit balance and stats.
    
    Returns:
    - balance: Current credit balance
    - total_earned: Total credits earned (daily claims, gifts)
    - total_spent: Total credits spent (shop, premium)
    - total_purchased: Total credits purchased with money
    - daily_claim_streak: Current daily claim streak
    - can_claim_daily: Whether user can claim daily credits now
    - next_claim_time: When user can claim next
    """
    try:
        user = await UserCredits.get_or_create_user(user_id, username)
        
        # Check if user can claim daily
        can_claim = True
        next_claim = None
        
        if user.get('last_daily_claim'):
            last_claim = user['last_daily_claim']
            hours_since_claim = (datetime.utcnow() - last_claim).total_seconds() / 3600
            
            if hours_since_claim < DAILY_CLAIM_COOLDOWN_HOURS:
                can_claim = False
                next_claim = last_claim + timedelta(hours=DAILY_CLAIM_COOLDOWN_HOURS)
        
        return UserBalanceResponse(
            user_id=user['user_id'],
            username=user['username'],
            balance=user['balance'],
            total_earned=user.get('total_earned', 0),
            total_spent=user.get('total_spent', 0),
            total_purchased=user.get('total_purchased', 0),
            daily_claim_streak=user.get('daily_claim_streak', 0),
            last_daily_claim=user.get('last_daily_claim'),
            can_claim_daily=can_claim,
            next_claim_time=next_claim
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user balance: {str(e)}"
        )


@router.get("/{user_id}/transactions", response_model=List[TransactionResponse])
async def get_user_transactions(
    user_id: int,
    limit: int = 50,
    transaction_type: Optional[str] = None
):
    """
    Get user's transaction history.
    
    Query Parameters:
    - limit: Maximum number of transactions (default 50)
    - transaction_type: Filter by type (daily_claim, purchase, spend, etc.)
    """
    try:
        transactions = await CreditTransaction.get_user_transactions(
            user_id=user_id,
            limit=limit,
            transaction_type=transaction_type
        )
        
        return [
            TransactionResponse(
                user_id=t['user_id'],
                transaction_type=t['transaction_type'],
                amount=t['amount'],
                description=t['description'],
                metadata=t.get('metadata', {}),
                created_at=t['created_at']
            )
            for t in transactions
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get transactions: {str(e)}"
        )


@router.post("/{user_id}/daily-claim", response_model=DailyClaimResponse)
async def claim_daily_credits(request: DailyClaimRequest):
    """
    Claim daily credits (5-10 credits).
    
    Rules:
    - Can claim once every 24 hours
    - Amount is random between 5-10 credits
    - Maintains streak if claimed within 48 hours
    """
    try:
        user = await UserCredits.get_or_create_user(request.user_id, request.username)
        
        # Check cooldown
        if user.get('last_daily_claim'):
            last_claim = user['last_daily_claim']
            hours_since_claim = (datetime.utcnow() - last_claim).total_seconds() / 3600
            
            if hours_since_claim < DAILY_CLAIM_COOLDOWN_HOURS:
                next_claim = last_claim + timedelta(hours=DAILY_CLAIM_COOLDOWN_HOURS)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "message": f"Daily claim on cooldown. Try again in {int(DAILY_CLAIM_COOLDOWN_HOURS - hours_since_claim)} hours.",
                        "next_claim_time": next_claim.isoformat()
                    }
                )
        
        # Generate random amount
        amount = random.randint(DAILY_CLAIM_MIN, DAILY_CLAIM_MAX)
        
        # Update user
        await UserCredits.update_daily_claim(request.user_id, amount)
        
        # Create transaction
        await CreditTransaction.create_transaction(
            user_id=request.user_id,
            transaction_type="daily_claim",
            amount=amount,
            description=f"Daily claim: {amount} ❄️",
            metadata={"streak": user.get('daily_claim_streak', 0) + 1}
        )
        
        # Get updated user
        updated_user = await UserCredits.get_user(request.user_id)
        next_claim = datetime.utcnow() + timedelta(hours=DAILY_CLAIM_COOLDOWN_HOURS)
        
        return DailyClaimResponse(
            success=True,
            amount=amount,
            new_balance=updated_user['balance'],
            streak=updated_user['daily_claim_streak'],
            next_claim_time=next_claim,
            message=f"You claimed {amount} ❄️ credits! Streak: {updated_user['daily_claim_streak']} days 🔥"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to claim daily credits: {str(e)}"
        )


@router.get("/packages", response_model=List[CreditPackageResponse])
async def get_credit_packages():
    """
    Get all available credit packages.
    
    Returns packages sorted by price (lowest to highest).
    """
    try:
        packages = await CreditPackage.get_all_packages()
        
        return [
            CreditPackageResponse(
                package_id=p['package_id'],
                name=p['name'],
                name_ar=p['name_ar'],
                base_credits=p['base_credits'],
                bonus_credits=p['bonus_credits'],
                total_credits=p['total_credits'],
                price_usd=p['price_usd'],
                price_sar=p['price_sar'],
                popular=p.get('popular', False),
                emoji=p.get('emoji', '❄️'),
                badge=p.get('badge')
            )
            for p in packages
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get credit packages: {str(e)}"
        )


@router.post("/purchase", response_model=PurchaseCreditsResponse)
async def purchase_credits(request: PurchaseCreditsRequest):
    """
    Purchase credits package.
    
    Creates a payment session and returns payment URL.
    User will be redirected to payment gateway (Moyasar/Stripe).
    After successful payment, credits will be added via webhook.
    """
    try:
        # Get package
        package = await CreditPackage.get_package(request.package_id)
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Package not found"
            )
        
        # Get or create user
        user = await UserCredits.get_or_create_user(request.user_id, request.username)
        
        # Create Moyasar payment session
        try:
            from payment.moyasar_integration import moyasar_payment
            
            # Convert USD to SAR (1 USD = 3.75 SAR approximate)
            price_sar = round(package['price_usd'] * 3.75, 2)
            
            # Success/Cancel URLs
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            success_url = f"{frontend_url}/shop?payment=success&package={request.package_id}"
            cancel_url = f"{frontend_url}/shop?payment=cancel"
            
            # Create payment
            payment_result = await moyasar_payment.create_credits_purchase(
                user_id=str(request.user_id),
                package_id=request.package_id,
                amount=price_sar,
                credits_amount=package['total_credits'],
                success_url=success_url,
                cancel_url=cancel_url
            )
            
            return PurchaseCreditsResponse(
                success=True,
                payment_url=payment_result['payment_url'],
                transaction_id=payment_result['payment_id'],
                message=f"Redirecting to Moyasar payment for {package['total_credits']} ❄️ credits (SAR {price_sar})..."
            )
        
        except Exception as e:
            # Fallback to test payment if Moyasar not configured
            payment_url = f"https://payment.test/checkout/{package['package_id']}"
            transaction_id = f"txn_{request.user_id}_{int(datetime.utcnow().timestamp())}"
            
            return PurchaseCreditsResponse(
                success=True,
                payment_url=payment_url,
                transaction_id=transaction_id,
                message=f"Test payment mode: {package['total_credits']} ❄️ credits. Error: {str(e)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment: {str(e)}"
        )


@router.post("/{user_id}/transfer", response_model=TransferCreditsResponse)
async def transfer_credits(request: TransferCreditsRequest):
    """
    Transfer credits to another user.
    
    Rules:
    - Minimum transfer: 10 credits
    - Cannot transfer to yourself
    - Must have sufficient balance
    """
    try:
        # Validation
        if request.amount < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum transfer amount is 10 credits"
            )
        
        if request.from_user_id == request.to_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot transfer credits to yourself"
            )
        
        # Get sender
        from_user = await UserCredits.get_user(request.from_user_id)
        if not from_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sender not found"
            )
        
        if from_user['balance'] < request.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient balance. You have {from_user['balance']} ❄️, need {request.amount} ❄️"
            )
        
        # Get or create receiver
        to_user = await UserCredits.get_or_create_user(request.to_user_id, request.to_username)
        
        # Perform transfer
        await UserCredits.update_balance(request.from_user_id, -request.amount)
        await UserCredits.update_balance(request.to_user_id, request.amount)
        
        # Create transactions
        note = request.note or "Credit transfer"
        
        await CreditTransaction.create_transaction(
            user_id=request.from_user_id,
            transaction_type="transfer_sent",
            amount=-request.amount,
            description=f"Sent {request.amount} ❄️ to {request.to_username}",
            metadata={"to_user_id": request.to_user_id, "note": note}
        )
        
        await CreditTransaction.create_transaction(
            user_id=request.to_user_id,
            transaction_type="transfer_received",
            amount=request.amount,
            description=f"Received {request.amount} ❄️ from user {request.from_user_id}",
            metadata={"from_user_id": request.from_user_id, "note": note}
        )
        
        # Get updated balances
        from_user = await UserCredits.get_user(request.from_user_id)
        to_user = await UserCredits.get_user(request.to_user_id)
        
        return TransferCreditsResponse(
            success=True,
            from_balance=from_user['balance'],
            to_balance=to_user['balance'],
            message=f"Successfully transferred {request.amount} ❄️ to {request.to_username}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to transfer credits: {str(e)}"
        )


@router.post("/webhook/moyasar")
async def moyasar_webhook(request: dict):
    """
    Handle Moyasar payment webhook.
    
    Called by Moyasar when payment is completed.
    Adds credits to user account automatically.
    """
    try:
        from payment.moyasar_integration import moyasar_payment
        from economy.credits_system import CreditsSystem
        from motor.motor_asyncio import AsyncIOMotorClient
        
        # Verify webhook signature (if configured)
        # signature = request.headers.get('X-Moyasar-Signature')
        # if not moyasar_payment.verify_webhook_signature(request.body, signature):
        #     raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Initialize credits system
        mongo_client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
        credits_system = CreditsSystem(mongo_client)
        
        # Process webhook
        result = await credits_system.handle_payment_webhook(
            payment_data=request,
            payment_provider="moyasar"
        )
        
        if result.get('success'):
            return {
                "success": True,
                "message": "Webhook processed successfully"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Webhook processing failed')
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing error: {str(e)}"
        )


# Export router
__all__ = ['router']

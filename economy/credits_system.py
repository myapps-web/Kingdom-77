"""
Kingdom-77 Bot v3.8 - Credits System

This module manages the K77 Credits economy system including:
- Daily claims with streak system
- Credit purchases with payment integration
- Credit transfers between users
- Transaction history
- Balance management

Author: Kingdom-77 Team
Date: 2024
"""

import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
import random
import asyncio

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
    DAILY_CLAIM_COOLDOWN_HOURS,
    PREMIUM_COSTS
)


class CreditsSystem:
    """
    Main system for managing K77 Credits.
    
    Features:
    - Daily claims with streak tracking
    - Credit purchases via payment gateway
    - Credit transfers between users
    - Transaction history
    - Balance queries
    """
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.daily_claim_cooldowns = {}  # Cache for cooldowns
        
        # Start background tasks
        self.cleanup_expired_cooldowns.start()
    
    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.cleanup_expired_cooldowns.cancel()
    
    # ============================================================
    # BALANCE MANAGEMENT
    # ============================================================
    
    async def get_balance(self, user_id: int, username: str = "Unknown") -> Dict[str, Any]:
        """
        Get user's credit balance and stats.
        
        Args:
            user_id: Discord user ID
            username: Discord username
            
        Returns:
            Dictionary with balance and stats
        """
        user = await UserCredits.get_or_create_user(user_id, username)
        
        # Check daily claim availability
        can_claim = await self.can_claim_daily(user_id)
        next_claim = await self.get_next_claim_time(user_id)
        
        return {
            'user_id': user['user_id'],
            'username': user['username'],
            'balance': user['balance'],
            'total_earned': user.get('total_earned', 0),
            'total_spent': user.get('total_spent', 0),
            'total_purchased': user.get('total_purchased', 0),
            'daily_claim_streak': user.get('daily_claim_streak', 0),
            'last_daily_claim': user.get('last_daily_claim'),
            'can_claim_daily': can_claim,
            'next_claim_time': next_claim
        }
    
    async def add_credits(
        self,
        user_id: int,
        amount: int,
        description: str,
        transaction_type: str = "admin_grant",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add credits to user's balance.
        
        Args:
            user_id: Discord user ID
            amount: Amount to add (positive number)
            description: Transaction description
            transaction_type: Type of transaction
            metadata: Additional transaction data
            
        Returns:
            True if successful
        """
        if amount <= 0:
            return False
        
        # Update balance
        success = await UserCredits.update_balance(user_id, amount)
        
        if success:
            # Create transaction
            await CreditTransaction.create_transaction(
                user_id=user_id,
                transaction_type=transaction_type,
                amount=amount,
                description=description,
                metadata=metadata or {}
            )
        
        return success
    
    async def spend_credits(
        self,
        user_id: int,
        amount: int,
        description: str,
        transaction_type: str = "spend",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Spend credits from user's balance.
        
        Args:
            user_id: Discord user ID
            amount: Amount to spend (positive number)
            description: Transaction description
            transaction_type: Type of transaction
            metadata: Additional transaction data
            
        Returns:
            True if successful, False if insufficient balance
        """
        if amount <= 0:
            return False
        
        # Check balance
        user = await UserCredits.get_user(user_id)
        if not user or user['balance'] < amount:
            return False
        
        # Update balance (negative amount)
        success = await UserCredits.update_balance(user_id, -amount)
        
        if success:
            # Create transaction
            await CreditTransaction.create_transaction(
                user_id=user_id,
                transaction_type=transaction_type,
                amount=-amount,
                description=description,
                metadata=metadata or {}
            )
        
        return success
    
    async def has_sufficient_balance(self, user_id: int, amount: int) -> bool:
        """
        Check if user has sufficient balance.
        
        Args:
            user_id: Discord user ID
            amount: Required amount
            
        Returns:
            True if user has enough credits
        """
        user = await UserCredits.get_user(user_id)
        return user is not None and user['balance'] >= amount
    
    # ============================================================
    # DAILY CLAIM SYSTEM
    # ============================================================
    
    async def can_claim_daily(self, user_id: int) -> bool:
        """
        Check if user can claim daily credits.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            True if user can claim
        """
        # Check cache first
        if user_id in self.daily_claim_cooldowns:
            cooldown_end = self.daily_claim_cooldowns[user_id]
            if datetime.utcnow() < cooldown_end:
                return False
        
        # Check database
        user = await UserCredits.get_user(user_id)
        if not user or not user.get('last_daily_claim'):
            return True
        
        last_claim = user['last_daily_claim']
        hours_since = (datetime.utcnow() - last_claim).total_seconds() / 3600
        
        return hours_since >= DAILY_CLAIM_COOLDOWN_HOURS
    
    async def get_next_claim_time(self, user_id: int) -> Optional[datetime]:
        """
        Get the next time user can claim daily credits.
        
        Args:
            user_id: Discord user ID
            
        Returns:
            Datetime of next claim or None if can claim now
        """
        user = await UserCredits.get_user(user_id)
        if not user or not user.get('last_daily_claim'):
            return None
        
        last_claim = user['last_daily_claim']
        next_claim = last_claim + timedelta(hours=DAILY_CLAIM_COOLDOWN_HOURS)
        
        if datetime.utcnow() >= next_claim:
            return None
        
        return next_claim
    
    async def claim_daily_credits(self, user_id: int, username: str) -> Dict[str, Any]:
        """
        Claim daily credits for user.
        
        Args:
            user_id: Discord user ID
            username: Discord username
            
        Returns:
            Dictionary with claim result
        """
        # Check if can claim
        if not await self.can_claim_daily(user_id):
            next_claim = await self.get_next_claim_time(user_id)
            return {
                'success': False,
                'error': 'on_cooldown',
                'next_claim_time': next_claim
            }
        
        # Generate random amount
        amount = random.randint(DAILY_CLAIM_MIN, DAILY_CLAIM_MAX)
        
        # Get or create user
        user = await UserCredits.get_or_create_user(user_id, username)
        
        # Update daily claim
        await UserCredits.update_daily_claim(user_id, amount)
        
        # Create transaction
        await CreditTransaction.create_transaction(
            user_id=user_id,
            transaction_type="daily_claim",
            amount=amount,
            description=f"Daily claim: {amount} ❄️",
            metadata={
                'streak': user.get('daily_claim_streak', 0) + 1
            }
        )
        
        # Update cooldown cache
        self.daily_claim_cooldowns[user_id] = datetime.utcnow() + timedelta(hours=DAILY_CLAIM_COOLDOWN_HOURS)
        
        # Get updated user
        updated_user = await UserCredits.get_user(user_id)
        
        return {
            'success': True,
            'amount': amount,
            'new_balance': updated_user['balance'],
            'streak': updated_user['daily_claim_streak'],
            'next_claim_time': datetime.utcnow() + timedelta(hours=DAILY_CLAIM_COOLDOWN_HOURS)
        }
    
    # ============================================================
    # TRANSFER SYSTEM
    # ============================================================
    
    async def transfer_credits(
        self,
        from_user_id: int,
        to_user_id: int,
        to_username: str,
        amount: int,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transfer credits from one user to another.
        
        Args:
            from_user_id: Sender's Discord user ID
            to_user_id: Receiver's Discord user ID
            to_username: Receiver's username
            amount: Amount to transfer
            note: Optional note
            
        Returns:
            Dictionary with transfer result
        """
        # Validation
        if amount < 10:
            return {
                'success': False,
                'error': 'minimum_amount',
                'message': 'Minimum transfer amount is 10 credits'
            }
        
        if from_user_id == to_user_id:
            return {
                'success': False,
                'error': 'same_user',
                'message': 'Cannot transfer credits to yourself'
            }
        
        # Check balance
        if not await self.has_sufficient_balance(from_user_id, amount):
            return {
                'success': False,
                'error': 'insufficient_balance',
                'message': 'Insufficient credits'
            }
        
        # Get or create receiver
        await UserCredits.get_or_create_user(to_user_id, to_username)
        
        # Perform transfer
        await UserCredits.update_balance(from_user_id, -amount)
        await UserCredits.update_balance(to_user_id, amount)
        
        # Create transactions
        note_text = note or "Credit transfer"
        
        await CreditTransaction.create_transaction(
            user_id=from_user_id,
            transaction_type="transfer_sent",
            amount=-amount,
            description=f"Sent {amount} ❄️ to user {to_user_id}",
            metadata={'to_user_id': to_user_id, 'note': note_text}
        )
        
        await CreditTransaction.create_transaction(
            user_id=to_user_id,
            transaction_type="transfer_received",
            amount=amount,
            description=f"Received {amount} ❄️ from user {from_user_id}",
            metadata={'from_user_id': from_user_id, 'note': note_text}
        )
        
        # Get updated balances
        from_user = await UserCredits.get_user(from_user_id)
        to_user = await UserCredits.get_user(to_user_id)
        
        return {
            'success': True,
            'amount': amount,
            'from_balance': from_user['balance'],
            'to_balance': to_user['balance']
        }
    
    # ============================================================
    # TRANSACTION HISTORY
    # ============================================================
    
    async def get_transaction_history(
        self,
        user_id: int,
        limit: int = 50,
        transaction_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's transaction history.
        
        Args:
            user_id: Discord user ID
            limit: Maximum number of transactions
            transaction_type: Filter by type
            
        Returns:
            List of transactions
        """
        return await CreditTransaction.get_user_transactions(
            user_id=user_id,
            limit=limit,
            transaction_type=transaction_type
        )
    
    # ============================================================
    # PURCHASE SYSTEM
    # ============================================================
    
    async def get_credit_packages(self) -> List[Dict[str, Any]]:
        """
        Get all available credit packages.
        
        Returns:
            List of credit packages
        """
        return await CreditPackage.get_all_packages()
    
    async def purchase_credits_with_payment(
        self,
        user_id: int,
        username: str,
        package_id: str,
        payment_method: str = "moyasar",
        success_url: str = "",
        cancel_url: str = ""
    ) -> Dict[str, Any]:
        """
        Create payment session for credit purchase.
        
        Args:
            user_id: Discord user ID
            username: Discord username
            package_id: Package ID to purchase
            payment_method: Payment method (moyasar/stripe)
            success_url: URL to redirect after successful payment
            cancel_url: URL to redirect on cancel
            
        Returns:
            Dictionary with payment URL and transaction ID
        """
        # Get package
        package = await CreditPackage.get_package(package_id)
        if not package:
            return {
                'success': False,
                'error': 'package_not_found',
                'message': 'Package not found'
            }
        
        # Moyasar Integration
        if payment_method == "moyasar":
            try:
                from payment.moyasar_integration import moyasar_payment
                
                # Convert USD to SAR (approximate rate: 1 USD = 3.75 SAR)
                usd_price = package['price_usd']
                sar_price = round(usd_price * 3.75, 2)
                
                # Create Moyasar payment
                payment_result = await moyasar_payment.create_credits_purchase(
                    user_id=str(user_id),
                    package_id=package_id,
                    amount=sar_price,
                    credits_amount=package['total_credits'],
                    success_url=success_url or "https://your-dashboard.com/shop/success",
                    cancel_url=cancel_url or "https://your-dashboard.com/shop"
                )
                
                return {
                    'success': True,
                    'payment_method': 'moyasar',
                    'payment_url': payment_result['payment_url'],
                    'payment_id': payment_result['payment_id'],
                    'amount_sar': sar_price,
                    'amount_usd': usd_price,
                    'package': package
                }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': 'payment_creation_failed',
                    'message': f'Failed to create Moyasar payment: {str(e)}'
                }
        
        # Fallback: Mock payment for testing
        else:
            payment_url = f"https://payment.test/checkout/{package_id}"
            transaction_id = f"txn_{user_id}_{int(datetime.utcnow().timestamp())}"
            
            return {
                'success': True,
                'payment_method': 'test',
                'payment_url': payment_url,
                'transaction_id': transaction_id,
                'package': package
            }
    
    async def complete_credit_purchase(
        self,
        user_id: int,
        username: str,
        package_id: str,
        transaction_id: str
    ) -> bool:
        """
        Complete credit purchase after successful payment.
        Called by payment webhook.
        
        Args:
            user_id: Discord user ID
            username: Discord username
            package_id: Package ID purchased
            transaction_id: Payment transaction ID
            
        Returns:
            True if successful
        """
        # Get package
        package = await CreditPackage.get_package(package_id)
        if not package:
            return False
        
        # Add credits to user
        total_credits = package['total_credits']
        
        await self.add_credits(
            user_id=user_id,
            amount=total_credits,
            description=f"Purchased {package['name']} ({total_credits} ❄️)",
            transaction_type="purchase",
            metadata={
                'package_id': package_id,
                'base_credits': package['base_credits'],
                'bonus_credits': package['bonus_credits'],
                'price_usd': package['price_usd'],
                'transaction_id': transaction_id
            }
        )
        
        return True
    
    async def handle_payment_webhook(
        self,
        payment_data: Dict[str, Any],
        payment_provider: str = "moyasar"
    ) -> Dict[str, Any]:
        """
        Handle payment webhook from Moyasar or other providers.
        
        Args:
            payment_data: Webhook payload from payment provider
            payment_provider: Payment provider name
            
        Returns:
            Dict with processing result
        """
        try:
            if payment_provider == "moyasar":
                from payment.moyasar_integration import moyasar_payment
                
                # Process webhook
                result = await moyasar_payment.handle_webhook(payment_data)
                
                if result.get('event') == 'payment_success':
                    # Extract metadata
                    metadata = result.get('metadata', {})
                    user_id = int(metadata.get('user_id', 0))
                    package_id = metadata.get('package_id')
                    payment_id = result.get('payment_id')
                    
                    if user_id and package_id:
                        # Complete purchase
                        success = await self.complete_credit_purchase(
                            user_id=user_id,
                            username="User",  # Username not available from webhook
                            package_id=package_id,
                            transaction_id=payment_id
                        )
                        
                        if success:
                            return {
                                'success': True,
                                'message': 'Credits added successfully',
                                'user_id': user_id,
                                'package_id': package_id
                            }
                        else:
                            return {
                                'success': False,
                                'error': 'Failed to add credits'
                            }
                    else:
                        return {
                            'success': False,
                            'error': 'Invalid metadata in payment'
                        }
                
                elif result.get('event') == 'payment_failed':
                    return {
                        'success': False,
                        'event': 'payment_failed',
                        'error': result.get('error', 'Payment failed')
                    }
                
                else:
                    return {
                        'success': False,
                        'error': f"Unknown event: {result.get('event')}"
                    }
            
            else:
                return {
                    'success': False,
                    'error': f'Unsupported payment provider: {payment_provider}'
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Webhook processing failed: {str(e)}'
            }
    
    # ============================================================
    # PREMIUM INTEGRATION
    # ============================================================
    
    async def purchase_premium_with_credits(
        self,
        user_id: int,
        guild_id: int,
        duration: str = "monthly"
    ) -> Dict[str, Any]:
        """
        Purchase premium subscription using credits.
        
        Args:
            user_id: Discord user ID
            guild_id: Discord guild ID
            duration: "monthly" or "yearly"
            
        Returns:
            Dictionary with purchase result
        """
        # Get cost
        cost = PREMIUM_COSTS.get(duration)
        if not cost:
            return {
                'success': False,
                'error': 'invalid_duration',
                'message': 'Invalid duration. Use "monthly" or "yearly"'
            }
        
        # Check balance
        if not await self.has_sufficient_balance(user_id, cost):
            user = await UserCredits.get_user(user_id)
            balance = user['balance'] if user else 0
            return {
                'success': False,
                'error': 'insufficient_balance',
                'message': f'Insufficient credits. You have {balance} ❄️, need {cost} ❄️'
            }
        
        # Spend credits
        success = await self.spend_credits(
            user_id=user_id,
            amount=cost,
            description=f"Premium {duration} subscription for guild {guild_id}",
            transaction_type="premium_purchase",
            metadata={
                'guild_id': guild_id,
                'duration': duration
            }
        )
        
        if success:
            return {
                'success': True,
                'cost': cost,
                'duration': duration,
                'guild_id': guild_id
            }
        
        return {
            'success': False,
            'error': 'purchase_failed',
            'message': 'Failed to complete purchase'
        }
    
    # ============================================================
    # BACKGROUND TASKS
    # ============================================================
    
    @tasks.loop(hours=1)
    async def cleanup_expired_cooldowns(self):
        """Clean up expired cooldown cache entries."""
        now = datetime.utcnow()
        expired = [
            user_id for user_id, cooldown_end in self.daily_claim_cooldowns.items()
            if now >= cooldown_end
        ]
        
        for user_id in expired:
            del self.daily_claim_cooldowns[user_id]
    
    @cleanup_expired_cooldowns.before_loop
    async def before_cleanup(self):
        """Wait for bot to be ready before starting task."""
        await self.bot.wait_until_ready()
    
    # ============================================================
    # EMBED HELPERS
    # ============================================================
    
    def create_balance_embed(self, balance_data: Dict[str, Any]) -> discord.Embed:
        """Create balance display embed."""
        embed = discord.Embed(
            title="❄️ Your K77 Credits Balance",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="💰 Current Balance",
            value=f"**{balance_data['balance']} ❄️**",
            inline=False
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=(
                f"**Total Earned:** {balance_data['total_earned']} ❄️\n"
                f"**Total Spent:** {balance_data['total_spent']} ❄️\n"
                f"**Total Purchased:** {balance_data['total_purchased']} ❄️"
            ),
            inline=False
        )
        
        if balance_data['daily_claim_streak'] > 0:
            embed.add_field(
                name="🔥 Daily Claim Streak",
                value=f"**{balance_data['daily_claim_streak']} days**",
                inline=True
            )
        
        if balance_data['can_claim_daily']:
            embed.add_field(
                name="🎁 Daily Claim",
                value="**Available Now!**",
                inline=True
            )
        elif balance_data['next_claim_time']:
            next_claim = balance_data['next_claim_time']
            timestamp = int(next_claim.timestamp())
            embed.add_field(
                name="⏳ Next Daily Claim",
                value=f"<t:{timestamp}:R>",
                inline=True
            )
        
        embed.set_footer(text="Use /credits daily to claim your daily credits!")
        
        return embed


# Export
__all__ = ['CreditsSystem']

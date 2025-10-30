"""
Moyasar Payment Gateway Integration
====================================
Payment provider for Saudi Arabia and GCC countries
Supports: Credit Cards, MADA, Apple Pay, STC Pay

API Documentation: https://moyasar.com/docs/api/
"""

import os
import hmac
import hashlib
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from base64 import b64encode

logger = logging.getLogger(__name__)


class MoyasarProvider:
    """Moyasar payment gateway integration for Saudi Arabia"""
    
    def __init__(self):
        """Initialize Moyasar provider"""
        self.api_key = os.getenv("MOYASAR_API_KEY")
        self.publishable_key = os.getenv("MOYASAR_PUBLISHABLE_KEY")
        self.webhook_secret = os.getenv("MOYASAR_WEBHOOK_SECRET")
        self.api_base = "https://api.moyasar.com/v1"
        self.currency = os.getenv("PAYMENT_CURRENCY", "SAR")
        
        if not self.api_key:
            logger.warning("MOYASAR_API_KEY not configured")
        
        # Create auth header (Basic Auth with API key)
        self.auth_header = self._create_auth_header()
    
    def _create_auth_header(self) -> Dict[str, str]:
        """Create Basic Auth header for Moyasar API"""
        if not self.api_key:
            return {}
        
        # Moyasar uses Basic Auth with API key as username and empty password
        credentials = f"{self.api_key}:"
        encoded = b64encode(credentials.encode()).decode()
        
        return {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json"
        }
    
    async def create_payment(
        self,
        amount: float,
        currency: str = None,
        description: str = "",
        callback_url: str = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a payment (one-time charge)
        
        Args:
            amount: Amount in currency (e.g., 49.99 for SAR 49.99)
            currency: Currency code (SAR, USD, etc.)
            description: Payment description
            callback_url: URL to redirect after payment
            metadata: Additional data to store with payment
            
        Returns:
            Payment object with checkout URL
        """
        if not self.api_key:
            logger.error("Moyasar API key not configured")
            return None
        
        # Convert amount to halalas (smallest unit - 1 SAR = 100 halalas)
        amount_halalas = int(amount * 100)
        
        payload = {
            "amount": amount_halalas,
            "currency": currency or self.currency,
            "description": description,
            "callback_url": callback_url,
            "metadata": metadata or {}
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/payments",
                json=payload,
                headers=self.auth_header,
                timeout=10
            )
            
            response.raise_for_status()
            payment = response.json()
            
            logger.info(f"Created Moyasar payment: {payment.get('id')}")
            return payment
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create Moyasar payment: {e}")
            return None
    
    async def create_invoice(
        self,
        amount: float,
        currency: str = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create an invoice (for recurring payments)
        
        Args:
            amount: Invoice amount
            currency: Currency code
            description: Invoice description
            metadata: Additional data
            
        Returns:
            Invoice object with payment URL
        """
        if not self.api_key:
            logger.error("Moyasar API key not configured")
            return None
        
        amount_halalas = int(amount * 100)
        
        payload = {
            "amount": amount_halalas,
            "currency": currency or self.currency,
            "description": description,
            "metadata": metadata or {}
        }
        
        try:
            response = requests.post(
                f"{self.api_base}/invoices",
                json=payload,
                headers=self.auth_header,
                timeout=10
            )
            
            response.raise_for_status()
            invoice = response.json()
            
            logger.info(f"Created Moyasar invoice: {invoice.get('id')}")
            return invoice
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create Moyasar invoice: {e}")
            return None
    
    async def create_checkout_session(
        self,
        user_id: str,
        guild_id: str,
        tier: str,
        amount: float,
        billing_period: str = "monthly",
        success_url: str = None,
        cancel_url: str = None
    ) -> Optional[str]:
        """
        Create checkout session for subscription
        
        Args:
            user_id: Discord user ID
            guild_id: Discord guild ID
            tier: Subscription tier
            amount: Subscription amount
            billing_period: monthly or yearly
            success_url: Redirect URL on success
            cancel_url: Redirect URL on cancel
            
        Returns:
            Checkout URL or None
        """
        description = f"Kingdom-77 {tier.title()} - {billing_period.title()} Subscription"
        
        metadata = {
            "user_id": user_id,
            "guild_id": guild_id,
            "tier": tier,
            "billing_period": billing_period,
            "type": "subscription"
        }
        
        # For subscriptions, use invoices (recurring)
        invoice = await self.create_invoice(
            amount=amount,
            description=description,
            metadata=metadata
        )
        
        if not invoice:
            return None
        
        # Moyasar invoice URL format
        invoice_id = invoice.get("id")
        checkout_url = f"https://moyasar.com/i/{invoice_id}"
        
        return checkout_url
    
    async def get_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get payment details
        
        Args:
            payment_id: Moyasar payment ID
            
        Returns:
            Payment object or None
        """
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.api_base}/payments/{payment_id}",
                headers=self.auth_header,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Moyasar payment {payment_id}: {e}")
            return None
    
    async def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get invoice details
        
        Args:
            invoice_id: Moyasar invoice ID
            
        Returns:
            Invoice object or None
        """
        if not self.api_key:
            return None
        
        try:
            response = requests.get(
                f"{self.api_base}/invoices/{invoice_id}",
                headers=self.auth_header,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get Moyasar invoice {invoice_id}: {e}")
            return None
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Refund a payment
        
        Args:
            payment_id: Payment ID to refund
            amount: Partial refund amount (None = full refund)
            
        Returns:
            Refund object or None
        """
        if not self.api_key:
            return None
        
        payload = {}
        if amount is not None:
            payload["amount"] = int(amount * 100)
        
        try:
            response = requests.post(
                f"{self.api_base}/payments/{payment_id}/refund",
                json=payload,
                headers=self.auth_header,
                timeout=10
            )
            
            response.raise_for_status()
            refund = response.json()
            
            logger.info(f"Refunded Moyasar payment {payment_id}")
            return refund
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to refund Moyasar payment {payment_id}: {e}")
            return None
    
    def verify_webhook_signature(
        self,
        payload: str,
        signature: str
    ) -> bool:
        """
        Verify Moyasar webhook signature
        
        Args:
            payload: Raw webhook payload (as string)
            signature: Signature from X-Moyasar-Signature header
            
        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning("Moyasar webhook secret not configured")
            return False
        
        # Compute expected signature
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures (constant-time comparison)
        return hmac.compare_digest(expected, signature)
    
    async def handle_webhook(
        self,
        event: Dict[str, Any],
        premium_system = None
    ) -> bool:
        """
        Handle Moyasar webhook event
        
        Args:
            event: Webhook event data
            premium_system: PremiumSystem instance for creating subscriptions
            
        Returns:
            True if handled successfully
        """
        event_type = event.get("type")
        data = event.get("data", {})
        
        logger.info(f"Handling Moyasar webhook: {event_type}")
        
        # Payment succeeded
        if event_type == "payment_paid":
            return await self._handle_payment_success(data, premium_system)
        
        # Payment failed
        elif event_type == "payment_failed":
            return await self._handle_payment_failed(data, premium_system)
        
        # Invoice paid
        elif event_type == "invoice_paid":
            return await self._handle_invoice_paid(data, premium_system)
        
        # Refund processed
        elif event_type == "refund_created":
            return await self._handle_refund(data, premium_system)
        
        else:
            logger.warning(f"Unhandled Moyasar webhook type: {event_type}")
            return False
    
    async def _handle_payment_success(
        self,
        payment: Dict[str, Any],
        premium_system
    ) -> bool:
        """Handle successful payment"""
        metadata = payment.get("metadata", {})
        user_id = metadata.get("user_id")
        guild_id = metadata.get("guild_id")
        tier = metadata.get("tier")
        billing_period = metadata.get("billing_period", "monthly")
        
        if not (user_id and guild_id and tier):
            logger.error("Missing metadata in Moyasar payment")
            return False
        
        # Calculate subscription duration
        duration_days = 30 if billing_period == "monthly" else 365
        
        # Create subscription
        if premium_system:
            try:
                await premium_system.create_subscription(
                    user_id=user_id,
                    guild_id=guild_id,
                    tier=tier,
                    duration_days=duration_days,
                    payment_method="moyasar"
                )
                
                # Record payment
                amount = payment.get("amount", 0) / 100  # Convert from halalas
                await premium_system.schema.record_payment(
                    user_id=user_id,
                    guild_id=guild_id,
                    amount=amount,
                    currency=payment.get("currency", "SAR"),
                    tier=tier,
                    stripe_payment_id=payment.get("id", ""),  # Reuse field for Moyasar ID
                    status="completed"
                )
                
                logger.info(f"Created subscription for guild {guild_id} via Moyasar")
                return True
                
            except Exception as e:
                logger.error(f"Failed to create subscription from Moyasar payment: {e}")
                return False
        
        return False
    
    async def _handle_payment_failed(
        self,
        payment: Dict[str, Any],
        premium_system
    ) -> bool:
        """Handle failed payment"""
        metadata = payment.get("metadata", {})
        user_id = metadata.get("user_id")
        guild_id = metadata.get("guild_id")
        
        logger.warning(f"Payment failed for guild {guild_id}: {payment.get('message')}")
        
        # TODO: Send payment failed email notification
        # TODO: Retry payment after X days
        
        return True
    
    async def _handle_invoice_paid(
        self,
        invoice: Dict[str, Any],
        premium_system
    ) -> bool:
        """Handle paid invoice (recurring subscription)"""
        # Similar to payment success, but for invoices
        return await self._handle_payment_success(invoice, premium_system)
    
    async def _handle_refund(
        self,
        refund: Dict[str, Any],
        premium_system
    ) -> bool:
        """Handle refund processed"""
        payment_id = refund.get("payment_id")
        amount = refund.get("amount", 0) / 100
        
        logger.info(f"Refund processed for payment {payment_id}: {amount}")
        
        # TODO: Update subscription status
        # TODO: Send refund confirmation email
        
        return True
    
    def get_invoice_url(self, payment_id: str) -> str:
        """
        Get invoice URL for payment
        
        Args:
            payment_id: Moyasar payment/invoice ID
            
        Returns:
            Invoice URL
        """
        # Moyasar doesn't have a direct invoice URL in dashboard
        # Return payment details URL
        return f"https://dashboard.moyasar.com/payments/{payment_id}"
    
    def get_supported_payment_methods(self) -> list:
        """Get supported payment methods"""
        return [
            "creditcard",      # Visa, Mastercard
            "mada",           # MADA (Saudi local cards)
            "applepay",       # Apple Pay
            "stcpay"          # STC Pay (Saudi telecom wallet)
        ]
    
    def get_provider_name(self) -> str:
        """Get provider display name"""
        return "Moyasar"
    
    def is_configured(self) -> bool:
        """Check if provider is properly configured"""
        return bool(self.api_key and self.publishable_key)


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_moyasar():
        """Test Moyasar integration"""
        provider = MoyasarProvider()
        
        if not provider.is_configured():
            print("❌ Moyasar not configured. Set MOYASAR_API_KEY in .env")
            return
        
        print(f"✅ Moyasar configured")
        print(f"📍 Currency: {provider.currency}")
        print(f"💳 Payment methods: {', '.join(provider.get_supported_payment_methods())}")
        
        # Test creating a payment
        print("\n🔄 Creating test payment...")
        payment = await provider.create_payment(
            amount=49.99,
            description="Test Payment - Kingdom-77",
            metadata={"test": True}
        )
        
        if payment:
            print(f"✅ Payment created: {payment.get('id')}")
            print(f"🔗 Checkout URL: https://moyasar.com/p/{payment.get('id')}")
        else:
            print("❌ Failed to create payment")
    
    asyncio.run(test_moyasar())

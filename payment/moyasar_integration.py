"""
Moyasar Payment Integration
Saudi Arabia payment gateway integration for K77 Credits packages

Official Documentation: https://moyasar.com/docs/api/
"""

import os
import logging
import aiohttp
import json
from typing import Optional, Dict, Any
from datetime import datetime
import base64

logger = logging.getLogger(__name__)


class MoyasarPayment:
    """
    Moyasar Payment Gateway Integration
    
    Supports:
    - Credit Card (مدى، فيزا، ماستركارد)
    - Apple Pay
    - STC Pay
    
    Payment Flow:
    1. Create payment request
    2. Redirect user to payment page
    3. Handle webhook callback
    4. Verify payment status
    """
    
    def __init__(self):
        self.api_key = os.getenv("MOYASAR_API_KEY")
        self.publishable_key = os.getenv("MOYASAR_PUBLISHABLE_KEY")
        self.base_url = "https://api.moyasar.com/v1"
        self.webhook_secret = os.getenv("MOYASAR_WEBHOOK_SECRET")
        
        if not self.api_key:
            logger.warning("⚠️ MOYASAR_API_KEY not configured")
    
    def is_configured(self) -> bool:
        """Check if Moyasar is properly configured"""
        return bool(self.api_key and self.publishable_key)
    
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header for Moyasar API"""
        credentials = f"{self.api_key}:"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    async def create_payment(
        self,
        amount: float,
        currency: str = "SAR",
        description: str = "",
        callback_url: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment request
        
        Args:
            amount: Amount in SAR (minimum 1.00)
            currency: Currency code (SAR only supported)
            description: Payment description
            callback_url: URL to redirect after payment
            metadata: Custom metadata (user_id, package_id, etc.)
        
        Returns:
            Dict with payment details including payment URL
        
        Raises:
            Exception: If payment creation fails
        """
        if not self.is_configured():
            raise Exception("Moyasar not configured. Set MOYASAR_API_KEY and MOYASAR_PUBLISHABLE_KEY in .env")
        
        # Convert to halalas (1 SAR = 100 halalas)
        amount_halalas = int(amount * 100)
        
        if amount_halalas < 100:  # Minimum 1 SAR
            raise ValueError("Amount must be at least 1.00 SAR")
        
        payload = {
            "amount": amount_halalas,
            "currency": currency,
            "description": description,
            "callback_url": callback_url,
            "metadata": metadata or {}
        }
        
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/payments",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 201:
                        data = await response.json()
                        logger.info(f"✅ Moyasar payment created: {data.get('id')}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Moyasar payment creation failed: {error_text}")
                        raise Exception(f"Payment creation failed: {error_text}")
        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Moyasar API connection error: {e}")
            raise Exception(f"Failed to connect to Moyasar API: {str(e)}")
    
    async def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Retrieve payment details
        
        Args:
            payment_id: Moyasar payment ID
        
        Returns:
            Dict with payment details
        """
        if not self.is_configured():
            raise Exception("Moyasar not configured")
        
        headers = {
            "Authorization": self._get_auth_header()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/payments/{payment_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Failed to fetch payment: {error_text}")
                        raise Exception(f"Failed to fetch payment: {error_text}")
        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Moyasar API connection error: {e}")
            raise Exception(f"Failed to connect to Moyasar API: {str(e)}")
    
    async def verify_payment(self, payment_id: str) -> bool:
        """
        Verify if payment was successful
        
        Args:
            payment_id: Moyasar payment ID
        
        Returns:
            True if payment succeeded, False otherwise
        """
        try:
            payment = await self.get_payment(payment_id)
            status = payment.get("status")
            
            logger.info(f"Payment {payment_id} status: {status}")
            return status == "paid"
        
        except Exception as e:
            logger.error(f"❌ Payment verification failed: {e}")
            return False
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Refund a payment (full or partial)
        
        Args:
            payment_id: Moyasar payment ID
            amount: Amount to refund (None = full refund)
            reason: Refund reason
        
        Returns:
            Dict with refund details
        """
        if not self.is_configured():
            raise Exception("Moyasar not configured")
        
        payload = {}
        
        if amount is not None:
            payload["amount"] = int(amount * 100)  # Convert to halalas
        
        if reason:
            payload["description"] = reason
        
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/payments/{payment_id}/refund",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status in [200, 201]:
                        data = await response.json()
                        logger.info(f"✅ Moyasar refund created: {data.get('id')}")
                        return data
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Moyasar refund failed: {error_text}")
                        raise Exception(f"Refund failed: {error_text}")
        
        except aiohttp.ClientError as e:
            logger.error(f"❌ Moyasar API connection error: {e}")
            raise Exception(f"Failed to connect to Moyasar API: {str(e)}")
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature (if configured)
        
        Args:
            payload: Raw webhook payload
            signature: Signature from webhook headers
        
        Returns:
            True if signature is valid
        """
        if not self.webhook_secret:
            logger.warning("⚠️ Webhook secret not configured, skipping verification")
            return True
        
        # TODO: Implement HMAC signature verification
        # Moyasar uses HMAC-SHA256 for webhook signatures
        import hmac
        import hashlib
        
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected, signature)
    
    async def handle_webhook(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle Moyasar webhook event
        
        Events:
        - payment.paid: Payment succeeded
        - payment.failed: Payment failed
        - payment.refunded: Payment refunded
        
        Args:
            event_data: Webhook event data
        
        Returns:
            Dict with processing result
        """
        event_type = event_data.get("type")
        payment_data = event_data.get("data", {})
        payment_id = payment_data.get("id")
        
        logger.info(f"📥 Moyasar webhook received: {event_type} for payment {payment_id}")
        
        if event_type == "payment.paid":
            # Payment successful
            amount = payment_data.get("amount", 0) / 100  # Convert from halalas
            metadata = payment_data.get("metadata", {})
            
            return {
                "success": True,
                "event": "payment_success",
                "payment_id": payment_id,
                "amount": amount,
                "currency": payment_data.get("currency", "SAR"),
                "metadata": metadata
            }
        
        elif event_type == "payment.failed":
            # Payment failed
            return {
                "success": False,
                "event": "payment_failed",
                "payment_id": payment_id,
                "error": payment_data.get("message", "Payment failed")
            }
        
        elif event_type == "payment.refunded":
            # Payment refunded
            return {
                "success": True,
                "event": "payment_refunded",
                "payment_id": payment_id,
                "refund_amount": payment_data.get("refunded_amount", 0) / 100
            }
        
        else:
            logger.warning(f"⚠️ Unknown Moyasar webhook event: {event_type}")
            return {
                "success": False,
                "event": "unknown",
                "error": f"Unknown event type: {event_type}"
            }
    
    def get_payment_url(self, payment_id: str) -> str:
        """
        Get payment URL for user to complete payment
        
        Args:
            payment_id: Moyasar payment ID
        
        Returns:
            Payment URL
        """
        # Moyasar redirect URL format
        return f"https://api.moyasar.com/v1/payments/{payment_id}/redirect"
    
    async def create_credits_purchase(
        self,
        user_id: str,
        package_id: str,
        amount: float,
        credits_amount: int,
        success_url: str,
        cancel_url: str
    ) -> Dict[str, Any]:
        """
        Create payment for K77 Credits package purchase
        
        Args:
            user_id: Discord user ID
            package_id: Credits package ID
            amount: Amount in SAR
            credits_amount: Credits to add on success
            success_url: URL to redirect after success
            cancel_url: URL to redirect on cancel
        
        Returns:
            Dict with payment details and redirect URL
        """
        description = f"K77 Credits - {credits_amount} ❄️"
        
        metadata = {
            "user_id": user_id,
            "package_id": package_id,
            "credits_amount": credits_amount,
            "purchase_type": "credits_package"
        }
        
        payment = await self.create_payment(
            amount=amount,
            currency="SAR",
            description=description,
            callback_url=success_url,
            metadata=metadata
        )
        
        return {
            "payment_id": payment.get("id"),
            "payment_url": self.get_payment_url(payment.get("id")),
            "amount": amount,
            "credits": credits_amount,
            "status": payment.get("status")
        }


# Global instance
moyasar_payment = MoyasarPayment()

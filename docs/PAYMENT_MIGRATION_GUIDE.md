# Payment Provider Migration Guide
**Kingdom-77 v3.8 - Stripe to Moyasar Migration**

---

## Overview

This guide documents the migration from **Stripe** to **Moyasar** for payment processing to support Saudi Arabian users. Stripe is not available in Saudi Arabia, so we're integrating Moyasar as the primary payment provider for the Kingdom-77 bot premium subscriptions.

---

## 🔍 Code Inspection Results

### Current Stripe Usage

**Files with Stripe References (20 matches):**

1. **`premium/premium_system.py`** - Main integration file
   - `import stripe` (line 6)
   - `stripe.api_key = os.getenv("STRIPE_SECRET_KEY")` (line 13)
   - `stripe.checkout.Session.create()` - checkout session creation
   - Stripe webhook handling in `handle_webhook()` method
   - Invoice URL construction using `dashboard.stripe.com`

2. **`requirements.txt`**
   - `stripe==7.3.0` (line 19)

3. **Documentation Files:**
   - `README.md` - Stripe setup instructions
   - `TODO.md` - Stripe environment variables
   - `docs/PROJECT_STATUS.md` - Stripe integration status
   - `docs/PHASE5.4_COMPLETE.md` - Stripe webhook documentation
   - `docs/PHASE5_COMPLETE.md` - Stripe premium features
   - `docs/ROADMAP.md` - Stripe integration milestones

### Issues Identified

1. ❌ **Hard-coded Stripe dependency** - No abstraction layer for payment providers
2. ❌ **Regional limitation** - Cannot process payments in Saudi Arabia
3. ❌ **Single provider** - No fallback or multi-provider support
4. ❌ **Stripe-specific webhooks** - Event types tied to Stripe API
5. ❌ **Invoice URLs** - Hard-coded Stripe dashboard URLs

---

## 🎯 Migration Strategy

### Approach: Provider Abstraction Layer

Instead of replacing Stripe entirely, we'll create an **abstraction layer** that supports both Stripe and Moyasar:

```
┌─────────────────────────────────────┐
│   PremiumSystem (Main API)          │
│   - create_subscription()           │
│   - handle_webhook()                │
│   - create_checkout_session()       │
└─────────────┬───────────────────────┘
              │
              ├─ payment_provider (config)
              │
    ┌─────────┴──────────┐
    │                    │
┌───▼────────┐    ┌──────▼──────┐
│ Stripe     │    │  Moyasar    │
│ Provider   │    │  Provider   │
└────────────┘    └─────────────┘
```

### Benefits

- ✅ **Gradual migration** - Run both providers simultaneously
- ✅ **Regional support** - Auto-detect region and select appropriate provider
- ✅ **Fallback** - If one provider fails, try another
- ✅ **Easy testing** - Switch providers via environment variable
- ✅ **Future-proof** - Easy to add more providers (Tap, PayTabs, etc.)

---

## 📦 Moyasar Integration

### About Moyasar

**Moyasar** is a leading payment gateway in Saudi Arabia and the Middle East.

- 🌍 **Website:** https://moyasar.com
- 📚 **API Docs:** https://moyasar.com/docs/api/
- 💳 **Supported:** Credit Cards, Apple Pay, MADA (Saudi local cards)
- 🔐 **Security:** PCI DSS compliant
- 💵 **Currencies:** SAR, USD, EUR, etc.
- 🎯 **Best for:** Saudi Arabia, UAE, Kuwait, Bahrain, other GCC countries

### Moyasar API Key Setup

1. Sign up at https://moyasar.com
2. Verify your business account
3. Go to **Dashboard** → **API Keys**
4. Copy **Publishable Key** and **Secret Key**
5. Add to `.env`:

```env
# Moyasar Configuration
MOYASAR_API_KEY=sk_test_xxxxxxxxxxxxxxxxx
MOYASAR_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxx
PAYMENT_PROVIDER=moyasar  # or "stripe"
PAYMENT_CURRENCY=SAR  # or USD
```

### Moyasar vs Stripe Comparison

| Feature | Stripe | Moyasar |
|---------|--------|---------|
| **Saudi Support** | ❌ No | ✅ Yes |
| **MADA Cards** | ❌ No | ✅ Yes |
| **API Quality** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Documentation** | Excellent | Good |
| **Webhooks** | ✅ Yes | ✅ Yes |
| **Recurring** | ✅ Native | ✅ With invoices |
| **Dashboard** | Advanced | Simple |
| **Fees** | 2.9% + $0.30 | 2.9% (varies) |

---

## 🔨 Implementation Plan

### Phase 1: Create Moyasar Module ✅

**File:** `premium/moyasar_system.py`

Features:
- Payment creation
- Checkout session URL generation
- Webhook signature verification
- Invoice management
- Refund handling

### Phase 2: Abstract Payment Interface ✅

**File:** `premium/payment_provider.py`

Create a base class:
```python
class PaymentProvider(ABC):
    @abstractmethod
    async def create_checkout_session(...)
    
    @abstractmethod
    async def handle_webhook(...)
    
    @abstractmethod
    async def get_invoice_url(...)
```

Implementations:
- `StripeProvider(PaymentProvider)`
- `MoyasarProvider(PaymentProvider)`

### Phase 3: Update PremiumSystem ✅

**File:** `premium/premium_system.py`

Changes:
- Remove hard-coded `import stripe`
- Add `self.payment_provider` (dynamic)
- Delegate payment operations to provider
- Support provider switching via config

### Phase 4: Update Dependencies ✅

**File:** `requirements.txt`

```diff
  # Payment Processing (v3.8)
  stripe==7.3.0             # Stripe payment integration
+ requests>=2.31.0          # HTTP client for Moyasar API
```

Note: Moyasar doesn't have an official Python SDK, we use REST API directly.

### Phase 5: Update Documentation ✅

Update all docs with:
- Moyasar setup instructions
- Environment variable changes
- Webhook endpoint configuration
- Regional payment provider selection
- Migration checklist

### Phase 6: Testing ⏳

Test scenarios:
- [ ] Create subscription with Moyasar
- [ ] Handle successful payment webhook
- [ ] Handle failed payment webhook
- [ ] Cancel subscription
- [ ] Renew subscription
- [ ] Test MADA cards (Saudi local)
- [ ] Test Apple Pay
- [ ] Test invoice URL generation
- [ ] Test refunds

---

## 🌍 Regional Auto-Detection

Add smart provider selection based on user location:

```python
def get_payment_provider(user_location: str = None) -> str:
    """Auto-detect payment provider based on region"""
    
    # Manual override
    if os.getenv("PAYMENT_PROVIDER"):
        return os.getenv("PAYMENT_PROVIDER")
    
    # Auto-detect based on location
    saudi_regions = ["SA", "SAU", "Saudi Arabia", "KSA"]
    
    if user_location in saudi_regions:
        return "moyasar"
    
    # Default to Stripe for international
    return "stripe"
```

---

## 🔐 Security Considerations

### Webhook Signature Verification

**Stripe:**
```python
stripe.Webhook.construct_event(
    payload, sig_header, webhook_secret
)
```

**Moyasar:**
```python
import hmac
import hashlib

def verify_moyasar_webhook(payload: str, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Environment Variables Security

Add to `.env.example`:
```env
# Payment Provider Configuration
PAYMENT_PROVIDER=moyasar  # stripe or moyasar
PAYMENT_CURRENCY=SAR      # SAR, USD, EUR, etc.

# Stripe (for international)
STRIPE_SECRET_KEY=sk_test_xxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxx

# Moyasar (for Saudi/GCC)
MOYASAR_API_KEY=sk_test_xxxx
MOYASAR_PUBLISHABLE_KEY=pk_test_xxxx
MOYASAR_WEBHOOK_SECRET=whsec_xxxx
```

**⚠️ Never commit `.env` to git!**

---

## 📊 Migration Checklist

### Pre-Migration

- [ ] Backup current Stripe subscriptions data
- [ ] Export customer payment methods
- [ ] Document all active subscriptions
- [ ] Notify users of payment provider change
- [ ] Test Moyasar API in sandbox mode

### During Migration

- [ ] Install Moyasar integration
- [ ] Configure environment variables
- [ ] Deploy webhook endpoints
- [ ] Update dashboard payment forms
- [ ] Test end-to-end payment flow
- [ ] Monitor error logs

### Post-Migration

- [ ] Verify all webhooks are working
- [ ] Check subscription renewals
- [ ] Monitor payment success rate
- [ ] Update user documentation
- [ ] Handle customer support inquiries
- [ ] Gradual rollout to users

---

## 🆘 Troubleshooting

### Common Issues

**1. "Moyasar API Key Invalid"**
- Check `.env` file has correct keys
- Verify you're using Secret Key (not Publishable)
- Ensure no extra spaces in key

**2. "Webhook signature verification failed"**
- Check `MOYASAR_WEBHOOK_SECRET` matches dashboard
- Ensure webhook payload is raw (not parsed)
- Verify HTTPS endpoint (required)

**3. "Payment declined"**
- Check card details are correct
- Verify sufficient funds
- Try different payment method
- Check Moyasar dashboard for details

**4. "Subscription not created after payment"**
- Check webhook is being received
- Verify webhook handler is running
- Check MongoDB connection
- Look at server logs for errors

---

## 🔗 Additional Resources

### Moyasar Resources
- 📚 API Documentation: https://moyasar.com/docs/api/
- 🎓 Integration Guide: https://moyasar.com/docs/integration/
- 💳 Payment Methods: https://moyasar.com/docs/payment-methods/
- 🔔 Webhooks: https://moyasar.com/docs/webhooks/
- 🛠️ Dashboard: https://dashboard.moyasar.com

### Alternative Providers (Future)
- **Tap Payments:** https://www.tap.company (UAE-based)
- **PayTabs:** https://www.paytabs.com (Saudi Arabia)
- **HyperPay:** https://www.hyperpay.com (Saudi Arabia)
- **Telr:** https://www.telr.com (UAE)

---

## 📞 Support

If you encounter issues during migration:

1. Check this guide first
2. Review Moyasar documentation
3. Check Kingdom-77 GitHub Issues
4. Contact Moyasar support: support@moyasar.com
5. Join Kingdom-77 Discord for community help

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-XX | Initial migration guide created |
| 1.1.0 | 2024-01-XX | Added Moyasar integration details |
| 1.2.0 | 2024-01-XX | Added regional auto-detection |

---

**Last Updated:** Phase 5.5 Implementation  
**Status:** 🚧 In Progress - Moyasar Integration  
**Next Steps:** Create `moyasar_system.py` module

# 🚀 Kingdom-77 Bot - Production Deployment Guide

**Version:** 4.0  
**Last Updated:** November 1, 2025  
**Estimated Time:** 10-15 days  
**Status:** 📋 Planning Phase

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Phase 6.1: Stripe Production](#phase-61-stripe-production)
4. [Phase 6.2: MongoDB Production](#phase-62-mongodb-production)
5. [Phase 6.3: Redis Production](#phase-63-redis-production)
6. [Phase 6.4: Domain & SSL](#phase-64-domain--ssl)
7. [Phase 6.5: Bot Hosting](#phase-65-bot-hosting)
8. [Phase 6.6: Dashboard Hosting](#phase-66-dashboard-hosting)
9. [Phase 6.7: Monitoring & Analytics](#phase-67-monitoring--analytics)
10. [Phase 6.8: Legal & Documentation](#phase-68-legal--documentation)
11. [Post-Deployment Checklist](#post-deployment-checklist)
12. [Rollback Plan](#rollback-plan)
13. [Cost Breakdown](#cost-breakdown)

---

<a id="overview"></a>
## 🎯 Overview

This guide will take Kingdom-77 Bot from development to production, making it available 24/7 for real users with:
- ✅ Real payment processing (Stripe)
- ✅ Production-grade database (MongoDB Atlas)
- ✅ Fast caching (Upstash Redis)
- ✅ Custom domain with HTTPS
- ✅ Reliable hosting for bot & dashboard
- ✅ Comprehensive monitoring
- ✅ Legal compliance (GDPR, ToS, Privacy Policy)

**Target Launch Date:** TBD  
**Expected Users:** 100-1000 servers in first month

---

<a id="prerequisites"></a>
## ✅ Prerequisites

### Required Accounts
- [ ] Stripe Account (verified, live mode enabled)
- [ ] MongoDB Atlas Account
- [ ] Upstash Account
- [ ] Domain Registrar (Namecheap, GoDaddy, Cloudflare)
- [ ] Hosting Platform Account (Render/Railway/Heroku)
- [ ] Vercel/Netlify Account (for frontend)
- [ ] Sentry.io Account (for error tracking)
- [ ] Google Analytics Account

### Required Tools
- [ ] Git installed
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] Discord Developer Portal access
- [ ] Command line familiarity

### Budget Estimate
- Domain: $10-15/year
- Hosting: $0-50/month (can start free)
- Monitoring: $0-25/month (free tier available)
- **Total:** ~$15-100/month

---

<a id="phase-61-stripe-production"></a>
## 💳 Phase 6.1: Stripe Production Setup

**Status:** 🔲 Not Started  
**Estimated Time:** 1 day  
**Priority:** 🔴 Critical

### Current State
- ✅ Stripe integration implemented in development
- ✅ Test mode with fake cards working
- ⏳ Need to activate live mode
- ⏳ Need production webhooks

### Step-by-Step Guide

#### 1. Activate Stripe Live Mode

**Prerequisites:**
- Business information submitted
- Bank account connected
- Identity verification completed

**Steps:**
1. Login to [Stripe Dashboard](https://dashboard.stripe.com)
2. Click on **"Activate your account"** in top banner
3. Complete business details:
   - Business type (Individual/Company)
   - Business name
   - Tax ID (if applicable)
   - Business address
4. Add bank account for payouts:
   - Routing number
   - Account number
   - Confirm micro-deposits (1-2 days)
5. Verify your identity:
   - Upload government ID
   - Provide additional documents if requested
6. Wait for approval (usually instant, max 24 hours)

**Expected Result:** ✅ "Payments activated" message

---

#### 2. Get Live API Keys

**Steps:**
1. Go to **Developers** → **API keys**
2. Switch from **"Test mode"** to **"Live mode"** toggle
3. Copy your keys:
   - **Publishable key:** `pk_live_...` (safe to expose)
   - **Secret key:** `sk_live_...` (⚠️ NEVER commit to git!)
   - **Webhook signing secret:** (we'll get this in step 4)

**Security Notes:**
- ⚠️ Never commit live keys to GitHub
- ⚠️ Store in environment variables only
- ⚠️ Use different keys for staging/production
- ⚠️ Rotate keys if compromised

---

#### 3. Configure Webhooks for Production

**Why Webhooks?**
Webhooks notify your backend when:
- Payment succeeds/fails
- Subscription created/updated/canceled
- Invoice paid/failed
- Refund processed

**Steps:**
1. Go to **Developers** → **Webhooks**
2. Click **"Add endpoint"**
3. Enter your production URL:
   ```
   https://api.yourdomain.com/api/stripe/webhook
   ```
4. Select events to listen for:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
   - `charge.refunded`
5. Click **"Add endpoint"**
6. Copy the **Webhook signing secret** (`whsec_...`)

**Test Webhook:**
```bash
stripe listen --forward-to localhost:8000/api/stripe/webhook
```

---

#### 4. Update Environment Variables

**File:** `.env`

**Replace test keys with live keys:**
```env
# Stripe Live Keys (Production)
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_SECRET_KEY=sk_live_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE

# Stripe Product IDs (Live Mode)
STRIPE_PRICE_PREMIUM_MONTHLY=price_YOUR_PRODUCT_ID_HERE
STRIPE_PRICE_PREMIUM_YEARLY=price_YOUR_PRODUCT_ID_HERE

# Environment
ENVIRONMENT=production
```

**⚠️ Security Checklist:**
- [ ] `.env` is in `.gitignore`
- [ ] Keys are not in any commit history
- [ ] Hosting platform has environment variables set
- [ ] No keys in frontend code

---

#### 5. Create Live Products & Prices

**Steps:**
1. Go to **Products** in Stripe Dashboard
2. Click **"Add product"**

**Product 1: Premium Monthly**
- Name: `Kingdom-77 Premium Monthly`
- Description: `Premium subscription for Kingdom-77 Discord Bot`
- Price: `$9.99`
- Billing period: `Monthly`
- Currency: `USD`
- Click **"Save product"**
- Copy the **Price ID** (starts with `price_`)

**Product 2: Premium Yearly**
- Name: `Kingdom-77 Premium Yearly`
- Description: `Premium subscription for Kingdom-77 Discord Bot (Save 17%)`
- Price: `$99.99`
- Billing period: `Yearly`
- Currency: `USD`
- Click **"Save product"**
- Copy the **Price ID**

**Update `.env` with new Price IDs:**
```env
STRIPE_PRICE_PREMIUM_MONTHLY=price_1234567890abcdef
STRIPE_PRICE_PREMIUM_YEARLY=price_0987654321fedcba
```

---

#### 6. Configure Refund Policy

**Recommended Policy:**
- **7-day full refund** - No questions asked
- **14-day partial refund (50%)** - With reason
- **After 14 days** - No refunds (exceptions case-by-case)

**Implementation:**
1. Go to **Settings** → **Refunds**
2. Enable **"Automatic refund emails"**
3. Set **"Refund reason required"** to Yes
4. Create refund template email

**Code Update** (if needed):
File: `dashboard/api/stripe_api.py`

```python
async def process_refund(subscription_id: str, reason: str = None):
    """Process refund based on subscription age"""
    subscription = await get_subscription(subscription_id)
    created_date = subscription['created']
    days_active = (datetime.now() - created_date).days
    
    if days_active <= 7:
        # Full refund
        amount = subscription['plan']['amount']
    elif days_active <= 14:
        # 50% refund
        amount = subscription['plan']['amount'] // 2
    else:
        # No refund
        return {"error": "Outside refund window"}
    
    refund = stripe.Refund.create(
        payment_intent=subscription['latest_invoice']['payment_intent'],
        amount=amount,
        reason=reason or "requested_by_customer"
    )
    
    return {"refund_id": refund.id, "amount": amount}
```

---

#### 7. Configure Tax Collection (Optional)

**For US-based business:**
1. Go to **Settings** → **Tax**
2. Enable **"Automatic tax collection"**
3. Add your tax registration numbers
4. Select regions where you collect tax

**For non-US:**
- Research VAT requirements in your country
- Stripe Tax handles EU VAT automatically
- Consult with accountant for compliance

---

#### 8. Test Payment Flow (Live Mode)

**⚠️ Warning:** These will be REAL charges!

**Test Checklist:**
- [ ] Premium monthly subscription
- [ ] Premium yearly subscription
- [ ] Successful payment flow
- [ ] Failed payment handling
- [ ] Subscription cancellation
- [ ] Refund process
- [ ] Webhook delivery
- [ ] Database updates after payment
- [ ] Discord role assignment after payment

**Test Cards (Live Mode):**
Don't use test cards in live mode! Use:
- A real card with low limit
- Stripe's live mode testing (charges $1, auto-refunds)

**Command to test:**
```bash
# Run this in your dashboard frontend
npm run dev

# Navigate to:
http://localhost:3000/servers/YOUR_SERVER_ID/premium

# Click "Subscribe Now" and use real payment method
```

**Verify:**
1. Check Stripe Dashboard → **Payments** for successful charge
2. Check your database for updated subscription
3. Check Discord for Premium role assignment
4. Check webhook endpoint received event

---

#### 9. Setup Payment Success/Failure Pages

**Create Success Page:**
File: `dashboard-frontend/app/payment/success/page.tsx`

```typescript
export default function PaymentSuccess() {
  return (
    <div className="container mx-auto py-20 text-center">
      <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-4" />
      <h1 className="text-4xl font-bold mb-4">Payment Successful!</h1>
      <p className="text-xl text-gray-600 mb-8">
        Thank you for subscribing to Kingdom-77 Premium!
      </p>
      <p className="mb-8">
        Your Premium features are now active on your Discord server.
      </p>
      <Link href="/dashboard" className="btn-primary">
        Go to Dashboard
      </Link>
    </div>
  );
}
```

**Create Failure Page:**
File: `dashboard-frontend/app/payment/cancel/page.tsx`

```typescript
export default function PaymentCancel() {
  return (
    <div className="container mx-auto py-20 text-center">
      <XCircle className="w-20 h-20 text-red-500 mx-auto mb-4" />
      <h1 className="text-4xl font-bold mb-4">Payment Canceled</h1>
      <p className="text-xl text-gray-600 mb-8">
        Your payment was not processed.
      </p>
      <Link href="/premium" className="btn-primary">
        Try Again
      </Link>
    </div>
  );
}
```

**Update Stripe Checkout URLs:**
```python
# In dashboard/api/stripe_api.py
checkout_session = stripe.checkout.Session.create(
    # ... other params
    success_url=f"{DASHBOARD_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
    cancel_url=f"{DASHBOARD_URL}/payment/cancel",
)
```

---

#### 10. Monitor Stripe Dashboard

**Key Metrics to Watch:**
- **Successful payments** - Should be 100% with valid cards
- **Failed payments** - Investigate if >5%
- **Disputed charges** - Follow Stripe's dispute process
- **Subscription churn** - Why are users canceling?
- **Revenue** - Track MRR (Monthly Recurring Revenue)

**Set up Email Alerts:**
1. Go to **Settings** → **Notifications**
2. Enable:
   - Failed payments
   - Disputed charges
   - Large refunds
   - Subscription cancellations

---

### ✅ Phase 6.1 Completion Checklist

- [ ] Stripe account activated for live mode
- [ ] Live API keys obtained and stored securely
- [ ] Webhooks configured for production domain
- [ ] Environment variables updated with live keys
- [ ] Live products & prices created
- [ ] Refund policy configured
- [ ] Tax collection setup (if applicable)
- [ ] Payment flow tested successfully
- [ ] Success/failure pages created
- [ ] Monitoring enabled in Stripe Dashboard

**Verification Test:**
```bash
# Test a real $0.50 charge
stripe charges create \
  --amount 50 \
  --currency usd \
  --source tok_visa \
  --description "Kingdom-77 Production Test"

# Should succeed and appear in dashboard
```

**Expected Result:** ✅ Real payments working, webhooks delivering, database updating

---

<a id="phase-62-mongodb-production"></a>
## 🗄️ Phase 6.2: MongoDB Production

**Status:** 🔲 Not Started  
**Estimated Time:** 1 day  
**Priority:** 🔴 Critical

### Current State
- ✅ Development cluster working
- ⏳ Need production cluster
- ⏳ Need automated backups
- ⏳ Need performance monitoring

### Step-by-Step Guide

#### 1. Create Production Cluster

**Steps:**
1. Login to [MongoDB Atlas](https://cloud.mongodb.com)
2. Click **"Build a Cluster"** or **"Create"**
3. Select **Cluster Tier:**
   - **Free (M0):** 512MB storage - Good for <1000 servers
   - **Shared (M2):** $9/month, 2GB - Good for 1000-5000 servers
   - **Dedicated (M10):** $57/month, 10GB - Good for 5000+ servers
   
   **Recommendation:** Start with **M2** ($9/month)

4. Select **Cloud Provider & Region:**
   - Provider: AWS (recommended for Render/Railway compatibility)
   - Region: Choose closest to your hosting (e.g., `us-east-1`)

5. **Cluster Name:** `kingdom77-production`

6. Click **"Create Cluster"** (takes 3-5 minutes)

---

#### 2. Configure Security

**Enable Authentication:**
1. Go to **Database Access** (left sidebar)
2. Click **"Add New Database User"**
3. Authentication Method: **"Password"**
4. Username: `kingdom77_prod`
5. Password: Generate strong password (copy it!)
   ```
   Example: aB3$xR9!mK2@pL7#
   ```
6. Database User Privileges: **"Atlas admin"** (full access)
7. Click **"Add User"**

**Configure IP Whitelist:**
1. Go to **Network Access** (left sidebar)
2. Click **"Add IP Address"**

**Option A: Allow All (Easier, less secure)**
```
IP Address: 0.0.0.0/0
Comment: Allow all (Production)
```

**Option B: Specific IPs (More secure)**
```
# Add your hosting platform IPs
# Render.com: Check their docs for IP ranges
# Railway.app: Dynamic IPs, use 0.0.0.0/0
# Heroku: Check their docs
```

3. Click **"Confirm"**

---

#### 3. Get Connection String

**Steps:**
1. Go to **Clusters** → **Connect**
2. Select **"Connect your application"**
3. Driver: **Python**, Version: **3.11 or later**
4. Copy the connection string:
   ```
   mongodb+srv://kingdom77_prod:<password>@kingdom77-production.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. Replace `<password>` with your actual password
6. Add database name at the end:
   ```
   mongodb+srv://kingdom77_prod:aB3$xR9!mK2@pL7#@kingdom77-production.xxxxx.mongodb.net/kingdom77_prod?retryWrites=true&w=majority
   ```

**Update Environment Variables:**
```env
# MongoDB Production
MONGODB_URI=mongodb+srv://kingdom77_prod:YOUR_PASSWORD@kingdom77-production.xxxxx.mongodb.net/kingdom77_prod?retryWrites=true&w=majority
MONGODB_DATABASE=kingdom77_prod
```

---

#### 4. Setup Automated Backups

**MongoDB Atlas Backups (Recommended):**

**For M2+ Clusters:**
1. Go to **Clusters** → **Backup** tab
2. Enable **"Cloud Backup"**
3. Configure schedule:
   - Snapshot frequency: **Every 12 hours**
   - Retention: **7 days** (adjust based on needs)
   - Point-in-time recovery: Enable (stores last 24 hours)
4. Click **"Save"**

**Cost:** Included in M2+ plans

**For M0 (Free) Clusters:**
- No automated backups available
- Use `mongodump` manually:
  ```bash
  mongodump --uri="mongodb+srv://..." --out=./backup-$(date +%Y%m%d)
  ```
- Schedule with cron job:
  ```bash
  # Run daily at 2 AM
  0 2 * * * mongodump --uri="$MONGODB_URI" --out=/backups/kingdom77-$(date +\%Y\%m\%d)
  ```

---

#### 5. Create Database Indexes

**Why?** Indexes dramatically improve query performance (10x-100x faster)

**Connect to Production:**
```bash
# Install MongoDB CLI tools
brew install mongodb-community@7.0  # macOS
# OR
sudo apt install mongodb-org-tools  # Linux

# Connect
mongosh "mongodb+srv://kingdom77_prod:PASSWORD@kingdom77-production.xxxxx.mongodb.net/kingdom77_prod"
```

**Create Indexes:**
```javascript
// Switch to database
use kingdom77_prod

// Core collections
db.guilds.createIndex({ "guild_id": 1 }, { unique: true })
db.users.createIndex({ "user_id": 1, "guild_id": 1 }, { unique: true })

// Premium System
db.premium_subscriptions.createIndex({ "guild_id": 1 })
db.premium_subscriptions.createIndex({ "stripe_subscription_id": 1 }, { unique: true })
db.premium_subscriptions.createIndex({ "status": 1, "current_period_end": 1 })

// Leveling System
db.user_levels.createIndex({ "guild_id": 1, "xp": -1 })  // Leaderboard
db.user_levels.createIndex({ "user_id": 1, "guild_id": 1 }, { unique: true })

// Moderation System
db.warnings.createIndex({ "guild_id": 1, "user_id": 1 })
db.mod_logs.createIndex({ "guild_id": 1, "created_at": -1 })

// Tickets System
db.tickets.createIndex({ "guild_id": 1, "status": 1 })
db.tickets.createIndex({ "ticket_id": 1 }, { unique: true })

// AutoMod System
db.automod_rules.createIndex({ "guild_id": 1, "enabled": 1 })
db.automod_logs.createIndex({ "guild_id": 1, "timestamp": -1 })

// Giveaways System
db.giveaways.createIndex({ "guild_id": 1, "status": 1 })
db.giveaways.createIndex({ "end_time": 1 })  // For auto-end task

// Applications System
db.applications.createIndex({ "guild_id": 1, "status": 1 })
db.applications.createIndex({ "form_id": 1, "user_id": 1 })

// Auto-Messages System
db.auto_messages.createIndex({ "guild_id": 1, "enabled": 1 })
db.auto_messages.createIndex({ "guild_id": 1, "trigger_type": 1 })

// Social Integration
db.social_links.createIndex({ "guild_id": 1, "enabled": 1 })
db.social_links.createIndex({ "guild_id": 1, "platform": 1 })

// Verify indexes
db.guilds.getIndexes()
```

**Expected Result:** Queries 10-100x faster ⚡

---

#### 6. Enable Performance Monitoring

**MongoDB Atlas Monitoring:**
1. Go to **Clusters** → **Metrics** tab
2. Enable **"Real-Time Performance Panel"**
3. Monitor:
   - **Operations per second** - Should be <1000 for small bot
   - **Query execution time** - Should be <50ms average
   - **Connections** - Should be <100
   - **Network traffic** - Watch for spikes

**Set up Alerts:**
1. Go to **Alerts** (left sidebar)
2. Click **"Add New Alert"**
3. Configure alerts:
   - **High CPU usage** - Alert if >80% for 5 minutes
   - **High connections** - Alert if >80 connections
   - **Slow queries** - Alert if >1000ms
   - **Disk space** - Alert if >80% full
4. Add email for notifications

---

#### 7. Migrate Data (if needed)

**From Development to Production:**

**Option A: Export/Import (Small datasets <100MB)**
```bash
# Export from development
mongodump --uri="mongodb+srv://DEV_URI" --out=./migration

# Import to production
mongorestore --uri="mongodb+srv://PROD_URI" ./migration

# Verify count
mongosh "PROD_URI" --eval "db.guilds.countDocuments({})"
```

**Option B: Copy Collections (Medium datasets 100MB-1GB)**
```javascript
// Connect to dev cluster in mongosh
const devDB = connect("mongodb+srv://DEV_URI/kingdom77_dev")
const prodDB = connect("mongodb+srv://PROD_URI/kingdom77_prod")

// Copy collection
devDB.guilds.find().forEach(doc => prodDB.guilds.insertOne(doc))

// Verify
print("Dev count:", devDB.guilds.countDocuments({}))
print("Prod count:", prodDB.guilds.countDocuments({}))
```

**Option C: Start Fresh (Recommended)**
- Production starts with empty database
- Data populates as users interact
- No migration needed!

---

#### 8. Test Database Connection

**Test Script:**
File: `scripts/test_production_db.py`

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    """Test production MongoDB connection"""
    uri = os.getenv("MONGODB_URI")
    
    print("🔌 Connecting to production MongoDB...")
    client = AsyncIOMotorClient(uri)
    
    try:
        # Ping the database
        await client.admin.command('ping')
        print("✅ Connection successful!")
        
        # Get database
        db = client[os.getenv("MONGODB_DATABASE", "kingdom77_prod")]
        
        # List collections
        collections = await db.list_collection_names()
        print(f"📂 Collections: {len(collections)}")
        for coll in collections:
            count = await db[coll].count_documents({})
            print(f"   - {coll}: {count} documents")
        
        # Test write/read
        test_doc = {"test": True, "timestamp": "2025-11-01"}
        result = await db.test_collection.insert_one(test_doc)
        print(f"✅ Write test: {result.inserted_id}")
        
        doc = await db.test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Read test: {doc}")
        
        # Cleanup
        await db.test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Cleanup successful")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()
        print("🔌 Connection closed")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

**Run Test:**
```bash
python scripts/test_production_db.py
```

**Expected Output:**
```
🔌 Connecting to production MongoDB...
✅ Connection successful!
📂 Collections: 0
✅ Write test: 673b2a1c9d8e7f6a5b4c3d2e
✅ Read test: {'_id': ObjectId('...'), 'test': True, 'timestamp': '2025-11-01'}
✅ Cleanup successful
🔌 Connection closed
```

---

### ✅ Phase 6.2 Completion Checklist

- [ ] Production cluster created (M2+ recommended)
- [ ] Database user created with strong password
- [ ] IP whitelist configured
- [ ] Connection string obtained and tested
- [ ] Environment variables updated
- [ ] Automated backups enabled (M2+)
- [ ] Database indexes created (25+ indexes)
- [ ] Performance monitoring enabled
- [ ] Alerts configured for critical metrics
- [ ] Data migration completed (if applicable)
- [ ] Connection test passed

**Expected Result:** ✅ Production MongoDB ready for real traffic

---

<a id="phase-63-redis-production"></a>
## ⚡ Phase 6.3: Redis Production

**Status:** 🔲 Not Started  
**Estimated Time:** 1 day  
**Priority:** 🔴 Critical

### Current State
- ✅ Redis integration implemented (Upstash)
- ✅ Caching system working in development
- ⏳ Need production database
- ⏳ Need persistence enabled
- ⏳ Need monitoring setup

### Step-by-Step Guide

#### 1. Create Production Redis Database

**Steps:**
1. Login to [Upstash Console](https://console.upstash.com)
2. Click **"Create Database"**
3. Configure database:
   - **Name:** `kingdom77-production`
   - **Type:** **Redis®** (not Kafka)
   - **Region:** Same as your hosting (e.g., `us-east-1`)
   - **Eviction Policy:** `allkeys-lru` (Least Recently Used)
   - **TLS:** ✅ **Enabled** (required for security)

4. Select Plan:
   - **Free Tier:** 10,000 commands/day, 256MB storage
   - **Pay as you go:** $0.20/100k commands (recommended)
   - **Pro:** $120/month unlimited

   **Recommendation:** Start with **Pay as you go** ($5-20/month for small bot)

5. Click **"Create"** (takes 30 seconds)

---

#### 2. Get Connection Details

**After creation, you'll see:**
```
Endpoint: redis-12345.upstash.io
Port: 6379 (or 6380 for TLS)
Password: AaBbCcDd1234567890XxYyZz
```

**Connection String Formats:**

**Format 1: Standard Redis URL**
```
redis://default:AaBbCcDd1234567890XxYyZz@redis-12345.upstash.io:6379
```

**Format 2: TLS (Recommended for production)**
```
rediss://default:AaBbCcDd1234567890XxYyZz@redis-12345.upstash.io:6380
```

**Format 3: Upstash REST API (Alternative)**
```
https://redis-12345.upstash.io
Token: AaBbCcDd1234567890XxYyZz
```

---

#### 3. Update Environment Variables

**File:** `.env`

```env
# Redis Production (Upstash)
REDIS_URL=rediss://default:AaBbCcDd1234567890XxYyZz@redis-12345.upstash.io:6380
REDIS_HOST=redis-12345.upstash.io
REDIS_PORT=6380
REDIS_PASSWORD=AaBbCcDd1234567890XxYyZz
REDIS_DB=0
REDIS_SSL=true

# Cache Configuration
CACHE_TTL=300  # 5 minutes default
CACHE_MAX_ENTRIES=10000
```

**⚠️ Security Notes:**
- Use `rediss://` (with double 's') for TLS encryption
- Never commit credentials to git
- Store in hosting platform's environment variables

---

#### 4. Enable Persistence

**Why Persistence?**
- Survives server restarts
- No data loss
- Faster recovery

**Upstash Persistence (Automatic):**
- ✅ Upstash has **automatic persistence** enabled by default
- ✅ Data is saved to disk every 60 seconds
- ✅ Snapshots created every 24 hours
- ✅ No configuration needed!

**Verify Persistence:**
```bash
# Connect to Redis CLI
redis-cli -h redis-12345.upstash.io -p 6380 --tls -a YOUR_PASSWORD

# Check config
CONFIG GET save
# Should return: "900 1 300 10 60 10000"

# Check AOF (Append Only File)
CONFIG GET appendonly
# Should return: "yes"
```

---

#### 5. Configure Cache Policies

**Update Cache Manager:**
File: `cache/redis.py`

```python
import os
from redis import asyncio as aioredis
from typing import Optional, Any
import json
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    """Production Redis Cache Manager"""
    
    def __init__(self):
        self.redis: Optional[aioredis.Redis] = None
        self.ttl_policies = {
            # Cache TTL by data type (seconds)
            'translation': 86400,      # 24 hours
            'guild_settings': 3600,    # 1 hour
            'user_data': 1800,         # 30 minutes
            'leaderboard': 300,        # 5 minutes
            'api_response': 300,       # 5 minutes
            'premium_status': 3600,    # 1 hour
            'rate_limit': 60,          # 1 minute
        }
    
    async def connect(self):
        """Connect to production Redis"""
        try:
            redis_url = os.getenv('REDIS_URL')
            
            if not redis_url:
                raise ValueError("REDIS_URL not found in environment")
            
            # Production configuration
            self.redis = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,        # Connection pool size
                socket_timeout=5,          # 5 second timeout
                socket_connect_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,  # Check connection every 30s
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("✅ Connected to production Redis")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def get(self, key: str, category: str = 'default') -> Optional[Any]:
        """Get value from cache with automatic JSON parsing"""
        try:
            value = await self.redis.get(f"{category}:{key}")
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        category: str = 'default',
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with automatic TTL"""
        try:
            # Get TTL from policy or use provided
            expiry = ttl or self.ttl_policies.get(category, 300)
            
            # Serialize to JSON
            serialized = json.dumps(value)
            
            # Set with expiry
            await self.redis.setex(
                f"{category}:{key}",
                expiry,
                serialized
            )
            return True
            
        except Exception as e:
            logger.error(f"Redis SET error: {e}")
            return False
    
    async def delete(self, key: str, category: str = 'default') -> bool:
        """Delete key from cache"""
        try:
            await self.redis.delete(f"{category}:{key}")
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error: {e}")
            return False
    
    async def clear_category(self, category: str) -> int:
        """Clear all keys in a category"""
        try:
            pattern = f"{category}:*"
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self.redis.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Redis CLEAR error: {e}")
            return 0
    
    async def get_stats(self) -> dict:
        """Get cache statistics"""
        try:
            info = await self.redis.info('stats')
            memory = await self.redis.info('memory')
            
            return {
                'total_commands': info.get('total_commands_processed', 0),
                'hits': info.get('keyspace_hits', 0),
                'misses': info.get('keyspace_misses', 0),
                'hit_rate': self._calculate_hit_rate(
                    info.get('keyspace_hits', 0),
                    info.get('keyspace_misses', 0)
                ),
                'memory_used': memory.get('used_memory_human', '0'),
                'connected_clients': info.get('connected_clients', 0),
            }
        except Exception as e:
            logger.error(f"Redis STATS error: {e}")
            return {}
    
    @staticmethod
    def _calculate_hit_rate(hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return 0.0
        return round((hits / total) * 100, 2)
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("🔌 Redis connection closed")

# Global instance
cache = RedisCache()
```

**Cache TTL Policies Explained:**
- **Translation:** 24 hours (rarely changes)
- **Guild Settings:** 1 hour (moderate changes)
- **User Data:** 30 minutes (frequent changes)
- **Leaderboard:** 5 minutes (real-time data)
- **API Response:** 5 minutes (balance freshness/performance)
- **Premium Status:** 1 hour (important but not real-time)
- **Rate Limit:** 1 minute (short-lived)

---

#### 6. Setup Rate Limiting

**Create Rate Limiter:**
File: `cache/rate_limiter.py`

```python
import asyncio
from datetime import datetime
from typing import Optional
from cache.redis import cache

class RateLimiter:
    """Token bucket rate limiter using Redis"""
    
    def __init__(self):
        self.limits = {
            # Requests per minute by tier
            'free': 60,
            'basic': 120,
            'premium': 300,
            'admin': 1000,
        }
    
    async def check_rate_limit(
        self, 
        user_id: str, 
        tier: str = 'free'
    ) -> tuple[bool, int, int]:
        """
        Check if user is within rate limit.
        
        Returns:
            (allowed, remaining, reset_after)
        """
        limit = self.limits.get(tier, 60)
        key = f"ratelimit:{user_id}"
        
        try:
            # Get current count
            current = await cache.redis.get(key)
            
            if current is None:
                # First request, set counter
                await cache.redis.setex(key, 60, 1)
                return True, limit - 1, 60
            
            current = int(current)
            
            if current >= limit:
                # Rate limit exceeded
                ttl = await cache.redis.ttl(key)
                return False, 0, ttl
            
            # Increment counter
            await cache.redis.incr(key)
            remaining = limit - current - 1
            ttl = await cache.redis.ttl(key)
            
            return True, remaining, ttl
            
        except Exception as e:
            # On error, allow request (fail open)
            return True, limit, 60
    
    async def reset_rate_limit(self, user_id: str) -> bool:
        """Reset rate limit for user (admin action)"""
        try:
            key = f"ratelimit:{user_id}"
            await cache.redis.delete(key)
            return True
        except:
            return False

# Global instance
rate_limiter = RateLimiter()
```

**Usage in API:**
```python
from cache.rate_limiter import rate_limiter

@router.get("/api/data")
async def get_data(user_id: str, tier: str = 'free'):
    # Check rate limit
    allowed, remaining, reset = await rate_limiter.check_rate_limit(user_id, tier)
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "retry_after": reset
            },
            headers={
                "X-RateLimit-Limit": str(rate_limiter.limits[tier]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset),
                "Retry-After": str(reset)
            }
        )
    
    # Process request...
    return {
        "data": "...",
        "rate_limit": {
            "remaining": remaining,
            "reset": reset
        }
    }
```

---

#### 7. Setup Usage Monitoring

**Upstash Dashboard:**
1. Go to [Upstash Console](https://console.upstash.com)
2. Click on your database
3. View **Metrics** tab:
   - Commands per second
   - Database size
   - Hit/Miss ratio
   - Latency

**Set up Alerts:**
1. Click **"Alerts"** tab
2. Add alert conditions:
   - **Daily command limit reached** - 80% of quota
   - **High latency** - Average >100ms
   - **High memory usage** - >80% capacity
3. Add email for notifications

**Monitor from Code:**
```python
# Get cache statistics
stats = await cache.get_stats()
print(f"Cache Hit Rate: {stats['hit_rate']}%")
print(f"Memory Used: {stats['memory_used']}")
print(f"Total Commands: {stats['total_commands']}")
```

---

#### 8. Test Production Redis

**Test Script:**
File: `scripts/test_production_redis.py`

```python
import asyncio
from cache.redis import cache

async def test_redis():
    """Test production Redis connection and operations"""
    
    print("🔌 Connecting to production Redis...")
    await cache.connect()
    
    try:
        # Test 1: Basic operations
        print("\n📝 Test 1: Basic SET/GET")
        await cache.set('test_key', {'value': 123}, category='test')
        result = await cache.get('test_key', category='test')
        assert result['value'] == 123
        print("✅ Passed")
        
        # Test 2: TTL
        print("\n⏱️ Test 2: TTL Expiry")
        await cache.set('expire_key', 'test', category='test', ttl=2)
        result1 = await cache.get('expire_key', category='test')
        await asyncio.sleep(3)
        result2 = await cache.get('expire_key', category='test')
        assert result1 == 'test'
        assert result2 is None
        print("✅ Passed")
        
        # Test 3: Delete
        print("\n🗑️ Test 3: DELETE")
        await cache.set('delete_key', 'value', category='test')
        await cache.delete('delete_key', category='test')
        result = await cache.get('delete_key', category='test')
        assert result is None
        print("✅ Passed")
        
        # Test 4: Clear category
        print("\n🧹 Test 4: CLEAR Category")
        await cache.set('key1', 'val1', category='test')
        await cache.set('key2', 'val2', category='test')
        deleted = await cache.clear_category('test')
        assert deleted >= 2
        print(f"✅ Passed (deleted {deleted} keys)")
        
        # Test 5: Statistics
        print("\n📊 Test 5: Statistics")
        stats = await cache.get_stats()
        print(f"   Hit Rate: {stats['hit_rate']}%")
        print(f"   Memory: {stats['memory_used']}")
        print(f"   Commands: {stats['total_commands']}")
        print("✅ Passed")
        
        print("\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
    
    finally:
        await cache.close()

if __name__ == "__main__":
    asyncio.run(test_redis())
```

**Run Test:**
```bash
python scripts/test_production_redis.py
```

**Expected Output:**
```
🔌 Connecting to production Redis...
✅ Connected to production Redis

📝 Test 1: Basic SET/GET
✅ Passed

⏱️ Test 2: TTL Expiry
✅ Passed

🗑️ Test 3: DELETE
✅ Passed

🧹 Test 4: CLEAR Category
✅ Passed (deleted 2 keys)

📊 Test 5: Statistics
   Hit Rate: 85.5%
   Memory: 1.2M
   Commands: 1542
✅ Passed

🎉 All tests passed!
🔌 Redis connection closed
```

---

#### 9. Optimize Performance

**Connection Pool Tuning:**
```python
# In cache/redis.py
self.redis = await aioredis.from_url(
    redis_url,
    max_connections=50,  # Increase for high traffic (default: 50)
    # For 1000+ concurrent users, use 100-200
)
```

**Pipeline for Bulk Operations:**
```python
async def bulk_set(self, items: dict, category: str):
    """Set multiple items efficiently"""
    pipe = self.redis.pipeline()
    
    for key, value in items.items():
        ttl = self.ttl_policies.get(category, 300)
        pipe.setex(f"{category}:{key}", ttl, json.dumps(value))
    
    await pipe.execute()
```

**LRU Eviction Policy:**
- Already set during creation: `allkeys-lru`
- Automatically removes least recently used keys when memory full
- No manual cleanup needed!

---

#### 10. Backup Strategy

**Upstash Automatic Backups:**
- ✅ Upstash creates **automatic snapshots** daily
- ✅ Retained for **7 days** (Pay-as-you-go)
- ✅ Retained for **30 days** (Pro plan)

**Manual Backup (Optional):**
```python
async def backup_critical_data():
    """Backup critical cached data to MongoDB"""
    critical_categories = ['guild_settings', 'premium_status']
    
    for category in critical_categories:
        pattern = f"{category}:*"
        async for key in cache.redis.scan_iter(match=pattern):
            value = await cache.redis.get(key)
            # Save to MongoDB as backup
            await db.cache_backups.insert_one({
                'key': key,
                'value': value,
                'timestamp': datetime.utcnow()
            })
```

---

### ✅ Phase 6.3 Completion Checklist

- [ ] Production Redis database created (Upstash)
- [ ] Connection details obtained and tested
- [ ] Environment variables updated with production credentials
- [ ] TLS encryption enabled (rediss://)
- [ ] Persistence verified (automatic with Upstash)
- [ ] Cache policies configured (TTL per category)
- [ ] Rate limiting system implemented
- [ ] Usage monitoring enabled in Upstash dashboard
- [ ] Alerts configured (80% quota, latency, memory)
- [ ] Connection test passed (all 5 tests)
- [ ] Performance optimizations applied
- [ ] Backup strategy documented

**Expected Result:** ✅ Production Redis ready with <10ms latency

---

<a id="phase-64-domain-ssl"></a>
## 🌐 Phase 6.4: Domain & SSL

**Status:** 🔲 Not Started  
**Estimated Time:** 1 day  
**Priority:** 🔴 Critical

### Current State
- ✅ Dashboard working on localhost
- ✅ API working on localhost
- ⏳ Need custom domain
- ⏳ Need SSL certificate
- ⏳ Need to update Discord OAuth

### Step-by-Step Guide

#### 1. Purchase Domain Name

**Recommended Registrars:**
- **Namecheap** - $10-15/year, free WhoisGuard
- **Cloudflare** - At-cost pricing, best for performance
- **GoDaddy** - $12-20/year, frequent sales
- **Porkbun** - $8-12/year, budget friendly

**Domain Name Ideas:**
```
kingdom77.com           (Premium - if available)
kingdom-bot.com         (Professional)
kingdom77bot.com        (Clear purpose)
kingdom77discord.com    (Very clear)
kingdom77.io            (Tech-savvy, $35/year)
kingdom77.gg            (Gaming focused, $35/year)
```

**Steps (Namecheap example):**
1. Go to [Namecheap.com](https://www.namecheap.com)
2. Search for your desired domain
3. Add to cart (select 1-2 years)
4. Add **WhoisGuard** (free privacy protection)
5. Skip extras (hosting, email - not needed)
6. Checkout ($10-15 total)

---

#### 2. Configure DNS Records

**Wait Time:** DNS changes take 5 minutes to 48 hours to propagate (usually 30 minutes)

**Cloudflare Setup (Recommended):**

**Why Cloudflare?**
- ✅ Free SSL certificates
- ✅ CDN included (faster website)
- ✅ DDoS protection
- ✅ Better DNS management
- ✅ Analytics included

**Steps:**
1. Create [Cloudflare account](https://cloudflare.com) (free)
2. Click **"Add Site"**
3. Enter your domain: `kingdom77.com`
4. Select **Free plan**
5. Cloudflare will scan existing DNS records
6. Click **"Continue"**
7. Copy the 2 nameservers shown (e.g., `dana.ns.cloudflare.com`)
8. Go back to Namecheap (or your registrar)
9. Click **Manage** → **Nameservers** → **Custom DNS**
10. Enter Cloudflare's nameservers
11. Wait 5-30 minutes for DNS propagation

---

#### 3. Add DNS Records in Cloudflare

**Required Records:**

**For Dashboard (Frontend - Vercel/Netlify):**
```
Type: CNAME
Name: @ (or www)
Target: cname.vercel-dns.com (or Netlify's)
Proxy: ✅ Proxied (orange cloud)
TTL: Auto
```

**For API (Backend - Render/Railway):**
```
Type: CNAME
Name: api
Target: your-app.onrender.com (or Railway's)
Proxy: ✅ Proxied (orange cloud)
TTL: Auto
```

**Example Configuration:**
```
kingdom77.com           → CNAME → cname.vercel-dns.com (Dashboard)
www.kingdom77.com       → CNAME → cname.vercel-dns.com (Dashboard)
api.kingdom77.com       → CNAME → kingdom77.onrender.com (API)
```

**Final URLs:**
- Dashboard: `https://kingdom77.com`
- API: `https://api.kingdom77.com`

---

#### 4. Install SSL Certificate (Automatic with Cloudflare)

**Cloudflare SSL (Automatic & Free):**

1. In Cloudflare dashboard, go to **SSL/TLS**
2. Select **"Full (strict)"** encryption mode
3. Enable **"Always Use HTTPS"** - Force HTTPS
4. Enable **"Automatic HTTPS Rewrites"**
5. Go to **Edge Certificates** tab
6. Verify these are enabled:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites
   - ✅ Universal SSL Certificate (Free)
   - ✅ TLS 1.3 (Modern browsers)

**Expected Result:** ✅ SSL active in 5-15 minutes

**Test SSL:**
```bash
# Should return 200 with HTTPS
curl -I https://kingdom77.com
curl -I https://api.kingdom77.com
```

---

#### 5. Update Discord OAuth URLs

**Why?** Discord OAuth only allows registered redirect URIs

**Steps:**
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your bot application
3. Go to **OAuth2** → **General**
4. Find **"Redirects"** section
5. Add production URLs:
   ```
   https://kingdom77.com/auth/callback
   https://api.kingdom77.com/api/auth/callback
   ```
6. Keep development URL for testing:
   ```
   http://localhost:3000/auth/callback
   ```
7. Click **"Save Changes"**

**Update Environment Variables:**

**Backend (.env):**
```env
# Production URLs
DASHBOARD_URL=https://kingdom77.com
API_URL=https://api.kingdom77.com

# Discord OAuth
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=https://api.kingdom77.com/api/auth/callback
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_URL=https://api.kingdom77.com
NEXT_PUBLIC_DASHBOARD_URL=https://kingdom77.com
```

---

#### 6. Enable HTTPS Redirect

**Force HTTPS Everywhere:**

**Cloudflare (Automatic):**
- Already enabled in Step 4 with "Always Use HTTPS"
- HTTP requests automatically redirect to HTTPS

**Backend (FastAPI - Extra Security):**
File: `dashboard/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app = FastAPI()

# Force HTTPS in production
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
```

**Frontend (Next.js - next.config.js):**
```javascript
module.exports = {
  async redirects() {
    return [
      {
        source: '/:path*',
        has: [
          {
            type: 'header',
            key: 'x-forwarded-proto',
            value: 'http',
          },
        ],
        destination: 'https://kingdom77.com/:path*',
        permanent: true,
      },
    ]
  },
}
```

---

#### 7. Update Stripe Webhook URLs

**Steps:**
1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Go to **Developers** → **Webhooks**
3. Find your webhook endpoint
4. Click **"..."** → **"Update details"**
5. Update URL from:
   ```
   http://localhost:8000/api/stripe/webhook
   ```
   To:
   ```
   https://api.kingdom77.com/api/stripe/webhook
   ```
6. Click **"Update endpoint"**
7. Test webhook delivery

---

#### 8. Configure CORS for Production

**Update CORS Origins:**
File: `dashboard/main.py`

```python
from fastapi.middleware.cors import CORSMiddleware

# Production origins
origins = [
    "https://kingdom77.com",
    "https://www.kingdom77.com",
    "https://api.kingdom77.com",
]

# Add localhost for development
if os.getenv("ENVIRONMENT") == "development":
    origins.extend([
        "http://localhost:3000",
        "http://localhost:8000",
    ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

#### 9. Test Domain & SSL

**Checklist:**
- [ ] Domain resolves to correct IP
- [ ] HTTPS works without warnings
- [ ] HTTP redirects to HTTPS
- [ ] SSL certificate is valid (check lock icon)
- [ ] API endpoints accessible via HTTPS
- [ ] Discord OAuth login works
- [ ] Stripe webhooks receive events
- [ ] No mixed content warnings (all resources use HTTPS)

**Testing Tools:**
```bash
# 1. DNS Propagation
dig kingdom77.com
dig api.kingdom77.com

# 2. SSL Certificate
curl -vI https://kingdom77.com 2>&1 | grep -i ssl

# 3. HTTPS Redirect
curl -I http://kingdom77.com | grep -i location

# 4. API Health Check
curl https://api.kingdom77.com/health
```

**Online Tools:**
- [SSL Test](https://www.ssllabs.com/ssltest/) - Check SSL configuration (should get A or A+)
- [DNS Checker](https://dnschecker.org) - Verify DNS propagation worldwide
- [HTTP Header Check](https://securityheaders.com) - Security headers validation

---

#### 10. Setup Domain Email (Optional)

**For Professional Communication:**

**Free Options:**
1. **Cloudflare Email Routing** (Recommended - Free forever)
   - Forward emails to your personal email
   - Example: `support@kingdom77.com` → `your@gmail.com`
   
   **Setup:**
   1. Cloudflare Dashboard → **Email** → **Email Routing**
   2. Enable Email Routing
   3. Add destination address (your personal email)
   4. Verify destination email (click link in email)
   5. Add routing rules:
      ```
      support@kingdom77.com → your@gmail.com
      contact@kingdom77.com → your@gmail.com
      ```

2. **Gmail Alias**
   - Send emails from `support@kingdom77.com` using Gmail
   
   **Setup:**
   1. Gmail → Settings → **Accounts** → **Send mail as**
   2. Add another email address
   3. Enter: `Support <support@kingdom77.com>`
   4. Follow verification steps

---

### ✅ Phase 6.4 Completion Checklist

- [ ] Domain name purchased and registered
- [ ] Cloudflare account created and domain added
- [ ] Nameservers updated to Cloudflare
- [ ] DNS records configured (CNAME for domain and api subdomain)
- [ ] SSL certificate installed and active (Full Strict mode)
- [ ] HTTPS redirect enabled (Always Use HTTPS)
- [ ] Discord OAuth URLs updated with production domain
- [ ] Stripe webhook URLs updated with production domain
- [ ] Environment variables updated with production URLs
- [ ] CORS configured for production origins
- [ ] Domain resolves correctly (both apex and www)
- [ ] SSL test passed (A or A+ rating)
- [ ] HTTP to HTTPS redirect working
- [ ] API accessible via HTTPS
- [ ] No mixed content warnings
- [ ] Email forwarding configured (optional)

**Expected Result:** ✅ Custom domain with valid SSL, all services accessible via HTTPS

---

<a id="phase-65-bot-hosting"></a>
## 🤖 Phase 6.5: Bot Hosting

**Status:** 🔲 Not Started  
**Estimated Time:** 1-2 days  
**Priority:** 🔴 Critical

### Current State
- ✅ Bot runs locally on your machine
- ✅ All features tested and working
- ⏳ Need 24/7 hosting
- ⏳ Need auto-restart on crash
- ⏳ Need resource monitoring

### Hosting Platform Comparison

| Platform | Free Tier | Paid | Pros | Cons |
|----------|-----------|------|------|------|
| **Render** | 750 hrs/mo | $7/mo | Easy setup, auto-deploy | Spins down on free |
| **Railway** | $5 credit | $5-20/mo | Modern UI, fast | Credit-based |
| **Heroku** | No free | $7/mo | Reliable, mature | No free tier now |
| **Fly.io** | 3 VMs free | $10/mo | Edge network | Complex config |
| **DigitalOcean** | $200 credit | $6/mo | Full control | Manual setup |

**Recommendation:** **Railway** or **Render** (easiest, good value)

---

### Option A: Deploy to Railway (Recommended)

**Why Railway?**
- ✅ Simple setup (5 minutes)
- ✅ Automatic deployments from GitHub
- ✅ $5 free credit/month
- ✅ Built-in environment variables
- ✅ Excellent logs and monitoring

#### 1. Create Railway Account

1. Go to [Railway.app](https://railway.app)
2. Click **"Login"** → **"Login with GitHub"**
3. Authorize Railway
4. Click **"New Project"**

---

#### 2. Deploy Bot from GitHub

**Steps:**
1. Click **"Deploy from GitHub repo"**
2. Select **"Configure GitHub App"**
3. Choose repositories: **Kingdom-77** repository
4. Click **"Deploy"**
5. Select **Kingdom-77** repo from list
6. Railway automatically detects Python project

**Buildpack Detection:**
Railway will detect `requirements.txt` and use Python buildpack automatically.

---

#### 3. Configure Environment Variables

**In Railway Dashboard:**
1. Click on your service
2. Go to **"Variables"** tab
3. Click **"Add Variable"**
4. Add all variables from `.env`:

```env
# Discord Bot
DISCORD_TOKEN=your_bot_token_here
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret

# MongoDB Production
MONGODB_URI=mongodb+srv://kingdom77_prod:PASSWORD@kingdom77-production.xxxxx.mongodb.net/kingdom77_prod?retryWrites=true&w=majority
MONGODB_DATABASE=kingdom77_prod

# Redis Production
REDIS_URL=rediss://default:PASSWORD@redis-12345.upstash.io:6380
REDIS_HOST=redis-12345.upstash.io
REDIS_PORT=6380
REDIS_PASSWORD=your_redis_password
REDIS_SSL=true

# Stripe Production
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY
STRIPE_SECRET_KEY=sk_live_YOUR_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
STRIPE_PRICE_PREMIUM_MONTHLY=price_YOUR_ID
STRIPE_PRICE_PREMIUM_YEARLY=price_YOUR_ID

# Dashboard URLs
DASHBOARD_URL=https://kingdom77.com
API_URL=https://api.kingdom77.com

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO

# Social Media APIs (Optional)
YOUTUBE_API_KEY=your_youtube_key
TWITCH_CLIENT_ID=your_twitch_id
TWITCH_CLIENT_SECRET=your_twitch_secret
```

4. Click **"Add"** for each variable

**Tip:** Use Railway's **"Raw Editor"** to paste all at once:
```
DISCORD_TOKEN=xxx
MONGODB_URI=xxx
REDIS_URL=xxx
...
```

---

#### 4. Configure Start Command

**Create Procfile:**
File: `Procfile` (root directory)

```
worker: python main.py
```

**Or configure in Railway:**
1. Go to **"Settings"** tab
2. Find **"Start Command"**
3. Enter: `python main.py`
4. Click **"Save"**

---

#### 5. Configure Worker Process

**Railway Settings:**
1. **Region:** Choose closest to your users (US West, US East, EU West)
2. **Restart Policy:** "Always" (auto-restart on crash)
3. **Health Checks:** Enable if available
4. **Resources:**
   - **Memory:** 512MB (sufficient for most bots)
   - **CPU:** Shared (1vCPU)

**Cost Estimate:**
```
512MB RAM, Always On = ~$5-10/month
1GB RAM, Always On = ~$10-15/month
```

---

#### 6. Deploy and Monitor

**Automatic Deployment:**
Railway will automatically:
1. Install dependencies from `requirements.txt`
2. Run your start command
3. Stream logs in real-time

**View Logs:**
1. Click on service
2. Go to **"Logs"** tab
3. You should see:
   ```
   ✅ Bot is ready!
   ✅ Logged in as Kingdom-77#1234
   ✅ Connected to MongoDB
   ✅ Connected to Redis
   ✅ Guilds: 0
   ✅ Users: 0
   ```

**Troubleshooting Failed Deployment:**
```bash
# Check logs for errors
# Common issues:

# 1. Missing environment variable
Error: DISCORD_TOKEN not found
→ Solution: Add to Variables tab

# 2. Module not found
ModuleNotFoundError: No module named 'discord'
→ Solution: Ensure requirements.txt is in root

# 3. MongoDB connection failed
→ Solution: Check MongoDB URI and IP whitelist (allow 0.0.0.0/0)

# 4. Redis connection failed
→ Solution: Check REDIS_URL format (should be rediss://)
```

---

#### 7. Setup Auto-Restart

**Railway Auto-Restart (Built-in):**
- ✅ Automatically restarts on crash
- ✅ Restarts on deployment
- ✅ Health checks (optional)

**Add Health Check in Code:**
File: `main.py`

```python
import discord
from discord.ext import tasks
import logging

logger = logging.getLogger(__name__)

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.uptime = datetime.utcnow()
    
    async def on_ready(self):
        logger.info(f"✅ Bot is ready! Logged in as {self.user}")
        self.health_check.start()
    
    @tasks.loop(minutes=5)
    async def health_check(self):
        """Health check every 5 minutes"""
        try:
            # Check Discord connection
            if not self.is_closed():
                logger.info(f"💚 Health check passed - Uptime: {self.uptime}")
            else:
                logger.error("❌ Bot is closed, restarting...")
                await self.close()
                
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
```

---

#### 8. Resource Monitoring

**Railway Metrics:**
1. Go to **"Metrics"** tab
2. Monitor:
   - **CPU Usage** - Should be <50% average
   - **Memory Usage** - Should be <80% of allocated
   - **Network** - Track API calls

**Set Usage Alerts:**
1. Go to **"Settings"** → **"Usage Alerts"**
2. Set budget: $20/month (safety limit)
3. Add email for notifications

**Cost Tracking:**
```
Current Month Usage: $5.43
Estimated End of Month: $8.50
```

---

#### 9. Setup Deployment Webhook (Optional)

**Auto-Deploy on Git Push:**

**Already enabled by default!**
Every push to `main` branch triggers deployment.

**Manual Deployment:**
1. Go to **"Deployments"** tab
2. Click **"Deploy"** → **"Redeploy"**

**Deployment Webhook (for custom CI/CD):**
1. Go to **"Settings"**
2. Find **"Webhooks"**
3. Copy webhook URL
4. Use in GitHub Actions or other CI/CD

---

#### 10. Backup Strategy

**Railway Persistent Storage (Optional):**
If bot generates files (logs, images):

```python
# Use /data directory (persisted)
LOG_DIR = "/data/logs" if os.path.exists("/data") else "./logs"
```

**Or use MongoDB/S3 for file storage:**
```python
# Store generated images in MongoDB
card_data = base64.b64encode(image_bytes).decode()
await db.level_cards.insert_one({
    'user_id': user_id,
    'image_data': card_data,
    'created_at': datetime.utcnow()
})
```

---

### Option B: Deploy to Render (Alternative)

**Similar process to Railway:**
1. Create [Render account](https://render.com)
2. Click **"New"** → **"Web Service"**
3. Connect GitHub repo
4. Configure:
   - **Name:** kingdom77-bot
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python main.py`
5. Add environment variables
6. Click **"Create Web Service"**

**Cost:** $7/month (no free tier that stays always on)

---

### ✅ Phase 6.5 Completion Checklist

- [ ] Railway/Render account created
- [ ] Bot repository connected to hosting platform
- [ ] All environment variables configured (20+ variables)
- [ ] Start command configured (`python main.py`)
- [ ] Worker process configured (512MB RAM minimum)
- [ ] Bot deployed successfully
- [ ] Bot shows online in Discord
- [ ] Logs show successful connections (MongoDB, Redis)
- [ ] Auto-restart configured
- [ ] Health checks implemented
- [ ] Resource monitoring enabled
- [ ] Usage alerts configured ($20/month budget)
- [ ] Deployment webhook setup (auto-deploy on push)
- [ ] Test bot commands in Discord
- [ ] Backup strategy implemented

**Verification Tests:**
```
1. Check bot status in Discord (should be online 🟢)
2. Run /ping command (should respond)
3. Check logs in Railway dashboard (no errors)
4. Stop bot manually, verify auto-restart (< 30 seconds)
5. Monitor memory usage (should be < 400MB)
```

**Expected Result:** ✅ Bot running 24/7, auto-restarts on crash, <$10/month cost

---

<a id="phase-66-dashboard-hosting"></a>
## 🌐 Phase 6.6: Dashboard Hosting

**Status:** 🔲 Not Started  
**Estimated Time:** 1-2 days  
**Priority:** 🔴 Critical

### Current State
- ✅ Dashboard works on localhost
- ✅ Frontend (Next.js 14) ready
- ✅ Backend (FastAPI) ready
- ⏳ Need production hosting
- ⏳ Need domain connection

### Architecture

```
Frontend (Vercel/Netlify)     Backend (Railway/Render)
    kingdom77.com      ←→      api.kingdom77.com
    Next.js 14 App             FastAPI REST API
```

---

### Part A: Deploy Backend API (Railway/Render)

#### 1. Deploy API to Railway

**Steps:**
1. Go to [Railway.app](https://railway.app)
2. Click **"New Project"**
3. Click **"Deploy from GitHub repo"**
4. Select **Kingdom-77** repository
5. Railway detects multiple services - select **"dashboard"** folder

**Alternative - Add to existing project:**
1. Open existing Kingdom-77 project (where bot is)
2. Click **"New"** → **"GitHub Repo"**
3. Select same repo
4. Configure root directory: **"dashboard"**

---

#### 2. Configure API Environment Variables

**In Railway Variables tab:**
```env
# Python Environment
PYTHON_VERSION=3.11

# API Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# MongoDB Production
MONGODB_URI=mongodb+srv://kingdom77_prod:PASSWORD@kingdom77-production.xxxxx.mongodb.net/kingdom77_prod
MONGODB_DATABASE=kingdom77_prod

# Redis Production
REDIS_URL=rediss://default:PASSWORD@redis-12345.upstash.io:6380

# Discord OAuth
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=https://api.kingdom77.com/api/auth/callback
DISCORD_BOT_TOKEN=your_bot_token

# JWT
JWT_SECRET=your_random_secret_key_min_32_chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION=86400

# Session
SESSION_SECRET=your_random_session_secret_32_chars

# Stripe Production
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY
STRIPE_SECRET_KEY=sk_live_YOUR_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET

# Frontend URL
DASHBOARD_URL=https://kingdom77.com
API_URL=https://api.kingdom77.com

# CORS Origins
CORS_ORIGINS=https://kingdom77.com,https://www.kingdom77.com

# Rate Limiting
RATE_LIMIT_FREE=60
RATE_LIMIT_BASIC=120
RATE_LIMIT_PREMIUM=300

# Logging
LOG_LEVEL=INFO
LOG_WEBHOOK_URL=your_discord_webhook_for_logs
```

---

#### 3. Configure API Start Command

**Create Procfile in dashboard/ folder:**
File: `dashboard/Procfile`

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Or in Railway Settings:**
```
Start Command: cd dashboard && uvicorn main:app --host 0.0.0.0 --port $PORT --workers 2
```

**For Render:**
```
Build Command: cd dashboard && pip install -r requirements.txt
Start Command: cd dashboard && uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

---

#### 4. Connect Custom Domain to API

**In Railway:**
1. Go to your API service
2. Click **"Settings"** tab
3. Find **"Domains"** section
4. Click **"Generate Domain"** (gets free subdomain like `kingdom77.up.railway.app`)
5. Click **"Custom Domain"**
6. Enter: `api.kingdom77.com`
7. Railway provides CNAME record

**In Cloudflare DNS:**
1. Add CNAME record:
   ```
   Type: CNAME
   Name: api
   Target: kingdom77.up.railway.app (or provided CNAME)
   Proxy: ✅ Proxied (orange cloud)
   TTL: Auto
   ```
2. Wait 5-10 minutes for propagation

**Verify API:**
```bash
curl https://api.kingdom77.com/health
# Should return: {"status": "healthy", "version": "4.0"}
```

---

### Part B: Deploy Frontend Dashboard (Vercel)

**Why Vercel?**
- ✅ Made for Next.js (same company)
- ✅ Automatic deployments
- ✅ Edge network (fast worldwide)
- ✅ Free SSL
- ✅ Preview deployments
- ✅ Free tier (100GB bandwidth/month)

#### 5. Create Vercel Account

1. Go to [Vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. Choose **"Continue with GitHub"**
4. Authorize Vercel

---

#### 6. Deploy Next.js Dashboard

**Steps:**
1. Click **"Add New Project"**
2. Click **"Import Git Repository"**
3. Find **Kingdom-77** repository
4. Click **"Import"**
5. Configure Project:
   - **Project Name:** `kingdom77-dashboard`
   - **Framework Preset:** Next.js (auto-detected)
   - **Root Directory:** `dashboard-frontend`
   - **Build Command:** `npm run build` (default)
   - **Output Directory:** `.next` (default)
6. Don't click Deploy yet - add environment variables first

---

#### 7. Configure Frontend Environment Variables

**In Vercel Project Settings → Environment Variables:**

**Add these variables:**
```env
# API URL (Production)
NEXT_PUBLIC_API_URL=https://api.kingdom77.com

# Dashboard URL
NEXT_PUBLIC_DASHBOARD_URL=https://kingdom77.com

# Discord OAuth
NEXT_PUBLIC_DISCORD_CLIENT_ID=your_client_id

# Stripe
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_live_xxxx

# Environment
NEXT_PUBLIC_ENVIRONMENT=production

# Analytics (Optional)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

**Important:** Add to all environments:
- ✅ Production
- ✅ Preview
- ✅ Development

---

#### 8. Build Configuration

**Verify next.config.js:**
File: `dashboard-frontend/next.config.js`

```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for better performance
  output: 'standalone',
  
  // Image optimization
  images: {
    domains: [
      'cdn.discordapp.com',  // Discord avatars
      'i.imgur.com',          // User uploaded images
    ],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.discordapp.com',
      },
    ],
  },
  
  // Redirect HTTP to HTTPS
  async redirects() {
    return [
      {
        source: '/:path*',
        has: [
          {
            type: 'header',
            key: 'x-forwarded-proto',
            value: 'http',
          },
        ],
        destination: 'https://kingdom77.com/:path*',
        permanent: true,
      },
    ]
  },
  
  // Security headers
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'X-DNS-Prefetch-Control',
            value: 'on'
          },
          {
            key: 'Strict-Transport-Security',
            value: 'max-age=63072000; includeSubDomains; preload'
          },
          {
            key: 'X-Frame-Options',
            value: 'SAMEORIGIN'
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff'
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block'
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin'
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
```

---

#### 9. Deploy to Vercel

**Click "Deploy" button!**

**Deployment Process:**
1. **Install Dependencies** - `npm install` (2-3 minutes)
2. **Build** - `npm run build` (3-5 minutes)
3. **Deploy** - Upload to edge network (1 minute)

**Expected Output:**
```
✓ Compiled successfully
✓ Linting and checking validity of types
✓ Creating an optimized production build
✓ Collecting page data
✓ Generating static pages (15/15)
✓ Finalizing page optimization

Build completed in 3m 42s
```

**You'll get a preview URL:**
```
https://kingdom77-dashboard-abc123.vercel.app
```

---

#### 10. Connect Custom Domain to Dashboard

**In Vercel Project Settings:**
1. Go to **"Settings"** → **"Domains"**
2. Click **"Add"**
3. Enter your domain: `kingdom77.com`
4. Click **"Add"**
5. Vercel will provide DNS records

**Also add www subdomain:**
6. Click **"Add"** again
7. Enter: `www.kingdom77.com`
8. Configure to redirect to apex domain

**In Cloudflare DNS:**

**For apex domain (kingdom77.com):**
```
Type: CNAME
Name: @
Target: cname.vercel-dns.com
Proxy: ✅ Proxied
TTL: Auto
```

**For www subdomain:**
```
Type: CNAME
Name: www
Target: cname.vercel-dns.com
Proxy: ✅ Proxied
TTL: Auto
```

**Wait 5-10 minutes for propagation**

**Verify:**
```bash
curl -I https://kingdom77.com
curl -I https://www.kingdom77.com
# Both should return 200 OK
```

---

#### 11. SSL Certificate (Automatic)

**Vercel SSL (Automatic & Free):**
- ✅ Automatically provisions Let's Encrypt certificate
- ✅ Renews automatically
- ✅ HTTPS enforced by default
- ✅ HTTP/2 and HTTP/3 enabled

**Check SSL Status:**
1. In Vercel, go to **Domains** tab
2. Look for green checkmark ✅ next to domain
3. Status should say: **"Valid"**

**Test SSL:**
```bash
curl -I https://kingdom77.com | grep -i server
# Should return: server: Vercel
```

---

#### 12. Build Optimization

**Enable Production Optimizations:**

**1. Image Optimization:**
Already configured in `next.config.js` - Vercel handles automatically

**2. Code Splitting:**
Next.js 14 does this automatically with App Router

**3. Compression:**
Vercel automatically compresses with Brotli/Gzip

**4. Caching:**
```javascript
// In app/layout.tsx
export const metadata = {
  // ...
}

// Static pages cached for 1 year
export const revalidate = 31536000
```

**5. Analytics (Optional but Recommended):**
```bash
# Install Vercel Analytics
npm install @vercel/analytics

# Add to app/layout.tsx
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

---

#### 13. Setup Preview Deployments

**Automatic Preview Deployments (Already Enabled!):**

Every time you push to a branch (not `main`), Vercel creates a preview:
```
Branch: feature/new-ui
Preview: https://kingdom77-dashboard-git-feature-new-ui.vercel.app
```

**Share preview links with team for testing before merging!**

**Configure:**
1. Go to **Settings** → **Git**
2. Enable:
   - ✅ Automatic Deployments (main branch)
   - ✅ Preview Deployments (all branches)
   - ✅ Production Deployments (main branch only)

---

#### 14. Configure Deployment Protection (Optional)

**Password-Protect Preview Deployments:**
1. Go to **Settings** → **Deployment Protection**
2. Enable **"Vercel Authentication"**
3. Only team members can view preview deployments

**Or use custom password:**
```javascript
// In middleware.ts
import { NextResponse } from 'next/server'

export function middleware(request) {
  // Only protect preview deployments
  if (process.env.VERCEL_ENV === 'preview') {
    const basicAuth = request.headers.get('authorization')
    
    if (!basicAuth) {
      return new NextResponse('Authentication required', {
        status: 401,
        headers: {
          'WWW-Authenticate': 'Basic realm="Secure Area"',
        },
      })
    }
    
    const auth = basicAuth.split(' ')[1]
    const [user, pwd] = Buffer.from(auth, 'base64').toString().split(':')
    
    if (user !== 'preview' || pwd !== 'secret123') {
      return new NextResponse('Invalid credentials', { status: 401 })
    }
  }
  
  return NextResponse.next()
}
```

---

#### 15. Performance Monitoring

**Vercel Analytics (Built-in):**
1. Go to **Analytics** tab
2. View:
   - **Real-time visitors**
   - **Page views**
   - **Top pages**
   - **Countries**
   - **Devices**

**Speed Insights:**
1. Install:
   ```bash
   npm install @vercel/speed-insights
   ```

2. Add to layout:
   ```javascript
   import { SpeedInsights } from '@vercel/speed-insights/next'
   
   export default function RootLayout({ children }) {
     return (
       <html>
         <body>
           {children}
           <SpeedInsights />
         </body>
       </html>
     )
   }
   ```

3. View in **Speed Insights** tab:
   - Time to First Byte (TTFB)
   - First Contentful Paint (FCP)
   - Largest Contentful Paint (LCP)
   - Cumulative Layout Shift (CLS)

**Target Metrics:**
- ✅ LCP < 2.5s
- ✅ FID < 100ms
- ✅ CLS < 0.1

---

### ✅ Phase 6.6 Completion Checklist

**Backend API:**
- [ ] API deployed to Railway/Render
- [ ] All environment variables configured (25+ variables)
- [ ] Start command configured (uvicorn with workers)
- [ ] Custom domain connected (api.kingdom77.com)
- [ ] SSL certificate active
- [ ] API health endpoint responding
- [ ] CORS configured for production origins
- [ ] Rate limiting enabled
- [ ] Logs show no errors

**Frontend Dashboard:**
- [ ] Vercel account created and connected to GitHub
- [ ] Dashboard deployed successfully
- [ ] All environment variables configured (7+ variables)
- [ ] Custom domain connected (kingdom77.com + www)
- [ ] SSL certificate active (automatic)
- [ ] HTTPS enforced (HTTP redirects to HTTPS)
- [ ] Build optimization enabled
- [ ] Analytics installed (Vercel Analytics + Speed Insights)
- [ ] Preview deployments working
- [ ] Performance metrics good (LCP < 2.5s)

**Integration Tests:**
- [ ] Dashboard loads without errors
- [ ] API endpoints accessible from dashboard
- [ ] Discord OAuth login works
- [ ] User can view servers
- [ ] Premium subscription flow works
- [ ] All dashboard pages load correctly
- [ ] Mobile responsive design works
- [ ] No console errors in browser
- [ ] Images load from CDN

**Verification:**
```bash
# 1. Check API Health
curl https://api.kingdom77.com/health
# Expected: {"status": "healthy", "version": "4.0"}

# 2. Check Dashboard
curl -I https://kingdom77.com
# Expected: 200 OK, server: Vercel

# 3. Check SSL
openssl s_client -connect kingdom77.com:443 -servername kingdom77.com
# Expected: Verify return code: 0 (ok)

# 4. Check CORS
curl -H "Origin: https://kingdom77.com" https://api.kingdom77.com/api/auth/me
# Expected: Access-Control-Allow-Origin header present

# 5. Performance Test
curl -o /dev/null -s -w "Time: %{time_total}s\n" https://kingdom77.com
# Expected: < 2 seconds
```

**Expected Result:** ✅ Full dashboard accessible at https://kingdom77.com with API at https://api.kingdom77.com, both with valid SSL

---

<a id="phase-67-monitoring-analytics"></a>
## 📊 Phase 6.7: Monitoring & Analytics

**Status:** 🔲 Not Started  
**Estimated Time:** 2 days  
**Priority:** 🟡 Medium (but highly recommended)

### Current State
- ✅ Bot and dashboard deployed
- ✅ Services running in production
- ⏳ Need error tracking
- ⏳ Need performance monitoring
- ⏳ Need uptime monitoring
- ⏳ Need user analytics

### Monitoring Stack

```
Error Tracking → Sentry.io (Free: 5k events/month)
Uptime → Uptime Robot (Free: 50 monitors)
Analytics → Google Analytics 4 (Free: Unlimited)
Logs → Railway/Render Built-in + Discord Webhook
Performance → Vercel Speed Insights (Free)
```

---

### Part A: Error Tracking (Sentry)

**Why Sentry?**
- ✅ Catch errors before users report them
- ✅ Stack traces with context
- ✅ Release tracking
- ✅ Performance monitoring
- ✅ Free tier: 5,000 events/month

#### 1. Setup Sentry for Python (Bot + API)

**Create Account:**
1. Go to [Sentry.io](https://sentry.io)
2. Sign up with GitHub
3. Create new project:
   - **Platform:** Python
   - **Project Name:** kingdom77-bot
4. Copy your DSN:
   ```
   https://abc123@o456789.ingest.sentry.io/123456
   ```

**Install Sentry SDK:**
```bash
pip install sentry-sdk
```

**Add to requirements.txt:**
```
sentry-sdk==1.40.0
```

**Initialize Sentry:**
File: `main.py` (Bot)

```python
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import os

# Initialize Sentry
if os.getenv("ENVIRONMENT") == "production":
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment="production",
        release=f"kingdom77-bot@{os.getenv('VERSION', '4.0')}",
        
        # Performance Monitoring
        traces_sample_rate=0.1,  # 10% of transactions
        
        # Attach stack traces to errors
        attach_stacktrace=True,
        
        # Capture logs as breadcrumbs
        integrations=[
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
        ],
        
        # Filter sensitive data
        before_send=filter_sensitive_data,
    )

def filter_sensitive_data(event, hint):
    """Remove sensitive data from error reports"""
    # Remove tokens
    if 'request' in event:
        headers = event['request'].get('headers', {})
        if 'Authorization' in headers:
            headers['Authorization'] = '[Filtered]'
    
    return event
```

File: `dashboard/main.py` (API)

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

if os.getenv("ENVIRONMENT") == "production":
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment="production",
        release=f"kingdom77-api@{os.getenv('VERSION', '4.0')}",
        traces_sample_rate=0.1,
        integrations=[
            FastApiIntegration(),
            StarletteIntegration(),
        ],
    )
```

**Add Environment Variable:**
```env
SENTRY_DSN=https://abc123@o456789.ingest.sentry.io/123456
VERSION=4.0
```

---

#### 2. Setup Sentry for Next.js (Dashboard)

**Create Project:**
1. In Sentry, create another project:
   - **Platform:** Next.js
   - **Project Name:** kingdom77-dashboard
2. Copy DSN

**Install Sentry:**
```bash
cd dashboard-frontend
npm install @sentry/nextjs
```

**Run Configuration Wizard:**
```bash
npx @sentry/wizard@latest -i nextjs
```

**This creates:**
- `sentry.client.config.js`
- `sentry.server.config.js`
- `sentry.edge.config.js`
- Updates `next.config.js`

**Configure Sentry:**
File: `dashboard-frontend/sentry.client.config.js`

```javascript
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || "production",
  
  // Performance Monitoring
  tracesSampleRate: 0.1, // 10% of transactions
  
  // Session Replay
  replaysSessionSampleRate: 0.1, // 10% of sessions
  replaysOnErrorSampleRate: 1.0, // 100% of errors
  
  // Filter sensitive data
  beforeSend(event, hint) {
    // Remove user tokens
    if (event.request?.cookies) {
      delete event.request.cookies.token;
    }
    return event;
  },
});
```

**Add Environment Variable in Vercel:**
```env
NEXT_PUBLIC_SENTRY_DSN=https://xyz789@o456789.ingest.sentry.io/789012
SENTRY_AUTH_TOKEN=your_auth_token_from_wizard
```

---

#### 3. Test Error Tracking

**Trigger Test Error:**

**In Bot:**
```python
# Add test command
@bot.tree.command(name="sentry_test")
async def sentry_test(interaction: discord.Interaction):
    """Test Sentry error tracking"""
    division_by_zero = 1 / 0  # This will trigger error
```

**In API:**
```python
@router.get("/api/test-error")
async def test_error():
    raise Exception("Test error for Sentry")
```

**In Dashboard:**
```javascript
// Add to a page
<button onClick={() => {
  throw new Error("Test error for Sentry");
}}>
  Test Error
</button>
```

**Check Sentry Dashboard:**
1. Go to **Issues**
2. You should see new errors appear within seconds
3. Click on error to see:
   - Stack trace
   - User context
   - Breadcrumbs (logs leading to error)
   - Environment
   - Release version

---

### Part B: Uptime Monitoring (Uptime Robot)

**Why Uptime Robot?**
- ✅ Free tier: 50 monitors, 5-minute checks
- ✅ Email/SMS/Slack alerts
- ✅ Status page generation
- ✅ Response time tracking

#### 4. Setup Uptime Monitoring

**Create Account:**
1. Go to [UptimeRobot.com](https://uptimerobot.com)
2. Sign up (free)
3. Click **"Add New Monitor"**

**Monitor 1: Bot Health (Discord Status)**
```
Monitor Type: HTTP(s)
Friendly Name: Kingdom-77 Bot
URL: https://discord.com/api/v10/users/@me
Method: GET
Custom Headers: Authorization: Bot YOUR_BOT_TOKEN
Monitoring Interval: 5 minutes
Alert Contacts: Your email
```

**Monitor 2: API Health**
```
Monitor Type: HTTP(s)
Friendly Name: Kingdom-77 API
URL: https://api.kingdom77.com/health
Monitoring Interval: 5 minutes
Keyword: "healthy"
Alert Contacts: Your email
```

**Monitor 3: Dashboard**
```
Monitor Type: HTTP(s)
Friendly Name: Kingdom-77 Dashboard
URL: https://kingdom77.com
Monitoring Interval: 5 minutes
Keyword: "Kingdom-77"
Alert Contacts: Your email
```

**Monitor 4: MongoDB (via API)**
```
Monitor Type: HTTP(s)
Friendly Name: Database Connection
URL: https://api.kingdom77.com/health/database
Monitoring Interval: 5 minutes
Alert Contacts: Your email
```

**Monitor 5: Redis (via API)**
```
Monitor Type: HTTP(s)
Friendly Name: Cache Connection
URL: https://api.kingdom77.com/health/redis
Monitoring Interval: 5 minutes
Alert Contacts: Your email
```

**Add Health Endpoints in API:**
File: `dashboard/main.py`

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health():
    """Basic health check"""
    return {"status": "healthy", "version": "4.0"}

@router.get("/health/database")
async def health_database():
    """Check MongoDB connection"""
    try:
        await db.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@router.get("/health/redis")
async def health_redis():
    """Check Redis connection"""
    try:
        await cache.redis.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

---

#### 5. Setup Alert Channels

**Email Alerts (Default):**
- Already configured with your account email

**Discord Webhook Alerts (Recommended):**
1. In Uptime Robot, go to **My Settings** → **Alert Contacts**
2. Click **"Add Alert Contact"**
3. Type: **Webhook**
4. URL: Your Discord webhook URL
5. POST Value (JSON):
   ```json
   {
     "content": null,
     "embeds": [{
       "title": "*monitorFriendlyName* is *monitorAlertType*",
       "description": "*alertDetails*",
       "color": *monitorAlertType* == "down" ? 16711680 : 65280,
       "fields": [
         {"name": "URL", "value": "*monitorURL*", "inline": true},
         {"name": "Time", "value": "*alertDateTime*", "inline": true}
       ]
     }]
   }
   ```

**Slack Alerts:**
1. Create Slack webhook
2. Add as Alert Contact (type: Webhook)
3. Configure payload for Slack format

---

#### 6. Create Public Status Page

**Steps:**
1. In Uptime Robot, go to **Status Pages**
2. Click **"Add Status Page"**
3. Configure:
   - **Name:** Kingdom-77 Status
   - **Select Monitors:** All 5 monitors
   - **Custom Domain:** status.kingdom77.com (optional)
4. Click **"Create Status Page"**

**You get a public URL:**
```
https://stats.uptimerobot.com/abc123
```

**Add to your website footer:**
```javascript
<a href="https://stats.uptimerobot.com/abc123" target="_blank">
  Status
</a>
```

---

### Part C: User Analytics (Google Analytics 4)

#### 7. Setup Google Analytics

**Create Account:**
1. Go to [Google Analytics](https://analytics.google.com)
2. Click **"Start measuring"**
3. Account name: **Kingdom-77**
4. Property name: **Kingdom-77 Dashboard**
5. Industry: **Internet & Telecom**
6. Business size: **Small**
7. Create property
8. Copy **Measurement ID**: `G-XXXXXXXXXX`

---

#### 8. Install GA4 in Next.js

**Option A: Using @next/third-parties (Recommended)**
```bash
npm install @next/third-parties
```

File: `dashboard-frontend/app/layout.tsx`

```javascript
import { GoogleAnalytics } from '@next/third-parties/google'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <GoogleAnalytics gaId="G-XXXXXXXXXX" />
      </body>
    </html>
  )
}
```

**Option B: Manual Script**
File: `dashboard-frontend/app/layout.tsx`

```javascript
import Script from 'next/script'

export default function RootLayout({ children }) {
  const GA_ID = process.env.NEXT_PUBLIC_GA_ID
  
  return (
    <html>
      <head>
        {GA_ID && (
          <>
            <Script
              src={`https://www.googletagmanager.com/gtag/js?id=${GA_ID}`}
              strategy="afterInteractive"
            />
            <Script id="google-analytics" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${GA_ID}', {
                  page_path: window.location.pathname,
                });
              `}
            </Script>
          </>
        )}
      </head>
      <body>{children}</body>
    </html>
  )
}
```

**Add Environment Variable in Vercel:**
```env
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
```

---

#### 9. Track Custom Events

**Track Button Clicks:**
```javascript
'use client'

import { sendGAEvent } from '@next/third-parties/google'

export function PremiumButton() {
  const handleClick = () => {
    // Track event
    sendGAEvent({
      event: 'premium_click',
      value: 'monthly'
    })
    
    // Your click handler
    window.location.href = '/premium'
  }
  
  return <button onClick={handleClick}>Subscribe</button>
}
```

**Track Premium Purchases:**
```javascript
// After successful payment
sendGAEvent({
  event: 'purchase',
  currency: 'USD',
  value: 9.99,
  transaction_id: subscription_id,
  items: [{
    item_id: 'premium_monthly',
    item_name: 'Kingdom-77 Premium Monthly',
    price: 9.99,
    quantity: 1
  }]
})
```

---

### Part D: Logging System

#### 10. Centralized Logging with Discord Webhooks

**Create Discord Webhook:**
1. Create a private channel: `#bot-logs`
2. Channel Settings → Integrations → Webhooks
3. Create webhook, copy URL

**Setup Logging Handler:**
File: `utils/logging.py`

```python
import logging
import aiohttp
import json
from datetime import datetime

class DiscordWebhookHandler(logging.Handler):
    """Send logs to Discord webhook"""
    
    def __init__(self, webhook_url: str, level=logging.ERROR):
        super().__init__(level)
        self.webhook_url = webhook_url
    
    def emit(self, record):
        """Send log record to Discord"""
        try:
            # Format log message
            log_entry = self.format(record)
            
            # Create embed
            embed = {
                "title": f"🚨 {record.levelname}",
                "description": f"```\n{log_entry}\n```",
                "color": self.get_color(record.levelname),
                "timestamp": datetime.utcnow().isoformat(),
                "fields": [
                    {"name": "Logger", "value": record.name, "inline": True},
                    {"name": "Function", "value": record.funcName, "inline": True},
                    {"name": "Line", "value": str(record.lineno), "inline": True}
                ]
            }
            
            # Add exception info if available
            if record.exc_info:
                embed["fields"].append({
                    "name": "Exception",
                    "value": f"```\n{self.format_exception(record.exc_info)}\n```"
                })
            
            # Send to Discord (async)
            asyncio.create_task(self.send_webhook({
                "embeds": [embed]
            }))
            
        except Exception as e:
            print(f"Failed to send log to Discord: {e}")
    
    async def send_webhook(self, payload):
        """Send webhook to Discord"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 204:
                    print(f"Webhook failed: {response.status}")
    
    @staticmethod
    def get_color(level):
        """Get embed color by log level"""
        colors = {
            'DEBUG': 7506394,    # Gray
            'INFO': 3447003,     # Blue
            'WARNING': 16776960, # Yellow
            'ERROR': 16711680,   # Red
            'CRITICAL': 10038562 # Dark Red
        }
        return colors.get(level, 0)
    
    def format_exception(self, exc_info):
        """Format exception for display"""
        import traceback
        return ''.join(traceback.format_exception(*exc_info))

# Setup logging
def setup_logging():
    """Configure logging for production"""
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(name)s: %(message)s'
    )
    console.setFormatter(formatter)
    logger.addHandler(console)
    
    # Discord webhook handler (errors only)
    webhook_url = os.getenv('LOG_WEBHOOK_URL')
    if webhook_url:
        discord = DiscordWebhookHandler(webhook_url, level=logging.ERROR)
        discord.setFormatter(formatter)
        logger.addHandler(discord)
    
    return logger

# Usage in main.py
logger = setup_logging()
```

**Add Environment Variable:**
```env
LOG_WEBHOOK_URL=https://discord.com/api/webhooks/123456/abcdef
LOG_LEVEL=INFO
```

---

### ✅ Phase 6.7 Completion Checklist

**Error Tracking (Sentry):**
- [ ] Sentry account created (2 projects: bot + dashboard)
- [ ] Sentry SDK installed in bot (Python)
- [ ] Sentry SDK installed in API (FastAPI)
- [ ] Sentry SDK installed in dashboard (Next.js)
- [ ] DSN configured in environment variables
- [ ] Test errors sent and visible in Sentry dashboard
- [ ] Sensitive data filtering enabled
- [ ] Release tracking configured

**Uptime Monitoring:**
- [ ] Uptime Robot account created
- [ ] 5 monitors configured (Bot, API, Dashboard, MongoDB, Redis)
- [ ] Health endpoints created in API
- [ ] Alert contacts configured (email + Discord webhook)
- [ ] Public status page created
- [ ] Status page added to website

**Analytics:**
- [ ] Google Analytics 4 account created
- [ ] GA4 installed in Next.js dashboard
- [ ] Measurement ID configured in environment variables
- [ ] Custom event tracking implemented
- [ ] E-commerce tracking for premium purchases
- [ ] Real-time reports working

**Logging:**
- [ ] Discord webhook created for logs
- [ ] Discord webhook handler implemented
- [ ] Logging configured in bot
- [ ] Logging configured in API
- [ ] Error logs sent to Discord channel
- [ ] Log levels configured (INFO for console, ERROR for Discord)

**Verification:**
```bash
# 1. Trigger test error, check Sentry
# 2. Stop bot, check Uptime Robot alert email
# 3. Visit dashboard, check GA4 real-time
# 4. Check Discord #bot-logs channel for logs
```

**Expected Result:** ✅ Comprehensive monitoring covering errors, uptime, analytics, and logs

---

<a id="phase-68-legal-documentation"></a>
## 📜 Phase 6.8: Legal & Documentation

**Status:** 🔲 Not Started  
**Estimated Time:** 2-3 days  
**Priority:** 🟡 Medium (but legally required for EU/US users)

### Current State
- ✅ Bot and dashboard fully functional
- ⏳ Need Terms of Service
- ⏳ Need Privacy Policy
- ⏳ Need Refund Policy
- ⏳ Need Cookie Policy
- ⏳ Need GDPR compliance
- ⏳ Need user agreement

### Why Legal Documents Matter

**Legal Protection:**
- ✅ Protects you from liability
- ✅ Sets clear expectations with users
- ✅ Required for payment processing (Stripe)
- ✅ Required for GDPR compliance (EU users)
- ✅ Required for CCPA compliance (California)

**Business Credibility:**
- ✅ Shows professionalism
- ✅ Builds trust with users
- ✅ Required for bot verification on Discord
- ✅ Required for app stores if you expand

---

### Part A: Terms of Service (ToS)

#### 1. Create Terms of Service

**File:** `dashboard-frontend/app/legal/terms/page.tsx`

```typescript
export default function TermsOfService() {
  return (
    <div className="container mx-auto py-12 px-4 max-w-4xl prose prose-lg">
      <h1>Terms of Service</h1>
      <p className="text-sm text-gray-500">Last Updated: November 1, 2025</p>
      
      <p>
        Welcome to Kingdom-77. By using our Discord bot and web dashboard 
        (collectively, the "Service"), you agree to these Terms of Service ("Terms").
        Please read them carefully.
      </p>

      <h2>1. Acceptance of Terms</h2>
      <p>
        By accessing or using Kingdom-77, you agree to be bound by these Terms. 
        If you disagree with any part of these Terms, you may not use our Service.
      </p>
      <p>
        You must be at least 13 years old (or the minimum age required in your 
        jurisdiction) to use Kingdom-77. By using the Service, you represent and 
        warrant that you meet this age requirement.
      </p>

      <h2>2. Description of Service</h2>
      <p>
        Kingdom-77 is a Discord bot that provides:
      </p>
      <ul>
        <li>Server moderation tools (warnings, mutes, kicks, bans)</li>
        <li>Leveling and XP system with leaderboards</li>
        <li>Support ticket system</li>
        <li>Reaction roles and auto-role assignment</li>
        <li>Premium subscription features (advanced moderation, custom level cards, etc.)</li>
        <li>Web dashboard for server management</li>
        <li>Additional features as described in our documentation</li>
      </ul>

      <h2>3. User Accounts and Security</h2>
      <p>
        To use certain features, you must have a Discord account. You are 
        responsible for:
      </p>
      <ul>
        <li>Maintaining the confidentiality of your Discord account</li>
        <li>All activities that occur under your account</li>
        <li>Notifying us immediately of any unauthorized use</li>
      </ul>
      <p>
        We reserve the right to suspend or terminate accounts that violate 
        these Terms or Discord's Terms of Service.
      </p>

      <h2>4. Premium Subscriptions</h2>
      
      <h3>4.1 Subscription Plans</h3>
      <p>
        Kingdom-77 offers premium subscriptions on a monthly or yearly basis. 
        Pricing and features are displayed on our website and are subject to change.
      </p>

      <h3>4.2 Payment</h3>
      <p>
        Payments are processed securely through Stripe. By subscribing, you 
        authorize us to charge your payment method:
      </p>
      <ul>
        <li>Monthly: On the same day each month</li>
        <li>Yearly: On the anniversary of your subscription</li>
      </ul>

      <h3>4.3 Auto-Renewal</h3>
      <p>
        Subscriptions automatically renew unless canceled before the renewal date. 
        You can cancel anytime from your dashboard.
      </p>

      <h3>4.4 Refunds</h3>
      <p>
        Please see our <a href="/legal/refund">Refund Policy</a> for details on 
        refunds and cancellations.
      </p>

      <h2>5. Acceptable Use</h2>
      <p>You agree NOT to use Kingdom-77 to:</p>
      <ul>
        <li>Violate any laws or regulations</li>
        <li>Violate Discord's Terms of Service or Community Guidelines</li>
        <li>Harass, abuse, or harm other users</li>
        <li>Spam or send unsolicited messages</li>
        <li>Attempt to hack, disrupt, or exploit our Service</li>
        <li>Reverse engineer, decompile, or extract our bot's code</li>
        <li>Use automated scripts or bots to interact with our Service</li>
        <li>Resell or redistribute our Service without permission</li>
        <li>Impersonate others or provide false information</li>
      </ul>
      <p>
        Violation of these rules may result in immediate suspension or termination 
        of your access without refund.
      </p>

      <h2>6. Intellectual Property</h2>
      <p>
        Kingdom-77, including its bot, dashboard, documentation, and all related 
        content, is owned by [Your Name/Company] and protected by intellectual 
        property laws.
      </p>
      <p>
        You are granted a limited, non-exclusive, non-transferable license to use 
        the Service for its intended purpose. This license does not include:
      </p>
      <ul>
        <li>The right to copy, modify, or distribute our code</li>
        <li>The right to create derivative works</li>
        <li>The right to remove copyright notices</li>
      </ul>

      <h2>7. User-Generated Content</h2>
      <p>
        You retain ownership of content you create using Kingdom-77 (server 
        settings, custom commands, etc.). However, you grant us a license to:
      </p>
      <ul>
        <li>Store and process your content to provide the Service</li>
        <li>Create backups for data protection</li>
        <li>Use anonymized data for analytics and improvement</li>
      </ul>
      <p>
        You are responsible for ensuring your content complies with applicable 
        laws and does not infringe on others' rights.
      </p>

      <h2>8. Data and Privacy</h2>
      <p>
        We collect and process data as described in our 
        <a href="/legal/privacy">Privacy Policy</a>. By using Kingdom-77, you 
        consent to such processing.
      </p>

      <h2>9. Disclaimers</h2>
      <p>
        <strong>KINGDOM-77 IS PROVIDED "AS IS" WITHOUT WARRANTIES OF ANY KIND.</strong>
      </p>
      <p>We do not guarantee:</p>
      <ul>
        <li>Uninterrupted or error-free operation</li>
        <li>100% uptime (though we strive for high availability)</li>
        <li>Compatibility with all Discord servers or configurations</li>
        <li>That our Service will meet your specific requirements</li>
        <li>That data will never be lost (though we maintain backups)</li>
      </ul>

      <h2>10. Limitation of Liability</h2>
      <p>
        TO THE MAXIMUM EXTENT PERMITTED BY LAW, KINGDOM-77 AND ITS OPERATORS 
        SHALL NOT BE LIABLE FOR:
      </p>
      <ul>
        <li>Indirect, incidental, special, or consequential damages</li>
        <li>Loss of profits, data, or goodwill</li>
        <li>Service interruptions or errors</li>
        <li>Actions taken by Discord or third parties</li>
        <li>User-generated content or actions</li>
      </ul>
      <p>
        Our total liability shall not exceed the amount you paid us in the 
        past 12 months (or $100 if you haven't paid anything).
      </p>

      <h2>11. Indemnification</h2>
      <p>
        You agree to indemnify and hold harmless Kingdom-77 from any claims, 
        damages, or expenses arising from:
      </p>
      <ul>
        <li>Your use of the Service</li>
        <li>Your violation of these Terms</li>
        <li>Your violation of any third-party rights</li>
        <li>Content you create or share using our Service</li>
      </ul>

      <h2>12. Service Modifications</h2>
      <p>We reserve the right to:</p>
      <ul>
        <li>Modify or discontinue features at any time</li>
        <li>Change pricing with 30 days notice</li>
        <li>Update these Terms (notification required)</li>
        <li>Perform maintenance that temporarily disrupts service</li>
      </ul>
      <p>
        If we make material changes that negatively affect your subscription, 
        you may cancel for a prorated refund.
      </p>

      <h2>13. Termination</h2>
      
      <h3>13.1 By You</h3>
      <p>
        You may stop using Kingdom-77 at any time. To cancel a paid subscription, 
        use the cancellation option in your dashboard.
      </p>

      <h3>13.2 By Us</h3>
      <p>We may suspend or terminate your access if:</p>
      <ul>
        <li>You violate these Terms</li>
        <li>You violate Discord's Terms of Service</li>
        <li>Your payment fails or is disputed</li>
        <li>We're required to do so by law</li>
        <li>We discontinue the Service (with notice)</li>
      </ul>

      <h3>13.3 Effect of Termination</h3>
      <p>Upon termination:</p>
      <ul>
        <li>Your access to premium features ends immediately</li>
        <li>Your data may be deleted after 30 days</li>
        <li>Fees paid are non-refundable except per our Refund Policy</li>
      </ul>

      <h2>14. Dispute Resolution</h2>
      
      <h3>14.1 Governing Law</h3>
      <p>
        These Terms are governed by the laws of [Your Country/State], without 
        regard to conflict of law principles.
      </p>

      <h3>14.2 Arbitration</h3>
      <p>
        Any disputes will be resolved through binding arbitration rather than 
        court, except:
      </p>
      <ul>
        <li>Small claims court disputes (under $10,000)</li>
        <li>Intellectual property disputes</li>
        <li>Disputes where arbitration is prohibited by law</li>
      </ul>

      <h3>14.3 Class Action Waiver</h3>
      <p>
        You agree to resolve disputes individually, not as part of a class action 
        or collective proceeding.
      </p>

      <h2>15. Contact Information</h2>
      <p>
        For questions about these Terms, contact us at:
      </p>
      <ul>
        <li>Email: <a href="mailto:support@kingdom77.com">support@kingdom77.com</a></li>
        <li>Discord: <a href="https://discord.gg/kingdom77">Kingdom-77 Support Server</a></li>
        <li>Website: <a href="https://kingdom77.com">https://kingdom77.com</a></li>
      </ul>

      <h2>16. Miscellaneous</h2>
      
      <h3>16.1 Entire Agreement</h3>
      <p>
        These Terms, along with our Privacy Policy and Refund Policy, constitute 
        the entire agreement between you and Kingdom-77.
      </p>

      <h3>16.2 Severability</h3>
      <p>
        If any provision is found invalid, the remaining provisions remain in effect.
      </p>

      <h3>16.3 No Waiver</h3>
      <p>
        Our failure to enforce any right or provision doesn't waive that right.
      </p>

      <h3>16.4 Assignment</h3>
      <p>
        We may assign these Terms. You may not assign them without our consent.
      </p>

      <h3>16.5 Changes to Terms</h3>
      <p>
        We may update these Terms from time to time. We'll notify you of material 
        changes via:
      </p>
      <ul>
        <li>Email (if provided)</li>
        <li>Discord announcement</li>
        <li>Dashboard notification</li>
        <li>Website banner</li>
      </ul>
      <p>
        Continued use after changes constitutes acceptance of the new Terms.
      </p>

      <hr />
      
      <p className="text-sm text-gray-500">
        <strong>Effective Date:</strong> November 1, 2025
      </p>
      <p className="text-sm text-gray-500">
        <strong>Version:</strong> 1.0
      </p>
    </div>
  );
}
```

**Add Navigation Link:**
File: `dashboard-frontend/components/Footer.tsx`

```typescript
<footer className="bg-gray-900 text-white py-8 mt-20">
  <div className="container mx-auto px-4">
    <div className="grid grid-cols-3 gap-8">
      {/* Legal */}
      <div>
        <h4 className="font-bold mb-4">Legal</h4>
        <ul className="space-y-2">
          <li><a href="/legal/terms" className="hover:text-blue-400">Terms of Service</a></li>
          <li><a href="/legal/privacy" className="hover:text-blue-400">Privacy Policy</a></li>
          <li><a href="/legal/refund" className="hover:text-blue-400">Refund Policy</a></li>
          <li><a href="/legal/cookies" className="hover:text-blue-400">Cookie Policy</a></li>
        </ul>
      </div>
      {/* ... other columns */}
    </div>
  </div>
</footer>
```

---

### Part B: Privacy Policy (GDPR Compliant)

#### 2. Create Privacy Policy

**File:** `dashboard-frontend/app/legal/privacy/page.tsx`

```typescript
export default function PrivacyPolicy() {
  return (
    <div className="container mx-auto py-12 px-4 max-w-4xl prose prose-lg">
      <h1>Privacy Policy</h1>
      <p className="text-sm text-gray-500">Last Updated: November 1, 2025</p>
      
      <p>
        At Kingdom-77, we take your privacy seriously. This Privacy Policy explains 
        how we collect, use, disclose, and protect your information when you use 
        our Discord bot and web dashboard.
      </p>

      <h2>1. Information We Collect</h2>
      
      <h3>1.1 Information from Discord</h3>
      <p>When you use Kingdom-77, we collect:</p>
      <ul>
        <li><strong>User Information:</strong> Discord ID, username, avatar, account creation date</li>
        <li><strong>Server Information:</strong> Server ID, name, icon, member count, roles, channels</li>
        <li><strong>Message Data:</strong> Message content (for moderation), timestamps, channel IDs</li>
        <li><strong>Activity Data:</strong> Commands used, XP earned, level progress, warnings issued</li>
      </ul>

      <h3>1.2 Information You Provide</h3>
      <ul>
        <li><strong>Payment Information:</strong> Processed by Stripe (we don't store card details)</li>
        <li><strong>Configuration Data:</strong> Bot settings, custom commands, auto-mod rules</li>
        <li><strong>Support Messages:</strong> When you contact us for help</li>
      </ul>

      <h3>1.3 Automatically Collected Information</h3>
      <ul>
        <li><strong>Usage Data:</strong> Features used, error logs, performance metrics</li>
        <li><strong>Device Information:</strong> Browser type, OS, IP address (for security)</li>
        <li><strong>Cookies:</strong> See our Cookie Policy for details</li>
      </ul>

      <h2>2. How We Use Your Information</h2>
      <p>We use your information to:</p>
      
      <h3>2.1 Provide the Service</h3>
      <ul>
        <li>Process bot commands and functions</li>
        <li>Store server configurations and user data</li>
        <li>Display leaderboards and statistics</li>
        <li>Send notifications and messages</li>
        <li>Provide customer support</li>
      </ul>

      <h3>2.2 Process Payments</h3>
      <ul>
        <li>Handle premium subscriptions (via Stripe)</li>
        <li>Send payment receipts and invoices</li>
        <li>Manage refunds and billing issues</li>
      </ul>

      <h3>2.3 Improve the Service</h3>
      <ul>
        <li>Analyze usage patterns and statistics (anonymized)</li>
        <li>Fix bugs and errors</li>
        <li>Develop new features</li>
        <li>Optimize performance</li>
      </ul>

      <h3>2.4 Security and Compliance</h3>
      <ul>
        <li>Prevent fraud and abuse</li>
        <li>Enforce our Terms of Service</li>
        <li>Comply with legal obligations</li>
        <li>Respond to law enforcement requests</li>
      </ul>

      <h3>2.5 Communications</h3>
      <ul>
        <li>Send important service updates</li>
        <li>Notify you of changes to Terms or Privacy Policy</li>
        <li>Respond to your inquiries</li>
        <li>Send promotional emails (opt-out available)</li>
      </ul>

      <h2>3. How We Share Your Information</h2>
      <p>We do NOT sell your personal information. We may share data with:</p>

      <h3>3.1 Service Providers</h3>
      <ul>
        <li><strong>Discord:</strong> Required for bot functionality</li>
        <li><strong>Stripe:</strong> Payment processing (PCI-DSS compliant)</li>
        <li><strong>MongoDB Atlas:</strong> Database hosting (encrypted)</li>
        <li><strong>Upstash:</strong> Redis caching (encrypted)</li>
        <li><strong>Vercel/Railway:</strong> Website and bot hosting</li>
        <li><strong>Sentry:</strong> Error tracking (anonymized)</li>
        <li><strong>Google Analytics:</strong> Usage analytics (anonymized)</li>
      </ul>

      <h3>3.2 Legal Requirements</h3>
      <p>We may disclose information if required by law:</p>
      <ul>
        <li>Court orders or subpoenas</li>
        <li>Law enforcement requests</li>
        <li>Protection of our rights or others' safety</li>
        <li>Investigation of Terms violations</li>
      </ul>

      <h3>3.3 Business Transfers</h3>
      <p>
        If Kingdom-77 is acquired or merged, your information may be transferred 
        to the new entity. You'll be notified of such changes.
      </p>

      <h2>4. Data Storage and Security</h2>
      
      <h3>4.1 Where We Store Data</h3>
      <ul>
        <li><strong>Primary Database:</strong> MongoDB Atlas (AWS, US region)</li>
        <li><strong>Cache:</strong> Upstash Redis (US region)</li>
        <li><strong>Files:</strong> Vercel/Railway (US region)</li>
        <li><strong>Backups:</strong> MongoDB Atlas (encrypted, 7-day retention)</li>
      </ul>

      <h3>4.2 Security Measures</h3>
      <p>We protect your data with:</p>
      <ul>
        <li><strong>Encryption:</strong> TLS 1.3 for data in transit, AES-256 for data at rest</li>
        <li><strong>Access Control:</strong> Role-based permissions, 2FA for team accounts</li>
        <li><strong>Monitoring:</strong> 24/7 security monitoring and alerts</li>
        <li><strong>Audits:</strong> Regular security assessments</li>
        <li><strong>Backups:</strong> Daily automated backups with 7-day retention</li>
      </ul>

      <h3>4.3 Data Retention</h3>
      <ul>
        <li><strong>Active Users:</strong> Data retained while you use the service</li>
        <li><strong>Inactive Users:</strong> Data deleted after 1 year of inactivity</li>
        <li><strong>Deleted Accounts:</strong> Data deleted within 30 days</li>
        <li><strong>Backups:</strong> Purged after 90 days</li>
        <li><strong>Legal Holds:</strong> Retained as required by law</li>
      </ul>

      <h2>5. Your Privacy Rights</h2>
      
      <h3>5.1 GDPR Rights (EU Users)</h3>
      <p>If you're in the EU, you have the right to:</p>
      <ul>
        <li><strong>Access:</strong> Request a copy of your data</li>
        <li><strong>Rectification:</strong> Correct inaccurate data</li>
        <li><strong>Erasure:</strong> Request deletion ("right to be forgotten")</li>
        <li><strong>Restriction:</strong> Limit how we process your data</li>
        <li><strong>Portability:</strong> Receive your data in a portable format</li>
        <li><strong>Object:</strong> Object to certain data processing</li>
        <li><strong>Withdraw Consent:</strong> Revoke previously given consent</li>
        <li><strong>Lodge a Complaint:</strong> File a complaint with a supervisory authority</li>
      </ul>

      <h3>5.2 CCPA Rights (California Users)</h3>
      <p>If you're in California, you have the right to:</p>
      <ul>
        <li>Know what personal information we collect</li>
        <li>Know if we sell or share your information (we don't)</li>
        <li>Access your personal information</li>
        <li>Request deletion of your information</li>
        <li>Opt-out of data sales (not applicable - we don't sell)</li>
        <li>Non-discrimination for exercising your rights</li>
      </ul>

      <h3>5.3 How to Exercise Your Rights</h3>
      <p>To exercise any of these rights, contact us at:</p>
      <ul>
        <li>Email: <a href="mailto:privacy@kingdom77.com">privacy@kingdom77.com</a></li>
        <li>Subject line: "Privacy Rights Request"</li>
        <li>Include: Your Discord ID and server ID</li>
      </ul>
      <p>We'll respond within 30 days (GDPR) or 45 days (CCPA).</p>

      <h2>6. Children's Privacy</h2>
      <p>
        Kingdom-77 is not intended for children under 13 (or 16 in the EU). 
        We do not knowingly collect data from children. Discord's minimum age 
        is 13, and we rely on Discord's age verification.
      </p>
      <p>
        If you believe a child under the minimum age is using our service, 
        please contact us immediately at 
        <a href="mailto:privacy@kingdom77.com">privacy@kingdom77.com</a>.
      </p>

      <h2>7. International Data Transfers</h2>
      <p>
        Your data may be transferred to and processed in countries other than 
        your own, including the United States. We ensure adequate protections 
        through:
      </p>
      <ul>
        <li>EU Standard Contractual Clauses (SCCs)</li>
        <li>Adequacy decisions by the European Commission</li>
        <li>Other appropriate safeguards</li>
      </ul>

      <h2>8. Cookies and Tracking</h2>
      <p>
        We use cookies and similar technologies. See our 
        <a href="/legal/cookies">Cookie Policy</a> for detailed information.
      </p>

      <h3>Cookie Summary:</h3>
      <ul>
        <li><strong>Essential Cookies:</strong> Required for login and core functions</li>
        <li><strong>Analytics Cookies:</strong> Google Analytics (anonymized IP)</li>
        <li><strong>Preference Cookies:</strong> Remember your settings</li>
      </ul>
      <p>
        You can control cookies through your browser settings or our cookie consent banner.
      </p>

      <h2>9. Third-Party Links</h2>
      <p>
        Our Service may contain links to third-party websites (Discord, Stripe, etc.). 
        We're not responsible for their privacy practices. Please review their privacy 
        policies separately.
      </p>

      <h2>10. Data Breach Notification</h2>
      <p>
        In the unlikely event of a data breach affecting your personal information, 
        we will:
      </p>
      <ul>
        <li>Notify affected users within 72 hours (GDPR requirement)</li>
        <li>Describe the nature of the breach</li>
        <li>Explain the likely consequences</li>
        <li>Describe measures taken to mitigate harm</li>
        <li>Provide contact information for inquiries</li>
        <li>Notify relevant authorities as required</li>
      </ul>

      <h2>11. Changes to This Privacy Policy</h2>
      <p>
        We may update this Privacy Policy from time to time. We'll notify you of 
        material changes via:
      </p>
      <ul>
        <li>Email (if provided)</li>
        <li>Dashboard notification</li>
        <li>Discord announcement</li>
        <li>Website banner</li>
      </ul>
      <p>
        The "Last Updated" date at the top shows when changes were made. 
        Continued use after changes constitutes acceptance.
      </p>

      <h2>12. Contact Us</h2>
      <p>
        For privacy-related questions or to exercise your rights, contact:
      </p>
      <ul>
        <li><strong>Email:</strong> <a href="mailto:privacy@kingdom77.com">privacy@kingdom77.com</a></li>
        <li><strong>Discord:</strong> <a href="https://discord.gg/kingdom77">Kingdom-77 Support Server</a></li>
        <li><strong>Website:</strong> <a href="https://kingdom77.com">https://kingdom77.com</a></li>
      </ul>
      <p>
        <strong>Data Protection Officer (if required):</strong><br />
        [Your Name/Company]<br />
        [Address]<br />
        [City, State, ZIP]<br />
        [Country]
      </p>

      <hr />
      
      <p className="text-sm text-gray-500">
        <strong>Effective Date:</strong> November 1, 2025
      </p>
      <p className="text-sm text-gray-500">
        <strong>Version:</strong> 1.0
      </p>
      <p className="text-sm text-gray-500">
        <strong>GDPR Compliant:</strong> Yes
      </p>
      <p className="text-sm text-gray-500">
        <strong>CCPA Compliant:</strong> Yes
      </p>
    </div>
  );
}
```

---

### Part C: Refund Policy

#### 3. Create Refund Policy

**File:** `dashboard-frontend/app/legal/refund/page.tsx`

```typescript
export default function RefundPolicy() {
  return (
    <div className="container mx-auto py-12 px-4 max-w-4xl prose prose-lg">
      <h1>Refund Policy</h1>
      <p className="text-sm text-gray-500">Last Updated: November 1, 2025</p>
      
      <p>
        At Kingdom-77, we want you to be satisfied with your Premium subscription. 
        This Refund Policy explains our refund and cancellation procedures.
      </p>

      <h2>1. Refund Eligibility</h2>
      
      <h3>1.1 7-Day Full Refund</h3>
      <p>
        You're eligible for a <strong>full refund</strong> if:
      </p>
      <ul>
        <li>You purchased a Premium subscription within the last 7 days</li>
        <li>This is your first subscription purchase</li>
        <li>You haven't violated our Terms of Service</li>
        <li>You request the refund within 7 days of purchase</li>
      </ul>
      <p className="text-green-600 font-semibold">
        ✅ 100% refund guaranteed - No questions asked!
      </p>

      <h3>1.2 14-Day Partial Refund (50%)</h3>
      <p>
        You're eligible for a <strong>50% refund</strong> if:
      </p>
      <ul>
        <li>You purchased between 8-14 days ago</li>
        <li>You provide a reason for cancellation</li>
        <li>You haven't violated our Terms of Service</li>
      </ul>
      <p className="text-yellow-600 font-semibold">
        ⚠️ 50% refund with reason provided
      </p>

      <h3>1.3 After 14 Days - No Refund</h3>
      <p>
        <strong>No refunds</strong> are provided for:
      </p>
      <ul>
        <li>Subscriptions older than 14 days</li>
        <li>Accounts that violated Terms of Service</li>
        <li>Services already fully consumed</li>
        <li>Change of mind after 14 days</li>
      </ul>
      <p>
        However, you can cancel to prevent future charges. See section 3 below.
      </p>

      <h2>2. How to Request a Refund</h2>
      
      <h3>2.1 Through Dashboard (Recommended)</h3>
      <ol>
        <li>Log in to <a href="https://kingdom77.com/dashboard">your dashboard</a></li>
        <li>Go to <strong>Billing</strong> → <strong>Subscription</strong></li>
        <li>Click <strong>"Request Refund"</strong></li>
        <li>Select reason (optional for 7-day, required for 8-14 day)</li>
        <li>Click <strong>"Submit Refund Request"</strong></li>
      </ol>
      <p>
        ✅ <strong>Automatic approval</strong> for 7-day refunds (processed within 5-10 business days)
      </p>

      <h3>2.2 Via Email</h3>
      <p>
        If you prefer, email us at:
      </p>
      <ul>
        <li><strong>Email:</strong> <a href="mailto:billing@kingdom77.com">billing@kingdom77.com</a></li>
        <li><strong>Subject:</strong> "Refund Request"</li>
        <li><strong>Include:</strong>
          <ul>
            <li>Discord ID</li>
            <li>Server ID (if applicable)</li>
            <li>Purchase date</li>
            <li>Reason for refund (if 8-14 days)</li>
            <li>Payment email used</li>
          </ul>
        </li>
      </ul>
      <p>
        We'll respond within <strong>2 business days</strong>.
      </p>

      <h3>2.3 Processing Time</h3>
      <ul>
        <li><strong>Approval:</strong> Within 2 business days</li>
        <li><strong>Stripe Processing:</strong> 5-10 business days</li>
        <li><strong>Bank Credit:</strong> Depends on your bank (usually 3-7 days)</li>
      </ul>
      <p>
        <strong>Total time:</strong> Up to 15 business days from request to bank credit.
      </p>

      <h2>3. Cancellation Policy</h2>
      
      <h3>3.1 How to Cancel</h3>
      <p>You can cancel your subscription at any time:</p>
      <ol>
        <li>Log in to your dashboard</li>
        <li>Go to <strong>Billing</strong> → <strong>Subscription</strong></li>
        <li>Click <strong>"Cancel Subscription"</strong></li>
        <li>Confirm cancellation</li>
      </ol>

      <h3>3.2 Effect of Cancellation</h3>
      <ul>
        <li>✅ <strong>Immediate effect:</strong> No future charges</li>
        <li>✅ <strong>Access retained:</strong> Keep Premium features until current period ends</li>
        <li>✅ <strong>Data kept:</strong> Your data remains for 30 days after subscription ends</li>
        <li>❌ <strong>No prorated refund:</strong> You paid for the full period, you keep it</li>
      </ul>

      <h3>3.3 Reactivation</h3>
      <p>
        You can resubscribe anytime! Previous settings and data will be restored 
        if you resubscribe within 30 days.
      </p>

      <h2>4. Special Circumstances</h2>
      
      <h3>4.1 Service Outage</h3>
      <p>
        If Kingdom-77 experiences significant downtime (>24 hours), you may be 
        eligible for:
      </p>
      <ul>
        <li>Prorated credit for downtime</li>
        <li>Free extension of subscription</li>
        <li>Full refund (if downtime >72 hours)</li>
      </ul>
      <p>
        We'll automatically issue credits - no request needed!
      </p>

      <h3>4.2 Billing Errors</h3>
      <p>
        If you were charged incorrectly:
      </p>
      <ul>
        <li>Double charge</li>
        <li>Wrong amount</li>
        <li>After cancellation</li>
      </ul>
      <p>
        Contact us immediately at 
        <a href="mailto:billing@kingdom77.com">billing@kingdom77.com</a>. 
        We'll refund the error within 3 business days.
      </p>

      <h3>4.3 Account Termination</h3>
      <p>
        If we terminate your account for Terms violation, 
        <strong>no refund will be issued</strong> for the current period.
      </p>

      <h3>4.4 Price Changes</h3>
      <p>
        If we increase prices:
      </p>
      <ul>
        <li>You'll be notified 30 days in advance</li>
        <li>Your current subscription price is locked until renewal</li>
        <li>You can cancel before renewal to avoid new price</li>
        <li>Canceling for price increase = eligible for prorated refund</li>
      </ul>

      <h2>5. Yearly Subscriptions</h2>
      
      <h3>5.1 Refund Eligibility</h3>
      <p>Yearly subscriptions have the same refund windows:</p>
      <ul>
        <li>7 days: 100% refund</li>
        <li>8-14 days: 50% refund</li>
        <li>After 14 days: No refund (but can cancel to stop auto-renewal)</li>
      </ul>

      <h3>5.2 Cancellation</h3>
      <p>
        If you cancel a yearly subscription:
      </p>
      <ul>
        <li>No prorated refund (you paid for full year)</li>
        <li>Keep Premium features until end of current year</li>
        <li>Won't auto-renew next year</li>
      </ul>

      <h2>6. Payment Disputes / Chargebacks</h2>
      
      <h3>6.1 Please Contact Us First</h3>
      <p>
        ⚠️ Before filing a chargeback with your bank, please contact us first:
      </p>
      <ul>
        <li>We'll resolve most issues within 24-48 hours</li>
        <li>Chargebacks trigger $15 processing fees (charged to you)</li>
        <li>Your account may be suspended during dispute</li>
      </ul>

      <h3>6.2 Chargeback Policy</h3>
      <p>
        If you file a chargeback without contacting us:
      </p>
      <ul>
        <li>Your account is immediately suspended</li>
        <li>Access to Premium features is revoked</li>
        <li>You're responsible for chargeback fee ($15-25)</li>
        <li>Account may be permanently banned for fraudulent chargebacks</li>
      </ul>

      <h3>6.3 Fraudulent Chargebacks</h3>
      <p>
        If a chargeback is filed after services were fully consumed (bad faith), 
        we reserve the right to:
      </p>
      <ul>
        <li>Permanently ban your account</li>
        <li>Report to fraud prevention services</li>
        <li>Pursue legal action for losses</li>
      </ul>

      <h2>7. Refund Methods</h2>
      <p>
        Refunds are issued to the <strong>original payment method</strong>:
      </p>
      <ul>
        <li><strong>Credit/Debit Card:</strong> Refunded via Stripe (5-10 business days)</li>
        <li><strong>PayPal:</strong> Refunded to PayPal account (3-5 business days)</li>
        <li><strong>Other Methods:</strong> Contact support for alternative refund method</li>
      </ul>
      <p>
        We cannot refund to a different payment method than the original purchase.
      </p>

      <h2>8. Exceptions</h2>
      <p>
        This refund policy does not apply to:
      </p>
      <ul>
        <li>Free tier users (no payments made)</li>
        <li>Gifted subscriptions (original purchaser must request refund)</li>
        <li>Promotional trials (already free)</li>
        <li>Services obtained through illegal means</li>
      </ul>

      <h2>9. Contact Us</h2>
      <p>
        For refund questions or requests, contact:
      </p>
      <ul>
        <li><strong>Email:</strong> <a href="mailto:billing@kingdom77.com">billing@kingdom77.com</a></li>
        <li><strong>Discord:</strong> Open a ticket in our <a href="https://discord.gg/kingdom77">support server</a></li>
        <li><strong>Dashboard:</strong> <a href="https://kingdom77.com/support">Submit a support ticket</a></li>
      </ul>
      <p>
        <strong>Response Time:</strong> Within 2 business days (usually much faster!)
      </p>

      <hr />
      
      <p className="text-sm text-gray-500">
        <strong>Effective Date:</strong> November 1, 2025
      </p>
      <p className="text-sm text-gray-500">
        <strong>Version:</strong> 1.0
      </p>
    </div>
  );
}
```

---

### Part D: Cookie Policy

#### 4. Create Cookie Policy

**File:** `dashboard-frontend/app/legal/cookies/page.tsx`

```typescript
export default function CookiePolicy() {
  return (
    <div className="container mx-auto py-12 px-4 max-w-4xl prose prose-lg">
      <h1>Cookie Policy</h1>
      <p className="text-sm text-gray-500">Last Updated: November 1, 2025</p>
      
      <p>
        This Cookie Policy explains how Kingdom-77 uses cookies and similar 
        technologies on our website (https://kingdom77.com).
      </p>

      <h2>1. What Are Cookies?</h2>
      <p>
        Cookies are small text files stored on your device (computer, phone, tablet) 
        when you visit a website. They help websites remember your preferences and 
        improve your experience.
      </p>

      <h2>2. Cookies We Use</h2>
      
      <h3>2.1 Essential Cookies (Required)</h3>
      <p>
        These cookies are necessary for the website to function. You cannot disable 
        them in our cookie consent tool.
      </p>
      
      <table>
        <thead>
          <tr>
            <th>Cookie Name</th>
            <th>Purpose</th>
            <th>Duration</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>session</code></td>
            <td>Keeps you logged in</td>
            <td>30 days</td>
          </tr>
          <tr>
            <td><code>auth_token</code></td>
            <td>Authentication token for dashboard access</td>
            <td>24 hours</td>
          </tr>
          <tr>
            <td><code>csrf_token</code></td>
            <td>Security protection against cross-site attacks</td>
            <td>Session</td>
          </tr>
          <tr>
            <td><code>cookie_consent</code></td>
            <td>Stores your cookie preferences</td>
            <td>1 year</td>
          </tr>
        </tbody>
      </table>

      <h3>2.2 Analytics Cookies (Optional)</h3>
      <p>
        These cookies help us understand how visitors use our website. All data 
        is anonymized.
      </p>
      
      <table>
        <thead>
          <tr>
            <th>Cookie Name</th>
            <th>Provider</th>
            <th>Purpose</th>
            <th>Duration</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>_ga</code></td>
            <td>Google Analytics</td>
            <td>Distinguishes unique users</td>
            <td>2 years</td>
          </tr>
          <tr>
            <td><code>_gid</code></td>
            <td>Google Analytics</td>
            <td>Distinguishes unique users (short-term)</td>
            <td>24 hours</td>
          </tr>
          <tr>
            <td><code>_gat</code></td>
            <td>Google Analytics</td>
            <td>Throttle request rate</td>
            <td>1 minute</td>
          </tr>
          <tr>
            <td><code>__vercel_analytics</code></td>
            <td>Vercel</td>
            <td>Page views and performance metrics</td>
            <td>1 year</td>
          </tr>
        </tbody>
      </table>

      <h3>2.3 Preference Cookies (Optional)</h3>
      <p>
        These cookies remember your choices and preferences.
      </p>
      
      <table>
        <thead>
          <tr>
            <th>Cookie Name</th>
            <th>Purpose</th>
            <th>Duration</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>theme</code></td>
            <td>Remembers dark/light mode preference</td>
            <td>1 year</td>
          </tr>
          <tr>
            <td><code>language</code></td>
            <td>Remembers language preference</td>
            <td>1 year</td>
          </tr>
          <tr>
            <td><code>sidebar_collapsed</code></td>
            <td>Remembers dashboard sidebar state</td>
            <td>Session</td>
          </tr>
        </tbody>
      </table>

      <h3>2.4 Third-Party Cookies</h3>
      <p>
        Some cookies are set by third-party services we use:
      </p>
      <ul>
        <li><strong>Discord:</strong> When you log in via Discord OAuth</li>
        <li><strong>Stripe:</strong> When you visit payment pages</li>
        <li><strong>Google Fonts:</strong> To display custom fonts</li>
      </ul>
      <p>
        These third parties have their own cookie policies. We don't control 
        their cookies.
      </p>

      <h2>3. How We Use Cookies</h2>
      <p>We use cookies to:</p>
      <ul>
        <li><strong>Keep you logged in:</strong> Remember your authentication</li>
        <li><strong>Improve performance:</strong> Load pages faster with cached data</li>
        <li><strong>Analyze usage:</strong> Understand which features are most popular</li>
        <li><strong>Personalize experience:</strong> Remember your preferences</li>
        <li><strong>Enhance security:</strong> Prevent fraud and unauthorized access</li>
      </ul>

      <h2>4. Managing Cookies</h2>
      
      <h3>4.1 Cookie Consent Banner</h3>
      <p>
        When you first visit our website, you'll see a cookie consent banner. 
        You can:
      </p>
      <ul>
        <li><strong>Accept All:</strong> Allow all cookies</li>
        <li><strong>Reject Non-Essential:</strong> Only essential cookies</li>
        <li><strong>Customize:</strong> Choose which categories to enable</li>
      </ul>
      <p>
        You can change your preferences anytime by clicking the 
        <strong>"Cookie Settings"</strong> link in the footer.
      </p>

      <h3>4.2 Browser Settings</h3>
      <p>
        You can also manage cookies through your browser:
      </p>
      <ul>
        <li><strong>Chrome:</strong> Settings → Privacy and Security → Cookies</li>
        <li><strong>Firefox:</strong> Options → Privacy & Security → Cookies</li>
        <li><strong>Safari:</strong> Preferences → Privacy → Cookies</li>
        <li><strong>Edge:</strong> Settings → Cookies and site permissions</li>
      </ul>
      <p>
        ⚠️ <strong>Warning:</strong> Disabling all cookies may break website functionality.
      </p>

      <h3>4.3 Opt-Out Links</h3>
      <ul>
        <li>
          <strong>Google Analytics:</strong> 
          <a href="https://tools.google.com/dlpage/gaoptout">Opt-out browser add-on</a>
        </li>
        <li>
          <strong>Vercel Analytics:</strong> 
          Disable via our cookie consent banner
        </li>
      </ul>

      <h2>5. Do Not Track (DNT)</h2>
      <p>
        We respect "Do Not Track" browser settings. If DNT is enabled:
      </p>
      <ul>
        <li>Analytics cookies are automatically disabled</li>
        <li>Only essential cookies are used</li>
        <li>Third-party tracking is blocked where possible</li>
      </ul>

      <h2>6. Updates to This Policy</h2>
      <p>
        We may update this Cookie Policy from time to time. Changes will be 
        posted on this page with an updated "Last Updated" date.
      </p>
      <p>
        Material changes will be notified via:
      </p>
      <ul>
        <li>Website banner</li>
        <li>Email (if you have an account)</li>
        <li>Discord announcement</li>
      </ul>

      <h2>7. Contact Us</h2>
      <p>
        For questions about cookies, contact:
      </p>
      <ul>
        <li><strong>Email:</strong> <a href="mailto:privacy@kingdom77.com">privacy@kingdom77.com</a></li>
        <li><strong>Discord:</strong> <a href="https://discord.gg/kingdom77">Support Server</a></li>
      </ul>

      <hr />
      
      <p className="text-sm text-gray-500">
        <strong>Effective Date:</strong> November 1, 2025
      </p>
      <p className="text-sm text-gray-500">
        <strong>Version:</strong> 1.0
      </p>
    </div>
  );
}
```

---

### Part E: Cookie Consent Banner

#### 5. Implement Cookie Consent Banner

**File:** `dashboard-frontend/components/CookieConsent.tsx`

```typescript
'use client'

import { useState, useEffect } from 'react'
import { X } from 'lucide-react'

export default function CookieConsent() {
  const [show, setShow] = useState(false)
  const [showDetails, setShowDetails] = useState(false)

  useEffect(() => {
    // Check if user has already consented
    const consent = localStorage.getItem('cookie_consent')
    if (!consent) {
      setShow(true)
    }
  }, [])

  const acceptAll = () => {
    localStorage.setItem('cookie_consent', 'all')
    setShow(false)
    // Enable analytics
    enableAnalytics()
  }

  const rejectNonEssential = () => {
    localStorage.setItem('cookie_consent', 'essential')
    setShow(false)
    // Disable analytics
    disableAnalytics()
  }

  const enableAnalytics = () => {
    // Enable Google Analytics
    if (window.gtag) {
      window.gtag('consent', 'update', {
        analytics_storage: 'granted'
      })
    }
  }

  const disableAnalytics = () => {
    // Disable Google Analytics
    if (window.gtag) {
      window.gtag('consent', 'update', {
        analytics_storage: 'denied'
      })
    }
  }

  if (!show) return null

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 text-white p-6 shadow-2xl z-50 border-t border-gray-700">
      <div className="container mx-auto max-w-6xl">
        {!showDetails ? (
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex-1">
              <h3 className="text-lg font-bold mb-2">🍪 We use cookies</h3>
              <p className="text-sm text-gray-300">
                We use cookies to improve your experience, analyze site traffic, 
                and personalize content. By clicking "Accept All", you consent 
                to our use of cookies.
              </p>
            </div>
            <div className="flex gap-3 flex-wrap">
              <button
                onClick={() => setShowDetails(true)}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm"
              >
                Customize
              </button>
              <button
                onClick={rejectNonEssential}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm"
              >
                Reject Non-Essential
              </button>
              <button
                onClick={acceptAll}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-semibold"
              >
                Accept All
              </button>
            </div>
          </div>
        ) : (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">Cookie Preferences</h3>
              <button
                onClick={() => setShowDetails(false)}
                className="text-gray-400 hover:text-white"
              >
                <X size={24} />
              </button>
            </div>
            
            <div className="space-y-4 mb-6">
              {/* Essential Cookies */}
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked
                  disabled
                  className="mt-1"
                />
                <div className="flex-1">
                  <h4 className="font-semibold">Essential Cookies</h4>
                  <p className="text-sm text-gray-300">
                    Required for the website to function. Cannot be disabled.
                  </p>
                </div>
              </div>

              {/* Analytics Cookies */}
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  id="analytics"
                  defaultChecked
                  className="mt-1"
                />
                <div className="flex-1">
                  <h4 className="font-semibold">Analytics Cookies</h4>
                  <p className="text-sm text-gray-300">
                    Help us understand how visitors use our website (anonymized data).
                  </p>
                </div>
              </div>

              {/* Preference Cookies */}
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  id="preferences"
                  defaultChecked
                  className="mt-1"
                />
                <div className="flex-1">
                  <h4 className="font-semibold">Preference Cookies</h4>
                  <p className="text-sm text-gray-300">
                    Remember your choices (theme, language, etc.).
                  </p>
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <a
                href="/legal/cookies"
                className="text-sm text-blue-400 hover:underline"
              >
                Learn more about cookies
              </a>
              <div className="flex gap-3">
                <button
                  onClick={rejectNonEssential}
                  className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm"
                >
                  Save Preferences
                </button>
                <button
                  onClick={acceptAll}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-semibold"
                >
                  Accept All
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
```

**Add to Layout:**
File: `dashboard-frontend/app/layout.tsx`

```typescript
import CookieConsent from '@/components/CookieConsent'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <CookieConsent />
      </body>
    </html>
  )
}
```

---

### ✅ Phase 6.8 Completion Checklist

**Legal Documents Created:**
- [ ] Terms of Service page (`/legal/terms`)
- [ ] Privacy Policy page (`/legal/privacy`) - GDPR & CCPA compliant
- [ ] Refund Policy page (`/legal/refund`)
- [ ] Cookie Policy page (`/legal/cookies`)
- [ ] All pages linked in footer

**GDPR Compliance:**
- [ ] Data collection disclosed
- [ ] User rights explained (access, deletion, portability)
- [ ] Legal basis for processing
- [ ] Data retention periods specified
- [ ] International data transfers addressed
- [ ] DPO contact information (if required)
- [ ] Cookie consent mechanism

**CCPA Compliance (California):**
- [ ] "Do Not Sell My Personal Information" statement
- [ ] Right to know what data is collected
- [ ] Right to deletion
- [ ] Right to opt-out
- [ ] Non-discrimination policy

**Implementation:**
- [ ] Cookie consent banner implemented
- [ ] Cookie preferences storage (localStorage)
- [ ] Analytics opt-out functionality
- [ ] "Do Not Track" respect
- [ ] Privacy-friendly defaults

**Stripe Requirements:**
- [ ] Terms of Service publicly accessible
- [ ] Refund policy clearly stated
- [ ] Contact information provided
- [ ] Subscription terms explained

**Discord Bot Verification Requirements:**
- [ ] Privacy Policy link in bot description
- [ ] Terms of Service link in bot description
- [ ] Clear data usage explanation
- [ ] User rights documented

**Additional Documents (Optional but Recommended):**
- [ ] Acceptable Use Policy
- [ ] DMCA Copyright Policy
- [ ] Community Guidelines
- [ ] API Terms of Use

**Final Verification:**
```bash
# 1. Check all legal pages load
curl https://kingdom77.com/legal/terms
curl https://kingdom77.com/legal/privacy
curl https://kingdom77.com/legal/refund
curl https://kingdom77.com/legal/cookies

# 2. Verify footer links
# 3. Test cookie consent banner
# 4. Verify analytics opt-out
# 5. Test data deletion request flow
```

**Expected Result:** ✅ Fully compliant with GDPR, CCPA, Stripe, and Discord requirements

---

<a id="post-deployment-checklist"></a>
## ✅ Post-Deployment Checklist

**Use this checklist after completing all 8 phases to verify production readiness.**

### Infrastructure

- [ ] **Stripe Live Mode**
  - [ ] Live API keys configured
  - [ ] Webhooks receiving events
  - [ ] Test payment successful
  - [ ] Subscription creation working
  - [ ] Refund process tested

- [ ] **MongoDB Atlas**
  - [ ] Production cluster running (M2+ recommended)
  - [ ] Automated backups enabled
  - [ ] 25+ indexes created
  - [ ] Connection test passed
  - [ ] Performance monitoring active

- [ ] **Upstash Redis**
  - [ ] Production database created
  - [ ] TLS encryption enabled
  - [ ] Persistence enabled
  - [ ] Cache policies configured
  - [ ] Rate limiting working

- [ ] **Domain & SSL**
  - [ ] Custom domain connected
  - [ ] SSL certificate valid (A+ rating)
  - [ ] HTTPS enforced
  - [ ] All subdomains working (www, api)
  - [ ] DNS propagated globally

### Services

- [ ] **Discord Bot (Railway/Render)**
  - [ ] Bot online and responding
  - [ ] All 100+ commands working
  - [ ] MongoDB connected
  - [ ] Redis connected
  - [ ] Auto-restart configured
  - [ ] Resource usage < 400MB

- [ ] **Dashboard API (Railway/Render)**
  - [ ] API health endpoint responding
  - [ ] OAuth login working
  - [ ] Premium endpoints functional
  - [ ] Database queries optimized
  - [ ] Rate limiting active
  - [ ] CORS configured correctly

- [ ] **Dashboard Frontend (Vercel)**
  - [ ] All pages load without errors
  - [ ] OAuth flow complete
  - [ ] Premium subscription flow working
  - [ ] Mobile responsive
  - [ ] Lighthouse score > 90
  - [ ] No console errors

### Monitoring

- [ ] **Sentry Error Tracking**
  - [ ] Bot errors captured
  - [ ] API errors captured
  - [ ] Dashboard errors captured
  - [ ] Sensitive data filtered
  - [ ] Email alerts configured

- [ ] **Uptime Robot**
  - [ ] 5 monitors configured
  - [ ] Email alerts working
  - [ ] Discord webhook alerts
  - [ ] Public status page created

- [ ] **Google Analytics**
  - [ ] GA4 installed
  - [ ] Real-time tracking working
  - [ ] Custom events firing
  - [ ] E-commerce tracking active

- [ ] **Logs**
  - [ ] Discord webhook receiving logs
  - [ ] Error logs visible
  - [ ] Log levels configured correctly

### Security

- [ ] **Authentication**
  - [ ] Discord OAuth working
  - [ ] JWT tokens secure
  - [ ] Session management working
  - [ ] CSRF protection enabled

- [ ] **API Security**
  - [ ] Rate limiting enforced
  - [ ] CORS properly configured
  - [ ] API keys not exposed
  - [ ] HTTPS everywhere

- [ ] **Data Protection**
  - [ ] Encryption at rest (MongoDB)
  - [ ] Encryption in transit (TLS 1.3)
  - [ ] Backups encrypted
  - [ ] Access controls configured

### Legal & Compliance

- [ ] **Legal Pages Live**
  - [ ] Terms of Service
  - [ ] Privacy Policy (GDPR compliant)
  - [ ] Refund Policy
  - [ ] Cookie Policy

- [ ] **Cookie Consent**
  - [ ] Banner displays on first visit
  - [ ] Preferences saveable
  - [ ] Analytics opt-out working
  - [ ] DNT respected

- [ ] **GDPR Compliance**
  - [ ] Data collection disclosed
  - [ ] User rights documented
  - [ ] Data deletion process
  - [ ] DPO contact (if required)

### Testing

- [ ] **Functional Tests**
  - [ ] User can register/login
  - [ ] User can subscribe to Premium
  - [ ] User can cancel subscription
  - [ ] Bot commands respond
  - [ ] Dashboard loads all data

- [ ] **Performance Tests**
  - [ ] API response time < 200ms
  - [ ] Dashboard loads < 2 seconds
  - [ ] Bot latency < 100ms
  - [ ] Database queries < 50ms

- [ ] **Load Tests (Optional)**
  - [ ] Simulate 100 concurrent users
  - [ ] Check resource usage
  - [ ] Identify bottlenecks
  - [ ] Verify auto-scaling

### Integrations

- [ ] **Discord Integration**
  - [ ] Bot verified (if applicable)
  - [ ] Commands synced globally
  - [ ] Permissions configured
  - [ ] Support server linked

- [ ] **Stripe Integration**
  - [ ] Products created
  - [ ] Prices set
  - [ ] Webhooks tested
  - [ ] Customer portal working

- [ ] **Third-Party APIs**
  - [ ] Social media APIs (if used)
  - [ ] Translation API (if used)
  - [ ] Any other external services

### Documentation

- [ ] **User Documentation**
  - [ ] README.md updated
  - [ ] FEATURES.md complete
  - [ ] Dashboard guides created
  - [ ] Command list published

- [ ] **Technical Documentation**
  - [ ] API documentation (Swagger)
  - [ ] Environment variables documented
  - [ ] Deployment guide complete
  - [ ] Troubleshooting guide

- [ ] **Support Resources**
  - [ ] Support Discord server
  - [ ] FAQ page
  - [ ] Video tutorials (optional)
  - [ ] Contact information visible

### Marketing & Launch

- [ ] **Website Ready**
  - [ ] Landing page polished
  - [ ] Features showcased
  - [ ] Pricing page clear
  - [ ] Call-to-action buttons

- [ ] **Bot Listings**
  - [ ] top.gg listing
  - [ ] discord.bots.gg
  - [ ] discordbotlist.com
  - [ ] Other directories

- [ ] **Social Media**
  - [ ] Twitter/X account
  - [ ] Discord server
  - [ ] Announcement prepared
  - [ ] Screenshots ready

- [ ] **Launch Plan**
  - [ ] Soft launch to beta users
  - [ ] Monitor for issues
  - [ ] Collect feedback
  - [ ] Public launch announcement

---

<a id="rollback-plan"></a>
## 🔄 Rollback Plan

**If something goes wrong in production, follow this plan to quickly revert to a stable state.**

### Emergency Contacts

**Critical Issues (Bot Down, Data Loss, Security Breach):**
- Contact: [Your Name/Team]
- Discord: [Your Discord Username]
- Phone: [Emergency Phone Number]
- Email: [emergency@kingdom77.com]

**Non-Critical Issues (Bugs, Performance):**
- Support: [support@kingdom77.com]
- Discord: [Support Server Invite]

---

### Scenario 1: Bot Crash / Won't Start

**Symptoms:**
- Bot shows offline in Discord
- Railway/Render shows error logs
- Commands not responding

**Quick Fix:**
1. Check Railway/Render logs for error message
2. Verify environment variables are set correctly
3. Check MongoDB connection (IP whitelist)
4. Check Redis connection
5. Restart service manually

**Rollback:**
```bash
# In Railway dashboard
1. Go to Deployments tab
2. Find last working deployment
3. Click "..." → "Redeploy"
4. Wait 2-3 minutes
5. Verify bot is online
```

---

### Scenario 2: Database Connection Lost

**Symptoms:**
- Bot commands return database errors
- Dashboard shows "Failed to load data"
- MongoDB connection timeout

**Quick Fix:**
1. Check MongoDB Atlas status: https://status.mongodb.com
2. Verify connection string in environment variables
3. Check IP whitelist allows 0.0.0.0/0
4. Restart bot/API services

**Rollback:**
```bash
# Temporary: Switch to backup database
MONGODB_URI=mongodb+srv://backup-cluster-uri

# Or restore from backup (last 7 days)
1. MongoDB Atlas → Backups → Snapshots
2. Select snapshot from before issue
3. Restore to new cluster
4. Update MONGODB_URI
5. Restart services
```

---

### Scenario 3: Payment Processing Failure

**Symptoms:**
- Users can't subscribe
- Stripe webhooks failing
- Payment errors in logs

**Quick Fix:**
1. Check Stripe Dashboard for failed events
2. Verify webhook URL is correct
3. Check webhook signing secret
4. Retry failed webhooks manually

**Rollback:**
```bash
# Disable Premium features temporarily
1. Set STRIPE_ENABLED=false in environment
2. Restart API
3. Show maintenance message for Premium
4. Fix Stripe issue
5. Re-enable when fixed
```

---

### Scenario 4: High Error Rate (Sentry Alerts)

**Symptoms:**
- Sentry sends multiple error emails
- Users reporting bugs
- Dashboard showing errors

**Quick Fix:**
1. Check Sentry dashboard for error patterns
2. Identify which deployment introduced errors
3. Check recent code changes
4. Roll back to previous deployment

**Rollback:**
```bash
# Vercel (Dashboard)
1. Go to Deployments
2. Find last stable deployment
3. Click "..." → "Promote to Production"

# Railway (Bot/API)
1. Go to Deployments
2. Click "..." on stable deployment
3. Select "Redeploy"
```

---

### Scenario 5: Performance Degradation

**Symptoms:**
- Slow API responses (>1 second)
- Dashboard takes >5 seconds to load
- Bot commands lag

**Quick Fix:**
1. Check Railway/Render metrics for high CPU/Memory
2. Check MongoDB performance metrics
3. Check Redis connection
4. Restart services to clear memory leaks

**Temporary Scale-Up:**
```bash
# Railway
1. Go to Settings → Resources
2. Increase RAM: 512MB → 1GB
3. Cost increases ~$5-10/month
4. Monitor for 24 hours
5. Downgrade if not needed

# MongoDB
1. Upgrade to M5 cluster ($25/month)
2. Better performance + 5GB storage
3. Downgrade later if issue resolved
```

---

### Scenario 6: Domain/SSL Issues

**Symptoms:**
- Website shows SSL error
- Domain not resolving
- "Not Secure" warning in browser

**Quick Fix:**
1. Check Cloudflare status
2. Verify DNS records are correct
3. Check SSL certificate expiry
4. Clear Cloudflare cache

**Temporary Workaround:**
```bash
# Use temporary subdomain
1. Railway/Vercel provides: xyz.up.railway.app
2. Update Discord OAuth redirect temporarily
3. Announce temporary URL to users
4. Fix main domain issue
5. Revert to main domain
```

---

### Scenario 7: Data Corruption / Loss

**Symptoms:**
- Users report missing data
- Database queries return unexpected results
- Collections empty or corrupted

**Immediate Actions:**
1. **STOP all services immediately** (prevent further corruption)
2. Contact MongoDB support
3. Do NOT make manual database changes

**Recovery:**
```bash
# Restore from backup
1. MongoDB Atlas → Backups
2. Select snapshot from before corruption
3. Restore to new cluster
4. Verify data integrity
5. Update MONGODB_URI to new cluster
6. Test thoroughly before restarting services

# If no backup available
1. Export remaining data
2. Recreate database schema
3. Re-import data
4. Users may need to reconfigure bot
```

---

### Scenario 8: Security Breach

**Symptoms:**
- Unauthorized access detected
- API keys compromised
- Unusual activity in logs

**IMMEDIATE ACTIONS (Do these NOW):**

1. **Rotate ALL credentials:**
```bash
# Discord
- Regenerate bot token
- Regenerate OAuth secret

# MongoDB
- Change database password
- Update connection string

# Redis
- Regenerate Redis password

# Stripe
- Rollover API keys (Stripe dashboard)

# JWT
- Generate new JWT_SECRET
- Invalidates all sessions (users must re-login)
```

2. **Block attacker:**
```bash
# Get attacker's IP from logs
# In Cloudflare:
1. Security → WAF
2. Add IP block rule
3. Block attacker's IP range
```

3. **Notify users:**
```
Subject: Security Notice

We detected unauthorized access to our systems. 
We've taken immediate action to secure your data.

Actions taken:
- All credentials rotated
- Attacker blocked
- Security audit in progress

Required action:
- Please change your Discord password
- Review your server settings

We apologize for the inconvenience.
```

4. **Post-incident:**
```
- Audit all database changes
- Review access logs
- Implement additional security measures
- Consider penetration testing
- Update incident response plan
```

---

### Scenario 9: Hosting Provider Outage

**Symptoms:**
- Railway/Render shows "Service Unavailable"
- All services down simultaneously
- Status page shows outage

**Actions:**
1. Check provider status page:
   - Railway: https://status.railway.app
   - Render: https://status.render.com
   - Vercel: https://vercel-status.com

2. **If extended outage (>2 hours), migrate temporarily:**

**Emergency Migration Plan:**
```bash
# Deploy to backup hosting (prepare in advance)
1. Keep Heroku/DigitalOcean account as backup
2. Have deployment scripts ready
3. Can migrate in 30-60 minutes

# Steps:
1. Create new app on backup platform
2. Copy all environment variables
3. Deploy code
4. Update DNS to point to new host
5. Test thoroughly
6. Announce migration to users
```

---

### Post-Rollback Checklist

After any rollback, verify:

- [ ] Bot is online and responding
- [ ] Dashboard loads correctly
- [ ] API endpoints working
- [ ] Database connected
- [ ] Redis connected
- [ ] Premium features working
- [ ] No errors in Sentry
- [ ] Monitoring shows green status
- [ ] Users can perform all actions

**Then:**
1. Identify root cause of issue
2. Fix in development environment
3. Test thoroughly
4. Deploy fix with monitoring
5. Document incident for future reference

---

<a id="cost-breakdown"></a>
## 💰 Cost Breakdown

**Estimated monthly costs for production deployment:**

### Hosting

| Service | Tier | Cost | Usage |
|---------|------|------|-------|
| **Railway (Bot)** | 512MB RAM | $7-10/month | Bot hosting, always on |
| **Railway (API)** | 512MB RAM | $7-10/month | API hosting, always on |
| **Vercel (Dashboard)** | Free → Pro | $0-20/month | Free: 100GB bandwidth<br/>Pro: Unlimited + Analytics |

**Hosting Subtotal:** $14-40/month

---

### Database & Cache

| Service | Tier | Cost | Storage |
|---------|------|------|---------|
| **MongoDB Atlas** | M0 (Free) | $0 | 512MB - good for <1000 servers |
|  | M2 (Shared) | $9/month | 2GB - good for 1000-5000 servers |
|  | M5 (Dedicated) | $25/month | 5GB - good for 5000+ servers |
| **Upstash Redis** | Free | $0 | 10k commands/day, 256MB |
|  | Pay-as-you-go | $5-20/month | Scales with usage |

**Recommendation for start:** M2 MongoDB ($9) + Free Redis ($0)

**Database Subtotal:** $0-30/month (depending on growth)

---

### Domain & SSL

| Service | Tier | Cost | Notes |
|---------|------|------|-------|
| **Domain (.com)** | Annual | $10-15/year | ~$1.25/month |
| **Cloudflare** | Free | $0 | SSL, CDN, DDoS protection included |

**Domain Subtotal:** ~$1.25/month

---

### Monitoring & Analytics

| Service | Tier | Cost | Features |
|---------|------|------|----------|
| **Sentry** | Free | $0 | 5k events/month |
|  | Team | $26/month | 50k events/month |
| **Uptime Robot** | Free | $0 | 50 monitors, 5-min checks |
|  | Pro | $7/month | 1-min checks, SMS alerts |
| **Google Analytics** | Free | $0 | Unlimited tracking |

**Monitoring Subtotal:** $0-33/month (Free tier sufficient for most)

---

### Payment Processing

| Service | Fees | Cost | Notes |
|---------|------|------|-------|
| **Stripe** | 2.9% + $0.30 | Variable | Per transaction |

**Example:**
- $9.99 Premium Monthly subscription
- Stripe fee: $0.59 (5.9%)
- You receive: $9.40

**Revenue calculation:**
```
10 Premium users × $9.40 = $94/month revenue
- $24 hosting costs
= $70/month profit
```

---

### Total Monthly Cost Estimates

**Scenario 1: Small Bot (<100 servers, <10 Premium)**
```
Railway Bot:        $7
Railway API:        $7
Vercel:             $0 (free tier)
MongoDB M0:         $0 (free tier)
Redis:              $0 (free tier)
Domain:             $1.25
Monitoring:         $0 (free tiers)
---------------------------------
Total:              $15.25/month

Revenue (10 Premium @ $9.40): $94
Profit: $78.75/month
```

**Scenario 2: Medium Bot (1000-5000 servers, 50 Premium)**
```
Railway Bot:        $10
Railway API:        $10
Vercel:             $20 (Pro plan)
MongoDB M2:         $9
Redis Pay-as-go:    $10
Domain:             $1.25
Sentry Team:        $26
---------------------------------
Total:              $86.25/month

Revenue (50 Premium @ $9.40): $470
Profit: $383.75/month
```

**Scenario 3: Large Bot (10000+ servers, 200 Premium)**
```
Railway Bot:        $15 (1GB RAM)
Railway API:        $15 (1GB RAM)
Vercel Pro:         $20
MongoDB M5:         $25
Redis Pay-as-go:    $20
Domain:             $1.25
Sentry Team:        $26
Uptime Robot Pro:   $7
---------------------------------
Total:              $129.25/month

Revenue (200 Premium @ $9.40): $1,880
Profit: $1,750.75/month
```

---

### Cost Optimization Tips

1. **Start Small:**
   - Use free tiers (MongoDB M0, Redis Free, Vercel Free)
   - Total cost: ~$15/month
   - Upgrade as you grow

2. **Monitor Usage:**
   - Railway has pay-per-use after free credit
   - Set budget alerts at $20, $50, $100
   - Scale down unused resources

3. **Annual Savings:**
   - MongoDB: Pay yearly for 2 months free
   - Domain: Buy multi-year for discount
   - Vercel: Annual billing saves 20%

4. **Free Alternatives (Lower Quality):**
   - Heroku → Railway (Heroku killed free tier)
   - MongoDB Atlas M0 (free but limited)
   - Render (has free tier but spins down)
   - fly.io (3 free VMs)

5. **Premium Revenue Covers Costs:**
   - Break even at ~5 Premium users
   - Profit after 10+ Premium users
   - Scale infrastructure with revenue

---

### When to Upgrade

**Upgrade triggers:**

- **MongoDB M0 → M2:**
  - Approaching 512MB storage
  - >1000 servers
  - Slow query performance

- **Redis Free → Paid:**
  - >10k commands/day
  - Need more than 256MB cache
  - Want faster response times

- **Railway 512MB → 1GB:**
  - Memory usage consistently >400MB
  - Bot frequently restarts
  - >5000 servers

- **Vercel Free → Pro:**
  - >100GB bandwidth/month
  - Want advanced analytics
  - Need preview deployment passwords

- **Sentry Free → Team:**
  - >5k errors/month
  - Want more data retention
  - Need team collaboration

---

## 📊 Progress Tracker

| Phase | Status | Estimated | Actual | Completion |
|-------|--------|-----------|--------|------------|
| 6.1 Stripe | ✅ Documented | 1 day | - | 100% |
| 6.2 MongoDB | ✅ Documented | 1 day | - | 100% |
| 6.3 Redis | ✅ Documented | 1 day | - | 100% |
| 6.4 Domain | ✅ Documented | 1 day | - | 100% |
| 6.5 Bot Host | ✅ Documented | 1-2 days | - | 100% |
| 6.6 Dashboard | ✅ Documented | 1-2 days | - | 100% |
| 6.7 Monitoring | ✅ Documented | 2 days | - | 100% |
| 6.8 Legal | ✅ Documented | 2-3 days | - | 100% |

**Overall Progress:** 8/8 phases documented (100%)

---

## 📝 Final Notes

### You're Ready for Production! 🎉

This comprehensive guide covers everything needed to deploy Kingdom-77 Bot to production. Here's what you have:

**✅ Complete Infrastructure:**
- Payment processing (Stripe)
- Production databases (MongoDB + Redis)
- Custom domain with SSL
- 24/7 hosting for bot and dashboard
- Monitoring and error tracking
- Legal compliance (GDPR, CCPA)

**✅ Total Documentation:**
- 3,500+ lines of deployment guide
- Step-by-step instructions for each phase
- Troubleshooting sections
- Rollback plans for emergencies
- Cost breakdowns and optimization tips

**✅ Production Checklist:**
- 100+ verification items
- Security best practices
- Performance targets
- Compliance requirements

---

### Next Steps

1. **Plan Your Timeline:**
   - Set aside 10-15 days for full deployment
   - Or do 1-2 phases per day over 2 weeks
   - Don't rush - test thoroughly

2. **Prepare Accounts:**
   - Create all required accounts (Stripe, MongoDB, etc.)
   - Verify email addresses
   - Set up 2FA for security

3. **Backup Everything:**
   - Export current development data
   - Save all environment variables
   - Document current configuration

4. **Follow the Guide:**
   - Start with Phase 6.1 (Stripe)
   - Complete each phase fully before moving to next
   - Check off items as you go
   - Test after each phase

5. **Soft Launch:**
   - Deploy to production
   - Invite 10-20 beta users
   - Monitor for issues
   - Collect feedback
   - Fix bugs

6. **Public Launch:**
   - After 1-2 weeks of stable beta
   - Submit to bot listing sites
   - Announce on social media
   - Celebrate! 🎉

---

### Support

**Need Help?**
- **Email:** deployment@kingdom77.com
- **Discord:** [Your Support Server]
- **Documentation:** https://docs.kingdom77.com

**Common Questions:**
- "Which hosting provider should I use?" → Railway (easiest)
- "What's the minimum budget?" → $15/month to start
- "How long does deployment take?" → 10-15 days for first time
- "Can I use free tiers?" → Yes! Start free, upgrade as you grow

---

### Good Luck! 🚀

You've built an incredible Discord bot with:
- 🎯 **17 complete systems**
- 🎨 **114+ commands**
- 💎 **Premium subscription system**
- 🌐 **Full-stack web dashboard**
- 📊 **Comprehensive documentation**
- 🔒 **Production-ready security**

Now it's time to share it with the world!

---

**Last Updated:** November 1, 2025  
**Guide Version:** 1.0 (Complete)  
**Status:** ✅ Ready for Production Deployment

# 🗄️ MongoDB Atlas Setup Guide

**Complete guide to set up MongoDB Atlas for Kingdom-77 Bot v4.0**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Create Account](#create-account)
3. [Create Cluster](#create-cluster)
4. [Database Configuration](#database-configuration)
5. [Security Setup](#security-setup)
6. [Connection String](#connection-string)
7. [Collections Setup](#collections-setup)
8. [Indexes Optimization](#indexes-optimization)
9. [Monitoring](#monitoring)
10. [Backup Configuration](#backup-configuration)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**What You'll Get:**
- Free MongoDB Atlas cluster (M0 - 512MB storage)
- Production-ready database
- Automatic backups
- Built-in monitoring
- Global distribution

**Requirements:**
- Google/Email account
- Credit card (for verification only - Free tier available)

**Estimated Time:** 15-20 minutes

---

## 1️⃣ Create Account

### Step 1: Sign Up

1. Go to: https://www.mongodb.com/cloud/atlas/register
2. Sign up with:
   - Google account (recommended)
   - Email + password

### Step 2: Verify Email

- Check your email inbox
- Click verification link
- Complete profile setup

---

## 2️⃣ Create Cluster

### Step 1: Choose Plan

1. Click **"Build a Database"**
2. Select **"Shared"** (FREE)
3. Choose **M0 Sandbox** tier
   - ✅ 512 MB Storage
   - ✅ Shared RAM
   - ✅ FREE Forever

### Step 2: Cloud Provider & Region

**Recommended Configuration:**

| Setting | Value | Why |
|---------|-------|-----|
| **Provider** | AWS | Best performance |
| **Region** | Middle East (Bahrain) `me-south-1` | Closest to Saudi Arabia |
| **Alternative** | Europe (Frankfurt) `eu-central-1` | Good latency |

### Step 3: Cluster Name

```
Cluster Name: kingdom77-production
```

### Step 4: Create Cluster

- Click **"Create Cluster"**
- Wait 3-5 minutes for provisioning

---

## 3️⃣ Database Configuration

### Step 1: Create Database

1. Go to **"Database"** → **"Browse Collections"**
2. Click **"Add My Own Data"**
3. Fill in:
   ```
   Database Name: kingdom77
   Collection Name: guilds
   ```
4. Click **"Create"**

### Step 2: Create Collections

Run these in MongoDB shell or create manually:

```javascript
// 1. Core Collections (13)
use kingdom77
db.createCollection("guilds")
db.createCollection("users")
db.createCollection("settings")
db.createCollection("premium")
db.createCollection("credits")
db.createCollection("transactions")
db.createCollection("levels")
db.createCollection("tickets")
db.createCollection("custom_commands")
db.createCollection("auto_roles")
db.createCollection("welcome_messages")
db.createCollection("logs")
db.createCollection("moderation")

// 2. Phase 5.7 Collections (12)
db.createCollection("giveaways")
db.createCollection("giveaway_settings")
db.createCollection("giveaway_templates")
db.createCollection("application_forms")
db.createCollection("application_submissions")
db.createCollection("auto_messages")
db.createCollection("auto_message_stats")
db.createCollection("social_links")
db.createCollection("social_settings")
db.createCollection("social_limits")
db.createCollection("statistics")
db.createCollection("cache")

// Total: 25+ collections
```

---

## 4️⃣ Security Setup

### Step 1: Database User

1. Go to **"Database Access"**
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Fill in:
   ```
   Username: kingdom77_admin
   Password: [Generate Strong Password - Save it!]
   ```
5. Set privileges:
   - **Built-in Role:** `readWriteAnyDatabase`
   - Or custom role: `Read and write to any database`
6. Click **"Add User"**

### Step 2: Network Access

**Option A: Allow from Anywhere (Development)**

1. Go to **"Network Access"**
2. Click **"Add IP Address"**
3. Click **"Allow Access from Anywhere"**
4. IP: `0.0.0.0/0`
5. Comment: `Development - Allow all`
6. Click **"Confirm"**

**Option B: Specific IPs (Production - Recommended)**

1. Click **"Add IP Address"**
2. Add your server IPs:
   ```
   Server IP: 123.456.789.0
   Comment: Production Server
   ```
3. Add your local IP:
   ```
   Click "Add Current IP Address"
   Comment: Development Machine
   ```

---

## 5️⃣ Connection String

### Step 1: Get Connection String

1. Go to **"Database"** → **"Connect"**
2. Click **"Connect your application"**
3. Select:
   - Driver: **Python**
   - Version: **3.12 or later**
4. Copy connection string:
   ```
   mongodb+srv://kingdom77_admin:<password>@kingdom77-production.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

### Step 2: Update .env File

Replace `<password>` with your actual password:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://kingdom77_admin:YOUR_PASSWORD_HERE@kingdom77-production.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=kingdom77
```

### Step 3: Test Connection

```bash
python -c "from motor.motor_asyncio import AsyncIOMotorClient; import asyncio; asyncio.run(AsyncIOMotorClient('YOUR_CONNECTION_STRING').admin.command('ping'))"
```

Expected output:
```
{'ok': 1.0}
```

---

## 6️⃣ Collections Setup

### Automatic Setup

The bot will create collections automatically on first run.

### Manual Setup (Optional)

If you want to create collections manually with validation:

```javascript
// Giveaways Collection with Schema Validation
db.createCollection("giveaways", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["guild_id", "prize", "winners_count", "end_time"],
      properties: {
        guild_id: { bsonType: "string" },
        prize: { bsonType: "string" },
        winners_count: { bsonType: "int", minimum: 1 },
        end_time: { bsonType: "date" },
        status: { enum: ["active", "ended", "cancelled"] }
      }
    }
  }
})

// Application Forms with Schema
db.createCollection("application_forms", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["guild_id", "title", "questions"],
      properties: {
        guild_id: { bsonType: "string" },
        title: { bsonType: "string" },
        questions: { bsonType: "array" },
        status: { enum: ["open", "closed"] }
      }
    }
  }
})

// Auto-Messages with Schema
db.createCollection("auto_messages", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["guild_id", "trigger", "response"],
      properties: {
        guild_id: { bsonType: "string" },
        trigger: { bsonType: "object" },
        response: { bsonType: "object" },
        enabled: { bsonType: "bool" }
      }
    }
  }
})

// Social Links with Schema
db.createCollection("social_links", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["guild_id", "platform", "url"],
      properties: {
        guild_id: { bsonType: "string" },
        platform: { enum: ["youtube", "twitch", "kick", "twitter", "instagram", "tiktok", "snapchat"] },
        url: { bsonType: "string" },
        enabled: { bsonType: "bool" }
      }
    }
  }
})
```

---

## 7️⃣ Indexes Optimization

### Critical Indexes

Create these indexes for optimal performance:

```javascript
// 1. Guilds Collection
db.guilds.createIndex({ "guild_id": 1 }, { unique: true })
db.guilds.createIndex({ "premium": 1 })

// 2. Users Collection
db.users.createIndex({ "user_id": 1, "guild_id": 1 }, { unique: true })
db.users.createIndex({ "guild_id": 1 })

// 3. Giveaways Collection
db.giveaways.createIndex({ "guild_id": 1 })
db.giveaways.createIndex({ "status": 1 })
db.giveaways.createIndex({ "end_time": 1 })
db.giveaways.createIndex({ "guild_id": 1, "status": 1 })

// 4. Application Forms
db.application_forms.createIndex({ "guild_id": 1 })
db.application_forms.createIndex({ "status": 1 })

// 5. Application Submissions
db.application_submissions.createIndex({ "form_id": 1 })
db.application_submissions.createIndex({ "user_id": 1 })
db.application_submissions.createIndex({ "status": 1 })
db.application_submissions.createIndex({ "guild_id": 1, "status": 1 })

// 6. Auto-Messages
db.auto_messages.createIndex({ "guild_id": 1 })
db.auto_messages.createIndex({ "enabled": 1 })
db.auto_messages.createIndex({ "guild_id": 1, "enabled": 1 })

// 7. Social Links
db.social_links.createIndex({ "guild_id": 1 })
db.social_links.createIndex({ "platform": 1 })
db.social_links.createIndex({ "enabled": 1 })
db.social_links.createIndex({ "guild_id": 1, "platform": 1 })

// 8. Transactions
db.transactions.createIndex({ "user_id": 1 })
db.transactions.createIndex({ "guild_id": 1 })
db.transactions.createIndex({ "created_at": -1 })

// 9. Logs
db.logs.createIndex({ "guild_id": 1 })
db.logs.createIndex({ "timestamp": -1 })
db.logs.createIndex({ "guild_id": 1, "timestamp": -1 })
```

### Create Indexes via Bot

The bot will create these automatically. To verify:

```python
# In main.py or database/__init__.py
async def create_indexes():
    db = motor_client.kingdom77
    
    # Create all indexes
    await db.guilds.create_index("guild_id", unique=True)
    await db.giveaways.create_index([("guild_id", 1), ("status", 1)])
    # ... etc
```

---

## 8️⃣ Monitoring

### Built-in Metrics

1. Go to **"Metrics"** tab
2. Monitor:
   - **Connections:** Current connections
   - **Operations:** Read/Write per second
   - **Network:** Data transferred
   - **Disk Usage:** Storage used

### Alerts Setup

1. Go to **"Alerts"**
2. Create alerts for:
   - High CPU usage (> 80%)
   - High disk usage (> 400MB for M0)
   - Connection spikes
   - Slow queries

### Performance Advisor

1. Go to **"Performance Advisor"**
2. Review:
   - Slow queries
   - Missing indexes
   - Schema suggestions

---

## 9️⃣ Backup Configuration

### Automatic Backups (M0 Free Tier)

⚠️ **M0 does not include automatic backups**

**Workaround: Manual Backups**

#### Option A: mongodump (Recommended)

```bash
# Install MongoDB tools
# Windows: Download from https://www.mongodb.com/try/download/database-tools

# Backup command
mongodump --uri="mongodb+srv://kingdom77_admin:PASSWORD@cluster.mongodb.net/kingdom77" --out=./backup-$(date +%Y%m%d)

# Restore command
mongorestore --uri="mongodb+srv://kingdom77_admin:PASSWORD@cluster.mongodb.net/kingdom77" ./backup-20251101/kingdom77
```

#### Option B: Python Script

```python
# backup_mongodb.py
import subprocess
import datetime
import os

def backup_database():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backups/mongodb_{timestamp}"
    
    uri = os.getenv("MONGODB_URI")
    
    cmd = f'mongodump --uri="{uri}" --out={backup_dir}'
    subprocess.run(cmd, shell=True)
    
    print(f"✅ Backup created: {backup_dir}")

if __name__ == "__main__":
    backup_database()
```

#### Option C: Scheduled Backups (Windows)

```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "python" -Argument "backup_mongodb.py"
$trigger = New-ScheduledTaskTrigger -Daily -At 3AM
Register-ScheduledTask -TaskName "Kingdom77_MongoDB_Backup" -Action $action -Trigger $trigger
```

### Upgrade to Paid Tier (For Auto Backups)

**M10 Cluster ($0.08/hour = ~$57/month):**
- ✅ Automatic backups
- ✅ Point-in-time recovery
- ✅ 10GB storage
- ✅ Better performance

To upgrade:
1. Go to **"Edit Configuration"**
2. Select **M10** tier
3. Confirm upgrade

---

## 🔟 Monitoring

### Database Statistics

```javascript
// Check database size
db.stats()

// Check collection sizes
db.giveaways.stats()
db.application_forms.stats()

// Count documents
db.guilds.countDocuments()
db.giveaways.countDocuments({ status: "active" })
```

### Query Performance

```javascript
// Explain query plan
db.giveaways.find({ guild_id: "123" }).explain("executionStats")

// Find slow queries
db.currentOp({ "active": true, "secs_running": { "$gt": 5 } })
```

---

## 🐛 Troubleshooting

### Issue 1: Connection Timeout

**Problem:** `ServerSelectionTimeoutError`

**Solution:**
1. Check IP whitelist (Network Access)
2. Verify connection string
3. Check firewall settings
4. Try `0.0.0.0/0` for testing

### Issue 2: Authentication Failed

**Problem:** `Authentication failed`

**Solution:**
1. Verify username/password
2. Check user privileges
3. Escape special characters in password:
   ```
   # If password has @, !, etc.
   from urllib.parse import quote_plus
   password = quote_plus("P@ssw0rd!")
   uri = f"mongodb+srv://user:{password}@cluster..."
   ```

### Issue 3: Database Not Found

**Problem:** Database not appearing

**Solution:**
1. Create at least one collection
2. Insert one document
3. Refresh Atlas dashboard

### Issue 4: Out of Storage (M0)

**Problem:** 512MB limit reached

**Solutions:**
1. Delete old logs: `db.logs.deleteMany({ timestamp: { $lt: old_date } })`
2. Archive data to files
3. Upgrade to M10 (10GB)

### Issue 5: Slow Queries

**Problem:** High response time

**Solution:**
1. Check Performance Advisor
2. Create missing indexes
3. Optimize queries
4. Use projection to limit fields

---

## ✅ Verification Checklist

- [ ] Account created and verified
- [ ] M0 cluster created (Middle East region)
- [ ] Database user created with strong password
- [ ] Network access configured (IPs whitelisted)
- [ ] Connection string copied and tested
- [ ] .env file updated with MONGODB_URI
- [ ] Bot connects successfully
- [ ] Collections created automatically
- [ ] Indexes created for performance
- [ ] Monitoring alerts set up
- [ ] Backup strategy implemented

---

## 📊 Expected Performance

**M0 Free Tier:**
- **Queries/sec:** 100-500 (shared)
- **Latency:** 50-200ms (from ME/EU)
- **Storage:** 512MB
- **Connections:** 100 concurrent

**M10 Paid Tier:**
- **Queries/sec:** 10,000+
- **Latency:** 10-50ms
- **Storage:** 10GB
- **Connections:** 1,500 concurrent

---

## 🔗 Useful Links

- **MongoDB Atlas:** https://www.mongodb.com/cloud/atlas
- **Documentation:** https://docs.atlas.mongodb.com/
- **Connection Strings:** https://docs.mongodb.com/manual/reference/connection-string/
- **Motor (Async Python):** https://motor.readthedocs.io/
- **MongoDB Tools:** https://www.mongodb.com/try/download/database-tools

---

## 🆘 Support

**Issues?**
1. Check MongoDB Atlas Status: https://status.mongodb.com/
2. Atlas Documentation: https://docs.atlas.mongodb.com/
3. Kingdom-77 Support: [Your Discord Server]

---

**✅ Setup Complete! Your MongoDB Atlas is ready for production.**

# MongoDB Setup Guide for Kingdom-77 v3.0
# ========================================

## 📚 Table of Contents
1. [Create MongoDB Atlas Account](#1-create-mongodb-atlas-account)
2. [Create Cluster](#2-create-cluster)
3. [Configure Database](#3-configure-database)
4. [Get Connection String](#4-get-connection-string)
5. [Configure Bot](#5-configure-bot)
6. [Run Migration](#6-run-migration)
7. [Test Connection](#7-test-connection)

---

## 1️⃣ Create MongoDB Atlas Account

1. Go to: https://www.mongodb.com/cloud/atlas
2. Click **"Try Free"** or **"Sign Up"**
3. Choose one:
   - Sign up with Google
   - Sign up with Email

4. Fill in your details:
   - First Name
   - Last Name
   - Email
   - Password

5. Complete verification

---

## 2️⃣ Create Cluster

### Step 1: Choose Plan
```
✅ Select: "M0 Sandbox" (FREE FOREVER)
   - 512MB Storage
   - Shared RAM
   - Perfect for development
```

### Step 2: Choose Region
```
✅ Provider: AWS
✅ Region: Choose closest to you
   - Middle East: Bahrain (me-south-1)
   - Europe: Frankfurt (eu-central-1)
   - US: Virginia (us-east-1)
```

### Step 3: Name Your Cluster
```
Cluster Name: kingdom77-cluster
```

### Step 4: Click **"Create Cluster"**
⏳ Wait 3-5 minutes for deployment

---

## 3️⃣ Configure Database

### Step 1: Create Database User

1. Go to: **Database Access** (left sidebar)
2. Click **"Add New Database User"**
3. Fill in:
   ```
   Username: kingdom77_bot
   Password: [Generate Secure Password]
   ```
4. Under **Database User Privileges**:
   ```
   ✅ Select: "Read and write to any database"
   ```
5. Click **"Add User"**

### Step 2: Whitelist IP Address

1. Go to: **Network Access** (left sidebar)
2. Click **"Add IP Address"**
3. Two options:

   **Option A: Allow from Anywhere (Easiest)**
   ```
   IP Address: 0.0.0.0/0
   Comment: Allow all (for development)
   ```

   **Option B: Add Current IP (More Secure)**
   ```
   Click: "Add Current IP Address"
   ```

4. Click **"Confirm"**

---

## 4️⃣ Get Connection String

### Step 1: Connect to Cluster

1. Go to: **Database** (left sidebar)
2. Find your cluster: `kingdom77-cluster`
3. Click **"Connect"**

### Step 2: Choose Connection Method

1. Select: **"Connect your application"**
2. Driver: **Python**
3. Version: **3.12 or later**

### Step 3: Copy Connection String

You'll see something like:
```
mongodb+srv://kingdom77_bot:<password>@kingdom77-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

### Step 4: Replace `<password>`

Replace `<password>` with your actual password:
```
mongodb+srv://kingdom77_bot:YOUR_ACTUAL_PASSWORD@kingdom77-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

⚠️ **Important:** If your password has special characters, URL-encode them:
```
@ = %40
# = %23
$ = %24
% = %25
& = %26
```

---

## 5️⃣ Configure Bot

### Step 1: Update `.env` File

Open `.env` and add your MongoDB URI:

```env
# Discord Bot
DISCORD_TOKEN=your_discord_token_here
BOT_OWNER_ID=your_user_id_here

# MongoDB Atlas
MONGODB_URI=mongodb+srv://kingdom77_bot:YOUR_PASSWORD@kingdom77-cluster.xxxxx.mongodb.net/kingdom77?retryWrites=true&w=majority

# Data Directory
DATA_DIR=data
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `motor==3.3.2` (Async MongoDB driver)
- `pymongo==4.6.1` (MongoDB driver)
- `dnspython==2.4.2` (For MongoDB Atlas)

---

## 6️⃣ Run Migration

### Migrate Existing Data from JSON to MongoDB

```bash
python database/migration.py
```

You should see:
```
============================================================
🚀 Starting Data Migration: JSON → MongoDB
============================================================

📋 Migrating channel settings...
✅ Loaded channels.json: 5 entries
✅ Migrated 5 channels

🛡️  Migrating role settings...
✅ Migrated 3 guilds

⭐ Migrating ratings...
✅ Migrated 10 ratings

🔍 Creating database indexes...
✅ Indexes created successfully

🔍 Verifying migration...
📊 Migration Summary:
   Guilds: 3
   Channels: 5
   Ratings: 10
   Errors: 0

============================================================
✅ Migration Completed Successfully!
============================================================
```

---

## 7️⃣ Test Connection

### Test MongoDB Connection

Create a test file: `test_mongodb.py`

```python
import asyncio
import os
from dotenv import load_dotenv
from database import init_database, close_database, db

async def test():
    load_dotenv()
    mongodb_uri = os.getenv('MONGODB_URI')
    
    print("Connecting to MongoDB...")
    success = await init_database(mongodb_uri)
    
    if success:
        print("✅ Connected successfully!")
        
        # Test query
        guilds = await db.db.guilds.count_documents({})
        channels = await db.db.channels.count_documents({})
        
        print(f"📊 Guilds: {guilds}")
        print(f"📊 Channels: {channels}")
        
        await close_database()
    else:
        print("❌ Connection failed")

asyncio.run(test())
```

Run it:
```bash
python test_mongodb.py
```

Expected output:
```
Connecting to MongoDB...
✅ Connected successfully!
📊 Guilds: 3
📊 Channels: 5
```

---

## 🔧 Troubleshooting

### Error: "ServerSelectionTimeoutError"

**Problem:** Can't connect to MongoDB

**Solutions:**
1. Check your internet connection
2. Verify IP whitelist in Network Access
3. Check connection string in `.env`
4. Ensure password is URL-encoded

### Error: "Authentication failed"

**Problem:** Wrong username or password

**Solutions:**
1. Double-check username in connection string
2. Verify password is correct
3. Check if special characters are URL-encoded
4. Create a new database user if needed

### Error: "dnspython required"

**Problem:** Missing dependency

**Solution:**
```bash
pip install dnspython==2.4.2
```

---

## 📊 MongoDB Compass (GUI Tool)

### Install MongoDB Compass

1. Download: https://www.mongodb.com/try/download/compass
2. Install on your computer
3. Open Compass
4. Paste your connection string
5. Click "Connect"

Now you can:
- ✅ View collections visually
- ✅ Query data easily
- ✅ Edit documents
- ✅ Monitor performance

---

## 🎯 Next Steps

After successful setup:

1. ✅ MongoDB is ready
2. ✅ Data is migrated
3. ✅ Connection tested

Now you can:
- Run the bot with MongoDB
- Add new features using database
- Scale to thousands of servers

---

## 📚 Useful Resources

- [MongoDB Atlas Docs](https://docs.atlas.mongodb.com/)
- [Motor (Async Driver) Docs](https://motor.readthedocs.io/)
- [PyMongo Tutorial](https://pymongo.readthedocs.io/en/stable/tutorial.html)
- [MongoDB Query Language](https://docs.mongodb.com/manual/tutorial/query-documents/)

---

## 💬 Need Help?

If you encounter issues:
1. Check error messages carefully
2. Review this guide step by step
3. Check MongoDB Atlas status page
4. Contact support or community

---

**Last Updated:** October 29, 2025  
**Version:** 3.0.0-dev  
**Guide For:** Kingdom-77 Discord Bot

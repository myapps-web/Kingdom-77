# Quick Start Guide - v3.0 Dev Branch
# =====================================

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- MongoDB Atlas account (free tier available)
- Discord Bot Token

### Step 1: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

**New in v3.0:**
- `motor==3.3.2` - Async MongoDB driver
- `pymongo==4.6.1` - MongoDB Python driver  
- `dnspython==2.4.2` - DNS resolution for MongoDB Atlas

### Step 2: Configure Environment

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your credentials:**
   ```env
   # Discord Bot Token
   DISCORD_TOKEN=your_actual_bot_token_here
   
   # Your Discord User ID (for /owner command)
   BOT_OWNER_ID=your_discord_user_id_here
   
   # MongoDB Connection
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DB_NAME=kingdom77_bot
   ```

### Step 3: Set Up MongoDB Atlas

Follow the comprehensive guide: **[docs/MONGODB_SETUP.md](docs/MONGODB_SETUP.md)**

Quick steps:
1. Create free MongoDB Atlas account
2. Create a cluster (M0 free tier)
3. Create database user
4. Whitelist your IP address
5. Get connection string
6. Update `.env` with connection string

### Step 4: Test Connection

```bash
# Test MongoDB imports
python test_import.py

# Test MongoDB connection
python test_mongodb.py
```

Expected output:
```
✅ Connected to MongoDB successfully!
✅ Database: kingdom77_bot
✅ Collections: guilds (0 documents)
```

### Step 5: Migrate Existing Data (Optional)

If you have existing JSON files:

```bash
# Backup your data first!
mkdir backup
cp data/*.json backup/

# Run migration
python database/migration.py
```

This will migrate:
- `channels.json` → guilds collection (channel settings)
- `allowed_roles.json` + `role_languages.json` → guilds collection (role settings)
- `ratings.json` → ratings collection
- `servers.json` → guilds collection (server tracking)

### Step 6: Start the Bot

```bash
python main.py
```

Expected log messages:
```
✅ MongoDB connection initialized successfully
✅ Loaded X channel configurations
✅ Bot is ready in Y server(s)
```

## 🔍 Verification Checklist

- [ ] `test_import.py` runs without errors
- [ ] `test_mongodb.py` connects successfully
- [ ] Bot starts without MongoDB errors
- [ ] `/owner` command works
- [ ] Translation commands work
- [ ] Data persists after bot restart

## 📊 Monitoring

### Check Database Statistics
```bash
python test_mongodb.py
```

### Check Bot Logs
Watch for these log messages:
- `✅ MongoDB connection initialized successfully` - Database connected
- `✅ Loaded X channel configurations` - Data loaded
- `❌ Failed to initialize MongoDB` - Connection issues

## 🐛 Troubleshooting

### "No module named 'motor'"
```bash
pip install motor==3.3.2 pymongo==4.6.1 dnspython==2.4.2
```

### "ServerSelectionTimeoutError"
- Check your internet connection
- Verify MongoDB Atlas IP whitelist includes your IP
- Confirm connection string is correct in `.env`

### "AuthenticationFailed"
- Verify username and password in connection string
- Check database user permissions in MongoDB Atlas

### "Bot starts but commands don't work"
- Wait 1-2 minutes for Discord to sync commands
- Try `/owner` command first (always available)
- Check bot has proper permissions in your server

## 📚 Documentation

- **MongoDB Setup**: [docs/MONGODB_SETUP.md](docs/MONGODB_SETUP.md)
- **Development Guide**: [DEV_BRANCH_README.md](DEV_BRANCH_README.md)
- **Progress Tracking**: [PHASE1_PROGRESS.md](PHASE1_PROGRESS.md)
- **Main README**: [README.md](README.md)

## 🎯 Current Status

**Phase 1: Database Migration** - In Progress
- ✅ MongoDB infrastructure ready
- ✅ Bot initialization integrated
- ⏳ Data layer migration in progress
- ⏳ Full testing pending

## 💡 Tips

1. **Development Mode**: Use a test Discord server first
2. **Data Backup**: Always backup JSON files before migration
3. **Free Tier Limits**: MongoDB Atlas M0 has 512MB storage
4. **Connection Pooling**: Motor handles connections automatically
5. **Async Operations**: All database operations are async

## 🆘 Need Help?

1. Check [PHASE1_PROGRESS.md](PHASE1_PROGRESS.md) for detailed status
2. Review [docs/MONGODB_SETUP.md](docs/MONGODB_SETUP.md) for MongoDB issues
3. Check Discord bot has all required permissions
4. Verify `.env` file has correct credentials

## 📝 What's Working Now

✅ **MongoDB Connection**: Database initialization in bot startup
✅ **Import System**: All MongoDB modules import correctly  
✅ **Error Handling**: Graceful fallback if MongoDB unavailable
✅ **Backward Compatible**: JSON files still work during transition

## 🔄 What's Next

⏳ **Data Layer Migration**: Replace JSON operations with MongoDB
⏳ **Command Updates**: Ensure all commands use database module
⏳ **Testing**: Comprehensive testing of all features
⏳ **Phase 2**: Redis caching and advanced features

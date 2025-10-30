# Changelog

## [v3.9.0] - 2025-10-30

### ✨ New Features
- **Premium Credits Payment System** 💎
  - Purchase Premium subscriptions using K77 Credits
  - Monthly Premium: 500 ❄️ credits
  - Yearly Premium: 5,000 ❄️ credits (save 1,000)
  - `/premium subscribe payment_method:credits` command
  - Confirmation UI with balance display
  - Dashboard API endpoint: `/api/premium/{guild_id}/subscribe-with-credits`

- **Moyasar Payment Integration** 💳
  - Full integration with Moyasar (Saudi Arabia payment gateway)
  - Support for: مدى، Visa, Mastercard, Apple Pay, STC Pay
  - `payment/moyasar_integration.py` (350+ lines)
  - Webhook automation for automatic credits addition
  - SAR currency support (1 USD = 3.75 SAR)
  - Payment verification and refund support
  - Dashboard endpoint: `/api/credits/webhook/moyasar`

- **Custom Bot Branding Commands** 🎨
  - `/branding setup` - Setup custom bot branding (Premium)
  - `/branding preview` - Preview current branding
  - `/branding status` - View branding settings
  - `/branding reset` - Reset to default
  - Modal UI for easy configuration

### 🔄 Changes
- Updated `premium/premium_system.py` to support Credits payment
- Enhanced `economy/credits_system.py` with Moyasar integration
- Updated Dashboard APIs to support Credits payment for Premium
- Improved error handling across all payment systems
- Enhanced webhook processing for Moyasar events

### 🔧 Technical
- Added `PAYMENT_PROVIDER` environment variable (stripe/moyasar)
- Added Moyasar API keys to `.env`
- Support for multiple payment providers
- Improved webhook signature verification
- Better currency conversion handling

### 📚 Documentation
- Added `docs/PHASE5.6_TASKS_9_10_COMPLETE.md` - Complete guide for Tasks 9 & 10
- Updated TODO.md with Phase 5.6 completion status
- Added Moyasar setup instructions
- Payment integration examples

### 📊 Statistics
- ~915 lines of new code
- 3 new API endpoints
- 4 new Discord commands
- 2 payment gateways (Stripe + Moyasar)
- Total: ~21,900+ lines of code

---

## [v2.8] - 2025-10-28

### ✨ New Features
- **Hidden Auto-Priority Feature**: Automatically adds servers to priority guilds if server owner matches bot owner
  - Auto-sync commands immediately for owner's servers
  - Auto-removes from priority list when bot leaves server
  - Completely transparent to end users

### 🐛 Bug Fixes
- Fixed logger initialization order - moved logging setup before first logger usage
- Resolved NameError when DATA_DIR was being logged before logger initialization

### 🔧 Improvements
- Better error handling in guild join/leave events
- Improved logging for priority guild management

### 📦 Dependencies
- All dependencies updated and verified working with Python 3.13

---

## [v2.7] - 2025-10-28

### ✨ New Features
- **Comprehensive Server Cleanup**: Auto-delete all server data when bot leaves
  - Channel configurations
  - Role permissions
  - Role language assignments
  - Custom role permissions
  - Server marked as inactive

### 🔧 Improvements
- Enhanced guild removal logging
- Better cleanup statistics reporting

---

## [v2.6] - 2025-10-28

### ✨ New Features
- **Persistent Disk Storage**: Configured 1GB persistent disk at /data for Render deployment
- **Keep-Alive System**: Flask web server for Render Web Service free plan
- **Priority Guilds System**: Fast command sync for important servers via Secret Files

### 🚀 Deployment
- Render Web Service configuration
- UptimeRobot integration guide
- Secret Files setup for priority guilds

### 📝 Documentation
- Added RENDER_DEPLOYMENT.md with complete deployment guide
- Updated README with Render deployment instructions
- Troubleshooting section for common issues

### 🔧 Improvements
- Help command updated (removed /dashboard from public view)
- Data persistence across deployments
- Better environment variable handling

---

## [v2.5] - Previous Release

### Features
- Translation system with 7 languages
- Role-based permissions
- Rating system
- Dashboard command
- Server statistics tracking

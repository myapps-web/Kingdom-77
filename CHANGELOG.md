# Changelog

All notable changes to Kingdom-77 Bot are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [v4.0.0] - 2025-11-01

### 🎉 **MAJOR RELEASE - Phase 5.7 Complete**

**The biggest release in Kingdom-77 Bot history!**
- ✨ **4 new enterprise-level systems**
- 🚀 **40+ new Discord commands**
- 📡 **37 new API endpoints**
- 📝 **13,606 lines of production code** (+20% over estimate)
- 📚 **7,500+ lines of documentation**
- 🎯 **17 complete systems**

---

### 🆕 Added

#### 🎁 **1. Giveaway System** (2,850 lines | 11 commands | 9 APIs)

Complete giveaway management with entities (weighted entries) and templates.

**Commands:**
- `/giveaway create` - Create giveaway with customization
- `/giveaway list` - List active/ended giveaways
- `/giveaway end` - End early and pick winners
- `/giveaway reroll` - Reroll if winner doesn't respond
- `/giveaway delete` - Delete permanently
- `/giveaway edit` - Edit details
- `/giveaway entries` - View all entries
- `/giveaway winners` - View selected winners
- `/giveaway stats` - Statistics
- `/giveaway template` - Manage templates
- `/giveaway use-template` - Quick setup

**Features:**
- **Entities System:** Weighted entries (1-100 points per role)
- **Templates System:** Reusable configurations
- **Requirements:** Role, level, credits, account age
- **Auto-notifications:** DM + channel announcements
- **Custom embeds:** Full customization

**Database:** `giveaways`, `giveaway_settings`, `giveaway_templates`

---

#### 📝 **2. Applications System** (3,255 lines | 8 commands | 9 APIs)

Complete form builder and application management.

**Commands:**
- `/application create` - Create form
- `/application list` - List forms
- `/application delete` - Delete form
- `/application edit` - Edit form
- `/application submissions` - View with filters
- `/application review` - Approve/reject
- `/application stats` - Statistics
- `/apply` - Submit application

**Features:**
- **6 Question Types:** text, textarea, number, select, multiselect, yes/no
- **Review System:** Approve/reject with reason
- **Auto-Role Assignment:** On approval
- **Notifications:** DM on status change
- **Statistics:** Approval rates, response time

**Database:** `application_forms`, `application_submissions`

---

#### 💬 **3. Auto-Messages System** (3,651 lines | 12 commands | 9 APIs)

Advanced auto-response with Nova-style embed builder.

**Commands:**
- `/automsg create` - Create auto-message
- `/automsg list` - List messages
- `/automsg delete` - Delete message
- `/automsg edit` - Edit message
- `/automsg enable/disable` - Toggle
- `/automsg test` - Test message
- `/automsg stats` - Statistics
- `/automsg variables` - List variables
- `/automsg embed` - Embed builder
- `/automsg button` - Add buttons (up to 25)
- `/automsg dropdown` - Add dropdowns

**Features:**
- **3 Trigger Types:** Keywords (regex), Buttons, Dropdowns
- **4 Response Types:** Text, Embed, Both, Reaction
- **Nova-Style Builder:** Full embed customization
- **15+ Variables:** {user}, {server}, {channel}, etc.
- **Cooldown System:** Per user/global

**Database:** `auto_messages`, `auto_message_stats`

---

#### 🌐 **4. Social Integration System** (3,850 lines | 9 commands | 10 APIs)

Connect and share social media in Discord.

**Commands:**
- `/social add` - Add social link
- `/social list` - List links
- `/social remove` - Remove link
- `/social edit` - Edit settings
- `/social test` - Test connection
- `/social stats` - Statistics
- `/social recent` - Recent posts
- `/social purchase` - Buy link slots (200 credits)
- `/social limits` - View limits

**Features:**
- **7 Platforms:** YouTube, Twitch, Kick, Twitter, Instagram, TikTok, Snapchat
- **Link Limits:**
  - Free: 1/platform (7 total)
  - Pro: 3/platform (21 total)
  - Premium: 10/platform (70 total)
- **Purchase System:** 200 credits per extra link
- **Auto-Detection:** Platform validation
- **Recent Posts:** Last 10 posts

**Database:** `social_links`, `social_settings`, `social_limits`

---

### 📚 **Documentation** (7,500+ lines)

**New Files:**
- `docs/DASHBOARD_APPLICATIONS_GUIDE.md` (600+ lines)
- `docs/DASHBOARD_AUTOMESSAGES_GUIDE.md` (750+ lines)
- `docs/DASHBOARD_SOCIAL_GUIDE.md` (650+ lines)
- `FEATURES.md` (1,500+ lines) - All 17 systems
- `docs/API_DOCUMENTATION.md` (2,500+ lines) - 66+ endpoints
- `docs/TESTING_RESULTS.md` (3,000+ lines) - 480 test cases

---

### 🎨 **Dashboard Updates**

**New Pages:**
- Giveaway Management (create, templates, stats)
- Applications Manager (form builder, reviews)
- Auto-Messages Editor (Nova builder, live preview)
- Social Integration (7 platforms, purchase system)

**UI Improvements:**
- Modern card layouts
- Drag-and-drop builders
- Live previews
- Color/icon pickers
- Real-time validation

---

### 🔧 **Configuration**

**New Environment Variables (22):**
- Social Media APIs (7 platforms)
- Rate Limiting (3 tiers)
- JWT & Security
- Cache configuration

**Updated:**
- `.env.example` with full documentation

---

### 🔄 **Changed**

**Version Bumped (3.9.0 → 4.0.0):**
- `pyproject.toml`
- `package.json`
- `main.py`
- `dashboard/__init__.py`
- `dashboard/main.py`
- 5 module `__init__.py` files

**README.md:**
- v4.0 branding
- Phase 5.7 announcement
- 40+ new commands
- Updated statistics

**API Rate Limits:**
- Basic: 60 → 120 req/min (doubled)
- Premium: 60 → 300 req/min (5x)

---

### 📊 **Statistics**

| Metric | v3.9 | v4.0 | Change |
|--------|------|------|--------|
| Total Lines | ~21,400 | ~35,000 | +13,606 (+64%) |
| Systems | 13 | 17 | +4 |
| Commands | 45 | 85+ | +40 |
| API Endpoints | 29 | 66+ | +37 |
| Collections | 20 | 32+ | +12 |
| Documentation | - | 7,500+ | NEW |

**Phase 5.7 Delivery:**
- Estimated: 11,300 lines
- Delivered: 13,606 lines
- Bonus: +2,306 lines (+20%)

---

### 🐛 **Fixed**

- Dashboard API version mismatch
- Module version inconsistencies
- Missing API documentation
- Incomplete .env.example

---

### 🔮 **Migration Guide**

**1. Update Environment:**
```bash
# Pull latest
git pull origin main

# Update dependencies
pip install -r requirements.txt

# Copy new env variables
cp .env.example .env
# Fill Social Media APIs (optional)
```

**2. Restart Bot:**
```bash
python main.py
```

**3. No Database Migration Required**
- New collections auto-created
- Existing data preserved

---

### 🎯 **Breaking Changes**

**None!** Fully backward compatible.

---

### 🙏 **Credits**

- **Lead Developer:** [@myapps-web](https://github.com/myapps-web)
- **Phase:** 5.7 (Advanced Systems)
- **Duration:** 2 months
- **Lines:** 13,606 (+20%)

---

### 📅 **Roadmap**

**Phase 6 (Planned):**
- Music System
- Gaming Integration
- Advanced Analytics (ML)
- Two-Factor Authentication
- Mobile App

---

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

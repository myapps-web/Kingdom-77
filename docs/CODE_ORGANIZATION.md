# 🗂️ دليل تنظيم الكود - Kingdom-77 Bot

**آخر تحديث:** 30 أكتوبر 2025  
**الإصدار:** v3.6

---

## 📁 هيكل الملفات المنظم

### 🎯 الملفات الرئيسية

```
Kingdom-77/
│
├── main.py                          # الملف الرئيسي للبوت (5,116 سطر)
│   ├── Bot Initialization
│   ├── Event Handlers (on_ready, on_message, on_member_join, etc.)
│   ├── Context Menu Commands
│   ├── Cogs Loading
│   └── Bot Run
│
├── keep_alive.py                    # Flask server للـ Keep-Alive
│
├── requirements.txt                 # Python Dependencies
│
├── pyproject.toml                   # Project Configuration (uv)
│
├── .env                            # Environment Variables (SECRET)
│   ├── DISCORD_TOKEN
│   ├── MONGODB_URI
│   ├── REDIS_URL
│   ├── STRIPE_SECRET_KEY
│   ├── STRIPE_PUBLISHABLE_KEY
│   ├── STRIPE_WEBHOOK_SECRET
│   └── DASHBOARD_URL
│
└── .env.example                    # Environment Template
```

---

## 🗄️ Database Layer

```
database/
│
├── __init__.py                     # Package Init
│
├── mongodb.py                      # MongoDB Connection & Manager
│   ├── Database Connection Pool
│   ├── Collections Access
│   ├── Error Handling
│   └── Connection Management
│
├── moderation_schema.py            # Moderation Collections
│   ├── Collection: warnings
│   ├── Collection: mod_logs
│   └── Helper Functions
│
├── leveling_schema.py              # Leveling Collections
│   ├── Collection: user_levels
│   ├── Collection: guild_level_config
│   └── XP Calculation Functions
│
├── tickets_schema.py               # Tickets Collections
│   ├── Collection: tickets
│   ├── Collection: ticket_categories
│   ├── Collection: ticket_config
│   └── Status Management
│
├── autoroles_schema.py             # Auto-Roles Collections (400+ سطر)
│   ├── Collection: reaction_roles
│   ├── Collection: level_roles
│   ├── Collection: join_roles
│   ├── Collection: guild_autoroles_config
│   └── Role Assignment Logic
│
├── premium_schema.py               # Premium Collections (615 سطر)
│   ├── Collection: premium_subscriptions
│   ├── Collection: premium_features
│   ├── Collection: payment_history
│   ├── Collection: feature_usage
│   ├── PREMIUM_TIERS Configuration
│   └── Subscription Management
│
└── migration.py                    # Database Migration Tool
    ├── Schema Updates
    ├── Data Migration
    └── Rollback Support
```

**تنظيم Database:**
- كل نظام له schema خاص به
- Collections منفصلة ومنظمة
- Helper functions لكل schema
- Clear naming conventions

---

## 💾 Cache Layer

```
cache/
│
├── __init__.py                     # Package Init
│
└── redis.py                        # Redis Cache Manager
    ├── Redis Connection (Upstash)
    ├── Cache Get/Set/Delete
    ├── TTL Management
    ├── Translation Cache
    ├── Settings Cache
    └── Error Handling
```

**استخدام Cache:**
- Translation caching (60 دقيقة)
- Guild settings caching (30 دقيقة)
- User data caching (15 دقيقة)
- Leaderboard caching (5 دقائق)

---

## 🎮 Systems Layer

```
moderation/
│
├── __init__.py
│
└── mod_system.py                   # Moderation System
    ├── ModerationSystem Class
    ├── Warning Management
    ├── Mute/Unmute
    ├── Kick/Ban/Unban
    ├── Mod Logs
    └── Auto-Moderation

leveling/
│
├── __init__.py
│
└── level_system.py                 # Leveling System (Nova-style)
    ├── LevelingSystem Class
    ├── XP Calculation
    ├── Level Up Logic
    ├── Progress Bar
    ├── Leaderboard
    └── Premium XP Boost

tickets/
│
├── __init__.py
│
└── ticket_system.py                # Tickets System
    ├── TicketSystem Class
    ├── Category Management
    ├── Ticket Creation
    ├── Staff Management
    ├── Transcript System
    └── Ticket Stats

autoroles/
│
├── __init__.py
│
└── autorole_system.py              # Auto-Roles System (600+ سطر)
    ├── AutoRoleSystem Class
    ├── Reaction Roles (3 modes)
    │   ├── toggle (on/off)
    │   ├── unique (one at a time)
    │   └── multiple (stack roles)
    ├── Level Roles
    │   ├── stacking (keep old roles)
    │   └── replacing (remove old)
    ├── Join Roles
    │   ├── all (everyone)
    │   ├── humans (no bots)
    │   └── bots (only bots)
    └── Statistics & Config

premium/
│
├── __init__.py
│
└── premium_system.py               # Premium System (521 سطر)
    ├── PremiumSystem Class
    ├── Stripe Integration
    │   ├── Create Checkout Session
    │   ├── Handle Webhooks
    │   └── Manage Subscriptions
    ├── Feature Access Control
    │   ├── @require_premium decorator
    │   └── @check_limit decorator
    ├── XP Boost System
    ├── Limits & Quotas
    ├── Trial System (7 days)
    ├── Gift System
    ├── Usage Tracking
    └── Auto-cleanup Task
```

**تنظيم Systems:**
- كل نظام في مجلد منفصل
- Class-based architecture
- Clear separation of concerns
- Reusable components

---

## 🔌 Cogs Layer (Commands)

```
cogs/
│
├── __init__.py                     # Cogs Package Init
│
└── cogs/                          # Slash Commands Cogs
    │
    ├── __init__.py
    │
    ├── moderation.py              # Moderation Commands (9 أوامر)
    │   ├── /warn add
    │   ├── /warn remove
    │   ├── /warn list
    │   ├── /mute
    │   ├── /unmute
    │   ├── /kick
    │   ├── /ban
    │   ├── /unban
    │   └── /modlogs
    │
    ├── leveling.py                # Leveling Commands (5 أوامر)
    │   ├── /rank
    │   ├── /leaderboard
    │   ├── /setxp
    │   ├── /setlevel
    │   └── /levelconfig
    │
    ├── tickets.py                 # Tickets Commands (12 أمر)
    │   ├── /ticket setup
    │   ├── /ticket panel
    │   ├── /ticket close
    │   ├── /ticket delete
    │   ├── /ticket add
    │   ├── /ticket remove
    │   ├── /ticket rename
    │   ├── /ticket category add
    │   ├── /ticket category remove
    │   ├── /ticket category list
    │   ├── /ticket config
    │   └── /ticket stats
    │
    ├── autoroles.py               # Auto-Roles Commands (14 أمر)
    │   ├── Reaction Roles (6)
    │   │   ├── /reactionrole create
    │   │   ├── /reactionrole add
    │   │   ├── /reactionrole remove
    │   │   ├── /reactionrole list
    │   │   ├── /reactionrole delete
    │   │   └── /reactionrole refresh
    │   ├── Level Roles (3)
    │   │   ├── /levelrole add
    │   │   ├── /levelrole remove
    │   │   └── /levelrole list
    │   ├── Join Roles (4)
    │   │   ├── /joinrole add
    │   │   ├── /joinrole remove
    │   │   ├── /joinrole list
    │   │   └── /joinrole config
    │   └── General (1)
    │       └── /autoroles config
    │
    ├── premium.py                 # Premium Commands (8 أوامر)
    │   ├── /premium info
    │   ├── /premium subscribe
    │   ├── /premium status
    │   ├── /premium features
    │   ├── /premium trial
    │   ├── /premium cancel
    │   ├── /premium gift
    │   └── /premium billing
    │
    └── translate.py               # Translation System (400+ سطر)
        ├── TranslateCog Class
        ├── Context Menu: "Translate Message"
        ├── TranslationLanguageView (UI)
        ├── Translation Cache (10,000 entries)
        ├── 15+ Languages Support
        └── Role-based Detection
```

**تنظيم Cogs:**
- كل cog في ملف منفصل
- Commands grouped logically
- UI Components integrated
- Error handling per command

---

## 🌐 Web Dashboard

### Backend (FastAPI)

```
dashboard/
│
├── __init__.py
│
├── main.py                        # FastAPI Application Entry
│   ├── App Initialization
│   ├── Middleware (CORS, etc.)
│   ├── Router Registration
│   └── Startup/Shutdown Events
│
├── config.py                      # Dashboard Configuration
│   ├── Discord OAuth2 Config
│   ├── JWT Settings
│   ├── Database URLs
│   └── Environment Variables
│
├── api/                          # API Endpoints (22 endpoints)
│   │
│   ├── __init__.py
│   │
│   ├── auth.py                   # Authentication (4 endpoints)
│   │   ├── GET /api/auth/login
│   │   ├── GET /api/auth/callback
│   │   ├── GET /api/auth/me
│   │   └── POST /api/auth/logout
│   │
│   ├── servers.py                # Servers (4 endpoints)
│   │   ├── GET /api/servers
│   │   ├── GET /api/servers/{guild_id}
│   │   ├── GET /api/servers/{guild_id}/members
│   │   └── GET /api/servers/{guild_id}/channels
│   │
│   ├── stats.py                  # Statistics (4 endpoints)
│   │   ├── GET /api/stats/overview
│   │   ├── GET /api/stats/guild/{guild_id}
│   │   ├── GET /api/stats/leveling/{guild_id}
│   │   └── GET /api/stats/moderation/{guild_id}
│   │
│   ├── moderation.py             # Moderation (3 endpoints)
│   │   ├── GET /api/moderation/{guild_id}/warnings
│   │   ├── GET /api/moderation/{guild_id}/logs
│   │   └── POST /api/moderation/{guild_id}/warn
│   │
│   ├── leveling.py               # Leveling (5 endpoints)
│   │   ├── GET /api/leveling/{guild_id}/leaderboard
│   │   ├── GET /api/leveling/{guild_id}/user/{user_id}
│   │   ├── POST /api/leveling/{guild_id}/setxp
│   │   ├── GET /api/leveling/{guild_id}/config
│   │   └── PATCH /api/leveling/{guild_id}/config
│   │
│   ├── tickets.py                # Tickets (2 endpoints)
│   │   ├── GET /api/tickets/{guild_id}
│   │   └── GET /api/tickets/{guild_id}/stats
│   │
│   └── settings.py               # Settings (3 endpoints)
│       ├── GET /api/settings/{guild_id}
│       ├── PATCH /api/settings/{guild_id}
│       └── POST /api/settings/{guild_id}/reset
│
├── models/                       # Data Models
│   │
│   ├── __init__.py
│   │
│   ├── user.py                   # User Models
│   │   ├── User
│   │   ├── UserProfile
│   │   └── UserSettings
│   │
│   ├── guild.py                  # Guild Models
│   │   ├── Guild
│   │   ├── GuildSettings
│   │   └── GuildStats
│   │
│   └── response.py               # Response Models
│       ├── SuccessResponse
│       ├── ErrorResponse
│       └── PaginatedResponse
│
└── utils/                        # Utilities
    │
    ├── __init__.py
    │
    ├── auth.py                   # Authentication Utils
    │   ├── create_jwt_token()
    │   ├── verify_jwt_token()
    │   └── get_current_user()
    │
    ├── discord.py                # Discord Utils
    │   ├── get_user_guilds()
    │   ├── get_guild_info()
    │   └── check_admin_permissions()
    │
    └── database.py               # Database Utils
        ├── get_guild_settings()
        ├── update_guild_settings()
        └── get_guild_stats()
```

**تنظيم Backend:**
- RESTful API structure
- Clear endpoint organization
- Separate models and utils
- JWT authentication
- Error handling middleware

---

### Frontend (Next.js 14)

```
dashboard-frontend/
│
├── src/
│   │
│   ├── app/                      # App Router (Next.js 14)
│   │   │
│   │   ├── page.tsx             # Landing Page (/)
│   │   │
│   │   ├── layout.tsx           # Root Layout
│   │   │
│   │   ├── auth/                # Authentication
│   │   │   └── callback/
│   │   │       └── page.tsx     # OAuth Callback
│   │   │
│   │   ├── dashboard/           # Main Dashboard
│   │   │   ├── page.tsx         # Dashboard Home
│   │   │   └── layout.tsx       # Dashboard Layout
│   │   │
│   │   └── servers/             # Server Management
│   │       ├── page.tsx         # Servers List
│   │       └── [id]/
│   │           ├── page.tsx     # Server Dashboard
│   │           └── layout.tsx   # Server Layout
│   │
│   ├── components/               # UI Components
│   │   │
│   │   ├── Navbar.tsx           # Navigation Bar
│   │   ├── Footer.tsx           # Footer
│   │   ├── ServerCard.tsx       # Server Card Component
│   │   ├── StatCard.tsx         # Statistics Card
│   │   └── Loading.tsx          # Loading Spinner
│   │
│   ├── lib/                     # Libraries & Utils
│   │   │
│   │   ├── api.ts               # API Client
│   │   │   ├── auth endpoints
│   │   │   ├── servers endpoints
│   │   │   ├── stats endpoints
│   │   │   └── error handling
│   │   │
│   │   └── utils.ts             # Helper Functions
│   │       ├── formatDate()
│   │       ├── formatNumber()
│   │       └── truncateText()
│   │
│   └── styles/                  # Styles
│       └── globals.css          # Global CSS
│
├── public/                      # Static Assets
│   ├── logo.png
│   └── favicon.ico
│
├── tailwind.config.ts           # TailwindCSS Configuration
│
├── tsconfig.json                # TypeScript Configuration
│
├── next.config.js               # Next.js Configuration
│
└── package.json                 # Dependencies
```

**تنظيم Frontend:**
- App Router architecture
- Component-based UI
- TypeScript for type safety
- TailwindCSS for styling
- API client abstraction
- Protected routes

---

## 📝 Documentation

```
docs/
│
├── INDEX.md                     # Documentation Index
│
├── PROJECT_STATUS.md            # حالة المشروع (هذا الملف)
│
├── ROADMAP.md                   # خارطة الطريق
│
├── CODE_ORGANIZATION.md         # تنظيم الكود (هذا الملف)
│
├── guides/                      # أدلة المستخدم
│   │
│   ├── MODERATION_GUIDE.md     # دليل المراقبة (1000+ سطر)
│   │   ├── Commands Overview
│   │   ├── Warning System
│   │   ├── Mute/Kick/Ban
│   │   ├── Mod Logs
│   │   └── Best Practices
│   │
│   ├── LEVELING_GUIDE.md       # دليل الترقية (1000+ سطر)
│   │   ├── XP System
│   │   ├── Level Roles
│   │   ├── Commands
│   │   ├── Leaderboard
│   │   └── Configuration
│   │
│   ├── TICKETS_GUIDE.md        # دليل التذاكر (1000+ سطر)
│   │   ├── Setup Guide
│   │   ├── Categories
│   │   ├── Staff Management
│   │   ├── Transcripts
│   │   └── Advanced Features
│   │
│   ├── AUTOROLES_GUIDE.md      # دليل الأدوار التلقائية (1000+ سطر)
│   │   ├── Reaction Roles
│   │   ├── Level Roles
│   │   ├── Join Roles
│   │   ├── Emoji Guide
│   │   └── Troubleshooting
│   │
│   └── PREMIUM_GUIDE.md        # دليل Premium (1000+ سطر)
│       ├── Premium Tiers
│       ├── Features
│       ├── Subscription
│       ├── Billing
│       └── Developer Guide
│
├── phase1/                      # Phase 1 Documentation
│   └── PHASE1_PROGRESS.md
│
├── phase2/                      # Phase 2 Documentation
│   ├── PHASE2_PLAN.md
│   ├── PHASE2_COMPLETE.md
│   ├── PHASE2_COMPLETE_REDIS.md
│   └── PHASE2_COMPLETE_TICKETS.md
│
├── PHASE3_COMPLETE.md          # Phase 3 Documentation
├── PHASE3_SUMMARY.md
│
├── PHASE4_COMPLETE.md          # Phase 4 Documentation
├── PHASE4_SUMMARY.md
│
├── PREMIUM_UPDATE_SUMMARY.md   # Premium Tiers Update
│
├── DASHBOARD_QUICKSTART.md     # Dashboard Quick Start
│
├── MONGODB_SETUP.md            # MongoDB Setup Guide
│
└── other guides...             # Additional guides
```

**تنظيم Documentation:**
- Comprehensive user guides
- Phase-by-phase progress tracking
- Setup and configuration guides
- API documentation
- Code examples

---

## 🧪 Tests

```
tests/
│
├── check_cogs.py               # Cogs Verification
│
├── mongodb/                    # MongoDB Tests
│   ├── test_mongodb.py
│   ├── test_simple_connection.py
│   ├── test_bot_integration.py
│   ├── test_db_update.py
│   └── test_import.py
│
└── cache/                      # Redis Tests
    ├── test_redis.py
    ├── test_simple_redis.py
    └── test_async_redis.py
```

**تنظيم Tests:**
- Separated by system
- Integration tests
- Connection tests
- Unit tests

---

## ⚙️ Configuration Files

```
Kingdom-77/
│
├── .env                        # Environment Variables (SECRET)
│   ├── DISCORD_TOKEN           # Discord Bot Token
│   ├── MONGODB_URI            # MongoDB Connection String
│   ├── REDIS_URL              # Redis URL (Upstash)
│   ├── REDIS_PASSWORD         # Redis Password
│   ├── STRIPE_SECRET_KEY      # Stripe Secret Key
│   ├── STRIPE_PUBLISHABLE_KEY # Stripe Publishable Key
│   ├── STRIPE_WEBHOOK_SECRET  # Stripe Webhook Secret
│   ├── DASHBOARD_URL          # Dashboard URL
│   ├── DISCORD_CLIENT_ID      # Discord OAuth Client ID
│   ├── DISCORD_CLIENT_SECRET  # Discord OAuth Secret
│   └── JWT_SECRET_KEY         # JWT Secret
│
├── .env.example               # Environment Template
│
├── .gitignore                 # Git Ignore Rules
│   ├── __pycache__/
│   ├── .env
│   ├── *.pyc
│   ├── venv/
│   ├── .venv/
│   └── node_modules/
│
├── requirements.txt           # Python Dependencies
│   ├── discord.py==2.6.4
│   ├── motor==3.3.2
│   ├── pymongo==4.6.1
│   ├── redis==5.0.1
│   ├── stripe==7.3.0
│   ├── fastapi==0.104.1
│   ├── uvicorn==0.24.0
│   ├── PyJWT==2.8.0
│   └── ...more
│
├── pyproject.toml             # Project Configuration (uv)
│   ├── [project]
│   ├── dependencies
│   └── build-system
│
├── render.yaml                # Render Deployment Config
│   ├── services
│   ├── envVars
│   └── buildCommand
│
└── uv.lock                    # UV Lock File
```

**تنظيم Configuration:**
- Environment variables for secrets
- Requirements for dependencies
- Project configuration with uv
- Deployment configs

---

## 📊 إحصائيات تنظيم الكود

### عدد الملفات
- **Python Files:** ~120 ملف
- **TypeScript Files:** ~30 ملف
- **Documentation Files:** ~20 ملف
- **Configuration Files:** ~10 ملفات

### عدد الأسطر
- **Python Code:** ~11,000 سطر
- **TypeScript Code:** ~2,000 سطر
- **Documentation:** ~8,000 سطر
- **Total:** ~21,000 سطر

### تنظيم الكود
- **Cogs:** 6 ملفات (48 أمر)
- **Systems:** 5 أنظمة رئيسية
- **API Endpoints:** 22 endpoint
- **UI Components:** 30+ component

---

## 🎯 معايير تنظيم الكود

### 1. Naming Conventions
```python
# Files: snake_case
moderation_system.py
level_system.py

# Classes: PascalCase
class ModerationSystem:
class LevelingSystem:

# Functions: snake_case
def add_warning():
def calculate_xp():

# Constants: UPPER_SNAKE_CASE
PREMIUM_TIERS = {...}
MAX_WARNINGS = 5
```

### 2. Structure Patterns
```python
# System Pattern
system/
├── __init__.py
└── system_name.py
    ├── System Class
    ├── Helper Functions
    └── Constants

# Cog Pattern
cogs/cogs/
└── feature.py
    ├── Cog Class
    ├── Commands
    ├── UI Components
    └── Error Handlers
```

### 3. Documentation Standards
```python
# Function Documentation
def function_name(param1: type, param2: type) -> return_type:
    """
    وصف مختصر للدالة.
    
    Args:
        param1: وصف المعامل الأول
        param2: وصف المعامل الثاني
    
    Returns:
        وصف القيمة المرجعة
    
    Raises:
        Exception: متى ترفع الاستثناء
    """
```

### 4. Error Handling
```python
# Pattern
try:
    # Code that might fail
    result = await some_operation()
except SpecificException as e:
    logger.error(f"Error: {e}")
    # Handle error gracefully
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    # Fallback handling
```

### 5. Async Patterns
```python
# Always use async/await
async def async_function():
    result = await async_operation()
    return result

# Use asyncio for concurrent operations
import asyncio
results = await asyncio.gather(
    operation1(),
    operation2(),
    operation3()
)
```

---

## 🔍 نصائح للتنقل في الكود

### للعثور على ميزة معينة:

1. **Slash Command:**
   - ابحث في `cogs/cogs/`
   - كل cog يحتوي على أوامر مرتبطة

2. **System Logic:**
   - ابحث في المجلد المناسب (`moderation/`, `leveling/`, etc.)
   - كل نظام له ملف رئيسي واحد

3. **Database Schema:**
   - ابحث في `database/`
   - Schema name يطابق اسم النظام

4. **API Endpoint:**
   - ابحث في `dashboard/api/`
   - كل ملف يحتوي على endpoints مرتبطة

5. **UI Component:**
   - ابحث في `dashboard-frontend/src/components/`
   - أو في `cogs/cogs/` لـ Discord UI components

---

## ✅ قائمة مراجعة تنظيم الكود

### Structure ✅
- [x] منفصل بوضوح إلى layers
- [x] كل نظام في مجلد خاص
- [x] Cogs منظمة حسب الميزة
- [x] Database schemas منفصلة

### Documentation ✅
- [x] كل نظام موثق
- [x] أدلة مستخدم شاملة
- [x] Code comments واضحة
- [x] API documentation (Swagger)

### Code Quality ✅
- [x] Consistent naming conventions
- [x] Error handling في كل مكان
- [x] Async/await patterns
- [x] Type hints (where applicable)

### Testing ✅
- [x] MongoDB tests
- [x] Redis tests
- [x] Cogs verification
- [x] Integration tests

---

## 🎊 الخلاصة

Kingdom-77 Bot v3.6 منظم بشكل احترافي:

✅ **هيكل واضح** - كل شيء في مكانه الصحيح  
✅ **Separation of Concerns** - كل layer مستقل  
✅ **Documentation كاملة** - 8,000+ سطر توثيق  
✅ **Scalable Architecture** - سهل التوسع والصيانة  
✅ **Clean Code** - معايير عالية  
✅ **Professional Grade** - جاهز للإنتاج  

---

**تاريخ الإنشاء:** 30 أكتوبر 2025  
**الإصدار:** v3.6  
**الحالة:** ✅ منظم واحترافي

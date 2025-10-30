# 👑 Kingdom-77 Discord Bot v3.9

بوت Discord متكامل مع 5 أنظمة رئيسية، Web Dashboard، ونظام Premium بـ Stripe Integration.

**Enterprise-level features | 48 أمر | MongoDB + Redis | Premium System**

## 📁 هيكل المشروع / Project Structure

```
Kingdom-77/
│
├── main.py                    # الملف الرئيسي للبوت / Main bot file
├── requirements.txt           # متطلبات البايثون / Python dependencies
├── render.yaml               # إعدادات Render للنشر / Render deployment config
├── priority_guilds.txt       # قائمة السيرفرات المهمة / Priority guilds list
├── .env.example              # مثال لملف المتغيرات / Environment variables example
├── .gitignore               # ملفات Git المستبعدة / Git ignored files
├── pyproject.toml           # إعدادات المشروع / Project settings
│
├── data/                     # ملفات البيانات / Data files (auto-created)
│   ├── channels.json             # إعدادات اللغات للقنوات
│   ├── servers.json              # معلومات السيرفرات المسجلة
│   ├── ratings.json              # تقييمات المستخدمين
│   ├── allowed_roles.json        # الرتب المسموحة
│   ├── role_languages.json       # لغات الرتب الافتراضية
│   ├── role_permissions.json     # صلاحيات الرتب المخصصة
│   └── translation_stats.json    # إحصائيات الترجمة
│
└── docs/                     # الوثائق / Documentation
    ├── README.md                 # دليل الاستخدام
    ├── RATING_SYSTEM.md          # وثائق نظام التقييم
    ├── RATING_SYSTEM_GUIDE.md    # دليل التقييم
    ├── ROLE_MANAGEMENT_SYSTEM.md # وثائق نظام الصلاحيات
    ├── ROLE_LANGUAGES_GUIDE.md   # دليل لغات الرتب
    └── replit.md                 # معلومات Replit
```

## ✨ الميزات الرئيسية / Main Features

### 🛡️ Moderation System
- نظام تحذيرات متقدم (Warning/Mute/Kick/Ban)
- سجلات مراقبة شاملة (Audit Logs)
- 9 أوامر إدارية

### 📊 Leveling System
- نظام XP ومستويات (Nova-style)
- � **Premium XP Boost** (2x multiplier)
- بطاقات مستوى تفاعلية
- لوحات متصدرين
- 5 أوامر

### 🎫 Tickets System
- نظام تذاكر دعم كامل
- � **Unlimited Tickets** (Premium)
- فئات متعددة
- واجهة تفاعلية (Modal, Buttons)
- حفظ النصوص (Transcripts)
- 12 أمر

### 🎭 Auto-Roles System
- Reaction Roles (3 modes)
- Level Roles (تكامل مع Leveling)
- Join Roles (تلقائية)
- 14 أمر

### 💎 Premium System
- 3 خطط اشتراك (Basic, Premium, Enterprise)
- نظام دفع Stripe متكامل
- 10+ Premium Features
- Trial System (7 days)
- Gift System
- 8 أوامر premium

### 🌐 Web Dashboard
- FastAPI Backend (22 API endpoints)
- Next.js 14 Frontend
- Discord OAuth2
- JWT Authentication
- Real-time statistics

### ⚡ Redis Cache (Upstash)
- تخزين مؤقت للإعدادات
- تحسين الأداء
- Distributed caching

## 🚀 التثبيت / Installation

### على Render (موصى به للإنتاج)

1. **اربط المستودع بـ Render:**
   - اذهب إلى [dashboard.render.com](https://dashboard.render.com/)
   - New → Blueprint
   - اختر مستودع `myapps-web/Kingdom-77`

2. **ضبط المتغيرات البيئية:**
   ```
   DISCORD_TOKEN = your_bot_token
   BOT_OWNER_ID = your_discord_user_id
   GUILD_ID = your_server_id (اختياري)
   ```

3. **إضافة ملف السيرفرات المهمة (اختياري):**
   - Dashboard → Secret Files
   - اسم الملف: `priority_guilds.txt`
   - المحتوى: IDs السيرفرات (كل سطر)

4. **النشر:**
   - Render سينشر البوت تلقائياً
   - البوت سيعمل 24/7

### محلياً (للتطوير)

1. **نسخ المستودع:**
```bash
git clone https://github.com/myapps-web/Kingdom-77.git
cd Kingdom-77
```

2. **إنشاء بيئة افتراضية:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. **تثبيت المتطلبات:**
```powershell
pip install -r requirements.txt
```

4. **إعداد المتغيرات:**
- انسخ `.env.example` إلى `.env`
- أضف المتغيرات:
```
DISCORD_TOKEN=YOUR_BOT_TOKEN
BOT_OWNER_ID=YOUR_DISCORD_ID
DEV_MODE=true
DEV_GUILD_ID=YOUR_TEST_SERVER_ID
```

5. **تشغيل البوت:**
```powershell
python main.py
```

## 📝 الأوامر المتاحة / Available Commands (48 commands)

### 🛡️ Moderation System (9 commands)
- `/warn` - تحذير عضو
- `/warnings` - عرض تحذيرات عضو
- `/removewarn` - حذف تحذير
- `/clearwarnings` - حذف جميع التحذيرات
- `/mute` - كتم عضو
- `/unmute` - إلغاء كتم
- `/kick` - طرد عضو
- `/ban` - حظر عضو
- `/modlogs` - عرض سجلات المراقبة

### 📊 Leveling System (5 commands)
- `/rank` - عرض بطاقة المستوى
- `/leaderboard` - لوحة المتصدرين
- `/xp add` - إضافة XP (Admin)
- `/xp remove` - إزالة XP (Admin)
- `/xp reset` - إعادة تعيين XP (Admin)

### 🎫 Tickets System (12 commands)
- `/ticket create` - إنشاء تذكرة
- `/ticket close` - إغلاق تذكرة
- `/ticket add` - إضافة عضو
- `/ticket remove` - إزالة عضو
- `/ticket claim` - المطالبة بتذكرة
- `/ticket transcript` - حفظ نص المحادثة
- `/ticketsetup` - إعداد النظام (Admin)
- `/ticketcategory` - إدارة الفئات (Admin)
- + 4 أوامر إدارية أخرى

### 🎭 Auto-Roles System (14 commands)
- `/reactionrole create` - إنشاء reaction role
- `/reactionrole add` - إضافة رد فعل ورتبة
- `/reactionrole remove` - إزالة رد فعل
- `/reactionrole list` - عرض reaction roles
- `/reactionrole delete` - حذف reaction role
- `/reactionrole refresh` - تحديث الرسالة
- `/levelrole add` - إضافة رتبة للمستوى
- `/levelrole remove` - إزالة رتبة من المستوى
- `/levelrole list` - عرض رتب المستويات
- `/joinrole add` - إضافة رتبة للانضمام
- `/joinrole remove` - إزالة رتبة
- `/joinrole list` - عرض رتب الانضمام
- `/joinrole config` - الإعدادات
- `/autoroles config` - عرض الإحصائيات

### 💎 Premium System (8 commands)
- `/premium info` - عرض الخطط والأسعار
- `/premium subscribe` - الاشتراك في خطة
- `/premium status` - حالة الاشتراك
- `/premium features` - عرض جميع الميزات
- `/premium trial` - تجربة مجانية 7 أيام
- `/premium cancel` - إلغاء الاشتراك
- `/premium gift` - إهداء اشتراك
- `/premium billing` - سجل الفواتير

## 🌐 اللغات المدعومة / Supported Languages

أكثر من 30 لغة مدعومة، منها:

- 🇸🇦 العربية (Arabic) - `ar`
- 🇬🇧 الإنجليزية (English) - `en`
- 🇹🇷 التركية (Turkish) - `tr`
- 🇯🇵 اليابانية (Japanese) - `ja`
- 🇫🇷 الفرنسية (French) - `fr`
- 🇰🇷 الكورية (Korean) - `ko`
- 🇮🇹 الإيطالية (Italian) - `it`
- 🇪🇸 الإسبانية (Spanish) - `es`
- 🇩🇪 الألمانية (German) - `de`
- 🇨🇳 الصينية (Chinese) - `zh-CN`
- 🇷🇺 الروسية (Russian) - `ru`
- 🇵🇹 البرتغالية (Portuguese) - `pt`
- 🇳🇱 الهولندية (Dutch) - `nl`
- 🇵🇱 البولندية (Polish) - `pl`
- 🇮🇳 الهندية (Hindi) - `hi`

استخدم `/listlangs` لعرض القائمة الكاملة

## 🔐 نظام الصلاحيات / Permission System

### الصلاحيات الافتراضية / Default Permissions
- 👑 مالك السيرفر (Server Owner) - صلاحيات كاملة
- 🛡️ الأدمنستريتور (Administrator) - صلاحيات كاملة

### الصلاحيات المخصصة / Custom Permissions
يمكن للأدمنز إضافة رتب مخصصة باستخدام:
- `/addrole` - منح رتبة صلاحية إدارة لغات القنوات
- `/removerole` - سحب الصلاحية من رتبة

### نظام لغات الرتب / Role Language System
ميزة جديدة تسمح بتعيين لغة افتراضية لكل رتبة:
- عند استخدام "Translate Message" يترجم للغة رتبتك
- يدعم رتب متعددة بلغات مختلفة
- راجع [دليل لغات الرتب](docs/ROLE_LANGUAGES_GUIDE.md) للتفاصيل

## 📚 الوثائق / Documentation

### دلائل الأنظمة / System Guides
- [MODERATION_GUIDE.md](docs/MODERATION_GUIDE.md) - دليل نظام الإدارة
- [LEVELING_GUIDE.md](docs/LEVELING_GUIDE.md) - دليل نظام المستويات
- [TICKETS_GUIDE.md](docs/TICKETS_GUIDE.md) - دليل نظام التذاكر
- [AUTOROLES_GUIDE.md](docs/AUTOROLES_GUIDE.md) - دليل نظام الرتب التلقائية
- [PREMIUM_GUIDE.md](docs/PREMIUM_GUIDE.md) - دليل نظام Premium (المستخدمين والمطورين)

### وثائق المراحل / Phase Documentation
- [PHASE2_COMPLETE.md](docs/PHASE2_COMPLETE.md) - ملخص Phase 2 (5 أنظمة)
- [PHASE3_COMPLETE.md](docs/PHASE3_COMPLETE.md) - ملخص Phase 3 (Web Dashboard)
- [PHASE4_COMPLETE.md](docs/PHASE4_COMPLETE.md) - ملخص Phase 4 (Premium System)

### التطوير / Development
- [TODO.md](TODO.md) - قائمة المهام والتحديثات

## 🆕 آخر التحديثات / Latest Updates

### الإصدار 3.6 (2024) - Premium System ✨
- ✅ **Premium System مع Stripe**: 3 خطط اشتراك (Basic, Premium, Enterprise)
- ✅ **8 أوامر premium**: subscribe, trial, gift, billing, features, etc.
- ✅ **10+ Premium Features**: XP Boost, Unlimited Tickets, Custom Cards, etc.
- ✅ **Trial System**: 7-day free trial
- ✅ **Gift System**: إهداء الاشتراكات
- ✅ **Usage Tracking**: تتبع استخدام الميزات
- ✅ **XP Boost Integration**: 2x XP للسيرفرات البريميوم
- ✅ **Unlimited Tickets**: لا حدود للتذاكر (Premium)
- ✅ **Auto-cleanup**: تنظيف الاشتراكات المنتهية تلقائياً
- ✅ **Documentation**: دلائل شاملة للمستخدمين والمطورين

### الإصدار 3.5 - Web Dashboard
- ✅ **FastAPI Backend**: 22 API endpoints
- ✅ **Next.js 14 Frontend**: 5 pages
- ✅ **Discord OAuth2**: تسجيل دخول بحساب Discord
- ✅ **JWT Authentication**: نظام مصادقة آمن
- ✅ **Real-time Statistics**: إحصائيات مباشرة
- ✅ **Responsive Design**: واجهة متجاوبة

### الإصدار 3.0 - Core Systems
- ✅ **5 أنظمة رئيسية**: Moderation, Leveling, Tickets, Auto-Roles, Redis Cache
- ✅ **40 أمر**: أوامر شاملة لجميع الأنظمة
- ✅ **MongoDB Integration**: قاعدة بيانات متقدمة
- ✅ **Redis Cache (Upstash)**: تخزين مؤقت للأداء
- ✅ **UI Components**: Modals, Buttons, Selects
- ✅ **Documentation**: 4 دلائل شاملة

## 🔒 ملاحظات أمان / Security Notes

- ⚠️ لا ترفع توكن البوت إلى المستودع العام
- ✅ استخدم متغيرات البيئة أو Secrets على Replit
- 📁 ملفات البيانات محمية في `.gitignore`
- 🔐 نظام صلاحيات متقدم يحمي الأوامر الإدارية

## 💎 خطط Premium / Premium Plans

| Tier | Monthly | Yearly | Features |
|------|---------|--------|----------|
| **🆓 Basic (Free)** | Free | Free | Unlimited Level Roles, Unlimited Tickets, Advanced Dashboard, Priority Support |
| **💎 Premium** | $9.99 | $99.99 | **All Basic +** XP Boost (2x), Custom Cards, Advanced Automod, API Access, Unlimited Commands & Roles |

**🎁 Trial:** 7-day free trial available for Premium
**✨ XP Boost & Custom Level Cards:** Exclusive to Premium tier

## ⚡ الأداء / Performance

- � **MongoDB + Redis**: قاعدة بيانات عالية الأداء مع تخزين مؤقت
- 💾 **Redis Caching**: تخزين مؤقت للإعدادات والبيانات المتكررة
- 📊 **Optimized Queries**: استعلامات محسّنة للأداء
- 🎯 **استجابة فورية**: معظم الأوامر تنفذ في أقل من ثانية
- ⚡ **Async Operations**: معالجة غير متزامنة لجميع العمليات
- 🔄 **Auto-cleanup Tasks**: تنظيف تلقائي للبيانات القديمة

## 🤝 المساهمة / Contributing

المساهمات مرحب بها! يرجى:
1. Fork المستودع
2. إنشاء فرع للميزة الجديدة
3. Commit التغييرات
4. Push إلى الفرع
5. إنشاء Pull Request

## 📄 الترخيص / License

هذا المشروع مفتوح المصدر ومتاح للاستخدام الشخصي والتعليمي.

## 🆘 الدعم / Support

للمساعدة أو الإبلاغ عن مشاكل:
- افتح Issue في GitHub
- راجع الوثائق في مجلد `docs/`

---

## 📊 إحصائيات المشروع / Project Statistics

- **Lines of Code**: ~13,000+ lines
- **Systems**: 5 major systems (Moderation, Leveling, Tickets, Auto-Roles, Premium)
- **Commands**: 48 slash commands
- **API Endpoints**: 22 RESTful endpoints
- **UI Components**: 30+ interactive components
- **Documentation**: 6 comprehensive guides
- **Premium Features**: 10+ premium-only features
- **Collections**: 15+ MongoDB collections
- **Technologies**: Python, Discord.py, MongoDB, Redis, FastAPI, Next.js, Stripe

## 🛠️ التقنيات المستخدمة / Technologies Used

### Backend
- **Python 3.13**: Programming language
- **discord.py 2.6.4**: Discord API library
- **MongoDB (motor)**: Database
- **Redis (Upstash)**: Cache
- **Stripe 7.3.0**: Payment processing
- **FastAPI**: RESTful API

### Frontend (Dashboard)
- **Next.js 14**: React framework
- **TypeScript**: Type safety
- **TailwindCSS 4**: Styling
- **Discord OAuth2**: Authentication

### Infrastructure
- **MongoDB Atlas**: Cloud database
- **Upstash Redis**: Cloud Redis
- **Stripe**: Payment gateway

---

## 👑 Kingdom-77 Bot v3.9

**Enterprise-level Discord bot with premium features**

تم التطوير بواسطة [myapps-web](https://github.com/myapps-web)

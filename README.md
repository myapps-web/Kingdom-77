# 👑 Kingdom-77 Discord Bot v4.0 🎉

بوت Discord متكامل واحترافي مع **17 نظاماً**، Web Dashboard متطور، وميزات Premium حصرية.

**Enterprise-level | 85+ أمر | 66+ API | MongoDB + Redis | 30+ لغة | ~35,000+ سطر كود**

---

## 🎊 **NEW IN v4.0 - Phase 5.7 Complete!**

✨ **4 أنظمة جديدة ثورية بإجمالي 13,606 سطر!**

- 🎁 **Giveaway System** - نظام جوائز احترافي مع قوالب وجدولة تلقائية (11 أمر)
- 📝 **Applications System** - نظام طلبات بـ 6 أنواع أسئلة ومراجعة احترافية (8 أوامر)
- 💬 **Auto-Messages System** - ردود تلقائية ذكية بـ Nova-style embed builder (12 أمر)
- 🌐 **Social Integration** - ربط 7 منصات (YouTube, Twitch, Kick, Twitter, Instagram, TikTok, Snapchat) (9 أوامر)

📊 **Dashboard Upgrade:** 3 صفحات جديدة مع Nova UI System

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

### � **NEW! Giveaway System** (Phase 5.7)
- **نظام جوائز احترافي** مع قوالب جاهزة
- **جدولة تلقائية** للجوائز المستقبلية
- **متطلبات مخصصة** (رتب، مستويات، أعمار حسابات)
- **11 أمر كامل**: create, start, end, reroll, list, delete, templates
- **لوحة تحكم** Dashboard لإدارة الجوائز

### 📝 **NEW! Applications System** (Phase 5.7)
- **6 أنواع أسئلة**: Text, TextArea, Number, Select, MultiSelect, YesNo
- **نظام مراجعة احترافي** بـ Approve/Reject
- **إعطاء رتب تلقائياً** عند القبول
- **8 أوامر**: create, edit, delete, list, questions, review, stats
- **Dashboard UI** مع Nova-style forms

### 💬 **NEW! Auto-Messages System** (Phase 5.7)
- **3 أنواع triggers**: Keyword, Button, Dropdown
- **4 أنواع ردود**: Text, Embed, Both, Reaction
- **Nova-style Embed Builder** مع Live Preview
- **نظام Variables** متقدم (15+ variable)
- **12 أمر**: create, edit, delete, list, toggle, test, stats

### 🌐 **NEW! Social Integration** (Phase 5.7)
- **7 منصات مدعومة**: YouTube 📺, Twitch 🎮, Kick ⚡, Twitter 🐦, Instagram 📷, TikTok 🎵, Snapchat 👻
- **نشر تلقائي** للمحتوى الجديد في Discord
- **نظام شراء روابط** (200 ❄️ per link)
- **9 أوامر**: social add, remove, list, toggle, test, limits, purchase, posts
- **Dashboard Timeline** لآخر المنشورات

---

### �🌍 Translation System
- ترجمة تلقائية لـ **30+ لغة**
- ترجمة ثنائية اللغة للقنوات
- ترجمة بالريأكشن
- 8 أوامر ترجمة

### 🛡️ Moderation System
- نظام تحذيرات متقدم (19 أمر)
- AutoMod ذكي بدون AI
- سجلات مراقبة شاملة
- Kick/Ban/Timeout/Mute

### 📊 Leveling System
- نظام XP ومستويات (Nova-style)
- 💎 **Premium XP Boost** (2x)
- بطاقات مستوى مخصصة
- لوحات متصدرين
- 3 أوامر + API

### 🎫 Tickets System
- تذاكر دعم احترافية
- 💎 **Unlimited Tickets** (Premium)
- فئات متعددة + UI تفاعلية
- حفظ المحادثات (Transcripts)
- 6 أوامر

### 🎭 Auto-Roles System
- Reaction Roles (3 أوضاع)
- Level Roles + Join Roles
- تكامل مع المستويات
- 5 أوامر

### 💰 Economy System
- نظام اقتصادي متكامل (19 أمر)
- متجر + مخزون + بنك
- ألعاب قمار (Slots/Coinflip/Dice)
- وظائف وجرائم
- مكافآت يومية وأسبوعية

### 🏠 Welcome System
- بطاقات ترحيب مخصصة
- 4 تصاميم + Captcha
- رسائل ترحيب تلقائية
- أدوار تلقائية

### 📝 Logging System
- 8 أنواع سجلات
- تصدير السجلات
- تجاهل قنوات/أعضاء
- 8 أوامر

### ✨ Custom Commands
- أوامر مخصصة بلا حدود (Premium)
- Auto-responses ذكية
- Variables + Embeds
- إحصائيات الاستخدام

### 💎 Premium System
- 3 خطط (Basic/Premium/Enterprise)
- Stripe + Moyasar
- 15+ ميزات حصرية
- نظام تجربة وهدايا

### 🌐 Web Dashboard
- FastAPI Backend **(66+ API)**
- Next.js 14 Frontend + **Nova UI**
- Discord OAuth2
- **8 صفحات كاملة** مع إحصائيات فورية

### ⚡ Performance
- MongoDB + Redis caching
- Async operations
- **~35,000 سطر كود محسّن**
- مُحسّن للسيرفرات الكبيرة

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

## 📝 الأوامر المتاحة / Available Commands (85+ commands)

### 🎁 **NEW! Giveaway System (11 commands)** ⭐
- `/giveaway create` - إنشاء جائزة جديدة
- `/giveaway start` - بدء جائزة
- `/giveaway end` - إنهاء جائزة مبكراً
- `/giveaway reroll` - إعادة اختيار الفائزين
- `/giveaway list` - عرض جميع الجوائز
- `/giveaway cancel` - إلغاء جائزة
- `/giveaway delete` - حذف جائزة
- `/giveaway template save` - حفظ قالب
- `/giveaway template load` - تحميل قالب
- `/giveaway template list` - عرض القوالب
- `/giveaway stats` - إحصائيات الجوائز

### 📝 **NEW! Applications System (8 commands)** ⭐
- `/application create` - إنشاء نموذج طلب
- `/application edit` - تعديل نموذج
- `/application delete` - حذف نموذج
- `/application list` - عرض النماذج
- `/application question add` - إضافة سؤال
- `/application question edit` - تعديل سؤال
- `/application review` - مراجعة الطلبات
- `/application stats` - إحصائيات النماذج

### � **NEW! Auto-Messages System (12 commands)** ⭐
- `/automessage create` - إنشاء رسالة تلقائية
- `/automessage edit` - تعديل رسالة
- `/automessage delete` - حذف رسالة
- `/automessage list` - عرض الرسائل
- `/automessage toggle` - تفعيل/تعطيل رسالة
- `/automessage test` - اختبار رسالة
- `/automessage trigger add` - إضافة trigger
- `/automessage response edit` - تعديل الرد
- `/automessage variables` - عرض المتغيرات
- `/automessage stats` - إحصائيات الرسائل
- `/automessage export` - تصدير الإعدادات
- `/automessage import` - استيراد الإعدادات

### 🌐 **NEW! Social Integration (9 commands)** ⭐
- `/social add` - إضافة رابط منصة
- `/social remove` - حذف رابط
- `/social list` - عرض الروابط
- `/social toggle` - تفعيل/تعطيل رابط
- `/social test` - اختبار رابط
- `/social limits` - عرض حدود الروابط
- `/social purchase` - شراء خانة إضافية
- `/social posts` - عرض آخر المنشورات
- `/social stats` - إحصائيات المنصات

---

### �🛡️ Moderation System (9 commands)
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

**⚡ Plus:** 18+ أمر إضافي للترجمة، الاقتصاد، الترحيب، السجلات، والأوامر المخصصة

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

### 🆕 **v4.0 Dashboard Guides** (Phase 5.7)
- [DASHBOARD_APPLICATIONS_GUIDE.md](docs/DASHBOARD_APPLICATIONS_GUIDE.md) - دليل نظام الطلبات الشامل
- [DASHBOARD_AUTOMESSAGES_GUIDE.md](docs/DASHBOARD_AUTOMESSAGES_GUIDE.md) - دليل الرسائل التلقائية
- [DASHBOARD_SOCIAL_GUIDE.md](docs/DASHBOARD_SOCIAL_GUIDE.md) - دليل ربط المنصات الاجتماعية

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
- **[PHASE5_COMPLETE.md](docs/PHASE5_COMPLETE.md)** - ملخص Phase 5.7 (4 أنظمة جديدة)

### التطوير / Development
- [TODO.md](TODO.md) - خارطة الطريق الكاملة
- [TESTING_RESULTS.md](docs/TESTING_RESULTS.md) - نتائج الاختبارات (480 test case)

## 🆕 آخر التحديثات / Latest Updates

### 🎉 الإصدار 4.0 (نوفمبر 2025) - Phase 5.7 Complete! **BREAKTHROUGH**

**أكبر تحديث في تاريخ المشروع - 13,606 سطر من الكود عالي الجودة!**

#### 🎁 **Giveaway System** (2,850 سطر)
- ✅ نظام جوائز احترافي مع قوالب جاهزة (Premium Templates)
- ✅ جدولة تلقائية للجوائز المستقبلية
- ✅ متطلبات مخصصة (رتب، مستويات، أعمار حسابات)
- ✅ 11 أمر كامل + 9 API endpoints
- ✅ Dashboard UI مع Nova-style cards

#### 📝 **Applications System** (3,255 سطر)
- ✅ 6 أنواع أسئلة (Text, TextArea, Number, Select, MultiSelect, YesNo)
- ✅ نظام مراجعة احترافي بـ Approve/Reject
- ✅ إعطاء رتب تلقائياً عند القبول
- ✅ 8 أوامر + 9 API endpoints
- ✅ Dashboard UI مع Nova-style forms

#### 💬 **Auto-Messages System** (3,651 سطر)
- ✅ 3 أنواع triggers: Keyword, Button, Dropdown
- ✅ 4 أنواع ردود: Text, Embed, Both, Reaction
- ✅ Nova-style Embed Builder مع Live Preview
- ✅ نظام Variables متقدم (15+ variable)
- ✅ 12 أمر + 9 API endpoints

#### 🌐 **Social Integration** (3,850 سطر)
- ✅ 7 منصات: YouTube, Twitch, Kick, Twitter, Instagram, TikTok, Snapchat
- ✅ نشر تلقائي للمحتوى الجديد في Discord
- ✅ نظام شراء روابط (200 ❄️ per link)
- ✅ 9 أوامر + 10 API endpoints
- ✅ Dashboard Timeline لآخر المنشورات

#### 📊 **Statistics**
- ✨ **إجمالي Phase 5.7:** 13,606 سطر
- ✨ **إجمالي المشروع:** ~35,000 سطر
- ✨ **أوامر جديدة:** +40 أمر (85+ إجمالي)
- ✨ **APIs جديدة:** +37 endpoint (66+ إجمالي)
- ✨ **Dashboard Pages:** +3 صفحات (8 صفحات إجمالي)

---

### الإصدار 3.6 (2024) - Premium System ✨
- ✅ **Premium System مع Stripe**: 3 خطط اشتراك
- ✅ **8 أوامر premium**: subscribe, trial, gift, billing
- ✅ **10+ Premium Features**: XP Boost, Unlimited Tickets, Custom Cards
- ✅ **Trial System**: 7-day free trial
- ✅ **Usage Tracking**: تتبع استخدام الميزات

### الإصدار 3.5 - Web Dashboard
- ✅ **FastAPI Backend**: 22 API endpoints
- ✅ **Next.js 14 Frontend**: 5 pages
- ✅ **Discord OAuth2**: تسجيل دخول
- ✅ **Real-time Statistics**: إحصائيات مباشرة

### الإصدار 3.0 - Core Systems
- ✅ **5 أنظمة رئيسية**: Moderation, Leveling, Tickets, Auto-Roles
- ✅ **MongoDB + Redis**: قاعدة بيانات متقدمة
- ✅ **UI Components**: Modals, Buttons, Selects

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

### 🎯 **v4.0 Statistics**

| Category | Count | Details |
|----------|-------|---------|
| **💻 Lines of Code** | ~35,000+ | إجمالي الكود عالي الجودة |
| **🎮 Systems** | 17 نظام | Giveaways, Applications, Auto-Messages, Social + 13 نظام سابق |
| **⚡ Commands** | 85+ أمر | +40 أمر جديد في v4.0 |
| **🌐 API Endpoints** | 66+ endpoint | +37 endpoint جديد (REST + WebSocket) |
| **🎨 UI Components** | 50+ component | Modals, Buttons, Selects, Dropdowns |
| **📚 Documentation** | 12 دليل | 3 دلائل Dashboard جديدة |
| **💎 Premium Features** | 15+ ميزة | XP Boost, Unlimited, Custom Cards, etc. |
| **🗄️ Collections** | 25+ collection | MongoDB collections |
| **🌍 Languages** | 30+ لغة | ترجمة تلقائية |
| **📈 Phase 5.7** | 13,606 سطر | أكبر Phase في تاريخ المشروع |

### 🏆 **Achievements**

- ✨ **أول بوت عربي** بـ 17 نظام متكامل
- ✨ **أكبر dashboard** (8 صفحات كاملة)
- ✨ **أقوى نظام social** (7 منصات)
- ✨ **Nova UI System** - تصميم احترافي
- ✨ **Enterprise-level** - جودة إنتاجية

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

## 👑 Kingdom-77 Bot v4.0 🎉

**The Ultimate Enterprise-level Discord Bot**

**🎊 Phase 5.7 Complete | 17 Systems | 35,000+ Lines | 85+ Commands | 66+ APIs**

تم التطوير بواسطة [myapps-web](https://github.com/myapps-web)

### 🚀 **Quick Start**

1. **Invite Bot:** [Add to Server](https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=8&scope=bot%20applications.commands)
2. **Dashboard:** [dashboard.kingdom77.com](https://dashboard.kingdom77.com)
3. **Documentation:** [docs.kingdom77.com](https://github.com/myapps-web/Kingdom-77/tree/main/docs)
4. **Support:** [Join Support Server](https://discord.gg/kingdom77)

---

**Made with ❤️ in Saudi Arabia 🇸🇦**

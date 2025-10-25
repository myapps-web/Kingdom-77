# Kingdom-77 Discord Bot

مستودع بسيط لبوت ديسكورد مخصّص للترجمة مع نظام تقييم وإدارة صلاحيات.

## 📁 هيكل المشروع / Project Structure

```
Kingdom-77/
│
├── main.py                 # الملف الرئيسي للبوت / Main bot file
├── requirements.txt        # متطلبات البايثون / Python dependencies
├── .env.example           # مثال لملف المتغيرات / Environment variables example
│
├── data/                  # ملفات البيانات / Data files
│   ├── channels.json          # إعدادات اللغات للقنوات
│   ├── ratings.json           # تقييمات المستخدمين
│   ├── allowed_roles.json     # الرتب المسموحة
│   ├── role_languages.json    # لغات الرتب الافتراضية
│   └── *.json.example         # أمثلة الملفات
│
├── docs/                  # الوثائق / Documentation
│   ├── README.md              # دليل الاستخدام
│   ├── RATING_SYSTEM.md       # وثائق نظام التقييم
│   ├── RATING_SYSTEM_GUIDE.md # دليل التقييم (عربي/إنجليزي)
│   ├── ROLE_MANAGEMENT_SYSTEM.md # وثائق نظام الصلاحيات
│   ├── ROLE_LANGUAGES_GUIDE.md # دليل لغات الرتب (عربي شامل)
│   └── replit.md              # معلومات Replit
│
├── backup/                # ملفات النسخ الاحتياطي / Backup files
│
├── tests/                 # الاختبارات / Tests
│   └── check_cogs.py
│
└── cogs/                  # Cogs (إضافية) / Additional cogs
    └── ...
```

## ✨ الميزات / Features

- 🌍 **ترجمة تلقائية** - ترجمة الرسائل حسب لغة القناة المحددة
- 🖱️ **ترجمة بالنقر اليمين** - ترجم أي رسالة إلى لغتك بنقرة واحدة
- 🎭 **ترجمة حسب الرتب** - تعيين لغة افتراضية لكل رتبة
- ⭐ **نظام التقييم** - تقييم البوت من 1-5 نجوم مع إحصائيات
- 🔐 **نظام الصلاحيات** - إدارة الصلاحيات عبر الرتب
- 📊 **تقارير مفصلة** - إحصائيات وتقارير شاملة
- 🎨 **واجهة تفاعلية** - أزرار وقوائم منسدلة وفلاتر ذكية
- ⚡ **أداء محسّن** - ترجمة سريعة مع نظام تخزين مؤقت

## 🚀 التثبيت / Installation

### محلياً (Windows / PowerShell)

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
- أضف توكن البوت في ملف `.env`:
```
TOKEN=YOUR_DISCORD_BOT_TOKEN
```

5. **تشغيل البوت:**
```powershell
python main.py
```

### على Replit

1. ارفع المجلد أو اربط المستودع بـ Replit
2. في **Settings → Secrets** أدخل `TOKEN` بقيمة توكن البوت
3. اضبط أمر التشغيل إلى: `python main.py`
4. اضغط **Run**

## 📝 الأوامر المتاحة / Available Commands

### أوامر عامة / General Commands
- `/ping` - فحص استجابة البوت
- `/help` - عرض جميع الأوامر
- `/listlangs` - عرض اللغات المدعومة
- `/listchannels` - عرض القنوات المهيأة مع فلتر ذكي

### إدارة اللغات / Language Management
- `/setlang [channel]` - تعيين لغة افتراضية لقناة
- `/removelang [channel]` - حذف إعدادات اللغة

### ميزة الترجمة التفاعلية / Interactive Translation
- **نقر يمين على رسالة → Translate Message** - ترجم أي رسالة إلى لغتك
- يتطلب أن يكون لديك رتبة بلغة محددة

### نظام التقييم / Rating System
- `/rate` - تقييم البوت (1-5 نجوم)
- `/ratings` - عرض إحصائيات التقييمات

### إدارة الصلاحيات / Permission Management (Admin Only)
- `/addrole <role>` - إضافة رتبة مسموحة لإدارة اللغات
- `/removerole <role>` - إزالة رتبة من إدارة اللغات
- `/listroles` - عرض الرتب المسموحة

### إدارة لغات الرتب / Role Languages Management (Admin Only)
- `/setrolelang <role> <language>` - تعيين لغة افتراضية لرتبة
- `/removerolelang <role>` - حذف لغة الرتبة
- `/listrolelanguages` - عرض جميع الرتب ولغاتها

### أدوات التطوير / Debug Tools (Admin Only)
- `/debug` - معلومات تصحيح الأخطاء

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

لمزيد من التفاصيل، راجع مجلد `docs/`:
- [نظام التقييم](docs/RATING_SYSTEM.md) - وثائق نظام التقييم التقنية
- [دليل التقييم الشامل](docs/RATING_SYSTEM_GUIDE.md) - دليل المستخدم للتقييم (عربي/إنجليزي)
- [نظام إدارة الصلاحيات](docs/ROLE_MANAGEMENT_SYSTEM.md) - وثائق نظام الصلاحيات
- [دليل لغات الرتب](docs/ROLE_LANGUAGES_GUIDE.md) - دليل شامل لميزة الترجمة حسب الرتب (عربي)

## 🆕 آخر التحديثات / Latest Updates

### الإصدار الحالي / Current Version
- ✅ **ميزة الترجمة التفاعلية**: انقر يمين على أي رسالة → Translate Message
- ✅ **نظام لغات الرتب**: تعيين لغة افتراضية لكل رتبة
- ✅ **تحسين الأداء**: نظام تخزين مؤقت للترجمة (1000 إدخال)
- ✅ **واجهة محسنة**: قوائم منسدلة وفلاتر ذكية في `/listchannels`
- ✅ **دعم 30+ لغة**: مع أسماء كاملة باللغة العربية
- ✅ **تنظيف الكود**: إزالة الأوامر المكررة لتجربة أفضل

## 🔒 ملاحظات أمان / Security Notes

- ⚠️ لا ترفع توكن البوت إلى المستودع العام
- ✅ استخدم متغيرات البيئة أو Secrets على Replit
- 📁 ملفات البيانات محمية في `.gitignore`
- 🔐 نظام صلاحيات متقدم يحمي الأوامر الإدارية

## ⚡ الأداء / Performance

- 🚀 **ترجمة سريعة**: استخدام مكتبة `deep-translator` المحسّنة
- 💾 **تخزين مؤقت**: 1000 ترجمة محفوظة للوصول الفوري
- 📊 **كشف اللغة**: نظام ذكي يدعم 30+ لغة
- 🎯 **استجابة فورية**: معظم الأوامر تنفذ في أقل من ثانية

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

تم التطوير بواسطة [myapps-web](https://github.com/myapps-web)

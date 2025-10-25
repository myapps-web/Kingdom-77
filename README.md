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
│   └── allowed_roles.json.example  # مثال للرتب
│
├── docs/                  # الوثائق / Documentation
│   ├── README.md              # دليل الاستخدام
│   ├── RATING_SYSTEM.md       # وثائق نظام التقييم
│   ├── RATING_SYSTEM_GUIDE.md # دليل التقييم (عربي/إنجليزي)
│   ├── ROLE_MANAGEMENT_SYSTEM.md # وثائق نظام الصلاحيات
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
- ⭐ **نظام التقييم** - تقييم البوت من 1-5 نجوم مع إحصائيات
- 🔐 **نظام الصلاحيات** - إدارة الصلاحيات عبر الرتب
- 📊 **تقارير مفصلة** - إحصائيات وتقارير شاملة
- 🎨 **واجهة تفاعلية** - أزرار وقوائم منسدلة

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
- `/listchannels` - عرض القنوات المهيأة (مع صفحات)

### إدارة اللغات / Language Management
- `/setlang [channel]` - تعيين لغة افتراضية لقناة
- `/getlang [channel]` - عرض اللغة المحددة للقناة
- `/removelang [channel]` - حذف إعدادات اللغة

### نظام التقييم / Rating System
- `/rate` - تقييم البوت (1-5 نجوم)
- `/ratings` - عرض إحصائيات التقييمات

### إدارة الصلاحيات / Permission Management (Admin Only)
- `/addrole <role>` - إضافة رتبة مسموحة
- `/removerole <role>` - إزالة رتبة
- `/listroles` - عرض الرتب المسموحة
- `/debug` - معلومات تصحيح الأخطاء

## 🌐 اللغات المدعومة / Supported Languages

- 🇸🇦 العربية (Arabic) - `ar`
- 🇬🇧 الإنجليزية (English) - `en`
- 🇹🇷 التركية (Turkish) - `tr`
- 🇯🇵 اليابانية (Japanese) - `ja`
- 🇫🇷 الفرنسية (French) - `fr`
- 🇰🇷 الكورية (Korean) - `ko`
- 🇮🇹 الإيطالية (Italian) - `it`

## 🔐 نظام الصلاحيات / Permission System

### الصلاحيات الافتراضية / Default Permissions
- 👑 مالك السيرفر (Server Owner)
- 🛡️ الأدمنستريتور (Administrator)

### الصلاحيات المخصصة / Custom Permissions
يمكن للأدمنز إضافة رتب مخصصة باستخدام `/addrole`

## 📚 الوثائق / Documentation

لمزيد من التفاصيل، راجع مجلد `docs/`:
- [نظام التقييم](docs/RATING_SYSTEM.md)
- [دليل التقييم الشامل](docs/RATING_SYSTEM_GUIDE.md)
- [نظام إدارة الصلاحيات](docs/ROLE_MANAGEMENT_SYSTEM.md)

## 🔒 ملاحظات أمان / Security Notes

- ⚠️ لا ترفع توكن البوت إلى المستودع العام
- ✅ استخدم متغيرات البيئة أو Secrets على Replit
- 📁 ملفات البيانات (ratings.json, allowed_roles.json) محمية في .gitignore

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

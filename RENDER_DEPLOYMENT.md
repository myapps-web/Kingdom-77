# 🚀 نشر البوت على Render

## خطوات النشر (Background Worker)

### 1️⃣ إنشاء الخدمة

1. اذهب إلى [dashboard.render.com](https://dashboard.render.com/)
2. اضغط **New +** → **Background Worker**
3. **Connect a repository:**
   - اختر `myapps-web/Kingdom-77`
   - أو أدخل الرابط: `https://github.com/myapps-web/Kingdom-77`

### 2️⃣ إعدادات الخدمة

```
Name: kingdom-77-bot
Region: Frankfurt (EU Central)
Branch: main
Runtime: Python 3

Build Command:
pip install -r requirements.txt

Start Command:
python main.py
```

### 3️⃣ Environment Variables (مطلوب)

أضف المتغيرات التالية:

```bash
# إجباري
DISCORD_TOKEN = your_bot_token_here
BOT_OWNER_ID = your_discord_user_id

# اختياري (للتحديث السريع)
GUILD_ID = your_server_id
```

### 4️⃣ Secret Files (اختياري)

لإضافة سيرفرات مهمة للمزامنة السريعة:

```
File Name: priority_guilds.txt
File Path: /etc/secrets/priority_guilds.txt

Contents:
1234567890123456
9876543210987654
```

### 5️⃣ نشر البوت

1. اضغط **Create Background Worker**
2. Render سيبدأ البناء والتشغيل تلقائياً
3. البوت سيعمل 24/7 مجاناً

---

## ✅ التحقق من التشغيل

في صفحة الخدمة، تحقق من:
- ✅ Status: **Live**
- ✅ Logs: `Logged in as YourBot#1234`
- ✅ Logs: `✅ Successfully synced X global commands`

---

## 🎛️ استخدام لوحة التحكم

بعد التشغيل:
```
/dashboard → إدارة البوت والسيرفرات المهمة
```

---

## ⚠️ ملاحظات مهمة

1. **لا تستخدم Web Service** - استخدم Background Worker فقط
2. **Free Plan**: 
   - يعمل 24/7 بدون توقف
   - يعيد التشغيل تلقائياً عند الأخطاء
3. **Auto Deploy**: 
   - كل Push للـ main branch سينشر تلقائياً
4. **Logs**: 
   - متاحة مباشرة في Dashboard
   - لمراقبة أداء البوت

---

## 🆘 حل المشاكل

### المشكلة: "Port scan timeout"
**الحل:** تأكد من اختيار **Background Worker** وليس Web Service

### المشكلة: "Token not set"
**الحل:** تأكد من إضافة `DISCORD_TOKEN` في Environment Variables

### المشكلة: "Commands not syncing"
**الحل:** 
- أضف `GUILD_ID` للمزامنة السريعة
- أو استخدم Secret File لإضافة سيرفرات مهمة

---

## 📞 الدعم

للمساعدة:
- افتح Issue في [GitHub](https://github.com/myapps-web/Kingdom-77/issues)
- راجع [Render Docs](https://render.com/docs/background-workers)

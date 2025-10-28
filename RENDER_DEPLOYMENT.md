# 🚀 نشر البوت على Render

## خطوات النشر (Web Service + UptimeRobot)

### 1️⃣ إنشاء Web Service

1. اذهب إلى [dashboard.render.com](https://dashboard.render.com/)
2. اضغط **New +** → **Web Service**
3. **Connect a repository:**
   - اختر `myapps-web/Kingdom-77`
   - أو أدخل الرابط: `https://github.com/myapps-web/Kingdom-77`

### 2️⃣ إعدادات الخدمة

```
Name: kingdom-77-bot
Region: Frankfurt (EU Central)
Branch: main
Runtime: Python 3

Build Command: (تلقائي من render.yaml)
Start Command: (تلقائي من render.yaml)
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

### 4️⃣ Secret Files (اختياري - للسيرفرات المهمة)

لإضافة سيرفرات مهمة للمزامنة الفورية:

**في Render Dashboard → Service → Secret Files:**

```
اضغط "Add Secret File"

File Name: priority_guilds.txt

Contents: (أضف IDs السيرفرات، كل سطر)
1234567890123456
9876543210987654
5555555555555555
```

**البوت سيقرأ الملف من:** `/etc/secrets/priority_guilds.txt`

**الفائدة:** 
- السيرفرات في هذا الملف تحصل على **تحديث فوري** للأوامر
- السيرفرات الأخرى تحصل على تحديث عام (بطيء)

**أو استخدم لوحة التحكم:**
```
/dashboard → ⚡ إدارة السيرفرات → ➕ إضافة سيرفر
```
```

### 5️⃣ إعداد UptimeRobot (مهم!)

بعد نشر البوت، ستحصل على URL مثل:
```
https://kingdom-77-bot.onrender.com
```

**لإبقاء البوت يعمل 24/7:**

1. أنشئ حساب مجاني في [UptimeRobot.com](https://uptimerobot.com/)
2. اضغط **Add New Monitor**:
   ```
   Monitor Type: HTTP(s)
   Friendly Name: Kingdom-77 Bot
   URL: https://kingdom-77-bot.onrender.com
   Monitoring Interval: 5 minutes
   ```
3. احفظ

**UptimeRobot سيزور البوت كل 5 دقائق ويمنعه من التوقف!**

---

## ✅ التحقق من التشغيل

في صفحة الخدمة، تحقق من:
- ✅ Status: **Live**
- ✅ Logs: `Logged in as YourBot#1234`
- ✅ Logs: `✅ Keep-alive server started on port 8080`
- ✅ Logs: `✅ Successfully synced X global commands`
- ✅ يمكنك زيارة URL للتأكد من عمل Keep-Alive

---

## 🎛️ استخدام لوحة التحكم

بعد التشغيل:
```
/dashboard → إدارة البوت والسيرفرات المهمة
```

---

## ⚠️ ملاحظات مهمة

1. **استخدم Web Service** (مجاني مع UptimeRobot)
2. **Free Plan**: 
   - يعمل 24/7 مع UptimeRobot
   - يعيد التشغيل تلقائياً عند الأخطاء
   - Keep-Alive على port 8080
3. **Auto Deploy**: 
   - كل Push للـ main branch سينشر تلقائياً
4. **Logs**: 
   - متاحة مباشرة في Dashboard
   - لمراقبة أداء البوت
5. **Secret Files**:
   - يجب إضافتها يدوياً من Dashboard
   - لا تُدعم في render.yaml

---

## 🆘 حل المشاكل

### المشكلة: "Port scan timeout"
**الحل:** تأكد من:
- استخدام **Web Service** وليس Background Worker
- Flask مثبت في requirements.txt
- Keep-Alive يعمل (تحقق من Logs)

### المشكلة: "Token not set"
**الحل:** تأكد من إضافة `DISCORD_TOKEN` في Environment Variables

### المشكلة: "Commands not syncing"
**الحل:** 
- أضف `GUILD_ID` للمزامنة السريعة لسيرفر واحد
- أو أضف Secret File `priority_guilds.txt` لعدة سيرفرات

### المشكلة: "البوت يتوقف بعد 15 دقيقة"
**الحل:** 
- تأكد من إضافة UptimeRobot
- تحقق من عمل Keep-Alive (زر URL في المتصفح)

### المشكلة: "Secret Files لا تعمل"
**الحل:**
- يجب إضافتها يدوياً من Dashboard → Secret Files
- لا تُضاف عبر render.yaml
- تأكد من المسار: `/etc/secrets/priority_guilds.txt`

---

## 📞 الدعم

للمساعدة:
- افتح Issue في [GitHub](https://github.com/myapps-web/Kingdom-77/issues)
- راجع [Render Docs](https://render.com/docs/background-workers)

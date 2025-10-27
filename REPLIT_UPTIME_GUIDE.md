# 🚀 دليل إبقاء البوت يعمل 24/7 على Replit

## المشكلة:
Replit يوقف البوت بعد فترة من عدم النشاط (بدون اشتراك Hacker Plan)

## ✅ الحل: استخدام Keep-Alive + UptimeRobot

---

## 📋 الخطوة 1: إعداد Keep-Alive (تم بالفعل)

تم إضافة ملف `keep_alive.py` الذي يُنشئ خادم ويب صغير على المنفذ 8080.

---

## 📋 الخطوة 2: إعداد UptimeRobot (مجاني)

### 1. سجّل حساب مجاني:
- اذهب إلى: [https://uptimerobot.com/signUp](https://uptimerobot.com/signUp)
- أنشئ حساب مجاني (يدعم حتى 50 مراقب)

### 2. أضف مراقب جديد (Monitor):
بعد تسجيل الدخول:

1. اضغط **"+ Add New Monitor"**
2. املأ البيانات:
   ```
   Monitor Type: HTTP(s)
   Friendly Name: Kingdom-77 Bot
   URL: https://your-replit-project.your-username.repl.co
   Monitoring Interval: 5 minutes (الأقصى المجاني)
   ```

### 3. احصل على رابط Replit الخاص بك:
- في Replit، بعد تشغيل البوت، ستظهر نافذة صغيرة تُظهر رابط مثل:
  ```
  https://kingdom-77.your-username.repl.co
  ```
- انسخ هذا الرابط وضعه في UptimeRobot

### 4. تفعيل المراقب:
- اضغط **"Create Monitor"**
- UptimeRobot سيزور الرابط كل 5 دقائق
- هذا يُبقي Replit نشطاً ويمنعه من الإيقاف

---

## 🎯 كيف يعمل النظام:

```
UptimeRobot (كل 5 دقائق)
    ↓
يزور → https://your-replit.repl.co
    ↓
Keep-Alive Server يستجيب
    ↓
Replit يظل نشطاً ← البوت يستمر في العمل
```

---

## 🔍 التحقق من أن كل شيء يعمل:

### في Replit Console:
يجب أن تشاهد:
```
✅ Keep-alive server started on port 8080
✅ Daily cleanup task started
Logged in as YourBot#1234
Bot is in X server(s)
```

### في المتصفح:
افتح رابط Replit الخاص بك، يجب أن تشاهد:
```
🤖 Kingdom-77 Bot
● Bot is Running!
Translation Bot • 24/7 Uptime
```

### في UptimeRobot Dashboard:
يجب أن يكون حالة المراقب:
```
✅ Up (مع نسبة uptime 99%+)
```

---

## 💡 حلول بديلة:

### الحل 2: Replit Hacker Plan (مدفوع)
- **التكلفة**: $7/شهر
- **المميزات**: 
  - البوت يعمل 24/7 تلقائياً
  - موارد أكبر
  - لا يحتاج UptimeRobot

### الحل 3: نقل البوت إلى VPS
إذا كان لديك VPS (مثل DigitalOcean، Linode، AWS):
1. ارفع الملفات
2. ثبّت المكتبات: `pip install -r requirements.txt`
3. شغّل البوت: `python main.py`
4. استخدم `screen` أو `tmux` للإبقاء عليه يعمل

---

## 🛠️ استكشاف المشاكل:

### المشكلة: البوت يتوقف بعد فترة
**الحل**:
- تأكد من أن UptimeRobot يزور الرابط الصحيح
- تأكد من أن المراقب "Paused" = OFF
- تحقق من أن Monitoring Interval = 5 minutes

### المشكلة: خطأ "Address already in use"
**الحل**:
- أعد تشغيل Repl من الصفر
- تأكد من أن المنفذ 8080 غير مستخدم

### المشكلة: رابط Replit لا يفتح
**الحل**:
- انتظر دقيقة بعد تشغيل البوت
- تأكد من أن `keep_alive.py` موجود
- تأكد من أن `flask` مثبت: `pip install flask`

---

## ✅ Checklist للتأكد من كل شيء:

- [ ] ملف `keep_alive.py` موجود
- [ ] `flask` في `requirements.txt`
- [ ] حساب UptimeRobot مُنشأ
- [ ] Monitor مُضاف برابط Replit
- [ ] Monitor حالته "Up"
- [ ] البوت يعمل في Replit
- [ ] رابط Replit يفتح في المتصفح
- [ ] Console يُظهر "Keep-alive server started"

---

## 📊 النتيجة المتوقعة:

بعد إتمام الخطوات:
```
✅ البوت يعمل 24/7
✅ Uptime: 99%+
✅ لا يتوقف عند عدم النشاط
✅ مجاني بالكامل
```

---

## 🆘 الدعم:

إذا واجهت مشاكل:
1. تحقق من Replit Console للأخطاء
2. تحقق من UptimeRobot Dashboard
3. تأكد من أن TOKEN صحيح في Replit Secrets

---

**ملاحظة هامة**: 
- Replit المجاني لديه حدود للموارد
- إذا كان البوت في عدد كبير من السيرفرات (100+)، قد تحتاج VPS
- UptimeRobot المجاني يدعم فحص كل 5 دقائق (كافي لمعظم الحالات)

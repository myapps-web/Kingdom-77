# 🚀 Auto-Messages System - Quick Start Guide

**Kingdom-77 Bot v4.0**  
**5 دقائق للبدء!**

---

## ⚡ البدء السريع

### الخطوة 1: إنشاء أول رسالة تلقائية

```bash
/automessage create keyword text
```

**في Modal:**
- **اسم الرسالة:** `welcome`
- **القيمة المحفزة:** `مرحبا`
- **محتوى الرد:** `أهلاً بك في السيرفر! 👋`

✅ **جاهز!** اكتب "مرحبا" في أي قناة والبوت سيرد تلقائياً.

---

## 🎨 إضافة Embed للرسالة

```bash
/automessage builder welcome
```

**في Modal:**
- **العنوان:** `مرحباً في Kingdom-77!`
- **الوصف:** `نحن سعداء بانضمامك إلى مجتمعنا`
- **اللون:** `#5865F2`

✅ الآن الرسالة ستظهر بشكل احترافي!

---

## 🔘 إضافة أزرار تفاعلية

### خطوة 1: إنشاء رسالة بأزرار

```bash
/automessage create keyword buttons
```

**في Modal:**
- **اسم:** `main_menu`
- **محفز:** `!menu`
- **رد:** `اختر قسماً:`

### خطوة 2: إضافة زر

```bash
/automessage add-button main_menu primary
```

**في Modal:**
- **نص الزر:** `Support`
- **Custom ID:** `button_support`
- **Emoji:** `🆘`

### خطوة 3: إنشاء رد للزر

```bash
/automessage create button text
```

**في Modal:**
- **اسم:** `support_response`
- **محفز:** `button_support`
- **رد:** `مرحباً! كيف يمكننا مساعدتك؟`

✅ **اكتمل!** اكتب `!menu` واضغط على الزر.

---

## ⏰ إضافة Cooldown (منع السبام)

```bash
/automessage settings welcome cooldown:60
```

✅ الآن الرسالة تُرسل مرة واحدة كل 60 ثانية لكل مستخدم.

---

## 🗑️ حذف تلقائي للرسائل المؤقتة

```bash
/automessage settings welcome auto_delete:10
```

✅ الرسالة ستُحذف تلقائياً بعد 10 ثوانٍ.

---

## 💌 إرسال في الرسائل الخاصة

```bash
/automessage settings welcome dm_response:True
```

✅ الرسالة ستُرسل في DM بدلاً من القناة.

---

## 📊 عرض الإحصائيات

```bash
/automessage stats
```

**يعرض:**
- إجمالي الرسائل
- المفعّلة/المعطّلة
- الاستخدامات الكلية
- الأكثر استخداماً (Top 5)

---

## 🧪 اختبار الرسالة

```bash
/automessage test welcome
```

✅ يرسل الرسالة في القناة الحالية للمعاينة.

---

## 📋 عرض جميع الرسائل

```bash
/automessage list
```

**يعرض:**
- اسم الرسالة
- نوع المحفز
- الحالة (✅/❌)
- عدد الاستخدامات

---

## 👀 عرض تفاصيل رسالة معينة

```bash
/automessage view welcome
```

**يعرض:**
- معلومات المحفز
- معلومات الرد
- الإعدادات
- الإحصائيات

---

## 🔄 تفعيل/تعطيل رسالة

```bash
/automessage toggle welcome
```

✅ يُبدّل بين التفعيل والتعطيل.

---

## 🗑️ حذف رسالة

```bash
/automessage delete welcome
```

⚠️ **تحذير:** سيُحذف كل شيء (Embed، أزرار، قوائم، إحصائيات)!

---

## 🎯 أمثلة سريعة

### مثال 1: FAQ بسيط

```bash
/automessage create keyword text

اسم: faq_rules
محفز: ما هي القوانين
رد: يمكنك قراءة القوانين في #rules

/automessage settings faq_rules cooldown:30
```

### مثال 2: قائمة تفاعلية

```bash
# إنشاء القائمة
/automessage create keyword buttons
  اسم: help_menu
  محفز: !help

# إضافة Embed
/automessage builder help_menu
  عنوان: ❓ مركز المساعدة
  وصف: اختر قسماً
  لون: #5865F2

# إضافة 3 أزرار
/automessage add-button help_menu primary
  → Support (button_support)
  
/automessage add-button help_menu secondary
  → Rules (button_rules)
  
/automessage add-button help_menu success
  → FAQ (button_faq)

# إنشاء ردود الأزرار
/automessage create button text
  اسم: support_resp
  محفز: button_support
  رد: مرحباً! اتصل بالدعم...
```

### مثال 3: رسالة مؤقتة

```bash
/automessage create keyword text
  اسم: temp_info
  محفز: !status
  رد: ✅ السيرفر يعمل بشكل طبيعي

/automessage settings temp_info
  cooldown: 30
  auto_delete: 5
```

---

## 💡 نصائح سريعة

### 1. استخدم أسماء واضحة

```
✅ welcome_new_users
✅ faq_vip_purchase
✅ menu_main

❌ msg1
❌ test
❌ a
```

### 2. Cooldowns الموصى بها

```
ترحيب: 60 ثانية
FAQ: 30 ثانية
قوائم: 10 ثوانٍ
أزرار: 5 ثوانٍ
```

### 3. Auto-Delete للمؤقتات

```
إشعارات: 5-10 ثوانٍ
تأكيدات: 15-20 ثانية
معلومات: 30 ثانية
دائمة: 0 (بدون حذف)
```

### 4. اختبر قبل التطبيق

```
1. أنشئ في قناة اختبار
2. استخدم /automessage test
3. جرّب جميع السيناريوهات
4. فعّل في القنوات الرئيسية
```

---

## 🐛 حل المشاكل السريع

### الرسالة لا تُرسل؟

```
✓ تأكد من التفعيل: /automessage toggle
✓ تحقق من المحفز (case_sensitive؟)
✓ انتظر انتهاء الCooldown
```

### الزر لا يعمل؟

```
✓ تطابق Custom ID تماماً
✓ تأكد من إنشاء button trigger
✓ تحقق من الصلاحيات
```

### Embed لا يظهر؟

```
✓ استخدم /automessage builder
✓ تحقق من روابط الصور
✓ اللون بصيغة Hex (#5865F2)
```

---

## 📚 الوثائق الكاملة

للمزيد من التفاصيل، اقرأ:
- **`AUTOMESSAGES_GUIDE.md`** - دليل شامل (1,600+ lines)
- **`PHASE5.7_AUTOMESSAGES_COMPLETE.md`** - ملخص تقني

---

## 🎉 جاهز!

الآن لديك نظام رسائل تلقائية احترافي!

### ما يمكنك فعله:

```
✅ رسائل ترحيب تلقائية
✅ إجابات FAQ فورية
✅ قوائم تفاعلية
✅ أزرار وقوائم منسدلة
✅ Cooldowns & Auto-Delete
✅ DM Response
✅ إحصائيات شاملة
```

---

**Kingdom-77 Bot v4.0** 👑  
**Auto-Messages System** 📬  
**ابدأ الآن!** 🚀

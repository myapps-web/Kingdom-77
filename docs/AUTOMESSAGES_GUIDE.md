# 📬 Auto-Messages System - دليل الاستخدام الشامل

**Kingdom-77 Bot v4.0** - نظام الرسائل التلقائية المتقدم  
**التاريخ:** 30 أكتوبر 2025  
**الإصدار:** v1.0

---

## 📖 المحتويات

1. [نظرة عامة](#نظرة-عامة)
2. [الميزات الرئيسية](#الميزات-الرئيسية)
3. [أنواع المحفزات (Triggers)](#أنواع-المحفزات-triggers)
4. [أنواع الردود (Responses)](#أنواع-الردود-responses)
5. [الأوامر](#الأوامر)
6. [أمثلة عملية](#أمثلة-عملية)
7. [الإعدادات المتقدمة](#الإعدادات-المتقدمة)
8. [استكشاف الأخطاء](#استكشاف-الأخطاء)

---

## 🎯 نظرة عامة

**Auto-Messages System** هو نظام متقدم لإنشاء رسائل تلقائية تُرسل استجابةً لمحفزات مختلفة (كلمات، أزرار، قوائم منسدلة).

### ما يميز هذا النظام؟

- ✅ **3 أنواع من المحفزات** (Keyword, Button, Dropdown)
- ✅ **Rich Embed Builder** (Nova Style)
- ✅ **حتى 25 زر** للرسالة الواحدة
- ✅ **حتى 5 قوائم منسدلة** للرسالة الواحدة
- ✅ **Cooldown System** لمنع السبام
- ✅ **Auto-Delete Messages** للرسائل المؤقتة
- ✅ **DM Response** للرسائل الخاصة
- ✅ **Role & Channel Restrictions** لتحكم دقيق
- ✅ **إحصائيات شاملة** لكل رسالة

---

## ⭐ الميزات الرئيسية

### 1. محفزات متعددة (Multi-Trigger)

```
📌 Keyword Trigger
   - أي كلمة أو جملة في الرسالة
   - Case Sensitive (حساس للأحرف الكبيرة/الصغيرة)
   - Exact Match (مطابقة تامة)

🔘 Button Trigger
   - عند الضغط على زر معين
   - Custom ID based

📋 Dropdown Trigger
   - عند اختيار خيار من قائمة
   - Value based
```

### 2. ردود غنية (Rich Responses)

```
💬 Text Response
   - رسالة نصية بسيطة

📄 Embed Response
   - Embed كامل (عنوان، وصف، ألوان، صور)
   - Nova Style Builder

🔘 Buttons Response
   - حتى 25 زر
   - 5 أنماط (Primary, Secondary, Success, Danger, Link)

📋 Dropdowns Response
   - حتى 5 قوائم
   - 25 خيار لكل قائمة
```

### 3. إعدادات متقدمة

```
⏰ Cooldown System
   - منع السبام
   - Cooldown لكل مستخدم

🗑️ Auto-Delete
   - حذف تلقائي بعد X ثواني
   - مفيد للرسائل المؤقتة

💌 DM Response
   - إرسال في الرسائل الخاصة
   - بدلاً من القناة

🔒 Permissions
   - تحديد الرتب المسموحة
   - تحديد القنوات المسموحة

📊 Statistics
   - عدد الاستخدامات
   - آخر استخدام
   - الأكثر استخداماً
```

---

## 🎯 أنواع المحفزات (Triggers)

### 1️⃣ Keyword Trigger

**متى يُستخدم:**
- رسائل الترحيب التلقائية
- إجابات الأسئلة الشائعة
- معلومات سريعة

**مثال:**

```
المحفز: "مرحبا"
الرد: "أهلاً بك في السيرفر! 👋"

عندما يكتب أي عضو "مرحبا" → يرسل البوت الرد تلقائياً
```

**إعدادات Keyword:**

```
✅ Case Sensitive: No
   "مرحبا" = "مَرحبا" = "مرحباً"

✅ Exact Match: No
   "مرحبا" موجودة في "مرحبا كيف الحال؟" ← يُفعّل

✅ Case Sensitive: Yes
   "Hello" ≠ "hello"

✅ Exact Match: Yes
   "مرحبا" فقط ← يُفعّل
   "مرحبا كيف الحال؟" ← لا يُفعّل
```

### 2️⃣ Button Trigger

**متى يُستخدم:**
- القوائم التفاعلية
- نماذج التقديم
- أزرار الإجراءات

**مثال:**

```
رسالة أولية:
"اختر قسم المساعدة:"
[Support] [Rules] [FAQ]

Button Trigger:
Custom ID: "button_support"
الرد: "مرحباً! كيف يمكننا مساعدتك؟"

عندما يضغط العضو "Support" → يرسل الرد
```

**Custom ID Format:**

```
✅ صحيح:
   - "button_support"
   - "action_buy_vip"
   - "menu_select_1"

❌ خطأ:
   - أطول من 100 حرف
   - أحرف خاصة معقدة
```

### 3️⃣ Dropdown Trigger

**متى يُستخدم:**
- قوائم الخيارات الطويلة
- تصنيفات متعددة
- نماذج معقدة

**مثال:**

```
Dropdown:
Custom ID: "help_category"
الخيارات:
  - Technical Support (value: tech)
  - Billing (value: billing)
  - General (value: general)

Dropdown Trigger:
Custom ID: "help_category"
Value: "tech"
الرد: "قسم الدعم الفني..."

عندما يختار العضو "Technical Support" → يرسل الرد
```

**Trigger Format:**

```
Format: "dropdown_id:option_value"

مثال:
  - "help_category:tech"
  - "role_select:vip"
  - "menu_main:option_1"
```

---

## 💬 أنواع الردود (Responses)

### 1️⃣ Text Response

**الأبسط والأسرع:**

```
/automessage create
  trigger_type: keyword
  response_type: text

Modal:
  - اسم الرسالة: "welcome"
  - القيمة المحفزة: "مرحبا"
  - محتوى الرد: "أهلاً بك في السيرفر! 👋"

النتيجة:
  عندما يكتب أحد "مرحبا" → يرسل "أهلاً بك في السيرفر! 👋"
```

### 2️⃣ Embed Response

**الأكثر احترافية:**

```
خطوة 1: إنشاء الرسالة
/automessage create
  trigger_type: keyword
  response_type: embed

خطوة 2: بناء Embed
/automessage builder message_name:welcome

Embed Builder Modal:
  - العنوان: "مرحباً في Kingdom-77!"
  - الوصف: "نحن سعداء بانضمامك..."
  - اللون: #5865F2
  - الصورة المصغرة: https://...
  - الصورة الكبيرة: https://...

النتيجة:
  Embed كامل باللون الأزرق مع الصور
```

**Embed Components:**

```json
{
  "title": "العنوان (256 حرف)",
  "description": "الوصف (4000 حرف)",
  "color": "#5865F2",
  "thumbnail": "رابط الصورة المصغرة",
  "image": "رابط الصورة الكبيرة",
  "fields": [
    {
      "name": "اسم Field",
      "value": "قيمة Field",
      "inline": true/false
    }
  ],
  "footer": {
    "text": "نص Footer",
    "icon_url": "أيقونة Footer"
  },
  "timestamp": true/false
}
```

### 3️⃣ Buttons Response

**تفاعلي وجذاب:**

```
خطوة 1: إنشاء الرسالة
/automessage create
  trigger_type: keyword
  response_type: buttons

خطوة 2: إضافة أزرار
/automessage add-button
  message_name: "main_menu"
  style: primary

Button Modal:
  - نص الزر: "Support"
  - Custom ID: "button_support"
  - Emoji: 🆘

كرر لإضافة المزيد (حتى 25 زر)

النتيجة:
  رسالة مع أزرار تفاعلية
  [Support] [Rules] [FAQ] [VIP]
```

**Button Styles:**

```
🔵 Primary (أزرق)
   - الأزرار الرئيسية

⚪ Secondary (رمادي)
   - الأزرار الثانوية

🟢 Success (أخضر)
   - إجراءات إيجابية (موافق، شراء)

🔴 Danger (أحمر)
   - إجراءات خطرة (حذف، رفض)

🔗 Link (رابط خارجي)
   - لفتح صفحة ويب
```

### 4️⃣ Dropdowns Response

**للقوائم الطويلة:**

```
خطوة 1: إنشاء الرسالة
/automessage create
  trigger_type: keyword
  response_type: dropdowns

خطوة 2: إضافة قائمة
/automessage add-dropdown
  message_name: "help_menu"

Dropdown Modal:
  - Custom ID: "help_category"
  - النص الافتراضي: "اختر قسم المساعدة"
  - الخيارات:
      Technical:tech:مساعدة تقنية
      Billing:billing:مشاكل الفواتير
      General:general:أسئلة عامة

Format: Label:Value:Description

النتيجة:
  قائمة منسدلة بالخيارات الثلاثة
```

---

## 🎮 الأوامر

### `/automessage create`

**إنشاء رسالة تلقائية جديدة**

```
الاستخدام:
/automessage create
  trigger_type: keyword/button/dropdown
  response_type: text/embed/buttons/dropdowns

المتطلبات:
  - صلاحية Manage Server

Modal:
  1. اسم الرسالة (مُعرّف فريد)
  2. القيمة المحفزة (الكلمة، Custom ID)
  3. محتوى الرد (للنصوص)

مثال:
/automessage create keyword text
  اسم: "welcome"
  محفز: "مرحبا"
  رد: "أهلاً بك! 👋"
```

### `/automessage builder`

**Embed Builder - Nova Style**

```
الاستخدام:
/automessage builder message_name:"welcome"

Modal:
  1. العنوان (256 حرف)
  2. الوصف (4000 حرف)
  3. اللون (Hex: #5865F2)
  4. الصورة المصغرة (URL)
  5. الصورة الكبيرة (URL)

الميزات:
  - معاينة مباشرة
  - Timestamp تلقائي
  - دعم الصور والألوان

مثال:
/automessage builder "welcome"
  عنوان: "مرحباً في Kingdom-77"
  وصف: "نحن سعداء بانضمامك..."
  لون: #5865F2
```

### `/automessage add-button`

**إضافة زر للرسالة**

```
الاستخدام:
/automessage add-button
  message_name: "menu"
  style: primary/secondary/success/danger/link

Modal:
  1. نص الزر (80 حرف)
  2. Custom ID أو URL
  3. Emoji (اختياري)

الحد الأقصى: 25 زر للرسالة

مثال:
/automessage add-button "menu" primary
  نص: "Support"
  ID: "button_support"
  Emoji: 🆘
```

### `/automessage add-dropdown`

**إضافة قائمة منسدلة**

```
الاستخدام:
/automessage add-dropdown message_name:"help"

Modal:
  1. Custom ID
  2. النص الافتراضي
  3. الخيارات (سطر لكل خيار)

Format: Label:Value:Description

الحد الأقصى:
  - 5 قوائم للرسالة
  - 25 خيار لكل قائمة

مثال:
/automessage add-dropdown "help"
  ID: "help_cat"
  نص: "اختر قسماً"
  خيارات:
    Support:support:دعم فني
    Rules:rules:القوانين
```

### `/automessage list`

**عرض جميع الرسائل**

```
الاستخدام:
/automessage list [show_disabled:True/False]

يعرض:
  - اسم الرسالة
  - نوع المحفز
  - عدد الاستخدامات
  - الحالة (✅/❌)

الحد: 10 رسائل في الصفحة

مثال:
/automessage list True
  → يعرض المفعّلة والمعطّلة
```

### `/automessage view`

**عرض تفاصيل رسالة**

```
الاستخدام:
/automessage view message_name:"welcome"

يعرض:
  - معلومات المحفز
  - معلومات الرد
  - الإعدادات
  - الإحصائيات

مثال:
/automessage view "welcome"
  → يعرض كل التفاصيل
```

### `/automessage toggle`

**تفعيل/تعطيل رسالة**

```
الاستخدام:
/automessage toggle message_name:"welcome"

المتطلبات:
  - صلاحية Manage Server

النتيجة:
  ✅ تم التفعيل
  أو
  ❌ تم التعطيل

مثال:
/automessage toggle "welcome"
```

### `/automessage delete`

**حذف رسالة تلقائية**

```
الاستخدام:
/automessage delete message_name:"old_message"

المتطلبات:
  - صلاحية Manage Server
  - تأكيد الحذف (أزرار)

تحذير:
  ⚠️ سيتم حذف كل شيء:
     - الEmbed
     - الأزرار
     - القوائم
     - الإحصائيات

مثال:
/automessage delete "old_welcome"
  [✅ نعم، احذف] [❌ لا، إلغاء]
```

### `/automessage test`

**اختبار رسالة**

```
الاستخدام:
/automessage test message_name:"welcome"

الوظيفة:
  - يرسل الرسالة في القناة الحالية
  - لا يحتسب في الإحصائيات
  - للاختبار فقط

مثال:
/automessage test "welcome"
  → يرسل رسالة الترحيب للمعاينة
```

### `/automessage stats`

**إحصائيات شاملة**

```
الاستخدام:
/automessage stats

يعرض:
  - إجمالي الرسائل
  - المفعّلة/المعطّلة
  - إجمالي الاستخدامات
  - التوزيع حسب النوع
  - الأكثر استخداماً (Top 5)

مثال:
/automessage stats
  📈 إجمالي: 15 رسالة
  ✅ مفعّلة: 12
  🔥 الاستخدامات: 1,250
```

### `/automessage settings`

**تعديل إعدادات رسالة**

```
الاستخدام:
/automessage settings
  message_name: "welcome"
  cooldown: 30
  auto_delete: 10
  dm_response: True

الإعدادات المتاحة:
  - cooldown: ثواني الانتظار
  - auto_delete: ثواني قبل الحذف
  - dm_response: إرسال في DM

مثال:
/automessage settings "welcome"
  cooldown: 60
  → منع السبام (دقيقة واحدة)
```

---

## 🎯 أمثلة عملية

### مثال 1: رسالة ترحيب بسيطة

```
الهدف: رسالة ترحيب عند كتابة "مرحبا"

الخطوات:
1. /automessage create keyword text
   - اسم: "welcome_simple"
   - محفز: "مرحبا"
   - رد: "أهلاً بك في Kingdom-77! 👋"

2. اختبار:
   - اكتب "مرحبا" في أي قناة
   - البوت يرد تلقائياً

النتيجة:
  ✅ رسالة بسيطة وسريعة
```

### مثال 2: قائمة رئيسية مع أزرار

```
الهدف: قائمة تفاعلية مع 4 أزرار

الخطوات:
1. إنشاء الرسالة:
   /automessage create keyword buttons
   - اسم: "main_menu"
   - محفز: "!menu"
   - رد: "اختر قسماً:"

2. إضافة Embed:
   /automessage builder "main_menu"
   - عنوان: "📋 القائمة الرئيسية"
   - وصف: "اختر أحد الأقسام التالية:"
   - لون: #5865F2

3. إضافة أزرار:
   /automessage add-button "main_menu" primary
     [Support] [Rules] [FAQ] [VIP]

4. إنشاء ردود الأزرار:
   /automessage create button text
   - اسم: "support_response"
   - محفز: "button_support"
   - رد: "مرحباً! كيف يمكننا مساعدتك؟"

النتيجة:
  ✅ قائمة تفاعلية كاملة
```

### مثال 3: نظام مساعدة متقدم

```
الهدف: نظام مساعدة مع قائمة منسدلة

الخطوات:
1. إنشاء رسالة القائمة:
   /automessage create keyword dropdowns
   - اسم: "help_menu"
   - محفز: "!help"

2. بناء Embed:
   /automessage builder "help_menu"
   - عنوان: "❓ مركز المساعدة"
   - وصف: "اختر قسم المساعدة:"

3. إضافة القائمة:
   /automessage add-dropdown "help_menu"
   - ID: "help_category"
   - نص: "اختر قسماً"
   - خيارات:
       Technical:tech:مساعدة تقنية
       Billing:billing:مشاكل الدفع
       General:general:أسئلة عامة
       Account:account:مشاكل الحساب

4. إنشاء ردود لكل خيار:
   /automessage create dropdown embed
   - اسم: "help_tech"
   - محفز: "help_category:tech"
   
   /automessage builder "help_tech"
   - عنوان: "🔧 الدعم الفني"
   - وصف: "يمكنك التواصل مع الدعم الفني..."

النتيجة:
  ✅ نظام مساعدة احترافي
```

### مثال 4: أسئلة شائعة (FAQ)

```
الهدف: إجابات تلقائية للأسئلة الشائعة

الخطوات:
1. سؤال: "كيف أشتري VIP؟"
   /automessage create keyword embed
   - اسم: "faq_vip"
   - محفز: "كيف أشتري vip"
   - case_sensitive: False
   - exact_match: False

   /automessage builder "faq_vip"
   - عنوان: "💎 شراء VIP"
   - وصف: "يمكنك شراء VIP من..."
   - صورة: "رابط صورة الشرح"

2. سؤال: "ما هي القوانين؟"
   /automessage create keyword embed
   - اسم: "faq_rules"
   - محفز: "القوانين"

   /automessage builder "faq_rules"
   - عنوان: "📜 القوانين"
   - وصف: "قوانين السيرفر..."

3. إعدادات:
   /automessage settings "faq_vip"
     cooldown: 30
     → منع السبام

النتيجة:
  ✅ إجابات فورية على الأسئلة الشائعة
```

### مثال 5: نظام التذاكر المبسط

```
الهدف: نظام تذاكر مبسط بالأزرار

الخطوات:
1. رسالة الإنشاء:
   /automessage create keyword buttons
   - اسم: "ticket_create"
   - محفز: "!ticket"

   /automessage builder "ticket_create"
   - عنوان: "🎫 نظام التذاكر"
   - وصف: "اختر نوع التذكرة:"

   /automessage add-button "ticket_create" primary
     - نص: "Support"
     - ID: "ticket_support"
     - emoji: 🆘

   /automessage add-button "ticket_create" success
     - نص: "Report"
     - ID: "ticket_report"
     - emoji: 📝

2. رد التذكرة:
   /automessage create button text
   - اسم: "ticket_support_response"
   - محفز: "ticket_support"
   - dm_response: True
   - رد: "تم إنشاء تذكرة Support! سيتم التواصل معك قريباً."

النتيجة:
  ✅ نظام تذاكر بسيط وفعال
```

---

## ⚙️ الإعدادات المتقدمة

### 1️⃣ Cooldown System

**منع السبام:**

```
المشكلة:
  عضو يكتب "مرحبا" 100 مرة
  → البوت يرد 100 مرة (سبام)

الحل: Cooldown
/automessage settings "welcome"
  cooldown: 60

النتيجة:
  - أول "مرحبا" → يرد
  - "مرحبا" مرة أخرى خلال 60 ثانية → لا يرد
  - بعد 60 ثانية → يرد مرة أخرى
```

**Cooldown per User:**

```
✅ كل عضو له cooldown منفصل

مثال:
  - العضو A يكتب "مرحبا" → يرد
  - العضو B يكتب "مرحبا" → يرد (cooldown منفصل)
  - العضو A يكتب "مرحبا" مرة أخرى خلال 60 ث → لا يرد
```

### 2️⃣ Auto-Delete Messages

**رسائل مؤقتة:**

```
المشكلة:
  رسائل البوت تملأ القنوات

الحل: Auto-Delete
/automessage settings "temp_message"
  auto_delete: 10

النتيجة:
  - يرسل الرسالة
  - بعد 10 ثواني → يحذفها تلقائياً
```

**الاستخدامات:**

```
1. إشعارات مؤقتة
   auto_delete: 5

2. رسائل تحذيرية
   auto_delete: 15

3. معلومات سريعة
   auto_delete: 10

4. رسائل دائمة
   auto_delete: 0 (بدون حذف)
```

### 3️⃣ DM Response

**رسائل خاصة:**

```
المشكلة:
  ردود حساسة في القنوات العامة

الحل: DM Response
/automessage settings "private_info"
  dm_response: True

النتيجة:
  - المحفز في القناة
  - الرد في DM للعضو
```

**متى تُستخدم:**

```
✅ معلومات خاصة
✅ إشعارات شخصية
✅ تأكيدات الإجراءات
✅ رسائل VIP

❌ لا تُستخدم للردود العامة
```

### 4️⃣ Role Permissions

**تحديد الرتب المسموحة:**

```
السيناريو:
  أمر VIP يجب أن يُستخدم فقط من VIP

الإعداد:
  settings: {
    "allowed_roles": ["123456789", "987654321"]
  }

النتيجة:
  - عضو لديه إحدى الرتب → يستطيع التفعيل
  - عضو بدون الرتب → لا يستطيع
```

**ملاحظة:**

```
⚠️ حالياً يتم الإعداد عبر Database مباشرة
📌 قريباً: أمر /automessage permissions
```

### 5️⃣ Channel Restrictions

**تحديد القنوات المسموحة:**

```
السيناريو:
  رسالة معينة فقط في #welcome

الإعداد:
  settings: {
    "allowed_channels": ["123456789"]
  }

النتيجة:
  - في #welcome → يُفعّل
  - في قنوات أخرى → لا يُفعّل
```

### 6️⃣ Case Sensitivity & Exact Match

**Case Sensitive:**

```
False (افتراضي):
  "مرحبا" = "مَرحبا" = "مرحباً"
  "Hello" = "hello" = "HELLO"

True:
  "Hello" ≠ "hello"
  "مرحبا" = "مرحبا" فقط
```

**Exact Match:**

```
False (افتراضي):
  محفز: "help"
  "help me" → يُفعّل ✅
  "I need help" → يُفعّل ✅

True:
  محفز: "help"
  "help" → يُفعّل ✅
  "help me" → لا يُفعّل ❌
```

---

## 📊 الإحصائيات

### معلومات تُتبع تلقائياً:

```
📈 لكل رسالة:
  - total_triggers: عدد الاستخدامات
  - last_triggered: آخر استخدام
  - created_at: تاريخ الإنشاء
  - updated_at: آخر تحديث

📊 للسيرفر:
  - total_messages: إجمالي الرسائل
  - enabled_messages: المفعّلة
  - disabled_messages: المعطّلة
  - by_type: توزيع حسب النوع
  - most_used: الأكثر استخداماً (Top 5)
```

### عرض الإحصائيات:

```
/automessage stats

الناتج:
📊 إحصائيات الرسائل التلقائية

📈 إجمالي
**الرسائل:** 15
**المفعّلة:** 12
**المعطّلة:** 3
**الاستخدامات:** 1,250

📋 حسب النوع
**keyword:** 8
**button:** 5
**dropdown:** 2

🔥 الأكثر استخداماً
**welcome_message** - 450 (keyword)
**main_menu** - 320 (button)
**help_menu** - 180 (dropdown)
```

---

## 🐛 استكشاف الأخطاء

### المشكلة 1: "الرسالة لا تُرسل"

**الأسباب المحتملة:**

```
1. ❌ الرسالة معطّلة
   الحل: /automessage toggle "message_name"

2. ❌ المحفز غير صحيح
   الحل: تحقق من case_sensitive و exact_match

3. ❌ Cooldown نشط
   الحل: انتظر انتهاء الCooldown

4. ❌ الرتبة غير مسموحة
   الحل: تحقق من allowed_roles

5. ❌ القناة غير مسموحة
   الحل: تحقق من allowed_channels
```

### المشكلة 2: "الزر لا يعمل"

**الأسباب المحتملة:**

```
1. ❌ Custom ID غير متطابق
   الحل: تأكد من التطابق التام

2. ❌ لم تُنشئ button trigger
   الحل: /automessage create button ...

3. ❌ Cooldown نشط
   الحل: انتظر

4. ❌ الرتبة غير مسموحة
   الحل: تحقق من الصلاحيات
```

### المشكلة 3: "القائمة المنسدلة لا تعمل"

**الأسباب المحتملة:**

```
1. ❌ Custom ID:Value غير صحيح
   الحل: Format صحيح "dropdown_id:value"

2. ❌ لم تُنشئ dropdown trigger
   الحل: /automessage create dropdown ...

3. ❌ الخيار غير موجود في القائمة
   الحل: تحقق من الخيارات المتاحة
```

### المشكلة 4: "Embed لا يظهر"

**الأسباب المحتملة:**

```
1. ❌ لم تستخدم /automessage builder
   الحل: أنشئ Embed عبر Builder

2. ❌ روابط الصور معطوبة
   الحل: تحقق من صلاحية الروابط

3. ❌ اللون بصيغة خاطئة
   الحل: استخدم Hex (#5865F2)
```

### المشكلة 5: "رسائل كثيرة (سبام)"

**الحل:**

```
/automessage settings "message_name"
  cooldown: 60
  auto_delete: 10

→ يمنع السبام ويحذف الرسائل
```

---

## 🎓 نصائح وأفضل الممارسات

### 1. تسمية الرسائل

```
✅ صحيح:
  - "welcome_simple"
  - "main_menu"
  - "faq_vip_purchase"
  - "ticket_support"

❌ خطأ:
  - "msg1"
  - "test"
  - "asdfgh"
  - "رسالة"
```

### 2. استخدام Cooldowns

```
الترحيب: 60 ثانية
FAQ: 30 ثانية
القوائم: 10 ثوانٍ
الأزرار: 5 ثوانٍ
```

### 3. Auto-Delete

```
إشعارات: 5-10 ثوانٍ
تأكيدات: 15-20 ثانية
معلومات مؤقتة: 30 ثانية
رسائل دائمة: 0 (بدون حذف)
```

### 4. تنظيم الرسائل

```
استخدم prefix للتصنيف:
  - welcome_*
  - faq_*
  - menu_*
  - ticket_*
  - button_*
```

### 5. الاختبار قبل التطبيق

```
1. أنشئ في قناة اختبار
2. استخدم /automessage test
3. جرّب جميع السيناريوهات
4. فعّل في القنوات الرئيسية
```

---

## 🚀 ما القادم؟

### ميزات قادمة (v2.0):

```
1. ✨ Edit Message Command
   - تعديل الرسائل بدون حذف

2. 🎨 Advanced Embed Fields
   - إضافة Fields عبر الأوامر

3. 🔒 Advanced Permissions UI
   - إعداد Roles/Channels عبر الأوامر

4. 📤 Export/Import Messages
   - نقل الرسائل بين السيرفرات

5. 🎯 Message Templates
   - قوالب جاهزة للاستخدام

6. 📊 Advanced Analytics
   - تحليلات مفصلة

7. 🔔 Scheduled Messages
   - رسائل مجدولة
```

---

## 📞 الدعم

### إذا واجهت مشاكل:

```
1. تحقق من هذا الدليل
2. استخدم /automessage view لمعرفة التفاصيل
3. استخدم /automessage test للاختبار
4. تحقق من الإحصائيات /automessage stats
5. تواصل مع الدعم في السيرفر
```

---

**Kingdom-77 Bot v4.0** 👑  
**Auto-Messages System - نظام الرسائل التلقائية المتقدم** 📬  
**جاهز للاستخدام الآن!** 🚀

---

**تم بواسطة:** Kingdom-77 Development Team  
**التاريخ:** 30 أكتوبر 2025  
**الإصدار:** v1.0  
**الحالة:** ✅ مكتمل 100%

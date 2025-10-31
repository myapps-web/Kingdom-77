# 🛡️ AutoMod System - دليل المستخدم الشامل

**الإصدار:** v3.7  
**آخر تحديث:** 31 أكتوبر 2025  
**النوع:** Behavior Analysis (تحليل السلوك)

---

## 📋 جدول المحتويات

1. [نظرة عامة](#نظرة-عامة)
2. [الميزات الرئيسية](#الميزات-الرئيسية)
3. [الإعداد الأولي](#الإعداد-الأولي)
4. [أنواع القواعد](#أنواع-القواعد)
5. [الإجراءات التلقائية](#الإجراءات-التلقائية)
6. [نظام Trust Score](#نظام-trust-score)
7. [الأوامر المتاحة](#الأوامر-المتاحة)
8. [أمثلة عملية](#أمثلة-عملية)
9. [الأسئلة الشائعة](#الأسئلة-الشائعة)
10. [استكشاف الأخطاء](#استكشاف-الأخطاء)

---

## 🎯 نظرة عامة

**AutoMod System** هو نظام مراقبة تلقائي ذكي يحمي سيرفرك من:
- 🚫 Spam والرسائل المتكررة
- 🔗 الروابط الضارة والدعوات
- 📢 Mention Spam والإزعاج
- 🔠 Caps Lock المفرط
- 😀 Emoji Spam
- ⚡ Rate Limiting (سرعة الرسائل)
- 🚷 الكلمات المحظورة

### المزايا الرئيسية:

✅ **مجاني تماماً** - بدون تكاليف شهرية  
✅ **سريع جداً** - بدون API calls خارجية  
✅ **ذكي** - يحلل سلوك الأعضاء تلقائياً  
✅ **قابل للتخصيص** - كل قاعدة قابلة للتعديل  
✅ **Trust Score System** - يميز بين الأعضاء الموثوقين والمشبوهين  
✅ **Progressive Penalties** - تصعيد العقوبات تلقائياً

---

## 🎁 الميزات الرئيسية

### 1. أنواع القواعد (8 أنواع)

| النوع | الوصف | الإعدادات |
|------|-------|----------|
| **spam** | كشف الرسائل المتكررة | عدد التكرار، المدة الزمنية |
| **rate_limit** | الحد من سرعة الرسائل | عدد الرسائل، المدة الزمنية |
| **links** | كشف الروابط | حظر الكل، القائمة البيضاء |
| **invites** | كشف دعوات Discord | - |
| **mentions** | كشف Mention Spam | الحد الأقصى، تضمين الأدوار |
| **caps** | كشف Caps Lock المفرط | النسبة المئوية، الحد الأدنى للطول |
| **emojis** | كشف Emoji Spam | الحد الأقصى للإيموجي |
| **blacklist** | الكلمات المحظورة | القائمة، حساسية الحالة |

### 2. الإجراءات التلقائية (5 إجراءات)

| الإجراء | الوصف | المدة |
|---------|-------|------|
| **delete** | حذف الرسالة فقط | - |
| **warn** | تحذير + حذف الرسالة | - |
| **mute** | كتم العضو | قابل للتحديد |
| **kick** | طرد العضو | - |
| **ban** | حظر العضو | - |

### 3. نظام Trust Score

- 🆕 **حسابات جديدة (0-7 أيام):** 30 نقطة
- 📅 **حسابات حديثة (7-30 يوم):** 50 نقطة
- 📆 **حسابات متوسطة (30-180 يوم):** 70 نقطة
- 🏆 **حسابات قديمة (180+ يوم):** 100 نقطة

**التغيير التلقائي:**
- ✅ Delete: -2 نقطة
- ⚠️ Warn: -5 نقاط
- 🔇 Mute: -10 نقطة
- 👢 Kick: -20 نقطة
- 🔨 Ban: -30 نقطة

---

## ⚙️ الإعداد الأولي

### الخطوة 1: تفعيل النظام

```
/automod-setup
```

هذا الأمر سيقوم بـ:
- ✅ إنشاء الإعدادات الأساسية
- ✅ إعداد قاعدة البيانات
- ✅ تجهيز النظام للاستخدام

### الخطوة 2: تفعيل AutoMod

```
/automod-config action:enable
```

### الخطوة 3: تحديد قناة السجلات

```
/automod-config action:update log_channel:#logs
```

### الخطوة 4: إضافة أول قاعدة

```
/automod-rule-add rule_type:spam action:delete name:"Anti-Spam"
```

---

## 📜 أنواع القواعد

### 1. Spam Detection (كشف الرسائل المتكررة)

**الوصف:** يكتشف الرسائل المتطابقة المرسلة بسرعة

**الإعدادات الافتراضية:**
- `duplicate_count`: 3 رسائل متطابقة
- `time_window`: 10 ثواني

**مثال:**
```
/automod-rule-add rule_type:spam action:warn name:"Anti-Spam Basic"
```

**متى يُفعّل:**
- إرسال 3 رسائل متطابقة في 10 ثواني
- مثال: "مرحبا مرحبا مرحبا" بسرعة

---

### 2. Rate Limit (الحد من سرعة الرسائل)

**الوصف:** يمنع إرسال الرسائل بسرعة كبيرة

**الإعدادات الافتراضية:**
- `messages_count`: 5 رسائل
- `time_window`: 5 ثواني

**مثال:**
```
/automod-rule-add rule_type:rate_limit action:mute name:"Rate Limiter" duration:300
```

**متى يُفعّل:**
- إرسال 5+ رسائل في 5 ثواني
- حماية ضد Spam Bots

---

### 3. Links Detection (كشف الروابط)

**الوصف:** يكتشف ويحظر الروابط

**الإعدادات الافتراضية:**
- `block_all_links`: false (لا يحظر كل الروابط)
- `allow_whitelist`: [] (قائمة الروابط المسموحة)

**مثال - حظر كل الروابط:**
```
/automod-rule-add rule_type:links action:delete name:"No Links"
```

**مثال - السماح بروابط معينة:**
يمكن تحديث القاعدة من Dashboard لإضافة:
```json
{
  "block_all_links": true,
  "allow_whitelist": ["youtube.com", "discord.gg/yourserver"]
}
```

**متى يُفعّل:**
- أي رابط يبدأ بـ `http://` أو `https://`
- إلا إذا كان في القائمة البيضاء

---

### 4. Invites Detection (كشف دعوات Discord)

**الوصف:** يكتشف روابط دعوات Discord الأخرى

**الإعدادات:** لا توجد إعدادات إضافية

**مثال:**
```
/automod-rule-add rule_type:invites action:delete name:"No Discord Invites"
```

**متى يُفعّل:**
- `discord.gg/xxxxx`
- `discord.com/invite/xxxxx`

---

### 5. Mentions Detection (كشف Mention Spam)

**الوصف:** يمنع الإشارة لعدد كبير من الأعضاء

**الإعدادات الافتراضية:**
- `max_mentions`: 5 إشارات
- `include_roles`: true (يشمل إشارة الأدوار)

**مثال:**
```
/automod-rule-add rule_type:mentions action:warn name:"Anti-Mention Spam"
```

**متى يُفعّل:**
- الإشارة لـ 5+ أعضاء في رسالة واحدة
- الإشارة لأدوار + أعضاء = 5+

---

### 6. Caps Lock Detection (كشف Caps Lock المفرط)

**الوصف:** يكتشف الرسائل المكتوبة بأحرف كبيرة

**الإعدادات الافتراضية:**
- `percentage`: 70% (نسبة الأحرف الكبيرة)
- `min_length`: 10 أحرف (الحد الأدنى للطول)

**مثال:**
```
/automod-rule-add rule_type:caps action:delete name:"Anti-Caps"
```

**متى يُفعّل:**
- رسالة طولها 10+ حرف
- 70%+ منها بأحرف كبيرة
- مثال: "HELLO EVERYONE PLEASE HELP ME!!!"

---

### 7. Emoji Spam Detection (كشف Emoji Spam)

**الوصف:** يمنع إرسال إيموجي كثيرة

**الإعدادات الافتراضية:**
- `max_emojis`: 10 إيموجي

**مثال:**
```
/automod-rule-add rule_type:emojis action:delete name:"Anti-Emoji Spam"
```

**متى يُفعّل:**
- 10+ إيموجي في رسالة واحدة
- يشمل: Custom Emojis + Unicode Emojis

---

### 8. Blacklist Words (الكلمات المحظورة)

**الوصف:** يحظر كلمات أو عبارات معينة

**الإعدادات الافتراضية:**
- `words`: [] (القائمة فارغة)
- `case_sensitive`: false (غير حساس للحالة)

**مثال:**
```
/automod-rule-add rule_type:blacklist action:warn name:"Bad Words Filter"
```

**ملاحظة:** يجب إضافة الكلمات يدوياً من قاعدة البيانات أو Dashboard

**متى يُفعّل:**
- عند وجود أي كلمة من القائمة في الرسالة

---

## 🎯 الإجراءات التلقائية

### 1. Delete (حذف فقط)

**الوصف:** يحذف الرسالة المخالفة

**المميزات:**
- ✅ حذف سريع
- ✅ تسجيل في قاعدة البيانات
- ✅ إرسال لقناة السجلات

**الاستخدام:**
```
/automod-rule-add rule_type:spam action:delete name:"Simple Spam Filter"
```

---

### 2. Warn (تحذير)

**الوصف:** حذف + تحذير + رسالة خاصة

**المميزات:**
- ✅ حذف الرسالة
- ✅ تسجيل التحذير
- 📧 إرسال DM للعضو
- 📊 تسجيل في Trust Score (-5)

**الاستخدام:**
```
/automod-rule-add rule_type:caps action:warn name:"Caps Warning"
```

---

### 3. Mute (كتم)

**الوصف:** حذف + كتم مؤقت

**المميزات:**
- ✅ حذف الرسالة
- 🔇 Timeout للعضو
- 📧 إرسال DM بالمدة
- 📊 تسجيل في Trust Score (-10)

**الاستخدام:**
```
/automod-rule-add rule_type:rate_limit action:mute name:"Rate Limit Mute" duration:600
```

**المدة:** بالثواني (600 = 10 دقائق)

---

### 4. Kick (طرد)

**الوصف:** حذف + طرد من السيرفر

**المميزات:**
- ✅ حذف الرسالة
- 👢 طرد العضو
- 📊 تسجيل في Trust Score (-20)

**الاستخدام:**
```
/automod-rule-add rule_type:invites action:kick name:"Invite Kicker"
```

**تحذير:** استخدم بحذر!

---

### 5. Ban (حظر)

**الوصف:** حذف + حظر دائم

**المميزات:**
- ✅ حذف الرسالة
- 🔨 حظر العضو
- 🗑️ حذف رسائل آخر يوم
- 📊 تسجيل في Trust Score (-30)

**الاستخدام:**
```
/automod-rule-add rule_type:spam action:ban name:"Spam Banner"
```

**تحذير:** استخدم للحالات الخطيرة فقط!

---

## 🔢 نظام Trust Score

### ما هو Trust Score؟

نظام نقاط يقيم موثوقية العضو بناءً على:
- 📅 عمر الحساب
- 📊 عدد المخالفات
- ⏰ وقت الانضمام للسيرفر

### مستويات Trust Score:

| النقاط | التصنيف | الوصف |
|--------|---------|-------|
| 0-19 | 🔴 خطر جداً | حساب مشبوه للغاية |
| 20-39 | 🟠 خطر | حساب مشبوه |
| 40-59 | 🟡 حذر | حساب جديد أو له مخالفات |
| 60-79 | 🟢 جيد | حساب عادي |
| 80-100 | 💎 ممتاز | حساب موثوق |

### كيف يتم الحساب؟

**عند الانضمام:**
```
عمر الحساب 0-7 أيام   → 30 نقطة
عمر الحساب 7-30 يوم   → 50 نقطة
عمر الحساب 30-180 يوم → 70 نقطة
عمر الحساب 180+ يوم   → 100 نقطة
```

**عند المخالفات:**
```
Delete → -2 نقطة
Warn   → -5 نقطة
Mute   → -10 نقطة
Kick   → -20 نقطة
Ban    → -30 نقطة
```

### Progressive Penalties (العقوبات التدريجية)

عند تفعيل `progressive_penalties`، يتم تصعيد العقوبات تلقائياً:

| عدد المخالفات (آخر ساعة) | الإجراء |
|---------------------------|---------|
| 1-2 | Delete |
| 3-4 | Warn |
| 5-6 | Mute |
| 7-8 | Kick |
| 9+ | Ban |

---

## 💻 الأوامر المتاحة

### 1. /automod-setup
**الوصف:** إعداد AutoMod للسيرفر

**الصلاحيات:** Administrator

**الاستخدام:**
```
/automod-setup
```

**النتيجة:**
- ✅ إنشاء إعدادات أساسية
- ✅ تحضير قاعدة البيانات
- ✅ عرض الخطوات التالية

---

### 2. /automod-config
**الوصف:** إدارة إعدادات AutoMod

**الصلاحيات:** Administrator

**الخيارات:**

#### Enable (تفعيل)
```
/automod-config action:enable
```

#### Disable (تعطيل)
```
/automod-config action:disable
```

#### Status (الحالة)
```
/automod-config action:status
```

#### Update (تحديث)
```
/automod-config action:update log_channel:#logs dm_users:True progressive_penalties:True
```

**المعاملات:**
- `log_channel`: قناة السجلات
- `dm_users`: إرسال رسائل خاصة (True/False)
- `progressive_penalties`: العقوبات التدريجية (True/False)

---

### 3. /automod-rule-add
**الوصف:** إضافة قاعدة جديدة

**الصلاحيات:** Manage Server

**الاستخدام:**
```
/automod-rule-add 
  rule_type:spam 
  action:warn 
  name:"My Rule" 
  duration:300
```

**المعاملات:**
- `rule_type`: نوع القاعدة (spam, rate_limit, links, إلخ)
- `action`: الإجراء (delete, warn, mute, kick, ban)
- `name`: اسم القاعدة
- `duration`: المدة بالثواني (للـ mute فقط)

---

### 4. /automod-rule-list
**الوصف:** عرض جميع القواعد

**الصلاحيات:** Manage Server

**الاستخدام:**
```
/automod-rule-list
```

**النتيجة:**
- 📋 قائمة بجميع القواعد
- ✅/❌ حالة كل قاعدة
- 🔍 نوع وإجراء كل قاعدة

---

### 5. /automod-rule-remove
**الوصف:** حذف قاعدة

**الصلاحيات:** Manage Server

**الاستخدام:**
```
/automod-rule-remove rule_name:"My Rule"
```

---

### 6. /automod-whitelist
**الوصف:** إدارة القائمة البيضاء

**الصلاحيات:** Manage Server

**الاستخدام:**

#### Add (إضافة دور)
```
/automod-whitelist action:add rule_name:"Anti-Spam" role:@Moderator
```

#### Remove (إزالة دور)
```
/automod-whitelist action:remove rule_name:"Anti-Spam" role:@Moderator
```

#### List (عرض القائمة)
```
/automod-whitelist action:list rule_name:"Anti-Spam"
```

---

### 7. /automod-logs
**الوصف:** عرض سجلات AutoMod

**الصلاحيات:** Manage Server

**الاستخدام:**

#### كل السجلات
```
/automod-logs limit:20
```

#### سجلات عضو معين
```
/automod-logs user:@Member limit:10
```

---

### 8. /automod-stats
**الوصف:** إحصائيات AutoMod

**الصلاحيات:** Manage Server

**الاستخدام:**
```
/automod-stats days:7
```

**المعاملات:**
- `days`: عدد الأيام (1-30)

**النتيجة:**
- 📊 إجمالي الإجراءات
- 🎯 الإجراءات حسب النوع
- 📋 المخالفات حسب القاعدة
- 👥 أكثر المخالفين

---

## 📚 أمثلة عملية

### مثال 1: إعداد حماية أساسية

```bash
# 1. إعداد النظام
/automod-setup

# 2. تفعيل AutoMod
/automod-config action:enable

# 3. تحديد قناة السجلات
/automod-config action:update log_channel:#mod-logs

# 4. إضافة حماية من Spam
/automod-rule-add rule_type:spam action:warn name:"Anti-Spam"

# 5. إضافة حماية من Rate Limit
/automod-rule-add rule_type:rate_limit action:mute name:"Rate Limiter" duration:300

# 6. منع دعوات Discord
/automod-rule-add rule_type:invites action:delete name:"No Invites"
```

---

### مثال 2: حماية متقدمة

```bash
# 1. Spam Protection مع Progressive Penalties
/automod-config action:update progressive_penalties:True

# 2. حماية من Mention Spam
/automod-rule-add rule_type:mentions action:warn name:"Anti-Mention"

# 3. منع Caps Lock المفرط
/automod-rule-add rule_type:caps action:delete name:"Anti-Caps"

# 4. منع Emoji Spam
/automod-rule-add rule_type:emojis action:delete name:"Anti-Emoji"

# 5. إضافة Moderators للقائمة البيضاء
/automod-whitelist action:add rule_name:"Anti-Spam" role:@Moderator
/automod-whitelist action:add rule_name:"Rate Limiter" role:@Moderator
```

---

### مثال 3: سيرفر صارم

```bash
# 1. منع كل الروابط
/automod-rule-add rule_type:links action:delete name:"No Links"

# 2. طرد عند إرسال دعوات
/automod-rule-add rule_type:invites action:kick name:"Kick Inviters"

# 3. كتم طويل للـ Spammers
/automod-rule-add rule_type:spam action:mute name:"Spam Mute" duration:3600

# 4. Blacklist Words
/automod-rule-add rule_type:blacklist action:warn name:"Bad Words"
```

---

## ❓ الأسئلة الشائعة

### Q1: هل AutoMod يؤثر على الأداء؟
**A:** لا، النظام مُحسّن جداً:
- ✅ Caching للقواعد والإعدادات
- ✅ بدون API calls خارجية
- ✅ معالجة سريعة في الذاكرة

---

### Q2: كيف أستثني Moderators من القواعد؟
**A:** استخدم القائمة البيضاء:
```
/automod-whitelist action:add rule_name:"..." role:@Moderator
```

أو يمكن إضافة أدوار محصنة عامة:
```
/automod-config action:update immune_roles:...
```

---

### Q3: هل يمكن تخصيص رسائل التحذير؟
**A:** نعم، ولكن يجب التعديل مباشرة في قاعدة البيانات أو من Dashboard:
```json
{
  "custom_message": "تحذير! تم كشف spam في رسالتك."
}
```

---

### Q4: كيف أعرف إذا كان AutoMod يعمل؟
**A:** 
1. افحص الحالة: `/automod-config action:status`
2. تحقق من السجلات: `/automod-logs limit:5`
3. اختبر بإرسال رسائل spam في قناة اختبار

---

### Q5: ماذا يحدث إذا حذفت قاعدة؟
**A:** 
- ❌ القاعدة تُحذف فوراً
- ✅ السجلات القديمة تبقى
- ✅ Trust Scores لا يتأثر

---

### Q6: هل يمكن تعطيل AutoMod في قنوات معينة؟
**A:** نعم، أضف القنوات لقائمة التجاهل:
```
/automod-config action:update ignored_channels:...
```

---

### Q7: كيف أرى Trust Score لعضو معين؟
**A:** حالياً من خلال قاعدة البيانات فقط. سيتم إضافة أمر قريباً:
```
/automod-trust user:@Member (قريباً)
```

---

### Q8: هل AutoMod يحمي من Raids؟
**A:** نعم جزئياً:
- ✅ Trust Score يكتشف الحسابات الجديدة تلقائياً
- ✅ Rate Limiting يمنع Spam السريع
- ✅ Progressive Penalties تصعّد العقوبات

للحماية القصوى، استخدم:
```
/automod-rule-add rule_type:rate_limit action:kick name:"Anti-Raid"
```

---

## 🔧 استكشاف الأخطاء

### المشكلة 1: AutoMod لا يحذف الرسائل

**الحلول:**
1. تحقق من تفعيل النظام:
   ```
   /automod-config action:status
   ```

2. تحقق من صلاحيات البوت:
   - ✅ Manage Messages
   - ✅ Moderate Members (للـ Mute)
   - ✅ Kick Members (للـ Kick)
   - ✅ Ban Members (للـ Ban)

3. تحقق من ترتيب الأدوار:
   - يجب أن يكون دور البوت أعلى من دور الأعضاء

---

### المشكلة 2: لا تصل رسائل DM للأعضاء

**الأسباب:**
- ❌ العضو أغلق DMs
- ❌ إعداد `dm_users` معطل

**الحل:**
```
/automod-config action:update dm_users:True
```

---

### المشكلة 3: Moderators يتأثرون بالقواعد

**الحل:**
أضفهم للقائمة البيضاء:
```
/automod-whitelist action:add rule_name:"..." role:@Moderator
```

أو أضف دورهم كدور محصن:
```
/automod-config action:update immune_roles:...
```

---

### المشكلة 4: القواعد لا تُطبّق في قنوات معينة

**السبب:** القناة في قائمة التجاهل

**الحل:**
راجع القنوات المتجاهلة وأزل ما لا يلزم.

---

### المشكلة 5: Trust Score لا يتغير

**السبب:** ربما لم تحدث مخالفات كافية

**الحل:**
- Trust Score يتحدث تلقائياً عند كل مخالفة
- يمكن التحقق من السجلات: `/automod-logs user:@Member`

---

## 📊 الإحصائيات والتقارير

### عرض الإحصائيات

```
/automod-stats days:30
```

**ستحصل على:**
- 📊 إجمالي الإجراءات (30 يوم)
- 🎯 التوزيع حسب الإجراء:
  - Delete: X
  - Warn: X
  - Mute: X
  - Kick: X
  - Ban: X
- 📋 التوزيع حسب القاعدة:
  - Spam: X
  - Links: X
  - Invites: X
  - إلخ...
- 👥 أكثر 5 مخالفين

---

## 🎓 نصائح وأفضل الممارسات

### 1. ابدأ بالأساسيات
```
1. Anti-Spam (warn)
2. Rate Limiter (mute)
3. No Invites (delete)
```

### 2. استخدم Progressive Penalties
```
/automod-config action:update progressive_penalties:True
```
هذا يجعل النظام يصعّد العقوبات تلقائياً.

### 3. استثنِ Moderators
دائماً أضف Moderators للقائمة البيضاء.

### 4. راقب السجلات
افحص السجلات بانتظام:
```
/automod-logs limit:20
```

### 5. لا تبالغ في القواعد
- ❌ لا تضع 10+ قواعد في البداية
- ✅ ابدأ بـ 3-5 قواعد أساسية
- ✅ أضف قواعد جديدة تدريجياً

### 6. اختبر القواعد
قبل التفعيل الكامل، اختبر في قناة خاصة.

---

## 🔐 الأمان والخصوصية

### ما يتم حفظه:
- ✅ نوع المخالفة
- ✅ الإجراء المتخذ
- ✅ وقت الحدث
- ✅ محتوى الرسالة (1000 حرف فقط)
- ✅ Trust Score

### ما لا يتم حفظه:
- ❌ رسائل الأعضاء العادية
- ❌ بيانات شخصية
- ❌ IPs

### الصلاحيات المطلوبة:
```
✅ Manage Messages - لحذف الرسائل
✅ Moderate Members - للـ Mute
✅ Kick Members - للطرد
✅ Ban Members - للحظر
✅ View Channels - لرؤية القنوات
✅ Send Messages - لإرسال السجلات
```

---

## 📞 الدعم والمساعدة

### لمزيد من المساعدة:
- 📖 **التوثيق:** راجع هذا الدليل
- 🐛 **مشاكل تقنية:** تواصل مع مطور البوت
- 💡 **اقتراحات:** شاركنا أفكارك لتحسين AutoMod

---

## 📝 سجل التغييرات

### الإصدار v3.7 (31 أكتوبر 2025)
- ✅ إصدار أول من AutoMod System
- ✅ 8 أنواع قواعد
- ✅ 5 إجراءات تلقائية
- ✅ Trust Score System
- ✅ Progressive Penalties
- ✅ 8 أوامر slash command

---

## 🎉 شكراً لاستخدام AutoMod!

نأمل أن يساعدك هذا النظام في حماية سيرفرك وتوفير بيئة آمنة لأعضائك.

**Kingdom-77 Bot Team** ❤️

---

**آخر تحديث:** 31 أكتوبر 2025  
**الإصدار:** v3.7  
**البوت:** Kingdom-77

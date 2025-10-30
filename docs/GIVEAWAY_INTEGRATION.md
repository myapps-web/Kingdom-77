# 🎁 Giveaway System Integration Guide

**Kingdom-77 Bot v4.0**

---

## 📋 التكامل مع main.py

### الخطوة 1: تحديث main.py

أضف الكود التالي في `main.py`:

```python
# في البداية - Imports
from database.giveaway_schema import init_giveaway_schema

# في دالة setup_database()
async def setup_database():
    """تهيئة قاعدة البيانات"""
    try:
        # ... الكود الحالي ...
        
        # تهيئة Giveaway Schema
        bot.giveaway_db = await init_giveaway_schema(bot.db)
        print("✅ Giveaway database initialized")
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")

# في دالة load_cogs()
async def load_cogs():
    """تحميل الـ cogs"""
    cogs = [
        # ... الـ cogs الحالية ...
        "cogs.cogs.giveaway",  # ← إضافة هذا السطر
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded: {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")
```

---

## 🗄️ MongoDB Setup

### إنشاء Collections تلقائياً

عند تشغيل البوت لأول مرة، سيتم إنشاء:

```javascript
// Collections
db.giveaways
db.giveaway_settings

// Indexes
db.giveaways.createIndex({ "giveaway_id": 1 }, { unique: true })
db.giveaways.createIndex({ "guild_id": 1 })
db.giveaways.createIndex({ "guild_id": 1, "status": 1 })
db.giveaways.createIndex({ "message_id": 1 })
db.giveaways.createIndex({ "end_time": 1 })
db.giveaways.createIndex({ "status": 1, "end_time": 1 })

db.giveaway_settings.createIndex({ "guild_id": 1 }, { unique: true })
```

---

## ⚙️ Environment Variables

لا توجد متغيرات بيئة إضافية مطلوبة! 🎉

نظام Giveaway يعمل مباشرة مع:
- ✅ MongoDB (موجود)
- ✅ Discord Bot Token (موجود)

---

## 🧪 الاختبار

### 1. اختبار الإنشاء

```
/giveaway create channel:#test
```

**ما يجب أن يحدث:**
- ✅ Modal يظهر
- ✅ بعد الإرسال: سؤال عن Entities
- ✅ رسالة القرعة تظهر في القناة
- ✅ زر "دخول القرعة" يعمل

### 2. اختبار Entities

```
/giveaway create channel:#test
→ Modal: Prize, Duration, Winners
→ اختر: نعم، تفعيل Entities
→ Modal: Mode, Roles, Points
→ إضافة رتب إضافية (اختياري)
→ إنهاء
```

**ما يجب أن يحدث:**
- ✅ Embed يعرض معلومات Entities
- ✅ عند الدخول: رسالة تعرض النقاط المكتسبة
- ✅ إحصائيات Entities ظاهرة في `/giveaway info`

### 3. اختبار الدخول

```
اضغط زر "دخول القرعة"
```

**ما يجب أن يحدث:**
- ✅ رسالة: "تم تسجيل دخولك!"
- ✅ إذا لديك Entities: "مكافأة Entities: +X% فرصة فوز!"
- ✅ عداد المشاركين يزيد
- ✅ لا يمكن الدخول مرتين

### 4. اختبار الإنهاء

```
/giveaway end giveaway_id:<id>
```

**ما يجب أن يحدث:**
- ✅ يختار فائزين عشوائياً
- ✅ Embed يُحدّث: "انتهت القرعة!"
- ✅ رسالة إعلان الفائزين
- ✅ DM للفائزين (إذا مفعّل)

### 5. اختبار Background Task

انتظر حتى تنتهي قرعة تلقائياً...

**ما يجب أن يحدث:**
- ✅ بعد انتهاء المدة (30 ثانية check)
- ✅ البوت ينهي القرعة تلقائياً
- ✅ نفس النتائج كأنك استخدمت `/giveaway end`

---

## 🐛 استكشاف الأخطاء

### مشكلة: Modal لا يظهر

**الحل:**
```python
# تأكد من أن البوت لديه صلاحيات:
- Use Slash Commands
- Send Messages
- Embed Links
- Add Reactions
```

### مشكلة: Background task لا يعمل

**الحل:**
```python
# في cog __init__:
self.check_giveaways_task.start()

# في cog_unload:
self.check_giveaways_task.cancel()
```

### مشكلة: Entities لا تحسب صحيح

**الحل:**
```python
# تأكد من:
1. role_entities صحيحة في قاعدة البيانات
2. العضو لديه الرتب فعلاً
3. mode = "cumulative" أو "highest" (lowercase)
```

### مشكلة: DM لا يُرسَل

**الحل:**
```python
# المستخدم قد يكون:
1. أغلق DMs من السيرفر
2. حظر البوت
3. لديه privacy settings عالية

# البوت يتجاهل الخطأ ويكمل
```

---

## 📊 مراقبة الأداء

### Logs مهمة

```python
# في console ستشاهد:
✅ Giveaway database initialized
✅ Loaded: cogs.cogs.giveaway
✅ Background task started

# عند إنشاء قرعة:
[Giveaway] Created: prize="Nitro" guild=123456789

# عند إنهاء قرعة:
[Giveaway] Ended: giveaway_id=abc123 winners=3

# عند خطأ:
[ERROR] Giveaway task error: <error details>
```

### MongoDB Queries

```javascript
// عرض جميع القرعات النشطة
db.giveaways.find({ status: "active" })

// عرض قرعة معينة
db.giveaways.findOne({ giveaway_id: "abc123xyz" })

// إحصائيات سيرفر
db.giveaway_settings.findOne({ guild_id: "123456789" })

// عدد القرعات الكلي
db.giveaways.countDocuments()
```

---

## 🔧 Customization

### تغيير Check Interval

```python
# في cogs/cogs/giveaway.py
@tasks.loop(seconds=30)  # ← غيّر هنا (افتراضي: 30 ثانية)
async def check_giveaways_task(self):
    ...
```

**توصيات:**
- ⚠️ لا تقل عن 10 ثوانِ (حمل على قاعدة البيانات)
- ✅ 30 ثانية مناسب (افتراضي)
- ⚡ 60 ثانية للبوتات الكبيرة

### تغيير Entities Ratio

```python
# في giveaway/giveaway_system.py
# في دالة add_entry():

bonus_entries = entities_points  # ← 1:1 ratio (افتراضي)

# يمكنك تغييرها إلى:
bonus_entries = entities_points * 2  # 1:2 ratio (أقوى)
bonus_entries = entities_points // 2  # 1:0.5 ratio (أضعف)
```

### تغيير Max Points

```python
# في database/giveaway_schema.py
"points": {
    "bsonType": "int",
    "minimum": 1,
    "maximum": 100  # ← غيّر هنا
}
```

---

## 📱 الاستخدام اليومي

### للمديرين

```bash
# صباح كل يوم
/giveaway list status:active
# → تحقق من القرعات النشطة

# عند انتهاء قرعة مهمة
/giveaway info giveaway_id:<id>
# → راجع الإحصائيات

# إذا الفائز لم يرد
/giveaway reroll giveaway_id:<id>
# → اختر فائز جديد
```

### للأعضاء

```bash
# صباح كل يوم
/giveaway list
# → شاهد القرعات الجديدة

# اضغط "دخول القرعة" 🎉
# → ادخل في كل القرعات!
```

---

## 🎓 Best Practices

### 1. إعداد Entities بحكمة

✅ **افعل:**
- ضع نقاط أعلى للرتب المهمة (VIP, Booster)
- استخدم `cumulative` لمكافأة النشيطين
- استخدم `highest` لتحديد أولويات واضحة

❌ **لا تفعل:**
- تضع نقاط متساوية للجميع
- تستخدم نقاط عالية جداً (فوق 50) إلا للرتب الخاصة
- تضع أكثر من 20 رتبة

### 2. مدة القرعات

| المدة | الاستخدام |
|-------|-----------|
| 30m - 2h | قرعات سريعة، جوائز صغيرة |
| 12h - 1d | قرعات يومية، جوائز متوسطة |
| 3d - 7d | قرعات كبيرة، جوائز ضخمة |

### 3. عدد الفائزين

```
جائزة صغيرة → 1-3 فائزين
جائزة متوسطة → 3-5 فائزين
جائزة كبيرة → 1 فائز (مميز!)
```

### 4. الشروط

```python
# قرعة للجميع
requirements = {}

# قرعة للنشيطين
requirements = {
    "min_level": 10,
    "min_server_join_days": 7
}

# قرعة لـ VIP فقط
requirements = {
    "required_roles": ["vip_role_id"]
}
```

---

## 🚀 Launch Checklist

قبل الإطلاق العام للنظام:

- [ ] اختبر إنشاء قرعة عادية ✅
- [ ] اختبر إنشاء قرعة مع Entities ✅
- [ ] اختبر cumulative mode ✅
- [ ] اختبر highest mode ✅
- [ ] اختبر الدخول في قرعة ✅
- [ ] اختبر Entities calculation ✅
- [ ] اختبر إنهاء يدوي ✅
- [ ] اختبر إنهاء تلقائي (background task) ✅
- [ ] اختبر reroll ✅
- [ ] اختبر cancel ✅
- [ ] اختبر DM notifications ✅
- [ ] اختبر جميع الأوامر ✅
- [ ] راجع الدليل مع الفريق ✅
- [ ] أعلن عن الميزة الجديدة! 🎉

---

## 📢 الإعلان

### رسالة مقترحة للإعلان

```markdown
🎁 **ميزة جديدة: نظام القرعات مع Entities!** ⭐

نقدم لكم نظام قرعات متقدم مع ميزة **Entities** الفريدة!

**ما هو Entities؟**
• نظام نقاط يعطي فرص فوز إضافية حسب رتبك
• 1 نقطة = 1% فرصة فوز إضافية!

**الميزات:**
✨ قرعات مخصصة بالكامل
⭐ نظام Entities (وضعان: إجمالي / أعلى رتبة)
📋 شروط متعددة (رتب، مستوى، كريديت، عمر)
🔄 إدارة كاملة (إنهاء، إعادة سحب، إلغاء)
📊 إحصائيات شاملة
🔔 إشعارات تلقائية

**جرّب الآن:**
`/giveaway create`

**اقرأ الدليل الكامل:** [رابط]

نتمنى لكم حظاً موفقاً! 🎉
```

---

## 🎯 Next Steps

بعد إطلاق النظام:

1. **جمع Feedback**
   - اسأل المديرين عن تجربتهم
   - اسأل الأعضاء عن وضوح Entities

2. **مراقبة الأداء**
   - راقب استخدام Background task
   - تحقق من سرعة المعالجة

3. **تحسينات مستقبلية**
   - Entities presets
   - Dashboard integration
   - Analytics

---

**Kingdom-77 Bot v4.0** 👑  
**Giveaway System with Entities** 🎁⭐

**جاهز للإطلاق!** 🚀

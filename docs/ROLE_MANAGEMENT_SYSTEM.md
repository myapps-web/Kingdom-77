# نظام التحكم بالصلاحيات عبر الرتب - Role-Based Permission System

## نظرة عامة / Overview

تم إضافة نظام شامل للتحكم في صلاحيات البوت عبر الرتب. الآن يمكن لمالك السيرفر والأدمنز تعيين رتب محددة يمكنها إدارة إعدادات اللغات في القنوات.

A comprehensive role-based permission system has been added. Server owners and administrators can now assign specific roles that can manage language settings.

---

## 🔐 نظام الصلاحيات / Permission System

### الصلاحيات الافتراضية / Default Permissions

**لديهم صلاحيات كاملة دائماً:**
- 👑 مالك السيرفر (Server Owner)
- 🛡️ الأدمنستريتور (Administrator Permission)

**Always have full permissions:**
- 👑 Server Owner
- 🛡️ Administrator Permission

### الصلاحيات المخصصة / Custom Permissions

يمكن للأدمنز إضافة رتب مخصصة تمنح أعضائها القدرة على:
- ⚙️ تعيين اللغة الافتراضية للقنوات (`/setlang`)
- ❌ حذف إعدادات اللغة (`/removelang`)
- 📋 عرض اللغة المحددة للقناة (`/getlang`)

Admins can add custom roles that grant members the ability to:
- ⚙️ Set default language for channels (`/setlang`)
- ❌ Remove language settings (`/removelang`)
- 📋 View channel language (`/getlang`)

---

## 📝 الأوامر الجديدة / New Commands

### 1. `/addrole` - إضافة رتبة مسموحة

**الوصف:** إضافة رتبة إلى قائمة الرتب المسموحة لإدارة اللغات
**الصلاحية المطلوبة:** مالك السيرفر أو أدمنستريتور
**المعاملات:**
- `role` - الرتبة المراد إضافتها

**Usage:**
```
/addrole role:@Moderators
```

**المخرجات / Output:**
```
✅ Role Added

Successfully added @Moderators to allowed roles.

Members with this role can now:
• Set channel languages (/setlang)
• Remove language settings (/removelang)
• View channel languages (/getlang)
```

---

### 2. `/removerole` - إزالة رتبة مسموحة

**الوصف:** إزالة رتبة من قائمة الرتب المسموحة
**الصلاحية المطلوبة:** مالك السيرفر أو أدمنستريتور
**المعاملات:**
- `role` - الرتبة المراد إزالتها

**Usage:**
```
/removerole role:@Moderators
```

**المخرجات / Output:**
```
✅ Role Removed

Successfully removed @Moderators from allowed roles.

Members with this role can no longer manage language settings.
```

---

### 3. `/listroles` - عرض الرتب المسموحة

**الوصف:** عرض جميع الرتب التي لديها صلاحية إدارة اللغات
**الصلاحية المطلوبة:** جميع الأعضاء
**المعاملات:** لا يوجد

**Usage:**
```
/listroles
```

**المخرجات / Output:**
```
📋 Allowed Roles

Roles with language management permissions:

• @Moderators (Moderators)
• @Helpers (Helpers)

Also have access:
• Server Owner
• Administrator

Total: 2 custom role(s)
```

---

## 🔧 التفاصيل التقنية / Technical Details

### الملفات المعدلة / Modified Files

**`main.py`:**
- ✅ إضافة ثابت `ROLES_FILE` لمسار ملف الرتب
- ✅ إضافة قاموس `allowed_roles` عام
- ✅ إضافة دالة `load_allowed_roles()` لتحميل الرتب
- ✅ إضافة دالة `save_allowed_roles()` غير متزامنة لحفظ الرتب
- ✅ إضافة دالة `has_permission()` للتحقق من الصلاحيات
- ✅ تحديث جميع الأوامر الإدارية لاستخدام النظام الجديد
- ✅ إضافة 3 أوامر جديدة: `/addrole`, `/removerole`, `/listroles`
- ✅ تحديث أمر `/help` ليعرض الأوامر الإدارية للأدمنز فقط

**New file created:**
- `allowed_roles.json` - يتم إنشاؤه تلقائياً عند أول استخدام

---

## 💾 تخزين البيانات / Data Storage

### ملف `allowed_roles.json`

**الصيغة / Format:**
```json
{
  "guild_id": [
    "role_id_1",
    "role_id_2",
    "role_id_3"
  ],
  "another_guild_id": [
    "role_id_1"
  ]
}
```

**مثال / Example:**
```json
{
  "1234567890123456789": [
    "9876543210987654321",
    "1111222233334444555"
  ]
}
```

---

## 🔍 منطق التحقق من الصلاحيات / Permission Check Logic

```python
def has_permission(member, guild_id):
    # 1. مالك السيرفر - صلاحية دائمة
    if member.guild.owner_id == member.id:
        return True
    
    # 2. أدمنستريتور - صلاحية دائمة
    if member.guild_permissions.administrator:
        return True
    
    # 3. التحقق من الرتب المخصصة
    if guild_id in allowed_roles:
        if any(str(role.id) in allowed_roles[guild_id] for role in member.roles):
            return True
        return False  # إذا كانت هناك رتب مخصصة ولم يملكها
    
    # 4. افتراضي: صلاحية Manage Channels
    return member.guild_permissions.manage_channels
```

---

## 📊 أمثلة الاستخدام / Usage Examples

### السيناريو 1: إعداد نظام الصلاحيات

1. **الأدمن ينشئ رتبة للمترجمين:**
   - ينشئ رتبة اسمها `@Translators` في إعدادات السيرفر

2. **الأدمن يضيف الرتبة للبوت:**
   ```
   /addrole role:@Translators
   ```

3. **الأعضاء مع رتبة Translators يستطيعون الآن:**
   ```
   /setlang channel:#arabic language:Arabic
   /removelang channel:#french
   /getlang channel:#english
   ```

### السيناريو 2: إدارة عدة رتب

```bash
# إضافة رتب متعددة
/addrole role:@Moderators
/addrole role:@Staff
/addrole role:@Helpers

# عرض جميع الرتب
/listroles

# إزالة رتبة
/removerole role:@Helpers
```

### السيناريو 3: فحص الصلاحيات

**عضو عادي بدون رتب:**
```
/setlang
❌ Permission Denied
You need proper permissions to use this command.

Required: Server Owner, Administrator, or an allowed role.
```

**عضو مع رتبة مسموحة:**
```
/setlang channel:#general
✅ Shows language selection menu
```

---

## 🛡️ الأمان / Security

### الحماية المطبقة / Implemented Protections

✅ **فحص صلاحيات مزدوج:**
- فحص على مستوى الأمر
- فحص على مستوى الواجهة التفاعلية (UI callback)

✅ **عزل البيانات:**
- كل سيرفر له قائمة رتب منفصلة
- لا يمكن للسيرفرات رؤية أو تعديل إعدادات بعضها

✅ **حماية الأوامر الإدارية:**
- فقط Server Owner و Administrator يستطيعون:
  - إضافة رتب (`/addrole`)
  - إزالة رتب (`/removerole`)

✅ **سجل الأحداث:**
- جميع العمليات الإدارية تُسجل في logs
- يتضمن: اسم الرتبة، الـ ID، اسم السيرفر

---

## 🔄 التوافق مع النظام القديم / Backward Compatibility

✅ **السيرفرات القديمة:**
- إذا لم يتم تعيين رتب، النظام يستخدم `manage_channels` كإعداد افتراضي
- لا حاجة لإعادة إعداد السيرفرات الحالية

✅ **البيانات الموجودة:**
- جميع إعدادات اللغات الحالية تبقى كما هي
- لا يوجد تأثير على `channels.json`

---

## 📋 قائمة التحقق للنشر / Deployment Checklist

- [x] إضافة ملف `ROLES_FILE` constant
- [x] إضافة دوال load/save للرتب
- [x] إضافة دالة `has_permission()`
- [x] تحديث جميع الأوامر الإدارية
- [x] إضافة 3 أوامر جديدة
- [x] تحديث أمر `/help`
- [x] تحديث `on_ready()` لتحميل الرتب
- [x] اختبار الـ syntax
- [ ] رفع إلى GitHub
- [ ] إعادة تشغيل البوت على Replit
- [ ] اختبار الأوامر في سيرفر حقيقي

---

## 🎯 الأوامر المحمية / Protected Commands

**الأوامر التي تتطلب صلاحيات الآن:**
1. `/setlang` - تعيين لغة القناة
2. `/removelang` - حذف لغة القناة
3. Language selection dropdown - القائمة المنسدلة لاختيار اللغة

**الأوامر الإدارية (Owner/Admin فقط):**
1. `/addrole` - إضافة رتبة
2. `/removerole` - إزالة رتبة
3. `/debug` - معلومات التصحيح

**الأوامر المتاحة للجميع:**
1. `/getlang` - عرض لغة القناة
2. `/listchannels` - عرض جميع القنوات المهيأة
3. `/listlangs` - عرض اللغات المدعومة
4. `/listroles` - عرض الرتب المسموحة
5. `/rate` - تقييم البوت
6. `/ratings` - عرض إحصائيات التقييم
7. `/ping` - فحص الاتصال
8. `/help` - عرض المساعدة

---

## 🚀 الخطوات التالية / Next Steps

### للنشر / For Deployment:
1. رفع التحديثات إلى GitHub
2. إعادة تشغيل البوت على Replit
3. سيتم مزامنة الأوامر الجديدة تلقائياً

### للاختبار / For Testing:
1. استخدم `/addrole` لإضافة رتبة
2. أعط عضو عادي هذه الرتبة
3. اطلب منه تجربة `/setlang`
4. تحقق من الصلاحيات تعمل بشكل صحيح

---

## ❓ الأسئلة الشائعة / FAQ

**س: هل يمكن إضافة عدة رتب؟**
✅ نعم، يمكنك إضافة أي عدد من الرتب لكل سيرفر.

**س: ماذا يحدث إذا تم حذف رتبة من السيرفر؟**
ℹ️ ستظهر كـ "Deleted Role" في `/listroles` ولن تمنح صلاحيات.

**س: هل يمكن للأعضاء العاديين رؤية الرتب المسموحة؟**
✅ نعم، أمر `/listroles` متاح للجميع للشفافية.

**س: ماذا لو لم أعين أي رتب؟**
ℹ️ النظام سيستخدم `manage_channels` كصلاحية افتراضية.

**س: هل يمكنني إزالة صلاحية مالك السيرفر؟**
❌ لا، مالك السيرفر والأدمنز لديهم صلاحية دائمة.

---

تم التطوير بنجاح! ✨
Development completed successfully! ✨

# نظام تقييم البوت - Bot Rating System

## نظرة عامة / Overview

تم إضافة نظام تقييم كامل للبوت يسمح للمستخدمين بتقييم تجربتهم مع البوت باستخدام نظام النجوم (1-5 نجوم).

A complete rating system has been added to the bot that allows users to rate their experience using a star-based system (1-5 stars).

---

## الميزات الجديدة / New Features

### 1. أمر التقييم `/rate`
**الوصف**: يسمح للمستخدمين بتقييم البوت من 1 إلى 5 نجوم
**الواجهة**: أزرار تفاعلية مع تسميات النجوم
**الوظائف**:
- المستخدم يمكنه التقييم بالضغط على زر النجوم (⭐ إلى ⭐⭐⭐⭐⭐)
- كل مستخدم له تقييم واحد فقط (التقييم الجديد يحل محل القديم)
- يتم حفظ التقييم فوراً مع التاريخ واسم المستخدم
- الرد يكون خاص (مرئي للمستخدم فقط)

**Description**: Allows users to rate the bot from 1 to 5 stars
**Interface**: Interactive buttons with star labels
**Features**:
- User can rate by clicking star buttons (⭐ to ⭐⭐⭐⭐⭐)
- Each user can only have one rating (new rating replaces old one)
- Rating is saved immediately with timestamp and username
- Response is ephemeral (visible to user only)

### 2. أمر الإحصائيات `/ratings`
**الوصف**: يعرض إحصائيات شاملة لتقييمات البوت
**الوظائف**:
- يعرض متوسط التقييم مع النجوم
- يعرض إجمالي عدد التقييمات
- يعرض توزيع التقييمات (5⭐ إلى 1⭐)
- أشرطة بصرية تظهر نسبة كل تقييم
- الرد يكون عام (مرئي لجميع المستخدمين)

**Description**: Displays comprehensive bot rating statistics
**Features**:
- Shows average rating with stars
- Displays total number of ratings
- Shows distribution of ratings (5⭐ to 1⭐)
- Visual bars showing percentage distribution
- Response is public (visible to all users)

---

## كيفية الاستخدام / How to Use

### تقييم البوت / Rating the Bot
1. اكتب `/rate` في أي قناة
2. سيظهر البوت رسالة مع 5 أزرار للنجوم
3. اضغط على التقييم الذي تريده (مثل: ⭐⭐⭐⭐)
4. سيؤكد البوت استلام تقييمك
5. يتم حفظ التقييم في ملف `ratings.json`

1. Type `/rate` in any channel
2. Bot will show a message with 5 star buttons
3. Click your desired rating (e.g., ⭐⭐⭐⭐)
4. Bot will confirm your rating submission
5. Rating is saved to `ratings.json` file

### عرض الإحصائيات / Viewing Statistics
1. اكتب `/ratings` في أي قناة
2. سيظهر البوت:
   - متوسط التقييم: ⭐⭐⭐⭐ (4.20/5.00)
   - إجمالي التقييمات: 10
   - توزيع التقييمات مع أشرطة بصرية ونسب مئوية

1. Type `/ratings` in any channel
2. Bot will display:
   - Average Rating: ⭐⭐⭐⭐ (4.20/5.00)
   - Total Ratings: 10
   - Distribution with visual bars and percentages

---

## التفاصيل التقنية / Technical Details

### الملفات المعدلة / Modified Files
- `main.py`: إضافة نظام التقييم الكامل
  - ثابت `RATINGS_FILE` لمسار ملف التقييمات
  - قاموس `bot_ratings` العام
  - دالة `load_ratings()` لتحميل التقييمات
  - دالة `save_ratings()` غير متزامنة لحفظ التقييمات
  - فئة `RatingView` للواجهة التفاعلية
  - أمر `/rate` الجديد
  - أمر `/ratings` الجديد
  - تحديث أمر `/help`
  - تحديث `on_ready()` لتحميل التقييمات عند بدء البوت

### Added to main.py:
- `RATINGS_FILE` constant for file path
- `bot_ratings` global dictionary
- `load_ratings()` function
- Async `save_ratings()` function
- `RatingView` UI class with 5 star buttons
- `/rate` slash command
- `/ratings` slash command
- Updated `/help` command
- Updated `on_ready()` to load ratings

### تخزين البيانات / Data Storage
- **الملف**: `ratings.json`
- **الصيغة**:
```json
{
  "user_id": {
    "rating": 5,
    "timestamp": "2024-01-01T12:00:00.000000",
    "username": "User#1234"
  }
}
```

---

## مثال على النتيجة / Example Output

### عند التقييم / When Rating
```
🎉 Rating Submitted!

Thank you for rating the bot!

Your rating: ⭐⭐⭐⭐⭐ (5/5)

Your feedback has been submitted successfully.
```

### عند عرض الإحصائيات / When Viewing Statistics
```
📊 Bot Ratings

Average Rating: ⭐⭐⭐⭐ (4.20/5.00)
Total Ratings: 10

Distribution:
⭐⭐⭐⭐⭐: ████████████░░░░░░░░ 6 (60.0%)
⭐⭐⭐⭐: ████░░░░░░░░░░░░░░░░ 2 (20.0%)
⭐⭐⭐: ██░░░░░░░░░░░░░░░░░░ 1 (10.0%)
⭐⭐: ██░░░░░░░░░░░░░░░░░░ 1 (10.0%)
⭐: ░░░░░░░░░░░░░░░░░░░░ 0 (0.0%)

Thank you to everyone who rated the bot!
```

---

## ملاحظات مهمة / Important Notes

✅ **تم الإكمال**:
- نظام التقييم بالنجوم (1-5)
- واجهة تفاعلية بالأزرار
- حفظ التقييمات في ملف JSON
- إحصائيات شاملة مع رسوم بيانية
- تحديث التقييم (تقييم واحد لكل مستخدم)
- تسجيل جميع العمليات في السجلات

✅ **Completed**:
- Star rating system (1-5)
- Interactive button interface
- Save ratings to JSON file
- Comprehensive statistics with charts
- Rating updates (one rating per user)
- Logging of all operations

📝 **للنشر / For Deployment**:
- تأكد من رفع التحديثات إلى GitHub
- أعد تشغيل البوت على Replit
- سيتم مزامنة الأوامر الجديدة تلقائياً
- قد تستغرق المزامنة العالمية حتى ساعة

- Make sure to push updates to GitHub
- Restart bot on Replit
- New commands will sync automatically
- Global sync may take up to 1 hour

---

## الأوامر المتاحة الآن / Available Commands Now

1. `/rate` - تقييم البوت / Rate the bot
2. `/ratings` - عرض إحصائيات التقييمات / View rating statistics
3. `/setlang` - تعيين لغة القناة / Set channel language
4. `/getlang` - الحصول على لغة القناة / Get channel language
5. `/removelang` - إزالة لغة القناة / Remove channel language
6. `/listlangs` - عرض اللغات المدعومة / List supported languages
7. `/listchannels` - عرض جميع القنوات المهيأة / List all configured channels
8. `/ping` - فحص استجابة البوت / Check bot responsiveness
9. `/help` - عرض جميع الأوامر / Show all commands
10. `/debug` - معلومات تصحيح الأخطاء (للمدراء فقط) / Debug info (Admins only)

---

تم التطوير بنجاح! ✨
Development completed successfully! ✨

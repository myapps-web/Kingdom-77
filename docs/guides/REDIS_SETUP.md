# Redis Cache Setup Guide
## Kingdom-77 Bot v3.0

### ما هو Redis؟
Redis هو قاعدة بيانات في الذاكرة (in-memory) تُستخدم للـ caching لتسريع أداء البوت وتقليل الضغط على MongoDB.

---

## 📋 الخطوات السريعة

### 1. الحصول على Redis مجاني

#### الخيار 1: Upstash (الموصى به)
- اذهب إلى: https://upstash.com/
- سجل باستخدام GitHub أو Google
- اضغط **"Create Database"**
- اختر:
  - **Type:** Regional (مجاني)
  - **Region:** أقرب منطقة لك
  - **Name:** kingdom77-cache
- انسخ **Redis URL** من صفحة التفاصيل

#### الخيار 2: Redis Cloud
- اذهب إلى: https://redis.com/try-free/
- سجل حساب جديد
- أنشئ قاعدة Redis مجانية (30 MB)
- انسخ Connection String

---

### 2. إضافة Redis للبوت

أضف الـ Connection String في ملف `.env`:

```env
REDIS_URL="rediss://default:password@host:port"
```

> ⚠️ **ملاحظة:** استخدم `rediss://` (مع s مزدوجة) للـ SSL

---

### 3. اختبار الاتصال

```bash
python tests/cache/test_simple_redis.py
```

يجب أن ترى:
```
✅ PING successful: True
✅ SET successful
✅ GET successful: Hello from Kingdom-77!
```

---

## 🚀 كيف يعمل Redis في البوت؟

### التدفق الكامل:

```
1. طلب إعدادات سيرفر/قناة
   ↓
2. البحث في Redis Cache أولاً
   ↓
3. إذا موجود → إرجاع من Cache (سريع!)
   ↓
4. إذا غير موجود → تحميل من MongoDB
   ↓
5. حفظ في Cache لـ 5-10 دقائق
   ↓
6. إرجاع البيانات
```

### مثال عملي:
```python
# الطريقة القديمة (بطيئة):
settings = await db.guilds.find_one({"guild_id": "123"})

# الطريقة الجديدة (سريعة):
settings = await get_guild_settings_cached("123")
# Cache Hit: 1-2ms
# Cache Miss + MongoDB: 50-100ms
```

---

## ⚡ الفوائد

### 1. **سرعة الاستجابة**
- **بدون Redis:** 50-100ms لكل استعلام MongoDB
- **مع Redis:** 1-2ms للبيانات المكررة

### 2. **توفير التكاليف**
- تقليل استعلامات MongoDB بنسبة 70-90%
- أقل ضغط على قاعدة البيانات

### 3. **تحسين تجربة المستخدم**
- استجابة فورية للأوامر المكررة
- أداء أفضل للترجمة الأوتوماتيكية

---

## 🔧 الدوال المتوفرة

### في `main.py`:

```python
# الحصول على إعدادات القناة مع Cache
settings = await get_channel_settings_cached(channel_id)

# الحصول على إعدادات السيرفر مع Cache
guild_data = await get_guild_settings_cached(guild_id)

# مسح Cache عند التحديث
await invalidate_channel_cache(channel_id)
await invalidate_guild_cache(guild_id)
```

---

## 📊 مراقبة الأداء

### الحصول على إحصائيات Cache:

```python
from cache import cache

if cache and cache.connected:
    stats = await cache.get_stats()
    print(f"Cache Hits: {stats['keyspace_hits']}")
    print(f"Cache Misses: {stats['keyspace_misses']}")
    print(f"Hit Rate: {stats['keyspace_hits'] / (stats['keyspace_hits'] + stats['keyspace_misses']) * 100:.1f}%")
```

**معدل نجاح جيد:** 70-90% Hit Rate

---

## 🐛 استكشاف الأخطاء

### المشكلة: "Redis connection failed"

**الحل:**
1. تأكد أن `REDIS_URL` في `.env` صحيح
2. تأكد أن الرابط يبدأ بـ `rediss://` (للـ SSL)
3. جرب الاختبار البسيط:
   ```bash
   python tests/cache/test_simple_redis.py
   ```

### المشكلة: "SSL certificate verification failed"

**الحل:**
في `cache/redis.py`، تأكد من وجود:
```python
ssl_cert_reqs=None  # Disable SSL verification
```

---

## ⚙️ الإعدادات المتقدمة

### تعديل مدة الـ Cache:

في `main.py`:
```python
# Cache لـ 5 دقائق (افتراضي)
await cache.set_json(f"channel:{id}", data, ttl=300)

# Cache لـ 10 دقائق
await cache.set_json(f"guild:{id}", data, ttl=600)

# Cache لـ ساعة واحدة
await cache.set_json(f"user:{id}", data, ttl=3600)
```

---

## 📈 الخطوات التالية

✅ Redis Cache جاهز الآن!

**المرحلة التالية (Phase 2.2):**
- نظام الإشراف (Moderation)
- تحذيرات، ميوت، باند
- سجلات الإشراف

---

## 🔗 روابط مفيدة

- [Upstash Documentation](https://docs.upstash.com/redis)
- [Redis Commands](https://redis.io/commands/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)

---

**تم إنشاؤه بواسطة:** Kingdom-77 Development Team  
**التاريخ:** أكتوبر 2025  
**الإصدار:** v3.0

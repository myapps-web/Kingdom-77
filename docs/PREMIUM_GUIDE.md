# 👑 Kingdom-77 Premium System Guide

## مقدمة

نظام Premium في Kingdom-77 يوفر ميزات متقدمة للسيرفرات من خلال نظام اشتراكات مدفوعة باستخدام Stripe.

---

## 📊 خطط الاشتراك

### 🆓 Basic - مجاني
**الخطة الأساسية المجانية لجميع السيرفرات**

**ميزات:**
- ✅ Unlimited Level Roles
- ✅ Unlimited Tickets
- ✅ Advanced Dashboard
- ✅ Priority Support

**الحدود:**
- 10 Custom Commands
- 20 Auto-Roles

---

### 💎 Premium - $9.99/شهر ($99.99/سنة)
**الخطة المدفوعة مع جميع الميزات المتقدمة**

**يشمل جميع ميزات Basic +**
- ✨ **XP Boost (2x multiplier)**
- ✨ **Custom Level Cards**
- ✨ Advanced Auto-Moderation (AI-powered)
- ✨ Custom Mod Actions
- ✨ Ticket Analytics
- ✨ Custom Branding
- ✨ Custom Commands
- ✨ API Access
- ✨ Dedicated Support
- ✨ Custom Integrations

**الحدود:**
- ♾️ **Unlimited Custom Commands**
- ♾️ **Unlimited Auto-Roles**

---

## 🔧 الأوامر

### `/premium info`
عرض جميع خطط الاشتراك والميزات

### `/premium subscribe [billing]`
الاشتراك في خطة Premium
- `billing`: monthly, yearly (اختياري، افتراضي: monthly)

**متطلبات:**
- صلاحية Administrator

**ملاحظة:** Basic مجاني ومتاح لجميع السيرفرات تلقائياً

### `/premium status`
عرض حالة الاشتراك الحالي

### `/premium features`
عرض جميع الميزات المتاحة حسب الفئة

### `/premium trial`
بدء تجربة مجانية لمدة 7 أيام (مرة واحدة فقط)

**متطلبات:**
- صلاحية Administrator
- السيرفر لم يستخدم التجربة المجانية من قبل

### `/premium cancel`
إلغاء الاشتراك (يبقى نشطاً حتى تاريخ الانتهاء)

**متطلبات:**
- صلاحية Administrator

### `/premium gift <server_id> [duration]`
إهداء اشتراك Premium لسيرفر آخر

**معاملات:**
- `server_id`: معرف السيرفر
- `duration`: المدة بالأيام (7-365، افتراضي 30)

**متطلبات:**
- صلاحية Administrator
- البوت موجود في السيرفر المستهدف

**ملاحظة:** فقط Premium يمكن إهداؤه (لا يمكن إهداء Basic لأنه مجاني)

### `/premium billing`
عرض سجل الفواتير والمدفوعات

**متطلبات:**
- صلاحية Administrator

---

## 💳 الدفع

### إعداد Stripe

1. **إنشاء حساب Stripe:**
   - اذهب إلى [Stripe.com](https://stripe.com)
   - سجل حساب جديد

2. **الحصول على API Keys:**
   - Dashboard → Developers → API keys
   - انسخ Secret Key و Publishable Key
   - استخدم Test keys للتطوير (تبدأ بـ `sk_test_`)

3. **إعداد Webhooks:**
   - Dashboard → Developers → Webhooks
   - أضف endpoint: `https://your-domain.com/stripe/webhook`
   - اختر events:
     - `checkout.session.completed`
     - `customer.subscription.deleted`
   - انسخ Webhook Secret

4. **تحديث `.env`:**
```env
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
```

### كيفية الدفع

1. المستخدم يستخدم `/premium subscribe <tier>`
2. البوت ينشئ Stripe Checkout Session
3. المستخدم يُوجه لصفحة الدفع
4. بعد الدفع، يتم تفعيل الاشتراك تلقائياً
5. البوت يستقبل webhook من Stripe
6. يتم إنشاء subscription في قاعدة البيانات

---

## 🎯 الميزات

### XP Boost
**Feature ID:** `xp_boost`
**Description:** 2x XP multiplier لجميع الأعضاء
**Tier:** Basic+

**الاستخدام:**
```python
# في leveling system
base_xp = 15
if await bot.premium_system.has_feature(guild_id, "xp_boost"):
    xp = await bot.premium_system.apply_xp_boost(guild_id, base_xp)
else:
    xp = base_xp
```

### Custom Level Cards
**Feature ID:** `custom_level_card`
**Description:** تخصيص تصميم بطاقات المستوى
**Tier:** Basic+

### Advanced Auto-Mod
**Feature ID:** `advanced_automod`
**Description:** فلترة محتوى بالذكاء الاصطناعي
**Tier:** Premium+

### API Access
**Feature ID:** `api_access`
**Description:** الوصول لـ Developer API
**Tier:** Enterprise

---

## 🔒 التحقق من الميزات

### في Commands

```python
from premium.premium_system import require_premium

@bot.slash_command()
@require_premium("custom_level_card")
async def custom_card(ctx):
    """This command requires premium"""
    await ctx.respond("✨ Premium feature!")
```

### في الكود العادي

```python
# Check if guild has feature
has_feature = await bot.premium_system.has_feature(guild_id, "xp_boost")

# Get all guild features
features = await bot.premium_system.get_guild_features(guild_id)

# Check if premium
is_premium = await bot.premium_system.is_premium(guild_id)

# Get tier
tier = await bot.premium_system.get_tier(guild_id)  # "basic", "premium", "enterprise", or None
```

---

## 📊 الحدود (Limits)

### التحقق من الحدود

```python
from premium.premium_system import check_limit

@bot.slash_command()
@check_limit("max_custom_commands")
async def add_command(ctx):
    """Command with limit check"""
    await ctx.respond("Command added!")
```

### في الكود العادي

```python
# Get limit
limit = await bot.premium_system.get_limit(guild_id, "max_custom_commands")

# Check if within limit
current_usage = 5
can_use = await bot.premium_system.check_limit(guild_id, "max_custom_commands", current_usage)

if not can_use:
    await ctx.respond(f"❌ You've reached your limit of {limit}!")
```

### الحدود المتاحة

```python
LIMITS = {
    "max_custom_commands": 5,  # Free: 5, Basic: 10, Premium: 50, Enterprise: ∞
    "max_autoroles": 10,        # Free: 10, Basic: 20, Premium: 100, Enterprise: ∞
    "max_tickets": 50           # Free: 50, Basic: ∞, Premium: ∞, Enterprise: ∞
}
```

---

## 📈 تتبع الاستخدام

### تسجيل الاستخدام

```python
await bot.premium_system.track_usage(
    guild_id=guild_id,
    feature_id="custom_level_card",
    user_id=user_id,
    metadata={"card_type": "custom"}
)
```

### الحصول على إحصائيات

```python
# Get usage stats for last 30 days
stats = await bot.premium_system.get_usage_stats(guild_id, days=30)
# Returns: {"xp_boost": 1500, "custom_level_card": 230}
```

---

## 🎁 النظام الإهداء

### إهداء اشتراك

```python
subscription = await bot.premium_system.gift_subscription(
    gifter_user_id="123456789",
    recipient_guild_id="987654321",
    tier="premium",
    duration_days=30
)
```

---

## 🔄 إدارة الاشتراكات

### إنشاء اشتراك

```python
subscription = await bot.premium_system.create_subscription(
    user_id="123456789",
    guild_id="987654321",
    tier="premium",
    duration_days=30
)
```

### الحصول على اشتراك

```python
# By user and guild
sub = await bot.premium_system.get_subscription(user_id="123", guild_id="456")

# By guild only
sub = await bot.premium_system.get_subscription(guild_id="456")
```

### تجديد اشتراك

```python
success = await bot.premium_system.renew_subscription(
    subscription_id="abc123",
    duration_days=30
)
```

### إلغاء اشتراك

```python
success = await bot.premium_system.cancel_subscription(subscription_id="abc123")
```

---

## 🗄️ قاعدة البيانات

### Collections

#### `premium_subscriptions`
```json
{
    "_id": ObjectId,
    "user_id": "123456789",
    "guild_id": "987654321",
    "tier": "premium",
    "status": "active",
    "created_at": ISODate,
    "expires_at": ISODate,
    "stripe_subscription_id": "sub_xxxxx",
    "auto_renew": true,
    "features": ["xp_boost", "custom_level_card", ...],
    "metadata": {
        "is_trial": false,
        "is_gift": false
    }
}
```

#### `premium_features`
```json
{
    "_id": ObjectId,
    "feature_id": "xp_boost",
    "name": "XP Boost",
    "description": "2x XP multiplier",
    "tier": "basic",
    "category": "leveling",
    "enabled": true
}
```

#### `payment_history`
```json
{
    "_id": ObjectId,
    "user_id": "123456789",
    "guild_id": "987654321",
    "amount": 9.99,
    "currency": "usd",
    "tier": "premium",
    "stripe_payment_id": "pi_xxxxx",
    "status": "completed",
    "created_at": ISODate
}
```

#### `feature_usage`
```json
{
    "_id": ObjectId,
    "guild_id": "987654321",
    "feature_id": "xp_boost",
    "user_id": "123456789",
    "timestamp": ISODate,
    "metadata": {}
}
```

---

## 🔧 التكامل مع الأنظمة الموجودة

### Leveling System

```python
# في leveling/level_system.py
async def add_xp(self, guild_id, user_id, base_xp):
    # Apply XP boost if premium
    xp = await self.bot.premium_system.apply_xp_boost(guild_id, base_xp)
    # ... rest of code
```

### Moderation System

```python
# في moderation system
if await bot.premium_system.has_feature(guild_id, "advanced_automod"):
    # Use AI-powered filtering
    pass
else:
    # Use basic filtering
    pass
```

### Tickets System

```python
# Check unlimited tickets
if await bot.premium_system.has_feature(guild_id, "unlimited_tickets"):
    # No limit
    can_create = True
else:
    # Check limit
    current_tickets = await get_ticket_count(guild_id)
    can_create = current_tickets < 50
```

---

## 🧪 الاختبار

### Test Mode (بدون Stripe)

في `.env`:
```env
# اترك فارغاً للتطوير
STRIPE_SECRET_KEY=
```

البوت سينشئ subscriptions مباشرة بدون الدفع.

### مع Stripe Test Mode

استخدم Test keys:
```env
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
```

استخدم بطاقات الاختبار:
- `4242 4242 4242 4242` - Successful payment
- `4000 0000 0000 0002` - Declined payment

---

## 📊 الإحصائيات

```python
# Get system stats
stats = await bot.premium_system.get_stats()
# Returns:
# {
#     "total": 100,
#     "active": 75,
#     "by_tier": {
#         "basic": 40,
#         "premium": 30,
#         "enterprise": 5
#     }
# }
```

---

## 🔄 Cleanup Task

يعمل تلقائياً كل 24 ساعة لتحديث الاشتراكات المنتهية:

```python
@tasks.loop(hours=24)
async def cleanup_task(self):
    count = await self.bot.premium_system.cleanup_expired()
    print(f"✅ Cleaned up {count} expired subscriptions")
```

---

## 🚀 الإنتاج (Production)

### Checklist

- [ ] استخدم Live Stripe keys (تبدأ بـ `sk_live_`)
- [ ] أضف Webhook endpoint صحيح
- [ ] فعّل HTTPS
- [ ] راجع الأسعار
- [ ] اختبر جميع السيناريوهات
- [ ] أضف Terms of Service
- [ ] أضف Privacy Policy
- [ ] أضف Refund Policy
- [ ] راقب الـ webhooks
- [ ] أضف error logging (Sentry)

---

## ❓ استكشاف الأخطاء

### Stripe webhook لا يعمل
1. تأكد من Webhook URL صحيح
2. تأكد من HTTPS enabled
3. راجع Stripe Dashboard → Webhooks → Logs

### الاشتراك لا ينشأ بعد الدفع
1. راجع webhook logs
2. تأكد من metadata في checkout session
3. راجع bot logs

### Premium features لا تعمل
1. تحقق من `has_feature()` في الكود
2. راجع subscription في database
3. تأكد من features list محدثة

---

## 📝 ملاحظات مهمة

1. **التجربة المجانية:** مرة واحدة فقط لكل سيرفر
2. **الإهداء:** يمكن إهداء أي tier لأي سيرفر
3. **Auto-Renew:** يعمل فقط مع Stripe subscriptions
4. **Expiration:** الاشتراكات تبقى نشطة حتى تاريخ الانتهاء بعد الإلغاء
5. **Limits:** تُطبق فوراً بعد downgrade

---

**Kingdom-77 Bot v3.6 | Premium System** 👑

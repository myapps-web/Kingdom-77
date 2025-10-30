# 🚀 Kingdom-77 Bot v4.0 - Phase 5.7 Complete Plan
**التاريخ:** 30 أكتوبر 2025
**الإصدار المستهدف:** v4.0.0

---

## 📋 الأنظمة الجديدة المُضافة

### 1️⃣ نظام التقديمات (Applications System) ✅ مكتمل
**مثل:** Appy Bot

**الملفات المُنشأة:**
- ✅ `database/application_schema.py` (850+ lines)
  - Collections: application_forms, application_submissions, application_settings
  - Full CRUD operations
  - Statistics tracking
  
- ✅ `applications/__init__.py`
- ✅ `applications/application_system.py` (600+ lines)
  - Form management (create, edit, delete, toggle)
  - Question management (add, remove, reorder)
  - Submission handling (validate, submit, review)
  - Permission checks (cooldowns, limits, blocks)
  
- ✅ `cogs/cogs/applications.py` (700+ lines)
  - 12 Discord commands:
    1. `/application setup` - إنشاء نموذج (Modal)
    2. `/application add-question` - إضافة سؤال (Modal)
    3. `/application list` - عرض جميع النماذج
    4. `/application view` - تفاصيل نموذج
    5. `/application toggle` - تفعيل/تعطيل
    6. `/application delete` - حذف نموذج (Confirmation)
    7. `/application submit` - تقديم طلب (Modal)
    8. `/application mystatus` - حالة تقديماتك
    9. `/application submissions` - عرض التقديمات
    10. `/application stats` - إحصائيات
  - UI Components: FormSetupModal, AddQuestionModal, SubmissionModal, ReviewView

**الميزات:**
- ✅ نماذج مخصصة بأسئلة غير محدودة
- ✅ 6 أنواع أسئلة: text, textarea, number, select, multiselect, yes_no
- ✅ Validation (min/max length, required fields)
- ✅ Cooldown system (hours between submissions)
- ✅ Max submissions limit per user
- ✅ Review system (Accept/Reject with reason)
- ✅ Auto role assignment on acceptance
- ✅ DM notifications
- ✅ User blocking system
- ✅ Full statistics tracking

**إحصائيات:**
- 📊 ~2,150+ lines of code
- 📝 12 Discord commands
- 🎨 4 Modal UIs + 1 Button View
- 📋 3 Database collections

---

### 2️⃣ نظام الرسائل التلقائية (Auto-Messages) ⚠️ جزئي
**مثل:** Nova Bot

**الملفات المُنشأة:**
- ✅ `database/automessages_schema.py` (400+ lines)
  - Collections: auto_messages, auto_messages_settings
  - Trigger types: keyword, button, dropdown, slash_command
  - Response types: text, embed, buttons, dropdowns

**المُتبقي لإكمال النظام:**

```python
# ===== automessages/__init__.py =====
from .automessage_system import AutoMessageSystem
__all__ = ["AutoMessageSystem"]


# ===== automessages/automessage_system.py ===== (500+ lines مطلوب)
"""
Core AutoMessage System

المطلوب:
- create_message(guild_id, name, trigger_type, trigger_value, response)
- build_embed(title, description, color, fields, thumbnail, image, footer)
- build_buttons(buttons_list) -> discord.ui.View
- build_dropdown(options_list) -> discord.ui.View
- find_matching_keyword(message_content, guild_id) -> Optional[Dict]
- handle_button_interaction(custom_id, guild_id) -> Optional[Dict]
- handle_dropdown_interaction(value, guild_id) -> Optional[Dict]
- send_auto_response(channel, message_data)
- check_cooldown(user_id, message_id) -> bool
- check_permissions(user, message_data) -> bool
"""


# ===== cogs/cogs/automessages.py ===== (800+ lines مطلوب)
"""
Discord Commands for Auto-Messages

المطلوب:
- /automessage create - إنشاء رسالة جديدة (Modal)
- /automessage edit - تعديل رسالة (Modal)
- /automessage delete - حذف رسالة
- /automessage list - عرض جميع الرسائل
- /automessage test - اختبار رسالة
- /automessage builder - فتح Embed Builder (Modal)
- /automessage add-button - إضافة زر (Modal)
- /automessage add-dropdown - إضافة قائمة منسدلة (Modal)
- /automessage toggle - تفعيل/تعطيل
- /automessage stats - إحصائيات الاستخدام
- /automessage settings - إعدادات النظام

UI Components المطلوبة:
- CreateMessageModal - إنشاء رسالة
- EmbedBuilderModal - بناء Embed (نمط Nova)
  - Fields: title, description, color, thumbnail, image, footer
  - Preview button
- ButtonBuilderModal - إضافة زر
  - Fields: label, style, custom_id/url, emoji
- DropdownBuilderModal - إضافة قائمة
  - Fields: placeholder, options (comma-separated)
- AutoMessageView - أزرار الرسالة التلقائية
- AutoDropdownView - قائمة منسدلة

Event Handlers المطلوبة:
- on_message() - التحقق من الكلمات المفتاحية
- on_button_click() - معالجة النقر على الأزرار
- on_dropdown_select() - معالجة اختيار من القائمة
"""
```

**الميزات المطلوبة:**
- ✅ Keyword triggers (case-sensitive, exact match options)
- ✅ Button triggers (custom_id based)
- ✅ Dropdown triggers (value based)
- ✅ Rich embed builder (Nova style)
- ✅ Multiple buttons per message (up to 25)
- ✅ Dropdown menus (up to 25 options)
- ✅ Role permissions
- ✅ Channel restrictions
- ✅ Cooldown system
- ✅ Auto-delete messages
- ✅ Usage statistics

---

### 3️⃣ نظام التكامل مع وسائل التواصل (Social Media Integration) ⏳ غير مبدوء
**مثل:** Pingcord

**الملفات المطلوبة:**

```python
# ===== database/social_integration_schema.py ===== (600+ lines مطلوب)
"""
Collections:
- social_links: روابط وسائل التواصل
  - link_id, guild_id, user_id, platform (youtube, twitch, kick, twitter, instagram, tiktok)
  - channel_url, notification_channel_id, role_mention_id
  - last_post_id, is_active, created_at
  
- social_posts: سجل المنشورات
  - post_id, link_id, platform, post_title, post_description
  - post_thumbnail, post_url, published_at, notified_at
  
- social_settings: إعدادات النظام
  - guild_id, free_links_used (max: 2 per guild)
  - additional_links_purchased (200 ❄️ per link)
  - check_interval_minutes (default: 5)
  
- user_purchased_links: الروابط المشتراة
  - user_id, guild_id, links_count, purchased_at
"""


# ===== integrations/__init__.py =====
from .social_integration import SocialIntegrationSystem
__all__ = ["SocialIntegrationSystem"]


# ===== integrations/social_integration.py ===== (800+ lines مطلوب)
"""
Core Social Integration System

المطلوب:
- link_account(guild_id, user_id, platform, channel_url) -> bool
- unlink_account(link_id) -> bool
- check_new_posts(link_id) -> List[Dict]  # Polling mechanism
- send_notification(guild, post_data, link_data)
- get_user_links(user_id, guild_id) -> List[Dict]
- get_guild_links(guild_id) -> List[Dict]
- can_add_link(guild_id) -> tuple[bool, Optional[str]]
- purchase_additional_link(user_id, guild_id) -> bool  # 200 ❄️

Platform Integrations:
- YouTube API (RSS feeds or Data API v3)
- Twitch API (EventSub webhooks or polling)
- Kick API (unofficial API or scraping)
- Twitter API (v2 - recent tweets)
- Instagram (unofficial API)
- TikTok (unofficial API)

Background Tasks:
- check_all_links_task() - كل 5 دقائق
- cleanup_old_posts_task() - كل 24 ساعة
"""


# ===== cogs/cogs/social.py ===== (600+ lines مطلوب)
"""
Discord Commands for Social Integration

المطلوب:
- /social link <platform> <url> - ربط حساب
  - YouTube: channel URL or channel ID
  - Twitch: username
  - Kick: username
  - Twitter: username
  - Instagram: username
  - TikTok: username
  
- /social unlink <link_id> - فك الربط
- /social list - عرض جميع الروابط
- /social test <link_id> - اختبار إشعار
- /social notifications <link_id> - تعديل قناة الإشعارات
- /social role <link_id> <role> - تعيين رتبة للإشارة
- /social toggle <link_id> - تفعيل/تعطيل
- /social mylimits - حدودك الحالية (free vs purchased)
- /social purchase-link - شراء رابط إضافي (200 ❄️)
- /social stats - إحصائيات الاستخدام

UI Components:
- LinkSetupModal - إعداد الربط
- NotificationPreview - معاينة الإشعار
- PurchaseLinkView - تأكيد شراء رابط
"""
```

**الميزات المطلوبة:**
- ✅ 6 منصات: YouTube, Twitch, Kick, Twitter, Instagram, TikTok
- ✅ 2 روابط مجانية لكل سيرفر
- ✅ شراء روابط إضافية (200 ❄️ للرابط الواحد - دائم)
- ✅ تكامل مع Credits System
- ✅ إشعارات تلقائية عند النشر
- ✅ Embed مخصص مع صورة الغلاف التلقائية
- ✅ إشارة رتبة اختيارية
- ✅ Background polling (كل 5 دقائق)
- ✅ معالجة الأخطاء (rate limits, invalid URLs)

**التكامل مع Credits:**
```python
# في economy/credits_system.py
async def purchase_social_link(user_id: str, guild_id: str) -> tuple[bool, str]:
    """شراء رابط social إضافي بـ 200 ❄️"""
    LINK_COST = 200
    
    # Check balance
    balance = await self.get_balance(user_id)
    if balance < LINK_COST:
        return False, f"❌ رصيدك غير كافٍ! المطلوب: {LINK_COST} ❄️"
    
    # Spend credits
    success = await self.spend_credits(
        user_id=user_id,
        amount=LINK_COST,
        reason="شراء رابط Social إضافي",
        metadata={"guild_id": guild_id, "type": "social_link"}
    )
    
    if success:
        # Increment purchased links
        await self.db.social_settings.update_one(
            {"guild_id": guild_id},
            {"$inc": {"additional_links_purchased": 1}}
        )
        return True, f"✅ تم شراء رابط إضافي! متبقي: {balance - LINK_COST} ❄️"
    
    return False, "❌ فشل شراء الرابط!"
```

---

### 4️⃣ Dashboard APIs & UI ⏳ غير مبدوء

**الملفات المطلوبة:**

```python
# ===== dashboard/api/applications.py ===== (500+ lines)
"""
FastAPI Endpoints for Applications

- GET    /api/applications/{guild_id}/forms
- POST   /api/applications/{guild_id}/forms
- GET    /api/applications/{guild_id}/forms/{form_id}
- PUT    /api/applications/{guild_id}/forms/{form_id}
- DELETE /api/applications/{guild_id}/forms/{form_id}
- POST   /api/applications/{guild_id}/forms/{form_id}/questions
- DELETE /api/applications/{guild_id}/forms/{form_id}/questions/{question_id}
- GET    /api/applications/{guild_id}/forms/{form_id}/submissions
- GET    /api/applications/{guild_id}/submissions/{submission_id}
- PUT    /api/applications/{guild_id}/submissions/{submission_id}/review
- GET    /api/applications/{guild_id}/stats
"""


# ===== dashboard/api/automessages.py ===== (400+ lines)
"""
FastAPI Endpoints for Auto-Messages

- GET    /api/automessages/{guild_id}/messages
- POST   /api/automessages/{guild_id}/messages
- GET    /api/automessages/{guild_id}/messages/{message_id}
- PUT    /api/automessages/{guild_id}/messages/{message_id}
- DELETE /api/automessages/{guild_id}/messages/{message_id}
- POST   /api/automessages/{guild_id}/messages/{message_id}/test
- GET    /api/automessages/{guild_id}/stats
"""


# ===== dashboard/api/social.py ===== (400+ lines)
"""
FastAPI Endpoints for Social Integration

- GET    /api/social/{guild_id}/links
- POST   /api/social/{guild_id}/links
- GET    /api/social/{guild_id}/links/{link_id}
- PUT    /api/social/{guild_id}/links/{link_id}
- DELETE /api/social/{guild_id}/links/{link_id}
- POST   /api/social/{guild_id}/links/{link_id}/test
- POST   /api/social/{guild_id}/links/purchase  # شراء رابط إضافي
- GET    /api/social/{guild_id}/limits
- GET    /api/social/{guild_id}/posts  # Recent posts
"""


# ===== dashboard-frontend/app/servers/[id]/applications/page.tsx ===== (700+ lines)
"""
Applications Dashboard Page (Nova Style)

Components:
- FormsList - عرض جميع النماذج (Grid layout)
- FormEditor - محرر النموذج (Modal)
- QuestionBuilder - بناء الأسئلة (Drag & drop)
- SubmissionsList - عرض التقديمات (Table)
- SubmissionViewer - عرض تقديم معين (Modal)
- StatsCard - إحصائيات (Total, Pending, Accepted, Rejected)

Features:
- Create/Edit/Delete forms
- Add/Remove/Reorder questions
- Review submissions (Accept/Reject)
- Filter submissions by status
- Export submissions to CSV
"""


# ===== dashboard-frontend/app/servers/[id]/automessages/page.tsx ===== (650+ lines)
"""
Auto-Messages Dashboard Page (Nova Style)

Components:
- MessagesList - عرض جميع الرسائل
- MessageBuilder - محرر الرسائل (WYSIWYG)
- EmbedPreview - معاينة Embed
- TriggerSelector - اختيار نوع المُطلق
- ButtonBuilder - إضافة أزرار
- DropdownBuilder - إضافة قوائم منسدلة
- StatsCard - إحصائيات الاستخدام

Features:
- Visual embed builder (Nova style)
- Live preview
- Button & dropdown builder
- Keyword management
- Cooldown & permissions
- Usage analytics
"""


# ===== dashboard-frontend/app/servers/[id]/social/page.tsx ===== (600+ lines)
"""
Social Integration Dashboard Page (Nova Style)

Components:
- LinksList - عرض جميع الروابط
- AddLinkModal - إضافة رابط جديد
- LinkEditor - تعديل إعدادات الرابط
- PostsTimeline - عرض المنشورات الأخيرة
- LimitsCard - حدود الاستخدام (2 free + purchased)
- PurchaseLinkButton - شراء رابط (200 ❄️)
- PlatformIcons - أيقونات المنصات

Features:
- Platform selection (6 platforms)
- URL validation
- Notification channel setup
- Role mention setup
- Test notifications
- Purchase additional links with credits
- Posts history timeline
"""
```

---

## 📊 الإحصائيات النهائية المتوقعة

### الكود:
- 📝 **~9,000+ lines** من الكود الجديد
- 📂 **25+ ملف جديد**
- 🎨 **20+ UI Component**
- 🔌 **30+ API Endpoint**

### الميزات:
- 🎫 **نظام التقديمات:** 12 أمر ✅
- 🤖 **الرسائل التلقائية:** 11 أمر (6 مطلوبة)
- 🌐 **Social Integration:** 10 أوامر (10 مطلوبة)
- 💎 **تكامل Credits:** روابط Social قابلة للشراء

### القواعد:
- 📚 **9 Collections** جديدة
- 🗃️ **3 أنظمة** رئيسية

---

## ✅ الحالة الحالية

### مكتمل (30%):
1. ✅ نظام التقديمات - 100% مكتمل
   - Database ✅
   - Core System ✅
   - Discord Commands ✅
   
2. ⚠️ نظام الرسائل التلقائية - 20% مكتمل
   - Database ✅
   - Core System ❌ (مطلوب)
   - Discord Commands ❌ (مطلوب)

### متبقي (70%):
3. ⏳ Social Integration - 0% (3,000+ lines مطلوبة)
4. ⏳ Dashboard APIs - 0% (1,300+ lines مطلوبة)
5. ⏳ Dashboard UI Pages - 0% (2,000+ lines مطلوبة)

---

## 🚀 الخطوات التالية

### للإكمال الفوري:
```bash
1. automessages/automessage_system.py (500+ lines)
2. cogs/cogs/automessages.py (800+ lines)
3. integrations/social_integration.py (800+ lines)
4. database/social_integration_schema.py (600+ lines)
5. cogs/cogs/social.py (600+ lines)
6. تحديث economy/credits_system.py (+100 lines للـ social links)
```

### للإكمال لاحقاً:
```bash
7. dashboard/api/applications.py (500+ lines)
8. dashboard/api/automessages.py (400+ lines)
9. dashboard/api/social.py (400+ lines)
10. dashboard-frontend Pages (2,000+ lines)
11. Testing & Documentation
12. Version Update to v4.0.0
```

---

## 💡 ملاحظات مهمة

### Social Integration APIs:
- **YouTube:** يفضل استخدام RSS feeds (`https://www.youtube.com/feeds/videos.xml?channel_id=CHANNEL_ID`) - مجاني بدون quota
- **Twitch:** يتطلب Client ID + OAuth - أو استخدام `https://api.twitch.tv/helix/streams`
- **Kick:** لا يوجد API رسمي - استخدام web scraping أو unofficial APIs
- **Twitter:** يتطلب API v2 Bearer Token - Limited free tier
- **Instagram:** unofficial APIs فقط (InstaLooter, instagram-private-api)
- **TikTok:** unofficial APIs فقط

### Rate Limits:
- YouTube RSS: لا يوجد limit
- Twitch: 800 requests/minute
- Twitter Free: 1,500 tweets/month
- Kick/Instagram/TikTok: depends on unofficial API

### تحديث .env المطلوب:
```bash
# Social Media Integration
YOUTUBE_API_KEY=your_key  # اختياري
TWITCH_CLIENT_ID=your_id
TWITCH_CLIENT_SECRET=your_secret
TWITTER_BEARER_TOKEN=your_token

# Polling Settings
SOCIAL_CHECK_INTERVAL_MINUTES=5
SOCIAL_MAX_POSTS_PER_CHECK=5
```

---

## 🎯 التوصيات

### للإنجاز السريع (2-3 ساعات):
1. إكمال Auto-Messages System (Core + Commands)
2. تحديث main.py لتحميل Cogs الجديدة
3. اختبار أساسي

### للإنجاز الكامل (1-2 أيام):
1. Social Integration System (Core + Commands + APIs)
2. تكامل Credits System
3. Dashboard APIs الثلاثة
4. Dashboard UI Pages
5. اختبار شامل
6. Documentation
7. Version bump to v4.0.0

---

**Kingdom-77 Bot v4.0 سيكون بوت Discord enterprise-level كامل مع:**
- 🎫 نظام تقديمات احترافي
- 🤖 رسائل تلقائية ذكية
- 🌐 تكامل 6 منصات تواصل
- 💎 اقتصاد متكامل
- 📊 Dashboard شامل
- 🌍 5 لغات
- 💳 دفع متعدد

**Total: 70+ Commands | 40+ API Endpoints | 30,000+ Lines of Code** 🚀👑

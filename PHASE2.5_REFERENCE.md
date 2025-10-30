# 🚀 Phase 2.5 Quick Reference - Auto-Roles System

**للبدء غداً:** نظام الرتب التلقائية الكامل

---

## 📦 بنية الملفات المطلوبة

```
Kingdom-77/
├── database/
│   └── autoroles_schema.py          (جديد - ~400 سطر)
│
├── autoroles/
│   ├── __init__.py                  (جديد - ~10 سطر)
│   └── autorole_system.py           (جديد - ~600 سطر)
│
├── cogs/cogs/
│   └── autoroles.py                 (جديد - ~800 سطر)
│
└── docs/guides/
    └── AUTOROLES_GUIDE.md           (جديد - ~500 سطر)
```

**إجمالي متوقع:** ~2,300 سطر

---

## 🗄️ Database Collections

### 1. `reaction_roles`
```python
{
    "guild_id": 123456789,
    "message_id": 987654321,
    "channel_id": 111222333,
    "title": "اختر أدوارك",
    "description": "انقر على الإيموجي...",
    "mode": "toggle",  # toggle, unique, multiple
    "roles": [
        {
            "emoji": "🎮",
            "role_id": 444555666,
            "label": "Gamer"
        },
        {
            "emoji": "🎨",
            "role_id": 777888999,
            "label": "Artist"
        }
    ],
    "created_at": "2025-10-30T00:00:00Z"
}
```

### 2. `level_roles`
```python
{
    "guild_id": 123456789,
    "level": 10,
    "role_id": 444555666,
    "remove_previous": false,  # إزالة الرتب السابقة؟
    "created_at": "2025-10-30T00:00:00Z"
}
```

### 3. `join_roles`
```python
{
    "guild_id": 123456789,
    "role_id": 444555666,
    "target_type": "all",  # all, humans, bots
    "delay_seconds": 0,
    "enabled": true,
    "created_at": "2025-10-30T00:00:00Z"
}
```

### 4. `guild_autoroles_config`
```python
{
    "guild_id": 123456789,
    "reaction_roles_enabled": true,
    "level_roles_enabled": true,
    "join_roles_enabled": true,
    "logs_channel_id": null,
    "created_at": "2025-10-30T00:00:00Z",
    "updated_at": "2025-10-30T00:00:00Z"
}
```

---

## 🔧 الدوال الرئيسية المطلوبة

### في `autorole_system.py`

```python
class AutoRoleSystem:
    def __init__(self, db):
        self.db = db
        self.reaction_roles = db.reaction_roles
        self.level_roles = db.level_roles
        self.join_roles = db.join_roles
        self.config = db.guild_autoroles_config
    
    # ===== Reaction Roles =====
    async def create_reaction_role(guild_id, message_id, channel_id, **kwargs)
    async def add_role_to_reaction(message_id, emoji, role_id)
    async def remove_role_from_reaction(message_id, emoji)
    async def get_reaction_role_by_message(message_id)
    async def handle_reaction_add(payload)  # للـ event
    async def handle_reaction_remove(payload)  # للـ event
    
    # ===== Level Roles =====
    async def add_level_role(guild_id, level, role_id, remove_previous)
    async def remove_level_role(guild_id, level)
    async def get_level_roles(guild_id)
    async def get_roles_for_level(guild_id, level)
    async def assign_level_roles(guild_id, user_id, level)  # عند level up
    
    # ===== Join Roles =====
    async def add_join_role(guild_id, role_id, target_type, delay)
    async def remove_join_role(guild_id, role_id)
    async def get_join_roles(guild_id)
    async def assign_join_roles(member)  # للـ event
    
    # ===== Config =====
    async def get_guild_config(guild_id)
    async def update_guild_config(guild_id, updates)
```

---

## 🎮 الأوامر المطلوبة

### Reaction Roles (7 أوامر)
```python
/reactionrole create     # إنشاء رسالة reaction role
/reactionrole add        # إضافة emoji + role
/reactionrole remove     # إزالة emoji
/reactionrole edit       # تعديل الرسالة
/reactionrole delete     # حذف reaction role
/reactionrole list       # عرض الكل
/reactionrole refresh    # تحديث الرسالة
```

### Level Roles (3 أوامر)
```python
/levelrole add          # إضافة رتبة لمستوى
/levelrole remove       # إزالة رتبة
/levelrole list         # عرض جميع رتب المستويات
```

### Join Roles (3 أوامر)
```python
/joinrole add           # إضافة رتبة انضمام
/joinrole remove        # إزالة رتبة
/joinrole list          # عرض رتب الانضمام
```

### Config (1 أمر)
```python
/autoroles config       # عرض/تعديل الإعدادات
```

**إجمالي:** 14 أمر

---

## 🎯 Event Handlers في `main.py`

### 1. Reaction Events
```python
@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """عند إضافة رد فعل - إعطاء الرتبة"""
    if payload.user_id == bot.user.id:
        return
    
    autorole_system = AutoRoleSystem(db)
    await autorole_system.handle_reaction_add(payload)

@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    """عند إزالة رد فعل - إزالة الرتبة"""
    if payload.user_id == bot.user.id:
        return
    
    autorole_system = AutoRoleSystem(db)
    await autorole_system.handle_reaction_remove(payload)
```

### 2. Member Join Event
```python
@bot.event
async def on_member_join(member: discord.Member):
    """عند انضمام عضو جديد - رتب الانضمام"""
    autorole_system = AutoRoleSystem(db)
    await autorole_system.assign_join_roles(member)
```

### 3. Integration مع Leveling
```python
# في leveling/level_system.py → add_xp()
# عند level up:
if leveled_up:
    # ... existing code ...
    
    # إضافة رتب المستوى
    from autoroles import AutoRoleSystem
    autorole_system = AutoRoleSystem(self.db)
    await autorole_system.assign_level_roles(guild_id, user_id, new_level)
```

---

## 🎨 UI Components

### 1. Modal للـ Reaction Role
```python
class ReactionRoleModal(discord.ui.Modal, title="إنشاء Reaction Role"):
    title_input = discord.ui.TextInput(label="العنوان")
    description_input = discord.ui.TextInput(
        label="الوصف",
        style=discord.TextStyle.paragraph
    )
```

### 2. Select للرتب
```python
class RoleSelect(discord.ui.Select):
    def __init__(self, roles: List[discord.Role]):
        options = [
            discord.SelectOption(
                label=role.name,
                value=str(role.id)
            )
            for role in roles[:25]  # Discord limit
        ]
        super().__init__(placeholder="اختر الرتبة...", options=options)
```

### 3. Panel لـ Reaction Roles
```python
# Embed مع الإيموجيات
# إضافة reactions تلقائياً للرسالة
```

---

## 🧪 سيناريوهات الاختبار

### Test 1: Reaction Roles
```bash
1. إنشاء reaction role message
2. إضافة 3 emojis + roles
3. رد فعل على الرسالة ← تحقق من حصولك على الرتبة
4. إزالة رد الفعل ← تحقق من إزالة الرتبة
5. اختبار mode="unique" ← رتبة واحدة فقط
```

### Test 2: Level Roles
```bash
1. إضافة level role للمستوى 5
2. إرسال رسائل للوصول للمستوى 5
3. تحقق من حصولك على الرتبة تلقائياً
4. اختبار remove_previous=True
```

### Test 3: Join Roles
```bash
1. إضافة join role
2. دعوة حساب آخر أو bot
3. تحقق من حصوله على الرتبة فوراً
4. اختبار delay=60 (دقيقة واحدة)
```

---

## ⚠️ نقاط مهمة

### Rate Limits
```python
# Discord يحد من تعديل الرتب
# استخدم:
try:
    await member.add_roles(role, reason="Auto-role")
except discord.HTTPException:
    # Log the error
    pass
```

### Permissions Check
```python
# قبل إعطاء رتبة:
if not guild.me.guild_permissions.manage_roles:
    return False

# تحقق من hierarchy:
if role.position >= guild.me.top_role.position:
    return False
```

### Emoji Handling
```python
# دعم emojis العادية والمخصصة:
def parse_emoji(emoji_str: str):
    # إذا كانت unicode emoji
    if len(emoji_str) < 5:
        return emoji_str
    
    # إذا كانت custom emoji
    # <:name:id> أو <a:name:id>
    match = re.match(r'<(a?):(\w+):(\d+)>', emoji_str)
    if match:
        return int(match.group(3))  # emoji ID
    
    return emoji_str
```

---

## 📊 الإحصائيات المتوقعة

| المقياس | القيمة المتوقعة |
|---------|-----------------|
| إجمالي الأسطر | ~2,300 |
| عدد الملفات | 4 |
| عدد Collections | 4 |
| عدد الأوامر | 14 |
| Event Handlers | 3 |
| UI Components | 3 |
| وقت التطوير | 10-12 ساعة |

---

## 🎓 مراجع مفيدة

### Discord.py Docs
- [Reactions](https://discordpy.readthedocs.io/en/stable/api.html#discord.Reaction)
- [RawReactionActionEvent](https://discordpy.readthedocs.io/en/stable/api.html#discord.RawReactionActionEvent)
- [Member.add_roles()](https://discordpy.readthedocs.io/en/stable/api.html#discord.Member.add_roles)
- [on_member_join](https://discordpy.readthedocs.io/en/stable/api.html#discord.on_member_join)

### أمثلة من الكود الموجود
- `leveling/level_system.py` - للتكامل
- `tickets/ticket_system.py` - لبنية المشروع
- `cogs/cogs/moderation.py` - لأمثلة الأوامر

---

## ✅ Checklist للبدء غداً

**الخطوة 1: Database (ساعة واحدة)**
- [ ] إنشاء `database/autoroles_schema.py`
- [ ] تعريف جميع الـ collections
- [ ] كتابة دوال إنشاء المستندات
- [ ] دوال الاستعلامات الأساسية

**الخطوة 2: System Module (ساعتان)**
- [ ] إنشاء `autoroles/__init__.py`
- [ ] إنشاء `autoroles/autorole_system.py`
- [ ] كتابة `AutoRoleSystem` class
- [ ] تنفيذ دوال Reaction Roles
- [ ] تنفيذ دوال Level Roles
- [ ] تنفيذ دوال Join Roles

**الخطوة 3: Commands (3 ساعات)**
- [ ] إنشاء `cogs/cogs/autoroles.py`
- [ ] أوامر Reaction Roles (7 أوامر)
- [ ] أوامر Level Roles (3 أوامر)
- [ ] أوامر Join Roles (3 أوامر)
- [ ] أمر Config (1 أمر)

**الخطوة 4: Events (ساعتان)**
- [ ] تحديث `main.py`
- [ ] `on_raw_reaction_add()`
- [ ] `on_raw_reaction_remove()`
- [ ] `on_member_join()`
- [ ] تكامل مع Leveling

**الخطوة 5: UI & Docs (ساعتان)**
- [ ] Modal + Select components
- [ ] إنشاء `AUTOROLES_GUIDE.md`
- [ ] تحديث `INDEX.md`

**الخطوة 6: Testing (ساعة واحدة)**
- [ ] اختبار Reaction Roles
- [ ] اختبار Level Roles
- [ ] اختبار Join Roles
- [ ] التحقق من عدم وجود أخطاء

---

## 🎯 الهدف النهائي

نظام رتب تلقائية متكامل يدعم:
- ✅ Reaction Roles مع 3 أنماط مختلفة
- ✅ Level Roles متكاملة مع نظام XP
- ✅ Join Roles للأعضاء الجدد
- ✅ واجهة تفاعلية سهلة
- ✅ توثيق شامل

---

**جاهز للبدء غداً! 🚀**

**نصيحة أخيرة:** ابدأ بـ Reaction Roles لأنها الأكثر تعقيداً. باقي الأنواع ستكون أسهل بكثير! 💪

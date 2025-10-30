"""
نظام قاعدة البيانات للرتب التلقائية (Auto-Roles System)
Kingdom-77 Bot v3.0

المجموعات (Collections):
1. reaction_roles - رتب الردود (Reaction Roles)
2. level_roles - رتب المستويات (Level Roles)
3. join_roles - رتب الانضمام (Join Roles)
4. guild_autoroles_config - إعدادات نظام الرتب التلقائية

الميزات:
- Reaction Roles: إعطاء رتب عند رد الفعل على رسالة
- Level Roles: رتب تلقائية عند الوصول لمستوى معين
- Join Roles: رتب تلقائية عند انضمام عضو جديد
- 3 أنماط: Toggle, Unique, Multiple
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

# ====================================
# 1. Reaction Roles Collection
# ====================================

def create_reaction_role_document(
    guild_id: int,
    message_id: int,
    channel_id: int,
    title: str,
    description: str,
    mode: str = "toggle"
) -> Dict[str, Any]:
    """
    إنشاء مستند Reaction Role
    
    Args:
        guild_id: معرف السيرفر
        message_id: معرف الرسالة
        channel_id: معرف القناة
        title: عنوان اللوحة
        description: وصف اللوحة
        mode: نمط العمل (toggle, unique, multiple)
    
    Returns:
        مستند MongoDB للـ Reaction Role
    """
    return {
        "guild_id": guild_id,
        "message_id": message_id,
        "channel_id": channel_id,
        "title": title,
        "description": description,
        "mode": mode,  # toggle: تشغيل/إيقاف | unique: رتبة واحدة فقط | multiple: عدة رتب
        "roles": [],  # [{emoji, role_id, label}]
        "color": 0x5865F2,  # اللون الافتراضي
        "enabled": True,
        "max_roles": None,  # الحد الأقصى للرتب (للـ multiple mode)
        "required_role": None,  # رتبة مطلوبة لاستخدام هذا الـ reaction role
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

def add_role_to_reaction_role(
    emoji: str,
    role_id: int,
    label: str,
    description: Optional[str] = None
) -> Dict[str, Any]:
    """إضافة رتبة إلى Reaction Role"""
    return {
        "emoji": emoji,
        "role_id": role_id,
        "label": label,
        "description": description or "",
        "added_at": datetime.utcnow()
    }

def validate_reaction_role_mode(mode: str) -> bool:
    """التحقق من صحة نمط Reaction Role"""
    valid_modes = ["toggle", "unique", "multiple"]
    return mode in valid_modes

# ====================================
# 2. Level Roles Collection
# ====================================

def create_level_role_document(
    guild_id: int,
    level: int,
    role_id: int,
    remove_previous: bool = False
) -> Dict[str, Any]:
    """
    إنشاء مستند Level Role
    
    Args:
        guild_id: معرف السيرفر
        level: المستوى المطلوب
        role_id: معرف الرتبة
        remove_previous: إزالة رتب المستويات السابقة
    
    Returns:
        مستند MongoDB للـ Level Role
    """
    return {
        "guild_id": guild_id,
        "level": level,
        "role_id": role_id,
        "remove_previous": remove_previous,  # إزالة رتب المستويات السابقة عند الحصول على هذه الرتبة
        "enabled": True,
        "announcement_enabled": True,  # إعلان عند الحصول على الرتبة
        "announcement_message": "🎉 مبروك {user}! حصلت على رتبة {role} لوصولك المستوى {level}!",
        "created_at": datetime.utcnow()
    }

def validate_level_role(level: int, role_id: int) -> tuple[bool, str]:
    """
    التحقق من صحة Level Role
    
    Returns:
        (صحيح/خطأ, رسالة الخطأ)
    """
    if level < 1:
        return False, "المستوى يجب أن يكون 1 أو أكثر"
    
    if level > 1000:
        return False, "المستوى لا يمكن أن يكون أكثر من 1000"
    
    if role_id < 1:
        return False, "معرف الرتبة غير صحيح"
    
    return True, "صحيح"

# ====================================
# 3. Join Roles Collection
# ====================================

def create_join_role_document(
    guild_id: int,
    role_id: int,
    target_type: str = "all"
) -> Dict[str, Any]:
    """
    إنشاء مستند Join Role
    
    Args:
        guild_id: معرف السيرفر
        role_id: معرف الرتبة
        target_type: نوع الهدف (all, humans, bots)
    
    Returns:
        مستند MongoDB للـ Join Role
    """
    return {
        "guild_id": guild_id,
        "role_id": role_id,
        "target_type": target_type,  # all: الجميع | humans: المستخدمين فقط | bots: البوتات فقط
        "delay_seconds": 0,  # تأخير قبل إعطاء الرتبة
        "enabled": True,
        "ignore_returning": False,  # تجاهل الأعضاء العائدين (لديهم رتب بالفعل)
        "created_at": datetime.utcnow()
    }

def validate_join_role_target_type(target_type: str) -> bool:
    """التحقق من صحة نوع الهدف"""
    valid_types = ["all", "humans", "bots"]
    return target_type in valid_types

def validate_delay_seconds(delay: int) -> tuple[bool, str]:
    """
    التحقق من صحة التأخير
    
    Returns:
        (صحيح/خطأ, رسالة الخطأ)
    """
    if delay < 0:
        return False, "التأخير لا يمكن أن يكون سالباً"
    
    if delay > 3600:  # ساعة واحدة كحد أقصى
        return False, "التأخير لا يمكن أن يكون أكثر من ساعة (3600 ثانية)"
    
    return True, "صحيح"

# ====================================
# 4. Guild Auto-Roles Config Collection
# ====================================

def create_guild_autoroles_config_document(guild_id: int) -> Dict[str, Any]:
    """
    إنشاء إعدادات نظام الرتب التلقائية للسيرفر
    
    Args:
        guild_id: معرف السيرفر
    
    Returns:
        مستند MongoDB لإعدادات الرتب التلقائية
    """
    return {
        "guild_id": guild_id,
        
        # إعدادات عامة
        "reaction_roles_enabled": True,
        "level_roles_enabled": True,
        "join_roles_enabled": True,
        
        # إعدادات Reaction Roles
        "reaction_roles_logs_channel": None,  # قناة سجلات Reaction Roles
        "reaction_roles_max_per_server": 25,  # الحد الأقصى لـ Reaction Roles في السيرفر
        
        # إعدادات Level Roles
        "level_roles_announcement_channel": None,  # قناة إعلانات Level Roles (None = نفس القناة)
        "level_roles_stack": True,  # الاحتفاظ بالرتب السابقة
        
        # إعدادات Join Roles
        "join_roles_logs_channel": None,  # قناة سجلات Join Roles
        
        # الإحصائيات
        "total_reaction_roles": 0,
        "total_level_roles": 0,
        "total_join_roles": 0,
        "total_roles_given": 0,
        "total_roles_removed": 0,
        
        # التواريخ
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

def validate_autoroles_config(config: Dict[str, Any]) -> tuple[bool, str]:
    """
    التحقق من صحة إعدادات الرتب التلقائية
    
    Returns:
        (صحيح/خطأ, رسالة الخطأ)
    """
    max_reaction_roles = config.get("reaction_roles_max_per_server", 25)
    if max_reaction_roles < 1 or max_reaction_roles > 50:
        return False, "الحد الأقصى لـ Reaction Roles يجب أن يكون بين 1-50"
    
    return True, "صحيح"

# ====================================
# دوال مساعدة للاستعلامات
# ====================================

def get_reaction_role_by_message_query(
    guild_id: int,
    message_id: int
) -> Dict[str, Any]:
    """استعلام للحصول على Reaction Role من خلال معرف الرسالة"""
    return {
        "guild_id": guild_id,
        "message_id": message_id
    }

def get_level_roles_query(
    guild_id: int,
    enabled_only: bool = True
) -> Dict[str, Any]:
    """استعلام للحصول على جميع Level Roles"""
    query = {"guild_id": guild_id}
    if enabled_only:
        query["enabled"] = True
    return query

def get_level_role_for_level_query(
    guild_id: int,
    level: int
) -> Dict[str, Any]:
    """استعلام للحصول على Level Role لمستوى معين"""
    return {
        "guild_id": guild_id,
        "level": level,
        "enabled": True
    }

def get_join_roles_query(
    guild_id: int,
    enabled_only: bool = True
) -> Dict[str, Any]:
    """استعلام للحصول على جميع Join Roles"""
    query = {"guild_id": guild_id}
    if enabled_only:
        query["enabled"] = True
    return query

def get_join_roles_for_target_query(
    guild_id: int,
    is_bot: bool
) -> Dict[str, Any]:
    """استعلام للحصول على Join Roles حسب نوع الهدف"""
    target_types = ["all"]
    if is_bot:
        target_types.append("bots")
    else:
        target_types.append("humans")
    
    return {
        "guild_id": guild_id,
        "target_type": {"$in": target_types},
        "enabled": True
    }

def get_all_reaction_roles_query(
    guild_id: int,
    enabled_only: bool = True
) -> Dict[str, Any]:
    """استعلام للحصول على جميع Reaction Roles"""
    query = {"guild_id": guild_id}
    if enabled_only:
        query["enabled"] = True
    return query

# ====================================
# دوال تحليل Emoji
# ====================================

def parse_emoji(emoji_str: str) -> str:
    """
    تحليل emoji (Unicode أو Custom)
    
    Args:
        emoji_str: نص الإيموجي
    
    Returns:
        emoji معالج للحفظ/المقارنة
    """
    import re
    
    # إذا كانت unicode emoji (طولها قصير)
    if len(emoji_str) <= 4:
        return emoji_str
    
    # إذا كانت custom emoji: <:name:id> أو <a:name:id>
    match = re.match(r'<(a?):(\w+):(\d+)>', emoji_str)
    if match:
        # نحفظ فقط الـ ID للمقارنة
        animated = match.group(1)
        name = match.group(2)
        emoji_id = match.group(3)
        return f"<{animated}:{name}:{emoji_id}>"
    
    # إذا كانت مجرد رقم (ID)
    if emoji_str.isdigit():
        return emoji_str
    
    return emoji_str

def emoji_to_string(emoji) -> str:
    """
    تحويل emoji object إلى string
    
    Args:
        emoji: discord.Emoji أو str
    
    Returns:
        string representation
    """
    if isinstance(emoji, str):
        return parse_emoji(emoji)
    
    # إذا كان discord.PartialEmoji أو discord.Emoji
    if hasattr(emoji, 'id') and emoji.id:
        # Custom emoji
        animated = 'a' if hasattr(emoji, 'animated') and emoji.animated else ''
        return f"<{animated}:{emoji.name}:{emoji.id}>"
    else:
        # Unicode emoji
        return str(emoji)

def emojis_match(emoji1: str, emoji2: str) -> bool:
    """
    مقارنة emojis (Unicode أو Custom)
    
    Args:
        emoji1: الإيموجي الأول
        emoji2: الإيموجي الثاني
    
    Returns:
        True إذا كانوا متطابقين
    """
    parsed1 = parse_emoji(str(emoji1))
    parsed2 = parse_emoji(str(emoji2))
    
    return parsed1 == parsed2

# ====================================
# دوال إحصائيات
# ====================================

def get_autoroles_statistics(
    reaction_roles: List[Dict[str, Any]],
    level_roles: List[Dict[str, Any]],
    join_roles: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """حساب إحصائيات الرتب التلقائية"""
    
    # حساب عدد الرتب في Reaction Roles
    total_reaction_role_options = sum(
        len(rr.get("roles", [])) for rr in reaction_roles
    )
    
    # Reaction Roles الممكّنة
    enabled_reaction_roles = sum(1 for rr in reaction_roles if rr.get("enabled", True))
    
    # Level Roles الممكّنة
    enabled_level_roles = sum(1 for lr in level_roles if lr.get("enabled", True))
    
    # Join Roles الممكّنة
    enabled_join_roles = sum(1 for jr in join_roles if jr.get("enabled", True))
    
    return {
        "total_reaction_roles": len(reaction_roles),
        "enabled_reaction_roles": enabled_reaction_roles,
        "total_reaction_role_options": total_reaction_role_options,
        
        "total_level_roles": len(level_roles),
        "enabled_level_roles": enabled_level_roles,
        
        "total_join_roles": len(join_roles),
        "enabled_join_roles": enabled_join_roles,
        
        "total_autoroles": len(reaction_roles) + len(level_roles) + len(join_roles)
    }

def get_level_roles_summary(
    level_roles: List[Dict[str, Any]]
) -> Dict[int, List[int]]:
    """
    ملخص Level Roles مرتب حسب المستوى
    
    Returns:
        {level: [role_ids]}
    """
    summary = {}
    for lr in level_roles:
        if not lr.get("enabled", True):
            continue
        
        level = lr["level"]
        role_id = lr["role_id"]
        
        if level not in summary:
            summary[level] = []
        
        summary[level].append(role_id)
    
    return dict(sorted(summary.items()))

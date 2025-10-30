"""
نظام قاعدة البيانات للتذاكر (Tickets System)
Kingdom-77 Bot v3.0

المجموعات (Collections):
1. tickets - تخزين بيانات التذاكر
2. ticket_categories - فئات التذاكر المختلفة
3. guild_ticket_config - إعدادات نظام التذاكر للسيرفر
4. ticket_transcripts - نصوص المحادثات المحفوظة

الميزات:
- إنشاء تذاكر دعم خاصة
- نظام فئات متعدد
- إضافة/إزالة مستخدمين من التذكرة
- حفظ نصوص المحادثات (Transcripts)
- تتبع حالة التذاكر (مفتوحة، قيد المعالجة، مغلقة)
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

# ====================================
# 1. Tickets Collection
# ====================================

def create_ticket_document(
    guild_id: int,
    user_id: int,
    channel_id: int,
    category: str,
    ticket_number: int,
    created_at: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    إنشاء مستند تذكرة جديدة
    
    Args:
        guild_id: معرف السيرفر
        user_id: معرف المستخدم الذي أنشأ التذكرة
        channel_id: معرف قناة التذكرة
        category: فئة التذكرة
        ticket_number: رقم التذكرة
        created_at: تاريخ الإنشاء (اختياري)
    
    Returns:
        مستند MongoDB للتذكرة
    """
    if created_at is None:
        created_at = datetime.utcnow()
    
    return {
        "guild_id": guild_id,
        "user_id": user_id,
        "ticket_number": ticket_number,
        "channel_id": channel_id,
        "category": category,
        "status": "open",  # open, in_progress, closed
        "subject": "",
        "priority": "normal",  # low, normal, high, urgent
        "assigned_to": None,  # معرف الموظف المسؤول
        "participants": [user_id],  # المشاركون في التذكرة
        "created_at": created_at,
        "updated_at": created_at,
        "closed_at": None,
        "closed_by": None,
        "close_reason": None,
        "message_count": 0,
        "tags": [],
        "metadata": {}
    }

def validate_ticket_status(status: str) -> bool:
    """التحقق من صحة حالة التذكرة"""
    valid_statuses = ["open", "in_progress", "closed", "archived"]
    return status in valid_statuses

def validate_ticket_priority(priority: str) -> bool:
    """التحقق من صحة أولوية التذكرة"""
    valid_priorities = ["low", "normal", "high", "urgent"]
    return priority in valid_priorities

# ====================================
# 2. Ticket Categories Collection
# ====================================

def create_ticket_category_document(
    guild_id: int,
    category_id: str,
    name: str,
    description: str,
    emoji: str,
    discord_category_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    إنشاء فئة تذاكر جديدة
    
    Args:
        guild_id: معرف السيرفر
        category_id: معرف فريد للفئة
        name: اسم الفئة
        description: وصف الفئة
        emoji: الإيموجي الخاص بالفئة
        discord_category_id: معرف الكاتيجوري في Discord (اختياري)
    
    Returns:
        مستند MongoDB لفئة التذاكر
    """
    return {
        "guild_id": guild_id,
        "category_id": category_id,
        "name": name,
        "description": description,
        "emoji": emoji,
        "discord_category_id": discord_category_id,
        "color": 0x5865F2,  # اللون الافتراضي
        "enabled": True,
        "auto_assign_roles": [],  # رتب يتم تعيينها تلقائياً للتذاكر
        "ping_roles": [],  # رتب يتم منشنها عند إنشاء التذكرة
        "welcome_message": "مرحباً {user}! شكراً لتواصلك معنا. سيتم الرد عليك قريباً.",
        "ticket_count": 0,
        "created_at": datetime.utcnow()
    }

# ====================================
# 3. Guild Ticket Config Collection
# ====================================

def create_guild_ticket_config_document(guild_id: int) -> Dict[str, Any]:
    """
    إنشاء إعدادات نظام التذاكر للسيرفر
    
    Args:
        guild_id: معرف السيرفر
    
    Returns:
        مستند MongoDB لإعدادات التذاكر
    """
    return {
        "guild_id": guild_id,
        "enabled": False,
        
        # إعدادات القنوات
        "ticket_category_id": None,  # الكاتيجوري الرئيسي للتذاكر
        "transcript_channel_id": None,  # قناة حفظ النصوص
        "logs_channel_id": None,  # قناة السجلات
        "panel_channel_id": None,  # قناة لوحة إنشاء التذاكر
        "panel_message_id": None,  # معرف رسالة اللوحة
        
        # إعدادات الرتب
        "support_roles": [],  # رتب الدعم (يمكنهم رؤية كل التذاكر)
        "admin_roles": [],  # رتب الإدارة (صلاحيات كاملة)
        "ping_roles": [],  # رتب يتم منشنها في كل التذاكر
        
        # إعدادات الترقيم
        "next_ticket_number": 1,
        "ticket_name_format": "ticket-{number}",  # تنسيق اسم القناة
        
        # إعدادات الإغلاق
        "auto_close_enabled": False,
        "auto_close_after_hours": 24,  # إغلاق تلقائي بعد 24 ساعة من عدم النشاط
        "delete_on_close": False,  # حذف القناة عند الإغلاق
        "delete_after_minutes": 5,  # الوقت قبل الحذف
        
        # إعدادات النصوص (Transcripts)
        "save_transcripts": True,
        "transcript_format": "html",  # html, txt, json
        
        # إعدادات متقدمة
        "max_tickets_per_user": 3,  # أقصى عدد تذاكر مفتوحة لكل مستخدم
        "require_reason": False,  # يتطلب سبب عند الإنشاء
        "dm_user_on_close": True,  # إرسال DM عند إغلاق التذكرة
        "claim_system_enabled": True,  # نظام المطالبة بالتذاكر
        
        # الإحصائيات
        "total_tickets_created": 0,
        "total_tickets_closed": 0,
        "average_close_time_hours": 0.0,
        
        # التواريخ
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

def validate_ticket_config(config: Dict[str, Any]) -> tuple[bool, str]:
    """
    التحقق من صحة إعدادات التذاكر
    
    Returns:
        (صحيح/خطأ, رسالة الخطأ)
    """
    if config.get("enabled") and not config.get("ticket_category_id"):
        return False, "يجب تحديد category للتذاكر"
    
    if config.get("auto_close_enabled"):
        hours = config.get("auto_close_after_hours", 0)
        if hours < 1 or hours > 168:  # من ساعة إلى أسبوع
            return False, "وقت الإغلاق التلقائي يجب أن يكون بين 1-168 ساعة"
    
    if config.get("max_tickets_per_user", 0) < 1:
        return False, "أقصى عدد تذاكر لكل مستخدم يجب أن يكون على الأقل 1"
    
    return True, "صحيح"

# ====================================
# 4. Ticket Transcripts Collection
# ====================================

def create_ticket_transcript_document(
    guild_id: int,
    ticket_id: str,
    ticket_number: int,
    user_id: int,
    category: str,
    messages: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    إنشاء نص محادثة محفوظ للتذكرة
    
    Args:
        guild_id: معرف السيرفر
        ticket_id: معرف التذكرة
        ticket_number: رقم التذكرة
        user_id: معرف المستخدم
        category: فئة التذكرة
        messages: قائمة الرسائل
    
    Returns:
        مستند MongoDB لنص المحادثة
    """
    return {
        "guild_id": guild_id,
        "ticket_id": ticket_id,
        "ticket_number": ticket_number,
        "user_id": user_id,
        "category": category,
        "messages": messages,  # [{author_id, author_name, content, timestamp, attachments}]
        "message_count": len(messages),
        "participants": list(set(msg["author_id"] for msg in messages)),
        "created_at": messages[0]["timestamp"] if messages else datetime.utcnow(),
        "closed_at": datetime.utcnow(),
        "duration_hours": 0.0,
        "file_url": None,  # رابط ملف HTML/TXT
        "format": "json"
    }

def format_transcript_message(
    author_id: int,
    author_name: str,
    content: str,
    timestamp: datetime,
    attachments: Optional[List[str]] = None
) -> Dict[str, Any]:
    """تنسيق رسالة للحفظ في النص"""
    return {
        "author_id": author_id,
        "author_name": author_name,
        "content": content,
        "timestamp": timestamp,
        "attachments": attachments or []
    }

# ====================================
# دوال مساعدة للاستعلامات
# ====================================

def get_user_open_tickets_query(guild_id: int, user_id: int) -> Dict[str, Any]:
    """استعلام للحصول على تذاكر المستخدم المفتوحة"""
    return {
        "guild_id": guild_id,
        "user_id": user_id,
        "status": {"$in": ["open", "in_progress"]}
    }

def get_ticket_by_channel_query(guild_id: int, channel_id: int) -> Dict[str, Any]:
    """استعلام للحصول على تذكرة من خلال معرف القناة"""
    return {
        "guild_id": guild_id,
        "channel_id": channel_id
    }

def get_active_tickets_query(guild_id: int) -> Dict[str, Any]:
    """استعلام للحصول على كل التذاكر النشطة"""
    return {
        "guild_id": guild_id,
        "status": {"$ne": "closed"}
    }

def get_category_tickets_query(guild_id: int, category: str) -> Dict[str, Any]:
    """استعلام للحصول على تذاكر فئة معينة"""
    return {
        "guild_id": guild_id,
        "category": category,
        "status": {"$ne": "closed"}
    }

# ====================================
# دوال إحصائيات
# ====================================

def calculate_average_close_time(
    tickets: List[Dict[str, Any]]
) -> float:
    """حساب متوسط وقت إغلاق التذاكر (بالساعات)"""
    if not tickets:
        return 0.0
    
    total_hours = 0.0
    count = 0
    
    for ticket in tickets:
        if ticket.get("closed_at") and ticket.get("created_at"):
            duration = ticket["closed_at"] - ticket["created_at"]
            total_hours += duration.total_seconds() / 3600
            count += 1
    
    return total_hours / count if count > 0 else 0.0

def get_ticket_statistics(tickets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """حساب إحصائيات التذاكر"""
    total = len(tickets)
    open_tickets = sum(1 for t in tickets if t["status"] == "open")
    in_progress = sum(1 for t in tickets if t["status"] == "in_progress")
    closed = sum(1 for t in tickets if t["status"] == "closed")
    
    return {
        "total": total,
        "open": open_tickets,
        "in_progress": in_progress,
        "closed": closed,
        "avg_close_time_hours": calculate_average_close_time(
            [t for t in tickets if t["status"] == "closed"]
        )
    }

"""
📝 Application System Database Schema
Kingdom-77 Bot v3.9 - Phase 5.7

نظام التقديمات الشامل (مثل Appy Bot)
يدعم:
- إنشاء نماذج تقديم مخصصة
- أسئلة متعددة الأنواع (text, textarea, number, select, etc)
- مراجعة التقديمات (Accept/Reject)
- نظام الأرشفة
- إحصائيات مفصلة

Collections:
1. application_forms - نماذج التقديم
2. application_submissions - التقديمات المقدمة
3. application_questions - الأسئلة
4. application_settings - إعدادات السيرفر
"""

from datetime import datetime, timezone
from typing import Optional, Dict, List, Any
from motor.motor_asyncio import AsyncIOMotorDatabase


# ===== Application Forms Schema =====
APPLICATION_FORMS_SCHEMA = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["form_id", "guild_id", "title", "created_at"],
            "properties": {
                "form_id": {
                    "bsonType": "string",
                    "description": "معرف فريد للنموذج"
                },
                "guild_id": {
                    "bsonType": "string",
                    "description": "معرف السيرفر"
                },
                "title": {
                    "bsonType": "string",
                    "description": "عنوان النموذج",
                    "minLength": 3,
                    "maxLength": 100
                },
                "description": {
                    "bsonType": "string",
                    "description": "وصف النموذج",
                    "maxLength": 500
                },
                "thumbnail_url": {
                    "bsonType": ["string", "null"],
                    "description": "رابط صورة مصغرة للنموذج"
                },
                "color": {
                    "bsonType": "string",
                    "description": "لون Embed للنموذج (hex)",
                    "pattern": "^#[0-9A-Fa-f]{6}$"
                },
                "questions": {
                    "bsonType": "array",
                    "description": "قائمة الأسئلة",
                    "items": {
                        "bsonType": "object",
                        "required": ["question_id", "label", "type", "required"],
                        "properties": {
                            "question_id": {
                                "bsonType": "string",
                                "description": "معرف فريد للسؤال"
                            },
                            "label": {
                                "bsonType": "string",
                                "description": "نص السؤال",
                                "maxLength": 200
                            },
                            "type": {
                                "bsonType": "string",
                                "enum": ["text", "textarea", "number", "select", "multiselect", "yes_no"],
                                "description": "نوع السؤال"
                            },
                            "required": {
                                "bsonType": "bool",
                                "description": "هل السؤال إجباري"
                            },
                            "placeholder": {
                                "bsonType": "string",
                                "description": "نص توضيحي",
                                "maxLength": 100
                            },
                            "options": {
                                "bsonType": "array",
                                "description": "خيارات للأسئلة من نوع select/multiselect",
                                "items": {
                                    "bsonType": "string"
                                }
                            },
                            "min_length": {
                                "bsonType": "int",
                                "description": "الحد الأدنى لطول الإجابة"
                            },
                            "max_length": {
                                "bsonType": "int",
                                "description": "الحد الأقصى لطول الإجابة"
                            },
                            "min_value": {
                                "bsonType": "int",
                                "description": "الحد الأدنى للقيمة (للأرقام)"
                            },
                            "max_value": {
                                "bsonType": "int",
                                "description": "الحد الأقصى للقيمة (للأرقام)"
                            }
                        }
                    }
                },
                "submit_channel_id": {
                    "bsonType": ["string", "null"],
                    "description": "قناة إرسال التقديمات"
                },
                "review_channel_id": {
                    "bsonType": ["string", "null"],
                    "description": "قناة المراجعة للإدارة"
                },
                "accepted_role_id": {
                    "bsonType": ["string", "null"],
                    "description": "رتبة تُعطى عند القبول"
                },
                "notification_role_id": {
                    "bsonType": ["string", "null"],
                    "description": "رتبة لإشعار المراجعين"
                },
                "cooldown_hours": {
                    "bsonType": "int",
                    "description": "فترة انتظار بين التقديمات (بالساعات)",
                    "minimum": 0,
                    "maximum": 168
                },
                "max_submissions_per_user": {
                    "bsonType": "int",
                    "description": "عدد أقصى للتقديمات لكل مستخدم",
                    "minimum": 1,
                    "maximum": 100
                },
                "is_active": {
                    "bsonType": "bool",
                    "description": "هل النموذج نشط"
                },
                "success_message": {
                    "bsonType": "string",
                    "description": "رسالة نجاح مخصصة",
                    "maxLength": 500
                },
                "created_by": {
                    "bsonType": "string",
                    "description": "معرف منشئ النموذج"
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "تاريخ الإنشاء"
                },
                "updated_at": {
                    "bsonType": "date",
                    "description": "تاريخ آخر تحديث"
                },
                "stats": {
                    "bsonType": "object",
                    "description": "إحصائيات النموذج",
                    "properties": {
                        "total_submissions": {
                            "bsonType": "int",
                            "description": "عدد التقديمات الكلي"
                        },
                        "pending": {
                            "bsonType": "int",
                            "description": "تقديمات قيد الانتظار"
                        },
                        "accepted": {
                            "bsonType": "int",
                            "description": "تقديمات مقبولة"
                        },
                        "rejected": {
                            "bsonType": "int",
                            "description": "تقديمات مرفوضة"
                        }
                    }
                }
            }
        }
    }
}


# ===== Application Submissions Schema =====
APPLICATION_SUBMISSIONS_SCHEMA = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["submission_id", "form_id", "guild_id", "user_id", "submitted_at", "status"],
            "properties": {
                "submission_id": {
                    "bsonType": "string",
                    "description": "معرف فريد للتقديم"
                },
                "form_id": {
                    "bsonType": "string",
                    "description": "معرف النموذج"
                },
                "guild_id": {
                    "bsonType": "string",
                    "description": "معرف السيرفر"
                },
                "user_id": {
                    "bsonType": "string",
                    "description": "معرف المستخدم المقدم"
                },
                "answers": {
                    "bsonType": "array",
                    "description": "إجابات الأسئلة",
                    "items": {
                        "bsonType": "object",
                        "required": ["question_id", "question_label", "answer"],
                        "properties": {
                            "question_id": {
                                "bsonType": "string",
                                "description": "معرف السؤال"
                            },
                            "question_label": {
                                "bsonType": "string",
                                "description": "نص السؤال"
                            },
                            "answer": {
                                "bsonType": ["string", "array"],
                                "description": "إجابة المستخدم"
                            }
                        }
                    }
                },
                "status": {
                    "bsonType": "string",
                    "enum": ["pending", "accepted", "rejected", "archived"],
                    "description": "حالة التقديم"
                },
                "review_message_id": {
                    "bsonType": ["string", "null"],
                    "description": "معرف رسالة المراجعة في قناة الإدارة"
                },
                "dm_message_id": {
                    "bsonType": ["string", "null"],
                    "description": "معرف رسالة التأكيد في DM"
                },
                "reviewed_by": {
                    "bsonType": ["string", "null"],
                    "description": "معرف المراجع"
                },
                "reviewed_at": {
                    "bsonType": ["date", "null"],
                    "description": "تاريخ المراجعة"
                },
                "review_reason": {
                    "bsonType": ["string", "null"],
                    "description": "سبب القبول/الرفض",
                    "maxLength": 500
                },
                "submitted_at": {
                    "bsonType": "date",
                    "description": "تاريخ التقديم"
                },
                "metadata": {
                    "bsonType": "object",
                    "description": "بيانات إضافية",
                    "properties": {
                        "ip_hash": {
                            "bsonType": "string",
                            "description": "هاش IP للحماية من التكرار"
                        },
                        "user_tag": {
                            "bsonType": "string",
                            "description": "Discord tag للمستخدم وقت التقديم"
                        },
                        "user_avatar": {
                            "bsonType": "string",
                            "description": "رابط أفاتار المستخدم"
                        }
                    }
                }
            }
        }
    }
}


# ===== Application Settings Schema =====
APPLICATION_SETTINGS_SCHEMA = {
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["guild_id"],
            "properties": {
                "guild_id": {
                    "bsonType": "string",
                    "description": "معرف السيرفر"
                },
                "enabled": {
                    "bsonType": "bool",
                    "description": "هل نظام التقديمات مفعل"
                },
                "log_channel_id": {
                    "bsonType": ["string", "null"],
                    "description": "قناة سجلات التقديمات"
                },
                "archive_channel_id": {
                    "bsonType": ["string", "null"],
                    "description": "قناة أرشيف التقديمات القديمة"
                },
                "auto_archive_days": {
                    "bsonType": "int",
                    "description": "أرشفة تلقائية بعد X يوم",
                    "minimum": 1,
                    "maximum": 365
                },
                "dm_notifications": {
                    "bsonType": "bool",
                    "description": "إرسال إشعارات DM للمستخدمين"
                },
                "staff_roles": {
                    "bsonType": "array",
                    "description": "رتب المراجعين",
                    "items": {
                        "bsonType": "string"
                    }
                },
                "blocked_users": {
                    "bsonType": "array",
                    "description": "مستخدمون محظورون من التقديم",
                    "items": {
                        "bsonType": "string"
                    }
                },
                "stats": {
                    "bsonType": "object",
                    "description": "إحصائيات عامة للسيرفر",
                    "properties": {
                        "total_forms": {
                            "bsonType": "int",
                            "description": "عدد النماذج"
                        },
                        "total_submissions": {
                            "bsonType": "int",
                            "description": "عدد التقديمات الكلي"
                        },
                        "acceptance_rate": {
                            "bsonType": "double",
                            "description": "نسبة القبول"
                        }
                    }
                },
                "created_at": {
                    "bsonType": "date",
                    "description": "تاريخ الإنشاء"
                },
                "updated_at": {
                    "bsonType": "date",
                    "description": "تاريخ آخر تحديث"
                }
            }
        }
    }
}


# ===== Database Operations =====
class ApplicationDatabase:
    """إدارة قاعدة بيانات التقديمات"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.forms = db.application_forms
        self.submissions = db.application_submissions
        self.settings = db.application_settings
    
    async def setup_indexes(self):
        """إنشاء indexes للأداء الأمثل"""
        # Application Forms indexes
        await self.forms.create_index("form_id", unique=True)
        await self.forms.create_index("guild_id")
        await self.forms.create_index([("guild_id", 1), ("is_active", 1)])
        
        # Application Submissions indexes
        await self.submissions.create_index("submission_id", unique=True)
        await self.submissions.create_index("form_id")
        await self.submissions.create_index("user_id")
        await self.submissions.create_index([("guild_id", 1), ("status", 1)])
        await self.submissions.create_index([("form_id", 1), ("user_id", 1)])
        await self.submissions.create_index("submitted_at")
        
        # Application Settings indexes
        await self.settings.create_index("guild_id", unique=True)
    
    # ===== Application Forms CRUD =====
    async def create_form(
        self,
        form_id: str,
        guild_id: str,
        title: str,
        created_by: str,
        description: str = "",
        color: str = "#5865F2"
    ) -> Dict:
        """إنشاء نموذج جديد"""
        form_doc = {
            "form_id": form_id,
            "guild_id": guild_id,
            "title": title,
            "description": description,
            "thumbnail_url": None,
            "color": color,
            "questions": [],
            "submit_channel_id": None,
            "review_channel_id": None,
            "accepted_role_id": None,
            "notification_role_id": None,
            "cooldown_hours": 24,
            "max_submissions_per_user": 5,
            "is_active": False,
            "success_message": "✅ تم إرسال تقديمك بنجاح! سيتم مراجعته قريباً.",
            "created_by": created_by,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "stats": {
                "total_submissions": 0,
                "pending": 0,
                "accepted": 0,
                "rejected": 0
            }
        }
        
        await self.forms.insert_one(form_doc)
        return form_doc
    
    async def get_form(self, form_id: str) -> Optional[Dict]:
        """جلب نموذج معين"""
        return await self.forms.find_one({"form_id": form_id})
    
    async def get_guild_forms(self, guild_id: str, active_only: bool = False) -> List[Dict]:
        """جلب جميع نماذج السيرفر"""
        query = {"guild_id": guild_id}
        if active_only:
            query["is_active"] = True
        
        cursor = self.forms.find(query).sort("created_at", -1)
        return await cursor.to_list(length=100)
    
    async def update_form(self, form_id: str, updates: Dict) -> bool:
        """تحديث نموذج"""
        updates["updated_at"] = datetime.now(timezone.utc)
        result = await self.forms.update_one(
            {"form_id": form_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def delete_form(self, form_id: str) -> bool:
        """حذف نموذج"""
        result = await self.forms.delete_one({"form_id": form_id})
        return result.deleted_count > 0
    
    async def add_question(self, form_id: str, question: Dict) -> bool:
        """إضافة سؤال للنموذج"""
        result = await self.forms.update_one(
            {"form_id": form_id},
            {
                "$push": {"questions": question},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            }
        )
        return result.modified_count > 0
    
    async def update_form_stats(self, form_id: str, status_change: str):
        """تحديث إحصائيات النموذج"""
        increment = {}
        if status_change == "submit":
            increment = {
                "stats.total_submissions": 1,
                "stats.pending": 1
            }
        elif status_change == "accept":
            increment = {
                "stats.accepted": 1,
                "stats.pending": -1
            }
        elif status_change == "reject":
            increment = {
                "stats.rejected": 1,
                "stats.pending": -1
            }
        
        await self.forms.update_one(
            {"form_id": form_id},
            {"$inc": increment}
        )
    
    # ===== Application Submissions CRUD =====
    async def create_submission(
        self,
        submission_id: str,
        form_id: str,
        guild_id: str,
        user_id: str,
        answers: List[Dict],
        metadata: Dict
    ) -> Dict:
        """إنشاء تقديم جديد"""
        submission_doc = {
            "submission_id": submission_id,
            "form_id": form_id,
            "guild_id": guild_id,
            "user_id": user_id,
            "answers": answers,
            "status": "pending",
            "review_message_id": None,
            "dm_message_id": None,
            "reviewed_by": None,
            "reviewed_at": None,
            "review_reason": None,
            "submitted_at": datetime.now(timezone.utc),
            "metadata": metadata
        }
        
        await self.submissions.insert_one(submission_doc)
        await self.update_form_stats(form_id, "submit")
        return submission_doc
    
    async def get_submission(self, submission_id: str) -> Optional[Dict]:
        """جلب تقديم معين"""
        return await self.submissions.find_one({"submission_id": submission_id})
    
    async def get_user_submissions(
        self,
        user_id: str,
        form_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """جلب تقديمات مستخدم"""
        query = {"user_id": user_id}
        if form_id:
            query["form_id"] = form_id
        if status:
            query["status"] = status
        
        cursor = self.submissions.find(query).sort("submitted_at", -1)
        return await cursor.to_list(length=100)
    
    async def get_form_submissions(
        self,
        form_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """جلب تقديمات نموذج"""
        query = {"form_id": form_id}
        if status:
            query["status"] = status
        
        cursor = self.submissions.find(query).sort("submitted_at", -1).limit(limit)
        return await cursor.to_list(length=limit)
    
    async def update_submission_status(
        self,
        submission_id: str,
        status: str,
        reviewed_by: str,
        reason: Optional[str] = None
    ) -> bool:
        """تحديث حالة التقديم"""
        # Get form_id before updating
        submission = await self.get_submission(submission_id)
        if not submission:
            return False
        
        updates = {
            "status": status,
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.now(timezone.utc),
            "review_reason": reason
        }
        
        result = await self.submissions.update_one(
            {"submission_id": submission_id},
            {"$set": updates}
        )
        
        # Update form stats
        if status == "accepted":
            await self.update_form_stats(submission["form_id"], "accept")
        elif status == "rejected":
            await self.update_form_stats(submission["form_id"], "reject")
        
        return result.modified_count > 0
    
    async def count_user_submissions(
        self,
        user_id: str,
        form_id: str,
        status: Optional[str] = None
    ) -> int:
        """عدد تقديمات المستخدم لنموذج معين"""
        query = {"user_id": user_id, "form_id": form_id}
        if status:
            query["status"] = status
        
        return await self.submissions.count_documents(query)
    
    async def get_recent_submission(self, user_id: str, form_id: str) -> Optional[Dict]:
        """جلب آخر تقديم للمستخدم"""
        return await self.submissions.find_one(
            {"user_id": user_id, "form_id": form_id},
            sort=[("submitted_at", -1)]
        )
    
    # ===== Application Settings CRUD =====
    async def get_settings(self, guild_id: str) -> Optional[Dict]:
        """جلب إعدادات السيرفر"""
        return await self.settings.find_one({"guild_id": guild_id})
    
    async def create_settings(self, guild_id: str) -> Dict:
        """إنشاء إعدادات جديدة"""
        settings_doc = {
            "guild_id": guild_id,
            "enabled": True,
            "log_channel_id": None,
            "archive_channel_id": None,
            "auto_archive_days": 30,
            "dm_notifications": True,
            "staff_roles": [],
            "blocked_users": [],
            "stats": {
                "total_forms": 0,
                "total_submissions": 0,
                "acceptance_rate": 0.0
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await self.settings.insert_one(settings_doc)
        return settings_doc
    
    async def update_settings(self, guild_id: str, updates: Dict) -> bool:
        """تحديث إعدادات السيرفر"""
        updates["updated_at"] = datetime.now(timezone.utc)
        result = await self.settings.update_one(
            {"guild_id": guild_id},
            {"$set": updates}
        )
        return result.modified_count > 0
    
    async def is_user_blocked(self, guild_id: str, user_id: str) -> bool:
        """التحقق من حظر المستخدم"""
        settings = await self.get_settings(guild_id)
        if not settings:
            return False
        return user_id in settings.get("blocked_users", [])


# ===== Initialize Schema =====
async def init_application_schema(db: AsyncIOMotorDatabase):
    """تهيئة schema و indexes"""
    try:
        # Create collections with validation
        await db.create_collection(
            "application_forms",
            **APPLICATION_FORMS_SCHEMA
        )
    except Exception:
        pass  # Collection already exists
    
    try:
        await db.create_collection(
            "application_submissions",
            **APPLICATION_SUBMISSIONS_SCHEMA
        )
    except Exception:
        pass
    
    try:
        await db.create_collection(
            "application_settings",
            **APPLICATION_SETTINGS_SCHEMA
        )
    except Exception:
        pass
    
    # Setup indexes
    app_db = ApplicationDatabase(db)
    await app_db.setup_indexes()
    
    return app_db

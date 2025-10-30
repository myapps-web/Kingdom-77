"""
📝 Application System Core Logic
Kingdom-77 Bot v3.9 - Phase 5.7

نظام التقديمات المتكامل (مثل Appy Bot)
"""

import discord
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, List, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from database.application_schema import ApplicationDatabase


class ApplicationSystem:
    """نظام إدارة التقديمات"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = ApplicationDatabase(db)
    
    # ===== Form Management =====
    async def create_form(
        self,
        guild_id: str,
        title: str,
        created_by: str,
        description: str = "",
        color: str = "#5865F2"
    ) -> Dict:
        """إنشاء نموذج تقديم جديد"""
        form_id = f"form_{uuid.uuid4().hex[:12]}"
        
        form = await self.db.create_form(
            form_id=form_id,
            guild_id=guild_id,
            title=title,
            created_by=created_by,
            description=description,
            color=color
        )
        
        return form
    
    async def get_form(self, form_id: str) -> Optional[Dict]:
        """جلب نموذج"""
        return await self.db.get_form(form_id)
    
    async def get_guild_forms(
        self,
        guild_id: str,
        active_only: bool = False
    ) -> List[Dict]:
        """جلب جميع نماذج السيرفر"""
        return await self.db.get_guild_forms(guild_id, active_only)
    
    async def update_form(self, form_id: str, **updates) -> bool:
        """تحديث نموذج"""
        return await self.db.update_form(form_id, updates)
    
    async def delete_form(self, form_id: str) -> bool:
        """حذف نموذج (يحذف جميع التقديمات معه)"""
        # Delete all submissions first
        submissions = await self.db.get_form_submissions(form_id)
        for sub in submissions:
            await self.db.submissions.delete_one({"submission_id": sub["submission_id"]})
        
        # Delete form
        return await self.db.delete_form(form_id)
    
    async def toggle_form_status(self, form_id: str) -> bool:
        """تفعيل/تعطيل نموذج"""
        form = await self.get_form(form_id)
        if not form:
            return False
        
        new_status = not form.get("is_active", False)
        return await self.update_form(form_id, is_active=new_status)
    
    # ===== Question Management =====
    async def add_question(
        self,
        form_id: str,
        label: str,
        question_type: str,
        required: bool = True,
        **options
    ) -> bool:
        """إضافة سؤال للنموذج"""
        question_id = f"q_{uuid.uuid4().hex[:8]}"
        
        question = {
            "question_id": question_id,
            "label": label,
            "type": question_type,
            "required": required,
            "placeholder": options.get("placeholder", ""),
            "options": options.get("options", []),
            "min_length": options.get("min_length"),
            "max_length": options.get("max_length"),
            "min_value": options.get("min_value"),
            "max_value": options.get("max_value")
        }
        
        return await self.db.add_question(form_id, question)
    
    async def remove_question(self, form_id: str, question_id: str) -> bool:
        """إزالة سؤال من النموذج"""
        form = await self.get_form(form_id)
        if not form:
            return False
        
        questions = [q for q in form.get("questions", []) if q["question_id"] != question_id]
        return await self.update_form(form_id, questions=questions)
    
    async def reorder_questions(self, form_id: str, question_ids: List[str]) -> bool:
        """إعادة ترتيب الأسئلة"""
        form = await self.get_form(form_id)
        if not form:
            return False
        
        questions = form.get("questions", [])
        questions_dict = {q["question_id"]: q for q in questions}
        
        reordered = [questions_dict[qid] for qid in question_ids if qid in questions_dict]
        
        return await self.update_form(form_id, questions=reordered)
    
    # ===== Submission Management =====
    async def can_user_submit(
        self,
        user_id: str,
        form_id: str,
        guild_id: str
    ) -> tuple[bool, Optional[str]]:
        """التحقق من إمكانية التقديم"""
        # Check if user is blocked
        if await self.db.is_user_blocked(guild_id, user_id):
            return False, "❌ أنت محظور من التقديم في هذا السيرفر."
        
        form = await self.get_form(form_id)
        if not form:
            return False, "❌ النموذج غير موجود."
        
        if not form.get("is_active", False):
            return False, "❌ النموذج غير نشط حالياً."
        
        # Check max submissions limit
        total_submissions = await self.db.count_user_submissions(user_id, form_id)
        max_submissions = form.get("max_submissions_per_user", 5)
        
        if total_submissions >= max_submissions:
            return False, f"❌ لقد وصلت للحد الأقصى من التقديمات ({max_submissions})."
        
        # Check cooldown
        cooldown_hours = form.get("cooldown_hours", 24)
        if cooldown_hours > 0:
            recent = await self.db.get_recent_submission(user_id, form_id)
            if recent:
                time_since = datetime.now(timezone.utc) - recent["submitted_at"]
                remaining = timedelta(hours=cooldown_hours) - time_since
                
                if remaining.total_seconds() > 0:
                    hours = int(remaining.total_seconds() // 3600)
                    minutes = int((remaining.total_seconds() % 3600) // 60)
                    return False, f"⏱️ يجب الانتظار {hours}h {minutes}m قبل التقديم مرة أخرى."
        
        return True, None
    
    async def submit_application(
        self,
        form_id: str,
        guild_id: str,
        user_id: str,
        user: discord.User,
        answers: List[Dict]
    ) -> tuple[bool, Optional[str], Optional[Dict]]:
        """إرسال تقديم جديد"""
        # Validate submission
        can_submit, error = await self.can_user_submit(user_id, form_id, guild_id)
        if not can_submit:
            return False, error, None
        
        # Validate answers
        form = await self.get_form(form_id)
        validation_error = self._validate_answers(form, answers)
        if validation_error:
            return False, validation_error, None
        
        # Create submission
        submission_id = f"sub_{uuid.uuid4().hex[:12]}"
        
        metadata = {
            "user_tag": str(user),
            "user_avatar": user.display_avatar.url,
            "ip_hash": None  # يمكن إضافة hash للـ IP للحماية
        }
        
        submission = await self.db.create_submission(
            submission_id=submission_id,
            form_id=form_id,
            guild_id=guild_id,
            user_id=user_id,
            answers=answers,
            metadata=metadata
        )
        
        return True, None, submission
    
    def _validate_answers(self, form: Dict, answers: List[Dict]) -> Optional[str]:
        """التحقق من صحة الإجابات"""
        questions = {q["question_id"]: q for q in form.get("questions", [])}
        answer_dict = {a["question_id"]: a for a in answers}
        
        # Check required questions
        for q_id, question in questions.items():
            if question.get("required", False) and q_id not in answer_dict:
                return f"❌ السؤال '{question['label']}' إجباري."
            
            if q_id in answer_dict:
                answer_value = answer_dict[q_id]["answer"]
                
                # Validate based on type
                if question["type"] in ["text", "textarea"]:
                    if isinstance(answer_value, str):
                        min_len = question.get("min_length")
                        max_len = question.get("max_length")
                        
                        if min_len and len(answer_value) < min_len:
                            return f"❌ إجابة '{question['label']}' قصيرة جداً (الحد الأدنى: {min_len})."
                        if max_len and len(answer_value) > max_len:
                            return f"❌ إجابة '{question['label']}' طويلة جداً (الحد الأقصى: {max_len})."
                
                elif question["type"] == "number":
                    try:
                        num = int(answer_value)
                        min_val = question.get("min_value")
                        max_val = question.get("max_value")
                        
                        if min_val is not None and num < min_val:
                            return f"❌ القيمة في '{question['label']}' أقل من الحد الأدنى ({min_val})."
                        if max_val is not None and num > max_val:
                            return f"❌ القيمة في '{question['label']}' أكبر من الحد الأقصى ({max_val})."
                    except ValueError:
                        return f"❌ إجابة '{question['label']}' يجب أن تكون رقماً."
                
                elif question["type"] in ["select", "multiselect"]:
                    options = question.get("options", [])
                    if isinstance(answer_value, list):
                        for val in answer_value:
                            if val not in options:
                                return f"❌ خيار غير صحيح في '{question['label']}'."
                    elif answer_value not in options:
                        return f"❌ خيار غير صحيح في '{question['label']}'."
        
        return None
    
    async def get_submission(self, submission_id: str) -> Optional[Dict]:
        """جلب تقديم معين"""
        return await self.db.get_submission(submission_id)
    
    async def get_user_submissions(
        self,
        user_id: str,
        form_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """جلب تقديمات مستخدم"""
        return await self.db.get_user_submissions(user_id, form_id, status)
    
    async def get_form_submissions(
        self,
        form_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """جلب تقديمات نموذج"""
        return await self.db.get_form_submissions(form_id, status, limit)
    
    # ===== Review Management =====
    async def review_submission(
        self,
        submission_id: str,
        reviewer_id: str,
        action: str,  # "accept" or "reject"
        reason: Optional[str] = None
    ) -> bool:
        """مراجعة تقديم (قبول أو رفض)"""
        if action not in ["accept", "reject"]:
            return False
        
        status = "accepted" if action == "accept" else "rejected"
        
        return await self.db.update_submission_status(
            submission_id=submission_id,
            status=status,
            reviewed_by=reviewer_id,
            reason=reason
        )
    
    async def archive_submission(self, submission_id: str) -> bool:
        """أرشفة تقديم"""
        submission = await self.get_submission(submission_id)
        if not submission:
            return False
        
        return await self.db.submissions.update_one(
            {"submission_id": submission_id},
            {"$set": {"status": "archived"}}
        ).modified_count > 0
    
    # ===== Settings Management =====
    async def get_settings(self, guild_id: str) -> Dict:
        """جلب إعدادات السيرفر"""
        settings = await self.db.get_settings(guild_id)
        if not settings:
            settings = await self.db.create_settings(guild_id)
        return settings
    
    async def update_settings(self, guild_id: str, **updates) -> bool:
        """تحديث إعدادات السيرفر"""
        return await self.db.update_settings(guild_id, updates)
    
    async def block_user(self, guild_id: str, user_id: str) -> bool:
        """حظر مستخدم من التقديم"""
        settings = await self.get_settings(guild_id)
        if user_id not in settings.get("blocked_users", []):
            return await self.db.settings.update_one(
                {"guild_id": guild_id},
                {"$push": {"blocked_users": user_id}}
            ).modified_count > 0
        return False
    
    async def unblock_user(self, guild_id: str, user_id: str) -> bool:
        """إلغاء حظر مستخدم"""
        return await self.db.settings.update_one(
            {"guild_id": guild_id},
            {"$pull": {"blocked_users": user_id}}
        ).modified_count > 0
    
    # ===== Statistics =====
    async def get_form_stats(self, form_id: str) -> Dict:
        """إحصائيات النموذج"""
        form = await self.get_form(form_id)
        if not form:
            return {}
        
        return form.get("stats", {})
    
    async def get_guild_stats(self, guild_id: str) -> Dict:
        """إحصائيات السيرفر"""
        forms = await self.get_guild_forms(guild_id)
        
        total_forms = len(forms)
        total_submissions = sum(f.get("stats", {}).get("total_submissions", 0) for f in forms)
        total_accepted = sum(f.get("stats", {}).get("accepted", 0) for f in forms)
        total_rejected = sum(f.get("stats", {}).get("rejected", 0) for f in forms)
        total_pending = sum(f.get("stats", {}).get("pending", 0) for f in forms)
        
        acceptance_rate = (total_accepted / total_submissions * 100) if total_submissions > 0 else 0.0
        
        return {
            "total_forms": total_forms,
            "total_submissions": total_submissions,
            "pending": total_pending,
            "accepted": total_accepted,
            "rejected": total_rejected,
            "acceptance_rate": round(acceptance_rate, 2)
        }
    
    # ===== Utility Methods =====
    def create_submission_embed(
        self,
        submission: Dict,
        form: Dict,
        user: discord.User
    ) -> discord.Embed:
        """إنشاء embed لعرض التقديم"""
        embed = discord.Embed(
            title=f"📝 {form['title']}",
            description=f"**المقدم:** {user.mention} (`{user.id}`)",
            color=int(form.get("color", "#5865F2").replace("#", ""), 16),
            timestamp=submission["submitted_at"]
        )
        
        if form.get("thumbnail_url"):
            embed.set_thumbnail(url=form["thumbnail_url"])
        
        embed.set_author(name=str(user), icon_url=user.display_avatar.url)
        
        # Add answers
        for answer in submission["answers"]:
            answer_value = answer["answer"]
            if isinstance(answer_value, list):
                answer_value = ", ".join(answer_value)
            
            # Truncate long answers
            if len(str(answer_value)) > 1024:
                answer_value = str(answer_value)[:1021] + "..."
            
            embed.add_field(
                name=f"❓ {answer['question_label']}",
                value=f"```{answer_value}```" if len(str(answer_value)) > 50 else answer_value,
                inline=False
            )
        
        # Add status
        status_emoji = {
            "pending": "⏳",
            "accepted": "✅",
            "rejected": "❌",
            "archived": "📦"
        }
        
        status = submission.get("status", "pending")
        embed.add_field(
            name="الحالة",
            value=f"{status_emoji.get(status, '❔')} {status.upper()}",
            inline=True
        )
        
        embed.set_footer(text=f"Submission ID: {submission['submission_id']}")
        
        return embed
    
    def create_form_embed(self, form: Dict) -> discord.Embed:
        """إنشاء embed لعرض النموذج"""
        embed = discord.Embed(
            title=f"📋 {form['title']}",
            description=form.get("description", "لا يوجد وصف"),
            color=int(form.get("color", "#5865F2").replace("#", ""), 16)
        )
        
        if form.get("thumbnail_url"):
            embed.set_thumbnail(url=form["thumbnail_url"])
        
        # Add questions preview
        questions = form.get("questions", [])
        if questions:
            questions_text = "\n".join([
                f"{i+1}. {q['label']} {'**(إجباري)**' if q.get('required') else '(اختياري)'}"
                for i, q in enumerate(questions[:10])
            ])
            
            if len(questions) > 10:
                questions_text += f"\n... و {len(questions) - 10} أسئلة أخرى"
            
            embed.add_field(
                name=f"الأسئلة ({len(questions)})",
                value=questions_text,
                inline=False
            )
        
        # Add stats
        stats = form.get("stats", {})
        embed.add_field(
            name="📊 الإحصائيات",
            value=f"**التقديمات:** {stats.get('total_submissions', 0)}\n"
                  f"**قيد الانتظار:** {stats.get('pending', 0)}\n"
                  f"**مقبول:** {stats.get('accepted', 0)}\n"
                  f"**مرفوض:** {stats.get('rejected', 0)}",
            inline=True
        )
        
        # Add settings
        embed.add_field(
            name="⚙️ الإعدادات",
            value=f"**الحالة:** {'✅ نشط' if form.get('is_active') else '❌ معطل'}\n"
                  f"**فترة الانتظار:** {form.get('cooldown_hours', 24)}h\n"
                  f"**الحد الأقصى:** {form.get('max_submissions_per_user', 5)} تقديم/شخص",
            inline=True
        )
        
        embed.set_footer(text=f"Form ID: {form['form_id']}")
        embed.timestamp = form.get("created_at", datetime.now(timezone.utc))
        
        return embed

"""
Applications API
================
RESTful API endpoints for Application Forms management.

Endpoints:
- GET    /api/applications/guilds/{guild_id}/forms - List all forms
- GET    /api/applications/guilds/{guild_id}/forms/{form_id} - Get form details
- POST   /api/applications/guilds/{guild_id}/forms - Create form
- PUT    /api/applications/guilds/{guild_id}/forms/{form_id} - Update form
- DELETE /api/applications/guilds/{guild_id}/forms/{form_id} - Delete form
- PATCH  /api/applications/guilds/{guild_id}/forms/{form_id}/toggle - Toggle form
- GET    /api/applications/guilds/{guild_id}/submissions - List submissions
- GET    /api/applications/submissions/{submission_id} - Get submission details
- PATCH  /api/applications/submissions/{submission_id}/review - Review submission
- GET    /api/applications/guilds/{guild_id}/stats - Get statistics
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)


class ApplicationsAPI:
    """Dashboard API for Applications System"""
    
    def __init__(self, mongo_client: AsyncIOMotorClient):
        """Initialize Applications API
        
        Args:
            mongo_client: MongoDB client instance
        """
        self.db = mongo_client.kingdom77
        self.forms_collection = self.db.application_forms
        self.submissions_collection = self.db.application_submissions
    
    # ==================== FORMS MANAGEMENT ====================
    
    async def list_forms(
        self,
        guild_id: str,
        enabled_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all forms for a guild
        
        Args:
            guild_id: Discord guild ID
            enabled_only: Filter enabled forms only
            
        Returns:
            List of form documents
        """
        try:
            query = {"guild_id": guild_id}
            if enabled_only:
                query["enabled"] = True
            
            forms = await self.forms_collection.find(query).to_list(length=None)
            
            # Convert ObjectId to string
            for form in forms:
                form["_id"] = str(form["_id"])
            
            return forms
        except Exception as e:
            logger.error(f"Error listing forms: {e}")
            return []
    
    async def get_form(
        self,
        guild_id: str,
        form_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get form details
        
        Args:
            guild_id: Discord guild ID
            form_id: Form ID
            
        Returns:
            Form document or None
        """
        try:
            form = await self.forms_collection.find_one({
                "guild_id": guild_id,
                "form_id": form_id
            })
            
            if form:
                form["_id"] = str(form["_id"])
            
            return form
        except Exception as e:
            logger.error(f"Error getting form: {e}")
            return None
    
    async def create_form(
        self,
        guild_id: str,
        form_data: Dict[str, Any],
        creator_id: str
    ) -> tuple[bool, str, Optional[str]]:
        """Create new application form
        
        Args:
            guild_id: Discord guild ID
            form_data: Form configuration
            creator_id: User ID who created the form
            
        Returns:
            (success, message, form_id)
        """
        try:
            # Generate form ID
            import uuid
            form_id = str(uuid.uuid4())[:8]
            
            # Prepare document
            doc = {
                "guild_id": guild_id,
                "form_id": form_id,
                "name": form_data.get("name"),
                "description": form_data.get("description"),
                "questions": form_data.get("questions", []),
                "submit_channel_id": form_data.get("submit_channel_id"),
                "review_channel_id": form_data.get("review_channel_id"),
                "accept_role_id": form_data.get("accept_role_id"),
                "cooldown_hours": form_data.get("cooldown_hours", 24),
                "max_submissions": form_data.get("max_submissions", 1),
                "enabled": True,
                "created_at": datetime.utcnow(),
                "created_by": creator_id,
                "statistics": {
                    "total_submissions": 0,
                    "pending": 0,
                    "accepted": 0,
                    "rejected": 0
                }
            }
            
            await self.forms_collection.insert_one(doc)
            
            return True, f"✅ تم إنشاء النموذج: {form_data.get('name')}", form_id
        except Exception as e:
            logger.error(f"Error creating form: {e}")
            return False, f"❌ فشل إنشاء النموذج: {str(e)}", None
    
    async def update_form(
        self,
        guild_id: str,
        form_id: str,
        updates: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Update form configuration
        
        Args:
            guild_id: Discord guild ID
            form_id: Form ID
            updates: Fields to update
            
        Returns:
            (success, message)
        """
        try:
            result = await self.forms_collection.update_one(
                {"guild_id": guild_id, "form_id": form_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                return True, "✅ تم تحديث النموذج بنجاح"
            else:
                return False, "❌ النموذج غير موجود"
        except Exception as e:
            logger.error(f"Error updating form: {e}")
            return False, f"❌ فشل التحديث: {str(e)}"
    
    async def delete_form(
        self,
        guild_id: str,
        form_id: str
    ) -> tuple[bool, str]:
        """Delete application form
        
        Args:
            guild_id: Discord guild ID
            form_id: Form ID
            
        Returns:
            (success, message)
        """
        try:
            result = await self.forms_collection.delete_one({
                "guild_id": guild_id,
                "form_id": form_id
            })
            
            if result.deleted_count > 0:
                # Also delete all submissions
                await self.submissions_collection.delete_many({
                    "guild_id": guild_id,
                    "form_id": form_id
                })
                return True, "✅ تم حذف النموذج وجميع التقديمات"
            else:
                return False, "❌ النموذج غير موجود"
        except Exception as e:
            logger.error(f"Error deleting form: {e}")
            return False, f"❌ فشل الحذف: {str(e)}"
    
    async def toggle_form(
        self,
        guild_id: str,
        form_id: str
    ) -> tuple[bool, str, bool]:
        """Toggle form enabled status
        
        Args:
            guild_id: Discord guild ID
            form_id: Form ID
            
        Returns:
            (success, message, new_state)
        """
        try:
            form = await self.get_form(guild_id, form_id)
            if not form:
                return False, "❌ النموذج غير موجود", False
            
            new_state = not form.get("enabled", True)
            
            await self.forms_collection.update_one(
                {"guild_id": guild_id, "form_id": form_id},
                {"$set": {"enabled": new_state}}
            )
            
            status = "مفعّل" if new_state else "معطّل"
            return True, f"✅ النموذج الآن {status}", new_state
        except Exception as e:
            logger.error(f"Error toggling form: {e}")
            return False, f"❌ فشل التبديل: {str(e)}", False
    
    # ==================== SUBMISSIONS MANAGEMENT ====================
    
    async def list_submissions(
        self,
        guild_id: str,
        form_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get submissions for a guild
        
        Args:
            guild_id: Discord guild ID
            form_id: Filter by form ID (optional)
            status: Filter by status (pending/accepted/rejected)
            limit: Maximum submissions to return
            
        Returns:
            List of submission documents
        """
        try:
            query = {"guild_id": guild_id}
            if form_id:
                query["form_id"] = form_id
            if status:
                query["status"] = status
            
            submissions = await self.submissions_collection.find(query)\
                .sort("submitted_at", -1)\
                .limit(limit)\
                .to_list(length=None)
            
            # Convert ObjectId to string
            for sub in submissions:
                sub["_id"] = str(sub["_id"])
            
            return submissions
        except Exception as e:
            logger.error(f"Error listing submissions: {e}")
            return []
    
    async def get_submission(
        self,
        submission_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get submission details
        
        Args:
            submission_id: Submission ID
            
        Returns:
            Submission document or None
        """
        try:
            submission = await self.submissions_collection.find_one({
                "submission_id": submission_id
            })
            
            if submission:
                submission["_id"] = str(submission["_id"])
            
            return submission
        except Exception as e:
            logger.error(f"Error getting submission: {e}")
            return None
    
    async def review_submission(
        self,
        submission_id: str,
        reviewer_id: str,
        action: str,
        reason: Optional[str] = None
    ) -> tuple[bool, str]:
        """Review a submission (accept/reject)
        
        Args:
            submission_id: Submission ID
            reviewer_id: User ID of reviewer
            action: 'accept' or 'reject'
            reason: Review reason (optional)
            
        Returns:
            (success, message)
        """
        try:
            if action not in ["accept", "reject"]:
                return False, "❌ Action must be 'accept' or 'reject'"
            
            submission = await self.get_submission(submission_id)
            if not submission:
                return False, "❌ التقديم غير موجود"
            
            if submission["status"] != "pending":
                return False, "❌ التقديم تمت مراجعته مسبقاً"
            
            # Update submission
            update = {
                "status": "accepted" if action == "accept" else "rejected",
                "reviewed_by": reviewer_id,
                "reviewed_at": datetime.utcnow(),
                "review_reason": reason
            }
            
            await self.submissions_collection.update_one(
                {"submission_id": submission_id},
                {"$set": update}
            )
            
            # Update form statistics
            stat_field = "accepted" if action == "accept" else "rejected"
            await self.forms_collection.update_one(
                {
                    "guild_id": submission["guild_id"],
                    "form_id": submission["form_id"]
                },
                {
                    "$inc": {
                        f"statistics.{stat_field}": 1,
                        "statistics.pending": -1
                    }
                }
            )
            
            status_ar = "قُبل" if action == "accept" else "رُفض"
            return True, f"✅ {status_ar} التقديم بنجاح"
        except Exception as e:
            logger.error(f"Error reviewing submission: {e}")
            return False, f"❌ فشلت المراجعة: {str(e)}"
    
    # ==================== STATISTICS ====================
    
    async def get_statistics(
        self,
        guild_id: str
    ) -> Dict[str, Any]:
        """Get application statistics for guild
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            Statistics dictionary
        """
        try:
            # Count forms
            total_forms = await self.forms_collection.count_documents({
                "guild_id": guild_id
            })
            
            active_forms = await self.forms_collection.count_documents({
                "guild_id": guild_id,
                "enabled": True
            })
            
            # Count submissions
            total_submissions = await self.submissions_collection.count_documents({
                "guild_id": guild_id
            })
            
            pending_submissions = await self.submissions_collection.count_documents({
                "guild_id": guild_id,
                "status": "pending"
            })
            
            accepted_submissions = await self.submissions_collection.count_documents({
                "guild_id": guild_id,
                "status": "accepted"
            })
            
            rejected_submissions = await self.submissions_collection.count_documents({
                "guild_id": guild_id,
                "status": "rejected"
            })
            
            # Get forms with stats
            forms = await self.list_forms(guild_id)
            forms_stats = []
            for form in forms:
                forms_stats.append({
                    "form_id": form["form_id"],
                    "name": form["name"],
                    "enabled": form["enabled"],
                    "statistics": form.get("statistics", {})
                })
            
            return {
                "guild_id": guild_id,
                "forms": {
                    "total": total_forms,
                    "active": active_forms,
                    "inactive": total_forms - active_forms
                },
                "submissions": {
                    "total": total_submissions,
                    "pending": pending_submissions,
                    "accepted": accepted_submissions,
                    "rejected": rejected_submissions
                },
                "forms_details": forms_stats,
                "acceptance_rate": round(
                    (accepted_submissions / total_submissions * 100) 
                    if total_submissions > 0 else 0, 
                    2
                )
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "guild_id": guild_id,
                "error": str(e)
            }

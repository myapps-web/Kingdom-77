"""
Applications System API Endpoints
Kingdom-77 Bot v4.0 - Phase 5.7

FastAPI endpoints for managing application forms and submissions.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from dashboard.utils.auth import verify_api_key, get_current_user
from dashboard.utils.database import get_database


router = APIRouter(prefix="/api/applications", tags=["Applications"])


# ==================== Pydantic Models ====================

class QuestionModel(BaseModel):
    """Question model for application forms"""
    id: str = Field(..., description="Question ID")
    question_text: str = Field(..., max_length=500)
    question_type: str = Field(..., regex="^(text|textarea|number|select|multiselect|yes_no)$")
    required: bool = True
    options: Optional[List[str]] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    placeholder: Optional[str] = None


class ApplicationFormCreate(BaseModel):
    """Model for creating application form"""
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., max_length=1000)
    channel_id: str = Field(..., description="Channel ID for submissions")
    accept_role_id: Optional[str] = None
    cooldown_hours: int = Field(default=24, ge=0, le=168)
    max_submissions: int = Field(default=1, ge=1, le=10)
    questions: List[QuestionModel] = Field(..., min_items=1, max_items=25)


class ApplicationFormUpdate(BaseModel):
    """Model for updating application form"""
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    channel_id: Optional[str] = None
    accept_role_id: Optional[str] = None
    cooldown_hours: Optional[int] = Field(None, ge=0, le=168)
    max_submissions: Optional[int] = Field(None, ge=1, le=10)
    questions: Optional[List[QuestionModel]] = Field(None, min_items=1, max_items=25)


class SubmissionReview(BaseModel):
    """Model for reviewing submission"""
    status: str = Field(..., regex="^(approved|rejected)$")
    reason: Optional[str] = Field(None, max_length=500)


class ApplicationFormResponse(BaseModel):
    """Response model for application form"""
    id: str
    guild_id: str
    title: str
    description: str
    channel_id: str
    accept_role_id: Optional[str]
    cooldown_hours: int
    max_submissions: int
    questions: List[QuestionModel]
    enabled: bool
    created_at: datetime
    updated_at: datetime
    statistics: Dict[str, int]


class SubmissionResponse(BaseModel):
    """Response model for submission"""
    id: str
    form_id: str
    guild_id: str
    user_id: str
    answers: List[Dict[str, Any]]
    status: str
    submitted_at: datetime
    reviewed_at: Optional[datetime]
    reviewed_by: Optional[str]
    review_reason: Optional[str]


class ApplicationStatsResponse(BaseModel):
    """Response model for application statistics"""
    total_forms: int
    active_forms: int
    total_submissions: int
    pending_submissions: int
    approved_submissions: int
    rejected_submissions: int
    by_form: List[Dict[str, Any]]


# ==================== Helper Functions ====================

def serialize_form(form: Dict) -> Dict:
    """Serialize form document"""
    if form:
        form["id"] = str(form.pop("_id"))
        form["created_at"] = form.get("created_at", datetime.utcnow())
        form["updated_at"] = form.get("updated_at", datetime.utcnow())
    return form


def serialize_submission(submission: Dict) -> Dict:
    """Serialize submission document"""
    if submission:
        submission["id"] = str(submission.pop("_id"))
        submission["submitted_at"] = submission.get("submitted_at", datetime.utcnow())
    return submission


# ==================== API Endpoints ====================

@router.get("/guilds/{guild_id}/forms", response_model=List[ApplicationFormResponse])
async def list_forms(
    guild_id: str,
    enabled: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all application forms for a guild
    
    - **guild_id**: Guild ID
    - **enabled**: Filter by enabled status (optional)
    - **skip**: Number of forms to skip (pagination)
    - **limit**: Maximum number of forms to return
    """
    try:
        query = {"guild_id": guild_id}
        if enabled is not None:
            query["enabled"] = enabled
        
        cursor = db.application_forms.find(query).skip(skip).limit(limit).sort("created_at", -1)
        forms = await cursor.to_list(length=limit)
        
        return [serialize_form(form) for form in forms]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch forms: {str(e)}")


@router.get("/guilds/{guild_id}/forms/{form_id}", response_model=ApplicationFormResponse)
async def get_form(
    guild_id: str,
    form_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get application form details
    
    - **guild_id**: Guild ID
    - **form_id**: Form ID
    """
    try:
        form = await db.application_forms.find_one({
            "_id": ObjectId(form_id),
            "guild_id": guild_id
        })
        
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        return serialize_form(form)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to fetch form: {str(e)}")


@router.post("/guilds/{guild_id}/forms", response_model=ApplicationFormResponse, status_code=201)
async def create_form(
    guild_id: str,
    form_data: ApplicationFormCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new application form
    
    - **guild_id**: Guild ID
    - **form_data**: Form data
    """
    try:
        # Prepare form document
        form_doc = {
            "guild_id": guild_id,
            "title": form_data.title,
            "description": form_data.description,
            "channel_id": form_data.channel_id,
            "accept_role_id": form_data.accept_role_id,
            "cooldown_hours": form_data.cooldown_hours,
            "max_submissions": form_data.max_submissions,
            "questions": [q.dict() for q in form_data.questions],
            "enabled": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "statistics": {
                "total_submissions": 0,
                "pending": 0,
                "approved": 0,
                "rejected": 0
            }
        }
        
        # Insert form
        result = await db.application_forms.insert_one(form_doc)
        form_doc["_id"] = result.inserted_id
        
        return serialize_form(form_doc)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create form: {str(e)}")


@router.put("/guilds/{guild_id}/forms/{form_id}", response_model=ApplicationFormResponse)
async def update_form(
    guild_id: str,
    form_id: str,
    form_data: ApplicationFormUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Update application form
    
    - **guild_id**: Guild ID
    - **form_id**: Form ID
    - **form_data**: Updated form data
    """
    try:
        # Build update document
        update_doc = {"updated_at": datetime.utcnow()}
        
        if form_data.title is not None:
            update_doc["title"] = form_data.title
        if form_data.description is not None:
            update_doc["description"] = form_data.description
        if form_data.channel_id is not None:
            update_doc["channel_id"] = form_data.channel_id
        if form_data.accept_role_id is not None:
            update_doc["accept_role_id"] = form_data.accept_role_id
        if form_data.cooldown_hours is not None:
            update_doc["cooldown_hours"] = form_data.cooldown_hours
        if form_data.max_submissions is not None:
            update_doc["max_submissions"] = form_data.max_submissions
        if form_data.questions is not None:
            update_doc["questions"] = [q.dict() for q in form_data.questions]
        
        # Update form
        result = await db.application_forms.find_one_and_update(
            {"_id": ObjectId(form_id), "guild_id": guild_id},
            {"$set": update_doc},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Form not found")
        
        return serialize_form(result)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to update form: {str(e)}")


@router.delete("/guilds/{guild_id}/forms/{form_id}", status_code=204)
async def delete_form(
    guild_id: str,
    form_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete application form
    
    - **guild_id**: Guild ID
    - **form_id**: Form ID
    """
    try:
        result = await db.application_forms.delete_one({
            "_id": ObjectId(form_id),
            "guild_id": guild_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Form not found")
        
        # Also delete all submissions for this form
        await db.application_submissions.delete_many({"form_id": form_id})
        
        return None
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to delete form: {str(e)}")


@router.patch("/guilds/{guild_id}/forms/{form_id}/toggle", response_model=ApplicationFormResponse)
async def toggle_form(
    guild_id: str,
    form_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Toggle form enabled status
    
    - **guild_id**: Guild ID
    - **form_id**: Form ID
    """
    try:
        # Get current form
        form = await db.application_forms.find_one({
            "_id": ObjectId(form_id),
            "guild_id": guild_id
        })
        
        if not form:
            raise HTTPException(status_code=404, detail="Form not found")
        
        # Toggle enabled status
        new_status = not form.get("enabled", True)
        
        result = await db.application_forms.find_one_and_update(
            {"_id": ObjectId(form_id), "guild_id": guild_id},
            {
                "$set": {
                    "enabled": new_status,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        return serialize_form(result)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to toggle form: {str(e)}")


@router.get("/guilds/{guild_id}/submissions", response_model=List[SubmissionResponse])
async def list_submissions(
    guild_id: str,
    form_id: Optional[str] = None,
    status: Optional[str] = Query(None, regex="^(pending|approved|rejected)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get submissions for a guild
    
    - **guild_id**: Guild ID
    - **form_id**: Filter by form ID (optional)
    - **status**: Filter by status (optional)
    - **skip**: Number of submissions to skip (pagination)
    - **limit**: Maximum number of submissions to return
    """
    try:
        query = {"guild_id": guild_id}
        if form_id:
            query["form_id"] = form_id
        if status:
            query["status"] = status
        
        cursor = db.application_submissions.find(query).skip(skip).limit(limit).sort("submitted_at", -1)
        submissions = await cursor.to_list(length=limit)
        
        return [serialize_submission(sub) for sub in submissions]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch submissions: {str(e)}")


@router.patch("/submissions/{submission_id}/review", response_model=SubmissionResponse)
async def review_submission(
    submission_id: str,
    review_data: SubmissionReview,
    reviewer_id: str = Query(..., description="Discord user ID of reviewer"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Review a submission (approve/reject)
    
    - **submission_id**: Submission ID
    - **review_data**: Review data (status and reason)
    - **reviewer_id**: Discord user ID of reviewer
    """
    try:
        # Update submission
        result = await db.application_submissions.find_one_and_update(
            {"_id": ObjectId(submission_id), "status": "pending"},
            {
                "$set": {
                    "status": review_data.status,
                    "reviewed_at": datetime.utcnow(),
                    "reviewed_by": reviewer_id,
                    "review_reason": review_data.reason
                }
            },
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Submission not found or already reviewed")
        
        # Update form statistics
        await db.application_forms.update_one(
            {"_id": ObjectId(result["form_id"])},
            {
                "$inc": {
                    "statistics.pending": -1,
                    f"statistics.{review_data.status}": 1
                }
            }
        )
        
        return serialize_submission(result)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to review submission: {str(e)}")


@router.get("/guilds/{guild_id}/stats", response_model=ApplicationStatsResponse)
async def get_statistics(
    guild_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get application statistics for a guild
    
    - **guild_id**: Guild ID
    """
    try:
        # Get all forms
        forms = await db.application_forms.find({"guild_id": guild_id}).to_list(length=None)
        
        # Calculate statistics
        total_forms = len(forms)
        active_forms = sum(1 for f in forms if f.get("enabled", True))
        
        total_submissions = 0
        pending_submissions = 0
        approved_submissions = 0
        rejected_submissions = 0
        
        by_form = []
        for form in forms:
            stats = form.get("statistics", {})
            form_total = stats.get("total_submissions", 0)
            total_submissions += form_total
            pending_submissions += stats.get("pending", 0)
            approved_submissions += stats.get("approved", 0)
            rejected_submissions += stats.get("rejected", 0)
            
            by_form.append({
                "form_id": str(form["_id"]),
                "title": form["title"],
                "total": form_total,
                "pending": stats.get("pending", 0),
                "approved": stats.get("approved", 0),
                "rejected": stats.get("rejected", 0)
            })
        
        return ApplicationStatsResponse(
            total_forms=total_forms,
            active_forms=active_forms,
            total_submissions=total_submissions,
            pending_submissions=pending_submissions,
            approved_submissions=approved_submissions,
            rejected_submissions=rejected_submissions,
            by_form=by_form
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")

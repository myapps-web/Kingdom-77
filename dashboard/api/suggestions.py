"""
Kingdom-77 Bot - Suggestions Dashboard API
REST API endpoints for Suggestions System

Endpoints:
GET    /suggestions/{guild_id} - Get all suggestions
GET    /suggestions/{guild_id}/{suggestion_id} - Get specific suggestion
POST   /suggestions/{guild_id} - Create suggestion
PATCH  /suggestions/{guild_id}/{suggestion_id} - Update suggestion status
DELETE /suggestions/{guild_id}/{suggestion_id} - Delete suggestion

GET    /suggestions/{guild_id}/{suggestion_id}/votes - Get votes
POST   /suggestions/{guild_id}/{suggestion_id}/vote - Add/update vote
DELETE /suggestions/{guild_id}/{suggestion_id}/vote - Remove vote

GET    /suggestions/{guild_id}/{suggestion_id}/comments - Get comments
POST   /suggestions/{guild_id}/{suggestion_id}/comments - Add comment
DELETE /suggestions/{guild_id}/comments/{comment_id} - Delete comment

GET    /suggestions/{guild_id}/stats - Get statistics
GET    /suggestions/{guild_id}/leaderboard - Get leaderboard
GET    /suggestions/{guild_id}/settings - Get settings
PATCH  /suggestions/{guild_id}/settings - Update settings
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

router = APIRouter(prefix="/suggestions", tags=["Suggestions"])


# ============= Pydantic Models =============

class SuggestionCreate(BaseModel):
    """نموذج إنشاء اقتراح"""
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10, max_length=2000)
    anonymous: bool = Field(default=False)
    attachments: Optional[List[str]] = Field(default=None)


class SuggestionUpdate(BaseModel):
    """نموذج تحديث اقتراح"""
    status: str = Field(..., pattern="^(pending|approved|denied|implemented|duplicate|considering)$")
    staff_response: Optional[str] = Field(None, max_length=1000)


class VoteRequest(BaseModel):
    """نموذج التصويت"""
    vote_type: str = Field(..., pattern="^(upvote|downvote|neutral)$")


class CommentCreate(BaseModel):
    """نموذج التعليق"""
    content: str = Field(..., min_length=5, max_length=500)


class SettingsUpdate(BaseModel):
    """نموذج تحديث الإعدادات"""
    enabled: Optional[bool] = None
    suggestions_channel_id: Optional[str] = None
    review_channel_id: Optional[str] = None
    staff_role_ids: Optional[List[str]] = None
    allow_voting: Optional[bool] = None
    allow_anonymous: Optional[bool] = None
    min_suggestion_length: Optional[int] = Field(None, ge=5, le=100)
    max_suggestion_length: Optional[int] = Field(None, ge=100, le=4000)
    cooldown_minutes: Optional[int] = Field(None, ge=0, le=1440)
    show_author: Optional[bool] = None
    show_vote_count: Optional[bool] = None
    dm_notifications: Optional[bool] = None


class SuggestionResponse(BaseModel):
    """نموذج استجابة الاقتراح"""
    guild_id: str
    suggestion_id: int
    user_id: str
    title: str
    description: str
    status: str
    anonymous: bool
    attachments: List[str]
    created_at: datetime
    updated_at: datetime
    upvotes: int
    downvotes: int
    neutral_votes: int
    message_id: Optional[str] = None
    channel_id: Optional[str] = None
    staff_response: Optional[str] = None
    staff_responder_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    implemented_at: Optional[datetime] = None


class VoteResponse(BaseModel):
    """نموذج استجابة الصوت"""
    user_id: str
    vote_type: str
    created_at: datetime


class CommentResponse(BaseModel):
    """نموذج استجابة التعليق"""
    comment_id: str
    user_id: str
    content: str
    created_at: datetime
    edited: bool


class StatisticsResponse(BaseModel):
    """نموذج الإحصائيات"""
    total_suggestions: int
    status_breakdown: Dict[str, int]
    top_contributors: List[Dict[str, Any]]
    total_votes: int


class LeaderboardEntry(BaseModel):
    """نموذج إدخال لوحة المتصدرين"""
    user_id: str
    suggestions_count: int
    total_upvotes: int
    total_downvotes: int
    approved_count: int
    implemented_count: int
    score: int


# ============= Dependency Injection =============

async def get_suggestion_schema(guild_id: str):
    """الحصول على schema الاقتراحات"""
    from database import db
    from database.suggestions_schema import SuggestionsSchema
    
    if not db or not db.client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database not connected"
        )
    
    return SuggestionsSchema(db.db)


# ============= Suggestions Endpoints =============

@router.get("/{guild_id}", response_model=List[SuggestionResponse])
async def get_suggestions(
    guild_id: str,
    status_filter: Optional[str] = Query(None, alias="status"),
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    schema: Any = Depends(get_suggestion_schema)
):
    """الحصول على قائمة الاقتراحات"""
    try:
        suggestions = await schema.list_suggestions(
            guild_id=int(guild_id),
            status=status_filter,
            user_id=int(user_id) if user_id else None,
            limit=limit,
            skip=skip
        )
        
        # تحويل ObjectId إلى string
        for suggestion in suggestions:
            if "_id" in suggestion:
                del suggestion["_id"]
        
        return suggestions
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching suggestions: {str(e)}"
        )


@router.get("/{guild_id}/{suggestion_id}", response_model=SuggestionResponse)
async def get_suggestion(
    guild_id: str,
    suggestion_id: int,
    schema: Any = Depends(get_suggestion_schema)
):
    """الحصول على اقتراح محدد"""
    try:
        suggestion = await schema.get_suggestion(int(guild_id), suggestion_id)
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suggestion #{suggestion_id} not found"
            )
        
        # حذف _id
        if "_id" in suggestion:
            del suggestion["_id"]
        
        return suggestion
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching suggestion: {str(e)}"
        )


@router.post("/{guild_id}", status_code=status.HTTP_201_CREATED)
async def create_suggestion(
    guild_id: str,
    user_id: str,
    suggestion: SuggestionCreate,
    schema: Any = Depends(get_suggestion_schema)
):
    """إنشاء اقتراح جديد"""
    try:
        # التحقق من عدد الاقتراحات
        user_count = await schema.get_user_suggestions_count(int(guild_id), int(user_id))
        settings = await schema.get_settings(int(guild_id))
        
        if user_count >= settings["max_suggestions_per_user"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Maximum suggestions limit reached ({settings['max_suggestions_per_user']})"
            )
        
        # إنشاء الاقتراح
        new_suggestion = await schema.create_suggestion(
            guild_id=int(guild_id),
            user_id=int(user_id),
            title=suggestion.title,
            description=suggestion.description,
            anonymous=suggestion.anonymous,
            attachments=suggestion.attachments
        )
        
        # حذف _id
        if "_id" in new_suggestion:
            del new_suggestion["_id"]
        
        return {
            "success": True,
            "message": "Suggestion created successfully",
            "suggestion": new_suggestion
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating suggestion: {str(e)}"
        )


@router.patch("/{guild_id}/{suggestion_id}")
async def update_suggestion(
    guild_id: str,
    suggestion_id: int,
    staff_id: str,
    update: SuggestionUpdate,
    schema: Any = Depends(get_suggestion_schema)
):
    """تحديث حالة اقتراح"""
    try:
        success = await schema.update_suggestion_status(
            guild_id=int(guild_id),
            suggestion_id=suggestion_id,
            status=update.status,
            staff_id=int(staff_id),
            response=update.staff_response
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suggestion #{suggestion_id} not found or update failed"
            )
        
        return {
            "success": True,
            "message": f"Suggestion #{suggestion_id} updated to {update.status}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating suggestion: {str(e)}"
        )


@router.delete("/{guild_id}/{suggestion_id}")
async def delete_suggestion(
    guild_id: str,
    suggestion_id: int,
    schema: Any = Depends(get_suggestion_schema)
):
    """حذف اقتراح"""
    try:
        success = await schema.delete_suggestion(int(guild_id), suggestion_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suggestion #{suggestion_id} not found"
            )
        
        return {
            "success": True,
            "message": f"Suggestion #{suggestion_id} deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting suggestion: {str(e)}"
        )


# ============= Voting Endpoints =============

@router.get("/{guild_id}/{suggestion_id}/votes", response_model=Dict[str, int])
async def get_votes(
    guild_id: str,
    suggestion_id: int,
    schema: Any = Depends(get_suggestion_schema)
):
    """الحصول على ملخص الأصوات"""
    try:
        suggestion = await schema.get_suggestion(int(guild_id), suggestion_id)
        
        if not suggestion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Suggestion #{suggestion_id} not found"
            )
        
        return {
            "upvotes": suggestion["upvotes"],
            "downvotes": suggestion["downvotes"],
            "neutral_votes": suggestion["neutral_votes"],
            "total": suggestion["upvotes"] + suggestion["downvotes"] + suggestion["neutral_votes"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching votes: {str(e)}"
        )


@router.post("/{guild_id}/{suggestion_id}/vote")
async def add_vote(
    guild_id: str,
    suggestion_id: int,
    user_id: str,
    vote: VoteRequest,
    schema: Any = Depends(get_suggestion_schema)
):
    """إضافة أو تحديث صوت"""
    try:
        result = await schema.add_vote(
            guild_id=int(guild_id),
            suggestion_id=suggestion_id,
            user_id=int(user_id),
            vote_type=vote.vote_type
        )
        
        return {
            "success": True,
            "message": "Vote registered" if not result.get("old_vote") else "Vote updated",
            "previous_vote": result.get("old_vote"),
            "new_vote": result.get("new_vote")
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding vote: {str(e)}"
        )


@router.delete("/{guild_id}/{suggestion_id}/vote")
async def remove_vote(
    guild_id: str,
    suggestion_id: int,
    user_id: str,
    schema: Any = Depends(get_suggestion_schema)
):
    """إزالة صوت"""
    try:
        success = await schema.remove_vote(
            guild_id=int(guild_id),
            suggestion_id=suggestion_id,
            user_id=int(user_id)
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vote not found"
            )
        
        return {
            "success": True,
            "message": "Vote removed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing vote: {str(e)}"
        )


# ============= Comments Endpoints =============

@router.get("/{guild_id}/{suggestion_id}/comments", response_model=List[CommentResponse])
async def get_comments(
    guild_id: str,
    suggestion_id: int,
    limit: int = Query(50, ge=1, le=100),
    schema: Any = Depends(get_suggestion_schema)
):
    """الحصول على تعليقات اقتراح"""
    try:
        comments = await schema.get_comments(
            guild_id=int(guild_id),
            suggestion_id=suggestion_id,
            limit=limit
        )
        
        # تحويل ObjectId إلى string
        for comment in comments:
            comment["comment_id"] = str(comment.pop("_id"))
        
        return comments
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching comments: {str(e)}"
        )


@router.post("/{guild_id}/{suggestion_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    guild_id: str,
    suggestion_id: int,
    user_id: str,
    comment: CommentCreate,
    schema: Any = Depends(get_suggestion_schema)
):
    """إضافة تعليق"""
    try:
        new_comment = await schema.add_comment(
            guild_id=int(guild_id),
            suggestion_id=suggestion_id,
            user_id=int(user_id),
            content=comment.content
        )
        
        # تحويل ObjectId
        new_comment["comment_id"] = str(new_comment.pop("_id"))
        
        return {
            "success": True,
            "message": "Comment added successfully",
            "comment": new_comment
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding comment: {str(e)}"
        )


@router.delete("/{guild_id}/comments/{comment_id}")
async def delete_comment(
    guild_id: str,
    comment_id: str,
    schema: Any = Depends(get_suggestion_schema)
):
    """حذف تعليق"""
    try:
        success = await schema.delete_comment(int(guild_id), comment_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        return {
            "success": True,
            "message": "Comment deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting comment: {str(e)}"
        )


# ============= Statistics & Analytics =============

@router.get("/{guild_id}/stats", response_model=StatisticsResponse)
async def get_statistics(
    guild_id: str,
    schema: Any = Depends(get_suggestion_schema)
):
    """الحصول على إحصائيات"""
    try:
        stats = await schema.get_statistics(int(guild_id))
        return stats
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching statistics: {str(e)}"
        )


@router.get("/{guild_id}/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    guild_id: str,
    sort_by: str = Query("suggestions", pattern="^(suggestions|upvotes)$"),
    limit: int = Query(10, ge=1, le=50),
    schema: Any = Depends(get_suggestion_schema)
):
    """الحصول على لوحة المتصدرين"""
    try:
        leaderboard = await schema.get_leaderboard(
            guild_id=int(guild_id),
            sort_by=sort_by,
            limit=limit
        )
        
        return leaderboard
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching leaderboard: {str(e)}"
        )


# ============= Settings Endpoints =============

@router.get("/{guild_id}/settings")
async def get_settings(
    guild_id: str,
    schema: Any = Depends(get_suggestion_schema)
):
    """الحصول على الإعدادات"""
    try:
        settings = await schema.get_settings(int(guild_id))
        
        # حذف _id
        if "_id" in settings:
            del settings["_id"]
        
        return settings
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching settings: {str(e)}"
        )


@router.patch("/{guild_id}/settings")
async def update_settings(
    guild_id: str,
    settings: SettingsUpdate,
    schema: Any = Depends(get_suggestion_schema)
):
    """تحديث الإعدادات"""
    try:
        # تحويل النموذج إلى dict وحذف القيم None
        settings_data = settings.dict(exclude_none=True)
        
        if not settings_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No settings to update"
            )
        
        success = await schema.update_settings(int(guild_id), settings_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update settings"
            )
        
        return {
            "success": True,
            "message": "Settings updated successfully",
            "updated_fields": list(settings_data.keys())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating settings: {str(e)}"
        )


# ============= Batch Operations =============

@router.post("/{guild_id}/bulk-update")
async def bulk_update_status(
    guild_id: str,
    staff_id: str,
    suggestion_ids: List[int],
    new_status: str = Query(..., pattern="^(approved|denied|implemented|duplicate|considering)$"),
    response: Optional[str] = None,
    schema: Any = Depends(get_suggestion_schema)
):
    """تحديث حالة عدة اقتراحات دفعة واحدة"""
    try:
        updated = []
        failed = []
        
        for suggestion_id in suggestion_ids:
            success = await schema.update_suggestion_status(
                guild_id=int(guild_id),
                suggestion_id=suggestion_id,
                status=new_status,
                staff_id=int(staff_id),
                response=response
            )
            
            if success:
                updated.append(suggestion_id)
            else:
                failed.append(suggestion_id)
        
        return {
            "success": True,
            "message": f"Updated {len(updated)} suggestions",
            "updated": updated,
            "failed": failed
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in bulk update: {str(e)}"
        )


@router.get("/{guild_id}/export")
async def export_suggestions(
    guild_id: str,
    status_filter: Optional[str] = Query(None),
    format: str = Query("json", pattern="^(json|csv)$"),
    schema: Any = Depends(get_suggestion_schema)
):
    """تصدير الاقتراحات"""
    try:
        suggestions = await schema.list_suggestions(
            guild_id=int(guild_id),
            status=status_filter,
            limit=1000
        )
        
        # حذف _id من كل اقتراح
        for suggestion in suggestions:
            if "_id" in suggestion:
                del suggestion["_id"]
        
        if format == "json":
            return {
                "format": "json",
                "count": len(suggestions),
                "data": suggestions
            }
        
        # CSV format (simplified)
        elif format == "csv":
            import csv
            from io import StringIO
            
            output = StringIO()
            if suggestions:
                writer = csv.DictWriter(output, fieldnames=suggestions[0].keys())
                writer.writeheader()
                writer.writerows(suggestions)
            
            return {
                "format": "csv",
                "count": len(suggestions),
                "data": output.getvalue()
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting suggestions: {str(e)}"
        )

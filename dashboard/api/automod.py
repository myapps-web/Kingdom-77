"""
AutoMod API Endpoints
Manage AutoMod rules, settings, logs, and statistics
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from ..models.user import User
from ..models.response import APIResponse
from ..utils.auth import get_current_user
from ..utils.database import get_database

router = APIRouter()


# ==================== Request Models ====================

class AutoModRuleCreate(BaseModel):
    """Create AutoMod rule"""
    name: str
    rule_type: Literal["spam", "rate_limit", "links", "invites", "mentions", "caps", "emojis", "blacklist"]
    action: Literal["delete", "warn", "mute", "kick", "ban"]
    enabled: bool = True
    settings: Dict[str, Any] = {}
    whitelist_roles: List[int] = []
    custom_message: Optional[str] = None
    duration: Optional[int] = None


class AutoModRuleUpdate(BaseModel):
    """Update AutoMod rule"""
    name: Optional[str] = None
    enabled: Optional[bool] = None
    settings: Optional[Dict[str, Any]] = None
    whitelist_roles: Optional[List[int]] = None
    custom_message: Optional[str] = None
    duration: Optional[int] = None


class AutoModSettingsUpdate(BaseModel):
    """Update AutoMod settings"""
    enabled: Optional[bool] = None
    log_channel_id: Optional[int] = None
    dm_users: Optional[bool] = None
    progressive_penalties: Optional[bool] = None
    ignored_channels: Optional[List[int]] = None
    immune_roles: Optional[List[int]] = None


# ==================== Settings Endpoints ====================

@router.get("/{guild_id}/settings")
async def get_automod_settings(
    guild_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get AutoMod settings"""
    try:
        db = await get_database()
        
        settings = await db.guild_automod_settings.find_one({"guild_id": guild_id})
        
        if not settings:
            # Return default settings
            settings = {
                "guild_id": guild_id,
                "enabled": False,
                "log_channel_id": None,
                "dm_users": True,
                "progressive_penalties": True,
                "ignored_channels": [],
                "immune_roles": []
            }
        else:
            settings["_id"] = str(settings["_id"])
        
        return APIResponse(
            success=True,
            data=settings
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{guild_id}/settings")
async def update_automod_settings(
    guild_id: str,
    updates: AutoModSettingsUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update AutoMod settings"""
    try:
        db = await get_database()
        
        # Prepare updates
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.guild_automod_settings.update_one(
            {"guild_id": guild_id},
            {"$set": update_data},
            upsert=True
        )
        
        if result.modified_count > 0 or result.upserted_id:
            return APIResponse(
                success=True,
                message="Settings updated successfully"
            )
        else:
            return APIResponse(
                success=False,
                message="No changes made"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Rules Endpoints ====================

@router.get("/{guild_id}/rules")
async def get_automod_rules(
    guild_id: str,
    rule_type: Optional[str] = None,
    enabled_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Get all AutoMod rules"""
    try:
        db = await get_database()
        
        # Build query
        query = {"guild_id": guild_id}
        if rule_type:
            query["rule_type"] = rule_type
        if enabled_only:
            query["enabled"] = True
        
        rules = await db.automod_rules.find(query).to_list(None)
        
        # Convert ObjectId to string
        for rule in rules:
            rule["_id"] = str(rule["_id"])
        
        return APIResponse(
            success=True,
            data=rules
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{guild_id}/rules/{rule_id}")
async def get_automod_rule(
    guild_id: str,
    rule_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get specific AutoMod rule"""
    try:
        db = await get_database()
        from bson import ObjectId
        
        rule = await db.automod_rules.find_one({
            "_id": ObjectId(rule_id),
            "guild_id": guild_id
        })
        
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        rule["_id"] = str(rule["_id"])
        
        return APIResponse(
            success=True,
            data=rule
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{guild_id}/rules")
async def create_automod_rule(
    guild_id: str,
    rule: AutoModRuleCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new AutoMod rule"""
    try:
        db = await get_database()
        
        # Prepare rule document
        rule_doc = rule.dict()
        rule_doc["guild_id"] = guild_id
        rule_doc["created_at"] = datetime.utcnow()
        rule_doc["updated_at"] = datetime.utcnow()
        
        result = await db.automod_rules.insert_one(rule_doc)
        
        return APIResponse(
            success=True,
            message="Rule created successfully",
            data={"rule_id": str(result.inserted_id)}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{guild_id}/rules/{rule_id}")
async def update_automod_rule(
    guild_id: str,
    rule_id: str,
    updates: AutoModRuleUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update AutoMod rule"""
    try:
        db = await get_database()
        from bson import ObjectId
        
        # Prepare updates
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        result = await db.automod_rules.update_one(
            {"_id": ObjectId(rule_id), "guild_id": guild_id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return APIResponse(
                success=True,
                message="Rule updated successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Rule not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{guild_id}/rules/{rule_id}")
async def delete_automod_rule(
    guild_id: str,
    rule_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete AutoMod rule"""
    try:
        db = await get_database()
        from bson import ObjectId
        
        result = await db.automod_rules.delete_one({
            "_id": ObjectId(rule_id),
            "guild_id": guild_id
        })
        
        if result.deleted_count > 0:
            return APIResponse(
                success=True,
                message="Rule deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Rule not found")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{guild_id}/rules/{rule_id}/toggle")
async def toggle_automod_rule(
    guild_id: str,
    rule_id: str,
    current_user: User = Depends(get_current_user)
):
    """Toggle AutoMod rule enabled/disabled"""
    try:
        db = await get_database()
        from bson import ObjectId
        
        # Get current state
        rule = await db.automod_rules.find_one({
            "_id": ObjectId(rule_id),
            "guild_id": guild_id
        })
        
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Toggle
        new_state = not rule.get("enabled", False)
        
        await db.automod_rules.update_one(
            {"_id": ObjectId(rule_id)},
            {"$set": {"enabled": new_state, "updated_at": datetime.utcnow()}}
        )
        
        return APIResponse(
            success=True,
            message=f"Rule {'enabled' if new_state else 'disabled'}",
            data={"enabled": new_state}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Logs Endpoints ====================

@router.get("/{guild_id}/logs")
async def get_automod_logs(
    guild_id: str,
    user_id: Optional[str] = None,
    rule_type: Optional[str] = None,
    action: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get AutoMod logs"""
    try:
        db = await get_database()
        
        # Build query
        query = {"guild_id": guild_id}
        if user_id:
            query["user_id"] = user_id
        if rule_type:
            query["rule_type"] = rule_type
        if action:
            query["action"] = action
        
        # Get logs
        logs = await db.automod_logs.find(query).sort("timestamp", -1).skip(offset).limit(limit).to_list(limit)
        
        # Convert ObjectId to string
        for log in logs:
            log["_id"] = str(log["_id"])
        
        # Get total count
        total = await db.automod_logs.count_documents(query)
        
        return APIResponse(
            success=True,
            data={
                "logs": logs,
                "total": total,
                "limit": limit,
                "offset": offset
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Statistics Endpoints ====================

@router.get("/{guild_id}/stats")
async def get_automod_stats(
    guild_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user)
):
    """Get AutoMod statistics"""
    try:
        db = await get_database()
        from datetime import timedelta
        
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Total actions
        total_actions = await db.automod_logs.count_documents({
            "guild_id": guild_id,
            "timestamp": {"$gte": start_date}
        })
        
        # Actions by type
        action_pipeline = [
            {"$match": {
                "guild_id": guild_id,
                "timestamp": {"$gte": start_date}
            }},
            {"$group": {
                "_id": "$action",
                "count": {"$sum": 1}
            }}
        ]
        
        action_counts = await db.automod_logs.aggregate(action_pipeline).to_list(None)
        by_action = {item["_id"]: item["count"] for item in action_counts}
        
        # Rules by type
        rule_pipeline = [
            {"$match": {
                "guild_id": guild_id,
                "timestamp": {"$gte": start_date}
            }},
            {"$group": {
                "_id": "$rule_type",
                "count": {"$sum": 1}
            }}
        ]
        
        rule_counts = await db.automod_logs.aggregate(rule_pipeline).to_list(None)
        by_rule_type = {item["_id"]: item["count"] for item in rule_counts}
        
        # Top violators
        violator_pipeline = [
            {"$match": {
                "guild_id": guild_id,
                "timestamp": {"$gte": start_date}
            }},
            {"$group": {
                "_id": "$user_id",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        top_violators = await db.automod_logs.aggregate(violator_pipeline).to_list(10)
        
        return APIResponse(
            success=True,
            data={
                "guild_id": guild_id,
                "period_days": days,
                "total_actions": total_actions,
                "by_action": by_action,
                "by_rule_type": by_rule_type,
                "top_violators": [
                    {"user_id": v["_id"], "violations": v["count"]}
                    for v in top_violators
                ]
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Trust Score Endpoints ====================

@router.get("/{guild_id}/trust-scores")
async def get_trust_scores(
    guild_id: str,
    user_id: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get user trust scores"""
    try:
        db = await get_database()
        
        # Build query
        query = {"guild_id": guild_id}
        if user_id:
            query["user_id"] = user_id
        if min_score is not None or max_score is not None:
            query["score"] = {}
            if min_score is not None:
                query["score"]["$gte"] = min_score
            if max_score is not None:
                query["score"]["$lte"] = max_score
        
        scores = await db.user_trust_scores.find(query).sort("score", -1).limit(limit).to_list(limit)
        
        # Convert ObjectId to string
        for score in scores:
            score["_id"] = str(score["_id"])
        
        return APIResponse(
            success=True,
            data=scores
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

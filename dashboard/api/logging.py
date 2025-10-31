"""
Kingdom-77 Bot - Logging Dashboard API
FastAPI endpoints for viewing and managing logs
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime, timedelta

from database.logging_schema import LoggingSchema
from dashboard.api.auth import get_current_user, check_guild_permissions


router = APIRouter(prefix="/api/logging", tags=["Logging"])


# ==================== Pydantic Models ====================

class LoggingSettings(BaseModel):
    """Logging settings model"""
    enabled: bool = True
    channels: Dict[str, Optional[int]] = Field(default_factory=dict)
    log_types: Dict[str, bool] = Field(default_factory=dict)
    ignored_channels: List[int] = Field(default_factory=list)
    ignored_roles: List[int] = Field(default_factory=list)
    ignored_users: List[int] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)


class LogEntry(BaseModel):
    """Log entry model"""
    log_type: str
    timestamp: datetime
    guild_id: int
    user_id: Optional[int] = None
    channel_id: Optional[int] = None
    details: Dict[str, Any] = Field(default_factory=dict)


class LogStats(BaseModel):
    """Log statistics model"""
    total_logs: int
    by_type: Dict[str, int]
    most_active_users: List[Dict[str, Any]]
    most_active_channels: List[Dict[str, Any]]
    daily_breakdown: List[Dict[str, Any]]


# ==================== Helper Functions ====================

def get_db() -> LoggingSchema:
    """Get database instance"""
    from main import bot
    return bot.db.logging


# ==================== Endpoints ====================

@router.get("/{guild_id}/settings")
async def get_logging_settings(
    guild_id: int,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> LoggingSettings:
    """Get logging settings for a guild"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["manage_guild"])
    
    # Get settings
    settings = await db.get_server_settings(guild_id)
    if not settings:
        settings = await db.create_default_settings(guild_id)
    
    return LoggingSettings(
        enabled=settings.get("enabled", True),
        channels=settings.get("channels", {}),
        log_types=settings.get("log_types", {}),
        ignored_channels=settings.get("ignored_channels", []),
        ignored_roles=settings.get("ignored_roles", []),
        ignored_users=settings.get("ignored_users", []),
        settings=settings.get("settings", {})
    )


@router.patch("/{guild_id}/settings")
async def update_logging_settings(
    guild_id: int,
    settings: LoggingSettings,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> Dict[str, str]:
    """Update logging settings for a guild"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["manage_guild"])
    
    # Update settings
    updates = {
        "enabled": settings.enabled,
        "channels": settings.channels,
        "log_types": settings.log_types,
        "ignored_channels": settings.ignored_channels,
        "ignored_roles": settings.ignored_roles,
        "ignored_users": settings.ignored_users,
        "settings": settings.settings
    }
    
    success = await db.update_server_settings(guild_id, updates)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update settings")
    
    return {"message": "Settings updated successfully"}


@router.get("/{guild_id}/logs/{log_category}")
async def get_logs(
    guild_id: int,
    log_category: Literal["message", "member", "channel", "role", "voice", "server"],
    log_type: Optional[str] = None,
    user_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get logs with filters"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["manage_guild"])
    
    # Validate limit
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 1
    
    # Get logs
    logs = await db.get_logs(
        guild_id=guild_id,
        log_category=log_category,
        log_type=log_type,
        user_id=user_id,
        channel_id=channel_id,
        limit=limit,
        offset=offset,
        start_date=start_date,
        end_date=end_date
    )
    
    # Convert ObjectId to string
    for log in logs:
        if "_id" in log:
            log["_id"] = str(log["_id"])
    
    return logs


@router.get("/{guild_id}/logs/search")
async def search_logs(
    guild_id: int,
    query: str,
    search_in: Literal["all", "message", "member", "channel", "role"] = "all",
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Search logs by content"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["manage_guild"])
    
    # Search logs
    results = await db.search_logs(guild_id, query, search_in)
    
    # Convert ObjectId to string
    for log in results:
        if "_id" in log:
            log["_id"] = str(log["_id"])
    
    return results


@router.get("/{guild_id}/logs/user/{user_id}")
async def get_user_logs(
    guild_id: int,
    user_id: int,
    limit: int = 100,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> Dict[str, List[Dict[str, Any]]]:
    """Get all logs for a specific user"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["manage_guild"])
    
    # Validate limit
    if limit > 200:
        limit = 200
    if limit < 1:
        limit = 1
    
    # Get user history
    history = await db.get_user_history(guild_id, user_id, limit)
    
    # Convert ObjectId to string
    for category in history.values():
        for log in category:
            if "_id" in log:
                log["_id"] = str(log["_id"])
    
    return history


@router.get("/{guild_id}/stats")
async def get_logging_stats(
    guild_id: int,
    days: int = 7,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> LogStats:
    """Get logging statistics"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["manage_guild"])
    
    # Validate days
    if days > 30:
        days = 30
    if days < 1:
        days = 1
    
    # Get stats
    stats = await db.get_stats(guild_id, days)
    
    return LogStats(
        total_logs=stats.get("total_logs", 0),
        by_type=stats.get("by_type", {}),
        most_active_users=stats.get("most_active_users", []),
        most_active_channels=stats.get("most_active_channels", []),
        daily_breakdown=stats.get("daily_breakdown", [])
    )


@router.get("/{guild_id}/export")
async def export_logs(
    guild_id: int,
    log_category: Literal["message", "member", "channel", "role", "voice", "server", "all"] = "all",
    days: int = 7,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> Dict[str, Any]:
    """Export logs to JSON"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["administrator"])
    
    # Validate days
    if days > 30:
        days = 30
    if days < 1:
        days = 1
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get logs
    logs = {}
    
    if log_category == "all":
        # Export all categories
        for category in ["message", "member", "channel", "role", "voice", "server"]:
            category_logs = await db.get_logs(
                guild_id=guild_id,
                log_category=category,
                limit=1000,
                start_date=start_date,
                end_date=end_date
            )
            # Convert ObjectId to string
            for log in category_logs:
                if "_id" in log:
                    log["_id"] = str(log["_id"])
            logs[category] = category_logs
    else:
        # Export single category
        category_logs = await db.get_logs(
            guild_id=guild_id,
            log_category=log_category,
            limit=1000,
            start_date=start_date,
            end_date=end_date
        )
        # Convert ObjectId to string
        for log in category_logs:
            if "_id" in log:
                log["_id"] = str(log["_id"])
        logs[log_category] = category_logs
    
    # Count total logs
    total_logs = sum(len(v) for v in logs.values())
    
    return {
        "guild_id": guild_id,
        "category": log_category,
        "days": days,
        "total_logs": total_logs,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "logs": logs
    }


@router.delete("/{guild_id}/logs/clear")
async def clear_old_logs(
    guild_id: int,
    days: int = 30,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> Dict[str, Any]:
    """Clear old logs from the database"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["administrator"])
    
    # Validate days
    if days < 7:
        days = 7
    if days > 90:
        days = 90
    
    # Delete logs
    deleted_count = await db.cleanup_old_logs(guild_id, days)
    
    return {
        "message": "Logs cleared successfully",
        "deleted_count": deleted_count,
        "days": days
    }


@router.post("/{guild_id}/logs/channel")
async def set_log_channel(
    guild_id: int,
    log_type: str,
    channel_id: Optional[int] = None,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> Dict[str, str]:
    """Set logging channel for a specific type"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["manage_guild"])
    
    # Set channel
    success = await db.set_log_channel(guild_id, log_type, channel_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set log channel")
    
    return {"message": "Log channel updated successfully"}


@router.post("/{guild_id}/logs/toggle")
async def toggle_log_type(
    guild_id: int,
    log_type: str,
    enabled: bool,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> Dict[str, str]:
    """Enable or disable a specific log type"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["manage_guild"])
    
    # Toggle log type
    success = await db.toggle_log_type(guild_id, log_type, enabled)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to toggle log type")
    
    status = "enabled" if enabled else "disabled"
    return {"message": f"Log type {status} successfully"}


# ==================== Analytics Endpoints ====================

@router.get("/{guild_id}/analytics/activity")
async def get_activity_analytics(
    guild_id: int,
    days: int = 7,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> Dict[str, Any]:
    """Get activity analytics"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["manage_guild"])
    
    # Validate days
    if days > 30:
        days = 30
    if days < 1:
        days = 1
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get message activity
    message_logs = await db.get_logs(
        guild_id=guild_id,
        log_category="message",
        limit=1000,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get member activity
    member_logs = await db.get_logs(
        guild_id=guild_id,
        log_category="member",
        limit=1000,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get voice activity
    voice_logs = await db.get_logs(
        guild_id=guild_id,
        log_category="voice",
        limit=1000,
        start_date=start_date,
        end_date=end_date
    )
    
    # Calculate analytics
    analytics = {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "message_activity": {
            "total": len(message_logs),
            "edits": len([l for l in message_logs if l.get("log_type") == "message_edit"]),
            "deletes": len([l for l in message_logs if l.get("log_type") == "message_delete"]),
            "bulk_deletes": len([l for l in message_logs if l.get("log_type") == "bulk_delete"])
        },
        "member_activity": {
            "total": len(member_logs),
            "joins": len([l for l in member_logs if l.get("log_type") == "member_join"]),
            "leaves": len([l for l in member_logs if l.get("log_type") == "member_leave"]),
            "bans": len([l for l in member_logs if l.get("log_type") == "member_ban"]),
            "unbans": len([l for l in member_logs if l.get("log_type") == "member_unban"])
        },
        "voice_activity": {
            "total": len(voice_logs),
            "joins": len([l for l in voice_logs if l.get("log_type") == "voice_join"]),
            "leaves": len([l for l in voice_logs if l.get("log_type") == "voice_leave"]),
            "moves": len([l for l in voice_logs if l.get("log_type") == "voice_move"])
        }
    }
    
    return analytics


@router.get("/{guild_id}/analytics/moderation")
async def get_moderation_analytics(
    guild_id: int,
    days: int = 7,
    user = Depends(get_current_user),
    db: LoggingSchema = Depends(get_db)
) -> Dict[str, Any]:
    """Get moderation analytics"""
    # Check permissions
    await check_guild_permissions(guild_id, user["id"], ["manage_guild"])
    
    # Validate days
    if days > 30:
        days = 30
    if days < 1:
        days = 1
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get member logs
    member_logs = await db.get_logs(
        guild_id=guild_id,
        log_category="member",
        limit=1000,
        start_date=start_date,
        end_date=end_date
    )
    
    # Calculate moderation stats
    bans = [l for l in member_logs if l.get("log_type") == "member_ban"]
    unbans = [l for l in member_logs if l.get("log_type") == "member_unban"]
    
    # Get most active moderators
    moderators = {}
    for log in bans + unbans:
        mod_id = log.get("banned_by") or log.get("unbanned_by")
        if mod_id:
            moderators[mod_id] = moderators.get(mod_id, 0) + 1
    
    most_active_mods = [
        {"user_id": user_id, "actions": count}
        for user_id, count in sorted(moderators.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    analytics = {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_bans": len(bans),
        "total_unbans": len(unbans),
        "net_bans": len(bans) - len(unbans),
        "most_active_moderators": most_active_mods
    }
    
    return analytics

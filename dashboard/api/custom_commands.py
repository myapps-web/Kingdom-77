"""
Kingdom-77 Bot - Custom Commands API
FastAPI endpoints for managing custom commands via dashboard
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from database.custom_commands_schema import CustomCommandsSchema
from custom_commands.command_parser import CommandParser
from dashboard.api.auth import get_current_user, check_guild_permissions


router = APIRouter(prefix="/commands", tags=["Custom Commands"])


# ==================== Pydantic Models ====================

class CommandCreate(BaseModel):
    """Model for creating a command"""
    name: str = Field(..., min_length=1, max_length=32)
    response_type: str = Field(..., pattern="^(text|embed|both)$")
    response_content: Optional[str] = Field(None, max_length=2000)
    embed_data: Optional[Dict[str, Any]] = None
    aliases: Optional[List[str]] = Field(default_factory=list)
    cooldown: int = Field(default=0, ge=0)
    required_roles: Optional[List[int]] = Field(default_factory=list)
    allowed_channels: Optional[List[int]] = Field(default_factory=list)
    delete_trigger: bool = False


class CommandUpdate(BaseModel):
    """Model for updating a command"""
    response_type: Optional[str] = Field(None, pattern="^(text|embed|both)$")
    response_content: Optional[str] = Field(None, max_length=2000)
    embed_data: Optional[Dict[str, Any]] = None
    aliases: Optional[List[str]] = None
    cooldown: Optional[int] = Field(None, ge=0)
    required_roles: Optional[List[int]] = None
    allowed_channels: Optional[List[int]] = None
    delete_trigger: Optional[bool] = None
    enabled: Optional[bool] = None


class AutoResponseCreate(BaseModel):
    """Model for creating an auto-response"""
    trigger: str = Field(..., min_length=1, max_length=100)
    response: str = Field(..., min_length=1, max_length=2000)
    match_type: str = Field(default="contains", pattern="^(exact|contains|starts_with|ends_with|regex)$")
    case_sensitive: bool = False
    delete_trigger: bool = False
    cooldown: int = Field(default=0, ge=0)


class CommandResponse(BaseModel):
    """Model for command response"""
    name: str
    creator_id: int
    enabled: bool
    response_type: str
    response_content: Optional[str]
    embed_data: Optional[Dict[str, Any]]
    aliases: List[str]
    cooldown: int
    use_count: int
    created_at: datetime
    updated_at: datetime


class StatsResponse(BaseModel):
    """Model for statistics response"""
    total_commands: int
    total_usage: int
    success_rate: float
    period_days: int
    most_used_commands: List[Dict[str, Any]]
    most_active_users: List[Dict[str, Any]]


# ==================== Helper Functions ====================

def get_schema(db) -> CustomCommandsSchema:
    """Get schema instance"""
    return CustomCommandsSchema(db)


def get_parser() -> CommandParser:
    """Get parser instance"""
    return CommandParser()


# ==================== Command Endpoints ====================

@router.get("/{guild_id}/list")
async def list_commands(
    guild_id: int,
    enabled_only: bool = True,
    creator_id: Optional[int] = None,
    db = Depends(lambda: None),  # Injected by main app
    user = Depends(get_current_user)
):
    """Get all custom commands for a guild"""
    await check_guild_permissions(user, guild_id, ["view_commands"])
    
    schema = get_schema(db)
    
    if creator_id:
        commands = await schema.get_commands_by_creator(guild_id, creator_id)
    else:
        commands = await schema.get_all_commands(guild_id, enabled_only)
    
    # Convert ObjectId to string
    for cmd in commands:
        cmd["_id"] = str(cmd["_id"])
    
    return {
        "guild_id": guild_id,
        "count": len(commands),
        "commands": commands
    }


@router.post("/{guild_id}/create")
async def create_command(
    guild_id: int,
    command: CommandCreate,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Create a new custom command"""
    await check_guild_permissions(user, guild_id, ["manage_commands"])
    
    schema = get_schema(db)
    parser = get_parser()
    
    # Check premium limits
    is_premium = await check_premium(guild_id, db)
    limit_info = await schema.check_command_limit(guild_id, is_premium)
    
    if not limit_info["can_create"]:
        raise HTTPException(
            status_code=403,
            detail=f"Command limit reached ({limit_info['limit']}). Upgrade to Premium!"
        )
    
    # Validate command name
    is_valid, error_msg = parser.validate_command_name(command.name)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Validate content
    if command.response_type in ["text", "both"]:
        if not command.response_content:
            raise HTTPException(
                status_code=400,
                detail="Text response is required for this response type"
            )
        is_valid, error_msg = parser.validate_content(command.response_content)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
    
    # Validate embed
    if command.response_type in ["embed", "both"]:
        if not command.embed_data:
            raise HTTPException(
                status_code=400,
                detail="Embed data is required for this response type"
            )
        is_valid, error_msg = parser.validate_embed_data(command.embed_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
    
    # Create command
    try:
        command_id = await schema.create_command(
            guild_id=guild_id,
            name=command.name,
            creator_id=user["user_id"],
            response_type=command.response_type,
            response_content=command.response_content,
            embed_data=command.embed_data,
            aliases=command.aliases,
            cooldown=command.cooldown,
            required_roles=command.required_roles,
            allowed_channels=command.allowed_channels,
            delete_trigger=command.delete_trigger
        )
        
        return {
            "success": True,
            "message": f"Command '{command.name}' created successfully",
            "command_id": command_id,
            "remaining": limit_info["remaining"] - 1 if limit_info["remaining"] != float('inf') else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{guild_id}/commands/{name}")
async def get_command(
    guild_id: int,
    name: str,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Get a specific command"""
    await check_guild_permissions(user, guild_id, ["view_commands"])
    
    schema = get_schema(db)
    command = await schema.get_command(guild_id, name)
    
    if not command:
        raise HTTPException(status_code=404, detail=f"Command '{name}' not found")
    
    command["_id"] = str(command["_id"])
    return command


@router.patch("/{guild_id}/commands/{name}")
async def update_command(
    guild_id: int,
    name: str,
    updates: CommandUpdate,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Update a custom command"""
    await check_guild_permissions(user, guild_id, ["manage_commands"])
    
    schema = get_schema(db)
    parser = get_parser()
    
    # Build updates dict
    update_dict = {}
    for field, value in updates.dict(exclude_unset=True).items():
        if value is not None:
            update_dict[field] = value
    
    # Validate content if updated
    if "response_content" in update_dict:
        is_valid, error_msg = parser.validate_content(update_dict["response_content"])
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
    
    # Validate embed if updated
    if "embed_data" in update_dict:
        is_valid, error_msg = parser.validate_embed_data(update_dict["embed_data"])
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
    
    # Update command
    success = await schema.update_command(guild_id, name, update_dict)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Command '{name}' not found or no changes made")
    
    return {
        "success": True,
        "message": f"Command '{name}' updated successfully"
    }


@router.delete("/{guild_id}/commands/{name}")
async def delete_command(
    guild_id: int,
    name: str,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Delete a custom command"""
    await check_guild_permissions(user, guild_id, ["manage_commands"])
    
    schema = get_schema(db)
    success = await schema.delete_command(guild_id, name)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Command '{name}' not found")
    
    return {
        "success": True,
        "message": f"Command '{name}' deleted successfully"
    }


@router.get("/{guild_id}/commands/{name}/stats")
async def get_command_stats(
    guild_id: int,
    name: str,
    days: int = 7,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Get usage statistics for a specific command"""
    await check_guild_permissions(user, guild_id, ["view_commands"])
    
    schema = get_schema(db)
    command = await schema.get_command(guild_id, name)
    
    if not command:
        raise HTTPException(status_code=404, detail=f"Command '{name}' not found")
    
    # Get usage history
    from datetime import datetime, timedelta
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {
            "$match": {
                "guild_id": guild_id,
                "command_name": name,
                "timestamp": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$timestamp"
                    }
                },
                "count": {"$sum": 1},
                "success_count": {
                    "$sum": {"$cond": ["$success", 1, 0]}
                }
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    daily_usage = await schema.command_usage.aggregate(pipeline).to_list(length=None)
    
    return {
        "command": name,
        "total_uses": command.get("use_count", 0),
        "period_days": days,
        "daily_usage": daily_usage
    }


# ==================== Auto-Response Endpoints ====================

@router.get("/{guild_id}/autoresponses")
async def list_auto_responses(
    guild_id: int,
    enabled_only: bool = True,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Get all auto-responses for a guild"""
    await check_guild_permissions(user, guild_id, ["view_commands"])
    
    schema = get_schema(db)
    auto_responses = await schema.get_all_auto_responses(guild_id, enabled_only)
    
    for ar in auto_responses:
        ar["_id"] = str(ar["_id"])
    
    return {
        "guild_id": guild_id,
        "count": len(auto_responses),
        "auto_responses": auto_responses
    }


@router.post("/{guild_id}/autoresponses")
async def create_auto_response(
    guild_id: int,
    auto_response: AutoResponseCreate,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Create a new auto-response"""
    await check_guild_permissions(user, guild_id, ["manage_commands"])
    
    schema = get_schema(db)
    parser = get_parser()
    
    # Validate response
    is_valid, error_msg = parser.validate_content(auto_response.response)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Create auto-response
    try:
        ar_id = await schema.create_auto_response(
            guild_id=guild_id,
            trigger=auto_response.trigger,
            response=auto_response.response,
            creator_id=user["user_id"],
            match_type=auto_response.match_type,
            case_sensitive=auto_response.case_sensitive,
            delete_trigger=auto_response.delete_trigger,
            cooldown=auto_response.cooldown
        )
        
        return {
            "success": True,
            "message": f"Auto-response for '{auto_response.trigger}' created successfully",
            "id": ar_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{guild_id}/autoresponses/{trigger}")
async def delete_auto_response(
    guild_id: int,
    trigger: str,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Delete an auto-response"""
    await check_guild_permissions(user, guild_id, ["manage_commands"])
    
    schema = get_schema(db)
    success = await schema.delete_auto_response(guild_id, trigger)
    
    if not success:
        raise HTTPException(status_code=404, detail=f"Auto-response for '{trigger}' not found")
    
    return {
        "success": True,
        "message": f"Auto-response for '{trigger}' deleted successfully"
    }


# ==================== Statistics Endpoints ====================

@router.get("/{guild_id}/stats")
async def get_guild_stats(
    guild_id: int,
    days: int = 7,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Get command statistics for a guild"""
    await check_guild_permissions(user, guild_id, ["view_commands"])
    
    schema = get_schema(db)
    stats = await schema.get_command_stats(guild_id, days)
    
    # Add command count
    command_count = await schema.get_command_count(guild_id)
    stats["total_commands"] = command_count
    
    return stats


# ==================== Variables Documentation ====================

@router.get("/variables")
async def get_variables(
    user = Depends(get_current_user)
):
    """Get list of available variables"""
    parser = get_parser()
    variables = parser.get_available_variables()
    
    return {
        "variables": variables,
        "categories": {
            "user": [k for k in variables.keys() if k.startswith("{user")],
            "server": [k for k in variables.keys() if k.startswith("{server")],
            "channel": [k for k in variables.keys() if k.startswith("{channel")],
            "datetime": [k for k in variables.keys() if k.startswith(("{date", "{time", "{timestamp", "{unix"))],
            "utility": [k for k in variables.keys() if k.startswith(("{random", "{math", "{choose", "{args"))]
        }
    }


# ==================== Bulk Operations ====================

@router.post("/{guild_id}/bulk/toggle")
async def bulk_toggle_commands(
    guild_id: int,
    enabled: bool,
    command_names: Optional[List[str]] = None,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Enable or disable multiple commands"""
    await check_guild_permissions(user, guild_id, ["manage_commands"])
    
    schema = get_schema(db)
    count = await schema.bulk_toggle_commands(guild_id, enabled, command_names)
    
    status = "enabled" if enabled else "disabled"
    return {
        "success": True,
        "message": f"{count} commands {status}",
        "count": count
    }


@router.post("/{guild_id}/export")
async def export_commands(
    guild_id: int,
    db = Depends(lambda: None),
    user = Depends(get_current_user)
):
    """Export all commands for backup"""
    await check_guild_permissions(user, guild_id, ["manage_commands"])
    
    schema = get_schema(db)
    commands = await schema.export_commands(guild_id)
    
    # Convert ObjectId to string
    for cmd in commands:
        cmd["_id"] = str(cmd["_id"])
    
    return {
        "guild_id": guild_id,
        "count": len(commands),
        "commands": commands,
        "exported_at": datetime.utcnow().isoformat()
    }


# ==================== Helper Function ====================

async def check_premium(guild_id: int, db) -> bool:
    """Check if guild has premium (placeholder)"""
    # TODO: Implement premium check
    return False

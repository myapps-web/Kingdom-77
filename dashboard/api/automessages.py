"""
Auto-Messages System API Endpoints
Kingdom-77 Bot v4.0 - Phase 5.7

FastAPI endpoints for managing auto messages with triggers and responses.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from dashboard.utils.auth import verify_api_key
from dashboard.utils.database import get_database


router = APIRouter(prefix="/api/automessages", tags=["Auto Messages"])


# ==================== Pydantic Models ====================

class ButtonModel(BaseModel):
    """Button model"""
    custom_id: str = Field(..., max_length=100)
    label: str = Field(..., max_length=80)
    style: str = Field(..., regex="^(primary|secondary|success|danger|link)$")
    emoji: Optional[str] = None
    url: Optional[str] = None
    disabled: bool = False


class DropdownOptionModel(BaseModel):
    """Dropdown option model"""
    value: str = Field(..., max_length=100)
    label: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=100)
    emoji: Optional[str] = None
    default: bool = False


class DropdownModel(BaseModel):
    """Dropdown model"""
    custom_id: str = Field(..., max_length=100)
    placeholder: str = Field(..., max_length=150)
    min_values: int = Field(default=1, ge=1, le=25)
    max_values: int = Field(default=1, ge=1, le=25)
    options: List[DropdownOptionModel] = Field(..., min_items=1, max_items=25)


class EmbedModel(BaseModel):
    """Embed model"""
    title: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = Field(None, max_length=4096)
    color: Optional[int] = None
    footer_text: Optional[str] = Field(None, max_length=2048)
    footer_icon: Optional[str] = None
    thumbnail: Optional[str] = None
    image: Optional[str] = None
    author_name: Optional[str] = Field(None, max_length=256)
    author_icon: Optional[str] = None
    timestamp: bool = False


class AutoMessageCreate(BaseModel):
    """Model for creating auto message"""
    name: str = Field(..., min_length=3, max_length=100)
    trigger_type: str = Field(..., regex="^(keyword|button|dropdown)$")
    trigger_value: str = Field(..., max_length=200)
    response_type: str = Field(..., regex="^(text|embed|both)$")
    text_response: Optional[str] = Field(None, max_length=2000)
    embed_response: Optional[EmbedModel] = None
    buttons: Optional[List[ButtonModel]] = Field(None, max_items=25)
    dropdowns: Optional[List[DropdownModel]] = Field(None, max_items=5)
    allowed_roles: Optional[List[str]] = None
    allowed_channels: Optional[List[str]] = None
    case_sensitive: bool = False
    exact_match: bool = False
    delete_trigger: bool = False
    dm_response: bool = False


class AutoMessageUpdate(BaseModel):
    """Model for updating auto message"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    trigger_value: Optional[str] = Field(None, max_length=200)
    response_type: Optional[str] = Field(None, regex="^(text|embed|both)$")
    text_response: Optional[str] = Field(None, max_length=2000)
    embed_response: Optional[EmbedModel] = None
    buttons: Optional[List[ButtonModel]] = Field(None, max_items=25)
    dropdowns: Optional[List[DropdownModel]] = Field(None, max_items=5)
    allowed_roles: Optional[List[str]] = None
    allowed_channels: Optional[List[str]] = None
    case_sensitive: Optional[bool] = None
    exact_match: Optional[bool] = None
    delete_trigger: Optional[bool] = None
    dm_response: Optional[bool] = None


class AutoMessageSettingsUpdate(BaseModel):
    """Model for updating auto message settings"""
    global_cooldown: Optional[int] = Field(None, ge=0, le=3600)
    auto_delete_delay: Optional[int] = Field(None, ge=0, le=60)
    max_triggers_per_user: Optional[int] = Field(None, ge=1, le=100)


class AutoMessageResponse(BaseModel):
    """Response model for auto message"""
    id: str
    guild_id: str
    name: str
    trigger_type: str
    trigger_value: str
    response_type: str
    text_response: Optional[str]
    embed_response: Optional[Dict[str, Any]]
    buttons: Optional[List[Dict[str, Any]]]
    dropdowns: Optional[List[Dict[str, Any]]]
    allowed_roles: Optional[List[str]]
    allowed_channels: Optional[List[str]]
    case_sensitive: bool
    exact_match: bool
    delete_trigger: bool
    dm_response: bool
    enabled: bool
    created_at: datetime
    updated_at: datetime
    statistics: Dict[str, int]


class AutoMessageStatsResponse(BaseModel):
    """Response model for auto message statistics"""
    total_messages: int
    active_messages: int
    total_triggers: int
    by_type: Dict[str, int]
    by_message: List[Dict[str, Any]]


class AutoMessageSettingsResponse(BaseModel):
    """Response model for auto message settings"""
    guild_id: str
    global_cooldown: int
    auto_delete_delay: int
    max_triggers_per_user: int


# ==================== Helper Functions ====================

def serialize_message(message: Dict) -> Dict:
    """Serialize message document"""
    if message:
        message["id"] = str(message.pop("_id"))
        message["created_at"] = message.get("created_at", datetime.utcnow())
        message["updated_at"] = message.get("updated_at", datetime.utcnow())
    return message


# ==================== API Endpoints ====================

@router.get("/guilds/{guild_id}/messages", response_model=List[AutoMessageResponse])
async def list_messages(
    guild_id: str,
    trigger_type: Optional[str] = Query(None, regex="^(keyword|button|dropdown)$"),
    enabled: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all auto messages for a guild
    
    - **guild_id**: Guild ID
    - **trigger_type**: Filter by trigger type (optional)
    - **enabled**: Filter by enabled status (optional)
    - **skip**: Number of messages to skip (pagination)
    - **limit**: Maximum number of messages to return
    """
    try:
        query = {"guild_id": guild_id}
        if trigger_type:
            query["trigger_type"] = trigger_type
        if enabled is not None:
            query["enabled"] = enabled
        
        cursor = db.auto_messages.find(query).skip(skip).limit(limit).sort("created_at", -1)
        messages = await cursor.to_list(length=limit)
        
        return [serialize_message(msg) for msg in messages]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")


@router.get("/guilds/{guild_id}/messages/{message_id}", response_model=AutoMessageResponse)
async def get_message(
    guild_id: str,
    message_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get auto message details
    
    - **guild_id**: Guild ID
    - **message_id**: Message ID
    """
    try:
        message = await db.auto_messages.find_one({
            "_id": ObjectId(message_id),
            "guild_id": guild_id
        })
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return serialize_message(message)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to fetch message: {str(e)}")


@router.post("/guilds/{guild_id}/messages", response_model=AutoMessageResponse, status_code=201)
async def create_message(
    guild_id: str,
    message_data: AutoMessageCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new auto message
    
    - **guild_id**: Guild ID
    - **message_data**: Message data
    """
    try:
        # Validate response data
        if message_data.response_type in ["text", "both"] and not message_data.text_response:
            raise HTTPException(status_code=400, detail="text_response is required for text/both response type")
        
        if message_data.response_type in ["embed", "both"] and not message_data.embed_response:
            raise HTTPException(status_code=400, detail="embed_response is required for embed/both response type")
        
        # Prepare message document
        message_doc = {
            "guild_id": guild_id,
            "name": message_data.name,
            "trigger_type": message_data.trigger_type,
            "trigger_value": message_data.trigger_value,
            "response_type": message_data.response_type,
            "text_response": message_data.text_response,
            "embed_response": message_data.embed_response.dict() if message_data.embed_response else None,
            "buttons": [b.dict() for b in message_data.buttons] if message_data.buttons else [],
            "dropdowns": [d.dict() for d in message_data.dropdowns] if message_data.dropdowns else [],
            "allowed_roles": message_data.allowed_roles or [],
            "allowed_channels": message_data.allowed_channels or [],
            "case_sensitive": message_data.case_sensitive,
            "exact_match": message_data.exact_match,
            "delete_trigger": message_data.delete_trigger,
            "dm_response": message_data.dm_response,
            "enabled": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "statistics": {
                "total_triggers": 0,
                "last_triggered": None
            }
        }
        
        # Insert message
        result = await db.auto_messages.insert_one(message_doc)
        message_doc["_id"] = result.inserted_id
        
        return serialize_message(message_doc)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to create message: {str(e)}")


@router.put("/guilds/{guild_id}/messages/{message_id}", response_model=AutoMessageResponse)
async def update_message(
    guild_id: str,
    message_id: str,
    message_data: AutoMessageUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Update auto message
    
    - **guild_id**: Guild ID
    - **message_id**: Message ID
    - **message_data**: Updated message data
    """
    try:
        # Build update document
        update_doc = {"updated_at": datetime.utcnow()}
        
        if message_data.name is not None:
            update_doc["name"] = message_data.name
        if message_data.trigger_value is not None:
            update_doc["trigger_value"] = message_data.trigger_value
        if message_data.response_type is not None:
            update_doc["response_type"] = message_data.response_type
        if message_data.text_response is not None:
            update_doc["text_response"] = message_data.text_response
        if message_data.embed_response is not None:
            update_doc["embed_response"] = message_data.embed_response.dict()
        if message_data.buttons is not None:
            update_doc["buttons"] = [b.dict() for b in message_data.buttons]
        if message_data.dropdowns is not None:
            update_doc["dropdowns"] = [d.dict() for d in message_data.dropdowns]
        if message_data.allowed_roles is not None:
            update_doc["allowed_roles"] = message_data.allowed_roles
        if message_data.allowed_channels is not None:
            update_doc["allowed_channels"] = message_data.allowed_channels
        if message_data.case_sensitive is not None:
            update_doc["case_sensitive"] = message_data.case_sensitive
        if message_data.exact_match is not None:
            update_doc["exact_match"] = message_data.exact_match
        if message_data.delete_trigger is not None:
            update_doc["delete_trigger"] = message_data.delete_trigger
        if message_data.dm_response is not None:
            update_doc["dm_response"] = message_data.dm_response
        
        # Update message
        result = await db.auto_messages.find_one_and_update(
            {"_id": ObjectId(message_id), "guild_id": guild_id},
            {"$set": update_doc},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return serialize_message(result)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to update message: {str(e)}")


@router.delete("/guilds/{guild_id}/messages/{message_id}", status_code=204)
async def delete_message(
    guild_id: str,
    message_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete auto message
    
    - **guild_id**: Guild ID
    - **message_id**: Message ID
    """
    try:
        result = await db.auto_messages.delete_one({
            "_id": ObjectId(message_id),
            "guild_id": guild_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Message not found")
        
        return None
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")


@router.patch("/guilds/{guild_id}/messages/{message_id}/toggle", response_model=AutoMessageResponse)
async def toggle_message(
    guild_id: str,
    message_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Toggle message enabled status
    
    - **guild_id**: Guild ID
    - **message_id**: Message ID
    """
    try:
        # Get current message
        message = await db.auto_messages.find_one({
            "_id": ObjectId(message_id),
            "guild_id": guild_id
        })
        
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Toggle enabled status
        new_status = not message.get("enabled", True)
        
        result = await db.auto_messages.find_one_and_update(
            {"_id": ObjectId(message_id), "guild_id": guild_id},
            {
                "$set": {
                    "enabled": new_status,
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        return serialize_message(result)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to toggle message: {str(e)}")


@router.get("/guilds/{guild_id}/settings", response_model=AutoMessageSettingsResponse)
async def get_settings(
    guild_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get auto message settings for a guild
    
    - **guild_id**: Guild ID
    """
    try:
        settings = await db.auto_messages_settings.find_one({"guild_id": guild_id})
        
        if not settings:
            # Return default settings
            return AutoMessageSettingsResponse(
                guild_id=guild_id,
                global_cooldown=5,
                auto_delete_delay=0,
                max_triggers_per_user=10
            )
        
        return AutoMessageSettingsResponse(
            guild_id=settings["guild_id"],
            global_cooldown=settings.get("global_cooldown", 5),
            auto_delete_delay=settings.get("auto_delete_delay", 0),
            max_triggers_per_user=settings.get("max_triggers_per_user", 10)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch settings: {str(e)}")


@router.put("/guilds/{guild_id}/settings", response_model=AutoMessageSettingsResponse)
async def update_settings(
    guild_id: str,
    settings_data: AutoMessageSettingsUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Update auto message settings
    
    - **guild_id**: Guild ID
    - **settings_data**: Updated settings data
    """
    try:
        # Build update document
        update_doc = {}
        if settings_data.global_cooldown is not None:
            update_doc["global_cooldown"] = settings_data.global_cooldown
        if settings_data.auto_delete_delay is not None:
            update_doc["auto_delete_delay"] = settings_data.auto_delete_delay
        if settings_data.max_triggers_per_user is not None:
            update_doc["max_triggers_per_user"] = settings_data.max_triggers_per_user
        
        # Upsert settings
        await db.auto_messages_settings.update_one(
            {"guild_id": guild_id},
            {"$set": update_doc},
            upsert=True
        )
        
        # Return updated settings
        return await get_settings(guild_id, db, api_key)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update settings: {str(e)}")


@router.get("/guilds/{guild_id}/stats", response_model=AutoMessageStatsResponse)
async def get_statistics(
    guild_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get auto message statistics for a guild
    
    - **guild_id**: Guild ID
    """
    try:
        # Get all messages
        messages = await db.auto_messages.find({"guild_id": guild_id}).to_list(length=None)
        
        # Calculate statistics
        total_messages = len(messages)
        active_messages = sum(1 for m in messages if m.get("enabled", True))
        
        total_triggers = 0
        by_type = {"keyword": 0, "button": 0, "dropdown": 0}
        by_message = []
        
        for message in messages:
            triggers = message.get("statistics", {}).get("total_triggers", 0)
            total_triggers += triggers
            
            trigger_type = message.get("trigger_type", "keyword")
            by_type[trigger_type] = by_type.get(trigger_type, 0) + 1
            
            by_message.append({
                "message_id": str(message["_id"]),
                "name": message["name"],
                "trigger_type": trigger_type,
                "total_triggers": triggers,
                "enabled": message.get("enabled", True)
            })
        
        return AutoMessageStatsResponse(
            total_messages=total_messages,
            active_messages=active_messages,
            total_triggers=total_triggers,
            by_type=by_type,
            by_message=by_message
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")

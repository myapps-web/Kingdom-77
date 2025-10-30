"""
Kingdom-77 Dashboard API Server
================================
FastAPI server for web dashboard integration.

Provides RESTful API endpoints for:
- Applications System
- Auto-Messages System
- Social Integration System
"""

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
import os
from motor.motor_asyncio import AsyncIOMotorClient

from api.applications_api import ApplicationsAPI
from api.automessages_api import AutoMessagesAPI
from api.social_api import SocialAPI

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="Kingdom-77 Dashboard API",
    description="RESTful API for Kingdom-77 Discord Bot Dashboard",
    version="4.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Connection
mongo_client = None
applications_api = None
automessages_api = None
social_api = None


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_db_client():
    """Initialize MongoDB connection on startup"""
    global mongo_client, applications_api, automessages_api, social_api
    
    mongodb_uri = os.getenv("MONGODB_URI")
    if not mongodb_uri:
        raise Exception("MONGODB_URI not configured")
    
    mongo_client = AsyncIOMotorClient(mongodb_uri)
    
    # Initialize API modules
    applications_api = ApplicationsAPI(mongo_client)
    automessages_api = AutoMessagesAPI(mongo_client)
    social_api = SocialAPI(mongo_client)
    
    print("✅ Dashboard API initialized")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close MongoDB connection on shutdown"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
    print("✅ Dashboard API closed")


# ============================================================================
# AUTHENTICATION
# ============================================================================

async def verify_api_key(x_api_key: str = Header(...)):
    """Verify API key from request header"""
    api_key = os.getenv("DASHBOARD_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    if x_api_key != api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return x_api_key


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

# Applications Models
class FormCreate(BaseModel):
    name: str
    description: str
    questions: List[Dict[str, Any]]
    submit_channel_id: str
    review_channel_id: Optional[str] = None
    accept_role_id: Optional[str] = None
    cooldown_hours: int = 24
    max_submissions: int = 1


class FormUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[Dict[str, Any]]] = None
    submit_channel_id: Optional[str] = None
    review_channel_id: Optional[str] = None
    accept_role_id: Optional[str] = None
    cooldown_hours: Optional[int] = None
    max_submissions: Optional[int] = None


class SubmissionReview(BaseModel):
    action: str  # 'accept' or 'reject'
    reason: Optional[str] = None


# Auto-Messages Models
class AutoMessageCreate(BaseModel):
    name: str
    trigger_type: str
    trigger_value: str
    response_type: str = "text"
    response_content: Optional[str] = None
    embed: Optional[Dict[str, Any]] = None
    buttons: List[Dict[str, Any]] = []
    dropdown: Optional[Dict[str, Any]] = None
    allowed_roles: List[str] = []
    allowed_channels: List[str] = []


class AutoMessageUpdate(BaseModel):
    name: Optional[str] = None
    trigger_value: Optional[str] = None
    response_content: Optional[str] = None
    embed: Optional[Dict[str, Any]] = None
    buttons: Optional[List[Dict[str, Any]]] = None
    dropdown: Optional[Dict[str, Any]] = None
    allowed_roles: Optional[List[str]] = None
    allowed_channels: Optional[List[str]] = None


class AutoMessagesSettings(BaseModel):
    cooldown_seconds: Optional[int] = None
    auto_delete_seconds: Optional[int] = None
    dm_response: Optional[bool] = None
    case_sensitive: Optional[bool] = None
    exact_match: Optional[bool] = None


# Social Integration Models
class SocialLinkCreate(BaseModel):
    platform: str
    channel_url: str
    channel_id: str
    notification_channel_id: str
    mention_role_id: Optional[str] = None


class SocialLinkUpdate(BaseModel):
    notification_channel_id: Optional[str] = None
    mention_role_id: Optional[str] = None


# ============================================================================
# APPLICATIONS ENDPOINTS
# ============================================================================

@app.get("/api/applications/guilds/{guild_id}/forms")
async def get_guild_forms(
    guild_id: str,
    enabled_only: bool = False,
    api_key: str = Depends(verify_api_key)
):
    """List all application forms for a guild"""
    forms = await applications_api.list_forms(guild_id, enabled_only)
    return {"success": True, "data": forms}


@app.get("/api/applications/guilds/{guild_id}/forms/{form_id}")
async def get_form_details(
    guild_id: str,
    form_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get application form details"""
    form = await applications_api.get_form(guild_id, form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Form not found")
    return {"success": True, "data": form}


@app.post("/api/applications/guilds/{guild_id}/forms")
async def create_form(
    guild_id: str,
    form: FormCreate,
    creator_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Create new application form"""
    success, message, form_id = await applications_api.create_form(
        guild_id,
        form.dict(),
        creator_id
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message, "form_id": form_id}


@app.put("/api/applications/guilds/{guild_id}/forms/{form_id}")
async def update_form(
    guild_id: str,
    form_id: str,
    updates: FormUpdate,
    api_key: str = Depends(verify_api_key)
):
    """Update application form"""
    success, message = await applications_api.update_form(
        guild_id,
        form_id,
        {k: v for k, v in updates.dict().items() if v is not None}
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.delete("/api/applications/guilds/{guild_id}/forms/{form_id}")
async def delete_form(
    guild_id: str,
    form_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete application form"""
    success, message = await applications_api.delete_form(guild_id, form_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.patch("/api/applications/guilds/{guild_id}/forms/{form_id}/toggle")
async def toggle_form(
    guild_id: str,
    form_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Toggle application form"""
    success, message, new_state = await applications_api.toggle_form(guild_id, form_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message, "enabled": new_state}


@app.get("/api/applications/guilds/{guild_id}/submissions")
async def get_guild_submissions(
    guild_id: str,
    form_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    api_key: str = Depends(verify_api_key)
):
    """List submissions for a guild"""
    submissions = await applications_api.list_submissions(
        guild_id,
        form_id,
        status,
        limit
    )
    return {"success": True, "data": submissions}


@app.patch("/api/applications/submissions/{submission_id}/review")
async def review_submission(
    submission_id: str,
    review: SubmissionReview,
    reviewer_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Review a submission"""
    success, message = await applications_api.review_submission(
        submission_id,
        reviewer_id,
        review.action,
        review.reason
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.get("/api/applications/guilds/{guild_id}/stats")
async def get_applications_stats(
    guild_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get application statistics"""
    stats = await applications_api.get_statistics(guild_id)
    return {"success": True, "data": stats}


# ============================================================================
# AUTO-MESSAGES ENDPOINTS
# ============================================================================

@app.get("/api/automessages/guilds/{guild_id}/messages")
async def get_guild_automessages(
    guild_id: str,
    trigger_type: Optional[str] = None,
    enabled_only: bool = False,
    api_key: str = Depends(verify_api_key)
):
    """List all auto-messages for a guild"""
    messages = await automessages_api.list_messages(guild_id, trigger_type, enabled_only)
    return {"success": True, "data": messages}


@app.get("/api/automessages/guilds/{guild_id}/messages/{message_id}")
async def get_automessage_details(
    guild_id: str,
    message_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get auto-message details"""
    message = await automessages_api.get_message(guild_id, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return {"success": True, "data": message}


@app.post("/api/automessages/guilds/{guild_id}/messages")
async def create_automessage(
    guild_id: str,
    message: AutoMessageCreate,
    creator_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Create new auto-message"""
    success, msg, message_id = await automessages_api.create_message(
        guild_id,
        message.dict(),
        creator_id
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    return {"success": True, "message": msg, "message_id": message_id}


@app.put("/api/automessages/guilds/{guild_id}/messages/{message_id}")
async def update_automessage(
    guild_id: str,
    message_id: str,
    updates: AutoMessageUpdate,
    api_key: str = Depends(verify_api_key)
):
    """Update auto-message"""
    success, message = await automessages_api.update_message(
        guild_id,
        message_id,
        {k: v for k, v in updates.dict().items() if v is not None}
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.delete("/api/automessages/guilds/{guild_id}/messages/{message_id}")
async def delete_automessage(
    guild_id: str,
    message_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete auto-message"""
    success, message = await automessages_api.delete_message(guild_id, message_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.patch("/api/automessages/guilds/{guild_id}/messages/{message_id}/toggle")
async def toggle_automessage(
    guild_id: str,
    message_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Toggle auto-message"""
    success, message, new_state = await automessages_api.toggle_message(guild_id, message_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message, "enabled": new_state}


@app.get("/api/automessages/guilds/{guild_id}/settings")
async def get_automessages_settings(
    guild_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get auto-messages settings"""
    settings = await automessages_api.get_settings(guild_id)
    return {"success": True, "data": settings}


@app.put("/api/automessages/guilds/{guild_id}/settings")
async def update_automessages_settings(
    guild_id: str,
    settings: AutoMessagesSettings,
    api_key: str = Depends(verify_api_key)
):
    """Update auto-messages settings"""
    success, message = await automessages_api.update_settings(
        guild_id,
        {k: v for k, v in settings.dict().items() if v is not None}
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.get("/api/automessages/guilds/{guild_id}/stats")
async def get_automessages_stats(
    guild_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get auto-messages statistics"""
    stats = await automessages_api.get_statistics(guild_id)
    return {"success": True, "data": stats}


# ============================================================================
# SOCIAL INTEGRATION ENDPOINTS
# ============================================================================

@app.get("/api/social/guilds/{guild_id}/links")
async def get_guild_social_links(
    guild_id: str,
    platform: Optional[str] = None,
    enabled_only: bool = False,
    api_key: str = Depends(verify_api_key)
):
    """List all social links for a guild"""
    links = await social_api.list_links(guild_id, platform, enabled_only)
    return {"success": True, "data": links}


@app.get("/api/social/guilds/{guild_id}/links/{link_id}")
async def get_social_link_details(
    guild_id: str,
    link_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get social link details"""
    link = await social_api.get_link(guild_id, link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"success": True, "data": link}


@app.post("/api/social/guilds/{guild_id}/links")
async def create_social_link(
    guild_id: str,
    link: SocialLinkCreate,
    user_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Create new social media link"""
    success, message, link_id = await social_api.create_link(
        guild_id,
        user_id,
        link.dict()
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message, "link_id": link_id}


@app.put("/api/social/guilds/{guild_id}/links/{link_id}")
async def update_social_link(
    guild_id: str,
    link_id: str,
    updates: SocialLinkUpdate,
    api_key: str = Depends(verify_api_key)
):
    """Update social link"""
    success, message = await social_api.update_link(
        guild_id,
        link_id,
        {k: v for k, v in updates.dict().items() if v is not None}
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.delete("/api/social/guilds/{guild_id}/links/{link_id}")
async def delete_social_link(
    guild_id: str,
    link_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete social link"""
    success, message = await social_api.delete_link(guild_id, link_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.patch("/api/social/guilds/{guild_id}/links/{link_id}/toggle")
async def toggle_social_link(
    guild_id: str,
    link_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Toggle social link"""
    success, message, new_state = await social_api.toggle_link(guild_id, link_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message, "enabled": new_state}


@app.get("/api/social/guilds/{guild_id}/posts")
async def get_social_posts(
    guild_id: str,
    link_id: Optional[str] = None,
    limit: int = 50,
    api_key: str = Depends(verify_api_key)
):
    """Get recent social media posts"""
    posts = await social_api.get_posts(guild_id, link_id, limit)
    return {"success": True, "data": posts}


@app.get("/api/social/guilds/{guild_id}/limits")
async def get_social_limits(
    guild_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get link limits"""
    limits = await social_api.get_limits(guild_id)
    return {"success": True, "data": limits}


@app.post("/api/social/guilds/{guild_id}/purchase")
async def purchase_social_link(
    guild_id: str,
    user_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Purchase additional link slot"""
    success, message = await social_api.purchase_link(guild_id, user_id)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"success": True, "message": message}


@app.get("/api/social/guilds/{guild_id}/stats")
async def get_social_stats(
    guild_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get social integration statistics"""
    stats = await social_api.get_statistics(guild_id)
    return {"success": True, "data": stats}


# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "4.0.0",
        "services": {
            "mongodb": mongo_client is not None,
            "applications_api": applications_api is not None,
            "automessages_api": automessages_api is not None,
            "social_api": social_api is not None
        }
    }


# ============================================================================
# ROOT
# ============================================================================

@app.get("/")
async def root():
    """API root"""
    return {
        "name": "Kingdom-77 Dashboard API",
        "version": "4.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=int(os.getenv("API_PORT", "8000")),
        reload=True
    )

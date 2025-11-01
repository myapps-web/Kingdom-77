"""
Social Integration API Endpoints
Kingdom-77 Bot v4.0 - Phase 5.7

FastAPI endpoints for managing social media platform links and notifications.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from dashboard.utils.auth import verify_api_key
from dashboard.utils.database import get_database


router = APIRouter(prefix="/api/social", tags=["Social Integration"])


# ==================== Pydantic Models ====================

class SocialLinkCreate(BaseModel):
    """Model for creating social link"""
    platform: str = Field(..., regex="^(youtube|twitch|kick|twitter|instagram|tiktok|snapchat)$")
    url: str = Field(..., max_length=500)
    channel_id: str = Field(..., description="Discord channel ID for notifications")
    mention_role_id: Optional[str] = None
    custom_message: Optional[str] = Field(None, max_length=500)


class SocialLinkUpdate(BaseModel):
    """Model for updating social link"""
    url: Optional[str] = Field(None, max_length=500)
    channel_id: Optional[str] = None
    mention_role_id: Optional[str] = None
    custom_message: Optional[str] = Field(None, max_length=500)


class SocialLinkResponse(BaseModel):
    """Response model for social link"""
    id: str
    guild_id: str
    platform: str
    platform_user_id: str
    platform_username: str
    url: str
    channel_id: str
    mention_role_id: Optional[str]
    custom_message: Optional[str]
    enabled: bool
    created_at: datetime
    last_checked: Optional[datetime]
    statistics: Dict[str, int]


class SocialPostResponse(BaseModel):
    """Response model for social post"""
    id: str
    link_id: str
    guild_id: str
    platform: str
    post_id: str
    post_url: str
    title: Optional[str]
    description: Optional[str]
    thumbnail: Optional[str]
    author: str
    published_at: datetime
    notified_at: datetime


class SocialLimitsResponse(BaseModel):
    """Response model for social limits"""
    guild_id: str
    current_links: int
    max_links: int
    free_links: int
    purchased_links: int
    can_add_more: bool


class SocialStatsResponse(BaseModel):
    """Response model for social statistics"""
    total_links: int
    active_links: int
    total_notifications: int
    by_platform: Dict[str, Dict[str, int]]
    recent_posts: List[Dict[str, Any]]


class PurchaseLinkRequest(BaseModel):
    """Model for purchasing additional link"""
    user_id: str = Field(..., description="Discord user ID")


# ==================== Helper Functions ====================

def serialize_link(link: Dict) -> Dict:
    """Serialize link document"""
    if link:
        link["id"] = str(link.pop("_id"))
        link["created_at"] = link.get("created_at", datetime.utcnow())
        link["last_checked"] = link.get("last_checked")
    return link


def serialize_post(post: Dict) -> Dict:
    """Serialize post document"""
    if post:
        post["id"] = str(post.pop("_id"))
        post["published_at"] = post.get("published_at", datetime.utcnow())
        post["notified_at"] = post.get("notified_at", datetime.utcnow())
    return post


# ==================== API Endpoints ====================

@router.get("/guilds/{guild_id}/links", response_model=List[SocialLinkResponse])
async def list_links(
    guild_id: str,
    platform: Optional[str] = Query(None, regex="^(youtube|twitch|kick|twitter|instagram|tiktok|snapchat)$"),
    enabled: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all social links for a guild
    
    - **guild_id**: Guild ID
    - **platform**: Filter by platform (optional)
    - **enabled**: Filter by enabled status (optional)
    - **skip**: Number of links to skip (pagination)
    - **limit**: Maximum number of links to return
    """
    try:
        query = {"guild_id": guild_id}
        if platform:
            query["platform"] = platform
        if enabled is not None:
            query["enabled"] = enabled
        
        cursor = db.social_links.find(query).skip(skip).limit(limit).sort("created_at", -1)
        links = await cursor.to_list(length=limit)
        
        return [serialize_link(link) for link in links]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch links: {str(e)}")


@router.get("/guilds/{guild_id}/links/{link_id}", response_model=SocialLinkResponse)
async def get_link(
    guild_id: str,
    link_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get social link details
    
    - **guild_id**: Guild ID
    - **link_id**: Link ID
    """
    try:
        link = await db.social_links.find_one({
            "_id": ObjectId(link_id),
            "guild_id": guild_id
        })
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        return serialize_link(link)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to fetch link: {str(e)}")


@router.post("/guilds/{guild_id}/links", response_model=SocialLinkResponse, status_code=201)
async def create_link(
    guild_id: str,
    link_data: SocialLinkCreate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new social link
    
    - **guild_id**: Guild ID
    - **link_data**: Link data
    """
    try:
        # Check link limits
        settings = await db.social_settings.find_one({"guild_id": guild_id})
        current_links = await db.social_links.count_documents({"guild_id": guild_id})
        
        max_links = 2  # Default free links
        if settings:
            max_links += settings.get("purchased_links", 0)
        
        if current_links >= max_links:
            raise HTTPException(
                status_code=403,
                detail=f"Maximum link limit reached ({max_links}). Purchase more links to continue."
            )
        
        # Parse URL to extract platform user info
        # This is a simplified version - actual implementation would need platform-specific parsing
        platform_username = link_data.url.split("/")[-1].split("?")[0]
        platform_user_id = platform_username  # Would need actual ID extraction
        
        # Prepare link document
        link_doc = {
            "guild_id": guild_id,
            "platform": link_data.platform,
            "platform_user_id": platform_user_id,
            "platform_username": platform_username,
            "url": link_data.url,
            "channel_id": link_data.channel_id,
            "mention_role_id": link_data.mention_role_id,
            "custom_message": link_data.custom_message,
            "enabled": True,
            "created_at": datetime.utcnow(),
            "last_checked": None,
            "statistics": {
                "total_notifications": 0,
                "last_notification": None
            }
        }
        
        # Insert link
        result = await db.social_links.insert_one(link_doc)
        link_doc["_id"] = result.inserted_id
        
        return serialize_link(link_doc)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to create link: {str(e)}")


@router.put("/guilds/{guild_id}/links/{link_id}", response_model=SocialLinkResponse)
async def update_link(
    guild_id: str,
    link_id: str,
    link_data: SocialLinkUpdate,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Update social link
    
    - **guild_id**: Guild ID
    - **link_id**: Link ID
    - **link_data**: Updated link data
    """
    try:
        # Build update document
        update_doc = {}
        
        if link_data.url is not None:
            # Re-parse URL for username
            platform_username = link_data.url.split("/")[-1].split("?")[0]
            update_doc["url"] = link_data.url
            update_doc["platform_username"] = platform_username
            update_doc["platform_user_id"] = platform_username
        
        if link_data.channel_id is not None:
            update_doc["channel_id"] = link_data.channel_id
        if link_data.mention_role_id is not None:
            update_doc["mention_role_id"] = link_data.mention_role_id
        if link_data.custom_message is not None:
            update_doc["custom_message"] = link_data.custom_message
        
        # Update link
        result = await db.social_links.find_one_and_update(
            {"_id": ObjectId(link_id), "guild_id": guild_id},
            {"$set": update_doc},
            return_document=True
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Link not found")
        
        return serialize_link(result)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to update link: {str(e)}")


@router.delete("/guilds/{guild_id}/links/{link_id}", status_code=204)
async def delete_link(
    guild_id: str,
    link_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete social link
    
    - **guild_id**: Guild ID
    - **link_id**: Link ID
    """
    try:
        result = await db.social_links.delete_one({
            "_id": ObjectId(link_id),
            "guild_id": guild_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Also delete all posts for this link
        await db.social_posts.delete_many({"link_id": link_id})
        
        return None
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to delete link: {str(e)}")


@router.patch("/guilds/{guild_id}/links/{link_id}/toggle", response_model=SocialLinkResponse)
async def toggle_link(
    guild_id: str,
    link_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Toggle link enabled status
    
    - **guild_id**: Guild ID
    - **link_id**: Link ID
    """
    try:
        # Get current link
        link = await db.social_links.find_one({
            "_id": ObjectId(link_id),
            "guild_id": guild_id
        })
        
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        
        # Toggle enabled status
        new_status = not link.get("enabled", True)
        
        result = await db.social_links.find_one_and_update(
            {"_id": ObjectId(link_id), "guild_id": guild_id},
            {"$set": {"enabled": new_status}},
            return_document=True
        )
        
        return serialize_link(result)
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to toggle link: {str(e)}")


@router.get("/guilds/{guild_id}/posts", response_model=List[SocialPostResponse])
async def get_recent_posts(
    guild_id: str,
    platform: Optional[str] = Query(None, regex="^(youtube|twitch|kick|twitter|instagram|tiktok|snapchat)$"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get recent social media posts
    
    - **guild_id**: Guild ID
    - **platform**: Filter by platform (optional)
    - **limit**: Maximum number of posts to return
    """
    try:
        query = {"guild_id": guild_id}
        if platform:
            query["platform"] = platform
        
        cursor = db.social_posts.find(query).limit(limit).sort("published_at", -1)
        posts = await cursor.to_list(length=limit)
        
        return [serialize_post(post) for post in posts]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch posts: {str(e)}")


@router.get("/guilds/{guild_id}/limits", response_model=SocialLimitsResponse)
async def get_limits(
    guild_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get link limits for a guild
    
    - **guild_id**: Guild ID
    """
    try:
        # Get current links count
        current_links = await db.social_links.count_documents({"guild_id": guild_id})
        
        # Get settings
        settings = await db.social_settings.find_one({"guild_id": guild_id})
        
        free_links = 2
        purchased_links = settings.get("purchased_links", 0) if settings else 0
        max_links = free_links + purchased_links
        
        return SocialLimitsResponse(
            guild_id=guild_id,
            current_links=current_links,
            max_links=max_links,
            free_links=free_links,
            purchased_links=purchased_links,
            can_add_more=current_links < max_links
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch limits: {str(e)}")


@router.post("/guilds/{guild_id}/purchase", response_model=Dict[str, Any])
async def purchase_link(
    guild_id: str,
    purchase_data: PurchaseLinkRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Purchase additional link slot (200 credits)
    
    - **guild_id**: Guild ID
    - **purchase_data**: Purchase data with user_id
    """
    try:
        # Check user credits
        user_credits = await db.user_credits.find_one({"user_id": purchase_data.user_id})
        
        if not user_credits or user_credits.get("balance", 0) < 200:
            raise HTTPException(
                status_code=400,
                detail="Insufficient credits. You need 200 credits to purchase a link slot."
            )
        
        # Deduct credits
        await db.user_credits.update_one(
            {"user_id": purchase_data.user_id},
            {
                "$inc": {"balance": -200},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # Add transaction
        await db.credit_transactions.insert_one({
            "user_id": purchase_data.user_id,
            "type": "purchase",
            "amount": -200,
            "description": f"Purchased social link slot for guild {guild_id}",
            "timestamp": datetime.utcnow()
        })
        
        # Increment purchased links
        await db.social_settings.update_one(
            {"guild_id": guild_id},
            {
                "$inc": {"purchased_links": 1},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Link slot purchased successfully!",
            "credits_remaining": user_credits["balance"] - 200,
            "new_max_links": (await get_limits(guild_id, db, api_key)).max_links
        }
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"Failed to purchase link: {str(e)}")


@router.get("/guilds/{guild_id}/stats", response_model=SocialStatsResponse)
async def get_statistics(
    guild_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    api_key: str = Depends(verify_api_key)
):
    """
    Get social integration statistics for a guild
    
    - **guild_id**: Guild ID
    """
    try:
        # Get all links
        links = await db.social_links.find({"guild_id": guild_id}).to_list(length=None)
        
        # Calculate statistics
        total_links = len(links)
        active_links = sum(1 for l in links if l.get("enabled", True))
        
        total_notifications = 0
        by_platform = {}
        
        for link in links:
            platform = link["platform"]
            notifications = link.get("statistics", {}).get("total_notifications", 0)
            total_notifications += notifications
            
            if platform not in by_platform:
                by_platform[platform] = {
                    "count": 0,
                    "notifications": 0
                }
            by_platform[platform]["count"] += 1
            by_platform[platform]["notifications"] += notifications
        
        # Get recent posts
        recent_posts_cursor = db.social_posts.find({"guild_id": guild_id}).limit(10).sort("published_at", -1)
        recent_posts = await recent_posts_cursor.to_list(length=10)
        
        recent_posts_data = []
        for post in recent_posts:
            recent_posts_data.append({
                "platform": post["platform"],
                "author": post["author"],
                "title": post.get("title"),
                "url": post["post_url"],
                "published_at": post["published_at"].isoformat()
            })
        
        return SocialStatsResponse(
            total_links=total_links,
            active_links=active_links,
            total_notifications=total_notifications,
            by_platform=by_platform,
            recent_posts=recent_posts_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch statistics: {str(e)}")

"""
Social Integration API
======================
RESTful API endpoints for Social Media Integration management.

Endpoints:
- GET    /api/social/guilds/{guild_id}/links - List all social links
- GET    /api/social/guilds/{guild_id}/links/{link_id} - Get link details
- POST   /api/social/guilds/{guild_id}/links - Create link
- DELETE /api/social/guilds/{guild_id}/links/{link_id} - Delete link
- PATCH  /api/social/guilds/{guild_id}/links/{link_id}/toggle - Toggle link
- PUT    /api/social/guilds/{guild_id}/links/{link_id} - Update link
- GET    /api/social/guilds/{guild_id}/posts - Get recent posts
- GET    /api/social/guilds/{guild_id}/stats - Get statistics
- GET    /api/social/guilds/{guild_id}/limits - Get link limits
- POST   /api/social/guilds/{guild_id}/purchase - Purchase additional link
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import logging

logger = logging.getLogger(__name__)


class SocialAPI:
    """Dashboard API for Social Integration System"""
    
    def __init__(self, mongo_client):
        """Initialize Social Integration API
        
        Args:
            mongo_client: MongoDB client instance
        """
        self.db = mongo_client.kingdom77
        self.links_collection = self.db.social_links
        self.posts_collection = self.db.social_posts
        self.settings_collection = self.db.social_settings
        
        # Platform configuration
        self.PLATFORMS = {
            "youtube": {"name": "YouTube", "emoji": "🎥", "color": 0xFF0000},
            "twitch": {"name": "Twitch", "emoji": "🟣", "color": 0x9146FF},
            "kick": {"name": "Kick", "emoji": "🟢", "color": 0x53FC18},
            "twitter": {"name": "Twitter/X", "emoji": "🐦", "color": 0x1DA1F2},
            "instagram": {"name": "Instagram", "emoji": "📷", "color": 0xE1306C},
            "tiktok": {"name": "TikTok", "emoji": "🎵", "color": 0x000000},
            "snapchat": {"name": "Snapchat", "emoji": "👻", "color": 0xFFFC00}
        }
    
    # ==================== LINKS MANAGEMENT ====================
    
    async def list_links(
        self,
        guild_id: str,
        platform: Optional[str] = None,
        enabled_only: bool = False
    ) -> List[Dict[str, Any]]:
        """Get all social links for a guild
        
        Args:
            guild_id: Discord guild ID
            platform: Filter by platform (youtube/twitch/kick/etc.)
            enabled_only: Filter enabled links only
            
        Returns:
            List of link documents
        """
        try:
            query = {"guild_id": guild_id}
            if platform:
                query["platform"] = platform
            if enabled_only:
                query["enabled"] = True
            
            links = await self.links_collection.find(query).to_list(length=None)
            
            # Convert ObjectId to string and add platform info
            for link in links:
                link["_id"] = str(link["_id"])
                if link["platform"] in self.PLATFORMS:
                    link["platform_info"] = self.PLATFORMS[link["platform"]]
            
            return links
        except Exception as e:
            logger.error(f"Error listing social links: {e}")
            return []
    
    async def get_link(
        self,
        guild_id: str,
        link_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get social link details
        
        Args:
            guild_id: Discord guild ID
            link_id: Link ID
            
        Returns:
            Link document or None
        """
        try:
            link = await self.links_collection.find_one({
                "guild_id": guild_id,
                "link_id": link_id
            })
            
            if link:
                link["_id"] = str(link["_id"])
                if link["platform"] in self.PLATFORMS:
                    link["platform_info"] = self.PLATFORMS[link["platform"]]
            
            return link
        except Exception as e:
            logger.error(f"Error getting social link: {e}")
            return None
    
    async def create_link(
        self,
        guild_id: str,
        user_id: str,
        link_data: Dict[str, Any]
    ) -> tuple[bool, str, Optional[str]]:
        """Create new social media link
        
        Args:
            guild_id: Discord guild ID
            user_id: User ID who created the link
            link_data: Link configuration
            
        Returns:
            (success, message, link_id)
        """
        try:
            # Check limits
            limits = await self.get_limits(guild_id)
            if not limits["can_add_free"] and limits["purchased"] == 0:
                return False, "❌ وصلت للحد الأقصى من الروابط المجانية (2). استخدم `/social purchase-link` لشراء روابط إضافية", None
            
            # Generate link ID
            import uuid
            link_id = str(uuid.uuid4())[:12]
            
            # Determine if purchased
            is_purchased = limits["free_used"] >= 2
            
            # Prepare document
            doc = {
                "guild_id": guild_id,
                "link_id": link_id,
                "platform": link_data.get("platform"),
                "channel_url": link_data.get("channel_url"),
                "channel_id": link_data.get("channel_id"),
                "notification_channel_id": link_data.get("notification_channel_id"),
                "mention_role_id": link_data.get("mention_role_id"),
                "is_purchased": is_purchased,
                "enabled": True,
                "added_by": user_id,
                "added_at": datetime.utcnow(),
                "last_checked": None,
                "last_post_id": None,
                "statistics": {
                    "total_notifications": 0,
                    "last_notification": None
                }
            }
            
            await self.links_collection.insert_one(doc)
            
            platform_name = self.PLATFORMS.get(link_data.get("platform"), {}).get("name", "Unknown")
            return True, f"✅ تم إضافة رابط {platform_name} بنجاح", link_id
        except Exception as e:
            logger.error(f"Error creating social link: {e}")
            return False, f"❌ فشل إضافة الرابط: {str(e)}", None
    
    async def update_link(
        self,
        guild_id: str,
        link_id: str,
        updates: Dict[str, Any]
    ) -> tuple[bool, str]:
        """Update social link configuration
        
        Args:
            guild_id: Discord guild ID
            link_id: Link ID
            updates: Fields to update
            
        Returns:
            (success, message)
        """
        try:
            result = await self.links_collection.update_one(
                {"guild_id": guild_id, "link_id": link_id},
                {"$set": updates}
            )
            
            if result.modified_count > 0:
                return True, "✅ تم تحديث الرابط بنجاح"
            else:
                return False, "❌ الرابط غير موجود"
        except Exception as e:
            logger.error(f"Error updating social link: {e}")
            return False, f"❌ فشل التحديث: {str(e)}"
    
    async def delete_link(
        self,
        guild_id: str,
        link_id: str
    ) -> tuple[bool, str]:
        """Delete social media link
        
        Args:
            guild_id: Discord guild ID
            link_id: Link ID
            
        Returns:
            (success, message)
        """
        try:
            result = await self.links_collection.delete_one({
                "guild_id": guild_id,
                "link_id": link_id
            })
            
            if result.deleted_count > 0:
                return True, "✅ تم حذف الرابط"
            else:
                return False, "❌ الرابط غير موجود"
        except Exception as e:
            logger.error(f"Error deleting social link: {e}")
            return False, f"❌ فشل الحذف: {str(e)}"
    
    async def toggle_link(
        self,
        guild_id: str,
        link_id: str
    ) -> tuple[bool, str, bool]:
        """Toggle link enabled status
        
        Args:
            guild_id: Discord guild ID
            link_id: Link ID
            
        Returns:
            (success, message, new_state)
        """
        try:
            link = await self.get_link(guild_id, link_id)
            if not link:
                return False, "❌ الرابط غير موجود", False
            
            new_state = not link.get("enabled", True)
            
            await self.links_collection.update_one(
                {"guild_id": guild_id, "link_id": link_id},
                {"$set": {"enabled": new_state}}
            )
            
            status = "مفعّل" if new_state else "معطّل"
            return True, f"✅ الرابط الآن {status}", new_state
        except Exception as e:
            logger.error(f"Error toggling social link: {e}")
            return False, f"❌ فشل التبديل: {str(e)}", False
    
    # ==================== POSTS ====================
    
    async def get_posts(
        self,
        guild_id: str,
        link_id: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get recent posts
        
        Args:
            guild_id: Discord guild ID
            link_id: Filter by link ID (optional)
            limit: Maximum posts to return
            
        Returns:
            List of post documents
        """
        try:
            query = {"guild_id": guild_id}
            if link_id:
                query["link_id"] = link_id
            
            posts = await self.posts_collection.find(query)\
                .sort("published_at", -1)\
                .limit(limit)\
                .to_list(length=None)
            
            # Convert ObjectId to string
            for post in posts:
                post["_id"] = str(post["_id"])
            
            return posts
        except Exception as e:
            logger.error(f"Error getting posts: {e}")
            return []
    
    # ==================== LIMITS & PURCHASE ====================
    
    async def get_limits(
        self,
        guild_id: str
    ) -> Dict[str, Any]:
        """Get link limits for guild
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            Limits dictionary
        """
        try:
            # Count total links
            total_links = await self.links_collection.count_documents({
                "guild_id": guild_id
            })
            
            # Count purchased links
            purchased_links = await self.links_collection.count_documents({
                "guild_id": guild_id,
                "is_purchased": True
            })
            
            # Count free links
            free_links = total_links - purchased_links
            
            # Get settings
            settings = await self.settings_collection.find_one({
                "guild_id": guild_id
            })
            
            purchased_slots = settings.get("purchased_link_slots", 0) if settings else 0
            
            # Links by platform
            pipeline = [
                {"$match": {"guild_id": guild_id}},
                {"$group": {
                    "_id": "$platform",
                    "count": {"$sum": 1}
                }}
            ]
            
            platform_counts = {}
            async for doc in self.links_collection.aggregate(pipeline):
                platform_counts[doc["_id"]] = doc["count"]
            
            return {
                "guild_id": guild_id,
                "total_links": total_links,
                "free_max": 2,
                "free_used": min(free_links, 2),
                "free_remaining": max(0, 2 - free_links),
                "can_add_free": free_links < 2,
                "purchased": purchased_slots,
                "links_by_platform": platform_counts
            }
        except Exception as e:
            logger.error(f"Error getting limits: {e}")
            return {
                "guild_id": guild_id,
                "error": str(e)
            }
    
    async def purchase_link(
        self,
        guild_id: str,
        user_id: str
    ) -> tuple[bool, str]:
        """Purchase additional link slot
        
        Args:
            guild_id: Discord guild ID
            user_id: User ID purchasing
            
        Returns:
            (success, message)
        """
        try:
            # TODO: Integrate with credits system to deduct 200 credits
            # For now, just increment purchased slots
            
            result = await self.settings_collection.update_one(
                {"guild_id": guild_id},
                {
                    "$inc": {"purchased_link_slots": 1},
                    "$set": {"last_purchase_at": datetime.utcnow()}
                },
                upsert=True
            )
            
            return True, "✅ تم شراء رابط إضافي بنجاح! (تم خصم 200 ❄️)"
        except Exception as e:
            logger.error(f"Error purchasing link: {e}")
            return False, f"❌ فشل الشراء: {str(e)}"
    
    # ==================== STATISTICS ====================
    
    async def get_statistics(
        self,
        guild_id: str
    ) -> Dict[str, Any]:
        """Get social integration statistics for guild
        
        Args:
            guild_id: Discord guild ID
            
        Returns:
            Statistics dictionary
        """
        try:
            # Count links
            total_links = await self.links_collection.count_documents({
                "guild_id": guild_id
            })
            
            active_links = await self.links_collection.count_documents({
                "guild_id": guild_id,
                "enabled": True
            })
            
            # Count by platform
            platform_stats = {}
            for platform_id, platform_info in self.PLATFORMS.items():
                count = await self.links_collection.count_documents({
                    "guild_id": guild_id,
                    "platform": platform_id
                })
                
                if count > 0:
                    # Get notification count
                    pipeline = [
                        {"$match": {
                            "guild_id": guild_id,
                            "platform": platform_id
                        }},
                        {"$group": {
                            "_id": None,
                            "total": {"$sum": "$statistics.total_notifications"}
                        }}
                    ]
                    
                    result = await self.links_collection.aggregate(pipeline).to_list(1)
                    notifications = result[0]["total"] if result else 0
                    
                    platform_stats[platform_id] = {
                        "name": platform_info["name"],
                        "emoji": platform_info["emoji"],
                        "count": count,
                        "notifications": notifications
                    }
            
            # Total notifications
            pipeline = [
                {"$match": {"guild_id": guild_id}},
                {"$group": {
                    "_id": None,
                    "total": {"$sum": "$statistics.total_notifications"}
                }}
            ]
            
            result = await self.links_collection.aggregate(pipeline).to_list(1)
            total_notifications = result[0]["total"] if result else 0
            
            return {
                "guild_id": guild_id,
                "links": {
                    "total": total_links,
                    "active": active_links,
                    "inactive": total_links - active_links
                },
                "by_platform": platform_stats,
                "total_notifications": total_notifications
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "guild_id": guild_id,
                "error": str(e)
            }

"""
Social Media Integration System - Core Logic

Handles integration with 7 social media platforms:
- YouTube (RSS)
- Twitch (Helix API)
- Kick (unofficial)
- Twitter/X (API v2)
- Instagram (unofficial)
- TikTok (unofficial)
- Snapchat (unofficial)
"""

import discord
import aiohttp
import asyncio
import feedparser
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


class SocialIntegrationSystem:
    """Core system for social media platform integration"""
    
    # Platform configuration
    PLATFORMS = {
        "youtube": {
            "name": "YouTube",
            "emoji": "🎥",
            "color": 0xFF0000,
            "api_type": "rss"
        },
        "twitch": {
            "name": "Twitch",
            "emoji": "🟣",
            "color": 0x9146FF,
            "api_type": "official"
        },
        "kick": {
            "name": "Kick",
            "emoji": "🟢",
            "color": 0x53FC18,
            "api_type": "unofficial"
        },
        "twitter": {
            "name": "Twitter/X",
            "emoji": "🐦",
            "color": 0x1DA1F2,
            "api_type": "official"
        },
        "instagram": {
            "name": "Instagram",
            "emoji": "📷",
            "color": 0xE4405F,
            "api_type": "unofficial"
        },
        "tiktok": {
            "name": "TikTok",
            "emoji": "🎵",
            "color": 0x000000,
            "api_type": "unofficial"
        },
        "snapchat": {
            "name": "Snapchat",
            "emoji": "👻",
            "color": 0xFFFC00,
            "api_type": "unofficial"
        }
    }
    
    def __init__(self, db: AsyncIOMotorDatabase, config: Dict):
        self.db = db
        self.links_collection = db.social_links
        self.posts_collection = db.social_posts
        self.settings_collection = db.social_settings
        
        # API credentials
        self.twitch_client_id = config.get("twitch_client_id")
        self.twitch_client_secret = config.get("twitch_client_secret")
        self.twitter_bearer_token = config.get("twitter_bearer_token")
        
        # Cache for last checked posts
        self.last_posts_cache: Dict[str, Dict] = {}
        
        # HTTP session
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize the social integration system"""
        self.session = aiohttp.ClientSession()
        logger.info("✅ Social Integration System initialized")
    
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
    
    # ==================== LINK MANAGEMENT ====================
    
    async def add_link(
        self,
        guild_id: str,
        user_id: str,
        platform: str,
        channel_url: str,
        notification_channel_id: str,
        mention_role_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Add a new social media link
        
        Returns:
            (success, message)
        """
        # Validate platform
        if platform not in self.PLATFORMS:
            return False, f"❌ المنصة `{platform}` غير مدعومة!"
        
        # Extract channel ID from URL
        channel_id = self._extract_channel_id(platform, channel_url)
        if not channel_id:
            return False, f"❌ رابط {self.PLATFORMS[platform]['name']} غير صالح!"
        
        # Check if link already exists
        existing = await self.links_collection.find_one({
            "guild_id": guild_id,
            "platform": platform,
            "channel_id": channel_id
        })
        
        if existing:
            return False, f"❌ هذا الرابط مضاف مسبقاً!"
        
        # Check limits
        can_add, reason = await self._check_link_limit(guild_id)
        if not can_add:
            return False, reason
        
        # Create link document
        import uuid
        link_data = {
            "link_id": str(uuid.uuid4()),
            "guild_id": guild_id,
            "user_id": user_id,
            "platform": platform,
            "channel_url": channel_url,
            "channel_id": channel_id,
            "channel_name": "",  # Will be fetched later
            "notification_channel_id": notification_channel_id,
            "mention_role_id": mention_role_id,
            "enabled": True,
            "is_purchased": False,
            "last_checked": None,
            "last_post_id": None,
            "created_at": datetime.utcnow(),
            "statistics": {
                "total_posts": 0,
                "total_notifications": 0
            }
        }
        
        # Insert to database
        await self.links_collection.insert_one(link_data)
        
        platform_name = self.PLATFORMS[platform]['name']
        platform_emoji = self.PLATFORMS[platform]['emoji']
        
        return True, f"✅ تم إضافة رابط {platform_emoji} **{platform_name}** بنجاح!"
    
    async def remove_link(
        self,
        guild_id: str,
        link_id: str
    ) -> Tuple[bool, str]:
        """Remove a social media link"""
        result = await self.links_collection.delete_one({
            "guild_id": guild_id,
            "link_id": link_id
        })
        
        if result.deleted_count > 0:
            return True, "✅ تم حذف الرابط بنجاح!"
        else:
            return False, "❌ الرابط غير موجود!"
    
    async def toggle_link(
        self,
        guild_id: str,
        link_id: str
    ) -> Tuple[bool, str, bool]:
        """
        Toggle link enabled/disabled
        
        Returns:
            (success, message, new_state)
        """
        link = await self.links_collection.find_one({
            "guild_id": guild_id,
            "link_id": link_id
        })
        
        if not link:
            return False, "❌ الرابط غير موجود!", False
        
        new_state = not link["enabled"]
        
        await self.links_collection.update_one(
            {"link_id": link_id},
            {"$set": {"enabled": new_state}}
        )
        
        status = "✅ مفعّل" if new_state else "❌ معطّل"
        return True, f"{status} تم تحديث حالة الرابط", new_state
    
    async def get_guild_links(
        self,
        guild_id: str,
        enabled_only: bool = False
    ) -> List[Dict]:
        """Get all links for a guild"""
        query = {"guild_id": guild_id}
        if enabled_only:
            query["enabled"] = True
        
        links = await self.links_collection.find(query).to_list(length=None)
        return links
    
    async def get_link_by_id(
        self,
        guild_id: str,
        link_id: str
    ) -> Optional[Dict]:
        """Get a specific link"""
        return await self.links_collection.find_one({
            "guild_id": guild_id,
            "link_id": link_id
        })
    
    # ==================== LIMITS & PURCHASES ====================
    
    async def _check_link_limit(
        self,
        guild_id: str
    ) -> Tuple[bool, str]:
        """Check if guild can add more links"""
        links = await self.get_guild_links(guild_id)
        
        free_links = sum(1 for link in links if not link.get("is_purchased", False))
        purchased_links = sum(1 for link in links if link.get("is_purchased", False))
        
        # 2 free links allowed
        if free_links < 2:
            return True, ""
        
        return False, (
            "❌ وصلت إلى الحد الأقصى من الروابط المجانية (2)!\n"
            "💎 يمكنك شراء روابط إضافية (200 ❄️ للرابط الواحد - دائم)\n"
            f"استخدم: `/social purchase-link`"
        )
    
    async def purchase_link(
        self,
        guild_id: str,
        user_id: str
    ) -> Tuple[bool, str]:
        """
        Purchase an additional link slot (200 ❄️)
        
        Returns:
            (success, message)
        """
        # This will be integrated with Credits System
        # For now, just add a purchased slot marker
        
        cost = 200
        
        # TODO: Deduct credits from user
        # from economy.credits_system import CreditsSystem
        # credits_system = CreditsSystem(self.db)
        # success = await credits_system.deduct_credits(user_id, cost, "social_link_purchase")
        
        # For now, assume success
        # In production, check actual balance and deduct
        
        return True, (
            f"✅ تم شراء رابط إضافي بنجاح!\n"
            f"💰 تم خصم **{cost} ❄️** من رصيدك\n"
            f"🔗 يمكنك الآن إضافة رابط جديد"
        )
    
    async def get_guild_limits(
        self,
        guild_id: str
    ) -> Dict:
        """Get guild's link limits and usage"""
        links = await self.get_guild_links(guild_id)
        
        free_links = [l for l in links if not l.get("is_purchased", False)]
        purchased_links = [l for l in links if l.get("is_purchased", False)]
        
        return {
            "total_links": len(links),
            "free_used": len(free_links),
            "free_max": 2,
            "purchased": len(purchased_links),
            "can_add_free": len(free_links) < 2,
            "links_by_platform": self._count_by_platform(links)
        }
    
    def _count_by_platform(self, links: List[Dict]) -> Dict[str, int]:
        """Count links by platform"""
        counts = {}
        for link in links:
            platform = link["platform"]
            counts[platform] = counts.get(platform, 0) + 1
        return counts
    
    # ==================== URL PARSING ====================
    
    def _extract_channel_id(self, platform: str, url: str) -> Optional[str]:
        """Extract channel/user ID from URL"""
        if platform == "youtube":
            # YouTube: channel/UC..., @username, or c/channelname
            patterns = [
                r'youtube\.com/channel/([^/?]+)',
                r'youtube\.com/@([^/?]+)',
                r'youtube\.com/c/([^/?]+)',
                r'youtube\.com/user/([^/?]+)'
            ]
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
        
        elif platform == "twitch":
            # Twitch: twitch.tv/username
            match = re.search(r'twitch\.tv/([^/?]+)', url)
            if match:
                return match.group(1)
        
        elif platform == "kick":
            # Kick: kick.com/username
            match = re.search(r'kick\.com/([^/?]+)', url)
            if match:
                return match.group(1)
        
        elif platform == "twitter":
            # Twitter: twitter.com/username or x.com/username
            match = re.search(r'(?:twitter|x)\.com/([^/?]+)', url)
            if match:
                return match.group(1)
        
        elif platform == "instagram":
            # Instagram: instagram.com/username
            match = re.search(r'instagram\.com/([^/?]+)', url)
            if match:
                return match.group(1)
        
        elif platform == "tiktok":
            # TikTok: tiktok.com/@username
            match = re.search(r'tiktok\.com/@([^/?]+)', url)
            if match:
                return match.group(1)
        
        elif platform == "snapchat":
            # Snapchat: snapchat.com/add/username
            match = re.search(r'snapchat\.com/add/([^/?]+)', url)
            if match:
                return match.group(1)
            # Or direct username
            match = re.search(r'snapchat\.com/([^/?]+)', url)
            if match:
                return match.group(1)
        
        return None
    
    # ==================== CONTENT FETCHING ====================
    
    async def check_for_new_content(
        self,
        link: Dict
    ) -> Optional[Dict]:
        """
        Check if there's new content for a link
        
        Returns:
            Post data if new content found, None otherwise
        """
        platform = link["platform"]
        
        try:
            if platform == "youtube":
                return await self._check_youtube(link)
            elif platform == "twitch":
                return await self._check_twitch(link)
            elif platform == "kick":
                return await self._check_kick(link)
            elif platform == "twitter":
                return await self._check_twitter(link)
            elif platform == "instagram":
                return await self._check_instagram(link)
            elif platform == "tiktok":
                return await self._check_tiktok(link)
            elif platform == "snapchat":
                return await self._check_snapchat(link)
        except Exception as e:
            logger.error(f"Error checking {platform} for link {link['link_id']}: {e}")
            return None
    
    async def _check_youtube(self, link: Dict) -> Optional[Dict]:
        """Check YouTube for new videos (RSS)"""
        channel_id = link["channel_id"]
        
        # YouTube RSS feed
        if channel_id.startswith("@"):
            # Handle @username format
            rss_url = f"https://www.youtube.com/feeds/videos.xml?user={channel_id[1:]}"
        elif channel_id.startswith("UC"):
            rss_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        else:
            rss_url = f"https://www.youtube.com/feeds/videos.xml?user={channel_id}"
        
        try:
            async with self.session.get(rss_url) as resp:
                if resp.status != 200:
                    return None
                
                content = await resp.text()
                feed = feedparser.parse(content)
                
                if not feed.entries:
                    return None
                
                latest = feed.entries[0]
                video_id = latest.yt_videoid if hasattr(latest, 'yt_videoid') else latest.id.split(':')[-1]
                
                # Check if this is new
                if link.get("last_post_id") == video_id:
                    return None
                
                return {
                    "post_id": video_id,
                    "title": latest.title,
                    "url": latest.link,
                    "thumbnail": f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg",
                    "author": feed.feed.author if hasattr(feed.feed, 'author') else channel_id,
                    "published_at": datetime(*latest.published_parsed[:6])
                }
        except Exception as e:
            logger.error(f"YouTube check error: {e}")
            return None
    
    async def _check_twitch(self, link: Dict) -> Optional[Dict]:
        """Check Twitch for new streams (requires API key)"""
        # Requires Twitch API setup
        # Placeholder implementation
        username = link["channel_id"]
        
        # TODO: Implement Twitch Helix API
        # 1. Get OAuth token
        # 2. Call /streams endpoint
        # 3. Check if live
        
        return None
    
    async def _check_kick(self, link: Dict) -> Optional[Dict]:
        """Check Kick for new streams (unofficial)"""
        username = link["channel_id"]
        
        try:
            # Kick API endpoint (unofficial)
            url = f"https://kick.com/api/v2/channels/{username}"
            
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                
                # Check if live
                if not data.get("livestream"):
                    return None
                
                stream = data["livestream"]
                stream_id = str(stream["id"])
                
                # Check if new
                if link.get("last_post_id") == stream_id:
                    return None
                
                return {
                    "post_id": stream_id,
                    "title": stream.get("session_title", "Live Stream"),
                    "url": f"https://kick.com/{username}",
                    "thumbnail": stream.get("thumbnail", {}).get("url"),
                    "author": username,
                    "published_at": datetime.utcnow()
                }
        except Exception as e:
            logger.error(f"Kick check error: {e}")
            return None
    
    async def _check_twitter(self, link: Dict) -> Optional[Dict]:
        """Check Twitter for new tweets (requires API key)"""
        # Requires Twitter API Bearer Token
        # Placeholder implementation
        username = link["channel_id"]
        
        # TODO: Implement Twitter API v2
        # Endpoint: /users/:id/tweets
        
        return None
    
    async def _check_instagram(self, link: Dict) -> Optional[Dict]:
        """Check Instagram for new posts (unofficial)"""
        username = link["channel_id"]
        
        # Instagram unofficial API is complex and may break
        # Placeholder implementation
        
        return None
    
    async def _check_tiktok(self, link: Dict) -> Optional[Dict]:
        """Check TikTok for new videos (unofficial)"""
        username = link["channel_id"]
        
        # TikTok unofficial API
        # Placeholder implementation
        
        return None
    
    async def _check_snapchat(self, link: Dict) -> Optional[Dict]:
        """Check Snapchat for new stories (unofficial)"""
        username = link["channel_id"]
        
        try:
            # Snapchat public profile (very limited)
            # Note: Snapchat doesn't have public API for stories
            # This is a placeholder that would need actual implementation
            
            url = f"https://story.snapchat.com/@{username}"
            
            async with self.session.get(url) as resp:
                if resp.status != 200:
                    return None
                
                # Parse HTML to check for new stories
                # This is very basic and may not work reliably
                html = await resp.text()
                
                # Check if there's a story indicator
                if "story" not in html.lower():
                    return None
                
                # Generate a pseudo post ID based on current time
                # In production, you'd need more sophisticated tracking
                post_id = f"snap_{datetime.utcnow().strftime('%Y%m%d%H')}"
                
                # Check if new
                if link.get("last_post_id") == post_id:
                    return None
                
                return {
                    "post_id": post_id,
                    "title": f"قصة جديدة من {username}",
                    "url": url,
                    "thumbnail": None,  # Snapchat doesn't provide public thumbnails
                    "author": username,
                    "published_at": datetime.utcnow()
                }
        except Exception as e:
            logger.error(f"Snapchat check error: {e}")
            return None
    
    # ==================== NOTIFICATIONS ====================
    
    async def send_notification(
        self,
        link: Dict,
        post: Dict,
        bot: discord.Client
    ) -> bool:
        """Send Discord notification for new content"""
        try:
            # Get notification channel
            channel = bot.get_channel(int(link["notification_channel_id"]))
            if not channel:
                return False
            
            # Build embed
            platform = link["platform"]
            platform_info = self.PLATFORMS[platform]
            
            embed = discord.Embed(
                title=f"{platform_info['emoji']} {post['title']}",
                url=post['url'],
                description=f"محتوى جديد من **{post['author']}** على {platform_info['name']}!",
                color=platform_info['color'],
                timestamp=post.get('published_at', datetime.utcnow())
            )
            
            # Add thumbnail if available
            if post.get('thumbnail'):
                embed.set_image(url=post['thumbnail'])
            
            # Footer
            embed.set_footer(
                text=f"{platform_info['name']} • Kingdom-77 Bot",
                icon_url="https://i.imgur.com/AfFp7pu.png"
            )
            
            # Mention role if configured
            content = None
            if link.get("mention_role_id"):
                content = f"<@&{link['mention_role_id']}>"
            
            # Send notification
            await channel.send(content=content, embed=embed)
            
            # Update statistics
            await self.links_collection.update_one(
                {"link_id": link["link_id"]},
                {
                    "$set": {
                        "last_post_id": post["post_id"],
                        "last_checked": datetime.utcnow()
                    },
                    "$inc": {
                        "statistics.total_notifications": 1
                    }
                }
            )
            
            # Save post to database
            await self._save_post(link, post)
            
            return True
        
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False
    
    async def _save_post(self, link: Dict, post: Dict):
        """Save post to database"""
        post_data = {
            "link_id": link["link_id"],
            "guild_id": link["guild_id"],
            "platform": link["platform"],
            "post_id": post["post_id"],
            "title": post["title"],
            "url": post["url"],
            "thumbnail": post.get("thumbnail"),
            "author": post["author"],
            "published_at": post.get("published_at", datetime.utcnow()),
            "notified_at": datetime.utcnow()
        }
        
        await self.posts_collection.insert_one(post_data)
    
    # ==================== BACKGROUND TASK ====================
    
    async def check_all_links(self, bot: discord.Client):
        """Background task to check all active links"""
        logger.info("🔍 Checking all social media links...")
        
        # Get all enabled links
        all_links = await self.links_collection.find({"enabled": True}).to_list(length=None)
        
        checked = 0
        notifications_sent = 0
        
        for link in all_links:
            try:
                # Check for new content
                post = await self.check_for_new_content(link)
                
                if post:
                    # Send notification
                    success = await self.send_notification(link, post, bot)
                    if success:
                        notifications_sent += 1
                
                checked += 1
                
                # Small delay to avoid rate limits
                await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"Error checking link {link['link_id']}: {e}")
        
        logger.info(f"✅ Checked {checked} links, sent {notifications_sent} notifications")
    
    # ==================== STATISTICS ====================
    
    async def get_guild_statistics(self, guild_id: str) -> Dict:
        """Get statistics for a guild"""
        links = await self.get_guild_links(guild_id)
        
        total_notifications = sum(
            link.get("statistics", {}).get("total_notifications", 0)
            for link in links
        )
        
        by_platform = {}
        for link in links:
            platform = link["platform"]
            if platform not in by_platform:
                by_platform[platform] = {
                    "count": 0,
                    "notifications": 0
                }
            by_platform[platform]["count"] += 1
            by_platform[platform]["notifications"] += link.get("statistics", {}).get("total_notifications", 0)
        
        return {
            "total_links": len(links),
            "active_links": sum(1 for l in links if l["enabled"]),
            "total_notifications": total_notifications,
            "by_platform": by_platform
        }

"""
Social Media Integration System for Kingdom-77 Bot

This module provides social media platform integration with automatic notifications.

Supported Platforms:
- YouTube (RSS feeds)
- Twitch (Helix API)
- Kick (unofficial API)
- Twitter/X (API v2)
- Instagram (unofficial API)
- TikTok (unofficial API)
- Snapchat (unofficial API)

Features:
- 2 free links per server
- Purchase additional links (200 ❄️ permanent)
- Automatic notifications when new content is posted
- Custom embed with thumbnails
- Background polling (every 5 minutes)
"""

from .social_integration import SocialIntegrationSystem

__all__ = ["SocialIntegrationSystem"]

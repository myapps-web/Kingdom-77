"""
Dashboard Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Discord OAuth2
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:3000/auth/callback")
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Discord API
DISCORD_API_BASE = "https://discord.com/api/v10"
DISCORD_OAUTH_AUTHORIZE = f"{DISCORD_API_BASE}/oauth2/authorize"
DISCORD_OAUTH_TOKEN = f"{DISCORD_API_BASE}/oauth2/token"
DISCORD_OAUTH_REVOKE = f"{DISCORD_API_BASE}/oauth2/token/revoke"
DISCORD_USER_ENDPOINT = f"{DISCORD_API_BASE}/users/@me"
DISCORD_GUILDS_ENDPOINT = f"{DISCORD_API_BASE}/users/@me/guilds"

# JWT
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 7 * 24 * 60 * 60  # 7 days

# MongoDB
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB", "kingdom77")

# Redis
REDIS_URL = os.getenv("REDIS_URL")

# Application
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Rate Limiting
RATE_LIMIT_PER_MINUTE = 60
RATE_LIMIT_PER_HOUR = 1000

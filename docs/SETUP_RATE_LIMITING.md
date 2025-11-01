# 🚦 API Rate Limiting Configuration Guide

**Complete guide to implement rate limiting for Kingdom-77 Bot v4.0**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Rate Limit Strategy](#rate-limit-strategy)
3. [Implementation](#implementation)
4. [Tier Configuration](#tier-configuration)
5. [Headers & Responses](#headers--responses)
6. [Testing](#testing)
7. [Monitoring](#monitoring)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**Rate Limiting Goals:**
- Prevent API abuse
- Ensure fair usage
- Protect server resources
- Encourage premium upgrades

**Implementation Method:**
- Token bucket algorithm
- Redis-based counters
- Per-user tracking
- Sliding window

**Tiers:**
- **Free:** 60 requests/minute
- **Basic:** 120 requests/minute
- **Premium:** 300 requests/minute

---

## 1️⃣ Rate Limit Strategy

### Token Bucket Algorithm

```
User starts with N tokens (rate limit)
Each request consumes 1 token
Tokens refill at rate R per minute
If no tokens available → 429 Too Many Requests
```

**Example: Free Tier (60 req/min)**
```
Tokens: 60
Request 1: 60 → 59 ✅
Request 2: 59 → 58 ✅
...
Request 61: 0 → -1 ❌ (Rate limited)
After 1 minute: Tokens reset to 60
```

### Window Strategies

**Fixed Window:**
```
00:00-01:00 → 60 requests allowed
01:00-02:00 → Reset, 60 requests allowed
```

**Sliding Window (BETTER):**
```
Each minute is independent
Requests older than 60s don't count
More fair distribution
```

---

## 2️⃣ Implementation

### File Structure

```
Kingdom-77/
├── api/
│   ├── __init__.py
│   ├── rate_limiter.py    # Rate limiting logic
│   └── middleware.py      # FastAPI middleware
├── cache/
│   └── __init__.py        # Redis client
└── .env                   # Rate limit config
```

### rate_limiter.py

```python
"""
API Rate Limiter for Kingdom-77 Bot v4.0
Uses Redis for distributed rate limiting
"""
import time
from typing import Tuple, Optional
from enum import Enum
import redis
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse

class RateLimitTier(Enum):
    """Rate limit tiers"""
    FREE = 60       # 60 req/min
    BASIC = 120     # 120 req/min
    PREMIUM = 300   # 300 req/min
    ADMIN = 1000    # 1000 req/min (for testing)

class RateLimiter:
    """
    Token bucket rate limiter using Redis
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.window = 60  # 60 seconds
    
    def get_rate_limit(self, tier: str) -> int:
        """Get rate limit for tier"""
        tier_map = {
            "free": RateLimitTier.FREE.value,
            "basic": RateLimitTier.BASIC.value,
            "premium": RateLimitTier.PREMIUM.value,
            "admin": RateLimitTier.ADMIN.value
        }
        return tier_map.get(tier.lower(), RateLimitTier.FREE.value)
    
    def check_rate_limit(
        self,
        identifier: str,
        tier: str = "free",
        endpoint: Optional[str] = None
    ) -> Tuple[bool, int, int, int]:
        """
        Check if request is within rate limit
        
        Args:
            identifier: User ID, IP address, or API key
            tier: Rate limit tier (free/basic/premium)
            endpoint: Optional endpoint for per-endpoint limits
        
        Returns:
            (allowed, remaining, limit, reset_time)
        """
        limit = self.get_rate_limit(tier)
        current_time = int(time.time())
        window_start = current_time - self.window
        
        # Redis key
        key = f"ratelimit:{identifier}"
        if endpoint:
            key += f":{endpoint}"
        
        # Use sorted set for sliding window
        try:
            # Remove old entries
            self.redis.zremrangebyscore(key, 0, window_start)
            
            # Count requests in current window
            current_count = self.redis.zcard(key)
            
            if current_count >= limit:
                # Rate limit exceeded
                oldest = self.redis.zrange(key, 0, 0, withscores=True)
                reset_time = int(oldest[0][1]) + self.window if oldest else self.window
                remaining_time = reset_time - current_time
                
                return False, 0, limit, remaining_time
            
            # Add current request
            self.redis.zadd(key, {f"{current_time}:{id(self)}": current_time})
            self.redis.expire(key, self.window)
            
            remaining = limit - current_count - 1
            return True, remaining, limit, self.window
            
        except Exception as e:
            print(f"❌ Rate limiter error: {e}")
            # On error, allow request (fail open)
            return True, limit, limit, self.window
    
    def reset_limit(self, identifier: str, endpoint: Optional[str] = None):
        """Reset rate limit for user (admin only)"""
        key = f"ratelimit:{identifier}"
        if endpoint:
            key += f":{endpoint}"
        self.redis.delete(key)
    
    def get_usage(self, identifier: str) -> dict:
        """Get current usage stats"""
        key = f"ratelimit:{identifier}"
        current_time = int(time.time())
        window_start = current_time - self.window
        
        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Get count
        count = self.redis.zcard(key)
        
        return {
            "requests": count,
            "window": self.window,
            "timestamp": current_time
        }

# Global rate limiter instance
from cache import cache
rate_limiter = RateLimiter(cache.client)
```

### middleware.py

```python
"""
FastAPI Middleware for Rate Limiting
"""
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from api.rate_limiter import rate_limiter
import time

async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware
    Applied to all API endpoints
    """
    
    # Skip rate limiting for health check
    if request.url.path in ["/health", "/api/docs", "/api/redoc"]:
        return await call_next(request)
    
    # Get user identifier
    user_id = request.state.user_id if hasattr(request.state, "user_id") else None
    ip_address = request.client.host
    identifier = user_id or ip_address
    
    # Get user tier
    tier = request.state.tier if hasattr(request.state, "tier") else "free"
    
    # Get endpoint
    endpoint = request.url.path
    
    # Check rate limit
    allowed, remaining, limit, reset = rate_limiter.check_rate_limit(
        identifier=identifier,
        tier=tier,
        endpoint=None  # Global limit (set to endpoint for per-endpoint)
    )
    
    if not allowed:
        # Rate limit exceeded
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": f"You have exceeded the rate limit of {limit} requests per minute",
                "limit": limit,
                "remaining": 0,
                "reset": reset,
                "tier": tier,
                "upgrade_url": "https://kingdom77.com/premium"
            },
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + reset),
                "Retry-After": str(reset),
                "X-RateLimit-Tier": tier
            }
        )
    
    # Process request
    response = await call_next(request)
    
    # Add rate limit headers
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + reset)
    response.headers["X-RateLimit-Tier"] = tier
    
    return response
```

### dashboard/main.py Integration

```python
"""
Add rate limiting to FastAPI app
"""
from fastapi import FastAPI
from api.middleware import rate_limit_middleware

app = FastAPI(
    title="Kingdom-77 Dashboard API",
    version="4.0.0"
)

# Add rate limiting middleware
@app.middleware("http")
async def add_rate_limiting(request: Request, call_next):
    return await rate_limit_middleware(request, call_next)

# Your existing routes...
```

---

## 3️⃣ Tier Configuration

### Environment Variables

```bash
# .env file
RATE_LIMIT_FREE=60
RATE_LIMIT_BASIC=120
RATE_LIMIT_PREMIUM=300
RATE_LIMIT_ADMIN=1000

# Ban duration for abuse (in seconds)
RATE_LIMIT_BAN_DURATION=3600  # 1 hour

# Burst allowance (optional)
RATE_LIMIT_BURST=10  # Allow 10 extra requests in burst
```

### Database: User Tiers

```python
# Get user tier from database
async def get_user_tier(user_id: str) -> str:
    """Get user's premium tier"""
    user = await db.users.find_one({"user_id": user_id})
    
    if not user:
        return "free"
    
    premium_data = user.get("premium", {})
    
    if premium_data.get("admin"):
        return "admin"
    elif premium_data.get("tier") == "premium":
        return "premium"
    elif premium_data.get("tier") == "basic":
        return "basic"
    else:
        return "free"
```

---

## 4️⃣ Headers & Responses

### Response Headers

**All Requests:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1698768000
X-RateLimit-Tier: free
```

**Rate Limited (429):**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1698768000
Retry-After: 30
X-RateLimit-Tier: free
```

### Success Response (200)

```json
{
  "data": {
    "guild_id": "123456789",
    "name": "My Server",
    "premium": false
  },
  "meta": {
    "rate_limit": {
      "limit": 60,
      "remaining": 45,
      "reset": 1698768000,
      "tier": "free"
    }
  }
}
```

### Rate Limited Response (429)

```json
{
  "error": "Rate limit exceeded",
  "message": "You have exceeded the rate limit of 60 requests per minute",
  "limit": 60,
  "remaining": 0,
  "reset": 30,
  "tier": "free",
  "upgrade_url": "https://kingdom77.com/premium",
  "retry_after": 30
}
```

---

## 5️⃣ Per-Endpoint Limits

### Endpoint-Specific Limits

Some endpoints may have stricter limits:

```python
ENDPOINT_LIMITS = {
    "/api/guilds": 100,           # List guilds (expensive)
    "/api/users/search": 20,      # Search users (very expensive)
    "/api/export": 5,             # Export data (very expensive)
    "/api/stats": 30,             # Statistics (moderate)
}

def get_endpoint_limit(endpoint: str, tier: str) -> int:
    """Get limit for specific endpoint"""
    base_limit = rate_limiter.get_rate_limit(tier)
    endpoint_limit = ENDPOINT_LIMITS.get(endpoint)
    
    if endpoint_limit:
        return min(endpoint_limit, base_limit)
    
    return base_limit
```

### Implementation

```python
# In middleware
endpoint = request.url.path
endpoint_limit = get_endpoint_limit(endpoint, tier)

allowed, remaining, limit, reset = rate_limiter.check_rate_limit(
    identifier=identifier,
    tier=tier,
    endpoint=endpoint  # Per-endpoint tracking
)
```

---

## 6️⃣ Testing

### Test Script

```python
"""
Test Rate Limiting
"""
import asyncio
import httpx
import time

API_URL = "http://localhost:8000/api"
API_KEY = "your_test_api_key"

async def test_rate_limit():
    """Test rate limiting"""
    print("🧪 Testing Rate Limiting...")
    
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        # Test 1: Within limit
        print("\n📊 Test 1: Within Limit (Free tier: 60 req/min)")
        for i in range(5):
            response = await client.get(f"{API_URL}/guilds", headers=headers)
            print(f"Request {i+1}: {response.status_code}")
            print(f"  Remaining: {response.headers.get('X-RateLimit-Remaining')}")
        
        # Test 2: Exceed limit
        print("\n📊 Test 2: Exceed Limit")
        for i in range(65):
            response = await client.get(f"{API_URL}/guilds", headers=headers)
            if response.status_code == 429:
                print(f"✅ Rate limited at request {i+1}")
                print(f"  Reset in: {response.headers.get('Retry-After')}s")
                break
        
        # Test 3: Reset after window
        print("\n📊 Test 3: Reset After Window")
        print("Waiting 60 seconds...")
        await asyncio.sleep(60)
        
        response = await client.get(f"{API_URL}/guilds", headers=headers)
        assert response.status_code == 200
        print("✅ Rate limit reset successfully")
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_rate_limit())
```

### Load Testing

```bash
# Install Apache Bench
apt-get install apache2-utils

# Test rate limiting
ab -n 100 -c 10 -H "Authorization: Bearer YOUR_KEY" http://localhost:8000/api/guilds

# Expected: 60 success, 40 rate limited (429)
```

---

## 7️⃣ Monitoring

### Dashboard Metrics

```python
@app.get("/api/admin/rate-limits/stats")
async def get_rate_limit_stats(admin_only: bool = Depends(require_admin)):
    """Get rate limiting statistics"""
    
    # Get top users by request count
    keys = cache.client.keys("ratelimit:*")
    
    stats = []
    for key in keys[:100]:  # Top 100
        identifier = key.decode().split(":")[1]
        usage = rate_limiter.get_usage(identifier)
        stats.append({
            "identifier": identifier,
            "requests": usage["requests"],
            "window": usage["window"]
        })
    
    # Sort by requests
    stats.sort(key=lambda x: x["requests"], reverse=True)
    
    return {
        "total_users": len(keys),
        "top_users": stats[:20],
        "timestamp": int(time.time())
    }
```

### Grafana Dashboard

**Metrics to track:**
- Requests per minute (by tier)
- Rate limit hits (429 responses)
- Top users by request count
- Average response time
- Error rate

---

## 8️⃣ Best Practices

### 1. Informative Error Messages

```python
# ✅ Good
{
  "error": "Rate limit exceeded",
  "message": "You have exceeded the rate limit of 60 requests per minute. Upgrade to Premium for 300 req/min.",
  "upgrade_url": "https://kingdom77.com/premium"
}

# ❌ Bad
{
  "error": "Too many requests"
}
```

### 2. Graceful Degradation

```python
# If Redis is down, don't block all requests
try:
    allowed, remaining, limit, reset = rate_limiter.check_rate_limit(...)
except Exception as e:
    logger.error(f"Rate limiter error: {e}")
    # Allow request (fail open)
    allowed = True
```

### 3. Whitelist Critical Endpoints

```python
# Don't rate limit health checks
if request.url.path in ["/health", "/metrics"]:
    return await call_next(request)
```

### 4. Progressive Penalties

```python
# First offense: Normal rate limit
# Second offense: Reduced limit (30 req/min)
# Third offense: Temporary ban (1 hour)
```

---

## 9️⃣ Troubleshooting

### Issue 1: All Requests 429

**Problem:** Every request is rate limited

**Solution:**
1. Check Redis connection
2. Verify rate limiter initialization
3. Check tier assignment
4. Clear Redis keys: `FLUSHDB`

### Issue 2: Headers Not Showing

**Problem:** X-RateLimit-* headers missing

**Solution:**
1. Check middleware order
2. Verify response modification
3. Check CORS settings

### Issue 3: Incorrect Tier

**Problem:** User has wrong tier

**Solution:**
1. Check database premium field
2. Verify tier lookup logic
3. Clear cache for user

---

## ✅ Verification Checklist

- [ ] Redis connection configured
- [ ] Rate limiter module created
- [ ] Middleware implemented
- [ ] Tier configuration in .env
- [ ] Headers added to responses
- [ ] 429 error handling implemented
- [ ] Per-endpoint limits (optional)
- [ ] Test script passed
- [ ] Monitoring dashboard set up
- [ ] Documentation updated

---

## 📊 Expected Behavior

| Tier | Limit | Burst | Overage |
|------|-------|-------|---------|
| Free | 60/min | - | 429 error |
| Basic | 120/min | +10 | 429 error |
| Premium | 300/min | +20 | Rarely hit |
| Admin | 1000/min | +50 | For testing |

---

## 🔗 Resources

- **Redis Rate Limiting:** https://redis.io/docs/manual/patterns/rate-limiter/
- **Token Bucket:** https://en.wikipedia.org/wiki/Token_bucket
- **FastAPI Middleware:** https://fastapi.tiangolo.com/tutorial/middleware/

---

**✅ Rate Limiting Configured! Your API is protected.**

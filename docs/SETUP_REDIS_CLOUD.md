# ⚡ Redis Cloud Setup Guide

**Complete guide to set up Redis Cloud for Kingdom-77 Bot v4.0**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Create Account](#create-account)
3. [Create Database](#create-database)
4. [Configuration](#configuration)
5. [Connection Setup](#connection-setup)
6. [Cache Strategy](#cache-strategy)
7. [Rate Limiting Setup](#rate-limiting-setup)
8. [Monitoring](#monitoring)
9. [Testing](#testing)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**What You'll Get:**
- Free Redis database (30MB storage)
- In-memory caching (ultra-fast)
- Rate limiting support
- Session management
- 30ms latency

**Use Cases in Kingdom-77:**
- API response caching (5-minute TTL)
- Rate limiting counters
- Session management
- Leaderboard caching
- Real-time statistics

**Requirements:**
- Email account
- No credit card required

**Estimated Time:** 10 minutes

---

## 1️⃣ Create Account

### Step 1: Sign Up

1. Go to: https://redis.com/try-free/
2. Click **"Get Started Free"**
3. Fill in:
   ```
   Email: your-email@example.com
   Password: [Strong Password]
   ```
4. Or sign up with Google/GitHub

### Step 2: Verify Email

- Check your email inbox
- Click verification link
- Complete profile setup

---

## 2️⃣ Create Database

### Step 1: New Subscription

1. Click **"New Subscription"**
2. Select **"Free"** plan
   - ✅ 30MB storage
   - ✅ 30 connections
   - ✅ FREE Forever

### Step 2: Cloud Provider & Region

**Recommended Configuration:**

| Setting | Value | Reason |
|---------|-------|--------|
| **Provider** | AWS | Best performance |
| **Region** | Middle East (Bahrain) | Closest to Saudi Arabia |
| **Alternative** | EU Central (Frankfurt) | Good latency |

### Step 3: Database Settings

```
Database Name: kingdom77-cache
Type: Redis Stack
Eviction Policy: allkeys-lru (Least Recently Used)
```

**Eviction Policies Explained:**

- **allkeys-lru:** Remove least recently used keys (RECOMMENDED)
- **volatile-lru:** Remove least recently used keys with TTL
- **allkeys-lfu:** Remove least frequently used keys
- **volatile-ttl:** Remove keys with shortest TTL first

### Step 4: Create Database

- Click **"Activate"**
- Wait 1-2 minutes for provisioning

---

## 3️⃣ Configuration

### Database Settings

1. Go to **"Databases"** → Select your database
2. Note down:
   ```
   Endpoint: redis-12345.c123.middle-east-1.rds.amazonaws.com:12345
   Port: 12345
   Password: [Copy and save securely]
   ```

### Security Settings

**Password Authentication:**
- ✅ Default password is strong
- ⚠️ Don't share password
- 💡 Rotate password every 90 days

**IP Whitelist (Optional):**
1. Go to **"Security"** → **"CIDR Whitelist"**
2. Add your server IPs:
   ```
   0.0.0.0/0  # Allow from anywhere (dev)
   123.456.789.0/32  # Production server
   ```

---

## 4️⃣ Connection Setup

### Step 1: Get Connection String

**Format:**
```
redis://default:PASSWORD@ENDPOINT:PORT
```

**Example:**
```
redis://default:abc123def456@redis-12345.c123.me-south-1.rds.amazonaws.com:12345
```

**With SSL (Recommended):**
```
rediss://default:PASSWORD@ENDPOINT:PORT
```

### Step 2: Update .env File

```bash
# Redis Configuration
REDIS_URL=rediss://default:YOUR_PASSWORD@redis-12345.c123.me-south-1.rds.amazonaws.com:12345
REDIS_DB=0
CACHE_TTL=300  # 5 minutes in seconds
```

### Step 3: Test Connection

```bash
# Using redis-cli
redis-cli -h redis-12345.c123.me-south-1.rds.amazonaws.com -p 12345 -a YOUR_PASSWORD --tls ping

# Expected: PONG
```

**Python Test:**
```python
import redis
import os

redis_url = os.getenv("REDIS_URL")
client = redis.from_url(redis_url, decode_responses=True)

# Test connection
print(client.ping())  # Should print: True

# Test set/get
client.set("test", "Hello Kingdom-77!", ex=10)
print(client.get("test"))  # Should print: Hello Kingdom-77!
```

---

## 5️⃣ Cache Strategy

### Cache Configuration (cache/__init__.py)

```python
"""
Kingdom-77 Redis Cache Module
"""
import redis
import json
import os
from typing import Any, Optional
from datetime import timedelta

__version__ = '4.0.0'

class RedisCache:
    """Redis caching for Kingdom-77 Bot"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        self.cache_ttl = int(os.getenv("CACHE_TTL", 300))  # Default 5 min
        
        if not self.redis_url:
            raise ValueError("REDIS_URL not set in environment")
        
        self.client = redis.from_url(
            self.redis_url,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"❌ Redis GET error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cached value with TTL"""
        try:
            ttl = ttl or self.cache_ttl
            data = json.dumps(value)
            self.client.setex(key, ttl, data)
            return True
        except Exception as e:
            print(f"❌ Redis SET error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"❌ Redis DELETE error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.client.exists(key) > 0
    
    def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            print(f"❌ Redis CLEAR error: {e}")
            return 0
    
    def get_ttl(self, key: str) -> int:
        """Get remaining TTL in seconds"""
        return self.client.ttl(key)

# Global cache instance
cache = RedisCache()
```

### Cache Keys Strategy

**Naming Convention:**
```
{service}:{entity}:{id}:{attribute}
```

**Examples:**
```python
# Guild settings
cache_key = f"guild:{guild_id}:settings"

# User level
cache_key = f"user:{user_id}:guild:{guild_id}:level"

# Giveaway data
cache_key = f"giveaway:{giveaway_id}:data"

# API response
cache_key = f"api:guilds:{guild_id}:stats"

# Leaderboard
cache_key = f"leaderboard:{guild_id}:levels:top10"
```

### TTL Strategy

| Data Type | TTL | Reason |
|-----------|-----|--------|
| API Responses | 5 min | Fresh data |
| Guild Settings | 10 min | Rarely changes |
| User Profiles | 15 min | Moderate changes |
| Leaderboards | 1 min | Frequent updates |
| Statistics | 5 min | Real-time stats |
| Session Data | 24 hours | User sessions |

---

## 6️⃣ Rate Limiting Setup

### Rate Limiter Implementation

```python
"""
Rate Limiting using Redis
"""
import time
from typing import Tuple

class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int = 60
    ) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limit
        
        Args:
            key: Unique identifier (user_id, ip, etc.)
            limit: Max requests per window
            window: Time window in seconds (default: 60)
        
        Returns:
            (allowed, remaining, reset_time)
        """
        current_time = int(time.time())
        window_key = f"ratelimit:{key}:{current_time // window}"
        
        # Get current count
        count = self.redis.get(window_key)
        count = int(count) if count else 0
        
        if count >= limit:
            # Rate limit exceeded
            ttl = self.redis.ttl(window_key)
            return False, 0, ttl
        
        # Increment counter
        pipe = self.redis.pipeline()
        pipe.incr(window_key)
        pipe.expire(window_key, window)
        pipe.execute()
        
        remaining = limit - count - 1
        return True, remaining, window

# Usage in API
from cache import cache

rate_limiter = RateLimiter(cache.client)

@app.get("/api/guilds/{guild_id}")
async def get_guild(guild_id: str, request: Request):
    # Get user tier
    tier = get_user_tier(request.user_id)
    
    # Rate limits by tier
    limits = {
        "free": 60,      # 60 req/min
        "basic": 120,    # 120 req/min
        "premium": 300   # 300 req/min
    }
    
    limit = limits.get(tier, 60)
    
    # Check rate limit
    allowed, remaining, reset = rate_limiter.check_rate_limit(
        f"user:{request.user_id}",
        limit=limit,
        window=60
    )
    
    if not allowed:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "limit": limit,
                "remaining": 0,
                "reset": reset
            },
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(reset),
                "Retry-After": str(reset)
            }
        )
    
    # Add rate limit headers
    response = await get_guild_data(guild_id)
    response.headers["X-RateLimit-Limit"] = str(limit)
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset)
    
    return response
```

---

## 7️⃣ Monitoring

### Redis Cloud Dashboard

1. Go to **"Databases"** → Select database
2. Monitor:
   - **Operations/sec:** Read/write rate
   - **Memory Usage:** Current storage used
   - **Connections:** Active connections
   - **Hit Rate:** Cache effectiveness

### Performance Metrics

```python
# Get Redis stats
info = cache.client.info()

print(f"Used Memory: {info['used_memory_human']}")
print(f"Connected Clients: {info['connected_clients']}")
print(f"Total Commands: {info['total_commands_processed']}")
print(f"Hit Rate: {info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses']) * 100:.2f}%")
```

### Alerts Setup

1. Go to **"Alerts"**
2. Create alerts for:
   - Memory usage > 25MB (83%)
   - Connections > 25 (83%)
   - High latency > 100ms

---

## 8️⃣ Testing

### Test Script

```python
"""
Test Redis Cache and Rate Limiting
"""
import asyncio
from cache import cache, RateLimiter

async def test_cache():
    """Test caching functionality"""
    print("🧪 Testing Redis Cache...")
    
    # Test 1: Set/Get
    cache.set("test:key", {"value": "Hello"}, ttl=10)
    result = cache.get("test:key")
    assert result == {"value": "Hello"}, "❌ Set/Get failed"
    print("✅ Set/Get working")
    
    # Test 2: Expiry
    import time
    time.sleep(11)
    result = cache.get("test:key")
    assert result is None, "❌ TTL not working"
    print("✅ TTL working")
    
    # Test 3: Pattern delete
    cache.set("guild:123:settings", {})
    cache.set("guild:123:stats", {})
    cache.set("guild:456:settings", {})
    deleted = cache.clear_pattern("guild:123:*")
    assert deleted == 2, "❌ Pattern delete failed"
    print("✅ Pattern delete working")
    
    print("🎉 All cache tests passed!")

async def test_rate_limiting():
    """Test rate limiting"""
    print("\n🧪 Testing Rate Limiting...")
    
    limiter = RateLimiter(cache.client)
    
    # Test: 5 requests per minute
    key = "test:user:123"
    limit = 5
    
    results = []
    for i in range(7):
        allowed, remaining, reset = limiter.check_rate_limit(key, limit, 60)
        results.append((allowed, remaining))
        print(f"Request {i+1}: Allowed={allowed}, Remaining={remaining}")
    
    # First 5 should be allowed
    assert all(r[0] for r in results[:5]), "❌ Should allow first 5"
    
    # Last 2 should be blocked
    assert not any(r[0] for r in results[5:]), "❌ Should block after limit"
    
    print("✅ Rate limiting working")
    print("🎉 All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_cache())
    asyncio.run(test_rate_limiting())
```

---

## 9️⃣ Best Practices

### 1. Key Naming

```python
# ✅ Good
"guild:123:settings"
"user:456:level"
"api:response:guilds:123"

# ❌ Bad
"settings_123"
"user456level"
"response"
```

### 2. TTL Management

```python
# Set appropriate TTLs
cache.set("guild:settings", data, ttl=600)    # 10 min
cache.set("leaderboard", data, ttl=60)        # 1 min
cache.set("session:token", data, ttl=86400)   # 24 hours
```

### 3. Error Handling

```python
# Always handle Redis failures gracefully
def get_guild_settings(guild_id):
    # Try cache first
    cached = cache.get(f"guild:{guild_id}:settings")
    if cached:
        return cached
    
    # Fallback to database
    settings = db.get_guild_settings(guild_id)
    
    # Cache for next time
    cache.set(f"guild:{guild_id}:settings", settings, ttl=600)
    
    return settings
```

### 4. Memory Optimization

```python
# Use hashes for related data
cache.client.hset(f"guild:{guild_id}", "name", "My Server")
cache.client.hset(f"guild:{guild_id}", "premium", "true")
cache.client.expire(f"guild:{guild_id}", 600)

# Instead of multiple keys
cache.set(f"guild:{guild_id}:name", "My Server")
cache.set(f"guild:{guild_id}:premium", "true")
```

---

## 🔟 Troubleshooting

### Issue 1: Connection Refused

**Problem:** Cannot connect to Redis

**Solution:**
1. Check REDIS_URL in .env
2. Verify endpoint and port
3. Check IP whitelist
4. Test with redis-cli

### Issue 2: Authentication Failed

**Problem:** Wrong password

**Solution:**
1. Copy password from Redis Cloud dashboard
2. Escape special characters in URL
3. Use `rediss://` for SSL

### Issue 3: Memory Limit Exceeded

**Problem:** 30MB limit reached

**Solution:**
1. Check memory usage in dashboard
2. Reduce TTLs
3. Clear old keys: `cache.clear_pattern("old:*")`
4. Use LRU eviction policy
5. Upgrade to paid plan ($5/month for 250MB)

### Issue 4: High Latency

**Problem:** Slow responses

**Solution:**
1. Choose closer region
2. Check network connectivity
3. Use connection pooling
4. Reduce payload size

---

## ✅ Verification Checklist

- [ ] Account created and verified
- [ ] Free database created (30MB)
- [ ] Region selected (Middle East/EU)
- [ ] Connection string copied
- [ ] .env file updated with REDIS_URL
- [ ] Connection tested successfully
- [ ] Cache module implemented
- [ ] Rate limiter implemented
- [ ] TTL strategy defined
- [ ] Monitoring alerts set up
- [ ] Test script passed

---

## 📊 Expected Performance

**Free Plan:**
- **Storage:** 30MB
- **Connections:** 30 concurrent
- **Throughput:** 100K ops/sec
- **Latency:** 30-50ms (ME region)

**Paid Plan ($5/month):**
- **Storage:** 250MB
- **Connections:** 256 concurrent
- **Throughput:** 500K ops/sec
- **Backups:** Automatic

---

## 🔗 Useful Links

- **Redis Cloud:** https://redis.com/try-free/
- **Documentation:** https://docs.redis.com/
- **Python Client:** https://redis-py.readthedocs.io/
- **Best Practices:** https://redis.io/topics/best-practices

---

## 🆘 Support

**Issues?**
1. Redis Cloud Status: https://status.redis.com/
2. Documentation: https://docs.redis.com/
3. Kingdom-77 Support: [Your Discord Server]

---

**✅ Setup Complete! Your Redis Cache is ready for production.**

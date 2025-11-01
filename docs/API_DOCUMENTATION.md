# 🌐 Kingdom-77 Bot - API Documentation

**Version:** v4.0.0  
**Last Updated:** November 1, 2025  
**Base URL:** `https://api.kingdom77.com/v1`  
**Total Endpoints:** 66+

---

## 📋 Table of Contents

- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [🎁 Giveaway API](#giveaway-api) **NEW v4.0**
- [📝 Applications API](#applications-api) **NEW v4.0**
- [💬 Auto-Messages API](#auto-messages-api) **NEW v4.0**
- [🌐 Social Integration API](#social-integration-api) **NEW v4.0**
- [🛡️ Moderation API](#moderation-api)
- [📊 Leveling API](#leveling-api)
- [🎫 Tickets API](#tickets-api)
- [🎭 Auto-Roles API](#auto-roles-api)
- [💰 Economy API](#economy-api)
- [💎 Premium API](#premium-api)
- [📊 Statistics API](#statistics-api)
- [WebSocket Events](#websocket-events)

---

<a id="authentication"></a>
## 🔐 Authentication

All API requests require authentication using JWT tokens.

### Get Access Token

**Endpoint:** `POST /auth/token`

**Request Body:**
```json
{
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "grant_type": "client_credentials"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### Using Token

Include the token in the `Authorization` header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

<a id="rate-limiting"></a>
## ⚡ Rate Limiting

| Tier | Requests/Minute | Requests/Hour |
|------|-----------------|---------------|
| **Free** | 60 | 1,000 |
| **Basic** | 120 | 5,000 |
| **Premium** | 300 | 20,000 |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1635724800
```

**429 Response:**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Try again in 45 seconds.",
  "retry_after": 45
}
```

---

<a id="error-handling"></a>
## ❌ Error Handling

### Error Response Format

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "Additional context"
  },
  "request_id": "req_abc123"
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `invalid_request` | 400 | Missing or invalid parameters |
| `unauthorized` | 401 | Invalid or missing token |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `rate_limit_exceeded` | 429 | Too many requests |
| `internal_error` | 500 | Server error |

---

<a id="giveaway-api"></a>
## 🎁 Giveaway API **NEW v4.0**

**9 Endpoints** | Manage giveaways, templates, and entries

### 1. Create Giveaway

**Endpoint:** `POST /giveaways`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "channel_id": "987654321",
  "prize": "Discord Nitro",
  "winners": 1,
  "duration": 3600,
  "requirements": {
    "min_level": 5,
    "required_roles": ["role_id_1", "role_id_2"],
    "min_account_age": 604800
  },
  "scheduled_start": "2025-11-10T15:00:00Z"
}
```

**Response:**
```json
{
  "id": "giveaway_abc123",
  "guild_id": "123456789",
  "channel_id": "987654321",
  "message_id": "111222333",
  "prize": "Discord Nitro",
  "winners": 1,
  "duration": 3600,
  "entries": 0,
  "status": "scheduled",
  "starts_at": "2025-11-10T15:00:00Z",
  "ends_at": "2025-11-10T16:00:00Z",
  "created_at": "2025-11-01T12:00:00Z"
}
```

---

### 2. Get Giveaway

**Endpoint:** `GET /giveaways/{giveaway_id}`

**Response:**
```json
{
  "id": "giveaway_abc123",
  "guild_id": "123456789",
  "prize": "Discord Nitro",
  "winners": 1,
  "entries": 45,
  "participants": [
    {
      "user_id": "user_1",
      "entries": 1,
      "joined_at": "2025-11-10T15:05:00Z"
    }
  ],
  "status": "active",
  "ends_at": "2025-11-10T16:00:00Z"
}
```

---

### 3. List Giveaways

**Endpoint:** `GET /guilds/{guild_id}/giveaways`

**Query Parameters:**
- `status` - Filter by status (active, scheduled, ended)
- `limit` - Results per page (default: 20, max: 100)
- `offset` - Pagination offset

**Response:**
```json
{
  "data": [
    {
      "id": "giveaway_abc123",
      "prize": "Discord Nitro",
      "status": "active",
      "entries": 45,
      "ends_at": "2025-11-10T16:00:00Z"
    }
  ],
  "total": 10,
  "limit": 20,
  "offset": 0
}
```

---

### 4. End Giveaway

**Endpoint:** `POST /giveaways/{giveaway_id}/end`

**Response:**
```json
{
  "id": "giveaway_abc123",
  "status": "ended",
  "winners": [
    {
      "user_id": "user_1",
      "username": "Winner#1234",
      "selected_at": "2025-11-10T16:00:00Z"
    }
  ],
  "ended_at": "2025-11-10T16:00:00Z"
}
```

---

### 5. Reroll Giveaway

**Endpoint:** `POST /giveaways/{giveaway_id}/reroll`

**Request Body:**
```json
{
  "count": 1
}
```

**Response:**
```json
{
  "id": "giveaway_abc123",
  "new_winners": [
    {
      "user_id": "user_2",
      "username": "NewWinner#5678"
    }
  ]
}
```

---

### 6. Delete Giveaway

**Endpoint:** `DELETE /giveaways/{giveaway_id}`

**Response:**
```json
{
  "success": true,
  "message": "Giveaway deleted successfully"
}
```

---

### 7. Create Template

**Endpoint:** `POST /giveaways/templates`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "name": "Weekly Nitro Giveaway",
  "prize": "Discord Nitro",
  "winners": 1,
  "duration": 604800,
  "requirements": {
    "min_level": 10
  }
}
```

**Response:**
```json
{
  "id": "template_abc123",
  "name": "Weekly Nitro Giveaway",
  "guild_id": "123456789",
  "created_at": "2025-11-01T12:00:00Z"
}
```

---

### 8. List Templates

**Endpoint:** `GET /guilds/{guild_id}/giveaways/templates`

**Response:**
```json
{
  "data": [
    {
      "id": "template_abc123",
      "name": "Weekly Nitro Giveaway",
      "prize": "Discord Nitro",
      "usage_count": 5
    }
  ],
  "total": 3
}
```

---

### 9. Get Giveaway Statistics

**Endpoint:** `GET /guilds/{guild_id}/giveaways/stats`

**Response:**
```json
{
  "total_giveaways": 25,
  "active_giveaways": 3,
  "total_winners": 50,
  "total_entries": 1250,
  "avg_entries_per_giveaway": 50,
  "completion_rate": 0.96
}
```

---

<a id="applications-api"></a>
## 📝 Applications API **NEW v4.0**

**9 Endpoints** | Manage application forms and submissions

### 1. Create Application Form

**Endpoint:** `POST /applications`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "name": "Staff Application",
  "description": "Apply to become a moderator",
  "review_channel_id": "987654321",
  "approval_role_id": "role_123",
  "questions": [
    {
      "type": "text",
      "question": "What's your Discord username?",
      "required": true,
      "max_length": 100
    },
    {
      "type": "number",
      "question": "How old are you?",
      "required": true,
      "min_value": 13,
      "max_value": 100
    },
    {
      "type": "select",
      "question": "What timezone are you in?",
      "required": true,
      "options": ["UTC-5", "UTC", "UTC+1", "UTC+3"]
    }
  ]
}
```

**Response:**
```json
{
  "id": "app_abc123",
  "guild_id": "123456789",
  "name": "Staff Application",
  "status": "active",
  "questions_count": 3,
  "submissions_count": 0,
  "created_at": "2025-11-01T12:00:00Z"
}
```

---

### 2. Get Application Form

**Endpoint:** `GET /applications/{application_id}`

**Response:**
```json
{
  "id": "app_abc123",
  "guild_id": "123456789",
  "name": "Staff Application",
  "description": "Apply to become a moderator",
  "questions": [
    {
      "id": "q1",
      "type": "text",
      "question": "What's your Discord username?",
      "required": true
    }
  ],
  "submissions_count": 15,
  "approval_rate": 0.6
}
```

---

### 3. List Application Forms

**Endpoint:** `GET /guilds/{guild_id}/applications`

**Response:**
```json
{
  "data": [
    {
      "id": "app_abc123",
      "name": "Staff Application",
      "status": "active",
      "submissions_count": 15,
      "created_at": "2025-11-01T12:00:00Z"
    }
  ],
  "total": 3
}
```

---

### 4. Update Application Form

**Endpoint:** `PATCH /applications/{application_id}`

**Request Body:**
```json
{
  "name": "Updated Staff Application",
  "status": "active"
}
```

**Response:**
```json
{
  "id": "app_abc123",
  "name": "Updated Staff Application",
  "updated_at": "2025-11-01T13:00:00Z"
}
```

---

### 5. Delete Application Form

**Endpoint:** `DELETE /applications/{application_id}`

**Response:**
```json
{
  "success": true,
  "message": "Application form deleted"
}
```

---

### 6. Submit Application

**Endpoint:** `POST /applications/{application_id}/submit`

**Request Body:**
```json
{
  "user_id": "user_123",
  "answers": [
    {
      "question_id": "q1",
      "answer": "JohnDoe#1234"
    },
    {
      "question_id": "q2",
      "answer": 25
    }
  ]
}
```

**Response:**
```json
{
  "id": "submission_abc123",
  "application_id": "app_abc123",
  "user_id": "user_123",
  "status": "pending",
  "submitted_at": "2025-11-01T14:00:00Z"
}
```

---

### 7. Get Submission

**Endpoint:** `GET /applications/submissions/{submission_id}`

**Response:**
```json
{
  "id": "submission_abc123",
  "application_id": "app_abc123",
  "user": {
    "id": "user_123",
    "username": "JohnDoe",
    "discriminator": "1234"
  },
  "answers": [
    {
      "question": "What's your Discord username?",
      "answer": "JohnDoe#1234"
    }
  ],
  "status": "pending",
  "submitted_at": "2025-11-01T14:00:00Z"
}
```

---

### 8. Review Submission

**Endpoint:** `POST /applications/submissions/{submission_id}/review`

**Request Body:**
```json
{
  "action": "approve",
  "reason": "Great application!",
  "reviewer_id": "admin_123"
}
```

**Response:**
```json
{
  "id": "submission_abc123",
  "status": "approved",
  "reviewed_by": "admin_123",
  "reviewed_at": "2025-11-01T15:00:00Z"
}
```

---

### 9. Get Application Statistics

**Endpoint:** `GET /applications/{application_id}/stats`

**Response:**
```json
{
  "total_submissions": 50,
  "pending": 10,
  "approved": 30,
  "rejected": 10,
  "approval_rate": 0.75,
  "avg_review_time": 3600,
  "popular_answers": {
    "q1": {
      "most_common": "Yes",
      "count": 40
    }
  }
}
```

---

<a id="auto-messages-api"></a>
## 💬 Auto-Messages API **NEW v4.0**

**9 Endpoints** | Manage auto-messages, triggers, and responses

### 1. Create Auto-Message

**Endpoint:** `POST /auto-messages`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "name": "Welcome Message",
  "trigger": {
    "type": "keyword",
    "value": "!welcome",
    "case_sensitive": false
  },
  "response": {
    "type": "embed",
    "content": {
      "title": "Welcome to {server}!",
      "description": "Hello {user}, enjoy your stay!",
      "color": "#00FF00",
      "thumbnail": "https://example.com/logo.png"
    }
  },
  "settings": {
    "delete_trigger": true,
    "cooldown": 60,
    "required_permissions": []
  }
}
```

**Response:**
```json
{
  "id": "automsg_abc123",
  "guild_id": "123456789",
  "name": "Welcome Message",
  "status": "active",
  "trigger_count": 0,
  "created_at": "2025-11-01T12:00:00Z"
}
```

---

### 2. Get Auto-Message

**Endpoint:** `GET /auto-messages/{message_id}`

**Response:**
```json
{
  "id": "automsg_abc123",
  "guild_id": "123456789",
  "name": "Welcome Message",
  "trigger": {
    "type": "keyword",
    "value": "!welcome"
  },
  "response": {
    "type": "embed",
    "content": { }
  },
  "trigger_count": 150,
  "last_triggered": "2025-11-01T14:00:00Z"
}
```

---

### 3. List Auto-Messages

**Endpoint:** `GET /guilds/{guild_id}/auto-messages`

**Query Parameters:**
- `status` - Filter by status (active, disabled)
- `trigger_type` - Filter by trigger type

**Response:**
```json
{
  "data": [
    {
      "id": "automsg_abc123",
      "name": "Welcome Message",
      "status": "active",
      "trigger_count": 150
    }
  ],
  "total": 5
}
```

---

### 4. Update Auto-Message

**Endpoint:** `PATCH /auto-messages/{message_id}`

**Request Body:**
```json
{
  "name": "Updated Welcome",
  "status": "active"
}
```

**Response:**
```json
{
  "id": "automsg_abc123",
  "name": "Updated Welcome",
  "updated_at": "2025-11-01T13:00:00Z"
}
```

---

### 5. Delete Auto-Message

**Endpoint:** `DELETE /auto-messages/{message_id}`

**Response:**
```json
{
  "success": true,
  "message": "Auto-message deleted"
}
```

---

### 6. Toggle Auto-Message

**Endpoint:** `POST /auto-messages/{message_id}/toggle`

**Response:**
```json
{
  "id": "automsg_abc123",
  "status": "disabled"
}
```

---

### 7. Test Auto-Message

**Endpoint:** `POST /auto-messages/{message_id}/test`

**Request Body:**
```json
{
  "user_id": "user_123",
  "channel_id": "channel_123"
}
```

**Response:**
```json
{
  "success": true,
  "preview": {
    "type": "embed",
    "content": {
      "title": "Welcome to Test Server!",
      "description": "Hello TestUser, enjoy your stay!"
    }
  }
}
```

---

### 8. Get Variables

**Endpoint:** `GET /auto-messages/variables`

**Response:**
```json
{
  "variables": [
    {
      "name": "{user}",
      "description": "User mention",
      "example": "@JohnDoe"
    },
    {
      "name": "{server}",
      "description": "Server name",
      "example": "Kingdom-77"
    }
  ]
}
```

---

### 9. Get Auto-Message Statistics

**Endpoint:** `GET /guilds/{guild_id}/auto-messages/stats`

**Response:**
```json
{
  "total_messages": 10,
  "active_messages": 8,
  "total_triggers": 5000,
  "avg_triggers_per_message": 500,
  "most_triggered": {
    "id": "automsg_abc123",
    "name": "Welcome Message",
    "count": 1500
  }
}
```

---

<a id="social-integration-api"></a>
## 🌐 Social Integration API **NEW v4.0**

**10 Endpoints** | Manage social media integrations

### 1. Add Social Link

**Endpoint:** `POST /social/links`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "platform": "youtube",
  "url": "https://youtube.com/@channelname",
  "channel_id": "discord_channel_123",
  "custom_message": "🎥 New video from {author}: {title}",
  "mention_role_id": "role_123"
}
```

**Response:**
```json
{
  "id": "link_abc123",
  "guild_id": "123456789",
  "platform": "youtube",
  "author": "ChannelName",
  "status": "active",
  "created_at": "2025-11-01T12:00:00Z"
}
```

---

### 2. Get Social Link

**Endpoint:** `GET /social/links/{link_id}`

**Response:**
```json
{
  "id": "link_abc123",
  "guild_id": "123456789",
  "platform": "youtube",
  "url": "https://youtube.com/@channelname",
  "author": "ChannelName",
  "channel_id": "discord_channel_123",
  "status": "active",
  "posts_count": 25,
  "last_post": "2025-11-01T10:00:00Z"
}
```

---

### 3. List Social Links

**Endpoint:** `GET /guilds/{guild_id}/social/links`

**Query Parameters:**
- `platform` - Filter by platform (youtube, twitch, etc.)
- `status` - Filter by status (active, disabled)

**Response:**
```json
{
  "data": [
    {
      "id": "link_abc123",
      "platform": "youtube",
      "author": "ChannelName",
      "status": "active",
      "posts_count": 25
    }
  ],
  "total": 7,
  "limits": {
    "youtube": { "used": 1, "max": 3 },
    "twitch": { "used": 0, "max": 3 }
  }
}
```

---

### 4. Update Social Link

**Endpoint:** `PATCH /social/links/{link_id}`

**Request Body:**
```json
{
  "channel_id": "new_channel_123",
  "custom_message": "Updated message"
}
```

**Response:**
```json
{
  "id": "link_abc123",
  "updated_at": "2025-11-01T13:00:00Z"
}
```

---

### 5. Delete Social Link

**Endpoint:** `DELETE /social/links/{link_id}`

**Response:**
```json
{
  "success": true,
  "message": "Social link deleted"
}
```

---

### 6. Toggle Social Link

**Endpoint:** `POST /social/links/{link_id}/toggle`

**Response:**
```json
{
  "id": "link_abc123",
  "status": "disabled"
}
```

---

### 7. Test Social Link

**Endpoint:** `POST /social/links/{link_id}/test`

**Response:**
```json
{
  "success": true,
  "message": "Test post sent to channel"
}
```

---

### 8. Get Link Limits

**Endpoint:** `GET /guilds/{guild_id}/social/limits`

**Response:**
```json
{
  "total_used": 7,
  "total_purchased": 5,
  "platforms": {
    "youtube": { "used": 1, "max": 3, "remaining": 2 },
    "twitch": { "used": 2, "max": 3, "remaining": 1 }
  }
}
```

---

### 9. Purchase Link Slot

**Endpoint:** `POST /social/purchase`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "platform": "youtube",
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "success": true,
  "platform": "youtube",
  "new_limit": 4,
  "cost": 200,
  "new_balance": 800
}
```

---

### 10. Get Recent Posts

**Endpoint:** `GET /guilds/{guild_id}/social/posts`

**Query Parameters:**
- `platform` - Filter by platform
- `limit` - Results per page (default: 10, max: 50)

**Response:**
```json
{
  "data": [
    {
      "id": "post_abc123",
      "platform": "youtube",
      "author": "ChannelName",
      "title": "Amazing Video Title",
      "url": "https://youtube.com/watch?v=...",
      "posted_at": "2025-11-01T10:00:00Z"
    }
  ],
  "total": 50
}
```

---

<a id="moderation-api"></a>
## 🛡️ Moderation API

**8 Endpoints** | Warnings, bans, and AutoMod

### 1. Add Warning

**Endpoint:** `POST /moderation/warnings`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "user_id": "user_123",
  "moderator_id": "mod_123",
  "reason": "Spam in chat"
}
```

**Response:**
```json
{
  "id": "warn_abc123",
  "user_id": "user_123",
  "warning_count": 1,
  "reason": "Spam in chat",
  "created_at": "2025-11-01T12:00:00Z"
}
```

---

### 2. Get User Warnings

**Endpoint:** `GET /guilds/{guild_id}/users/{user_id}/warnings`

**Response:**
```json
{
  "user_id": "user_123",
  "total_warnings": 2,
  "warnings": [
    {
      "id": "warn_abc123",
      "reason": "Spam in chat",
      "moderator_id": "mod_123",
      "created_at": "2025-11-01T12:00:00Z"
    }
  ]
}
```

---

### 3. Remove Warning

**Endpoint:** `DELETE /moderation/warnings/{warning_id}`

**Response:**
```json
{
  "success": true,
  "message": "Warning removed"
}
```

---

### 4. Get Moderation Logs

**Endpoint:** `GET /guilds/{guild_id}/moderation/logs`

**Query Parameters:**
- `action_type` - warn, mute, kick, ban
- `moderator_id` - Filter by moderator
- `limit` - Results per page

**Response:**
```json
{
  "data": [
    {
      "id": "log_abc123",
      "action": "warn",
      "user_id": "user_123",
      "moderator_id": "mod_123",
      "reason": "Spam",
      "timestamp": "2025-11-01T12:00:00Z"
    }
  ],
  "total": 100
}
```

---

### 5. Configure AutoMod

**Endpoint:** `POST /guilds/{guild_id}/automod/config`

**Request Body:**
```json
{
  "spam_detection": true,
  "link_filter": true,
  "bad_words": ["word1", "word2"],
  "caps_limit": 70
}
```

**Response:**
```json
{
  "guild_id": "123456789",
  "config": {
    "spam_detection": true,
    "link_filter": true
  },
  "updated_at": "2025-11-01T12:00:00Z"
}
```

---

### 6. Get AutoMod Status

**Endpoint:** `GET /guilds/{guild_id}/automod/status`

**Response:**
```json
{
  "enabled": true,
  "actions_taken": 150,
  "last_action": "2025-11-01T11:00:00Z"
}
```

---

### 7. Ban User

**Endpoint:** `POST /guilds/{guild_id}/bans`

**Request Body:**
```json
{
  "user_id": "user_123",
  "moderator_id": "mod_123",
  "reason": "Repeated violations",
  "delete_message_days": 7
}
```

**Response:**
```json
{
  "success": true,
  "user_id": "user_123",
  "banned_at": "2025-11-01T12:00:00Z"
}
```

---

### 8. Get Moderation Statistics

**Endpoint:** `GET /guilds/{guild_id}/moderation/stats`

**Response:**
```json
{
  "total_warnings": 500,
  "total_mutes": 100,
  "total_kicks": 50,
  "total_bans": 25,
  "automod_actions": 300
}
```

---

<a id="leveling-api"></a>
## 📊 Leveling API

**3 Endpoints** | XP and rank management

### 1. Get User Level

**Endpoint:** `GET /guilds/{guild_id}/users/{user_id}/level`

**Response:**
```json
{
  "user_id": "user_123",
  "level": 15,
  "xp": 3500,
  "xp_to_next_level": 500,
  "total_messages": 1250,
  "rank": 10
}
```

---

### 2. Update User XP

**Endpoint:** `POST /guilds/{guild_id}/users/{user_id}/xp`

**Request Body:**
```json
{
  "amount": 100,
  "reason": "Event participation"
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "old_level": 15,
  "new_level": 16,
  "xp": 3600
}
```

---

### 3. Get Leaderboard

**Endpoint:** `GET /guilds/{guild_id}/leaderboard`

**Query Parameters:**
- `limit` - Results per page (default: 100)
- `timeframe` - daily, weekly, monthly, all_time

**Response:**
```json
{
  "data": [
    {
      "rank": 1,
      "user_id": "user_123",
      "username": "TopUser",
      "level": 50,
      "xp": 125000,
      "messages": 50000
    }
  ],
  "total": 5000
}
```

---

<a id="tickets-api"></a>
## 🎫 Tickets API

**6 Endpoints** | Support ticket management

### 1. Create Ticket

**Endpoint:** `POST /tickets`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "user_id": "user_123",
  "category": "support",
  "reason": "Need help with commands"
}
```

**Response:**
```json
{
  "id": "ticket_abc123",
  "guild_id": "123456789",
  "user_id": "user_123",
  "channel_id": "ticket_channel_123",
  "category": "support",
  "status": "open",
  "created_at": "2025-11-01T12:00:00Z"
}
```

---

### 2. Get Ticket

**Endpoint:** `GET /tickets/{ticket_id}`

**Response:**
```json
{
  "id": "ticket_abc123",
  "guild_id": "123456789",
  "user": {
    "id": "user_123",
    "username": "User#1234"
  },
  "status": "open",
  "claimed_by": null,
  "messages_count": 15,
  "created_at": "2025-11-01T12:00:00Z"
}
```

---

### 3. Close Ticket

**Endpoint:** `POST /tickets/{ticket_id}/close`

**Request Body:**
```json
{
  "closer_id": "staff_123",
  "reason": "Issue resolved"
}
```

**Response:**
```json
{
  "id": "ticket_abc123",
  "status": "closed",
  "closed_at": "2025-11-01T14:00:00Z"
}
```

---

### 4. Claim Ticket

**Endpoint:** `POST /tickets/{ticket_id}/claim`

**Request Body:**
```json
{
  "staff_id": "staff_123"
}
```

**Response:**
```json
{
  "id": "ticket_abc123",
  "claimed_by": "staff_123",
  "claimed_at": "2025-11-01T12:30:00Z"
}
```

---

### 5. Get Ticket Transcript

**Endpoint:** `GET /tickets/{ticket_id}/transcript`

**Response:**
```json
{
  "ticket_id": "ticket_abc123",
  "messages": [
    {
      "author_id": "user_123",
      "content": "I need help",
      "timestamp": "2025-11-01T12:05:00Z"
    }
  ],
  "transcript_url": "https://cdn.kingdom77.com/transcripts/ticket_abc123.txt"
}
```

---

### 6. Get Ticket Statistics

**Endpoint:** `GET /guilds/{guild_id}/tickets/stats`

**Response:**
```json
{
  "total_tickets": 500,
  "open_tickets": 15,
  "avg_response_time": 300,
  "avg_resolution_time": 1800
}
```

---

<a id="auto-roles-api"></a>
## 🎭 Auto-Roles API

**7 Endpoints** | Reaction roles, level roles, join roles

### 1. Create Reaction Role

**Endpoint:** `POST /auto-roles/reaction`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "channel_id": "channel_123",
  "message_id": "msg_123",
  "emoji": "🎮",
  "role_id": "role_123",
  "mode": "normal"
}
```

**Response:**
```json
{
  "id": "rr_abc123",
  "guild_id": "123456789",
  "emoji": "🎮",
  "role_id": "role_123",
  "created_at": "2025-11-01T12:00:00Z"
}
```

---

### 2. Add Level Role

**Endpoint:** `POST /auto-roles/level`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "level": 10,
  "role_id": "role_123",
  "remove_previous": false
}
```

**Response:**
```json
{
  "id": "lr_abc123",
  "level": 10,
  "role_id": "role_123"
}
```

---

### 3. Add Join Role

**Endpoint:** `POST /auto-roles/join`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "role_id": "role_123",
  "delay": 0
}
```

**Response:**
```json
{
  "id": "jr_abc123",
  "role_id": "role_123",
  "delay": 0
}
```

---

### 4. List Reaction Roles

**Endpoint:** `GET /guilds/{guild_id}/auto-roles/reaction`

**Response:**
```json
{
  "data": [
    {
      "id": "rr_abc123",
      "emoji": "🎮",
      "role_id": "role_123",
      "message_id": "msg_123"
    }
  ]
}
```

---

### 5. List Level Roles

**Endpoint:** `GET /guilds/{guild_id}/auto-roles/level`

**Response:**
```json
{
  "data": [
    {
      "id": "lr_abc123",
      "level": 10,
      "role_id": "role_123"
    }
  ]
}
```

---

### 6. List Join Roles

**Endpoint:** `GET /guilds/{guild_id}/auto-roles/join`

**Response:**
```json
{
  "data": [
    {
      "id": "jr_abc123",
      "role_id": "role_123",
      "delay": 0
    }
  ]
}
```

---

### 7. Delete Auto-Role

**Endpoint:** `DELETE /auto-roles/{auto_role_id}`

**Response:**
```json
{
  "success": true,
  "message": "Auto-role deleted"
}
```

---

<a id="economy-api"></a>
## 💰 Economy API

**8 Endpoints** | Credits, shop, and games

### 1. Get User Balance

**Endpoint:** `GET /guilds/{guild_id}/users/{user_id}/balance`

**Response:**
```json
{
  "user_id": "user_123",
  "wallet": 5000,
  "bank": 10000,
  "total": 15000,
  "networth": 20000
}
```

---

### 2. Update Balance

**Endpoint:** `POST /guilds/{guild_id}/users/{user_id}/balance`

**Request Body:**
```json
{
  "amount": 100,
  "type": "wallet",
  "reason": "Reward"
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "old_balance": 5000,
  "new_balance": 5100
}
```

---

### 3. Get Shop Items

**Endpoint:** `GET /guilds/{guild_id}/shop`

**Response:**
```json
{
  "items": [
    {
      "id": "item_1",
      "name": "VIP Role",
      "price": 10000,
      "stock": 5
    }
  ]
}
```

---

### 4. Purchase Item

**Endpoint:** `POST /guilds/{guild_id}/shop/purchase`

**Request Body:**
```json
{
  "user_id": "user_123",
  "item_id": "item_1",
  "quantity": 1
}
```

**Response:**
```json
{
  "success": true,
  "item": "VIP Role",
  "cost": 10000,
  "new_balance": 5000
}
```

---

### 5. Get Inventory

**Endpoint:** `GET /guilds/{guild_id}/users/{user_id}/inventory`

**Response:**
```json
{
  "items": [
    {
      "id": "item_1",
      "name": "VIP Role",
      "quantity": 1
    }
  ]
}
```

---

### 6. Daily Claim

**Endpoint:** `POST /guilds/{guild_id}/users/{user_id}/daily`

**Response:**
```json
{
  "amount": 500,
  "streak": 5,
  "next_claim": "2025-11-02T12:00:00Z"
}
```

---

### 7. Weekly Claim

**Endpoint:** `POST /guilds/{guild_id}/users/{user_id}/weekly`

**Response:**
```json
{
  "amount": 5000,
  "next_claim": "2025-11-08T12:00:00Z"
}
```

---

### 8. Transfer Credits

**Endpoint:** `POST /guilds/{guild_id}/transfer`

**Request Body:**
```json
{
  "from_user_id": "user_123",
  "to_user_id": "user_456",
  "amount": 1000
}
```

**Response:**
```json
{
  "success": true,
  "amount": 1000,
  "from_balance": 4000,
  "to_balance": 2000
}
```

---

<a id="premium-api"></a>
## 💎 Premium API

**5 Endpoints** | Premium subscriptions

### 1. Get Premium Status

**Endpoint:** `GET /guilds/{guild_id}/premium`

**Response:**
```json
{
  "guild_id": "123456789",
  "tier": "premium",
  "expires_at": "2025-12-01T12:00:00Z",
  "features": ["xp_boost", "unlimited_tickets"]
}
```

---

### 2. Subscribe

**Endpoint:** `POST /premium/subscribe`

**Request Body:**
```json
{
  "guild_id": "123456789",
  "tier": "premium",
  "payment_method": "stripe_pm_123"
}
```

**Response:**
```json
{
  "subscription_id": "sub_abc123",
  "tier": "premium",
  "status": "active"
}
```

---

### 3. Cancel Subscription

**Endpoint:** `DELETE /premium/subscriptions/{subscription_id}`

**Response:**
```json
{
  "success": true,
  "cancels_at": "2025-12-01T12:00:00Z"
}
```

---

### 4. Get Features

**Endpoint:** `GET /premium/features`

**Response:**
```json
{
  "tiers": {
    "basic": ["xp_boost_1.5x", "custom_cards"],
    "premium": ["xp_boost_2x", "unlimited_tickets", "api_access"]
  }
}
```

---

### 5. Gift Subscription

**Endpoint:** `POST /premium/gift`

**Request Body:**
```json
{
  "from_user_id": "user_123",
  "to_guild_id": "guild_456",
  "tier": "premium",
  "duration_months": 1
}
```

**Response:**
```json
{
  "gift_id": "gift_abc123",
  "redeemed": false
}
```

---

<a id="statistics-api"></a>
## 📊 Statistics API

**3 Endpoints** | Server and bot statistics

### 1. Get Guild Statistics

**Endpoint:** `GET /guilds/{guild_id}/stats`

**Response:**
```json
{
  "guild_id": "123456789",
  "member_count": 5000,
  "online_count": 1200,
  "total_messages": 500000,
  "total_commands": 50000,
  "level_avg": 15
}
```

---

### 2. Get Bot Statistics

**Endpoint:** `GET /stats`

**Response:**
```json
{
  "total_guilds": 1000,
  "total_users": 500000,
  "total_commands": 5000000,
  "uptime": 2592000,
  "ping": 45
}
```

---

### 3. Get Command Usage

**Endpoint:** `GET /guilds/{guild_id}/stats/commands`

**Response:**
```json
{
  "data": [
    {
      "command": "/rank",
      "usage_count": 5000
    }
  ]
}
```

---

<a id="websocket-events"></a>
## 🔌 WebSocket Events

**Endpoint:** `wss://api.kingdom77.com/v1/ws`

### Authentication

Send authentication message after connecting:

```json
{
  "type": "auth",
  "token": "your_jwt_token"
}
```

### Subscribe to Events

```json
{
  "type": "subscribe",
  "events": ["giveaway.created", "application.submitted"]
}
```

### Event Types

**Giveaway Events:**
- `giveaway.created`
- `giveaway.started`
- `giveaway.ended`
- `giveaway.entry`

**Application Events:**
- `application.submitted`
- `application.approved`
- `application.rejected`

**Auto-Message Events:**
- `automessage.triggered`

**Social Events:**
- `social.post`

**Example Event:**
```json
{
  "type": "event",
  "event": "giveaway.ended",
  "data": {
    "id": "giveaway_abc123",
    "winners": ["user_1", "user_2"]
  },
  "timestamp": "2025-11-01T12:00:00Z"
}
```

---

## 📝 SDK Examples

### Python

```python
import requests

BASE_URL = "https://api.kingdom77.com/v1"
TOKEN = "your_jwt_token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Create giveaway
response = requests.post(
    f"{BASE_URL}/giveaways",
    json={
        "guild_id": "123456789",
        "prize": "Discord Nitro",
        "winners": 1,
        "duration": 3600
    },
    headers=headers
)

print(response.json())
```

### JavaScript

```javascript
const BASE_URL = 'https://api.kingdom77.com/v1';
const TOKEN = 'your_jwt_token';

const headers = {
  'Authorization': `Bearer ${TOKEN}`,
  'Content-Type': 'application/json'
};

// Create giveaway
fetch(`${BASE_URL}/giveaways`, {
  method: 'POST',
  headers: headers,
  body: JSON.stringify({
    guild_id: '123456789',
    prize: 'Discord Nitro',
    winners: 1,
    duration: 3600
  })
})
.then(res => res.json())
.then(data => console.log(data));
```

---

## 🔗 Additional Resources

- **API Status:** [status.kingdom77.com](https://status.kingdom77.com)
- **Postman Collection:** [Download](https://api.kingdom77.com/postman)
- **OpenAPI Spec:** [Download](https://api.kingdom77.com/openapi.json)
- **Rate Limit Calculator:** [Tool](https://api.kingdom77.com/rate-limit-calc)

---

**Last Updated:** November 1, 2025  
**Version:** v4.0.0  
**Support:** api-support@kingdom77.com

---

**🎉 Kingdom-77 API - Powering Discord Bots**

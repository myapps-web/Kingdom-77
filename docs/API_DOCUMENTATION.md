# Kingdom-77 Dashboard API Documentation
**RESTful API for Web Dashboard Integration**

## Overview 📋

FastAPI-based REST API providing endpoints for managing:
- **Applications System** - Application forms and submissions
- **Auto-Messages System** - Automated messages with triggers
- **Social Integration** - Social media notifications

---

## Quick Start 🚀

### 1. Installation

```bash
# Install API dependencies
pip install -r requirements-api.txt
```

### 2. Environment Variables

```env
# MongoDB Connection
MONGODB_URI=mongodb://localhost:27017

# API Configuration
DASHBOARD_API_KEY=your_secret_api_key_here
API_PORT=8000

# CORS (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdashboard.com
```

### 3. Run Server

```bash
# Development mode (with auto-reload)
python api_server.py

# Production mode (with Uvicorn)
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

### 4. Access Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## Authentication 🔒

All endpoints (except `/`, `/health`) require API key authentication.

**Header:**
```
X-API-Key: your_secret_api_key_here
```

**Example:**
```bash
curl -H "X-API-Key: your_key" http://localhost:8000/api/applications/guilds/123/forms
```

---

## API Endpoints 🌐

### Applications System (9 endpoints)

#### List Forms
```http
GET /api/applications/guilds/{guild_id}/forms
Query: ?enabled_only=true
```

#### Get Form Details
```http
GET /api/applications/guilds/{guild_id}/forms/{form_id}
```

#### Create Form
```http
POST /api/applications/guilds/{guild_id}/forms
Body: {
  "name": "Staff Application",
  "description": "Apply for staff position",
  "questions": [...],
  "submit_channel_id": "123456",
  "review_channel_id": "789012",
  "accept_role_id": "345678",
  "cooldown_hours": 24,
  "max_submissions": 1
}
Query: ?creator_id=user_id
```

#### Update Form
```http
PUT /api/applications/guilds/{guild_id}/forms/{form_id}
Body: {
  "name": "Updated Name",
  "cooldown_hours": 48
}
```

#### Delete Form
```http
DELETE /api/applications/guilds/{guild_id}/forms/{form_id}
```

#### Toggle Form
```http
PATCH /api/applications/guilds/{guild_id}/forms/{form_id}/toggle
```

#### List Submissions
```http
GET /api/applications/guilds/{guild_id}/submissions
Query: ?form_id=abc123&status=pending&limit=50
```

#### Review Submission
```http
PATCH /api/applications/submissions/{submission_id}/review
Body: {
  "action": "accept",  // or "reject"
  "reason": "Optional reason"
}
Query: ?reviewer_id=user_id
```

#### Get Statistics
```http
GET /api/applications/guilds/{guild_id}/stats
```

---

### Auto-Messages System (9 endpoints)

#### List Messages
```http
GET /api/automessages/guilds/{guild_id}/messages
Query: ?trigger_type=keyword&enabled_only=true
```

#### Get Message Details
```http
GET /api/automessages/guilds/{guild_id}/messages/{message_id}
```

#### Create Message
```http
POST /api/automessages/guilds/{guild_id}/messages
Body: {
  "name": "Welcome Message",
  "trigger_type": "keyword",
  "trigger_value": "hello",
  "response_type": "text",
  "response_content": "Hello! Welcome!",
  "embed": {...},
  "buttons": [...],
  "allowed_roles": ["123", "456"],
  "allowed_channels": ["789"]
}
Query: ?creator_id=user_id
```

#### Update Message
```http
PUT /api/automessages/guilds/{guild_id}/messages/{message_id}
Body: {
  "trigger_value": "hi",
  "response_content": "Hi there!"
}
```

#### Delete Message
```http
DELETE /api/automessages/guilds/{guild_id}/messages/{message_id}
```

#### Toggle Message
```http
PATCH /api/automessages/guilds/{guild_id}/messages/{message_id}/toggle
```

#### Get Settings
```http
GET /api/automessages/guilds/{guild_id}/settings
```

#### Update Settings
```http
PUT /api/automessages/guilds/{guild_id}/settings
Body: {
  "cooldown_seconds": 10,
  "auto_delete_seconds": 30,
  "dm_response": false,
  "case_sensitive": true,
  "exact_match": false
}
```

#### Get Statistics
```http
GET /api/automessages/guilds/{guild_id}/stats
```

---

### Social Integration System (10 endpoints)

#### List Links
```http
GET /api/social/guilds/{guild_id}/links
Query: ?platform=youtube&enabled_only=true
```

#### Get Link Details
```http
GET /api/social/guilds/{guild_id}/links/{link_id}
```

#### Create Link
```http
POST /api/social/guilds/{guild_id}/links
Body: {
  "platform": "youtube",
  "channel_url": "https://youtube.com/@username",
  "channel_id": "UC...",
  "notification_channel_id": "123456",
  "mention_role_id": "789012"
}
Query: ?user_id=user_id
```

#### Update Link
```http
PUT /api/social/guilds/{guild_id}/links/{link_id}
Body: {
  "notification_channel_id": "new_channel_id",
  "mention_role_id": "new_role_id"
}
```

#### Delete Link
```http
DELETE /api/social/guilds/{guild_id}/links/{link_id}
```

#### Toggle Link
```http
PATCH /api/social/guilds/{guild_id}/links/{link_id}/toggle
```

#### Get Posts
```http
GET /api/social/guilds/{guild_id}/posts
Query: ?link_id=abc123&limit=50
```

#### Get Limits
```http
GET /api/social/guilds/{guild_id}/limits
```

#### Purchase Link
```http
POST /api/social/guilds/{guild_id}/purchase
Query: ?user_id=user_id
```

#### Get Statistics
```http
GET /api/social/guilds/{guild_id}/stats
```

---

## Response Format 📦

### Success Response
```json
{
  "success": true,
  "data": {...} | [...],
  "message": "Optional message"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized (invalid API key)
- `404` - Not Found
- `500` - Internal Server Error

---

## Example Usage (JavaScript/TypeScript) 💻

### Fetch API
```javascript
const API_KEY = 'your_api_key';
const BASE_URL = 'http://localhost:8000';

async function getForms(guildId) {
  const response = await fetch(
    `${BASE_URL}/api/applications/guilds/${guildId}/forms`,
    {
      headers: {
        'X-API-Key': API_KEY
      }
    }
  );
  
  const data = await response.json();
  return data.data; // Array of forms
}

async function createForm(guildId, creatorId, formData) {
  const response = await fetch(
    `${BASE_URL}/api/applications/guilds/${guildId}/forms?creator_id=${creatorId}`,
    {
      method: 'POST',
      headers: {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    }
  );
  
  return await response.json();
}
```

### Axios
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'X-API-Key': 'your_api_key'
  }
});

// Get forms
const forms = await api.get(`/api/applications/guilds/${guildId}/forms`);

// Create message
const result = await api.post(
  `/api/automessages/guilds/${guildId}/messages`,
  messageData,
  { params: { creator_id: userId } }
);

// Toggle link
const toggle = await api.patch(
  `/api/social/guilds/${guildId}/links/${linkId}/toggle`
);
```

---

## Statistics Examples 📊

### Applications Statistics
```json
{
  "guild_id": "123456",
  "forms": {
    "total": 5,
    "active": 3,
    "inactive": 2
  },
  "submissions": {
    "total": 150,
    "pending": 25,
    "accepted": 100,
    "rejected": 25
  },
  "acceptance_rate": 66.67,
  "forms_details": [...]
}
```

### Auto-Messages Statistics
```json
{
  "guild_id": "123456",
  "messages": {
    "total": 20,
    "active": 18,
    "inactive": 2
  },
  "by_trigger_type": {
    "keyword": 12,
    "button": 5,
    "dropdown": 3
  },
  "total_triggers": 5432,
  "top_messages": [
    {
      "message_id": "abc123",
      "name": "Welcome",
      "triggers": 1234
    }
  ]
}
```

### Social Integration Statistics
```json
{
  "guild_id": "123456",
  "links": {
    "total": 8,
    "active": 7,
    "inactive": 1
  },
  "by_platform": {
    "youtube": {
      "name": "YouTube",
      "emoji": "🎥",
      "count": 3,
      "notifications": 245
    },
    "snapchat": {
      "name": "Snapchat",
      "emoji": "👻",
      "count": 2,
      "notifications": 89
    }
  },
  "total_notifications": 678
}
```

---

## Deployment 🚀

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY api/ ./api/
COPY api_server.py .

EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017
      - DASHBOARD_API_KEY=${API_KEY}
      - ALLOWED_ORIGINS=http://localhost:3000
    depends_on:
      - mongo
  
  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

### Systemd Service
```ini
[Unit]
Description=Kingdom-77 Dashboard API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/kingdom77
Environment="PATH=/opt/kingdom77/venv/bin"
ExecStart=/opt/kingdom77/venv/bin/uvicorn api_server:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## Security Best Practices 🔒

1. **API Key Management**
   - Store API key in environment variables
   - Never commit API key to version control
   - Rotate keys regularly
   - Use different keys for dev/prod

2. **CORS Configuration**
   - Restrict origins to your dashboard domain only
   - Don't use `*` in production

3. **Rate Limiting** (TODO)
   - Implement rate limiting for production
   - Recommended: 100 requests/minute per IP

4. **HTTPS**
   - Always use HTTPS in production
   - Use reverse proxy (nginx/Apache) with SSL

5. **MongoDB Security**
   - Use authentication
   - Restrict network access
   - Regular backups

---

## Testing 🧪

### Manual Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Get forms
curl -H "X-API-Key: your_key" \
  http://localhost:8000/api/applications/guilds/123/forms

# Create form
curl -X POST \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Form","description":"Test","questions":[]}' \
  "http://localhost:8000/api/applications/guilds/123/forms?creator_id=456"

# Toggle message
curl -X PATCH \
  -H "X-API-Key: your_key" \
  http://localhost:8000/api/automessages/guilds/123/messages/abc/toggle
```

### Automated Testing (TODO)
```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from api_server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

---

## Troubleshooting 🔧

### API Key Issues
```
Error: 401 Unauthorized
```
- Check `X-API-Key` header is present
- Verify API key matches `DASHBOARD_API_KEY` env variable
- Ensure no extra spaces in key

### CORS Issues
```
Error: CORS policy blocked
```
- Add your frontend URL to `ALLOWED_ORIGINS`
- Format: `http://localhost:3000,https://yourdomain.com`
- No trailing slashes

### MongoDB Connection
```
Error: MongoDB not connected
```
- Verify `MONGODB_URI` is correct
- Check MongoDB is running: `mongosh`
- Test connection: `mongo <uri>`

### Import Errors
```
Error: Module not found
```
- Install dependencies: `pip install -r requirements-api.txt`
- Check Python version: `python --version` (3.11+ recommended)

---

## Performance Tips ⚡

1. **Indexing**
   - Create indexes on frequently queried fields:
     ```javascript
     db.application_forms.createIndex({ "guild_id": 1 })
     db.auto_messages.createIndex({ "guild_id": 1, "enabled": 1 })
     db.social_links.createIndex({ "guild_id": 1, "platform": 1 })
     ```

2. **Pagination**
   - Use `limit` parameter for large datasets
   - Default limits: 50 items

3. **Caching** (TODO)
   - Implement Redis caching for read-heavy endpoints
   - Cache guild statistics for 5 minutes

4. **Connection Pooling**
   - Motor handles connection pooling automatically
   - Default pool size: 100 connections

---

## Roadmap 🗺️

- [ ] Rate limiting middleware
- [ ] Request/response logging
- [ ] Redis caching layer
- [ ] Webhook events
- [ ] Pagination helpers
- [ ] GraphQL endpoint
- [ ] WebSocket support for real-time updates
- [ ] API versioning (v2)
- [ ] Automated tests
- [ ] Performance monitoring

---

## Support 💬

- **Documentation:** http://localhost:8000/docs
- **GitHub Issues:** [Repository URL]
- **Discord Support:** [Server Invite]

---

**Kingdom-77 Dashboard API v4.0.0**  
*Built with FastAPI, Motor, and ❤️*

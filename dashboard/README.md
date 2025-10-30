# Kingdom-77 Dashboard Backend

FastAPI-based REST API for the Kingdom-77 Discord Bot web dashboard.

## 🚀 Features

- **Discord OAuth2 Authentication** - Secure login with Discord
- **Server Management** - View and manage all bot servers
- **Statistics Dashboard** - Real-time stats for leveling, moderation, tickets
- **Settings Management** - Configure bot settings per server
- **RESTful API** - Clean API design with comprehensive documentation

## 📋 Requirements

- Python 3.11+
- MongoDB Atlas
- Redis (Upstash)
- Discord Bot Application (for OAuth2)

## 🔧 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp ../.env .env

# Add Discord OAuth2 credentials to .env
DISCORD_CLIENT_ID=your_client_id
DISCORD_CLIENT_SECRET=your_client_secret
DISCORD_REDIRECT_URI=http://localhost:3000/auth/callback
JWT_SECRET=your_secret_key_here
```

## 🏃 Running the Server

```bash
# Development mode with auto-reload
python -m dashboard.main

# Or using uvicorn directly
uvicorn dashboard.main:app --reload --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 📚 API Endpoints

### Authentication
- `GET /api/auth/login-url` - Get Discord OAuth2 login URL
- `POST /api/auth/login` - Login with OAuth2 code
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Servers
- `GET /api/servers` - Get user's servers
- `GET /api/servers/{guild_id}` - Get specific server
- `GET /api/servers/{guild_id}/settings` - Get server settings
- `PUT /api/servers/{guild_id}/settings` - Update server settings

### Statistics
- `GET /api/stats/{guild_id}/overview` - Server overview
- `GET /api/stats/{guild_id}/leveling` - Leveling stats
- `GET /api/stats/{guild_id}/moderation` - Moderation stats
- `GET /api/stats/{guild_id}/tickets` - Ticket stats

### Moderation
- `GET /api/moderation/{guild_id}/logs` - Get moderation logs
- `GET /api/moderation/{guild_id}/warnings/{user_id}` - Get user warnings
- `DELETE /api/moderation/{guild_id}/warnings/{warning_id}` - Delete warning

### Leveling
- `GET /api/leveling/{guild_id}/leaderboard` - Get leaderboard
- `GET /api/leveling/{guild_id}/user/{user_id}` - Get user level
- `GET /api/leveling/{guild_id}/rewards` - Get role rewards
- `POST /api/leveling/{guild_id}/rewards` - Add role reward
- `DELETE /api/leveling/{guild_id}/rewards/{level}` - Delete reward

### Tickets
- `GET /api/tickets/{guild_id}/tickets` - Get tickets
- `GET /api/tickets/{guild_id}/tickets/{ticket_id}` - Get specific ticket

### Settings
- `GET /api/settings/{guild_id}` - Get all settings
- `PUT /api/settings/{guild_id}` - Update settings
- `POST /api/settings/{guild_id}/reset` - Reset to defaults

## 🔒 Authentication

All endpoints (except `/api/auth/login-url` and `/api/auth/login`) require authentication using Bearer tokens:

```bash
Authorization: Bearer <your_jwt_token>
```

## 📊 Response Format

Success response:
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {...}
}
```

Error response:
```json
{
  "success": false,
  "error": "Error type",
  "message": "Error description",
  "status_code": 400
}
```

## 🛠️ Development

### Project Structure
```
dashboard/
├── api/           # API endpoints
├── models/        # Pydantic models
├── utils/         # Utilities (auth, discord, database)
├── main.py        # FastAPI app
├── config.py      # Configuration
└── requirements.txt
```

### Adding New Endpoints

1. Create new router in `api/` directory
2. Import and register in `main.py`
3. Add models in `models/` if needed
4. Test with `/api/docs`

## 📝 Environment Variables

```env
# Discord OAuth2
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=
DISCORD_REDIRECT_URI=http://localhost:3000/auth/callback
DISCORD_BOT_TOKEN=

# JWT
JWT_SECRET=your-secret-key-change-in-production

# MongoDB
MONGODB_URI=mongodb+srv://...
MONGODB_DB=kingdom77

# Redis
REDIS_URL=redis://...

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

## 🚀 Deployment

### Using Docker
```bash
docker build -t kingdom77-api .
docker run -p 8000:8000 --env-file .env kingdom77-api
```

### Using Render/Railway/Fly.io
1. Push code to GitHub
2. Connect repository
3. Set environment variables
4. Deploy!

## 📄 License

Part of Kingdom-77 Bot v3.6

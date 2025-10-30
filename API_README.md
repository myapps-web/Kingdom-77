# Kingdom-77 Dashboard API 🚀

RESTful API server for Kingdom-77 Discord Bot web dashboard integration.

## Features ✨

- **Applications Management** - CRUD operations for application forms and submissions
- **Auto-Messages Management** - Manage automated messages with triggers
- **Social Integration Management** - Control social media notifications
- **FastAPI Framework** - Modern, fast Python web framework
- **Async MongoDB** - Motor driver for high-performance database operations
- **API Key Authentication** - Secure access control
- **Auto-Generated Docs** - Swagger UI and ReDoc
- **CORS Support** - Cross-origin requests for web dashboard

## Quick Start 🏃

### 1. Install Dependencies

```bash
pip install -r requirements-api.txt
```

### 2. Configure Environment

```bash
# .env
MONGODB_URI=mongodb://localhost:27017
DASHBOARD_API_KEY=your_secret_key
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
```

### 3. Run Server

```bash
# Development
python api_server.py

# Production
uvicorn api_server:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Overview 📚

### Applications System (9 endpoints)
- List/Create/Update/Delete forms
- List/Review submissions
- Statistics

### Auto-Messages System (9 endpoints)
- List/Create/Update/Delete messages
- Settings management
- Statistics

### Social Integration (10 endpoints)
- List/Create/Update/Delete social links
- Purchase additional links
- Posts history
- Statistics

**Total: 28 REST endpoints**

## Authentication 🔒

All endpoints require API key in header:

```bash
curl -H "X-API-Key: your_key" http://localhost:8000/api/applications/guilds/123/forms
```

## Example Request 💻

```javascript
const response = await fetch(
  'http://localhost:8000/api/social/guilds/123/links',
  {
    headers: {
      'X-API-Key': 'your_api_key'
    }
  }
);

const data = await response.json();
console.log(data.data); // Array of social links
```

## Deployment 🚀

### Docker
```bash
docker build -t kingdom77-api .
docker run -p 8000:8000 -e MONGODB_URI=... kingdom77-api
```

### Systemd
See [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) for systemd service setup.

## Documentation 📖

Full API documentation: [API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

## Tech Stack 🛠️

- **FastAPI** - Modern Python web framework
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server

## License

MIT License - Kingdom-77 Bot v4.0.0

"""
Kingdom-77 Dashboard - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Kingdom-77 Dashboard API",
    description="RESTful API for Kingdom-77 Discord Bot Dashboard",
    version="3.9.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
origins = [
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:3001",
    os.getenv("FRONTEND_URL", "http://localhost:3000")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from .api import auth, servers, stats, moderation, leveling, tickets, settings, premium, level_cards, emails, credits, shop

# Register routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(servers.router, prefix="/api/servers", tags=["Servers"])
app.include_router(stats.router, prefix="/api/stats", tags=["Statistics"])
app.include_router(moderation.router, prefix="/api/moderation", tags=["Moderation"])
app.include_router(leveling.router, prefix="/api/leveling", tags=["Leveling"])
app.include_router(tickets.router, prefix="/api/tickets", tags=["Tickets"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])
app.include_router(premium.router, prefix="/api/premium", tags=["Premium"])
app.include_router(level_cards.router, prefix="/api/level-cards", tags=["Level Cards"])
app.include_router(emails.router, prefix="/api/emails", tags=["Email Notifications"])
app.include_router(credits.router, tags=["Credits"])
app.include_router(shop.router, tags=["Shop"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Kingdom-77 Dashboard API",
        "version": "3.9.0",
        "status": "online",
        "docs": "/api/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "3.6.0"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "dashboard.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

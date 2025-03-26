# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.session_handler import router as session_router
from app.config import settings
from app.core.database import engine, Base
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Successfully created database tables")
except Exception as e:
    logger.error(f"Error creating tables: {e}")

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(session_router, prefix="/api", tags=["HRV Sessions"])

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to the HRV Metrics API",
        "version": settings.API_VERSION,
        "docs": "/docs"
    }

# Debug endpoint to check environment
@app.get("/debug", tags=["Debug"])
async def debug():
    """Endpoint for debugging deployment issues"""
    return {
        "database_url": settings.DATABASE_URL.replace(
            # Hide password in response
            settings.DATABASE_URL.split("@")[0].split(":")[-1],
            "********"
        ),
        "debug_mode": settings.DEBUG,
        "api_version": settings.API_VERSION
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
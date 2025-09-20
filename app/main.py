from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.api.v1.api import api_router
from app.core.config import get_settings
from app.core.database import engine, async_engine
from app.models.models import Base
from app.core.middleware import (
    add_cors_middleware, 
    add_compression_middleware, 
    add_custom_middleware,
    limiter,
    rate_limit_handler
)
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import asyncio
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create database tables (sync for initial setup)
Base.metadata.create_all(bind=engine)

# Async database initialization
async def init_async_db():
    """Initialize async database"""
    try:
        async with async_engine.begin() as conn:
            # Create tables if they don't exist
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Async database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize async database: {e}")

# Create FastAPI app with optimized settings
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="High-performance FastAPI backend optimized for 1000+ concurrent users",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    # Performance optimizations
    generate_unique_id_function=lambda route: f"{route.tags[0]}-{route.name}" if route.tags else route.name
)

# Add all middleware in correct order (order matters!)
# 1. CORS - must be first
add_cors_middleware(app)

# 2. Compression - after CORS
add_compression_middleware(app)

# 3. Custom middleware
add_custom_middleware(app)

# 4. Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    await init_async_db()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application")
    await async_engine.dispose()
    logger.info("Application shutdown complete")

@app.get("/")
async def root(request: Request):
    """Root endpoint with performance info"""
    return {
        "message": "FastAPI Backend is running! - Optimized for 1000+ users",
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "healthy",
        "features": [
            "Async/Await support",
            "Database indexing", 
            "Rate limiting",
            "Security headers",
            "Compression",
            "Performance monitoring"
        ]
    }

@app.get("/health")
async def health_check(request: Request):
    """Enhanced health check with database connectivity"""
    try:
        # Test database connectivity
        from app.core.database import get_async_db
        async for db in get_async_db():
            # Simple query to test connection
            await db.execute(text("SELECT 1"))
            break
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": settings.VERSION,
            "timestamp": "2025-09-20T09:38:00Z"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected", 
                "error": str(e)
            }
        )

@app.get("/metrics")
async def get_metrics(request: Request):
    """Basic performance metrics"""
    return {
        "total_requests": getattr(app.state, 'total_requests', 0),
        "active_connections": getattr(app.state, 'active_connections', 0),
        "cache_hits": getattr(app.state, 'cache_hits', 0),
        "database_queries": getattr(app.state, 'db_queries', 0)
    }
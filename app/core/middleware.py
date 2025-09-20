from typing import Callable
import time
import asyncio
from functools import wraps
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security import HTTPBearer
from fastapi import HTTPException, status
from app.core.config import get_settings
import logging
import json

# Try to import redis, but don't crash if not available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

settings = get_settings()
logger = logging.getLogger(__name__)

# Rate Limiter Setup
limiter = Limiter(key_func=get_remote_address)

# Redis Connection for Caching (optional - falls back to memory)
redis_client = None
if REDIS_AVAILABLE:
    try:
        redis_client = redis.Redis.from_url("redis://localhost:6379", decode_responses=True)
    except Exception as e:
        redis_client = None
        logger.warning(f"Redis not available: {e}")
else:
    logger.warning("Redis package not installed, caching disabled")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # Updated CSP to allow Swagger UI external resources including source maps
        csp = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' https://cdn.jsdelivr.net"
        )
        response.headers["Content-Security-Policy"] = csp
        
        # Cache Control for API responses
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Add performance monitoring and optimization"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Add request ID for tracking
        request_id = f"{int(time.time() * 1000000)}"
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            
            # Log slow requests (> 1 second)
            if process_time > 1.0:
                logger.warning(f"Slow request: {request.method} {request.url.path} took {process_time:.2f}s")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.url.path} after {process_time:.2f}s - {str(e)}")
            raise

class DatabaseConnectionMiddleware(BaseHTTPMiddleware):
    """Optimize database connections"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Set connection pool limits based on request load
        if hasattr(request.state, 'db_pool_size'):
            request.state.db_pool_size = min(20, request.state.db_pool_size + 1)
        else:
            request.state.db_pool_size = 1
            
        response = await call_next(request)
        return response

# Authentication helpers
security = HTTPBearer()

def require_auth(func):
    """Decorator to require authentication for endpoints"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # This would integrate with your auth system
        # For now, it's a placeholder
        return await func(*args, **kwargs)
    return wrapper

# Custom Exception Handlers
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit exceeded handler"""
    response = JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": f"Too many requests. Limit: {exc.detail}",
            "retry_after": 60
        }
    )
    response.headers["Retry-After"] = "60"
    return response

# Middleware Configuration Functions
def add_cors_middleware(app):
    """Add CORS middleware with optimized settings"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
        max_age=86400,  # Cache preflight for 24 hours
    )

def add_compression_middleware(app):
    """Add compression middleware for better performance"""
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,  # Only compress responses > 1KB
        compresslevel=6     # Balance between compression and speed
    )

def add_custom_middleware(app):
    """Add all custom middleware"""
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(PerformanceMiddleware)
    app.add_middleware(DatabaseConnectionMiddleware)

# Rate limiting decorators for endpoints
def rate_limit_per_minute(requests: int = 100):
    """Rate limit decorator for endpoints"""
    return limiter.limit(f"{requests}/minute")

def rate_limit_per_hour(requests: int = 1000):
    """Rate limit decorator for endpoints"""
    return limiter.limit(f"{requests}/hour")

# Cache decorator for expensive operations
def cache_response(ttl: int = 300):
    """Cache response decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if redis_client:
                # Generate cache key
                cache_key = f"cache:{func.__name__}:{hash(str(args) + str(kwargs))}"
                
                try:
                    # Try to get from cache
                    cached = await redis_client.get(cache_key)
                    if cached:
                        return json.loads(cached)  # Safe JSON deserialization
                except Exception as e:
                    logger.debug(f"Cache read failed: {e}")
                
                # Get fresh data
                result = await func(*args, **kwargs)
                
                try:
                    # Cache the result safely
                    await redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
                except Exception as e:
                    logger.debug(f"Cache write failed: {e}")
                
                return result
            else:
                # No caching available
                return await func(*args, **kwargs)
        return wrapper
    return decorator
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from app.core.config import get_settings

settings = get_settings()
import asyncio

# Sync engine for compatibility
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Only needed for SQLite
    pool_pre_ping=True,  # Validate connections
    pool_recycle=300,  # Recycle connections every 5 minutes
)

# Async engine for performance
async_engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False,  # Set to True for SQL debugging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    autocommit=False, 
    autoflush=False
)

def get_db():
    """Sync database session - for compatibility"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """Async database session - for performance"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
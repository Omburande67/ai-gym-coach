"""Pytest configuration and fixtures"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.main import app
from app.models.user import Base

# Create test database engine
# Convert postgresql:// to postgresql+asyncpg://
test_database_url = settings.DATABASE_TEST_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

test_engine = create_async_engine(
    test_database_url,
    poolclass=NullPool,
    echo=False,
)

TestingSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest_asyncio.fixture
async def db_session():
    """Create a test database session"""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.rollback()
        finally:
            await session.close()
    
    # Drop tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


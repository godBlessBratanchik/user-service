import pytest
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db import Base
from app.models import Profile

# Для тестирования используем SQLite в памяти вместо PostgreSQL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def test_engine():
    """Создание тестового engine с БД в памяти"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
async def test_session(test_engine):
    """Создание тестовой сессии"""
    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False
    )
    
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture
def any_profile_data():
    """Фикстура с тестовыми данными профиля"""
    return {
        "user_id": "user_123",
        "full_name": "John Doe",
        "email": "john@example.com",
        "avatar_url": "https://example.com/avatar.jpg",
        "bio": "Test bio"
    }

@pytest.fixture
def another_profile_data():
    """Вторая фикстура с тестовыми данными"""
    return {
        "user_id": "user_456",
        "full_name": "Jane Smith",
        "email": "jane@example.com",
        "avatar_url": "https://example.com/avatar2.jpg",
        "bio": "Another bio"
    }

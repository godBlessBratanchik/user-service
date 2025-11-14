import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

DATABASE_URL = os.getenv(
    "PROFILE_DATABASE_URL",
    "postgresql+asyncpg://postgres:123@95.165.27.159:5433/user_db"
)

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
SessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

class Base(MappedAsDataclass, DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

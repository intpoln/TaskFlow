from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from src.config import settings

engine = create_async_engine(settings.DB_URI)
engine_null_pool = create_async_engine(settings.DB_URI, poolclass=NullPool)

async_session_maker = async_sessionmaker(
    bind=engine_null_pool, class_=AsyncSession, expire_on_commit=False
)
async_session_maker_null_pool = async_sessionmaker(
    bind=engine_null_pool, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

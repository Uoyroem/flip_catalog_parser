from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .config import settings

async_engine = create_async_engine(
    settings.postgres_dsn, echo=settings.mode == "development"
)
AsyncSession = async_sessionmaker(async_engine, expire_on_commit=True)

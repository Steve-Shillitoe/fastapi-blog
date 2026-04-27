from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
import os
from config import settings


# Load the database URL from the environment variable
#SQLALCHEMY_DATABASE_URL = os.getenv(
 #   "DATABASE_URL",
 #   "postgresql+asyncpg://postgres:pgAdmin@localhost:5433/blogdb"  # fallback for dev
#)

engine = create_async_engine(settings.database_url) # engine is the connection to the database

# SessionLocal is a factory that creates database sessions.
# A session is a transaction with the database
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
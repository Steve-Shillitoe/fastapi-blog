from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

#SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"  # blog.db is the database file
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:pgAdmin@localhost:5433/blogdb"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)   # engine is the connection to the database

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
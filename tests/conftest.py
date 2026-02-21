import asyncio
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import ASGITransport
from main import app
from database import Base, get_db

# -----------------------------
# 1️⃣ Define a separate test DB
# -----------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create async engine for test DB
# NullPool avoids SQLite locking issues during async tests
engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)

# Create session factory for test database
TestingSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,  # Prevent objects from expiring after commit
)

# ---------------------------------------------------
# 2️⃣ Create tables before tests and drop after tests
# ---------------------------------------------------
@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_test_db():
    # Create all tables at start of test session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # Run tests here

    # Drop all tables after test session ends
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------
# 3️⃣ Override FastAPI DB dependency with test DB
# ---------------------------------------------------
async def override_get_db():
    # Provide test session instead of real DB session
    async with TestingSessionLocal() as session:
        yield session


# Tell FastAPI to use test DB instead of production DB
app.dependency_overrides[get_db] = override_get_db


# ---------------------------------------------------
# 4️⃣ Create reusable async test client
# ---------------------------------------------------
@pytest_asyncio.fixture
async def client():
    # ASGITransport allows calling FastAPI app without running server
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test"
    ) as ac:
        yield ac  # Provide client to tests
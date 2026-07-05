from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from app.database import Base, get_db
from app.main import app

pytest_plugins = ('pytest_asyncio',)

TEST_DATABASE_URL = 'sqlite+aiosqlite:///:memory:'

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    echo=False
)
AsyncSessionTesting = async_sessionmaker(
    bind=engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    """
    Автоматическое создание и удаление
    таблиц тестовой БД.
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Подменяем реальную сессию БД на тестовую"""
    async with AsyncSessionTesting() as session:
        yield session


@pytest.fixture
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура тестового клиента для отправки HTTP-запросов к FastAPI"""
    app.dependency_overrides[get_db] = lambda: override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://test'
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

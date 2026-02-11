from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (create_async_engine,
                                    async_sessionmaker,
                                    AsyncSession)
from app.main import app
from app.database import get_async_session as main_session
from app.models import Base
from tests.add_data_from_db import insert_data

test_db_url = "postgresql+asyncpg://test:test@172.18.0.1:5432/testing"

test_engine = create_async_engine(test_db_url, poolclass=NullPool, echo=False)
test_async_session = async_sessionmaker(
    bind=test_engine, class_=AsyncSession, expire_on_commit=False
)


async def override_get_async_session():
    async with test_async_session() as session:
        yield session


app.dependency_overrides[main_session] = override_get_async_session


@pytest_asyncio.fixture(autouse=True, scope="session")
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await insert_data(conn)
        await conn.commit()
    yield


@pytest_asyncio.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test", ) as async_test_client:
        yield async_test_client

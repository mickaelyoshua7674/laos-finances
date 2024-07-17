from httpx import AsyncClient, ASGITransport
import pytest_asyncio
import pytest

from ..database import asyncEngine
from ..main import app

@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True) as ac:
        yield ac

@pytest_asyncio.fixture(scope="session")
async def conn():
    async with asyncEngine.connect() as conn:
        yield conn

@pytest.fixture
def register_user():
    return {"email":"test@test.com", "name":"test", "password":"0000"}
@pytest.fixture
def login_user():
    return {"username":"test@test.com", "password":"0000"}
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from ..main import app
import pytest

@pytest.mark.asyncio
async def test_register(my_engine):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/register", json={"email":"mycr@laos.com", "name":"mycr", "password":"0000"})
    assert response.status_code == 200
    async with my_engine.connect() as conn:
        res = await conn.execute(text("SELECT userid FROM users WHERE CTID = (SELECT MAX(CTID) FROM recurso);"))
    assert response.json()["userid"] == str(res.fetchone()[0])
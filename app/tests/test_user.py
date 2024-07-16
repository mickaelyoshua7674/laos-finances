from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from ..auth import hashPasword
from ..models import User
from ..main import app
import pytest

user_test_register = {"email":"test@test.com", "name":"test", "password":"0000"}
user_test_login = {"username":"test@test.com", "password":"0000"}

@pytest.mark.asyncio
async def test_register(my_engine):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/register", json=user_test_register)

    async with my_engine.connect() as conn:
        res = await conn.execute(text("SELECT userid FROM users WHERE CTID = (SELECT MAX(CTID) FROM users);"))
        userid = str(res.fetchone()[0])
        await conn.execute(text(f"DELETE FROM users WHERE userid='{userid}';"))
        await conn.commit()

    assert response.status_code == 200
    assert response.json()["userid"] == userid

@pytest.mark.asyncio
async def test_login(my_engine):
    async with my_engine.connect() as conn:
        user_test_register["password"] = await hashPasword(user_test_register["password"])
        res = await conn.execute(User.getInsertScript(), user_test_register)
        await conn.commit()
        userid = str(res.fetchone()[0])
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/login", data=user_test_login)
        print(response.json())
    finally:
        async with my_engine.connect() as conn:
            await conn.execute(text(f"DELETE FROM users WHERE userid='{userid}';"))
            await conn.commit()

    assert response.status_code == 200
    assert response.json()["userid"] == userid
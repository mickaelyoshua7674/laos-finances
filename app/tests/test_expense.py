from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from os import environ
import pytest
import time
import jwt

from .conftest import create_user, delete_user, get_last_insert
from ..database import asyncEngine
from ..main import app

SECRET_KEY = environ["SECRET_KEY"]
ALGORITHM = environ["ALGORITHM"]

def get_cookie(userid):
    return {"access_token":f"Bearer {jwt.encode({"userid":str(userid), "expires":time.time() + 60}, SECRET_KEY, algorithm=ALGORITHM)}"}
test_expense = {"userid": "",
                "idFrequencyType": 3,
                "idExpenseSubCategory": 3,
                "value": 1000,
                "expenseDate": "2024-07-13"}

@pytest.mark.asyncio
async def test_add_expense():
    userid = await create_user()
    try:
        test_expense["userid"] = userid
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True, cookies=get_cookie(userid)) as ac:
            response = await ac.post("/expenses", json=test_expense)
        id = await get_last_insert(column="id", table="fato_expense")
        async with asyncEngine.connect() as conn:
            await conn.execute(text(f"DELETE FROM fato_expense WHERE id={id};"))
            await conn.commit()
    finally:
        await delete_user(userid)
    
    assert response.status_code == 200
    assert response.json() == dict({"id":id}, **test_expense)
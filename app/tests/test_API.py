from httpx import AsyncClient
from sqlalchemy import text
from os import environ
import pytest
import time
import jwt

SECRET_KEY = environ["SECRET_KEY"]
ALGORITHM = environ["ALGORITHM"]

async def get_userid(conn, register_user) -> str:
    res = await conn.execute(text(f"SELECT userid FROM users WHERE username='{register_user["username"]}';"))
    return str(res.fetchone()[0])
async def remove_user(conn, register_user):
    await conn.execute(text(f"DELETE FROM users WHERE username='{register_user["username"]}';"))
    await conn.commit()

def get_cookie(userid):
    return {"access_token":f"Bearer {jwt.encode({"userid":str(userid), "expires":time.time() + 60}, SECRET_KEY, algorithm=ALGORITHM)}"}
async def get_expenseid(conn, userid):
    res = await conn.execute(text(f"SELECT id FROM fato_expense WHERE userid='{userid}';"))
    return res.fetchone()[0]
async def remove_expense(conn, id):
    await conn.execute(text(f"DELETE FROM fato_expense WHERE id='{id}';"))
    await conn.commit()

################################### TESTS DATABASE ###################################
@pytest.mark.asyncio
@pytest.mark.dependency()
async def test_connection(conn):
    res = await conn.execute(text("SELECT 1;"))
    assert res.fetchone()[0] == 1, "Somenthing went wrong witch connection"

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_connection"])
async def test_database_exists(conn):
    dbName = environ["DB_NAME"]
    res = await conn.execute(text(f"SELECT datname FROM pg_database WHERE datname='{dbName}';"))
    assert res.fetchone()[0] == dbName, "Database not found"

################################### TESTS USER ###################################
@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_database_exists"])
async def test_register(client_kwargs, conn, register_user):
    async with AsyncClient(**client_kwargs()) as ac:
        response = await ac.post("/register", json=register_user)

    assert response.json()["userid"] == await get_userid(conn, register_user)
    assert response.status_code == 200

    await remove_user(conn, register_user)

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_register"])
async def test_login(client_kwargs, conn, register_user, login_user):
    async with AsyncClient(**client_kwargs()) as ac:
        await ac.post("/register", json=register_user)
        res_login = await ac.post("/login", data=login_user)
        print(res_login.json())

    assert res_login.json()["userid"] == await get_userid(conn, register_user)
    assert res_login.status_code == 200

    await remove_user(conn, register_user)

################################### TESTS EXPENSES ###################################
@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_register"])
async def test_add_expense(client_kwargs, conn, register_user, add_expense):
    async with AsyncClient(**client_kwargs()) as ac:
        res_register = await ac.post("/register", json=register_user)
    userid = res_register.json()["userid"]
    add_expense["userid"] = userid

    async with AsyncClient(**client_kwargs(get_cookie(userid))) as ac:
        res_add = await ac.post("/expenses", json=add_expense)
    id = await get_expenseid(conn, userid)

    assert res_add.json()["id"] == id
    res_add.status_code == 200

    await remove_expense(conn, id)
    await remove_user(conn, register_user)

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_add_expense"])
async def test_del_expense(client_kwargs, conn, register_user, add_expense):
    async with AsyncClient(**client_kwargs()) as ac:
        res_register = await ac.post("/register", json=register_user)
    userid = res_register.json()["userid"]
    add_expense["userid"] = userid

    async with AsyncClient(**client_kwargs(get_cookie(userid))) as ac:
        res_add = await ac.post("/expenses", json=add_expense)
        res_add_json = res_add.json()
        id = res_add_json["id"]

        res_del = await ac.delete(f"/expenses/{id}")
    
    assert res_del.json()["message"] == "Expense deleted."
    assert res_del.status_code == 200

    await remove_user(conn, register_user)

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_del_expense"])
async def test_get_expense(client_kwargs, conn, register_user, add_expense):
    async with AsyncClient(**client_kwargs()) as ac:
        res_register = await ac.post("/register", json=register_user)
    userid = res_register.json()["userid"]
    add_expense["userid"] = userid

    async with AsyncClient(**client_kwargs(get_cookie(userid))) as ac:
        res_add = await ac.post("/expenses", json=add_expense)
        res_add_json = res_add.json()
        id = res_add_json["id"]

        res_get = await ac.get(f"/expenses/{userid}")

        assert res_get.json()[0]["id"] == id
        assert res_get.status_code == 200

        await ac.delete(f"/expenses/{id}")
    await remove_user(conn, register_user)

@pytest.mark.asyncio
@pytest.mark.dependency(depends=["test_get_expense"])
async def test_update_expense(client_kwargs, conn, register_user, add_expense, put_expense):
    async with AsyncClient(**client_kwargs()) as ac:
        res_register = await ac.post("/register", json=register_user)
    userid = res_register.json()["userid"]
    add_expense["userid"] = userid
    put_expense["userid"] = userid

    async with AsyncClient(**client_kwargs(get_cookie(userid))) as ac:
        res_add = await ac.post("/expenses", json=add_expense)
        res_add_json = res_add.json()
        id = res_add_json["id"]
        put_expense["id"] = id

        res_put = await ac.put("/expenses", json=put_expense)
        res_put_json = res_put.json()

        assert res_put_json != res_add_json
        assert res_put_json["id"] == id
        assert res_put.status_code == 200

        await ac.delete(f"/expenses/{id}")
    await remove_user(conn, register_user)
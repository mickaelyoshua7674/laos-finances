from sqlalchemy import text
from os import environ
import pytest

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

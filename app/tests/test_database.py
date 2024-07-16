from sqlalchemy import text
from os import environ
import pytest

@pytest.mark.asyncio
async def test_connection(my_engine):
    async with my_engine.connect() as conn:
        res = await conn.execute(text("SELECT 1;"))
    assert res.fetchone()[0] == 1, "Somenthing went wrong witch connection"

@pytest.mark.asyncio
async def test_database_exists(my_engine):
    dbName = environ["DB_NAME"]
    async with my_engine.connect() as conn:
        res = await conn.execute(text(f"SELECT datname FROM pg_database WHERE datname='{dbName}';"))
    assert res.fetchone()[0] == dbName, "Database not found"

from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from sqlalchemy import text, TextClause
from sqlalchemy.engine.url import URL
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
from os import environ

engine = create_async_engine(URL.create(drivername=environ["DB_DRIVERNAME"],
                                        username=environ["DB_USERNAME"],
                                        password=environ["DB_PASSWORD"],
                                        host=environ["DB_HOST"],
                                        port=environ["DB_PORT"],
                                        database=environ["DB_NAME"]), poolclass=NullPool)

async def getConn() -> AsyncGenerator[AsyncConnection,AsyncConnection]:
    conn = await engine.connect()
    try:
        yield conn
    finally:
        await conn.close()                                        
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from sqlalchemy.engine import create_engine
from sqlalchemy import text, TextClause
from sqlalchemy.engine.url import URL
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator
from os import environ

engineURL= URL.create(drivername=environ["DB_DRIVERNAME"],
                      username=environ["DB_USERNAME"],
                      password=environ["DB_PASSWORD"],
                      host=environ["DB_HOST"],
                      port=environ["DB_PORT"],
                      database=environ["DB_NAME"])
engineURLAsync = URL.create(drivername=environ["DB_ASYNC_DRIVERNAME"],
                            username=environ["DB_USERNAME"],
                            password=environ["DB_PASSWORD"],
                            host=environ["DB_HOST"],
                            port=environ["DB_PORT"],
                            database=environ["DB_NAME"])
engine = create_engine(engineURL, poolclass=NullPool)
asyncEngine = create_async_engine(engineURLAsync, poolclass=NullPool)

async def getConn() -> AsyncGenerator[AsyncConnection,AsyncConnection]:
    async with asyncEngine.connect() as conn:
        yield conn
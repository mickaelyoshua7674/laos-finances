from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import URL
from sqlalchemy import text
from os import environ

engine = create_async_engine(URL.create(drivername=environ["DB_DRIVERNAME"],
                                        username=environ["DB_USERNAME"],
                                        password=environ["DB_PASSWORD"],
                                        host=environ["DB_HOST"],
                                        port=environ["DB_PORT"],
                                        database=environ["DB_NAME"]), pool_size=100, max_overflow=0)

async def getFK(fk:str) -> set:
    async with engine.connect() as conn:
        res = await conn.execute(text(f'SELECT "{fk}" FROM "dim_{fk[2].lower()+fk[3:]}";'))
        return {v[0] for v in res.fetchall()}
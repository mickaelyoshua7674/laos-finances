from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from os import environ
import asyncio

engine = create_async_engine(URL.create(drivername=environ["DB_DRIVERNAME"],
                                        username=environ["DB_USERNAME"],
                                        password=environ["DB_PASSWORD"],
                                        host=environ["DB_HOST"],
                                        port=environ["DB_PORT"],
                                        database=environ["DB_NAME"]), poolclass=NullPool)

async def getUser() -> set:
    async with engine.connect() as conn:
        res = await conn.execute(text(f'SELECT "userName" FROM dim_user;'))
        return {v[0] for v in res.fetchall()}

async def getFK(fk:str) -> set:
    async with engine.connect() as conn:
        res = await conn.execute(text(f'SELECT "{fk}" FROM "dim_{fk[2].lower()+fk[3:]}";'))
        return {v[0] for v in res.fetchall()}

async def allFK():
    tasks = [asyncio.create_task(getUser()),
             asyncio.create_task(getFK("idFrequencyType")),
             asyncio.create_task(getFK("idExpenseSubCategory")),
             asyncio.create_task(getFK("idIncomeCategory"))]
    return await asyncio.gather(*tasks)
pkUserName, fkFrequencyType, fkExpenseSubCategory, fkIncomeCategory = asyncio.run(allFK())
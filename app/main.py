from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.engine.url import URL
from typing import AsyncGenerator
from fastapi import FastAPI
from os import environ

engine = create_async_engine(URL.create(drivername=environ["DB_DRIVERNAME"],
                                        username=environ["DB_USERNAME"],
                                        password=environ["DB_PASSWORD"],
                                        host=environ["DB_HOST"],
                                        port=environ["DB_PORT"],
                                        database=environ["DB_NAME"]), pool_size=100, max_overflow=0)

session = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)
async def getDBConnection() -> AsyncGenerator[AsyncSession]:
    db = await session()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.get("/")
async def home():
    return {"message":"Home"}

@app.get("/hi")
async def hw():
    return {"message":"Hello World!"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=int(environ["SERVER_PORT"]))
    # 'main' is the file name 'main.py'
    # 'app' is the FastAPI object 'app = FastAPI()'
    # 'reload=True' tells uvicorn to restart the server if main.py changes
    # 'host="0.0.0.0"' to make available to any device on the same network
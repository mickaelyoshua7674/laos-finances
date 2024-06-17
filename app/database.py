from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.engine.url import URL
from sqlalchemy import text
from os import environ
import asyncio

engine = create_async_engine(URL.create(drivername=environ["DB_DRIVERNAME"],
                                        username=environ["DB_USERNAME"],
                                        password=environ["DB_PASSWORD"],
                                        host=environ["DB_HOST"],
                                        port=environ["DB_PORT"],
                                        database=environ["DB_NAME"]), pool_size=100, max_overflow=0)
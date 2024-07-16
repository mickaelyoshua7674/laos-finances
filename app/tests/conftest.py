# 'conftest.py' will share the fixtures across all files
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.engine import URL

from os import environ
import pytest

@pytest.fixture(scope="session")
def my_engine():
    engineURLAsync = URL.create(drivername=environ["DB_ASYNC_DRIVERNAME"],
                                username=environ["DB_USERNAME"],
                                password=environ["DB_PASSWORD"],
                                host=environ["DB_HOST"],
                                port=environ["DB_PORT"],
                                database=environ["DB_NAME"])
    return create_async_engine(engineURLAsync, poolclass=NullPool)
from httpx import ASGITransport
import pytest_asyncio
import pytest

from ..database import asyncEngine
from ..main import app

@pytest.fixture
def client_kwargs():
    def _client_kwargs(cookie=None):
        return {"transport":ASGITransport(app=app), "base_url":"http://test", "follow_redirects":True, "cookies":cookie}
    return _client_kwargs

@pytest_asyncio.fixture
async def conn():
    async with asyncEngine.connect() as conn:
        yield conn

@pytest.fixture
def register_user():
    return {"username":"test@test.com", "name":"test", "password":"0000"}
@pytest.fixture
def login_user():
    return {"username":"test@test.com", "password":"0000"}

@pytest.fixture
def add_expense():
    return {"userid": "",
            "idFrequencyType": 3,
            "idExpenseSubCategory": 3,
            "value": 1000,
            "expenseDate": "2024-07-13"}
@pytest.fixture
def put_expense():
    return {"id": "",
            "userid": "",
            "idFrequencyType": 2,
            "idExpenseSubCategory": 1,
            "value": 5000,
            "expenseDate": "2024-07-17"}

@pytest.fixture
def add_income():
    return {"userid": "",
            "idFrequencyType": 3,
            "idIncomeCategory": 3,
            "value": 1000,
            "incomeDate": "2024-07-13"}
@pytest.fixture
def put_income():
    return {"id": "",
            "userid": "",
            "idFrequencyType": 2,
            "idIncomeCategory": 1,
            "value": 5000,
            "incomeDate": "2024-07-17"}
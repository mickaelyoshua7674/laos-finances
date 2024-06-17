from .model import Expense, insertScriptExpense
from fastapi import APIRouter
from datetime import datetime
from database import engine

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("/", response_model=Expense)
async def addExpense(e:Expense):
    insert = e.model_dump()
    insert["expenseDate"] = datetime.strptime(insert["expenseDate"], "%d-%m-%Y")
    print(insert)
    async with engine.connect() as conn:
        await conn.execute(insertScriptExpense, insert)
        await conn.commit()
    return e.model_dump()
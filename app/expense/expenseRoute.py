from .Expense import Expense, insertScriptExpense, text
from fastapi import APIRouter
from database import engine

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("/", response_model=Expense)
async def addExpense(e:Expense) -> dict[str, str|int|float]:
    insert = e.model_dump()
    async with engine.connect() as conn:
        await conn.execute(insertScriptExpense, insert)
        await conn.commit()
    return e.model_dump()

@expenses.get("/")
async def getExpenseAll():
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT * FROM fato_expense;"))
        fields = Expense.model_fields
        return [Expense(**{k:v for k,v in zip(fields, e)}).model_dump() for e in res.fetchall()]
from .Expense import Expense, insertScriptExpense, text
from fastapi import APIRouter
from database import engine

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("/", response_model=Expense)
async def addExpense(e:Expense) -> Expense:
    insert = e.model_dump()
    async with engine.connect() as conn:
        await conn.execute(insertScriptExpense, insert)
        await conn.commit()
    return e

@expenses.get("/")
async def getExpenseAll() -> list[Expense]:
    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT * FROM fato_expense;"))
        return [Expense(**{k:v for k,v in zip(Expense.model_fields, e)}) for e in res.fetchall()]

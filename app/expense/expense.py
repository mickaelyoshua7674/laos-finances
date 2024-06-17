from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .model import Expense, insertScriptExpense
from database import getSession

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("/", response_model=Expense)
async def addExpense(e:Expense, conn:Session=Depends(getSession)):
    insert = e.model_dump()
    await conn.execute(insertScriptExpense, insert)
    await conn.commit()
    await conn.refresh()
    return insert
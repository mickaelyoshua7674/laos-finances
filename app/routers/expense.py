from fastapi import APIRouter, Body, Depends
from models import Expense, JWTBearer, text
from database import getConn

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("", response_model=Expense, dependencies=[Depends(JWTBearer())])
@expenses.post("/", response_model=Expense)
async def addExpense(e:Expense, conn=Depends(getConn)) -> Expense:
    insert = e.model_dump()
    await conn.execute(e.getInsertScript(), insert)
    await conn.commit()
    return e

@expenses.get("")
@expenses.get("/")
async def getExpenseAll(conn=Depends(getConn)) -> list[Expense]:
    res = await conn.execute(text("SELECT * FROM fato_expense;"))
    return [Expense(**{k:v for k,v in zip(Expense.model_fields, e)}) for e in res.fetchall()]

@expenses.get("/user")
@expenses.get("/user/")
async def getExpenseUser(username:str=Body(), conn=Depends(getConn)) -> list[Expense]:
    res = await conn.execute(text(f'SELECT * FROM fato_expense WHERE username=\'{username}\';'))
    return [Expense(**{k:v for k,v in zip(Expense.model_fields, e)}) for e in res.fetchall()]
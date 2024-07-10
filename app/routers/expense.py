from fastapi import APIRouter, Body, Depends, Request
from models import Expense, JWTBearer, text, decodeJWT
from database import getConn

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("/", dependencies=[Depends(JWTBearer())])
async def addExpense(e:dict, request:Request, conn=Depends(getConn)) -> Expense:
    username = decodeJWT(request.state.token)["username"]
    insert = dict({"username":username}, **e)
    obj = Expense(**insert)
    print(obj.model_dump())
    await conn.execute(obj.getInsertScript(), obj.model_dump())
    await conn.commit()
    return obj

@expenses.get("/")
async def getExpenseAll(conn=Depends(getConn)) -> list[Expense]:
    res = await conn.execute(text("SELECT * FROM fato_expense;"))
    return [Expense(**{k:v for k,v in zip(Expense.model_fields, e)}) for e in res.fetchall()]

@expenses.get("/user")
async def getExpenseUser(username:str=Body(), conn=Depends(getConn)) -> list[Expense]:
    res = await conn.execute(text(f'SELECT * FROM fato_expense WHERE username=\'{username}\';'))
    return [Expense(**{k:v for k,v in zip(Expense.model_fields, e)}) for e in res.fetchall()]
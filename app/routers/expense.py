from fastapi import APIRouter, Depends, Request, HTTPException, Body
from auth import JWTBearer, decodeJWT
from models import Expense, text
from database import getConn

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("/", response_model=Expense, dependencies=[Depends(JWTBearer())])
async def addExpense(e:Expense, request:Request, conn=Depends(getConn)) -> Expense:
    JWTusername = decodeJWT(request.state.token)["username"]
    if JWTusername == e.username:
        await conn.execute(e.getInsertScript(), e.model_dump())
        await conn.commit()
        return e
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.get("/", dependencies=[Depends(JWTBearer())])
async def getAllExpensesUser(request:Request, username:str=Body(), conn=Depends(getConn)) -> list[Expense]:
    JWTusername = decodeJWT(request.state.token)["username"]
    if JWTusername == username:
        res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE username='{username}';"))
        return [Expense(**{k:v for k,v in zip(Expense.model_fields, e)}) for e in res.fetchall()]
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")
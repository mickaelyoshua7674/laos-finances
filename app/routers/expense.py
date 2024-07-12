from fastapi import APIRouter, Depends, Request, HTTPException, Body
from auth import JWTBearer, decodeJWT
from models import Expense, text
from database import getConn

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("/", dependencies=[Depends(JWTBearer())])
async def add(data:dict, request:Request, conn=Depends(getConn)) -> Expense:
    e = Expense(**dict({"id":0}, **data))
    JWTusername = decodeJWT(request.state.token)["username"]
    if JWTusername == e.username:
        insertData = e.model_dump()
        insertData.pop("id")
        res = await conn.execute(e.getInsertScript(), insertData)
        await conn.commit()
        return Expense(id=res.fetchone()[0], **insertData)
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.get("/", dependencies=[Depends(JWTBearer())])
async def get_all_user(request:Request, username:str=Body(), conn=Depends(getConn)) -> list[Expense]:
    JWTusername = decodeJWT(request.state.token)["username"]
    if JWTusername == username:
        res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE username='{username}';"))
        return [Expense.fromList(values) for values in res.fetchall()]
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request. User may not be registered.")

@expenses.delete("/", dependencies=[Depends(JWTBearer())])
async def delete(request:Request, id:int=Body(), conn=Depends(getConn)) -> dict:
    res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE id={id};"))
    data = res.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Expense id not found.")
    e = Expense.fromList(data)
    JWTusername = decodeJWT(request.state.token)["username"]
    if JWTusername == e.username:
        await conn.execute(text(f"DELETE FROM fato_expense WHERE id={e.id};"))
        await conn.commit()
        return {"message":"Expense deleted."}
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request. User may not be registered.")

@expenses.put("/", response_model=Expense, dependencies=[Depends(JWTBearer())])
async def update(e:Expense, request:Request, conn=Depends(getConn)) -> Expense:
    JWTusername = decodeJWT(request.state.token)["username"]
    if JWTusername == e.username:
        updateData = e.model_dump()
        updateData.pop("id")
        updateData.pop("username")
        await conn.execute(e.getUpdateScript(), updateData)
        await conn.commit()
        res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE id={e.id};"))
        return Expense.fromList(res.fetchone())
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request. User may not be registered.")
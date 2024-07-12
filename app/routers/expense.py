from fastapi import APIRouter, Depends, Request, HTTPException
from auth import JWTBearer, decodeJWT, checkUserExist
from models import Expense, text
from database import getConn

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("/", dependencies=[Depends(JWTBearer())])
async def add(request:Request, data:dict, conn=Depends(getConn)) -> Expense:
    e = Expense(**dict({"id":0}, **data))
    if decodeJWT(request.state.token)["username"] == e.username:
        insertData = e.model_dump()
        insertData.pop("id")
        res = await conn.execute(e.getInsertScript(), insertData)
        await conn.commit()
        return Expense(id=res.fetchone()[0], **insertData)
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.get("/{username}", dependencies=[Depends(JWTBearer())])
async def get_all(request:Request, username:str, conn=Depends(getConn)) -> list[Expense]:
    if not await checkUserExist(username=username):
        raise HTTPException(status_code=404, detail="Username not found.")
    if decodeJWT(request.state.token)["username"] == username:
        res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE username='{username}';"))
        return [Expense.fromList(values) for values in res.fetchall()]
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.delete("/{id}", dependencies=[Depends(JWTBearer())])
async def delete(request:Request, id:int, conn=Depends(getConn)) -> dict:
    res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE id={id};"))
    data = res.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Id not found.")
    e = Expense.fromList(data)
    if decodeJWT(request.state.token)["username"] == e.username:
        await conn.execute(text(f"DELETE FROM fato_expense WHERE id={e.id};"))
        await conn.commit()
        return {"message":"Expense deleted."}
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.put("/", response_model=Expense, dependencies=[Depends(JWTBearer())])
async def update(request:Request, e:Expense, conn=Depends(getConn)) -> Expense:
    if not e.validateID():
        raise HTTPException(status_code=404, detail="id not found.")
    if decodeJWT(request.state.token)["username"] == e.username:
        updateData = e.model_dump()
        updateData.pop("id")
        updateData.pop("username")
        await conn.execute(e.getUpdateScript(), updateData)
        await conn.commit()
        res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE id={e.id};"))
        return Expense.fromList(res.fetchone())
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")
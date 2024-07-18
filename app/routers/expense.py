from fastapi import APIRouter, Depends, Request, HTTPException, Response
from auth import oauth2_scheme, decodeJWT, checkUserExist, createAccessToken
from models import Expense, text
from database import getConn
from os import environ
from uuid import UUID
import time

ACCESS_TOKEN_EXPIRES_SECONDS = int(environ["ACCESS_TOKEN_EXPIRES_SECONDS"])

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("/", dependencies=[Depends(oauth2_scheme)])
async def add(request:Request, response:Response, data:dict, conn=Depends(getConn)) -> Expense:
    data["userid"] = UUID(data["userid"])
    e = Expense(**data)
    userid = str(e.userid)
    if decodeJWT(request.cookies.get("access_token"))["userid"] == userid:
        insertData = e.model_dump()
        insertData.pop("id")
        res = await conn.execute(e.getInsertScript(), insertData)
        await conn.commit()

        await createAccessToken(data={"userid":userid, "expires":time.time() + ACCESS_TOKEN_EXPIRES_SECONDS}, setCookie=True, response=response)

        return Expense(id=res.fetchone()[0], **insertData) 
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.get("/{userid}", dependencies=[Depends(oauth2_scheme)])
async def get_all(request:Request, response:Response, userid:str, conn=Depends(getConn)) -> list[Expense]:
    if not await checkUserExist(userid=userid):
        raise HTTPException(status_code=404, detail="Username not found.")
    if decodeJWT(request.cookies.get("access_token"))["userid"] == userid:
        res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE userid='{userid}' ORDER BY id;"))

        await createAccessToken(data={"userid":userid, "expires":time.time() + ACCESS_TOKEN_EXPIRES_SECONDS}, setCookie=True, response=response)

        return [Expense.fromList(values) for values in res.fetchall()]
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.delete("/{id}", dependencies=[Depends(oauth2_scheme)])
async def delete(request:Request, response:Response, id:int, conn=Depends(getConn)) -> dict:
    res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE id={id};"))
    data = res.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Id not found.")
    e = Expense.fromList(data)
    userid = str(e.userid)
    if decodeJWT(request.cookies.get("access_token"))["userid"] == userid:
        await conn.execute(text(f"DELETE FROM fato_expense WHERE id={e.id};"))
        await conn.commit()

        await createAccessToken(data={"userid":userid, "expires":time.time() + ACCESS_TOKEN_EXPIRES_SECONDS}, setCookie=True, response=response)

        return {"message":"Expense deleted."}
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.put("/", response_model=Expense, dependencies=[Depends(oauth2_scheme)])
async def update(request:Request, response:Response, e:Expense, conn=Depends(getConn)) -> Expense:
    if not e.validateID():
        raise HTTPException(status_code=404, detail="id not found.")
    userid = str(e.userid)
    if decodeJWT(request.cookies.get("access_token"))["userid"] == userid:
        updateData = e.model_dump()
        updateData.pop("id")
        updateData.pop("userid")
        await conn.execute(e.getUpdateScript(), updateData)
        await conn.commit()
        res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE id={e.id};"))

        await createAccessToken(data={"userid":userid, "expires":time.time() + ACCESS_TOKEN_EXPIRES_SECONDS}, setCookie=True, response=response)

        return Expense.fromList(res.fetchone())
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")
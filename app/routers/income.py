from fastapi import APIRouter, Depends, Request, HTTPException, Response
from auth import oauth2_scheme, decodeJWT, checkUserExist, createAccessToken
from models import Income, text
from database import getConn
from os import environ
from uuid import UUID
import time

ACCESS_TOKEN_EXPIRES_SECONDS = int(environ["ACCESS_TOKEN_EXPIRES_SECONDS"])

incomes = APIRouter(prefix="/incomes", tags=["incomes"])

@incomes.post("/", dependencies=[Depends(oauth2_scheme)])
async def add(request:Request, response:Response, data:dict, conn=Depends(getConn)) -> Income:
    data["userid"] = UUID(data["userid"])
    print()
    print(data)
    print()
    i = Income(**data)
    userid = str(i.userid)
    if decodeJWT(request.cookies.get("access_token"))["userid"] == userid:
        insertData = i.model_dump()
        insertData.pop("id")
        res = await conn.execute(i.getInsertScript(), insertData)
        await conn.commit()

        await createAccessToken(data={"userid":userid, "expires":time.time() + ACCESS_TOKEN_EXPIRES_SECONDS}, setCookie=True, response=response)

        return Income(id=res.fetchone()[0], **insertData) 
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@incomes.get("/{userid}", dependencies=[Depends(oauth2_scheme)])
async def get_all(request:Request, response:Response, userid:str, conn=Depends(getConn)) -> list[Income]:
    if not await checkUserExist(userid=userid):
        raise HTTPException(status_code=404, detail="Username not found.")
    if decodeJWT(request.cookies.get("access_token"))["userid"] == userid:
        res = await conn.execute(text(f"SELECT * FROM fato_income WHERE userid='{userid}' ORDER BY id;"))

        await createAccessToken(data={"userid":userid, "expires":time.time() + ACCESS_TOKEN_EXPIRES_SECONDS}, setCookie=True, response=response)

        return [Income.fromList(values) for values in res.fetchall()]
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@incomes.delete("/{id}", dependencies=[Depends(oauth2_scheme)])
async def delete(request:Request, response:Response, id:int, conn=Depends(getConn)) -> dict:
    res = await conn.execute(text(f"SELECT * FROM fato_income WHERE id={id};"))
    data = res.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Id not found.")
    i = Income.fromList(data)
    userid = str(i.userid)
    if decodeJWT(request.cookies.get("access_token"))["userid"] == userid:
        await conn.execute(text(f"DELETE FROM fato_income WHERE id={i.id};"))
        await conn.commit()

        await createAccessToken(data={"userid":userid, "expires":time.time() + ACCESS_TOKEN_EXPIRES_SECONDS}, setCookie=True, response=response)

        return {"message":"Income deleted."}
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@incomes.put("/", response_model=Income, dependencies=[Depends(oauth2_scheme)])
async def update(request:Request, response:Response, i:Income, conn=Depends(getConn)) -> Income:
    if not i.validateID():
        raise HTTPException(status_code=404, detail="id not found.")
    userid = str(i.userid)
    if decodeJWT(request.cookies.get("access_token"))["userid"] == userid:
        updateData = i.model_dump()
        updateData.pop("id")
        updateData.pop("userid")
        await conn.execute(i.getUpdateScript(), updateData)
        await conn.commit()
        res = await conn.execute(text(f"SELECT * FROM fato_income WHERE id={i.id};"))

        await createAccessToken(data={"userid":userid, "expires":time.time() + ACCESS_TOKEN_EXPIRES_SECONDS}, setCookie=True, response=response)

        return Income.fromList(res.fetchone())
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")
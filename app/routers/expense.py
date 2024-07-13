from fastapi import APIRouter, Depends, Request, HTTPException, Response
from auth import OAuth2PasswordBearerWithCookie, decodeJWT, checkUserExist, createAccessToken
from models import Expense, text
from database import getConn
import time

expenses = APIRouter(prefix="/expenses", tags=["expenses"])

@expenses.post("/", dependencies=[Depends(OAuth2PasswordBearerWithCookie(tokenUrl="/login"))])
async def add(request:Request, response:Response, data:dict, conn=Depends(getConn)) -> Expense:
    e = Expense(**dict({"id":0}, **data))
    if decodeJWT(request.cookies.get("access_token"))["email"] == e.email:
        insertData = e.model_dump()
        insertData.pop("id")
        res = await conn.execute(e.getInsertScript(), insertData)
        await conn.commit()

        await createAccessToken(data={"email":e.email, "expires":time.time() + 2*24*60*60}, setCookie=True, response=response)

        return Expense(id=res.fetchone()[0], **insertData) 
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.get("/{email}", dependencies=[Depends(OAuth2PasswordBearerWithCookie(tokenUrl="/login"))])
async def get_all(request:Request, response:Response, email:str, conn=Depends(getConn)) -> list[Expense]:
    if not await checkUserExist(email):
        raise HTTPException(status_code=404, detail="Email not found.")
    if decodeJWT(request.cookies.get("access_token"))["email"] == email:
        res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE email='{email}';"))

        await createAccessToken(data={"email":email, "expires":time.time() + 2*24*60*60}, setCookie=True, response=response)

        return [Expense.fromList(values) for values in res.fetchall()]
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.delete("/{id}", dependencies=[Depends(OAuth2PasswordBearerWithCookie(tokenUrl="/login"))])
async def delete(request:Request, response:Response, id:int, conn=Depends(getConn)) -> dict:
    res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE id={id};"))
    data = res.fetchone()
    if not data:
        raise HTTPException(status_code=404, detail="Id not found.")
    e = Expense.fromList(data)
    if decodeJWT(request.cookies.get("access_token"))["email"] == e.email:
        await conn.execute(text(f"DELETE FROM fato_expense WHERE id={e.id};"))
        await conn.commit()

        await createAccessToken(data={"email":e.email, "expires":time.time() + 2*24*60*60}, setCookie=True, response=response)

        return {"message":"Expense deleted."}
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")

@expenses.put("/", response_model=Expense, dependencies=[Depends(OAuth2PasswordBearerWithCookie(tokenUrl="/login"))])
async def update(request:Request, response:Response, e:Expense, conn=Depends(getConn)) -> Expense:
    if not e.validateID():
        raise HTTPException(status_code=404, detail="id not found.")
    if decodeJWT(request.cookies.get("access_token"))["email"] == e.email:
        updateData = e.model_dump()
        updateData.pop("id")
        updateData.pop("email")
        await conn.execute(e.getUpdateScript(), updateData)
        await conn.commit()
        res = await conn.execute(text(f"SELECT * FROM fato_expense WHERE id={e.id};"))

        await createAccessToken(data={"email":e.email, "expires":time.time() + 2*24*60*60}, setCookie=True, response=response)

        return Expense.fromList(res.fetchone())
    raise HTTPException(status_code=401, detail="JWT user does not match the user in request.")
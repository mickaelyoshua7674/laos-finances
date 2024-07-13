from routers.expense import expenses
from routers.income import incomes
from fastapi import FastAPI, Response
from os import environ

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException

from auth import checkUserExist, hashPasword, checkPassword, createAccessToken
from database import getConn
from typing import Annotated
from models import User
import time

app = FastAPI()
app.include_router(expenses)
app.include_router(incomes)

@app.get("/")
async def home():
    return {"message":"Home"}

@app.post("/register")
async def register(u:User, conn=Depends(getConn)) -> dict:
    insert = u.model_dump()
    if await checkUserExist(insert["email"]) is not None:
        raise HTTPException(status_code=401, detail="Email already registered")

    insert["password"] = await hashPasword(insert["password"].get_secret_value())
    await conn.execute(u.getInsertScript(), insert)
    await conn.commit()
    return {"message":"User registered"}

@app.post("/login")
async def login(response:Response, formData:Annotated[OAuth2PasswordRequestForm, Depends()]) -> dict:
    u = await checkUserExist(formData.username)
    if u is None:
        raise HTTPException(status_code=401, detail="Email incorrect.")
    elif not await checkPassword(formData.password, u.password.get_secret_value()):
        raise HTTPException(status_code=401, detail="Password incorrect.")
    token = await createAccessToken(data={"email":u.email, "expires":time.time() + 2*24*60*60}, setCookie=True, response=response)
    return {"access_token":token, "token_type":"bearer"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=int(environ["SERVER_PORT"]))
    # 'main' is the file name 'main.py'
    # 'app' is the FastAPI object 'app = FastAPI()'
    # 'reload=True' tells uvicorn to restart the server if main.py changes
    # 'host="0.0.0.0"' to make available to any device on the same network
from fastapi import FastAPI, Response, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from auth import checkUserExist, hashPasword, checkPassword, createAccessToken
from routers.expense import expenses
from routers.income import incomes
from database import getConn
from models import User
from os import environ
import time

ACCESS_TOKEN_EXPIRES_SECONDS = int(environ["ACCESS_TOKEN_EXPIRES_SECONDS"])

app = FastAPI()
app.include_router(expenses)
app.include_router(incomes)

@app.get("/")
async def home():
    return {"message":"Home"}

@app.post("/register")
async def register(data:dict, conn=Depends(getConn)) -> dict:
    u = User(**data)
    insert = u.model_dump()
    insert.pop("userid")
    if await checkUserExist(email=insert["email"]) is not None:
        raise HTTPException(status_code=401, detail="Email already registered")

    insert["password"] = await hashPasword(insert["password"].get_secret_value())
    res = await conn.execute(u.getInsertScript(), insert)
    await conn.commit()
    return {"message":"User registered", "userid":str(res.fetchone()[0])}

@app.post("/login")
async def login(response:Response, formData:OAuth2PasswordRequestForm=Depends()) -> str:
    u = await checkUserExist(email=formData.username)
    if u is None:
        raise HTTPException(status_code=401, detail="Email incorrect.")
    elif not await checkPassword(formData.password, u.password.get_secret_value()):
        raise HTTPException(status_code=401, detail="Password incorrect.")
    await createAccessToken(data={"userid":str(u.userid), "expires":time.time() + ACCESS_TOKEN_EXPIRES_SECONDS}, setCookie=True, response=response)
    return str(u.userid)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=int(environ["SERVER_PORT"]))
    # 'main' is the file name 'main.py'
    # 'app' is the FastAPI object 'app = FastAPI()'
    # 'reload=True' tells uvicorn to restart the server if main.py changes
    # 'host="0.0.0.0"' to make available to any device on the same network
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException

from auth import checkUserExist, hashPasword, checkPassword, createAccessToken
from database import getConn
from typing import Annotated
from models import User

users = APIRouter(prefix="/users",tags=["users"])

@users.post("/register")
async def register(u:User, conn=Depends(getConn)) -> str:
    insert = u.model_dump()
    if await checkUserExist(username=insert["username"]) is not None:
        raise HTTPException(status_code=401, detail="Username already in use")
    if await checkUserExist(email=insert["email"]) is not None:
        raise HTTPException(status_code=401, detail="Email already registered")

    insert["password"] = await hashPasword(insert["password"].get_secret_value())
    await conn.execute(u.getInsertScript(), insert)
    await conn.commit()
    return await createAccessToken(u.username)

@users.post("/login")
async def login(formData:Annotated[OAuth2PasswordRequestForm, Depends()]) -> str:
    u = await checkUserExist(username=formData.username)
    if u is None:
        raise HTTPException(status_code=401, detail="Username incorrect.")
    elif not await checkPassword(formData.password, u.password.get_secret_value()):
        raise HTTPException(status_code=401, detail="Password incorrect.")
    else:
        return await createAccessToken(u.username)
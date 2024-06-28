from passlib.context import CryptContext
import jwt

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from database import getConn, engine, text
from typing import Annotated
from models import User

SECRET_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJVc2VyIjoibGFvcyJ9.MvNzpRt3bxwP5EQkLX-aTxXFRm_IDU5DeooOnH0UvIk"
ALGORITHM = "HS256"

users = APIRouter(prefix="/users",tags=["users"])
pwdContext = CryptContext(schemes=["bcrypt"])

async def getUser(userName:str=None, email:str=None) -> User|None:
    if userName is not None:
        script = text(f'SELECT * FROM dim_user WHERE "userName"=\'{userName}\';')
    elif email is not None:
        script = text(f'SELECT * FROM dim_user WHERE email=\'{email}\';')
    else:
        raise ValueError("Give a 'userName' or 'email'")

    async with engine.connect() as conn:
        res = await conn.execute(script)
    result = res.fetchall()
    if result:
        return User(**{k:v for k,v in zip(User.model_fields, result[0])})

@users.post("/register", response_model=User)
@users.post("/register/", response_model=User)
async def register(u:User, conn=Depends(getConn)) -> User:
    insert = u.model_dump()
    if await getUser(userName=insert["userName"]) is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UserName already in use")
    if await getUser(email=insert["email"]) is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email already registered")

    insert["password"] = pwdContext.hash(insert["password"].get_secret_value())
    await conn.execute(u.getInsertScript(), insert)
    await conn.commit()
    return u

@users.post("/login", response_model=User)
@users.post("/login/", response_model=User)
async def login(formData:Annotated[OAuth2PasswordRequestForm, Depends()]) -> str:
    user = getUser(userName=formData.username)
    if await user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UserName incorrect.")
    elif not pwdContext.verify(formData.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password incorrect.")
    else:
        return jwt.encode({"sub":user.userName}, SECRET_KEY, ALGORITHM)
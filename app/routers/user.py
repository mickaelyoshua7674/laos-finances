from passlib.context import CryptContext

from fastapi import APIRouter, Depends, HTTPException, status
from database import getConn, engine, text
from models import User

users = APIRouter(prefix="/users",tags=["users"])

pwdContext = CryptContext(schemes=["bcrypt"])
async def verifyPassword(plainPassword:str, hashedPassword:str) -> bool:
    return pwdContext.verify(plainPassword, hashedPassword)

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

async def authenticateUser(userName:str, password:str) -> User|bool:
    u = await getUser(userName=userName)
    if not u:
        return False
    if not await verifyPassword(password, u.password):
        return False
    return User

@users.post("", response_model=User)
@users.post("/", response_model=User)
async def addUser(u:User, conn=Depends(getConn)) -> User:
    insert = u.model_dump()
    if await getUser(userName=insert["userName"]) is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="UserName already in use")
    if await getUser(email=insert["email"]) is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email already registered")

    insert["password"] = pwdContext.hash(insert["password"].get_secret_value())
    await conn.execute(u.getInsertScript(), insert)
    await conn.commit()
    return u

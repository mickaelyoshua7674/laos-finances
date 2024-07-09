from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
import jwt

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status
from .expense import expenses
from .income import incomes

from database import getConn, engine, text
from typing import Annotated
from models import User

SECRET_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJVc2VyIjoibGFvcyJ9.MvNzpRt3bxwP5EQkLX-aTxXFRm_IDU5DeooOnH0UvIk"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30

users = APIRouter(prefix="/users",tags=["users"])
users.include_router(expenses)
users.include_router(incomes)

pwdContext = CryptContext(schemes=["bcrypt"])
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def createAccessToken(data:dict, expiresDelta: timedelta|None=None):
    toEncode = data.copy()
    if expiresDelta:
        expire = datetime.now(timezone.utc) + expiresDelta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    toEncode.update({"exp":expire})
    encodeJWT = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)
    return encodeJWT

async def getUser(username:str=None, email:str=None) -> User|None:
    if username is not None:
        script = text(f'SELECT * FROM users WHERE username=\'{username}\';')
    elif email is not None:
        script = text(f'SELECT * FROM users WHERE email=\'{email}\';')
    else:
        raise ValueError("Give a 'username' or 'email'")

    async with engine.connect() as conn:
        res = await conn.execute(script)
    result = res.fetchall()
    if result:
        return User(**{k:v for k,v in zip(User.model_fields, result[0])})

async def getCurrentUser(token:Annotated[str, Depends(oauth2Scheme)]) -> User:
    credentialException = HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validade credentials",
                            headers={"WWW-Authenticate":"Bearer"}
                        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username:str = payload.get("sub")
        if username is None:
            raise credentialException
    except InvalidTokenError:
        raise credentialException
    user = await getUser(username)
    if user is None:
        raise credentialException
    return user

@users.post("/register", response_model=User)
@users.post("/register/", response_model=User)
async def register(u:User, conn=Depends(getConn)) -> User:
    insert = u.model_dump()
    if await getUser(username=insert["username"]) is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="username already in use")
    if await getUser(email=insert["email"]) is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email already registered")

    insert["password"] = pwdContext.hash(insert["password"].get_secret_value())
    await conn.execute(u.getInsertScript(), insert)
    await conn.commit()
    return u

@users.post("/login")
@users.post("/login/")
async def login(formData:Annotated[OAuth2PasswordRequestForm, Depends()]) -> str:
    user = await getUser(username=formData.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username incorrect.")
    elif not pwdContext.verify(formData.password, user.password.get_secret_value()):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password incorrect.")
    else:
        return await createAccessToken(data={"sub":user.username}, expiresDelta=timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES))
from datetime import timedelta, datetime, timezone
from typing import Annotated

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
import jwt

from fastapi import APIRouter, Depends, HTTPException, status
from .expense import expenses
from .income import incomes
from models import Expense, Token, User
from database import engine, text, getConn

auth = APIRouter(prefix="/auth", tags=["auth"])
auth.include_router(expenses)
auth.include_router(incomes)

SECRET_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJVc2VyIjoibGFvcyJ9.MvNzpRt3bxwP5EQkLX-aTxXFRm_IDU5DeooOnH0UvIk"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES_MINUTES = 30

pwdContext = CryptContext(schemes=["bcrypt"])
oauth2Scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

async def verifyPassword(plainPassword:str, hashedPassword:str) -> bool:
    return pwdContext.verify(plainPassword, hashedPassword)

async def getPasswordHash(password:str) -> str:
    return pwdContext.hash(password)

async def getUser(userName:str) -> User:
    async with engine.connect() as conn:
        res = await conn.execute(text(f'SELECT * FROM dim_user WHERE "userName"=\'{userName}\';'))
    result = res.fetchall()
    if result:
        print(result)
        return User(**{k:v for k,v in zip(User.model_fields, result[0])})

async def authenticateUser(userName:str, password:str) -> User | bool:
    u = await getUser(userName)
    if not u:
        return False
    if not await verifyPassword(password, u.password):
        return False
    return User

async def createAccessToken(data:dict, expiresDelta: timedelta|None=None):
    toEncode = data.copy()
    if expiresDelta:
        expire = datetime.now(timezone.utc) + expiresDelta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    toEncode.update({"expiration":expire})
    encodeJWT = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)
    return encodeJWT

async def getCurrentUser(token:Annotated[str, Depends(oauth2Scheme)]) -> User:
    credentialException = HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Could not validade credentials",
                            headers={"WWW-Authenticate":"Bearer"}
                        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        userName:str = payload.get("sub")
        if userName is None:
            raise credentialException
    except InvalidTokenError:
        raise credentialException
    user = getUser(userName)
    if user is None:
        raise credentialException
    return user

async def getCurrentActiveUser(currentUser:Annotated[User, Depends(getCurrentUser)]):
    if currentUser.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return currentUser

@auth.post("/token")
@auth.post("/token/")
async def loginForAccessToken(formData:Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    user = authenticateUser(formData.username, formData.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate":"Bearer"}
        )
    accessTokenExpires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    accesToken = createAccessToken(data={"sub":user.userName}, expiresDelta=accessTokenExpires)
    return Token(accessToken=accesToken, tokenType="bearer")

@auth.get("/user/me")
@auth.get("/user/me/")
async def readUserMe(currentUser:Annotated[User, Depends(getCurrentActiveUser)]) -> User:
    return currentUser

@auth.get("/user/me/items")
@auth.get("/user/me/items/")
async def readOwnItems(currentUser:Annotated[User, Depends(getCurrentActiveUser)], conn=Depends(getConn)) -> list[Expense]:
    res = await conn.execute(text(f'SELECT * FROM fato_expense WHERE "userName"=\'{currentUser.userName}\';'))
    return [Expense(**{k:v for k,v in zip(Expense.model_fields, e)}) for e in res.fetchall()]
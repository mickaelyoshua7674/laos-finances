from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from fastapi import APIRouter
from models import Token, TokenData, User, UserInDB
from database import engine, text
import asyncio

auth = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = "eyJhbGciOiJIUzI1NiJ9.eyJSb2xlIjoiQWRtaW4iLCJVc2VyIjoibGFvcyJ9.MvNzpRt3bxwP5EQkLX-aTxXFRm_IDU5DeooOnH0UvIk"
ALGORITHM = "HS256"

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
    if not verifyPassword(password, u.password):
        return False
    return User

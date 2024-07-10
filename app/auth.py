import time
from passlib.context import CryptContext
import jwt

from database import engine, text
from models import User
from os import environ

SECRET_KEY = environ["SECRET_KEY"]
ALGORITHM = environ["ALGORITHM"]

pwdContext = CryptContext(schemes=["bcrypt"])

async def hashPasword(password:str) -> str:
    return pwdContext.hash(password)
async def checkPassword(password:str, storedPassword:str) -> bool:
    return pwdContext.verify(password, storedPassword)

async def createAccessToken(username:str):
    toEncode = {
        "username":username,
        "expires":time.time() + 600
        }
    return jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)

async def checkUserExist(username:str|None=None, email:str|None=None) -> User|None:
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
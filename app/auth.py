from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
import jwt

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException

from database import asyncEngine, text
from models import User

from os import environ
import time

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
        "expires":time.time() + 7*24*60*60
        }
    return jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)

async def checkUserExist(username:str|None=None, email:str|None=None) -> User|None:
    if username is not None:
        script = text(f'SELECT * FROM users WHERE username=\'{username}\';')
    elif email is not None:
        script = text(f'SELECT * FROM users WHERE email=\'{email}\';')
    else:
        raise ValueError("Give a 'username' or 'email'")

    async with asyncEngine.connect() as conn:
        res = await conn.execute(script)
        result = res.fetchall()
    if result:
        return User(**{k:v for k,v in zip(User.model_fields, result[0])})

def decodeJWT(token:str) -> dict|None:
    decodedToken = jwt.decode(token, environ["SECRET_KEY"], algorithms=[environ["ALGORITHM"]])
    if decodedToken["expires"] >= time.time():
        return decodedToken

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error:bool=True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request:Request):
        credentials:HTTPAuthorizationCredentials|None = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authetication scheme.")
            if not self.verifyJWT(credentials.credentials):
                raise HTTPException(status_code=403, detail="Session expired, please login again.")
            request.state.token = credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
    
    def verifyJWT(self, token:str) -> bool:
        isTokenValid:bool = False

        try:
            payload = decodeJWT(token)
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token.")
            
        if payload:
            isTokenValid = True
        return isTokenValid
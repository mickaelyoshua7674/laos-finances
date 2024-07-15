from passlib.context import CryptContext
from jwt.exceptions import InvalidTokenError
import jwt

from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import Request, HTTPException, Response
from fastapi.security import OAuth2

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

async def createAccessToken(data:dict, setCookie:bool=False, response:Response|None=None):
    param = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    if setCookie:
        response.set_cookie(key="access_token", value=f"Bearer {param}", httponly=True, secure=True)
    return param

async def checkUserExist(userid:str|None=None, email:str|None=None) -> User|None:
    if userid:
        script = text(f"SELECT * FROM users WHERE userid='{userid}';")
    elif email:
        script = text(f"SELECT * FROM users WHERE email='{email}';")
    else:
        raise ValueError("Inform userid or email")

    async with asyncEngine.connect() as conn:
        res = await conn.execute(script)
        result = res.fetchone()
    if result:
        return User.fromList(result)

def decodeJWT(token:str) -> dict|None:
    decodedToken = jwt.decode(token.split(" ")[1], environ["SECRET_KEY"], algorithms=[environ["ALGORITHM"]])
    if decodedToken["expires"] >= time.time():
        return decodedToken

class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(self, tokenUrl:str, scheme_name:str|None=None, scopes:dict[str, str]|None=None, auto_error:bool=True):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl":tokenUrl, "scopes":scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request:Request) -> str|None:
        token:str|None = request.cookies.get("access_token")
        if token:
            scheme, param = token.split(" ")
            if self.auto_error:
                if scheme.lower() != "bearer":
                    raise HTTPException(status_code=401, detail="Not authenticated", headers={"WWW-Authenticate": "Bearer"})
                if not self.verifyJWT(token):
                    raise HTTPException(status_code=401, detail="Session expired, please login again.")
            return param

    def verifyJWT(self, token:str) -> bool:
        isTokenValid:bool = False
        try:
            payload = decodeJWT(token)
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token.")
        if payload:
            isTokenValid = True
        return isTokenValid

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login")
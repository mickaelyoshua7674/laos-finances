from pydantic import BaseModel, Field, field_validator, SecretStr, EmailStr
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import engine, text, TextClause
from datetime import date
import asyncio

async def getUserSet() -> set:
    async with engine.connect() as conn:
        res = await conn.execute(text(f'SELECT username FROM users;'))
        return {v[0] for v in res.fetchall()}
async def getFK(fk:str) -> set:
    async with engine.connect() as conn:
        res = await conn.execute(text(f'SELECT "{fk}" FROM "dim_{fk[2].lower()+fk[3:]}";'))
        return {v[0] for v in res.fetchall()}
async def allPK_FK():
    tasks = [asyncio.create_task(getUserSet()),
             asyncio.create_task(getFK("idFrequencyType")),
             asyncio.create_task(getFK("idExpenseSubCategory")),
             asyncio.create_task(getFK("idIncomeCategory"))]
    return await asyncio.gather(*tasks)
pkUsername, fkFrequencyType, fkExpenseSubCategory, fkIncomeCategory = asyncio.run(allPK_FK())

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error:bool=True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

class Token(BaseModel):
    accessToken:str
    tokenType:str

class User(BaseModel):
    username:str
    email:EmailStr = Field(pattern=r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
    name:str
    password:SecretStr

    @classmethod
    def getInsertScript(cls) -> TextClause:
        return text("INSERT INTO users VALUES (:username,:email,:name,:password);")

class Expense(BaseModel):
    username:str
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float = Field(gt=0)
    expenseDate:date

    @field_validator("username")
    def checkusername(cls, u:str) -> str:
        if u not in pkUsername:
            raise(ValueError("username not registred."))
        else:
            return u

    @field_validator("idFrequencyType")
    def checkFrequencyType(cls, x:int) -> int:
        if x not in fkFrequencyType:
            raise (ValueError("No match to constraint in Foreing Key idFrequencyType"))
        else:
            return x

    @field_validator("idExpenseSubCategory")
    def checkExpenseSubCategory(cls, x:int) -> int:
        if x not in fkExpenseSubCategory:
            raise (ValueError("No match to constraint in Foreing Key idExpenseSubCategory"))
        else:
            return x
    
    @classmethod
    def getInsertScript(cls) -> TextClause:
        return text("INSERT INTO fato_expense VALUES (:username,:idFrequencyType,:idExpenseSubCategory,:value,:expenseDate);")


class Income(BaseModel):
    idFrequencyType:int
    idIncomeCategory:int
    value:float
    incomeDate:str
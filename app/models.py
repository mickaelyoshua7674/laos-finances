from pydantic import BaseModel, Field, field_validator, SecretStr, EmailStr
from database import engine, text, TextClause
from datetime import date
import asyncio

async def getUser() -> set:
    async with engine.connect() as conn:
        res = await conn.execute(text(f'SELECT "userName" FROM dim_user;'))
        return {v[0] for v in res.fetchall()}
async def getFK(fk:str) -> set:
    async with engine.connect() as conn:
        res = await conn.execute(text(f'SELECT "{fk}" FROM "dim_{fk[2].lower()+fk[3:]}";'))
        return {v[0] for v in res.fetchall()}
async def allPK_FK():
    tasks = [asyncio.create_task(getUser()),
             asyncio.create_task(getFK("idFrequencyType")),
             asyncio.create_task(getFK("idExpenseSubCategory")),
             asyncio.create_task(getFK("idIncomeCategory"))]
    return await asyncio.gather(*tasks)
pkUserName, fkFrequencyType, fkExpenseSubCategory, fkIncomeCategory = asyncio.run(allPK_FK())


class Token(BaseModel):
    accessToken:str
    tokenType:str

class User(BaseModel):
    userName:str
    name:str
    email:EmailStr = Field(pattern=r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
    password:SecretStr
    disabled:bool

    @field_validator("userName")
    def checkUserName(cls, u:str) -> str:
        if u not in pkUserName:
            raise(ValueError("Username not registred."))
        else:
            return u

class Expense(BaseModel):
    userName:str
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float = Field(gt=0)
    expenseDate:date

    @field_validator("userName")
    def checkUserName(cls, u:str) -> str:
        if u not in pkUserName:
            raise(ValueError("Username not registred."))
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
        return text("INSERT INTO fato_expense VALUES (:userName,:idFrequencyType,:idExpenseSubCategory,:value,:expenseDate);")


class Income(BaseModel):
    idFrequencyType:int
    idIncomeCategory:int
    value:float
    incomeDate:str
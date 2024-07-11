from pydantic import BaseModel, Field, field_validator, SecretStr, EmailStr
from database import engine, text, TextClause
from datetime import date

def getUserSet() -> set:
    with engine.connect() as conn:
        res = conn.execute(text(f'SELECT username FROM users;'))
        return {v[0] for v in res.fetchall()}
def getFK(fk:str) -> set:
    with engine.connect() as conn:
        res = conn.execute(text(f'SELECT "{fk}" FROM "dim_{fk[2].lower()+fk[3:]}";'))
        return {v[0] for v in res.fetchall()}
fkIncomeCategory = getFK("idIncomeCategory")

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
        if u not in getUserSet():
            raise(ValueError("username not registred."))
        else:
            return u

    @field_validator("idFrequencyType")
    def checkFrequencyType(cls, x:int) -> int:
        if x not in getFK("idFrequencyType"):
            raise (ValueError("No match to constraint in Foreing Key idFrequencyType"))
        else:
            return x

    @field_validator("idExpenseSubCategory")
    def checkExpenseSubCategory(cls, x:int) -> int:
        if x not in getFK("idExpenseSubCategory"):
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
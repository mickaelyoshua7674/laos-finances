from pydantic import BaseModel, Field, field_validator, SecretStr, EmailStr
from database import engine, text, TextClause
from datetime import date

def getUserSet() -> set:
    with engine.connect() as conn:
        res = conn.execute(text(f'SELECT email FROM users;'))
        return {v[0] for v in res.fetchall()}
def getFK(fk:str) -> set:
    with engine.connect() as conn:
        res = conn.execute(text(f'SELECT "{fk}" FROM "dim_{fk[2].lower()+fk[3:]}";'))
        return {v[0] for v in res.fetchall()}
fkIncomeCategory = getFK("idIncomeCategory")

class User(BaseModel):
    email:EmailStr = Field(pattern=r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
    name:str
    password:SecretStr

    @classmethod
    def getInsertScript(cls) -> TextClause:
        return text("INSERT INTO users VALUES (:email,:name,:password);")

    @classmethod
    def fromList(cls, tpl:list|tuple):
        return cls(**{k:v for k,v in zip(cls.model_fields,tpl)})

class Expense(BaseModel):
    id:int = Field(ge=0)
    email:EmailStr = Field(pattern=r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float = Field(gt=0)
    expenseDate:date

    @field_validator("email")
    def checkusername(cls, u:str) -> str:
        if u not in getUserSet():
            raise ValueError("Email not registred.")
        else:
            return u

    @field_validator("idFrequencyType")
    def checkFrequencyType(cls, x:int) -> int:
        if x not in getFK("idFrequencyType"):
            raise ValueError("No match to constraint in Foreing Key idFrequencyType")
        else:
            return x

    @field_validator("idExpenseSubCategory")
    def checkExpenseSubCategory(cls, x:int) -> int:
        if x not in getFK("idExpenseSubCategory"):
            raise ValueError("No match to constraint in Foreing Key idExpenseSubCategory")
        else:
            return x
    
    @classmethod
    def getInsertScript(cls) -> TextClause:
        return text(
            'INSERT INTO fato_expense (email,"idFrequencyType","idExpenseSubCategory",value,"expenseDate") VALUES  (:email,:idFrequencyType,:idExpenseSubCategory,:value,:expenseDate) RETURNING id;')

    def getUpdateScript(self) -> TextClause:
        return text(
        f'UPDATE fato_expense SET "idFrequencyType"=:idFrequencyType, "idExpenseSubCategory"=:idExpenseSubCategory, value=:value, "expenseDate"=:expenseDate WHERE id={self.id};')
    
    def validateID(self) -> bool:
        with engine.connect() as conn:
            res = conn.execute(text(f"SELECT id FROM fato_expense WHERE id={self.id}")).fetchone()
        if res:
            return True
        return False

    @classmethod
    def fromList(cls, tpl:list|tuple):
        return cls(**{k:v for k,v in zip(cls.model_fields,tpl)})


class Income(BaseModel):
    id:int
    email:EmailStr = Field(pattern=r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
    idFrequencyType:int
    idIncomeCategory:int
    value:float
    incomeDate:str
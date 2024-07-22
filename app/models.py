from pydantic import BaseModel, Field, field_validator, SecretStr, EmailStr
from database import engine, text, TextClause
from datetime import date
from uuid import UUID

def getFK(fk:str) -> set:
    with engine.connect() as conn:
        res = conn.execute(text(f'SELECT "{fk}" FROM "dim_{fk[2].lower()+fk[3:]}";'))
        return {v[0] for v in res.fetchall()}
fkIncomeCategory = getFK("idIncomeCategory")

class User(BaseModel):
    userid:UUID = UUID("e0a79a89-1f3d-4af2-b627-8b3a697347d9")
    username:EmailStr = Field(pattern=r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?")
    name:str
    password:SecretStr

    @classmethod
    def getInsertScript(cls) -> TextClause:
        return text("INSERT INTO users (username,name,password) VALUES (:username,:name,:password) RETURNING userid;")

    @classmethod
    def fromList(cls, tpl:list|tuple):
        return cls(**{k:v for k,v in zip(cls.model_fields,tpl)})

class Expense(BaseModel):
    id:int = Field(ge=0, default=0)
    userid:UUID
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float = Field(gt=0)
    expenseDate:date

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
        'INSERT INTO fato_expense (userid,"idFrequencyType","idExpenseSubCategory",value,"expenseDate") VALUES  (:userid,:idFrequencyType,:idExpenseSubCategory,:value,:expenseDate) RETURNING id;')

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
    id:int = Field(ge=0, default=0)
    userid:UUID
    idFrequencyType:int
    idIncomeCategory:int
    value:float = Field(gt=0)
    incomeDate:date

    @field_validator("idFrequencyType")
    def checkFrequencyType(cls, x:int) -> int:
        if x not in getFK("idFrequencyType"):
            raise ValueError("No match to constraint in Foreing Key idFrequencyType")
        else:
            return x

    @field_validator("idIncomeCategory")
    def checkIncomeCategory(cls, x:int) -> int:
        if x not in getFK("idIncomeCategory"):
            raise ValueError("No match to constraint in Foreing Key idIncomeCategory")
        else:
            return x
    
    @classmethod
    def getInsertScript(cls) -> TextClause:
        return text(
        'INSERT INTO fato_income (userid,"idFrequencyType","idIncomeCategory",value,"incomeDate") VALUES (:userid,:idFrequencyType,:idIncomeCategory,:value,:incomeDate) RETURNING id;')

    def getUpdateScript(self) -> TextClause:
        return text(
        f'UPDATE fato_income SET "idFrequencyType"=:idFrequencyType, "idIncomeCategory"=:idIncomeCategory, value=:value, "incomeDate"=:incomeDate WHERE id={self.id};')
    
    def validateID(self) -> bool:
        with engine.connect() as conn:
            res = conn.execute(text(f"SELECT id FROM fato_income WHERE id={self.id}")).fetchone()
        if res:
            return True
        return False

    @classmethod
    def fromList(cls, tpl:list|tuple):
        return cls(**{k:v for k,v in zip(cls.model_fields,tpl)})
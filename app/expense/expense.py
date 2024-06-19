from database import pkUserName, fkFrequencyType, fkExpenseSubCategory
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from datetime import date

class Expense(BaseModel):
    userName:str
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float = Field(gt=0)
    expenseDate:date

    @field_validator("userName")
    @classmethod
    def checkUserName(cls, u:str) -> str:
        if u not in pkUserName:
            raise(ValueError("Username not registred."))
        else:
            return u

    @field_validator("idFrequencyType")
    @classmethod
    def checkFrequencyType(cls, x:int) -> int:
        if x not in fkFrequencyType:
            raise (ValueError("No match to constraint in Foreing Key idFrequencyType"))
        else:
            return x

    @field_validator("idExpenseSubCategory")
    @classmethod
    def checkExpenseSubCategory(cls, x:int) -> int:
        if x not in fkExpenseSubCategory:
            raise (ValueError("No match to constraint in Foreing Key idExpenseSubCategory"))
        else:
            return x

insertScriptExpense = text("INSERT INTO fato_expense VALUES (:userName,:idFrequencyType,:idExpenseSubCategory,:value,:expenseDate);")
from database import fkFrequencyType, fkExpenseSubCategory
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from datetime import date

class Expense(BaseModel):
    idUser:int
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float = Field(gt=0)
    expenseDate:date

    @field_validator("idFrequencyType")
    @classmethod
    def fkFrequencyType(cls, x):
        if x not in fkFrequencyType:
            raise (ValueError("No match to constraint in Foreing Key idFrequencyType"))
        else:
            return x

    @field_validator("idExpenseSubCategory")
    @classmethod
    def fkExpenseSubCategory(cls, x):
        if x not in fkExpenseSubCategory:
            raise (ValueError("No match to constraint in Foreing Key idExpenseSubCategory"))
        else:
            return x

insertScriptExpense = text("INSERT INTO fato_expense VALUES (:idUser,:idFrequencyType,:idExpenseSubCategory,:value,:expenseDate);")
from database import fkFrequencyType, fkExpenseSubCategory
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import text
from datetime import date

class Expense(BaseModel):
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float = Field(gt=0)
    expenseDate:date

    @field_validator("idFrequencyType")
    def fkFrequencyType(cls, x):
        if x not in fkFrequencyType:
            raise (ValueError("No match to constraint in Foreing Key idFrequencyType"))

    @field_validator("idExpenseSubCategory")
    def fkExpenseSubCategory(cls, x):
        if x not in fkExpenseSubCategory:
            raise (ValueError("No match to constraint in Foreing Key idExpenseSubCategory"))

insertScriptExpense = text('INSERT INTO fato_expense VALUES (:idFrequencyType,:idExpenseSubCategory,:value,:expenseDate);')
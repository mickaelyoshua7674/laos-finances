from pydantic import BaseModel
from sqlalchemy import text
from datetime import date

class Expense(BaseModel):
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float
    expenseDate:date

insertScriptExpense = text('INSERT INTO fato_expense VALUES (:idFrequencyType,:idExpenseSubCategory,:value,:expenseDate);')
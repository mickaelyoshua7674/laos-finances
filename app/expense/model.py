from pydantic import BaseModel
from sqlalchemy import text

class Expense(BaseModel):
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float
    expenseDate:str

insertScriptExpense = text("INSERT INTO fat_expense VALUES (:idFrequencyType, :idExpenseSubCategory, :value, :expenseDate);")
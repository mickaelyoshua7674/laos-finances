from pydantic import BaseModel, Field
from sqlalchemy import text

class Expense(BaseModel):
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float
    expenseDate:str = Field(pattern=r"(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[12])-(19|20)[0-9]{2}")

insertScriptExpense = text("INSERT INTO fato_expense VALUES (:idFrequencyType, :idExpenseSubCategory, :value, :expenseDate);")
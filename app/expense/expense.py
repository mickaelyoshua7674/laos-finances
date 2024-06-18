from pydantic import BaseModel
from sqlalchemy import text
from datetime import date

class Expense(BaseModel):
    idFrequencyType:int
    idExpenseSubCategory:int
    value:float
    expenseDate:date

    @classmethod
    def fromTuple(cls, tpl):
        print({k: v for k, v in zip(cls.model_fields.keys(), tpl)})
        return cls(**{k: v for k, v in zip(cls.model_fields.keys(), tpl)})

insertScriptExpense = text('INSERT INTO fato_expense VALUES (:idFrequencyType,:idExpenseSubCategory,:value,:expenseDate);')
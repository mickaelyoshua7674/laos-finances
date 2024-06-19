from pydantic import BaseModel, Field, SecretStr, field_validator
from database import pkUserName

class User(BaseModel):
    userName:str
    name:str
    email:str = Field(pattern=r"^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$")
    password:SecretStr

    @field_validator("userName")
    @classmethod
    def checkUserName(cls, u:str) -> str:
        if u not in pkUserName:
            raise(ValueError("Username not registred."))
        else:
            return u
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from enum import Enum


class Gender(str, Enum):
    Masculino = 'Masculino'
    Femenino = 'Femenino'


class UserModelGet(BaseModel):
    id: int | None
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    birth_date: datetime
    gender: Gender

class UserModelPost(BaseModel):
    first_name: str 
    last_name: str
    username: str
    email: EmailStr
    birth_date: datetime
    gender: Gender
    password_hash: str

    #validator for data type null
    @validator("first_name","last_name","username","email","birth_date","gender","password_hash")
    def convert_to_none(cls,value): #cls == UserModelPost
        if isinstance(value, str) and value.strip() == "":
            return None
        return value
    
class UserModelPut(BaseModel):
    username: str
    first_name: str
    last_name: str
    email : EmailStr

from pydantic import BaseModel

class GetCategory(BaseModel):
    id : int
    name : str

class PostCategory(BaseModel):
    name : str

class PutCategory(BaseModel):
    new_name : str
    old_name : str
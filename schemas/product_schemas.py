from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class StateOfProduct(str, Enum):
    Active = "Active"
    Desactive = "Desactive"

class ProductGet(BaseModel):
    unique_id : int
    name : str
    description : str
    price : float
    category_name : str
    stock : int
    sku : str
    created_at : datetime
    updated_at : datetime 
    status : StateOfProduct
    brand : str
    
class ProductPost(BaseModel):
    name : str
    description : str
    price : float
    category_name : str 
    stock : int
    created_at : datetime
    updated_at : datetime
    status : StateOfProduct
    brand : str

class ProductPut(BaseModel):
    name : str
    description : str
    price : int
    category_name : str
    stock : int
    status : StateOfProduct
    brand : str
    sku : str

class ProductDelete(BaseModel):
    sku : str

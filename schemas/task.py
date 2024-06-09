from pydantic import BaseModel
from datetime import datetime

class TasksModelGet(BaseModel):
    id: int
    title: str
    description: str| None
    created_at:datetime | None

    user_id : int

    def dict(self, **kwargs):
        # Override the default dict method
        data = super().dict(**kwargs)
        data['created_at'] = data['created_at'].strftime("%d/%m/%Y %H:%M:%S")  # Format and replace
        return data

class TasksModelPost(BaseModel):
    title: str
    description: str

class TasksModelSave(BaseModel):
    id: int
    title: str
    description: str
    user_id: int

class TaskModelDelete(BaseModel):
    title: str

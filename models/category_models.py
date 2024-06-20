from config.db import Base 
from sqlalchemy import Column, Integer, String

from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)

    product = relationship("Task", backref="category")

    def __init__(self,**kwargs):
        self.name = kwargs.get("name")
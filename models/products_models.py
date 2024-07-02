from config.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime

class Product(Base):
    __tablename__ = "product"

    unique_id = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=False)
    stock = Column(Integer, nullable=False)
    sku = Column(String, nullable=False) #SKU (Stock Keeping Unit): Un código único para identificar el producto en inventario.
    created_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    status = Column(Enum("Active","Desactive", name="state_of_product"), nullable=False)
    brand = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.price = kwargs.get("price")
        self.category_id = kwargs.get("category_id")
        self.stock = kwargs.get("stock")
        self.sku = kwargs.get("sku")
        self.updated_at = kwargs.get("updated_at")
        self.status = kwargs.get("status").value
        self.brand = kwargs.get("brand")


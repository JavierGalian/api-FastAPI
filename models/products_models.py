from config.db import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import hashlib

class Product(Base):
    __tablename__ = "product"

    unique_id = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category_name = Column(String, ForeignKey("category.name"), nullable=False)
    stock = Column(Integer, nullable=False)
    sku = Column(String, nullable=False, unique=True) #SKU (Stock Keeping Unit): Un código único para identificar el producto en inventario.
    created_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    updated_at = Column(DateTime, nullable=True)
    status = Column(Enum("Active","Desactive", name="state_of_product"), nullable=False)
    brand = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.price = kwargs.get("price")
        self.category_name = kwargs.get("category_name")
        self.stock = kwargs.get("stock")
        self.sku = self.create_sku(kwargs.get("brand"), kwargs.get("name"), self.created_at, kwargs.get("user_id"))
        self.updated_at = kwargs.get("updated_at")
        self.status = kwargs.get("status").value
        self.brand = kwargs.get("brand")
        self.user_id = kwargs.get("user_id")

    def create_sku(self, brand, name, created_at,user_id):
        # Crear un hash basado en el nombre, la marca y la fecha de creación
        hash_input = f"{brand[:3].upper()}-{name[:3].upper()}-{created_at}-{user_id}".encode()
        sku_hash = hashlib.md5(hash_input).hexdigest()[:16]  # Utilizar solo los primeros 8 caracteres del hash
        return f"{brand[:3].upper()}-{name[:3].upper()}-{sku_hash}"


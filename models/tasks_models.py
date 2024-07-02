from config.db import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

class Task(Base):
    __tablename__ = "task"

    unique_id = Column(Integer, primary_key=True,autoincrement=True)
    id = Column(Integer, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(350))
    created_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user_id = Column (Integer, ForeignKey("user.id"), nullable=False)

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.title = kwargs.get("title")
        self.description = kwargs.get("description")
        self.user_id = kwargs.get("user_id")

    def formatted_created_at(self):
        # Ejemplo: Formatear la fecha y hora para mostrar solo la fecha
        return self.created_at.strftime("%d/%m/%Y %H:%M:%S")
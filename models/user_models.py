import argon2
from config.db import Base
from sqlalchemy import Column, Integer, String, Date, VARCHAR, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from argon2 import PasswordHasher



class UserModels(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True,autoincrement=True, unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(VARCHAR(255), nullable=False, unique=True)
    birth_date = Column(Date, nullable=False)
    gender = Column(Enum("Masculino","Femenino", name="gender_type"), nullable=False)
    password_hash = Column(String(100), nullable=False)  # Almacena el hash
    is_active = Column(Boolean, nullable=False, default=True)

    tasks = relationship("Task", backref="user")

    def __init__(self, **kwargs):
        self.first_name = kwargs.get("first_name")
        self.last_name = kwargs.get("last_name")
        self.username = kwargs.get("username")
        self.email = kwargs.get("email")
        self.birth_date = kwargs.get("birth_date")
        self.gender = kwargs.get("gender").value
        self.is_active = kwargs.get("is_active", True)
        self.password_hash = self.set_password(kwargs.get("password_hash"))


    def set_password(self, password):
        hasher = PasswordHasher()
        #self.password_hash = hasher.hash(password)  # Genera y almacena el hash
        return hasher.hash(password)

    def verify_password(self, password): #Verifica si el password ingresado es igual al hash del password de la base de datos
        hasher = PasswordHasher()
        try:
            hasher.verify(self.password_hash, password)
            return True
        except argon2.exceptions.VerificationError:
            return False
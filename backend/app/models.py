from sqlalchemy import Column, Integer, String
from database import Base

# Modelo do banco de dados
class Time(Base):
    __tablename__ = "times"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    divisao = Column(String, index=True)
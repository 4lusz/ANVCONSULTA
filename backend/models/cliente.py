from sqlalchemy import Column, Integer, String, Boolean
from backend.core.db_base import Base



class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)

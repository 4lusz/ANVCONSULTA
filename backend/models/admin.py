from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from backend.core.db_base import Base



class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)

    ativo = Column(Boolean, default=True)

    criado_em = Column(DateTime, default=datetime.utcnow)

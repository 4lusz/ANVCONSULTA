from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from backend.core.db_base import Base



class EmailCliente(Base):
    __tablename__ = "emails_cliente"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    email = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)

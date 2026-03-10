from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from backend.core.db_base import Base



class KeywordCliente(Base):
    __tablename__ = "keywords_cliente"

    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)

    expressao = Column(String, nullable=False)
    operador = Column(String, nullable=False)
    hora_inicio = Column(String, nullable=False)
    hora_fim = Column(String, nullable=False)

    ativo = Column(Boolean, default=True)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.cliente import Cliente
from backend.core.security import verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    senha: str


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.email == data.email).first()

    if not cliente or not cliente.ativo:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not verificar_senha(data.senha, cliente.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token(cliente.id)
    return {"access_token": token}

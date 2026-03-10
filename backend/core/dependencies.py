from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import decodificar_token
from backend.models.cliente import Cliente
from backend.models.admin import Admin

security = HTTPBearer()


class UsuarioLogado:
    def __init__(self, cliente: Cliente, tipo: str):
        self.cliente = cliente
        self.tipo = tipo  # "admin" ou "cliente"


# =========================
# AUTH POR TOKEN (CLIENTE)
# =========================

def get_usuario_logado(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UsuarioLogado:
    payload = decodificar_token(credentials.credentials)

    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario_id = payload.get("sub")
    tipo = payload.get("tipo")

    if not usuario_id or tipo != "cliente":
        raise HTTPException(status_code=401, detail="Token inválido")

    cliente = db.query(Cliente).filter(Cliente.id == usuario_id).first()

    if not cliente or not cliente.ativo:
        raise HTTPException(status_code=401, detail="Cliente inválido")

    return UsuarioLogado(cliente=cliente, tipo=tipo)


def get_cliente_logado(
    usuario: UsuarioLogado = Depends(get_usuario_logado),
):
    return usuario.cliente


# =========================
# AUTH POR COOKIE (ADMIN)
# =========================

def get_admin_logado(
    request: Request,
    db: Session = Depends(get_db)
):
    token = request.cookies.get("admin_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = decodificar_token(token)

    if not payload or payload.get("tipo") != "admin":
        raise HTTPException(status_code=403, detail="Acesso restrito ao admin")

    admin_id = payload.get("sub")
    admin = db.query(Admin).filter(Admin.id == admin_id).first()

    if not admin or not admin.ativo:
        raise HTTPException(status_code=401, detail="Admin inválido")

    return admin

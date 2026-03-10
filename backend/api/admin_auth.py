from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.database import get_db
from backend.core.security import verificar_senha, criar_token
from backend.models.admin import Admin

router = APIRouter(prefix="/admin-auth", tags=["Admin Auth"])


# =====================
# SCHEMAS
# =====================

class AdminLoginRequest(BaseModel):
    email: str
    senha: str


# =====================
# LOGIN ADMIN
# =====================

@router.post("/login")
def login_admin(
    data: AdminLoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(
        Admin.email == data.email
    ).first()

    if not admin:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not admin.ativo:
        raise HTTPException(status_code=403, detail="Admin desativado")

    if not verificar_senha(data.senha, admin.senha_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token(admin.id, "admin")

    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        samesite="lax",
        path="/"
    )

    return {"ok": True}

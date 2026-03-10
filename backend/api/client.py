from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.database import get_db
from backend.core.dependencies import get_cliente_logado
from backend.core.security import verificar_senha, criar_token
from backend.models.email_cliente import EmailCliente
from backend.models.keyword_cliente import KeywordCliente
from backend.models.cliente import Cliente
from backend.schemas.auth import LoginRequest
from sqlalchemy import text

router = APIRouter(prefix="/api/client", tags=["Cliente"])


# ================= LOGIN =================

@router.post("/login")
def login_cliente(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(
        Cliente.email == data.email
    ).first()

    if not cliente or not cliente.ativo:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    if not verificar_senha(data.senha, cliente.senha_hash):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")

    token = criar_token(cliente.id, "cliente")

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ================= EMAILS =================

@router.get("/emails")
def listar_emails_cliente(
    cliente=Depends(get_cliente_logado),
    db: Session = Depends(get_db)
):
    return db.query(EmailCliente).filter(
        EmailCliente.cliente_id == cliente.id
    ).all()


@router.post("/emails")
def adicionar_email_cliente(
    email: str,
    cliente=Depends(get_cliente_logado),
    db: Session = Depends(get_db)
):
    novo = EmailCliente(
        cliente_id=cliente.id,
        email=email,
        ativo=True
    )
    db.add(novo)
    db.commit()
    return {"ok": True}


@router.post("/emails/{email_id}/toggle")
def toggle_email(
    email_id: int,
    ativo: bool,
    cliente=Depends(get_cliente_logado),
    db: Session = Depends(get_db)
):
    email = db.query(EmailCliente).filter(
        EmailCliente.id == email_id,
        EmailCliente.cliente_id == cliente.id
    ).first()

    if not email:
        raise HTTPException(404, "Email não encontrado")

    email.ativo = ativo
    db.commit()
    return {"ok": True}


@router.delete("/emails/{email_id}")
def remover_email_cliente(
    email_id: int,
    cliente=Depends(get_cliente_logado),
    db: Session = Depends(get_db)
):
    db.query(EmailCliente).filter(
        EmailCliente.id == email_id,
        EmailCliente.cliente_id == cliente.id
    ).delete()
    db.commit()
    return {"ok": True}


# ================= KEYWORDS =================

class KeywordCreate(BaseModel):
    expressao: str
    operador: str
    hora_inicio: str | None = None
    hora_fim: str | None = None


@router.get("/keywords")
def listar_keywords_cliente(
    cliente=Depends(get_cliente_logado),
    db: Session = Depends(get_db)
):
    return db.query(KeywordCliente).filter(
        KeywordCliente.cliente_id == cliente.id
    ).all()


@router.post("/keywords")
def adicionar_keyword_cliente(
    payload: KeywordCreate,
    cliente=Depends(get_cliente_logado),
    db: Session = Depends(get_db)
):
    if payload.operador not in ("AND", "OR"):
        raise HTTPException(400, "Operador inválido")

    nova = KeywordCliente(
        cliente_id=cliente.id,
        expressao=payload.expressao,
        operador=payload.operador,
        hora_inicio=payload.hora_inicio,
        hora_fim=payload.hora_fim,
        ativo=True
    )

    db.add(nova)
    db.commit()
    return {"ok": True}


@router.delete("/keywords/{keyword_id}")
def remover_keyword_cliente(
    keyword_id: int,
    cliente=Depends(get_cliente_logado),
    db: Session = Depends(get_db)
):
    db.query(KeywordCliente).filter(
        KeywordCliente.id == keyword_id,
        KeywordCliente.cliente_id == cliente.id
    ).delete()
    db.commit()
    return {"ok": True}

@router.get("/me")
def get_me(cliente=Depends(get_cliente_logado)):
    return {
        "id": cliente.id,
        "nome": cliente.nome,
        "email": cliente.email
    }

# ================= ALERTAS =================

from sqlalchemy import text



@router.get("/alerts")
def listar_alertas_cliente(
    cliente=Depends(get_cliente_logado),
    db: Session = Depends(get_db)
):
    resultados = db.execute(
        text("""
            SELECT
                id,
                termos,
                trecho,
                url,
                created_at
            FROM alerts
            WHERE cliente_id = :cliente_id
            ORDER BY created_at DESC
            LIMIT 100
        """),
        {"cliente_id": cliente.id}
    ).mappings().all()

    return [
        {
            "id": r["id"],
            "termos": r["termos"],
            "linha": r["trecho"],
            "url": r["url"],
            "created_at": r["created_at"]
        }
        for r in resultados
    ]



from fastapi.responses import FileResponse
import os

@router.get("/alerts/{alert_id}/pdf")
def baixar_pdf_alerta(
    alert_id: int,
    cliente=Depends(get_cliente_logado),
    db: Session = Depends(get_db)
):
    alerta = db.execute(
        text("""
        SELECT pdf_path
        FROM alerts
        WHERE id = :id
          AND cliente_id = :cliente_id
        """),
        {
            "id": alert_id,
            "cliente_id": cliente.id
        }
    ).mappings().first()

    if not alerta or not alerta["pdf_path"]:
        raise HTTPException(status_code=404, detail="PDF não encontrado")

    caminho = alerta["pdf_path"]

    if not os.path.isfile(caminho):
        raise HTTPException(status_code=404, detail="Arquivo não existe")

    return FileResponse(
        caminho,
        media_type="application/pdf",
        filename=os.path.basename(caminho)
    )

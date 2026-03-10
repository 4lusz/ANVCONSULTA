from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

import main
from backend.core.monitor_state import monitor_state
from backend.core.database import get_db
from backend.core.security import hash_senha
from backend.core.dependencies import get_admin_logado

from backend.models.cliente import Cliente
from backend.models.email_cliente import EmailCliente
from backend.models.keyword_cliente import KeywordCliente

router = APIRouter(prefix="/admin", tags=["Admin"])


# =====================
# SCHEMAS
# =====================

class ClienteCreate(BaseModel):
    nome: str
    email: str
    senha: str


class EmailCreate(BaseModel):
    email: str


class KeywordCreate(BaseModel):
    expressao: str
    operador: str
    hora_inicio: str
    hora_fim: str


class KeywordUpdate(BaseModel):
    expressao: str
    operador: str
    hora_inicio: str
    hora_fim: str


# =====================
# MONITOR
# =====================

@router.get("/status")
def status():
    return monitor_state

# =====================
# MANUTENÇÃO
# =====================

@router.post("/maintenance")
def set_maintenance(
    ativo: int = Query(...),
    admin=Depends(get_admin_logado)
):
    monitor_state["maintenance_mode"] = bool(ativo)
    return {
        "ok": True,
        "maintenance_mode": monitor_state["maintenance_mode"]
    }

@router.get("/start")
def start(admin=Depends(get_admin_logado)):
    main.start_monitor()
    return {"ok": True}


@router.get("/stop")
def stop(admin=Depends(get_admin_logado)):
    main.stop_monitor()
    return {"ok": True}


# =====================
# CLIENTES (ADMIN)
# =====================

@router.get("/clientes")
def listar_clientes(
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    return db.query(Cliente).order_by(Cliente.id.desc()).all()


@router.post("/clientes")
def criar_cliente(
    payload: ClienteCreate,
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    existe = db.query(Cliente).filter(Cliente.email == payload.email).first()
    if existe:
        raise HTTPException(400, "Email já cadastrado")

    cliente = Cliente(
        nome=payload.nome,
        email=payload.email,
        senha_hash=hash_senha(payload.senha),
        ativo=True
    )

    db.add(cliente)
    db.commit()
    return {"ok": True}


@router.post("/clientes/{cliente_id}/toggle")
def toggle_cliente(
    cliente_id: int,
    ativo: bool,
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado")

    cliente.ativo = ativo
    db.commit()
    return {"ok": True}


@router.delete("/clientes/{cliente_id}")
def remover_cliente(
    cliente_id: int,
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    db.query(EmailCliente).filter(
        EmailCliente.cliente_id == cliente_id
    ).delete()

    db.query(KeywordCliente).filter(
        KeywordCliente.cliente_id == cliente_id
    ).delete()

    db.query(Cliente).filter(
        Cliente.id == cliente_id
    ).delete()

    db.commit()
    return {"ok": True}


# =====================
# EMAILS (POR CLIENTE)
# =====================

@router.get("/emails")
def listar_emails(
    cliente_id: int = Query(...),
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    return db.query(EmailCliente).filter(
        EmailCliente.cliente_id == cliente_id
    ).all()


@router.post("/emails")
def adicionar_email(
    payload: EmailCreate,
    cliente_id: int = Query(...),
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    email = EmailCliente(
        cliente_id=cliente_id,
        email=payload.email,
        ativo=True
    )
    db.add(email)
    db.commit()
    return {"ok": True}


@router.post("/emails/{email_id}/toggle")
def toggle_email(
    email_id: int,
    ativo: bool,
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    email = db.query(EmailCliente).filter(
        EmailCliente.id == email_id
    ).first()

    if not email:
        raise HTTPException(404, "Email não encontrado")

    email.ativo = ativo
    db.commit()
    return {"ok": True}


@router.delete("/emails/{email_id}")
def remover_email(
    email_id: int,
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    db.query(EmailCliente).filter(
        EmailCliente.id == email_id
    ).delete()

    db.commit()
    return {"ok": True}


# =====================
# KEYWORDS (POR CLIENTE)
# =====================

from fastapi import Query

@router.get("/keywords")
def get_keywords(
    cliente_id: int = Query(...),
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    return db.query(KeywordCliente).filter(
        KeywordCliente.cliente_id == cliente_id
    ).all()


@router.post("/keywords")
def adicionar_keyword(
    payload: KeywordCreate,
    cliente_id: int = Query(...),
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    keyword = KeywordCliente(
        cliente_id=cliente_id,
        expressao=payload.expressao,
        operador=payload.operador,
        hora_inicio=payload.hora_inicio,
        hora_fim=payload.hora_fim,
        ativo=True
    )
    db.add(keyword)
    db.commit()
    return {"ok": True}


@router.put("/keywords/{keyword_id}")
def atualizar_keyword(
    keyword_id: int,
    payload: KeywordUpdate,
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    keyword = db.query(KeywordCliente).filter(
        KeywordCliente.id == keyword_id
    ).first()

    if not keyword:
        raise HTTPException(404, "Keyword não encontrada")

    keyword.expressao = payload.expressao
    keyword.operador = payload.operador
    keyword.hora_inicio = payload.hora_inicio
    keyword.hora_fim = payload.hora_fim
    db.commit()
    return {"ok": True}


@router.post("/keywords/{keyword_id}/toggle")
def toggle_keyword(
    keyword_id: int,
    ativo: bool,
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    keyword = db.query(KeywordCliente).filter(
        KeywordCliente.id == keyword_id
    ).first()

    if not keyword:
        raise HTTPException(404, "Keyword não encontrada")

    keyword.ativo = ativo
    db.commit()
    return {"ok": True}


@router.delete("/keywords/{keyword_id}")
def remover_keyword(
    keyword_id: int,
    admin=Depends(get_admin_logado),
    db: Session = Depends(get_db)
):
    db.query(KeywordCliente).filter(
        KeywordCliente.id == keyword_id
    ).delete()

    db.commit()
    return {"ok": True}

# =====================
# AUTH CHECK (ADMIN)
# =====================

@router.get("/me")
def admin_me(admin=Depends(get_admin_logado)):
    return {
        "ok": True,
        "id": admin.id,
        "email": admin.email
    }
# =====================
# LOOP INTERVAL
# =====================

from fastapi import Query

@router.post("/loop-interval")
def atualizar_loop_interval(
    segundos: int = Query(...),
    admin=Depends(get_admin_logado)
):
    monitor_state["loop_interval"] = segundos
    return {
        "ok": True,
        "loop_interval": segundos
    }

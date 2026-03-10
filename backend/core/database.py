import sqlite3
import os
from datetime import datetime

CAMINHO_DB = os.path.join(os.path.dirname(__file__), "..", "..", "monitor.db")


#  CONEXÃO 

def conectar():
    conn = sqlite3.connect(CAMINHO_DB)
    conn.row_factory = sqlite3.Row
    return conn


# CRIAÇÃO DE TABELAS

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()



    # KEYWORDS_CLIENTES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords_cliente (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            expressao TEXT NOT NULL,
            operador TEXT NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fim TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)


  

    #  CLIENTES 
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ================= ADMINS =================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ================= ALERTAS =================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            cliente_nome TEXT NOT NULL,
            termos TEXT NOT NULL,
            trecho TEXT NOT NULL,
            url TEXT NOT NULL,
            alert_hash TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_alert_dedupe
        ON alerts (cliente_id, alert_hash)
    """)

    # ================= ATOS PROCESSADOS =================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_acts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            processed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ================= EMAILS (POR CLIENTE) =================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    # ================= KEYWORDS (AND / OR + HORÁRIO) =================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            expressao TEXT NOT NULL,
            operador TEXT CHECK (operador IN ('AND', 'OR')) NOT NULL,
            hora_inicio TEXT NOT NULL,
            hora_fim TEXT NOT NULL,
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    conn.commit()
    conn.close()

    garantir_cliente_padrao()


# ================= CLIENTE PADRÃO =================

def garantir_cliente_padrao():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO clientes (id, nome)
        VALUES (1, 'Default')
    """)

    conn.commit()
    conn.close()


# ================= ATOS =================

def ato_ja_processado(url: str) -> bool:
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM processed_acts WHERE url = ? LIMIT 1",
        (url,)
    )

    existe = cursor.fetchone() is not None
    conn.close()
    return existe


def marcar_ato_processado(url: str):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO processed_acts (url) VALUES (?)",
        (url,)
    )

    conn.commit()
    conn.close()


# ================= ALERTAS =================

def alerta_ja_enviado(cliente_id: int, alert_hash: str) -> bool:
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM alerts
        WHERE cliente_id = ? AND alert_hash = ?
        LIMIT 1
    """, (cliente_id, alert_hash))

    existe = cursor.fetchone() is not None
    conn.close()
    return existe


def salvar_alerta_db(alerta: dict):
    conn = conectar()
    cursor = conn.cursor()

    try:
        cursor.execute("""
    INSERT INTO alerts (
        cliente_id,
        cliente_nome,
        termos,
        trecho,
        url,
        alert_hash,
        pdf_path,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    alerta.get("cliente_id"),
    alerta.get("cliente"),
    alerta.get("termos"),
    alerta.get("trecho"),
    alerta.get("url"),
    alerta.get("alert_hash"),
    alerta.get("pdf_path"),
    datetime.now()
))



        conn.commit()

    except sqlite3.IntegrityError:
        pass

    finally:
        conn.close()


# ================= LIMPEZA =================

def limpar_alertas_antigos(dias: int = 90):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM alerts
        WHERE created_at < datetime('now', ?)
    """, (f"-{dias} days",))

    conn.commit()
    conn.close()


def limpar_atos_processados_antigos(dias: int = 30):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM processed_acts
        WHERE processed_at < datetime('now', ?)
    """, (f"-{dias} days",))

    conn.commit()
    conn.close()


# ================= EMAILS =================

from backend.models.email_cliente import EmailCliente
from backend.core.db_base import Base



def listar_emails(cliente_id: int):
    db = SessionLocal()
    try:
        rows = (
            db.query(EmailCliente)
            .filter(EmailCliente.cliente_id == cliente_id)
            .all()
        )

        return [
            {
                "id": e.id,
                "email": e.email,
                "ativo": e.ativo
            }
            for e in rows
        ]
    finally:
        db.close()



def adicionar_email(cliente_id: int, email: str):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO emails (cliente_id, email)
        VALUES (?, ?)
    """, (cliente_id, email))

    conn.commit()
    conn.close()


def remover_email(email_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM emails WHERE id = ?", (email_id,))
    conn.commit()
    conn.close()


def alternar_email(email_id: int, ativo: bool):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE emails SET ativo = ? WHERE id = ?
    """, (1 if ativo else 0, email_id))

    conn.commit()
    conn.close()


# ================= CLIENTES =================

def listar_clientes():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM clientes
        ORDER BY nome ASC
    """)

    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def criar_cliente(nome: str):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO clientes (nome)
        VALUES (?)
    """, (nome,))

    conn.commit()
    conn.close()


def alternar_cliente(cliente_id: int, ativo: bool):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE clientes SET ativo = ? WHERE id = ?
    """, (1 if ativo else 0, cliente_id))

    conn.commit()
    conn.close()


def remover_cliente(cliente_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM emails WHERE cliente_id = ?", (cliente_id,))
    cursor.execute("DELETE FROM keywords WHERE cliente_id = ?", (cliente_id,))
    cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))

    conn.commit()
    conn.close()




# ================= KEYWORDS =================

from backend.models.keyword_cliente import KeywordCliente



def listar_keywords(cliente_id: int):
    db = SessionLocal()
    try:
        rows = (
            db.query(KeywordCliente)
            .filter(KeywordCliente.cliente_id == cliente_id)
            .all()
        )

        return [
            {
                "id": k.id,
                "expressao": k.expressao,
                "operador": k.operador,
                "hora_inicio": k.hora_inicio,
                "hora_fim": k.hora_fim,
                "ativo": k.ativo
            }
            for k in rows
        ]
    finally:
        db.close()

 


def adicionar_keyword(
    cliente_id: int,
    expressao: str,
    operador: str,
    hora_inicio: str,
    hora_fim: str
):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO keywords (
            cliente_id, expressao, operador, hora_inicio, hora_fim
        )
        VALUES (?, ?, ?, ?, ?)
    """, (cliente_id, expressao, operador, hora_inicio, hora_fim))

    conn.commit()
    conn.close()


def alternar_keyword(keyword_id: int, ativo: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE keywords
        SET ativo = ?
        WHERE id = ?
    """, (ativo, keyword_id))

    conn.commit()
    conn.close()



def remover_keyword(keyword_id: int):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM keywords WHERE id = ?", (keyword_id,))
    conn.commit()
    conn.close()



def atualizar_keyword(keyword_id, expressao, operador, hora_inicio, hora_fim):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE keywords
        SET expressao = ?, operador = ?, hora_inicio = ?, hora_fim = ?
        WHERE id = ?
    """, (expressao, operador, hora_inicio, hora_fim, keyword_id))

    conn.commit()
    conn.close()

# ==========================================================
# ORM (SQLAlchemy) - USADO APENAS PELA API (LOGIN / CLIENTE)
# ==========================================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = f"sqlite:///{CAMINHO_DB}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

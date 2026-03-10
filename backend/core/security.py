from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

SECRET_KEY = "MUDE_ESSA_CHAVE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 12

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =====================
# SENHAS
# =====================

def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha, senha_hash)


# =====================
# TOKENS
# =====================

def criar_token(user_id: int, tipo: str) -> str:
    payload = {
        "sub": str(user_id),
        "tipo": tipo,
        "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decodificar_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        payload["sub"] = int(payload["sub"])
        return payload
    except JWTError:
        return None

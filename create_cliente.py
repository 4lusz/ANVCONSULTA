from backend.core.database import conectar
from backend.core.security import hash_senha

conn = conectar()
cursor = conn.cursor()

email = "cliente@teste.com"
senha = "123456"

cursor.execute("""
    INSERT INTO clientes (nome, email, senha_hash, ativo)
    VALUES (?, ?, ?, 1)
""", (
    "Cliente Teste",
    email,
    hash_senha(senha)
))

conn.commit()
conn.close()

print("Cliente criado com sucesso")
print("Email:", email)
print("Senha:", senha)

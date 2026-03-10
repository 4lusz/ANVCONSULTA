from backend.core.database import conectar
from backend.core.security import hash_senha

# ======== CONFIGURE AQUI ========
NOME = "AluADM"
EMAIL = "aluisiomprado@gmail.com"
SENHA = "aluisio110205"
# ================================

def criar_admin():
    conn = conectar()
    cursor = conn.cursor()

    senha_hash = hash_senha(SENHA)

    cursor.execute("""
        INSERT INTO admins (nome, email, senha_hash, ativo)
        VALUES (?, ?, ?, 1)
    """, (NOME, EMAIL, senha_hash))

    conn.commit()
    conn.close()

    print("✅ Admin criado com sucesso!")
    print(f"📧 Email: {EMAIL}")
    print(f"🔑 Senha: {SENHA}")


if __name__ == "__main__":
    criar_admin()

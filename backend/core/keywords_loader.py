from backend.core.database import conectar


def carregar_keywords():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            k.id as keyword_id,
            k.cliente_id,
            c.nome as cliente_nome,
            k.expressao,
            k.operador,
            k.hora_inicio,
            k.hora_fim
        FROM keywords k
        JOIN clientes c ON c.id = k.cliente_id
        WHERE k.ativo = 1
          AND c.ativo = 1
    """)

    keywords = cursor.fetchall()

    entidades = []

    for k in keywords:
        cursor.execute("""
            SELECT email
            FROM emails
            WHERE cliente_id = ?
              AND ativo = 1
        """, (k["cliente_id"],))

        emails_rows = cursor.fetchall()
        emails = [r["email"].lower() for r in emails_rows if r["email"]]

        if not emails:
            continue

        termos = [
            t.strip().lower()
            for t in k["expressao"].split()
            if t.strip()
        ]

        if not termos:
            continue

        entidades.append({
            "cliente_id": k["cliente_id"],
            "cliente_nome": k["cliente_nome"],
            "email": emails,
            "termos": termos,
            "tipo": k["operador"],
            "horario_inicio": k["hora_inicio"],
            "horario_fim": k["hora_fim"]
        })

    conn.close()
    return entidades

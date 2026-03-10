import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def gerar_resumo_ia(texto_ato: str) -> str:
    """
    Gera um resumo curto e objetivo do texto do ato.
    Retorna string simples. Não lança exceção pra cima.
    """
    if not texto_ato or len(texto_ato.strip()) < 50:
        return ""

    # Limite de segurança
    texto_ato = texto_ato[:8000]

    prompt = f"""
Você é um assistente especializado em análise regulatória.

Resuma o texto abaixo em no máximo 3 frases curtas,
em linguagem objetiva e profissional.
Não invente informações e não faça recomendações.

Texto:
\"\"\"
{texto_ato}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você resume atos regulatórios."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=120,
        )

        resumo = response.choices[0].message.content.strip()
        return resumo

    except Exception as e:
        print(f"[IA] Falha ao gerar resumo: {e}")
        return ""

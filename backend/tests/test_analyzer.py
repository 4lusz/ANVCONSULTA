from backend.core.analyzer import verificar_alertas

TEXTO_TESTE = """
A anvisa publicou hoje nova resolucao relacionada a regulacao sanitaria.
O medicamento para importacao foi aprovado apos longa analise tecnica,
incluindo estudos de seguranca, eficacia e impacto regulatorio.
"""



URL_FAKE = "https://teste.local/ato/123"


if __name__ == "__main__":
    total = verificar_alertas(TEXTO_TESTE, URL_FAKE)
    print("Total de alertas gerados:", total)

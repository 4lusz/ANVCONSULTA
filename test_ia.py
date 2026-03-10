from dotenv import load_dotenv
load_dotenv()
from backend.core.ia_resumo import gerar_resumo_ia

texto_teste = """
RESOLUÇÃO DA DIRETORIA COLEGIADA - RDC Nº 123, DE 10 DE MAIO DE 2024

Dispõe sobre requisitos para importação de produtos para saúde,
estabelece critérios técnicos e administrativos e dá outras providências.
"""

resumo = gerar_resumo_ia(texto_teste)
print("RESUMO IA:")
print(resumo)

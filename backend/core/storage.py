import os
from datetime import datetime
import re


def salvar_texto_ato(texto, url_ato):
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    pasta_base = os.path.join("textos", data_hoje)
    os.makedirs(pasta_base, exist_ok=True)

    # extrair um id do ato pela URL
    match = re.search(r"-(\d{6,})$", url_ato)
    ato_id = match.group(1) if match else str(int(datetime.now().timestamp()))

    nome_arquivo = f"ato_{ato_id}.txt"
    caminho = os.path.join(pasta_base, nome_arquivo)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)

    return caminho

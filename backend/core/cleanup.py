import os
import shutil
from datetime import datetime, timedelta


def limpar_arquivos_antigos(base_path: str, dias: int = 7):
    """
    Remove pastas/arquivos mais antigos que X dias.
    Espera pastas nomeadas como YYYY-MM-DD.
    """

    if not os.path.exists(base_path):
        return

    hoje = datetime.now()
    limite = hoje - timedelta(days=dias)

    for nome in os.listdir(base_path):
        caminho = os.path.join(base_path, nome)

        if not os.path.isdir(caminho):
            continue

        try:
            data_pasta = datetime.strptime(nome, "%Y-%m-%d")
        except ValueError:
            continue  # ignora pastas fora do padrão

        if data_pasta < limite:
            shutil.rmtree(caminho)
            print(f"[CLEANED] Removido: {caminho}")

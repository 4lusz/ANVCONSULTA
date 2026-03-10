

import time
import traceback
from backend.main import main
raise RuntimeError("daemon.py desativado")

INTERVALO = 15 * 60  # 15 minutos

print("[START] ANVISA-MONITOR DAEMON INICIADO")

while True:
    try:
        print("\n[NEW] Iniciando novo ciclo...")
        main()
        print("[OK] Ciclo finalizado com sucesso")

    except Exception as e:
        print("[ERRO] ERRO NO CICLO:")
        traceback.print_exc()

    print(f"[WAIT] Aguardando {INTERVALO//60} minutos para o próximo ciclo...\n")
    time.sleep(INTERVALO)

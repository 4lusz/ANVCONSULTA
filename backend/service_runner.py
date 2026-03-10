import time
import traceback

from backend.main import main
from backend.core.monitor_state import monitor_state

INTERVALO_PADRAO = 15 * 60      # 15 minutos
INTERVALO_MINIMO = 30          # 30 segundos

print("[START] ANVISA-MONITOR SERVICE INICIADO")

while True:
    try:
        print("\n[NEW] Novo ciclo iniciado")
        main()
        print("[DONE] Ciclo finalizado com sucesso")

    except Exception:
        print("[ERRO] ERRO NO CICLO")
        traceback.print_exc()

    #  intervalo vem do estado global (controlado pelo admin)
    intervalo = monitor_state.get("loop_interval", INTERVALO_PADRAO)

    if intervalo < INTERVALO_MINIMO:
        print(
            f"[WARN] Intervalo {intervalo}s abaixo do minimo, "
            f"ajustando para {INTERVALO_MINIMO}s"
        )
        intervalo = INTERVALO_MINIMO

    print(f"[WAIT] Aguardando {intervalo // 60} minutos ({intervalo}s)...\n")
    time.sleep(intervalo)

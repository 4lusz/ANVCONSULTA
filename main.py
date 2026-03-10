import time
import signal
import sys
import traceback
import threading
import random
from datetime import datetime

from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env", override=True)
print("[ENV]", os.getenv("OPENAI_API_KEY"))

from backend.core.monitor_state import monitor_state
from backend.core.selenium_setup import iniciar_driver
from backend.core.selenium_anvisa_search import buscar_atos_anvisa
from backend.core.selenium_ato_processor import processar_ato
from backend.core.storage import salvar_texto_ato
from backend.core.analyzer import verificar_alertas

from backend.core.database import (
    criar_tabelas,
    ato_ja_processado,
    marcar_ato_processado,
    limpar_alertas_antigos,
    limpar_atos_processados_antigos
)
from backend.core.cleanup import limpar_arquivos_antigos


driver = None
RUNNING = False
monitor_thread = None


def shutdown_handler(sig, frame):
    print("\n[STOP] Interrupção detectada, finalizando...")
    stop_monitor()
    sys.exit(0)


def executar_ciclo():
    global driver

    print("\n[START] Novo ciclo ANVISA-MONITOR")

    monitor_state["last_cycle_start"] = datetime.now()
    monitor_state["last_error"] = None
    monitor_state["last_error_time"] = None
    monitor_state["retry_count"] = 0

    limpar_alertas_antigos(dias=2)
    limpar_atos_processados_antigos(dias=5)
    limpar_arquivos_antigos("textos", dias=7)
    limpar_arquivos_antigos("pdfs", dias=7)

    driver = iniciar_driver()

    try:
        print("[SEARCH] Buscando atos da ANVISA...")

        MAX_TENTATIVAS = 3
        tentativa = 0
        links = []

        while tentativa < MAX_TENTATIVAS and RUNNING:
            try:
                links = buscar_atos_anvisa(driver)
                break
            except Exception as e:
                tentativa += 1
                monitor_state["retry_count"] = tentativa
                monitor_state["last_error"] = str(e)
                monitor_state["last_error_time"] = datetime.now()

                print(
                    f"[WARN] Erro de rede "
                    f"(tentativa {tentativa}/{MAX_TENTATIVAS})"
                )
                print(e)
                time.sleep(10)

        if not links:
            print("[ERROR] Nenhum ato encontrado, ciclo ignorado")
            return

        print(f"[INFO] Atos encontrados: {len(links)}")

        for i, link in enumerate(links, start=1):
            if not RUNNING:
                print("[STOP] Monitor interrompido durante o ciclo")
                break

            print("\n==============================")
            print(f"[PROCESS] Ato {i}/{len(links)}")
            print(f"[LINK] {link}")

            if ato_ja_processado(link):
                print("[SKIP] Já processado")
                continue

            MAX_RETRY_ATO = 2
            tentativa_ato = 0

            while tentativa_ato < MAX_RETRY_ATO and RUNNING:
                try:
                    resultado = processar_ato(driver, link)

                    if resultado:
                        if isinstance(resultado, dict):
                            texto = resultado.get("texto")
                            pdf_path = resultado.get("pdf_path")
                        else:
                            texto = resultado
                            pdf_path = None

                        if texto:
                            caminho = salvar_texto_ato(texto, link)
                            print(f"[SAVE] Texto salvo em: {caminho}")
                            total = verificar_alertas(texto, link, pdf_path)
                            print(f"[ALERT] Alertas gerados: {total}")

                            marcar_ato_processado(link)
                        else:
                            print("[WARN] Texto vazio ou ato ignorado")
                    else:
                        print("[WARN] Texto vazio ou ato ignorado")

                    break

                except Exception as e:
                    tentativa_ato += 1
                    monitor_state["last_error"] = str(e)
                    monitor_state["last_error_time"] = datetime.now()

                    print(
                        f"[WARN] Falha ao processar ato "
                        f"(tentativa {tentativa_ato}/{MAX_RETRY_ATO})"
                    )
                    print(e)
                    time.sleep(5)

            time.sleep(random.uniform(6, 10))

        monitor_state["last_success"] = datetime.now()

    except Exception as e:
        monitor_state["last_error"] = str(e)
        monitor_state["last_error_time"] = datetime.now()
        print("[ERROR] Erro inesperado no ciclo")
        print(e)

    finally:
        monitor_state["last_cycle_end"] = datetime.now()
        print("[END] Ciclo finalizado")

        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        driver = None


def monitor_loop():
    global RUNNING

    print("[BOOT] Monitor em execução")

    while RUNNING:
        executar_ciclo()

        if not RUNNING:
            break

        intervalo = monitor_state.get("loop_interval", 900)

        if intervalo < 30:
            print("[WARN] Intervalo muito baixo, ajustado para 30s")
            intervalo = 30

        print(f"[WAIT] Dormindo {intervalo} segundos...\n")
        time.sleep(intervalo)

    print("[STOP] Monitor parado")


def start_monitor():
    global RUNNING, monitor_thread

    if RUNNING:
        print("[INFO] Monitor já está rodando")
        return False

    criar_tabelas()

    RUNNING = True
    monitor_state["running"] = True

    monitor_thread = threading.Thread(
        target=monitor_loop,
        daemon=True
    )
    monitor_thread.start()

    return True


def stop_monitor():
    global RUNNING

    if not RUNNING:
        return False

    RUNNING = False
    monitor_state["running"] = False

    if driver:
        try:
            driver.quit()
        except Exception:
            pass

    return True


def main():
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    criar_tabelas()
    start_monitor()

    while RUNNING:
        time.sleep(1)


if __name__ == "__main__":
    main()


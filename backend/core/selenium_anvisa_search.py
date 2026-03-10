from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time

DOU_BUSCA_ANVISA_URL = "https://www.in.gov.br/consulta/-/buscar/dou?q=anvisa"


def buscar_atos_anvisa(driver, timeout=45, max_tentativas=3):
    print("[SEARCH] Iniciando busca de atos da ANVISA no DOU")

    for tentativa in range(1, max_tentativas + 1):
        print(f"[SEARCH] Tentativa {tentativa}/{max_tentativas}")

        try:
            driver.set_page_load_timeout(timeout)
            driver.get(DOU_BUSCA_ANVISA_URL)
        except TimeoutException:
            print("[WARN] Timeout ao carregar a página do DOU")
            _esperar_retry(tentativa)
            continue
        except WebDriverException as e:
            print("[ERROR] Erro crítico ao abrir página do DOU")
            print(e)
            _esperar_retry(tentativa)
            continue

        try:
            wait = WebDriverWait(driver, timeout)
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "a[href*='/web/dou/']")
                )
            )
        except TimeoutException:
            print("[WARN] Página carregou, mas nenhum ato foi renderizado")
            _esperar_retry(tentativa)
            continue

        try:
            elementos = driver.find_elements(By.CSS_SELECTOR, "a[href*='/web/dou/']")
        except WebDriverException:
            print("[WARN] Falha ao coletar elementos do DOM")
            _esperar_retry(tentativa)
            continue

        links = []
        for el in elementos:
            try:
                href = el.get_attribute("href")
                if href and "/web/dou/" in href and href not in links:
                    links.append(href)
            except WebDriverException:
                continue

        if links:
            print(f"[INFO] Atos encontrados na busca: {len(links)}")
            return links

        print("[INFO] Busca retornou zero atos")
        _esperar_retry(tentativa)

    print("[WARN] Falha persistente ao buscar atos no DOU")
    return []


def _esperar_retry(tentativa):
    if tentativa < 3:
        espera = 10 * tentativa
        print(f"[WAIT] Aguardando {espera}s antes de nova tentativa")
        time.sleep(espera)

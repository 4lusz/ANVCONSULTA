from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


def baixar_pdfs_anvisa_dia(driver):
    """
    Abre a lista de atos do dia atual,
    encontra TODOS os atos da ANVISA
    e baixa o PDF individual (versão certificada) de cada um.
    """

    wait = WebDriverWait(driver, 20)

    # 1. Abre lista de atos do dia
    driver.get("https://www.in.gov.br/leiturajornal?data=16-12-2025")
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    time.sleep(3)

    # 2. Garante que estamos vendo a lista (não o diário completo)
    # Cada ato aparece como um "card"
    cards = driver.find_elements(By.XPATH, "//div[contains(@class,'resultado-item')]")

    print(f"[SEARCH] Total de atos encontrados no dia: {len(cards)}")

    atos_anvisa = []

    for card in cards:
        try:
            texto = card.text.upper()
            if "AGÊNCIA NACIONAL DE VIGILÂNCIA SANITÁRIA" in texto or "ANVISA" in texto:
                link = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                atos_anvisa.append(link)
        except Exception:
            continue

    print(f" Atos da ANVISA encontrados: {len(atos_anvisa)}")

    # 3. Para cada ato da ANVISA, entra e baixa o PDF
    for i, link_ato in enumerate(atos_anvisa, start=1):
        print(f"[INFO] [{i}/{len(atos_anvisa)}] Abrindo ato:")
        print(f"   {link_ato}")

        driver.get(link_ato)

        try:
            botao_pdf = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(., 'Versão certificada')]")
                )
            )

            botao_pdf.click()
            print("   ⬇ PDF solicitado")

            # tempo para download completar
            time.sleep(8)

        except TimeoutException:
            print("    Botão de PDF não encontrado")
            continue

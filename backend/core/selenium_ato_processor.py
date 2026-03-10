from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from datetime import datetime
import requests
import pdfplumber
import os
import time
import re


PDF_DIR = "pdfs_tmp"
os.makedirs(PDF_DIR, exist_ok=True)


def ato_eh_do_dia(driver):
    hoje = datetime.now().strftime("%d/%m/%Y")
    html = driver.page_source
    return hoje in html


def baixar_pdf_com_cookies(driver, pdf_url, nome_arquivo):
    session = requests.Session()

    for cookie in driver.get_cookies():
        session.cookies.set(cookie["name"], cookie["value"])

    headers = {
        "User-Agent": driver.execute_script("return navigator.userAgent;"),
        "Referer": driver.current_url
    }

    response = session.get(pdf_url, headers=headers, timeout=30)

    if response.status_code != 200:
        raise Exception(f"Erro ao baixar PDF: {response.status_code}")

    caminho = os.path.join(PDF_DIR, nome_arquivo)

    with open(caminho, "wb") as f:
        f.write(response.content)

    return caminho


def extrair_texto_pdf(caminho_pdf):
    texto = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            t = pagina.extract_text()
            if t:
                texto.append(t)

    return "\n".join(texto)


def _fechar_alert_se_existir(driver):
    try:
        alert = driver.switch_to.alert
        print("[INFO] Alert detectado, fechando...")
        alert.accept()
    except Exception:
        pass


def _buscar_pdf_url_fallback(driver, wait):
    try:
        frame = wait.until(
            EC.presence_of_element_located((By.NAME, "visualizador"))
        )
        return frame.get_attribute("src")
    except TimeoutException:
        print("[INFO] iframe 'visualizador' não encontrado")

    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            src = iframe.get_attribute("src")
            if src and ".pdf" in src.lower():
                print("[INFO] PDF encontrado via iframe alternativo")
                return src
    except Exception:
        pass

    try:
        embeds = driver.find_elements(By.TAG_NAME, "embed")
        for embed in embeds:
            src = embed.get_attribute("src")
            if src and ".pdf" in src.lower():
                print("[INFO] PDF encontrado via embed")
                return src
    except Exception:
        pass

    try:
        objects = driver.find_elements(By.TAG_NAME, "object")
        for obj in objects:
            data = obj.get_attribute("data")
            if data and ".pdf" in data.lower():
                print("[INFO] PDF encontrado via object")
                return data
    except Exception:
        pass

    return None


def processar_ato(driver, url_ato, timeout=30):
    try:
        print(f"\n[INFO] Abrindo ato: {url_ato}")

        # ===== PROTEÇÃO DE LOAD =====
        driver.set_page_load_timeout(timeout)

        tentou = 0
        while tentou < 2:
            try:
                driver.get(url_ato)
                break
            except (TimeoutException, WebDriverException) as e:
                tentou += 1
                print(f"[WARN] Timeout ao abrir ato (tentativa {tentou}/2)")
                if tentou >= 2:
                    return None
                time.sleep(3)

        wait = WebDriverWait(driver, timeout)

        _fechar_alert_se_existir(driver)

        if not ato_eh_do_dia(driver):
            print("[SKIP] Ato não é do dia atual")
            return None

        try:
            botao = wait.until(
                EC.element_to_be_clickable((By.ID, "versao-certificada"))
            )
            botao.click()
            print("[OK] Versão Certificada aberta")
        except Exception as e:
            print("[ERRO] Falha ao clicar em Versão Certificada")
            print(e)
            return None

        time.sleep(2)
        _fechar_alert_se_existir(driver)

        pdf_url = _buscar_pdf_url_fallback(driver, wait)

        if not pdf_url:
            print("[ERRO] Não foi possível localizar o PDF por iframe/embed/object")
            return None

        print("[OK] URL do PDF encontrada:")
        print(pdf_url)

        nome_pdf = f"ato_{int(time.time())}.pdf"
        try:
            caminho_pdf = baixar_pdf_com_cookies(driver, pdf_url, nome_pdf)
            print(f"[SAVE] PDF salvo em: {caminho_pdf}")
        except Exception as e:
            print("[ERRO] Erro ao baixar PDF")
            print(e)
            return None

        texto = extrair_texto_pdf(caminho_pdf)

        if not texto.strip():
            print("[WARNING] PDF baixado, mas texto vazio")
            return None

        print("[INFO] TEXTO EXTRAÍDO (preview):")
        print(texto[:500])
        print("-" * 60)

        return {
    "texto": texto,
    "pdf_path": caminho_pdf
}


    except Exception as e:
        print("[WARN] Erro inesperado ao processar ato")
        print(e)
        return None

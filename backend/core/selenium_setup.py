from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time


def iniciar_driver():
    chrome_options = Options()

    # ===== HEADLESS MODERNO =====
    chrome_options.add_argument("--headless=new")

    # ===== FLAGS DE ESTABILIDADE (LINUX / SERVER) =====
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")

    # ===== VIEWPORT REAL =====
    chrome_options.add_argument("--window-size=1920,1080")

    # ===== USER AGENT REAL =====
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    # ===== LOCALIZAÇÃO =====
    chrome_options.add_argument("--lang=pt-BR")

    # ===== REMOVE FLAGS DE AUTOMAÇÃO =====
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"]
    )
    chrome_options.add_experimental_option(
        "useAutomationExtension", False
    )

    # ===== DOWNLOADS =====
    pasta_downloads = os.path.abspath("pdfs")
    os.makedirs(pasta_downloads, exist_ok=True)

    prefs = {
        "download.default_directory": pasta_downloads,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": False
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # ===== INICIA DRIVER =====
    driver = webdriver.Chrome(options=chrome_options)

    # ===== FORÇA RESOLUÇÃO VIA CDP =====
    driver.execute_cdp_cmd(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": 1920,
            "height": 1080,
            "deviceScaleFactor": 1,
            "mobile": False
        }
    )

    # ===== REMOVE navigator.webdriver + ALERTS =====
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.alert = function() {};
                window.confirm = function() { return true; };
                window.prompt = function() { return null; };
            """
        }
    )

    # ===== AQUECIMENTO DO CHROME =====
    try:
        driver.get("https://www.google.com")
        time.sleep(2)
    except Exception:
        pass

    return driver

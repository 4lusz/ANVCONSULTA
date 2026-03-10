from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os

def iniciar_driver(download_dir):
    options = Options()
    options.add_argument("--start-maximized")

    prefs = {
        "download.default_directory": os.path.abspath(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }

    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)
    return driver

from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def build_chrome_driver(*, headless: bool) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-notifications")
    options.page_load_strategy = 'eager'
    
    # Indha line dhaan script mudinjadhum browser close aagama thadukkum!
    options.add_experimental_option("detach", True)

    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    
    return driver

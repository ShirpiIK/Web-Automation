from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def build_chrome_driver(*, headless: bool) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-notifications")
    
    # Idhu dhaan romba mukkiyam! Full page load aaga wait pannama udane adutha step pogum
    options.page_load_strategy = 'eager'

    if headless:
        options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=options)
    
    # 30 seconds ku mela load aana automatic aah stop panni error kaatidum
    driver.set_page_load_timeout(30)
    
    return driver

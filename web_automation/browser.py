from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def build_chrome_driver(*, headless: bool) -> webdriver.Chrome:
    options = Options()
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-notifications")

    if headless:
        options.add_argument("--headless=new")

    return webdriver.Chrome(options=options)

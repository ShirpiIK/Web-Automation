from __future__ import annotations

from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from web_automation.config import Settings


EMAIL_SELECTORS = [
    "input[type='email']",
    "input[name='email']",
    "input[name='username']",
    "input#email",
    "input#username",
]

PASSWORD_SELECTORS = [
    "input[type='password']",
    "input[name='password']",
    "input#password",
]

SUBMIT_SELECTORS = [
    "button[type='submit']",
    "input[type='submit']",
]

LOGIN_SUCCESS_SELECTORS = [
    "a[href*='/account/logout']",
    "a[href='/account']",
    "a[href*='/account/']",
    "button[aria-label*='account' i]",
    "button[aria-label*='profile' i]",
]

ERROR_SELECTORS = [
    ".error",
    ".alert",
    "[role='alert']",
    ".login-error",
]


class InternetArchiveLogin:
    def __init__(self, driver: WebDriver, settings: Settings) -> None:
        self.driver = driver
        self.settings = settings
        self.wait = WebDriverWait(driver, settings.timeout_seconds)

    def run(self) -> bool:
        self.driver.get(self.settings.login_url)

        email_input = self._first_visible_css(EMAIL_SELECTORS)
        password_input = self._first_visible_css(PASSWORD_SELECTORS)

        self._replace_text(email_input, self.settings.internet_archive_email)
        self._replace_text(password_input, self.settings.internet_archive_password)

        submit_button = self._first_clickable_css(SUBMIT_SELECTORS)
        submit_button.click()

        try:
            self.wait.until(self._login_completed)
        except TimeoutException as exc:
            error_message = self._visible_error_message()
            if error_message:
                raise RuntimeError(f"Internet Archive login failed: {error_message}") from exc
            raise RuntimeError(
                "Login was not confirmed. If a CAPTCHA, OTP, or verification page appeared, "
                "complete it manually and run again."
            ) from exc

        if self.settings.save_login_screenshot:
            self.save_screenshot("login-success.png")

        return True

    def save_screenshot(self, file_name: str) -> Path:
        output_dir = Path("artifacts") / "screenshots"
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / file_name
        self.driver.save_screenshot(str(path))
        return path

    def _first_visible_css(self, selectors: list[str]) -> WebElement:
        last_error: TimeoutException | None = None
        for selector in selectors:
            try:
                return self.wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
                )
            except TimeoutException as exc:
                last_error = exc

        joined = ", ".join(selectors)
        raise TimeoutException(f"Could not find a visible element matching: {joined}") from last_error

    def _first_clickable_css(self, selectors: list[str]) -> WebElement:
        last_error: TimeoutException | None = None
        for selector in selectors:
            try:
                return self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            except TimeoutException as exc:
                last_error = exc

        joined = ", ".join(selectors)
        raise TimeoutException(f"Could not find a clickable element matching: {joined}") from last_error

    def _replace_text(self, element: WebElement, value: str) -> None:
        element.clear()
        element.send_keys(value)

    def _login_completed(self, driver: WebDriver) -> bool:
        current_url = driver.current_url.lower()
        if "/login" not in current_url and "/account/login" not in current_url:
            return True

        for selector in LOGIN_SUCCESS_SELECTORS:
            if self._has_visible_element(selector):
                return True

        return False

    def _has_visible_element(self, selector: str) -> bool:
        return any(element.is_displayed() for element in self.driver.find_elements(By.CSS_SELECTOR, selector))

    def _visible_error_message(self) -> str:
        messages = []
        for selector in ERROR_SELECTORS:
            for element in self.driver.find_elements(By.CSS_SELECTOR, selector):
                if element.is_displayed() and element.text.strip():
                    messages.append(element.text.strip())
        return " ".join(messages)

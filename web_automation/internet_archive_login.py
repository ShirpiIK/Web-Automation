from __future__ import annotations

from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from web_automation.config import Settings


Locator = tuple[str, str]


EMAIL_LOCATORS: list[Locator] = [
    (By.CSS_SELECTOR, "input[type='email']"),
    (By.CSS_SELECTOR, "input[name='email']"),
    (By.CSS_SELECTOR, "input[name='emailAddress']"),
    (By.CSS_SELECTOR, "input[name='username']"),
    (By.CSS_SELECTOR, "input[name='identifier']"),
    (By.CSS_SELECTOR, "input[autocomplete='email']"),
    (By.CSS_SELECTOR, "input#email"),
    (By.CSS_SELECTOR, "input#username"),
    (By.CSS_SELECTOR, "input#identifier"),
    (By.XPATH, "//label[contains(normalize-space(), 'Email address')]/following::input[1]"),
    (
        By.XPATH,
        "//*[self::label or self::div or self::span]"
        "[contains(normalize-space(), 'Email address')]/following::input[1]",
    ),
]

PASSWORD_LOCATORS: list[Locator] = [
    (By.CSS_SELECTOR, "input[type='password']"),
    (By.CSS_SELECTOR, "input[name='password']"),
    (By.CSS_SELECTOR, "input[autocomplete='current-password']"),
    (By.CSS_SELECTOR, "input#password"),
    (By.XPATH, "//label[contains(normalize-space(), 'Password')]/following::input[1]"),
    (
        By.XPATH,
        "//*[self::label or self::div or self::span]"
        "[contains(normalize-space(), 'Password')]/following::input[1]",
    ),
]

SUBMIT_LOCATORS: list[Locator] = [
    (By.XPATH, "//button[normalize-space()='Log in']"),
    (By.XPATH, "//button[normalize-space()='Log In']"),
    (By.CSS_SELECTOR, "button[type='submit']"),
    (By.CSS_SELECTOR, "input[type='submit']"),
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

        email_input = self._first_visible_locator(EMAIL_LOCATORS, "email address field")
        password_input = self._first_visible_locator(PASSWORD_LOCATORS, "password field")

        self._replace_text(email_input, self.settings.internet_archive_email)
        self._replace_text(password_input, self.settings.internet_archive_password)

        submit_button = self._first_clickable_locator(SUBMIT_LOCATORS, "Log in button")
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

    def _first_visible_locator(self, locators: list[Locator], name: str) -> WebElement:
        last_error: TimeoutException | None = None
        for locator in locators:
            try:
                return self.wait.until(
                    EC.visibility_of_element_located(locator)
                )
            except TimeoutException as exc:
                last_error = exc

        searched = "; ".join(f"{by}={value}" for by, value in locators)
        raise TimeoutException(
            f"Could not find the visible {name}. Searched: {searched}"
        ) from last_error

    def _first_clickable_locator(self, locators: list[Locator], name: str) -> WebElement:
        last_error: TimeoutException | None = None
        for locator in locators:
            try:
                return self.wait.until(
                    EC.element_to_be_clickable(locator)
                )
            except TimeoutException as exc:
                last_error = exc

        searched = "; ".join(f"{by}={value}" for by, value in locators)
        raise TimeoutException(
            f"Could not find the clickable {name}. Searched: {searched}"
        ) from last_error

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

from __future__ import annotations

import time
from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from web_automation.config import Settings


EMAIL_SELECTORS = [
    "input[type='email']",
    "input[name='email']",
    "input[name='username']",
    ".login-form input[type='text']"
]

PASSWORD_SELECTORS = [
    "input[type='password']",
    "input[name='password']"
]

SUBMIT_SELECTORS = [
    "ia-button[type='submit']",
    "button[type='submit']",
    ".login-button"
]

class InternetArchiveLogin:
    def __init__(self, driver: WebDriver, settings: Settings) -> None:
        self.driver = driver
        self.settings = settings
        self.wait = WebDriverWait(driver, settings.timeout_seconds)

    def save_debug_info(self, step_name: str) -> None:
        output_dir = Path("artifacts") / "debug"
        output_dir.mkdir(parents=True, exist_ok=True)
        self.driver.save_screenshot(str(output_dir / f"{step_name}.png"))
        with open(output_dir / f"{step_name}.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        print(f"[DEBUG] Saved debug files for '{step_name}'")

    def _get_shadow_element(self, selectors: list[str]) -> WebElement | None:
        """JavaScript vazhiya Shadow DOM kulla elements ah thedura function."""
        js = """
        function findInShadows(selector, root = document.body) {
            let el = root.querySelector(selector);
            if (el) return el;
            let elements = root.querySelectorAll('*');
            for (let i = 0; i < elements.length; i++) {
                if (elements[i].shadowRoot) {
                    let found = findInShadows(selector, elements[i].shadowRoot);
                    if (found) return found;
                }
            }
            return null;
        }
        for (let sel of arguments[0]) {
            let el = findInShadows(sel);
            if (el) return el;
        }
        return null;
        """
        return self.driver.execute_script(js, selectors)

    def _wait_for_shadow_element(self, selectors: list[str], name: str) -> WebElement:
        """Element render aagura varaikum wait panni, adha scroll panni edukkum."""
        end_time = time.time() + self.settings.timeout_seconds
        while time.time() < end_time:
            el = self._get_shadow_element(selectors)
            if el:
                # Screen la theliva theriya center ku scroll pandrom
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", el)
                time.sleep(0.5) 
                return el
            time.sleep(1)
        raise TimeoutException(f"Could not find {name} inside Shadow DOM.")

    def run(self) -> bool:
        print("[INFO] Navigating to login URL...")
        self.driver.get(self.settings.login_url)
        self.save_debug_info("1_after_page_load")

        try:
            print("[INFO] Searching for email field...")
            email_input = self._wait_for_shadow_element(EMAIL_SELECTORS, "email address field")
            
            print("[INFO] Searching for password field...")
            password_input = self._wait_for_shadow_element(PASSWORD_SELECTORS, "password field")

            print("[INFO] Entering credentials...")
            # Shadow DOM ulla elements ku normal send_keys silar neram work aagadhu, so JS dispatch event use pandrom
            self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_input, self.settings.internet_archive_email)
            self.driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", password_input, self.settings.internet_archive_password)
            
            self.save_debug_info("2_after_entering_credentials")

            print("[INFO] Searching for submit button...")
            submit_button = self._wait_for_shadow_element(SUBMIT_SELECTORS, "Log in button")
            
            print("[INFO] Clicking submit button...")
            self.driver.execute_script("arguments[0].click();", submit_button)
            
            self.save_debug_info("3_after_submit_click")

            print("[INFO] Waiting for login to complete...")
            end_time = time.time() + self.settings.timeout_seconds
            logged_in = False
            while time.time() < end_time:
                # URL maariyurukka nu check pandrom
                if "/login" not in self.driver.current_url.lower():
                    logged_in = True
                    break
                # User profile icon login aanadhum varudha nu check pandrom
                if self._get_shadow_element(["a[href*='/account/logout']", "button[aria-label*='profile' i]"]):
                    logged_in = True
                    break
                time.sleep(1)
            
            if not logged_in:
                raise TimeoutException("Login completion check timed out. Verification page vandhurukalama nu check pannunga.")
            
        except TimeoutException as exc:
            print("[ERROR] Timeout occurred. Saving failure state...")
            self.save_debug_info("4_timeout_failure_state")
            raise RuntimeError("Login failed. Check artifacts/debug screenshots.") from exc
        except Exception as exc:
            print(f"[ERROR] Unexpected error: {exc}")
            self.save_debug_info("5_unexpected_error_state")
            raise

        if self.settings.save_login_screenshot:
            output_dir = Path("artifacts") / "screenshots"
            output_dir.mkdir(parents=True, exist_ok=True)
            self.driver.save_screenshot(str(output_dir / "login-success.png"))

        print("[INFO] Login completed successfully.")
        return True

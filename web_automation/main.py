from __future__ import annotations

import argparse
import sys

from web_automation.browser import build_chrome_driver
from web_automation.config import Settings
from web_automation.internet_archive_login import InternetArchiveLogin


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Log in to Internet Archive using Selenium."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run Chrome without opening a visible browser window.",
    )
    parser.add_argument(
        "--keep-open",
        action="store_true",
        help="Keep the browser open after the script finishes.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = Settings.from_env()
    settings.validate_credentials()

    if args.headless:
        settings = Settings(
            internet_archive_email=settings.internet_archive_email,
            internet_archive_password=settings.internet_archive_password,
            login_url=settings.login_url,
            headless=True,
            timeout_seconds=settings.timeout_seconds,
            keep_browser_open=settings.keep_browser_open,
            save_login_screenshot=settings.save_login_screenshot,
        )

    if args.keep_open:
        settings = Settings(
            internet_archive_email=settings.internet_archive_email,
            internet_archive_password=settings.internet_archive_password,
            login_url=settings.login_url,
            headless=settings.headless,
            timeout_seconds=settings.timeout_seconds,
            keep_browser_open=True,
            save_login_screenshot=settings.save_login_screenshot,
        )

    driver = build_chrome_driver(headless=settings.headless)

    try:
        InternetArchiveLogin(driver, settings).run()
        print("Login completed successfully.")
        return 0
    finally:
        if settings.keep_browser_open:
            print("Browser left open because KEEP_BROWSER_OPEN is enabled.")
        else:
            driver.quit()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)

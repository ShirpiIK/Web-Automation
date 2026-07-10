from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None or value.strip() == "":
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False

    raise ValueError(f"Invalid boolean value: {value!r}")


def _as_int(value: str | None, default: int) -> int:
    if value is None or value.strip() == "":
        return default
    return int(value)


@dataclass(frozen=True)
class Settings:
    internet_archive_email: str
    internet_archive_password: str
    login_url: str = "https://archive.org/account/login"
    headless: bool = False
    timeout_seconds: int = 30
    keep_browser_open: bool = False
    save_login_screenshot: bool = True

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()

        return cls(
            internet_archive_email=os.getenv("INTERNET_ARCHIVE_EMAIL", "").strip(),
            internet_archive_password=os.getenv("INTERNET_ARCHIVE_PASSWORD", ""),
            login_url=os.getenv(
                "INTERNET_ARCHIVE_LOGIN_URL",
                "https://archive.org/account/login",
            ).strip(),
            headless=_as_bool(os.getenv("LOGIN_HEADLESS"), False),
            timeout_seconds=_as_int(os.getenv("LOGIN_TIMEOUT_SECONDS"), 30),
            keep_browser_open=_as_bool(os.getenv("KEEP_BROWSER_OPEN"), False),
            save_login_screenshot=_as_bool(os.getenv("SAVE_LOGIN_SCREENSHOT"), True),
        )

    def validate_credentials(self) -> None:
        missing = []
        if not self.internet_archive_email:
            missing.append("INTERNET_ARCHIVE_EMAIL")
        if not self.internet_archive_password:
            missing.append("INTERNET_ARCHIVE_PASSWORD")

        if missing:
            names = ", ".join(missing)
            raise ValueError(
                f"Missing {names}. Create a .env file from .env.example and fill it in."
            )

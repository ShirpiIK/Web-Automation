# Web Automation

Selenium automation for logging in to an Internet Archive account.

## What This Project Does

- Opens the Internet Archive login page.
- Reads your email and password from a local `.env` file.
- Logs in with Selenium.
- Verifies whether the login appears successful.

The first goal is only login automation. More actions can be added later.

## Setup

1. Open this folder in VS Code:

   ```powershell
   C:\Users\Admin\OneDrive\Documents\web automation
   ```

2. Create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

4. Create your private `.env` file:

   ```powershell
   Copy-Item .env.example .env
   ```

5. Open `.env` and fill in your Internet Archive email and password.

   Do not commit `.env` to GitHub.

## Run

```powershell
python -m web_automation.main
```

By default, the browser opens visibly so you can watch what happens.

## Notes

- If Internet Archive shows a CAPTCHA, OTP, or extra verification, complete it manually in the browser.
- Credentials stay in `.env`, which is ignored by Git.
- Screenshots and logs are stored under `artifacts/`, which is also ignored by Git.

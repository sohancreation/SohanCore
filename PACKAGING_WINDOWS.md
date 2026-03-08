# Package SohanCore as a Windows `.exe` (PyInstaller)

## 1) Prerequisites

Install on the build machine:

1. Python 3.11 or 3.12 (64-bit).
2. Git.
3. Tesseract OCR (required for screen text extraction).
4. Microsoft Visual C++ Redistributable (x64).

Notes:
- Python 3.13 can work, but 3.11/3.12 is more predictable with Windows automation libs.
- Install Tesseract to `C:\Program Files\Tesseract-OCR` and add it to `PATH`.

## 2) Prepare project

From project root:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

Create `.env` from template:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set at minimum:
- `TELEGRAM_BOT_TOKEN`
- At least one provider key (`OPENROUTER_API_KEY` or `OPENAI_API_KEY`), or keep Ollama enabled.

### Telegram setup for end users

1. Open Telegram and chat with `@BotFather`.
2. Run `/newbot`.
3. Set bot name and username.
4. Copy the generated token.
5. Put token in `.env`:
   - `TELEGRAM_BOT_TOKEN=...`

### LLM setup options for end users

Option A: Cloud key
- Fill one key in `.env` such as `OPENROUTER_API_KEY` or `OPENAI_API_KEY`.

Option B: Local Ollama
1. Install Ollama from `https://ollama.com/download/windows`.
2. Pull model:
   ```powershell
   ollama pull gpt-oss:120b-cloud
   ```
3. Keep in `.env`:
   - `OLLAMA_BASE_URL=http://127.0.0.1:11434`
   - `LLM_PROVIDER_ORDER=ollama,openrouter,openai,gemini`

## 3) Local smoke test before build

```powershell
python main.py
```

Confirm:
- Telegram bot responds to `/start`.
- Normal text message returns a response.

Stop with `Ctrl+C`.

## 4) Build executable (recommended: `onedir`)

Fast path (one command):

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

Script flags:
- `-NoVenv`: use system Python instead of `.venv`.
- `-SkipInstall`: skip `pip install -r requirements.txt`.
- `-SkipPlaywright`: skip `playwright install chromium`.

GUI build (desktop app with graphical interface):

```powershell
powershell -ExecutionPolicy Bypass -File .\build_gui.ps1
```

GUI output:
- `dist\SohanCoreUI\SohanCoreUI.exe`

Manual command:

```powershell
pyinstaller --noconfirm --clean `
  --name SohanCore `
  --onedir `
  --console `
  --collect-all telegram `
  --collect-all playwright `
  --collect-all pywinauto `
  --collect-all pycaw `
  --collect-all cv2 `
  --collect-all PIL `
  --hidden-import=win32gui `
  --hidden-import=win32con `
  --hidden-import=win32process `
  --hidden-import=win32api `
  main.py
```

Output:
- `dist\SohanCore\SohanCore.exe`

Why `onedir`:
- More stable for Playwright/OpenCV/Windows automation than `onefile`.

## 5) Package for end users

Ship these together:

1. `dist\SohanCore\` folder
2. `.env.example` (rename to `.env` after user fills values)
3. `run_sohancore_background.bat` (provided below)

Optional:
- Zip all files into `SohanCore-Windows.zip`.

## 6) Run in background

Create `run_sohancore_background.bat` next to `SohanCore.exe`:

```bat
@echo off
setlocal
cd /d "%~dp0"
start "" /B "%~dp0SohanCore.exe"
exit /b 0
```

This starts without opening a persistent console window.

## 7) Auto-start on Windows login (optional)

Use Task Scheduler:

1. Open Task Scheduler -> `Create Task`.
2. `General`:
   - Name: `SohanCore Agent`
   - Run whether user is logged on or not.
3. `Triggers`:
   - New -> At log on.
4. `Actions`:
   - Start a program -> select `run_sohancore_background.bat`.
5. Save task and test `Run`.

## 8) Clean Windows environment test plan

Use Windows Sandbox or a fresh VM.

Test checklist:

1. Install Python and VC++ runtime.
2. Install Tesseract and verify:
   ```powershell
   tesseract --version
   ```
3. Extract packaged app.
4. Fill `.env` with a new Telegram bot token and provider key (or Ollama local endpoint).
5. Run `SohanCore.exe` once.
6. From Telegram:
   - `/start`
   - `/help`
   - a normal text prompt
7. Validate logs in `sohan_ai.log`.
8. Start via `run_sohancore_background.bat` and verify bot still responds.

Pass criteria:
- Bot starts without import errors.
- Bot responds to Telegram commands/messages.
- Background mode works after restart/login.

## 9) Common failures

1. `ModuleNotFoundError` in exe:
   - Rebuild with missing module in `--hidden-import` or `--collect-all`.
2. OCR not working:
   - Tesseract not installed or not in `PATH`.
3. Browser actions failing:
   - Run `playwright install chromium` on target machine.
4. LLM errors:
   - Invalid/missing API key in `.env`, or quota exceeded.

## 10) Build installable setup (.exe installer)

Install Inno Setup 6:
- https://jrsoftware.org/isinfo.php

Build setup package:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_installer.ps1
```

Installer output:
- `release\SohanCore-Setup.exe`

This installer deploys:
- `SohanCoreUI` desktop app
- backend `SohanCore` engine
- `.env.example` and initial `.env`
- Start menu shortcut and optional desktop shortcut

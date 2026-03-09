# SohanCore

SohanCore is a Windows-first AI assistant that combines a Telegram bot, desktop/browser automation, and multi-provider LLM routing.

## Quick Start For Users

If you only want to install and run the app (not build from source):

1. Go to the `release` folder.
2. Run `SohanCore-Setup.exe`.
3. Complete setup and open **SohanCore** from Start Menu.
4. Configure `.env` in the app folder:
   - `TELEGRAM_BOT_TOKEN`
   - `ALLOWED_USER_IDS`
   - At least one provider key (`OPENROUTER_API_KEY` or `OPENAI_API_KEY`) or local Ollama
5. Start the backend from the UI.
6. Open Telegram and message your bot.

It includes:
- A backend runtime service (`main.py`)
- A desktop control panel (`sohancore_gui.py`)
- Build scripts for Windows executables and installer packages

## Key Features

- Telegram-based command and chat interface
- Automation for desktop actions and web tasks
- Multi-provider LLM support (Ollama, OpenRouter, OpenAI, Gemini)
- Safety checks before executing sensitive actions
- Memory and task-learning components for better continuity

## Project Structure

- `main.py`: backend runtime entrypoint
- `sohancore_gui.py`: desktop UI and operational controls
- `bot_bridge/`: Telegram listener and execution bridge
- `brain/`: intent parsing, planning, orchestration
- `executor/`: desktop, browser, file, and code execution tools
- `memory/`: chat/task memory and embeddings support
- `safety/`: execution guardrails
- `installer/`: Inno Setup installer definition

## Installable Software Locations

After building locally, installable artifacts are generated here:

- Installer package (share this to other Windows users): `release\\SohanCore-Setup.exe`
- Backend app folder: `dist\\SohanCore\\` (`SohanCore.exe` inside)
- Desktop UI folder: `dist\\SohanCoreUI\\` (`SohanCoreUI.exe` inside)

If you publish releases on GitHub, upload `release\\SohanCore-Setup.exe` as the main installer asset.

## How To Use (End Users)

### Option 1: Installer (recommended)

1. Locate installer in `release\\SohanCore-Setup.exe`.
2. Run `SohanCore-Setup.exe`.
3. Complete installation.
4. Open **SohanCore** from Start Menu (launches UI).
5. In UI, open/edit `.env` and set:
   - `TELEGRAM_BOT_TOKEN`
   - `ALLOWED_USER_IDS`
   - At least one provider key (or configure Ollama)
6. Start the backend from UI controls.
7. Open Telegram and chat with your bot.

### Option 2: Portable executables (without installer)

1. Use `dist\\SohanCoreUI\\SohanCoreUI.exe` to open the UI.
2. Use `dist\\SohanCore\\SohanCore.exe` to run backend manually (if needed).
3. Keep `.env` in the project root with valid configuration.

## Developer Setup

### Requirements

- Windows 10/11
- Python 3.11 or 3.12 recommended
- Telegram account and bot token
- At least one LLM provider key or local Ollama

Optional for full feature coverage:
- Playwright Chromium runtime
- Tesseract OCR

### Local Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
Copy-Item .env.example .env
python main.py
```

Run UI separately:

```powershell
python sohancore_gui.py
```

## Build Commands

Build backend executable:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

Build UI executable:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_gui.ps1
```

Build installer:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_installer.ps1
```

## Troubleshooting

- Telegram `Conflict` error: another process is already polling the same bot token.
- Browser automation issues: run `playwright install chromium`.
- No model response: verify API key validity, quota, and provider order.
- OCR issues: verify Tesseract installation and PATH setup.

## Security Notes

- Never commit `.env` or real API keys.
- Restrict `ALLOWED_USER_IDS` to trusted Telegram IDs.
- Rotate compromised keys immediately.

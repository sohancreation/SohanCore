# SohanCore

SohanCore is a Windows-first personal desktop AI agent that combines a Telegram interface, multi-provider LLM routing, desktop/browser automation, and memory-backed execution loops.

The project includes:
- A backend agent runtime (`main.py`)
- A desktop control panel (`sohancore_gui.py`)
- Packaging scripts for standalone `.exe` and installer builds

## What The Application Does

SohanCore receives tasks from Telegram, interprets intent, plans execution, applies safety checks, runs actions through executor modules, and logs outcomes for future context.

Core capabilities include:
- Telegram bot command and message handling
- Multi-provider LLM usage (Ollama, OpenRouter, OpenAI, Gemini, Grok, DeepSeek)
- Desktop and browser interaction pipelines
- Local memory/cache components for context and learning
- GUI dashboard for setup, run/stop control, and live logs

## Architecture Overview

Top-level modules:
- `main.py`: backend runtime entrypoint and lifecycle management
- `sohancore_gui.py`: desktop control panel
- `bot_bridge/`: Telegram listener and bridge
- `brain/`: orchestration, planning, and agent-level reasoning
- `executor/`: action execution modules (browser, desktop, file/code utilities)
- `memory/`: memory store, cache, embeddings, experience learning
- `safety/`: safety guardrails
- `utils/`: shared infrastructure (logging, LLM client, analyzers)
- `installer/` + `build*.ps1`: packaging and installer automation

## Requirements

- Windows 10/11
- Python 3.11 or 3.12 recommended
- Telegram account (for bot integration)
- At least one LLM provider configured (or local Ollama)

Optional but commonly required for full feature set:
- Tesseract OCR
- Playwright Chromium runtime

## Quick Start (Developer)

1. Clone and enter the repo.
2. Create and activate virtual env:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
playwright install chromium
```

4. Create config file:

```powershell
Copy-Item .env.example .env
```

5. Edit `.env` and set:
- `TELEGRAM_BOT_TOKEN`
- `ALLOWED_USER_IDS` (comma-separated Telegram numeric IDs)
- At least one provider key (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, etc.) or Ollama settings

6. Run backend:

```powershell
python main.py
```

7. Run GUI (optional, recommended for operations):

```powershell
python sohancore_gui.py
```

## Secure Configuration Notes

- Never commit `.env` or real API tokens.
- Rotate tokens immediately if exposed.
- Restrict `ALLOWED_USER_IDS` to trusted accounts only.
- Keep `.env.example` as template-only values.

## Running The App

Backend runtime:
- `python main.py`

GUI control panel:
- `python sohancore_gui.py`

Helper scripts:
- `run_sohan_ai.bat`
- `run_sohancore_gui.bat`
- `run_sohancore_background.bat`

## Build and Distribution

Build backend executable:

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
```

Build GUI executable:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_gui.ps1
```

Build installer:

```powershell
powershell -ExecutionPolicy Bypass -File .\build_installer.ps1
```

Primary docs:
- `PACKAGING_WINDOWS.md`
- `SHAREABLE_INSTALLER.md`

## Troubleshooting

- Telegram conflict error: another process is polling the same bot token; stop the other process.
- No model response: verify provider key/quota or local Ollama availability.
- Browser automation issues: run `playwright install chromium`.
- OCR-dependent features failing: verify Tesseract installation and PATH.

## Project Status

This repository is actively evolving and includes runtime, packaging, and experimental support modules. Use tagged releases for stable distribution snapshots.


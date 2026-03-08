# Share SohanCore As Installable Software

## Build installer on your machine

1. Build core and UI executables (if not already built):
```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1 -SkipPlaywright
powershell -ExecutionPolicy Bypass -File .\build_gui.ps1 -SkipInstall
```

2. Install Inno Setup 6:
- https://jrsoftware.org/isinfo.php

3. Build installer:
```powershell
powershell -ExecutionPolicy Bypass -File .\build_installer.ps1
```

Output:
- `release\SohanCore-Setup.exe`

## What to share

Share only:
- `release\SohanCore-Setup.exe`

## What your users will do

1. Run `SohanCore-Setup.exe`.
2. Open `SohanCore` from Start Menu.
3. In `Setup Wizard` tab:
   - Create Telegram bot via `@BotFather`.
   - Copy bot token.
4. In `Configuration` tab:
   - Set `TELEGRAM_BOT_TOKEN`.
   - Set `ALLOWED_USER_IDS` (their Telegram numeric id).
   - Add at least one provider key, or configure Ollama.
5. Click `Save Configuration`.
6. Go to `Dashboard` tab and click `Start Agent`.
7. Send `/start` to their Telegram bot.

## Notes

- Installer path is user-local (`%LOCALAPPDATA%\SohanCore`), so no admin rights required.
- `Run In Background` works from GUI after install.

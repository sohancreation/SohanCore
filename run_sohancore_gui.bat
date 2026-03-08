@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0.venv\Scripts\pythonw.exe" (
    start "" /B "%~dp0.venv\Scripts\pythonw.exe" "%~dp0sohancore_gui.py"
) else (
    start "" /B pyw -3 "%~dp0sohancore_gui.py"
)

exit /b 0

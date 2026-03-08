@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0dist\SohanCore\SohanCore.exe" (
    start "" /B "%~dp0dist\SohanCore\SohanCore.exe"
) else if exist "%~dp0.venv\Scripts\pythonw.exe" (
    start "" /B "%~dp0.venv\Scripts\pythonw.exe" "%~dp0main.py"
) else (
    start "" /B pyw -3 "%~dp0main.py"
)

exit /b 0

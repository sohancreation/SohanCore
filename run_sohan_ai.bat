@echo off
setlocal
cd /d "%~dp0"
set "PYW=%LocalAppData%\Programs\Python\Python313\pythonw.exe"
if exist "%PYW%" (
    start "" /B "%PYW%" "%~dp0main.py"
) else (
    start "" /B pyw -3 "%~dp0main.py"
)
exit /b 0

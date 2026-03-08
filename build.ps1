param(
    [switch]$NoVenv,
    [switch]$SkipPlaywright,
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Resolve-Python {
    if (-not $NoVenv) {
        if (-not (Test-Path ".venv")) {
            py -3 -m venv .venv
        }
        return (Resolve-Path ".venv\Scripts\python.exe").Path
    }
    return $null
}

$python = Resolve-Python

function Invoke-Py {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )
    if ($NoVenv) {
        & py -3 @Args
    } else {
        & $python @Args
    }
}

if (-not $NoVenv) {
    Invoke-Py -Args @("-m", "pip", "install", "--upgrade", "pip")
}

if (-not $SkipInstall) {
    Invoke-Py -Args @("-m", "pip", "install", "-r", "requirements.txt")
}

if (-not $SkipPlaywright) {
    Invoke-Py -Args @("-m", "playwright", "install", "chromium")
}

if (-not (Test-Path ".env") -and (Test-Path ".env.example")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example. Fill it before runtime."
}

Invoke-Py -Args @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--name", "SohanCore",
    "--onedir",
    "--console",
    "--collect-all", "telegram",
    "--collect-all", "playwright",
    "--collect-all", "pywinauto",
    "--collect-all", "pycaw",
    "--collect-all", "cv2",
    "--collect-all", "PIL",
    "--hidden-import=win32gui",
    "--hidden-import=win32con",
    "--hidden-import=win32process",
    "--hidden-import=win32api",
    "main.py"
)

Write-Host ""
Write-Host "Build complete:"
Write-Host "  dist\\SohanCore\\SohanCore.exe"

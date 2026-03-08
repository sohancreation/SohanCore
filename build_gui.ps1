param(
    [switch]$NoVenv,
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

Invoke-Py -Args @(
    "-m", "PyInstaller",
    "--noconfirm",
    "--clean",
    "--name", "SohanCoreUI",
    "--onedir",
    "--windowed",
    "sohancore_gui.py"
)

Write-Host ""
Write-Host "GUI build complete:"
Write-Host "  dist\\SohanCoreUI\\SohanCoreUI.exe"

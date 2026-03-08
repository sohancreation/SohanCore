param(
    [switch]$RebuildCore,
    [switch]$RebuildUI,
    [switch]$SkipPlaywright
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if ($RebuildCore) {
    if ($SkipPlaywright) {
        powershell -ExecutionPolicy Bypass -File .\build.ps1 -SkipPlaywright
    } else {
        powershell -ExecutionPolicy Bypass -File .\build.ps1
    }
}

if ($RebuildUI) {
    powershell -ExecutionPolicy Bypass -File .\build_gui.ps1
}

if (-not (Test-Path ".\dist\SohanCore\SohanCore.exe")) {
    throw "Missing dist\\SohanCore\\SohanCore.exe. Build core first."
}
if (-not (Test-Path ".\dist\SohanCoreUI\SohanCoreUI.exe")) {
    throw "Missing dist\\SohanCoreUI\\SohanCoreUI.exe. Build UI first."
}

$isccCandidates = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
)
$iscc = $null
foreach ($candidate in $isccCandidates) {
    if (Test-Path $candidate) {
        $iscc = $candidate
        break
    }
}

if (-not $iscc) {
    throw "Inno Setup not found. Install Inno Setup 6 from https://jrsoftware.org/isinfo.php"
}

if (-not (Test-Path ".\release")) {
    New-Item -ItemType Directory -Path ".\release" | Out-Null
}

& $iscc ".\installer\SohanCoreSetup.iss"

if (-not (Test-Path ".\release\SohanCore-Setup.exe")) {
    throw "Installer build finished but release\\SohanCore-Setup.exe not found."
}

Write-Host ""
Write-Host "Installer created:"
Write-Host "  release\\SohanCore-Setup.exe"

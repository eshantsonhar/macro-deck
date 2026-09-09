param(
    [switch]$Run,
    [switch]$Reboot
)

$ErrorActionPreference = "Stop"

$Port = "COM4"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "Uploading Pico W firmware..." -ForegroundColor Cyan

py -m mpremote connect $Port fs cp "$Root\main.py" :main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Upload failed." -ForegroundColor Red
    exit 1
}

Write-Host "Upload successful." -ForegroundColor Green

if ($Run) {

    Write-Host ""
    Write-Host "Running main.py..." -ForegroundColor Cyan

    py -m mpremote connect $Port run "$Root\main.py"

}
elseif ($Reboot) {

    Write-Host ""
    Write-Host "Rebooting Pico..." -ForegroundColor Cyan

    py -m mpremote connect $Port reset
}

Write-Host ""

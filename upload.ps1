# Pico Firmware Upload Script
# Usage: .\upload.ps1 [-Reset]

param(
    [switch]$Reset
)

$mainPy = "$PSScriptRoot\main.py"
$comPort = "COM4"

Write-Host "=== Pico Firmware Upload ===" -ForegroundColor Cyan
Write-Host "Firmware: $mainPy"
Write-Host "COM Port: $comPort"
Write-Host ""

# Check if main.py exists
if (-not (Test-Path $mainPy)) {
    Write-Host "ERROR: main.py not found at $mainPy" -ForegroundColor Red
    exit 1
}

# Upload firmware
Write-Host "Uploading main.py to Pico..." -ForegroundColor Yellow
py -m mpremote connect $comPort fs cp $mainPy :main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Upload failed" -ForegroundColor Red
    exit 1
}
Write-Host "Upload complete!" -ForegroundColor Green

# Reset if requested
if ($Reset) {
    Write-Host "Resetting Pico..." -ForegroundColor Yellow
    py -m mpremote connect $comPort reset
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Reset command failed (may be expected)" -ForegroundColor Yellow
    }
    else {
        Write-Host "Reset complete!" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=== Upload Complete ===" -ForegroundColor Green
Write-Host "Pico is now running the new firmware."
Write-Host "You can now start the PC bridge:"
Write-Host "  py pc\spotify_bridge.py"
Write-Host ""
Write-Host "NOTE: Do NOT use 'mpremote run' for deployment as it holds COM4 open."

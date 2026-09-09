param(
    [switch]$StartBridge
)

$ErrorActionPreference = "Stop"

$Port = "COM4"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host ""
Write-Host "=== Pico W Deployment ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Stop any running program
Write-Host "Step 1: Stopping any running program..." -ForegroundColor Yellow
try {
    $ser = New-Object System.IO.Ports.SerialPort($Port, 115200)
    $ser.Open()
    $ser.Write([char]3)  # Ctrl+C
    Start-Sleep -Milliseconds 500
    $ser.Close()
    Write-Host "Program stopped." -ForegroundColor Green
} catch {
    Write-Host "Could not stop program (may not be running)" -ForegroundColor Yellow
}

Start-Sleep -Milliseconds 500

# Step 2: Upload main.py
Write-Host ""
Write-Host "Step 2: Uploading main.py..." -ForegroundColor Yellow
py -m mpremote connect $Port fs cp "$Root\main.py" :main.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "Upload failed." -ForegroundColor Red
    exit 1
}
Write-Host "Upload successful." -ForegroundColor Green

# Step 3: Reset Pico
Write-Host ""
Write-Host "Step 3: Resetting Pico..." -ForegroundColor Yellow
py -m mpremote connect $Port reset

if ($LASTEXITCODE -ne 0) {
    Write-Host "Reset failed." -ForegroundColor Red
    exit 1
}
Write-Host "Reset successful." -ForegroundColor Green

# Step 4: Wait for Pico to boot
Write-Host ""
Write-Host "Step 4: Waiting for Pico to boot..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Step 5: Test connection
Write-Host ""
Write-Host "Step 5: Testing connection..." -ForegroundColor Yellow
try {
    $result = py -m mpremote connect $Port exec "print('Pico ready')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Connection test successful." -ForegroundColor Green
    } else {
        Write-Host "Connection test failed, but Pico may still be running." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Connection test failed, but Pico may still be running." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Deployment Complete ===" -ForegroundColor Green
Write-Host "Pico is now running main.py independently on COM4" -ForegroundColor Cyan
Write-Host ""

if ($StartBridge) {
    Write-Host "Starting Spotify bridge..." -ForegroundColor Cyan
    Write-Host ""
    & py "$Root\pc\spotify_bridge.py"
} else {
    Write-Host "To start the Spotify bridge, run:" -ForegroundColor Cyan
    Write-Host "  .\deploy.ps1 -StartBridge" -ForegroundColor White
    Write-Host "Or manually:" -ForegroundColor Cyan
    Write-Host "  cd pc; py spotify_bridge.py" -ForegroundColor White
    Write-Host ""
}

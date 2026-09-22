$deviceId = "USB\VID_2E8A&PID_0005&MI_00\6&2C2EF436&0&0000"
Write-Host "Disabling device..."
Disable-PnpDevice -InstanceId $deviceId -Confirm:$false
Start-Sleep -Seconds 2
Write-Host "Enabling device..."
Enable-PnpDevice -InstanceId $deviceId -Confirm:$false
Write-Host "Done"

$deviceId = "USB\VID_2E8A&PID_0005\e6614103e762802f"
Write-Host "Disabling composite device..."
Disable-PnpDevice -InstanceId $deviceId -Confirm:$false
Start-Sleep -Seconds 2
Write-Host "Enabling composite device..."
Enable-PnpDevice -InstanceId $deviceId -Confirm:$false
Write-Host "Done"

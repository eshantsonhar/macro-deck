# Test Windows volume control using PowerShell
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class VolumeControl {
    [DllImport("user32.dll")]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, IntPtr dwExtraInfo);
    
    public const int KEYEVENTF_KEYUP = 0x0002;
    public const byte VK_VOLUME_UP = 0xAF;
    public const byte VK_VOLUME_DOWN = 0xAE;
    public const byte VK_VOLUME_MUTE = 0xAD;
    
    public static void VolumeUp() {
        keybd_event(VK_VOLUME_UP, 0, 0, IntPtr.Zero);
        keybd_event(VK_VOLUME_UP, 0, KEYEVENTF_KEYUP, IntPtr.Zero);
    }
    
    public static void VolumeDown() {
        keybd_event(VK_VOLUME_DOWN, 0, 0, IntPtr.Zero);
        keybd_event(VK_VOLUME_DOWN, 0, KEYEVENTF_KEYUP, IntPtr.Zero);
    }
    
    public static void MuteToggle() {
        keybd_event(VK_VOLUME_MUTE, 0, 0, IntPtr.Zero);
        keybd_event(VK_VOLUME_MUTE, 0, KEYEVENTF_KEYUP, IntPtr.Zero);
    }
}
"@

Write-Host "=== Windows Volume Control Test ==="
Write-Host ""
Write-Host "Test 1: Volume UP"
Write-Host "Your system volume should increase..."
[VolumeControl]::VolumeUp()
Start-Sleep -Milliseconds 500

Write-Host ""
Write-Host "Test 2: Volume DOWN"
Write-Host "Your system volume should decrease..."
[VolumeControl]::VolumeDown()
Start-Sleep -Milliseconds 500

Write-Host ""
Write-Host "Test 3: Mute Toggle"
Write-Host "Your system mute should toggle..."
[VolumeControl]::MuteToggle()

Write-Host ""
Write-Host "=== Test Complete ==="
Write-Host "Did your Windows volume actually change?"

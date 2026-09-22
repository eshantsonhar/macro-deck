# Investigate Windows Media Session API (SMTC)
Add-Type -AssemblyName System.Runtime.WindowsRuntime

# Try to use Windows Media Session API
# This requires complex interop, so we'll try a simpler approach first

# Check GlobalSystemMediaTransportControls
Write-Host "=== Windows Media Session Investigation ==="
Write-Host ""

# Method 1: Check if Windows exposes media sessions via known PowerShell modules
try {
    $sessions = Get-CimInstance -ClassName Win32_Process -ErrorAction Stop | Where-Object { $_.Name -like "*vivaldi*" }
    Write-Host "Vivaldi processes found:"
    $sessions | Format-Table Id, Name, MainWindowTitle
} catch {
    Write-Host "Error enumerating processes: $_"
}

Write-Host ""

# Method 2: Check foreground window
try {
    Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class Win32 {
        [DllImport("user32.dll")]
        public static extern IntPtr GetForegroundWindow();
        [DllImport("user32.dll")]
        public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
    }
"@
    $sb = New-Object System.Text.StringBuilder(256)
    [Win32]::GetWindowText([Win32]::GetForegroundWindow(), $sb, 256)
    Write-Host "Foreground window title: $($sb.ToString())"
} catch {
    Write-Host "Error getting foreground window: $_"
}

Write-Host ""

# Method 3: Check if there's a way to get media info without MainWindowTitle
Write-Host "Checking for media session accessibility..."
Write-Host "Windows SMTC (System Media Transport Controls) requires:"
Write-Host "  - Complex interop with Windows Runtime APIs"
Write-Host "  - Cannot be accessed via simple PowerShell commands"
Write-Host "  - Would require a Python library (e.g., pypiwin32 or WindowsRuntime)"
Write-Host ""
Write-Host "Conclusion: MainWindowTitle is the only simple method available via PowerShell"

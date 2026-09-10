# Volume Control Integration

This integration adds volume control functionality to your Pico W Controller using the rotary encoder.

## Components

### Pico Side
- `main.py` - Updated to send volume commands over UART
  - Rotary encoder CW: Volume Up
  - Rotary encoder CCW: Volume Down  
  - Encoder press: Mute/Unmute toggle

### PC Side
- `pc/simple_combined_bridge.py` - Combined bridge for media display + volume control
- `pc/volume_controller.py` - Standalone volume controller
- `pc/test_volume.py` - Test script for volume commands

## Serial Protocol

### PC to Pico (Media Display)
```
TRACK|<song name>|<artist name>|<app name>
```

### Pico to PC (Volume Control)
```
VOLUME|UP
VOLUME|DOWN
VOLUME|MUTE
```

## How It Works

1. **Media Display**: PC detects playing media in browsers and sends to Pico
2. **Volume Control**: Pico detects encoder input and sends commands to PC
3. **Bidirectional Communication**: Uses UART for two-way communication

## Testing

### Test Volume Control
```powershell
cd pc
py test_volume.py
```

This will test basic volume up/down and mute functionality.

### Test Complete System
```powershell
cd pc
py simple_combined_bridge.py
```

This will:
- Display current playing media on OLED
- Respond to rotary encoder for volume control
- Respond to encoder press for mute toggle

## Usage

**Rotary Encoder:**
- **Clockwise rotation**: Volume up (2% per click)
- **Counter-clockwise rotation**: Volume down (2% per click)
- **Press button**: Toggle mute/unmute

**OLED Display:**
- Shows current track and artist from browser
- Shows volume change feedback briefly

## Features

✅ **Volume Control**: 2% adjustment per encoder click
✅ **Mute Toggle**: Press encoder button to mute/unmute
✅ **Media Display**: Shows currently playing track
✅ **Bidirectional**: Both display and control work simultaneously
✅ **Browser Priority**: Detects media from browser tabs (Vivaldi, Chrome, etc.)

## Configuration

You can adjust volume step size in `simple_combined_bridge.py`:
```python
VOLUME_STEP = 2  # Change to 1, 5, 10 for different increments
```

## Troubleshooting

If volume control doesn't work:
1. Ensure Windows audio device is properly configured
2. Check that the PowerShell audio commands work with `test_volume.py`
3. Verify serial communication is working (no COM4 conflicts)

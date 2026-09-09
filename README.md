# Media Display Integration

This integration displays your currently playing media from any player on the Pico W OLED screen.

## Components

### PC Side
- `pc/media_bridge.py` - Main bridge that monitors multiple media players and sends track info to Pico
- `pc/spotify_bridge.py` - Legacy Spotify-specific bridge (still works)
- `pc/manual_spotify_test.py` - Manual test script to send sample track data
- `pc/test_media_detection.py` - Test script to verify media window detection
- `pc/requirements.txt` - Python dependencies (pyserial)

### Pico Side
- `main.py` - Updated main program that receives serial data and displays on OLED
- `tests/test_serial_display.py` - Standalone test for serial display functionality

## Supported Media Players

The media bridge automatically detects content from:
- **Spotify** (desktop app and web player)
- **VLC Media Player**
- **Windows Media Player**
- **YouTube** (Chrome, Edge, Firefox browsers)
- **MPC (Media Player Classic)**
- **PotPlayer**
- **Generic media windows** (any window with " - " separator, filtered from non-media apps)

## Quick Start

### 1. Install PC Dependencies
```powershell
cd pc
py -m pip install -r requirements.txt
```

### 2. Deploy Updated Pico Firmware
```powershell
# The Pico should already be running the updated main.py from the deployment
# If needed, you can redeploy using:
cd pc
py upload_raw.py    # Uploads main.py to Pico
py reset_pico.py    # Resets Pico to run new code
```

### 3. Test the Display
```powershell
cd pc
py manual_spotify_test.py
```

This will send test tracks to your Pico and you should see them displayed on the OLED.

### 4. Test Media Detection
```powershell
cd pc
py test_media_detection.py
```

This will show what media windows are currently detected on your system.

### 5. Run Media Bridge
```powershell
cd pc
py media_bridge.py
```

The bridge will:
- Monitor all supported media players
- Send track info to Pico when content changes
- Display the app name in brackets (e.g., "[Spotify]")
- Display "No Track - Playing" when no media is detected

**Note:** Make sure a media player is running with content playing for the bridge to detect it.

## Deployment Workflow

The project uses a hands-off deployment workflow without BOOTSEL:

1. **Stop any running Pico program**: `py force_reset.py`
2. **Upload updated main.py**: `py upload_raw.py`
3. **Reset Pico**: `py reset_pico.py`
4. **Run bridge**: `py media_bridge.py`

The Pico runs main.py independently, freeing COM4 for the bridge to connect.

## Serial Protocol

Messages sent from PC to Pico use the format:
```
TRACK|<song name>|<artist name>|<app name>
```

Example:
```
TRACK|Bohemian Rhapsody|Queen|Spotify
```

## Current Status

**Working:**
- Serial communication between PC and Pico
- Multi-media player detection
- Track display on OLED with app name
- Manual test script for verification
- Pico runs independently (no mpremote run needed)

**Limitations:**
- Uses window title detection (works best with visible windows)
- Requires media players to be running on the same Windows machine
- Window title detection may not work if players are minimized to tray
- Generic detection may occasionally pick up non-media windows

## Future Improvements

- Use media APIs for more reliable track detection
- Add error handling for media player connection issues
- Support for album art display
- Button controls for media (play/pause, next/previous)
- Better handling of long track/artist names (scrolling text)
- Volume control integration

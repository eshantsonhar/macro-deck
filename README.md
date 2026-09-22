# Pico W Physical Media Controller

A hardware controller for Windows media playback using a Raspberry Pi Pico W. The device provides physical volume control and media display through a rotary encoder, push switch, buttons, and OLED display. The Pico handles hardware input/output while the Windows PC manages media detection and system volume control.

## Overview

The system consists of two components:

**Windows PC**
- Runs media players (Spotify, Vivaldi, VLC, etc.)
- Python bridge connects to Pico via USB serial
- Detects current media information
- Controls system volume via Windows input simulation

**Pico W**
- Reads rotary encoder (CW/CCW movement and push switch)
- Reads 10 button inputs
- Displays media information on SH1106 OLED
- Sends hardware events to PC via USB serial
- Receives track/artist information from PC for display

The Pico does not communicate directly with media applications. All media detection and volume control logic runs on the Windows PC.

## Features

- Rotary encoder controls Windows system volume (clockwise up, counter-clockwise down)
- Encoder push switch toggles system mute/unmute
- OLED displays current track name, artist, and application
- Media detection works for background tabs (e.g., Vivaldi playing in background)
- Ten buttons available for future controller actions
- Bidirectional USB serial communication between Pico and PC

## Hardware

### Components
- Raspberry Pi Pico W (RP2040)
- SH1106-compatible 128x64 OLED display
- Rotary encoder with push switch
- 10 tactile buttons

### Pin Assignments

**OLED (I2C0)**
- SDA: GP20
- SCL: GP21
- Address: 0x3C
- Frequency: 400 kHz

**Rotary Encoder**
- DT: GP6
- CLK: GP7
- Switch: GP0
- All pins configured with internal pull-up

**Buttons**
- GP9, GP10, GP11, GP12, GP13
- GP14, GP15, GP16, GP17, GP18
- All configured with internal pull-up (active-low: pressed = 0)

### Electrical Notes
- OLED uses SH1106-specific initialization and column addressing
- Buttons are active-low with internal pull-up resistors
- Encoder requires two valid quadrature transitions per physical detent

## Encoder Implementation

The encoder was experimentally characterized rather than using a generic rotary encoder library. The firmware uses a state-based quadrature decoder.

**State representation:**
```python
state = (CLK.value() << 1) | DT.value()
```

**Verified transition table:**
```
0 -> 1: -1 (counter-clockwise movement)
0 -> 2: +1 (clockwise movement)
1 -> 3: -1 (counter-clockwise movement)
1 -> 0: +1 (clockwise movement)
3 -> 2: -1 (counter-clockwise movement)
3 -> 1: +1 (clockwise movement)
2 -> 0: -1 (counter-clockwise movement)
2 -> 3: +1 (clockwise movement)
```

The physical encoder produces two valid quadrature transitions per detent. The firmware accumulates transitions and generates one software movement event per two valid transitions to match the physical detent feel.

## Software Architecture

### main.py (Pico Firmware)
- Handles all hardware I/O (OLED, encoder, buttons)
- Implements calibrated encoder state machine
- Receives track/artist data from PC via USB serial
- Sends hardware events to PC via USB serial
- Uses `select.poll()` for non-blocking USB serial input

### pc/combined_bridge.py (PC Bridge)
- Main integration point between Pico and Windows
- Detects media information using Windows Global System Media Transport Controls (SMTC)
- Sends track/artist data to Pico for OLED display
- Receives hardware events from Pico and translates to Windows volume commands
- Runs volume listener thread for real-time encoder event handling

### pc/volume_controller.py (Windows Volume Control)
- Implements Windows volume control using SendInput API
- Uses multimedia virtual-key codes (VK_VOLUME_UP, VK_VOLUME_DOWN, VK_VOLUME_MUTE)
- Provides volume_up(), volume_down(), volume_mute() functions

### pc/spotify_bridge.py (Legacy)
- Window-title based media detection (fallback method)
- Not used in primary operation but retained as alternative

## Serial Protocol

### Pico to PC (Hardware Events)
The Pico sends machine-readable event messages:

```
ENCODER_CW      - Clockwise encoder movement (volume up)
ENCODER_CCW     - Counter-clockwise encoder movement (volume down)
ENCODER_SW      - Encoder switch press (mute toggle)
BUTTON_1        - Button 1 press
BUTTON_2        - Button 2 press
...
BUTTON_10       - Button 10 press
```

### PC to Pico (Display Updates)
The PC sends track information in pipe-delimited format:

```
TRACK|<track name>|<artist name>|<app name>
```

Example:
```
TRACK|Heat Waves|Glass Animals|Vivaldi
```

Track and artist names are truncated to 21 characters for OLED display. The app name is optional.

Serial output from the Pico is intended to be machine-readable protocol data, not arbitrary debugging text.

## Windows Integration

The PC bridge uses Windows SendInput API for system volume control:

**Event mapping:**
- ENCODER_CW → volume_up() → VK_VOLUME_UP (0xAF)
- ENCODER_CCW → volume_down() → VK_VOLUME_DOWN (0xAE)
- ENCODER_SW → volume_mute() → VK_VOLUME_MUTE (0xAD)

SendInput simulates multimedia key presses, which works consistently across Windows applications. This approach was physically verified during development.

## Media Display

The PC bridge obtains current media information using Windows Global System Media Transport Controls (SMTC). This API allows media information to be retrieved even when the media application is not the foreground window (e.g., Vivaldi playing in a background tab).

The bridge prefers Vivaldi by AUMID but falls back to other media sessions if Vivaldi is not active. Media information is polled every 2 seconds and sent to the Pico only when the track changes.

The fallback window-title detection method (spotify_bridge.py) is retained but not used in normal operation.

## OLED Implementation

The display uses an SH1106-compatible 128x64 OLED. The project uses direct SH1106 initialization and column addressing rather than an SSD1306 driver library. The display is organized as 8 pages of 128 columns.

Screen layout:
- Line 0: "Now Playing:"
- Line 1: Track name (truncated to 21 chars)
- Line 2: Artist name (truncated to 21 chars)
- Line 3: App name in brackets [optional] or event status

## Installation / Setup

### Requirements
- Windows PC
- Python 3.8+
- Raspberry Pi Pico W
- MicroPython firmware v1.28.0 for Pico W

### PC Dependencies
```powershell
cd pc
py -m pip install -r requirements.txt
```

Required packages:
- pyserial>=3.5
- winsdk (via pip)

### MicroPython Firmware
Flash MicroPython v1.28.0 for Pico W to the device. The UF2 file is available in `backups/RPI_PICO_W-20260406-v1.28.0.uf2`.

To flash:
1. Hold BOOTSEL button while connecting USB (or press BOOTSEL then reset)
2. Copy the UF2 file to the RPI-RP2 mass storage device
3. Pico will automatically reboot into MicroPython

### Pico Firmware Deployment
```powershell
# From project root
.\upload.ps1 -Reset
```

Or manually:
```powershell
py -m mpremote connect COM4 fs cp main.py :main.py
py -m mpremote connect COM4 reset
```

The `boot.py` file is also deployed to auto-start `main.py` on boot.

### Running the Bridge
```powershell
cd pc
py combined_bridge.py
```

The bridge will:
- Connect to COM4 at 115200 baud
- Start monitoring media via SMTC
- Listen for encoder events from Pico
- Display media information on Pico OLED
- Control Windows volume based on encoder events

Press Ctrl+C to stop the bridge.

## Development Workflow

Normal development workflow for firmware changes:

1. Modify `main.py` locally
2. Deploy to Pico: `.\upload.ps1 -Reset` or `py -m mpremote connect COM4 fs cp main.py :main.py`
3. Pico resets and runs new firmware
4. Start bridge: `py pc\combined_bridge.py`

**Important:** Do not use `mpremote run` for deployment. It keeps the serial connection open, preventing the bridge from connecting. The Pico runs `main.py` independently, freeing COM4 for the bridge.

**COM4 ownership:** Only one process may own COM4 at a time. Do not run multiple PC scripts that open COM4 simultaneously.

## Recovery

If the Pico becomes unresponsive or requires firmware recovery:

1. Enter BOOTSEL mode: Hold BOOTSEL button while connecting USB (or press BOOTSEL then reset)
2. Windows will enumerate RPI-RP2 as a mass storage device
3. Copy MicroPython UF2 firmware to RPI-RP2
4. Pico will automatically reboot into the new firmware
5. Re-deploy `main.py` using normal deployment workflow

BOOTSEL is a firmware programming mechanism in the RP2040 ROM. It is not a flash-nuke operation. The RP2040 bootloader is stored in ROM and cannot be corrupted.

The known working baseline is MicroPython v1.28.0 for Pico W. Do not use Pico 2 firmware or generic Pico firmware.

## Project Structure

```
diy_macro_deck/
├── main.py                 # Pico firmware
├── boot.py                 # Auto-start main.py on boot
├── upload.ps1              # Firmware upload script
├── pc/
│   ├── combined_bridge.py  # Main PC bridge (media + volume)
│   ├── volume_controller.py # Windows volume control via SendInput
│   ├── spotify_bridge.py   # Legacy window-title media detection
│   └── requirements.txt    # Python dependencies
├── backups/
│   └── RPI_PICO_W-20260406-v1.28.0.uf2  # MicroPython firmware
└── docs/                   # Development documentation
```

## Verification / v1.0.0 Status

The following functionality was physically verified for v1.0.0:

- OLED displays media information correctly (track, artist, app)
- OLED updates when track changes
- Encoder clockwise rotation increases Windows system volume
- Encoder counter-clockwise rotation decreases Windows system volume
- Encoder push switch toggles Windows mute/unmute
- Encoder direction and detent behavior match physical feel (2 transitions per detent)
- Ten buttons are electrically functional (detected on Pico)
- Pico-to-PC serial communication works (encoder events received)
- PC-to-Pico serial communication works (TRACK messages received and displayed)
- Media detection works for background tabs (Vivaldi SMTC)
- Complete controller operates as intended with combined bridge

## Known Limitations

- Ten buttons are electrically functional but not assigned to specific application functions in v1.0.0
- Media detection requires a Windows PC with SMTC support
- Serial port (COM4) must be available and not in use by other applications
- OLED track/artist names are truncated to 21 characters (no scrolling)
- No album art display
- No play/pause/next/previous control via hardware

## Version

Version 1.0.0
Status: Complete
Platform: Raspberry Pi Pico W + Windows PC

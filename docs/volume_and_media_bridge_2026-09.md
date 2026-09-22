# Volume and Media Bridge Implementation

**Date:** 2026-09  
**Project:** Raspberry Pi Pico W Macro Deck  
**Baseline Commit:** a36ca87 ("all buttons, encoder and oled working")

## Purpose

This document describes the final architecture and implementation of the bidirectional bridge between the Raspberry Pi Pico W controller and Windows, providing:

1. **Volume control** via rotary encoder and switch using Windows SendInput API
2. **Media detection and OLED display** via window title monitoring

## Hardware/Software Architecture

```
┌─────────────────┐
│  Raspberry Pi   │
│     Pico W      │
│                 │
│  - OLED (128x64)│
│  - Encoder      │
│  - 10 Buttons   │
│  - USB CDC      │
└────────┬────────┘
         │ USB Serial (COM4, 115200 baud)
         │
┌────────▼────────┐
│ combined_bridge  │  ← Single Python process (sole COM4 owner)
│     .py         │
│                 │
│  ┌─────────────┐│
│  │ Main Thread ││→ Detects media → Sends TRACK|... to Pico
│  └─────────────┘│
│                 │
│  ┌─────────────┐│
│  │Volume Thread ││← Receives encoder events → Calls SendInput
│  └─────────────┘│
└────────┬────────┘
         │ Win32 SendInput
         │
┌────────▼────────┐
│    Windows      │
│                 │
│  - Volume UP    │
│  - Volume DOWN  │
│  - MUTE toggle  │
└─────────────────┘
```

## Pico Firmware Baseline

**Commit:** `a36ca87`  
**Description:** "all buttons, encoder and oled working"  
**Status:** Physically verified working  
**Constraint:** Pico firmware MUST remain completely untouched

### Known-Good Pico Event Protocol

The Pico emits the following serial strings (from commit a36ca87):

```
Encoder CW | Position: X
Encoder CCW | Position: X
Encoder switch pressed
Button 1 pressed
Button 2 pressed
...
Button 10 pressed
```

**Important:** The encoder events include position information for OLED display. The volume control uses the event string prefix to detect direction.

### Pico Serial Input Protocol

The Pico receives messages in this format:

```
TRACK|song name|artist name|app name
```

This is used to update the OLED display with current media information.

## Windows Volume Mapping

| Pico Event String | Windows Action | Virtual Key |
|-------------------|----------------|-------------|
| `Encoder CW | Position: X` | Volume Up | VK_VOLUME_UP (0xAF) |
| `Encoder CCW | Position: X` | Volume Down | VK_VOLUME_DOWN (0xAE) |
| `Encoder switch pressed` | Mute Toggle | VK_VOLUME_MUTE (0xAD) |

## SendInput Implementation

**File:** `pc/volume_controller.py`

The volume control uses Microsoft's Win32 SendInput API through Python ctypes:

```python
# Virtual-Key Codes
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

# Structures (64-bit Windows)
ULONG_PTR = ctypes.c_uint64

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", INPUT_UNION),
    ]
```

**Functions:**
- `volume_up()` - Sends VK_VOLUME_UP key-down + key-up
- `volume_down()` - Sends VK_VOLUME_DOWN key-down + key-up
- `volume_mute()` - Sends VK_VOLUME_MUTE key-down + key-up

**Physical Verification:** All three functions were independently tested and confirmed to produce one normal Windows volume step per call.

## COM4 Ownership

**Sole Owner:** `combined_bridge.py`

**Constraint:** Only ONE process may connect to COM4 at a time.

**Important:** The following scripts should NOT be run simultaneously with `combined_bridge.py`:
- `spotify_bridge.py` - Would compete for COM4
- `volume_controller.py` - Would compete for COM4

## combined_bridge.py Responsibilities

### Main Thread (Media Detection)
1. Opens COM4
2. Starts volume listener daemon thread
3. Polls window titles every 2 seconds (POLL_INTERVAL)
4. Detects media from:
   - Browsers (Vivaldi, Chrome, Edge, Firefox, Brave, Opera)
   - Spotify
   - VLC
   - Windows Media Player
   - MPC
   - PotPlayer
5. Formats media info for OLED (21 char max per line)
6. Sends `TRACK|song|artist|app` messages to Pico
7. Handles "No Track" state

### Volume Listener Thread (Serial Reader)
1. Reads from COM4 (single reader, no conflicts)
2. Dispatches incoming lines:
   - `VOLUME|UP` → `volume_up()`
   - `VOLUME|DOWN` → `volume_down()`
   - `VOLUME|MUTE` → `volume_mute()`
   - `Encoder CW | Position: X` → `volume_up()`
   - `Encoder CCW | Position: X` → `volume_down()`
   - `Encoder switch pressed` → `volume_mute()`
3. Calls verified SendInput functions
4. Runs continuously with 50ms sleep

## Media Detection Flow

```
PowerShell: Get-Process with MainWindowTitle
         ↓
Filter by known media player patterns
         ↓
Extract track/artist using regex
         ↓
Priority selection (browsers > standalone players)
         ↓
Format for OLED (21 char max)
         ↓
Send TRACK|song|artist|app to Pico
```

## TRACK| Protocol

**Format:** `TRACK|song name|artist name|app name\n`

**Example:** `TRACK|Bohemian Rhapsody|Queen|Spotify\n`

**Pico Processing:** The Pico parses this message and updates the OLED display:
- Line 1: Song name
- Line 2: Artist name
- Line 3: App name
- Line 4: Status

## OLED Data Flow

```
Windows Media → combined_bridge.py → TRACK|... → Pico → OLED
```

The OLED updates only when the track/artist/app changes (deduplication logic in main thread).

## Why Pico Firmware Was Deliberately Left Unchanged

1. **Known-good baseline:** Commit a36ca87 was physically verified working
2. **Previous regression:** Changing print statements previously caused input unresponsiveness
3. **Minimal risk:** Using existing event strings requires no Pico modification
4. **Reversible:** If issues arise, the Pico is still on the known-good firmware
5. **Simpler:** Protocol already exists; no need to redesign

## Files Involved

### Pico Side
- `main.py` - Firmware (commit a36ca87, **untouched**)

### PC Side
- `pc/combined_bridge.py` - Main bidirectional bridge (**modified**)
- `pc/volume_controller.py` - SendInput volume functions (**verified, not modified**)
- `pc/spotify_bridge.py` - Legacy media-only bridge (**not used**)

### Documentation
- `docs/debugging_print_regression_2026-09.md` - Previous regression incident
- `docs/volume_and_media_bridge_2026-09.md` - This document

## Known-Good Baseline Commit

**Commit:** `a36ca87`  
**Description:** "all buttons, encoder and oled working"  
**Verified:**
- All 10 buttons working
- Encoder CW working
- Encoder CCW working
- Encoder switch working
- OLED working

## Testing Performed

### SendInput Functions (Independent)
- `volume_up()` - Confirmed one normal Windows volume-up step
- `volume_down()` - Confirmed one normal Windows volume-down step
- `volume_mute()` - Confirmed mute toggle

### ABI Verification
- KEYBDINPUT structure layout verified
- INPUT structure layout verified
- ULONG_PTR type verified for 64-bit Windows
- Import safety verified (no COM4 open on import)

### End-to-End Volume Control
- Encoder CW → Windows volume up ✓
- Encoder CCW → Windows volume down ✓
- Encoder switch → Mute toggle ✓

### End-to-End Media/OLED
- Media detection from browsers ✓
- TRACK| message sent to Pico ✓
- OLED displays track/artist/app ✓
- Media updates on track change ✓

### Combined Operation
- Volume control works while media is playing ✓
- Media/OLED updates while volume is active ✓
- No bridge crashes ✓
- No serial errors ✓

## Remaining Work

### Windows Permanent-Process Setup
The combined_bridge.py currently runs as a manual foreground process. Future work includes:
- Running as a Windows service or background process
- Auto-start on Windows login
- Tray icon for status/control

### Macro Buttons
The ten physical buttons are currently not assigned to any Windows actions. Future work includes:
- Button → Windows macro/key mapping
- Configurable button assignments
- Application-specific button profiles

## Important Warnings

### COM4 Ownership
**NEVER run these simultaneously with combined_bridge.py:**
- `spotify_bridge.py`
- `volume_controller.py`

Doing so will cause a port conflict and one or both processes will fail to connect.

### Pico Firmware
**DO NOT modify main.py** unless:
- You have a clear reversible change
- You have tested in isolation
- You have preserved the a36ca87 baseline

### Bootsel Recovery
**DO NOT use BOOTSEL** as a first-line debugging step. The known-good a36ca87 firmware is already on the device.

## References

- Microsoft SendInput API: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput
- Virtual-Key Codes: https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
- MicroPython mpremote: https://docs.micropython.org/en/latest/reference/mpremote.html

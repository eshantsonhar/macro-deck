# USB Serial Protocol

## Overview
The Pico W communicates with the PC bridge over USB CDC serial (COM4).
The protocol is machine-readable only. Human-readable diagnostics are printed by the PC bridge separately.

## Pico → PC Messages

### Encoder Events
```
ENCODER_CW
ENCODER_CCW
ENCODER_SW
```

- `ENCODER_CW`: Clockwise rotation (one physical detent)
- `ENCODER_CCW`: Counterclockwise rotation (one physical detent)
- `ENCODER_SW`: Encoder switch press

Each message is newline-terminated (`\n`).

### Button Events
```
BUTTON|1
BUTTON|2
...
BUTTON|10
```

Format: `BUTTON|<button_number>`

Each message is newline-terminated (`\n`).

## PC → Pico Messages

### Spotify/OLED State Updates
```
TRACK|<song name>|<artist name>|<app name>
```

Format: `TRACK|<track>|<artist>|<app>`

Example:
```
TRACK|Sweater Weather|The Neighbourhood|Spotify
```

Each message is newline-terminated (`\n`).

If no track is playing:
```
TRACK|No Track|Playing|
```

## Message Format Rules

1. All protocol messages are ASCII text
2. Each message ends with `\n` (newline)
3. No spaces around pipe separators in protocol messages
4. Protocol messages do NOT include debug text
5. PC bridge may print diagnostics to its own stdout
6. PC bridge diagnostics are NOT sent back to the Pico

## PC Bridge Behavior

### Input Handling
- Read lines from COM4
- Ignore empty lines
- Ignore malformed lines
- Log errors locally
- Do not send errors back to Pico

### Output Handling
- Send `TRACK|...` messages to Pico
- Print `[RX] ENCODER_CW` etc. to local console
- Keep protocol and diagnostics separate

## Windows Volume Mapping

The PC bridge translates encoder events to Windows multimedia keys:

| Pico Event    | Windows Virtual Key | Action          |
|---------------|---------------------|-----------------|
| ENCODER_CW    | VK_VOLUME_UP (0xAF)  | Volume up       |
| ENCODER_CCW   | VK_VOLUME_DOWN (0xAE)| Volume down     |
| ENCODER_SW    | VK_VOLUME_MUTE (0xAD)| Mute toggle     |

Implementation uses `ctypes.windll.user32.keybd_event()`:
```python
ctypes.windll.user32.keybd_event(VK_CODE, 0, 0, 0)  # Key down
ctypes.windll.user32.keybd_event(VK_CODE, 0, 2, 0)  # Key up
```

## Error Handling

### Pico Side
- Serial communication wrapped in try/except
- Exceptions do not crash the main loop
- Hardware polling continues even if serial fails

### PC Side
- Serial connection errors handled gracefully
- Connection retries allowed
- malformed messages ignored
- No crashes on protocol errors

## Connection Behavior

### Normal Operation
1. Pico boots
2. Pico waits for serial input
3. PC bridge opens COM4
4. PC bridge sends track updates
5. Pico displays track on OLED
6. Pico sends encoder/button events
7. PC bridge maps events to Windows actions

### PC Bridge Disconnection
- Pico continues to poll hardware
- OLED continues to show last known track
- Encoder/button events are lost (no PC to receive them)
- PC bridge can reconnect later

### Pico Disconnection
- PC bridge detects serial error
- PC bridge attempts reconnection
- No harm to Windows or applications

# Hardware Configuration

## Board
- **Model:** Raspberry Pi Pico W
- **Microcontroller:** RP2040
- **USB VID:** 2E8A
- **USB PID:** 0005
- **USB Serial Port:** COM4 (Windows)

## OLED Display
- **Controller:** SH1106-compatible
- **Resolution:** 128x64
- **I2C Address:** 0x3C
- **I2C Bus:** I2C0
- **SDA Pin:** GP20
- **SCL Pin:** GP21
- **Frequency:** 400 kHz
- **Visible Column Addressing:**
  ```python
  oled_cmd(0x02)
  oled_cmd(0x10)
  ```

### SH1106 Initialization Sequence
```python
for c in (
    0xAE,      # Display off
    0xD5, 0x80, # Clock division
    0xA8, 0x3F, # Multiplex ratio
    0xD3, 0x00, # Display offset
    0x40,      # Display on
    0xAD, 0x8B, # External VCC
    0xA1,      # Segment remap
    0xC8,      # COM scan direction
    0xDA, 0x12, # COM pins
    0x81, 0xFF, # Contrast
    0xD9, 0x1F, # Pre-charge period
    0xDB, 0x40, # VCOM deselect
    0xA4,      # Resume display
    0xA6,      # Normal display
    0xAF       # Display on
):
    oled_cmd(c)
```

## Rotary Encoder
- **DT Pin:** GP6
- **CLK Pin:** GP7
- **Switch Pin:** GP0
- **Input Mode:** Pull-up internal
- **Pressed State:** 0 (low)
- **Released State:** 1 (high)

### Encoder State Calculation
```python
state = (CLK.value() << 1) | DT.value()
```

### Verified Transition Table
```python
TRANSITIONS = {
    0: {1: -1, 2: 1},
    1: {3: -1, 0: 1},
    3: {2: -1, 1: 1},
    2: {0: -1, 3: 1},
}
```

### Calibration
- **2 valid quadrature transitions = 1 physical detent**
- 10 physical clicks produce exactly 10 software events
- Direction is verified correct

## Buttons
All buttons use internal pull-up resistors.
- **Pressed:** 0 (low)
- **Released:** 1 (high)

### Button Pin Assignments
| Button | Pin |
|--------|-----|
| 1      | GP9 |
| 2      | GP10 |
| 3      | GP11 |
| 4      | GP12 |
| 5      | GP13 |
| 6      | GP14 |
| 7      | GP15 |
| 8      | GP16 |
| 9      | GP17 |
| 10     | GP18 |

## Verified Behavior
- OLED initializes correctly
- Rotary encoder produces exactly one event per physical detent
- Encoder direction is correct
- Encoder switch works
- All 10 buttons work

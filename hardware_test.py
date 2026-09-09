from machine import Pin, I2C
import time

# ============================================================
# Raspberry Pi Pico W Controller
# Hardware Diagnostic
#
# Rotary encoder:
#   CLK = GP7
#   DT  = GP6
#   SW  = GP0
#
# OLED:
#   SDA = GP21
#   SCL = GP20
#
# Buttons:
#   GP9 - GP18
# ============================================================


# ------------------------------------------------------------
# Pin configuration
# ------------------------------------------------------------

PIN_DT = 6
PIN_CLK = 7
PIN_SW = 0

PIN_SDA = 21
PIN_SCL = 20

BUTTON_PINS = [
    9, 10, 11, 12, 13,
    14, 15, 16, 17, 18
]


# ------------------------------------------------------------
# I2C
# ------------------------------------------------------------

print()
print("================================================")
print("        PICO W HARDWARE DIAGNOSTIC")
print("================================================")
print()

print("Initializing I2C...")

i2c = I2C(
    0,
    scl=Pin(PIN_SCL),
    sda=Pin(PIN_SDA),
    freq=400000
)

devices = i2c.scan()

print("I2C devices found:", [hex(x) for x in devices])

oled = None
oled_addr = None

# Try common SSD1306 addresses
if 0x3C in devices:
    oled_addr = 0x3C
elif 0x3D in devices:
    oled_addr = 0x3D

if oled_addr is not None:
    try:
        from ssd1306 import SSD1306

        oled = SSD1306(
            128,
            64,
            False,
            i2c,
            addr=oled_addr
        )

        print("SSD1306 OLED detected at", hex(oled_addr))

    except Exception as e:
        print("OLED initialization failed:", repr(e))

else:
    print("No SSD1306 detected at 0x3C or 0x3D.")


# ------------------------------------------------------------
# Rotary encoder
# ------------------------------------------------------------

clk = Pin(PIN_CLK, Pin.IN, Pin.PULL_UP)
dt = Pin(PIN_DT, Pin.IN, Pin.PULL_UP)
sw = Pin(PIN_SW, Pin.IN, Pin.PULL_UP)

last_clk = clk.value()
encoder_position = 0

last_sw = sw.value()


# ------------------------------------------------------------
# Buttons
# ------------------------------------------------------------

buttons = []

for pin_number in BUTTON_PINS:
    buttons.append(
        Pin(pin_number, Pin.IN, Pin.PULL_UP)
    )


# ------------------------------------------------------------
# OLED helper
# ------------------------------------------------------------

def oled_screen():
    if oled is None:
        return

    oled.fill(0)

    oled.text("PICO W DIAGNOSTIC", 0, 0)

    if oled_addr is not None:
        oled.text("OLED: " + hex(oled_addr), 0, 10)
    else:
        oled.text("OLED: NOT FOUND", 0, 10)

    oled.text("ENC: " + str(encoder_position), 0, 20)

    if sw.value() == 0:
        oled.text("ENC SW: PRESSED", 0, 30)
    else:
        oled.text("ENC SW: released", 0, 30)

    # Display ten buttons in two rows.
    # 1 = released
    # 0 = pressed
    oled.text(
        "BTN 1-5: " +
        "".join(str(buttons[i].value()) for i in range(5)),
        0,
        42
    )

    oled.text(
        "BTN 6-10:" +
        "".join(str(buttons[i].value()) for i in range(5, 10)),
        0,
        52
    )

    oled.show()


# ------------------------------------------------------------
# Initial screen
# ------------------------------------------------------------

oled_screen()

print()
print("Hardware test running.")
print()
print("Press the encoder to test SW.")
print("Turn the encoder to test CLK/DT.")
print("Press each button to test GP9-GP18.")
print()


# ------------------------------------------------------------
# Main diagnostic loop
# ------------------------------------------------------------

last_button_states = [
    button.value()
    for button in buttons
]

last_oled_update = time.ticks_ms()

while True:

    # --------------------------------------------------------
    # Rotary encoder
    # --------------------------------------------------------

    current_clk = clk.value()

    if current_clk != last_clk:

        if current_clk == 1:

            if dt.value() != current_clk:
                encoder_position += 1
                direction = "CW"
            else:
                encoder_position -= 1
                direction = "CCW"

            print(
                "Encoder:",
                direction,
                "position =",
                encoder_position
            )

        last_clk = current_clk


    # --------------------------------------------------------
    # Encoder push button
    # --------------------------------------------------------

    current_sw = sw.value()

    if current_sw != last_sw:

        if current_sw == 0:
            print("Encoder switch: PRESSED")
        else:
            print("Encoder switch: RELEASED")

        last_sw = current_sw


    # --------------------------------------------------------
    # Buttons
    # --------------------------------------------------------

    for i in range(10):

        current = buttons[i].value()

        if current != last_button_states[i]:

            if current == 0:
                print(
                    "Button",
                    i + 1,
                    "GP" + str(BUTTON_PINS[i]),
                    "PRESSED"
                )
            else:
                print(
                    "Button",
                    i + 1,
                    "GP" + str(BUTTON_PINS[i]),
                    "RELEASED"
                )

            last_button_states[i] = current


    # --------------------------------------------------------
    # Refresh OLED
    # --------------------------------------------------------

    now = time.ticks_ms()

    if time.ticks_diff(now, last_oled_update) >= 100:
        oled_screen()
        last_oled_update = now


    time.sleep_ms(1)

from machine import Pin, I2C
import framebuf
import time
import sys

# ============================================================
# OLED
# ============================================================

I2C_SDA = 20
I2C_SCL = 21
OLED_ADDR = 0x3C

WIDTH = 128
HEIGHT = 64

i2c = I2C(
    0,
    sda=Pin(I2C_SDA),
    scl=Pin(I2C_SCL),
    freq=400000
)

buf = bytearray(WIDTH * HEIGHT // 8)

oled = framebuf.FrameBuffer(
    buf,
    WIDTH,
    HEIGHT,
    framebuf.MONO_VLSB
)


def oled_cmd(c):
    i2c.writeto(OLED_ADDR, bytes([0x00, c]))


def oled_data(d):
    i2c.writeto(OLED_ADDR, bytes([0x40]) + d)


for c in (
    0xAE,
    0xD5, 0x80,
    0xA8, 0x3F,
    0xD3, 0x00,
    0x40,
    0xAD, 0x8B,
    0xA1,
    0xC8,
    0xDA, 0x12,
    0x81, 0xFF,
    0xD9, 0x1F,
    0xDB, 0x40,
    0xA4,
    0xA6,
    0xAF
):
    oled_cmd(c)


def oled_show():
    for page in range(8):
        oled_cmd(0xB0 + page)
        oled_cmd(0x02)
        oled_cmd(0x10)

        start = page * 128
        oled_data(buf[start:start + 128])


def clear():
    oled.fill(0)


# ============================================================
# SERIAL COMMUNICATION
# ============================================================

current_track = "No Track"
current_artist = "Playing"
current_app = ""


def parse_serial_message(line):
    """
    Parse serial message from PC bridge
    Format: TRACK|song name|artist name|app name
    """
    global current_track, current_artist, current_app

    if line.startswith("TRACK|"):
        parts = line.split("|")
        if len(parts) >= 3:
            current_track = parts[1]
            current_artist = parts[2]
            current_app = parts[3] if len(parts) >= 4 else ""
            return True

    return False


def check_serial_input():
    """
    Check for serial input from stdin (mpremote USB serial)
    """
    try:
        line = sys.stdin.readline()
        if line:
            line = line.strip()
            if line and parse_serial_message(line):
                print(f"Received: {current_track} - {current_artist}")
                show_screen()
    except:
        pass


# ============================================================
# HARDWARE
# ============================================================

DT = Pin(6, Pin.IN, Pin.PULL_UP)
CLK = Pin(7, Pin.IN, Pin.PULL_UP)
ENC_SW = Pin(0, Pin.IN, Pin.PULL_UP)

BUTTON_PINS = [
    9, 10, 11, 12, 13,
    14, 15, 16, 17, 18
]

buttons = [
    Pin(pin, Pin.IN, Pin.PULL_UP)
    for pin in BUTTON_PINS
]


# ============================================================
# CALIBRATED ENCODER
# ============================================================

TRANSITIONS = {
    0: {1: -1, 2: 1},
    1: {3: -1, 0: 1},
    3: {2: -1, 1: 1},
    2: {0: -1, 3: 1},
}

last_state = (CLK.value() << 1) | DT.value()

encoder_count = 0
encoder_position = 0


# ============================================================
# DISPLAY
# ============================================================

event = "Ready"


def show_screen():
    clear()

    oled.text("Now Playing:", 0, 0)

    oled.text(current_track, 0, 16)
    oled.text(current_artist, 0, 32)

    if current_app:
        oled.text(f"[{current_app}]", 0, 48)
        oled.text(event, 0, 56)
    else:
        oled.text(event, 0, 48)

    oled_show()


# Initial screen
show_screen()


# ============================================================
# MAIN LOOP
# ============================================================

last_button_states = [1] * 10
last_sw = 1

while True:

    # --------------------------------------------------------
    # SERIAL INPUT
    # --------------------------------------------------------

    check_serial_input()

    # --------------------------------------------------------
    # ENCODER
    # --------------------------------------------------------

    current_state = (CLK.value() << 1) | DT.value()

    if current_state != last_state:

        movement = TRANSITIONS.get(
            last_state,
            {}
        ).get(
            current_state,
            0
        )

        if movement != 0:

            encoder_count += movement

            if encoder_count >= 2:

                encoder_position += 1
                encoder_count = 0

                event = "Encoder: CW"

                print(
                    "Encoder CW | Position:",
                    encoder_position
                )

                show_screen()

            elif encoder_count <= -2:

                encoder_position -= 1
                encoder_count = 0

                event = "Encoder: CCW"

                print(
                    "Encoder CCW | Position:",
                    encoder_position
                )

                show_screen()

        last_state = current_state


    # --------------------------------------------------------
    # 10 BUTTONS
    # --------------------------------------------------------

    for i in range(10):

        state = buttons[i].value()

        if state == 0 and last_button_states[i] == 1:

            event = "Button " + str(i + 1)

            print("Button", i + 1, "pressed")

            show_screen()

        last_button_states[i] = state


    # --------------------------------------------------------
    # ENCODER PUSH BUTTON
    # --------------------------------------------------------

    sw = ENC_SW.value()

    if sw == 0 and last_sw == 1:

        event = "Encoder SW"

        print("Encoder switch pressed")

        show_screen()

    last_sw = sw

    time.sleep_ms(2)

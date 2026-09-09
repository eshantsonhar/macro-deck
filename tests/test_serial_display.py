"""
Simple test for serial display functionality
Run with: mpremote connect COM4 run tests/test_serial_display.py
Or upload and run standalone
"""

from machine import Pin, I2C, UART
import framebuf
import time

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

uart = UART(0, 115200)

current_track = "No Track"
current_artist = "Playing"
serial_buffer = ""


def parse_serial_message(line):
    """
    Parse serial message from PC bridge
    Format: TRACK|song name|artist name
    """
    global current_track, current_artist
    
    if line.startswith("TRACK|"):
        parts = line.split("|")
        if len(parts) >= 3:
            current_track = parts[1]
            current_artist = parts[2]
            return True
    
    return False


def show_screen():
    clear()

    oled.text("Now Playing:", 0, 0)

    oled.text(current_track, 0, 16)
    oled.text(current_artist, 0, 32)

    oled.text("Type: TRACK|name|artist", 0, 56)

    oled_show()


# Initial screen
show_screen()

print("Serial Display Test")
print("Waiting for serial data...")

# ============================================================
# MAIN LOOP
# ============================================================

while True:
    try:
        if uart.any():
            data = uart.read()
            if data:
                serial_buffer += data.decode('utf-8')
                # Process all complete lines
                while '\n' in serial_buffer:
                    line, serial_buffer = serial_buffer.split('\n', 1)
                    line = line.strip()
                    if line and parse_serial_message(line):
                        print(f"Updated: {current_track} - {current_artist}")
                        show_screen()
    except Exception:
        pass
    
    time.sleep_ms(10)

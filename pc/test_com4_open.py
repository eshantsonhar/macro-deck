"""
Bounded test: open COM4 and inspect properties
"""

import serial
import time

print("Test: Opening COM4")
try:
    ser = serial.Serial("COM4", 115200, timeout=1)
    print(f"SUCCESS: COM4 opened")
    print(f"Port: {ser.port}")
    print(f"Baudrate: {ser.baudrate}")
    print(f"Is open: {ser.is_open}")
    time.sleep(0.5)
    ser.close()
    print("SUCCESS: COM4 closed")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

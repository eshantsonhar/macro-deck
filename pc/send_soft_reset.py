"""
Send soft-reset to Pico via serial
"""

import serial
import time

print("Sending soft-reset to Pico")
try:
    ser = serial.Serial("COM4", 115200, timeout=2)
    print(f"SUCCESS: COM4 opened")
    
    # Send Ctrl+D twice (soft-reset)
    ser.write(b'\x04')
    time.sleep(0.2)
    ser.write(b'\x04')
    time.sleep(0.5)
    
    print("Soft-reset commands sent")
    
    ser.close()
    print("SUCCESS: COM4 closed")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

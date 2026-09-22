"""
Send exact TRACK|TEST|TEST| message as requested by user
"""

import serial
import time

print("Sending exact TRACK|TEST|TEST| message...")
try:
    ser = serial.Serial("COM4", 115200, timeout=1, write_timeout=2)
    print(f"SUCCESS: COM4 opened")
    
    # Send exact message requested
    payload = b"TRACK|TEST|TEST|\n"
    print(f"Sending: {repr(payload)}")
    ser.write(payload)
    print("Write completed")
    
    # Small wait
    time.sleep(0.5)
    
    ser.close()
    print("SUCCESS: COM4 closed")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

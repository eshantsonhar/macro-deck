"""
Test A: Check for existing device output
Read-only test - do not write anything
"""

import serial
import time

print("Test A: Opening COM4 for read-only")
try:
    ser = serial.Serial("COM4", 115200, timeout=1)
    print(f"SUCCESS: COM4 opened")
    
    # Wait a moment and check for any existing output
    print("Waiting for existing output...")
    time.sleep(1)
    
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)
        print(f"Existing output: {repr(data)}")
    else:
        print("No existing output available")
    
    ser.close()
    print("SUCCESS: COM4 closed")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

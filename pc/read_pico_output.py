"""
Read from COM4 to check if Pico is sending encoder/button messages
"""

import serial
import time

print("Reading from COM4 to check Pico output...")
try:
    ser = serial.Serial("COM4", 115200, timeout=2)
    print(f"SUCCESS: COM4 opened")
    
    # Read for 5 seconds
    print("Reading for 5 seconds...")
    start = time.time()
    total_bytes = 0
    
    while time.time() - start < 5:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            total_bytes += len(data)
            print(f"Received: {repr(data)}")
        time.sleep(0.1)
    
    print(f"Total bytes received: {total_bytes}")
    
    ser.close()
    print("SUCCESS: COM4 closed")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

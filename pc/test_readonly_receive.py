"""
Test C: Read-only receive test
Attempt to read any incoming data without writing
"""

import serial
import time

print("Test C: Opening COM4 for read-only receive test")
try:
    ser = serial.Serial("COM4", 115200, timeout=1)
    print(f"SUCCESS: COM4 opened")
    
    # Read for 3 seconds without writing anything
    print("Reading for 3 seconds...")
    start = time.time()
    total_bytes = 0
    
    while time.time() - start < 3:
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

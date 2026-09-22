"""
Bounded test: write TRACK|TEST|TEST| to COM4
"""

import serial
import time

print("Test: Opening COM4")
try:
    ser = serial.Serial("COM4", 115200, timeout=1, write_timeout=2)
    print(f"SUCCESS: COM4 opened")
    
    payload = b"TRACK|TEST|TEST|\n"
    print(f"Attempting write: {len(payload)} bytes - {repr(payload)}")
    
    start = time.time()
    ser.write(payload)
    elapsed = time.time() - start
    
    print(f"SUCCESS: Write completed in {elapsed:.3f}s")
    
    time.sleep(0.5)
    ser.close()
    print("SUCCESS: COM4 closed")
    
except Exception as e:
    elapsed = time.time() - start if 'start' in locals() else 0
    print(f"ERROR after {elapsed:.3f}s: {type(e).__name__}: {e}")

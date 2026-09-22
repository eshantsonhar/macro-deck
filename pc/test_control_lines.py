"""
Test B: Check USB CDC control-line status
Read-only test - do not toggle lines
"""

import serial

print("Test B: Opening COM4 to check control lines")
try:
    ser = serial.Serial("COM4", 115200, timeout=1)
    print(f"SUCCESS: COM4 opened")
    
    # Query control lines (read-only)
    print(f"CTS: {ser.cts}")
    print(f"DSR: {ser.dsr}")
    print(f"CD: {ser.cd}")
    print(f"RI: {ser.ri}")
    
    ser.close()
    print("SUCCESS: COM4 closed")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

"""
Exit raw REPL mode
"""

import serial
import time

print("Exiting raw REPL mode...")
try:
    ser = serial.Serial("COM4", 115200, timeout=2)
    print(f"SUCCESS: COM4 opened")
    
    # Send Ctrl+B to exit raw REPL
    ser.write(b'\x02')
    time.sleep(0.5)
    
    # Check for response
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"Response: {repr(response)}")
    else:
        print("No response")
    
    ser.close()
    print("SUCCESS: COM4 closed")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

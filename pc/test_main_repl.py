"""
Try to run main.py from REPL and see if there's an error
"""

import serial
import time

print("Running main.py from REPL to check for errors...")
try:
    ser = serial.Serial("COM4", 115200, timeout=2)
    print(f"SUCCESS: COM4 opened")
    
    # Interrupt any running program
    ser.write(b'\x03')
    time.sleep(0.2)
    ser.write(b'\x03')
    time.sleep(0.2)
    
    # Run main.py
    ser.write(b'import main\r\n')
    time.sleep(2)
    
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

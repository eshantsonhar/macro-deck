"""
Check main.py file on Pico
"""

import serial
import time

print("Checking main.py on Pico...")
try:
    ser = serial.Serial("COM4", 115200, timeout=2)
    print(f"SUCCESS: COM4 opened")
    
    # Interrupt any running program
    ser.write(b'\x03')
    time.sleep(0.2)
    ser.write(b'\x03')
    time.sleep(0.2)
    
    # Enter raw REPL
    ser.write(b'\x01')
    time.sleep(0.5)
    
    # Check file
    ser.write(b'import os; f = open("main.py", "r"); content = f.read(); f.close(); print(len(content))\r\n')
    time.sleep(1)
    
    # Execute
    ser.write(b'\x04')
    time.sleep(1)
    
    # Exit raw REPL
    ser.write(b'\x02')
    time.sleep(0.5)
    
    # Check response
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"Response: {repr(response)}")

    ser.close()
    print("Complete!")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

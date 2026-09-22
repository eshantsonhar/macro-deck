"""
Delete main.py from Pico filesystem
"""

import serial
import time

print("Deleting main.py from Pico filesystem...")

# Connect to Pico
ser = serial.Serial('COM4', 115200, timeout=2)
time.sleep(1)

# Interrupt any running program
ser.write(b'\x03')
time.sleep(0.2)
ser.write(b'\x03')
time.sleep(0.2)

# Enter raw REPL
ser.write(b'\x01')
time.sleep(0.5)

# Delete main.py
ser.write(b'import os; os.remove("main.py")\r\n')
time.sleep(0.5)

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

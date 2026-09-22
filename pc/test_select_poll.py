"""
Test if select.poll() works on the Pico
"""

import serial
import time

print("Testing select.poll() on Pico...")
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

    # Test select.poll()
    ser.write(b'import sys, select; p = select.poll(); p.register(sys.stdin, select.POLLIN); print("poll works:", p.poll(0))\r\n')
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

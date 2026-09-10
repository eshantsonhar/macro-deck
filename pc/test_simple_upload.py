import serial
import time

print("Testing simple upload to Pico...")

# Create a minimal test program
test_code = """
from machine import Pin
import time

led = Pin(25, Pin.OUT)
while True:
    led.value(1)
    time.sleep(0.5)
    led.value(0)
    time.sleep(0.5)
"""

ser = serial.Serial('COM4', 115200, timeout=2)
time.sleep(1)

# Try to enter raw REPL
print("Entering raw REPL...")
ser.write(b'\r\n')
time.sleep(0.2)
ser.write(b'\x03')  # Ctrl+C
time.sleep(0.2)
ser.write(b'\x01')  # Ctrl+A (raw REPL)
time.sleep(0.5)

# Send the code
print("Sending test code...")
ser.write(test_code.encode('utf-8'))
time.sleep(0.5)

# Execute
ser.write(b'\x04')  # Ctrl+D
time.sleep(0.5)

ser.close()
print("Upload complete")

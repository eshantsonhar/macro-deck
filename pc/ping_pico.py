import serial
import time

print("Testing if Pico is responsive...")
ser = serial.Serial('COM4', 115200, timeout=2)
time.sleep(1)

# Try to send a simple command
ser.write(b'\r\n')
time.sleep(0.2)
ser.write(b'print("hello")\r\n')
time.sleep(0.5)

# Read response
if ser.in_waiting > 0:
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(f"Pico response: {response}")
else:
    print("No response from Pico")

ser.close()

import serial
import time

ser = serial.Serial('COM4', 115200, timeout=10)
print("Sending machine.reset() command...")

# Send machine.reset() command
ser.write(b'import machine; machine.reset()\r\n')

# Give it time to reboot and execute main.py
print("Waiting 5 seconds for boot...")
time.sleep(5)

# Try to capture any output
available = ser.in_waiting
print(f"Bytes available after 5 seconds: {available}")

if available > 0:
    result = ser.read(available)
    print("Boot output:")
    print(repr(result.decode('utf-8', errors='ignore')))
else:
    print("No boot output captured")

ser.close()
print("Connection closed")

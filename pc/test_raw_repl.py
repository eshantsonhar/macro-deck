import serial
import time

print("Attempting to enter raw REPL manually...")

ser = serial.Serial('COM4', 115200, timeout=2)
time.sleep(1)

# Send Ctrl+C multiple times
for i in range(3):
    ser.write(b'\x03')
    time.sleep(0.2)

# Send Ctrl+A to enter raw REPL
ser.write(b'\x01')
time.sleep(0.5)

# Read response
if ser.in_waiting > 0:
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(f"Response: {repr(response)}")
else:
    print("No response")

# Try to send a simple command
ser.write(b'\x04')  # Ctrl+D to soft reset
time.sleep(0.5)

ser.close()
print("Done")

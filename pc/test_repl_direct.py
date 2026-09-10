import serial
import time

print("=== Testing MicroPython REPL on COM4 ===")
print("Opening COM4 at 115200 baud...")

ser = serial.Serial('COM4', 115200, timeout=2)
time.sleep(1)

print("Connected. Sending Ctrl+C to interrupt any running program...")
ser.write(b'\x03')
time.sleep(0.5)

print("Sending Enter to get prompt...")
ser.write(b'\r\n')
time.sleep(0.5)

print("Reading response...")
if ser.in_waiting > 0:
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(f"Response:\n{repr(response)}")
else:
    print("No response")

print("\nSending simple test: 1+1")
ser.write(b'1+1\r\n')
time.sleep(0.5)

if ser.in_waiting > 0:
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(f"Response:\n{repr(response)}")
else:
    print("No response")

ser.close()
print("\nConnection closed")

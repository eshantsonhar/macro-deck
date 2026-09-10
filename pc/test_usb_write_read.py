import serial
import time

print("=== Testing USB CDC write/read without baud rate dependency ===")

ser = serial.Serial('COM4', 115200, timeout=2)
time.sleep(1)

print("Sending Ctrl+C (0x03)...")
ser.write(b'\x03')
time.sleep(0.5)

print("Sending Enter (0x0D 0x0A)...")
ser.write(b'\r\n')
time.sleep(0.5)

print("Reading any response...")
if ser.in_waiting > 0:
    data = ser.read(ser.in_waiting)
    print(f"Received {len(data)} bytes: {repr(data)}")
    print(f"Text: {data.decode('utf-8', errors='ignore')}")
else:
    print("No response")

print("\nSending 'help' command...")
ser.write(b'help\r\n')
time.sleep(0.5)

if ser.in_waiting > 0:
    data = ser.read(ser.in_waiting)
    print(f"Received {len(data)} bytes: {repr(data)}")
    print(f"Text: {data.decode('utf-8', errors='ignore')}")
else:
    print("No response")

ser.close()
print("\nDone")

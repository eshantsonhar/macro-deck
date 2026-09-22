import serial
import time

# Connect to COM4
ser = serial.Serial('COM4', 115200, timeout=10)
print("Connected to COM4")

# Clear any existing data
ser.read(ser.in_waiting)

# Send machine.reset() via serial
print("Sending machine.reset() command...")
ser.write(b'import machine; machine.reset()\r\n')

# Immediately start capturing output
print("Capturing boot output...")
output = b''
start_time = time.time()
timeout = 5  # 5 seconds

while time.time() - start_time < timeout:
    if ser.in_waiting > 0:
        chunk = ser.read(ser.in_waiting)
        output += chunk
        print(f"Captured {len(chunk)} bytes")
    time.sleep(0.1)

ser.close()

print(f"\nTotal bytes captured: {len(output)}")
print("Boot output:")
print(repr(output.decode('utf-8', errors='ignore')))

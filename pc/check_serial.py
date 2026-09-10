import serial
import time

print("Checking what Pico is sending over COM4...")
ser = serial.Serial('COM4', 115200, timeout=2)
ser.timeout = 2

print("Reading for 5 seconds...")
start = time.time()
lines_read = 0
while time.time() - start < 5:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            print(f"LINE: {line}")
            lines_read += 1
    time.sleep(0.01)

ser.close()
print(f"\nTotal lines read: {lines_read}")

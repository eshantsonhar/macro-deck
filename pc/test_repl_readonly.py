import serial
import time

print("=== Testing if Pico sends any data on COM4 ===")
print("Opening COM4 and listening for 5 seconds...")

ser = serial.Serial('COM4', 115200, timeout=1)
time.sleep(1)

print("Listening...")
start = time.time()
data_received = False
all_data = b''

while time.time() - start < 5:
    if ser.in_waiting > 0:
        data = ser.read(ser.in_waiting)
        all_data += data
        data_received = True
        print(f"Received {len(data)} bytes: {repr(data)}")
    time.sleep(0.1)

ser.close()

if data_received:
    print(f"\nTotal data received: {len(all_data)} bytes")
    print(f"Data (as text): {all_data.decode('utf-8', errors='ignore')}")
else:
    print("\nNo data received from Pico")

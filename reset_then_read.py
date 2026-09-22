import subprocess
import serial
import time

print("Step 1: Reset via mpremote...")
subprocess.run(["py", "-m", "mpremote", "connect", "COM4", "reset"], capture_output=True)

print("Step 2: Wait 2 seconds...")
time.sleep(2)

print("Step 3: Open serial and capture...")
ser = serial.Serial('COM4', 115200, timeout=1)
ser.read(ser.in_waiting)  # Clear any existing data

print("Step 4: Monitor for 3 seconds...")
all_data = b''
start = time.time()
while time.time() - start < 3:
    try:
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            all_data += chunk
            print(f"Got chunk: {len(chunk)} bytes")
    except:
        pass
    time.sleep(0.05)

ser.close()

print(f"\nTotal captured: {len(all_data)} bytes")
print("Data:")
print(repr(all_data.decode('utf-8', errors='ignore')))

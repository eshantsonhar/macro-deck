import subprocess
import serial
import time

print("Step 1: Hard reset via mpremote...")
subprocess.run(["py", "-m", "mpremote", "connect", "COM4", "reset"], capture_output=True)

print("Step 2: Wait 1 second...")
time.sleep(1)

print("Step 3: Open serial monitor...")
ser = serial.Serial('COM4', 115200, timeout=5)
print("Connected to COM4")

print("Step 4: Monitor for 5 seconds...")
all_output = b''
start = time.time()
while time.time() - start < 5:
    try:
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            all_output += chunk
            print(f"Captured: {repr(chunk.decode('utf-8', errors='ignore'))}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(0.1)

ser.close()

print(f"\nTotal bytes: {len(all_output)}")
print("Complete output:")
print(repr(all_output.decode('utf-8', errors='ignore')))

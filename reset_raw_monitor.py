import subprocess
import serial
import time

print("=== HARD RESET + RAW SERIAL MONITOR ===")
print()

# Reset via mpremote
print("1. Hard reset via mpremote...")
subprocess.run(
    ["py", "-m", "mpremote", "connect", "COM4", "reset"],
    capture_output=True
)

# Wait 1 second
print("2. Waiting 1 second...")
time.sleep(1)

# Open raw serial and monitor
print("3. Opening raw serial monitor...")
ser = serial.Serial('COM4', 115200, timeout=5)
print("   Connected")

# Monitor for 5 seconds
print("4. Monitoring for 5 seconds...")
all_output = b''
start = time.time()

while time.time() - start < 5:
    try:
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            all_output += chunk
            print(f"   Output: {repr(chunk.decode('utf-8', errors='ignore'))}")
    except Exception as e:
        print(f"   Error: {e}")
    time.sleep(0.1)

ser.close()

print(f"\n5. Total bytes: {len(all_output)}")
print("6. Output:")
print(repr(all_output.decode('utf-8', errors='ignore')))

print("\n=== COMPLETE ===")

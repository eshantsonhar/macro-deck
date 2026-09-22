import serial
import time
import subprocess

print("=== HARD RESET + MONITOR ONLY ===")
print()

# Step 1: Hard reset via mpremote
print("1. Sending hard reset via mpremote...")
subprocess.run(
    ["py", "-m", "mpremote", "connect", "COM4", "reset"],
    capture_output=True
)

# Step 2: Wait 1 second
print("2. Waiting 1 second...")
time.sleep(1)

# Step 3: Open serial and monitor WITHOUT sending anything
print("3. Opening serial port (read-only)...")
ser = serial.Serial('COM4', 115200, timeout=10)
print("   Connected")

# Step 4: Monitor for 10 seconds, just reading what comes out
print("4. Monitoring for 10 seconds (read-only)...")
all_output = b''
start = time.time()
last_output_time = start

while time.time() - start < 10:
    try:
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            all_output += chunk
            last_output_time = time.time()
            print(f"   [{time.time() - start:.1f}s] Captured: {repr(chunk.decode('utf-8', errors='ignore'))}")
    except Exception as e:
        print(f"   Error: {e}")
    time.sleep(0.1)

ser.close()

print(f"\n5. Total bytes captured: {len(all_output)}")
print("6. Complete output:")
print(repr(all_output.decode('utf-8', errors='ignore')))

print("\n=== COMPLETE ===")

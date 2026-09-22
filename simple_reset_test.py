import serial
import time

print("Step 1: Send reset via mpremote...")
import subprocess
subprocess.run(["py", "-m", "mpremote", "connect", "COM4", "reset"], capture_output=True)

print("Step 2: Wait 3 seconds for boot...")
time.sleep(3)

print("Step 3: Open serial port and read any available data...")
try:
    ser = serial.Serial('COM4', 115200, timeout=2)
    time.sleep(0.5)
    available = ser.in_waiting
    print(f"Bytes available: {available}")
    if available > 0:
        data = ser.read(available)
        print("Boot output:")
        print(repr(data.decode('utf-8', errors='ignore')))
    else:
        print("No boot output available")
    ser.close()
except Exception as e:
    print(f"Error: {e}")

print("Step 4: Try REPL via mpremote...")
result = subprocess.run(["py", "-m", "mpremote", "connect", "COM4", "exec", "print('TEST')"], capture_output=True, text=True)
print(f"REPL test output: {result.stdout}")

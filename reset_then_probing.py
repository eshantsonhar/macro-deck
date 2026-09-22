import subprocess
import serial
import time

print("=== HARD RESET + REPL PROBE ===")
print()

# Reset
print("1. Sending hard reset...")
subprocess.run(["py", "-m", "mpremote", "connect", "COM4", "reset"], capture_output=True)

# Wait
print("2. Waiting 1 second...")
time.sleep(1)

# Open serial
print("3. Opening serial port...")
ser = serial.Serial('COM4', 115200, timeout=3)
ser.read(ser.in_waiting)  # Clear

# Send newline to wake REPL
print("4. Sending newline to probe REPL...")
ser.write(b'\r\n')
time.sleep(0.5)

# Read response
available = ser.in_waiting
print(f"5. Bytes available: {available}")

if available > 0:
    data = ser.read(available)
    print("Response:")
    print(repr(data.decode('utf-8', errors='ignore')))
else:
    print("No response to newline")

# Send a simple command
print("6. Sending test command...")
ser.write(b'print("TEST")\r\n')
time.sleep(0.5)

available = ser.in_waiting
if available > 0:
    data = ser.read(available)
    print("Response to test:")
    print(repr(data.decode('utf-8', errors='ignore')))

ser.close()
print("\n=== COMPLETE ===")

import subprocess
import serial
import time

print("=== BOOT CAPTURE TEST ===")
print()

# Step 1: Reset the board
print("Step 1: Sending reset command...")
result = subprocess.run(
    ["py", "-m", "mpremote", "connect", "COM4", "reset"],
    capture_output=True,
    text=True
)
print(f"Reset result: {result.stdout if result.stdout else 'OK'}")
print(f"Reset stderr: {result.stderr if result.stderr else 'None'}")

# Step 2: Wait for reboot
print("\nStep 2: Waiting 4 seconds for boot...")
time.sleep(4)

# Step 3: Open serial and check what's there
print("\nStep 3: Opening serial port...")
try:
    ser = serial.Serial('COM4', 115200, timeout=2)
    print("Connected to COM4")

    # Send a newline to wake up REPL if it's waiting
    ser.write(b'\r\n')
    time.sleep(0.5)

    # Read everything available
    available = ser.in_waiting
    print(f"Bytes available: {available}")

    if available > 0:
        data = ser.read(available)
        print("Output after reset:")
        print(repr(data.decode('utf-8', errors='ignore')))
    else:
        print("No output available after reset")

    # Try to execute a simple command
    print("\nStep 4: Sending test command...")
    ser.write(b'print("BOOT_TEST")\r\n')
    time.sleep(0.5)

    available = ser.in_waiting
    if available > 0:
        data = ser.read(available)
        print("Response to test command:")
        print(repr(data.decode('utf-8', errors='ignore')))

    ser.close()
    print("\nConnection closed")

except Exception as e:
    print(f"Error: {e}")

print("\n=== TEST COMPLETE ===")

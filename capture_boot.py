import serial
import time

ser = serial.Serial('COM4', 115200, timeout=5)
print("Monitoring COM4 for boot output...")
print("Capturing for 5 seconds...")

# Send machine.reset() command
ser.write(b'import machine; machine.reset()\r\n')

# Wait and capture boot output
time.sleep(5)
available = ser.in_waiting
print(f"Bytes available after 5 seconds: {available}")

if available > 0:
    result = ser.read(available)
    print("Boot output:")
    print(repr(result.decode('utf-8', errors='ignore')))
else:
    print("No boot output captured")

ser.close()

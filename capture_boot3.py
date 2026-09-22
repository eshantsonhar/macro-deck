import serial
import time

ser = serial.Serial('COM4', 115200, timeout=10)
print("Connected to COM4")

# Try to establish a connection first
ser.write(b'\r\n')
time.sleep(0.5)
ser.read(ser.in_waiting)

print("Sending machine.reset() command...")
ser.write(b'import machine; machine.reset()\r\n')

# Wait for disconnection
print("Waiting for disconnect...")
time.sleep(1)

# Wait for reconnection
print("Waiting for reconnection...")
time.sleep(4)

# Try to reconnect
print("Attempting to reconnect...")
ser.close()
time.sleep(1)

try:
    ser = serial.Serial('COM4', 115200, timeout=10)
    print("Reconnected to COM4")
    
    # Try to read any boot output
    time.sleep(1)
    available = ser.in_waiting
    print(f"Bytes available after reconnect: {available}")
    
    if available > 0:
        result = ser.read(available)
        print("Boot output:")
        print(repr(result.decode('utf-8', errors='ignore')))
    else:
        print("No boot output captured")
    
    ser.close()
except Exception as e:
    print(f"Reconnection failed: {e}")

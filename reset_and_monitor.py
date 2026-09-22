import serial
import time

print("Opening COM4...")
ser = serial.Serial('COM4', 115200, timeout=5)
print("Connected. Clearing buffer...")
ser.read(ser.in_waiting)

print("Sending machine.reset() command...")
ser.write(b'import machine; machine.reset()\r\n')

print("Monitoring boot output for 5 seconds...")
all_output = b''
start_time = time.time()

while time.time() - start_time < 5:
    try:
        if ser.in_waiting > 0:
            chunk = ser.read(ser.in_waiting)
            all_output += chunk
            print(f"Captured: {repr(chunk.decode('utf-8', errors='ignore'))}")
    except Exception as e:
        print(f"Error reading: {e}")
    time.sleep(0.1)

print(f"\nTotal bytes captured: {len(all_output)}")
print("Complete output:")
print(repr(all_output.decode('utf-8', errors='ignore')))

ser.close()
print("Connection closed")

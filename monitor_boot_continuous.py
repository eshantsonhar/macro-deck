import serial
import time

print("Starting continuous serial monitor on COM4...")
ser = serial.Serial('COM4', 115200, timeout=1)
print("Connected. Monitoring for 10 seconds...")

start_time = time.time()
all_output = b''

while time.time() - start_time < 10:
    if ser.in_waiting > 0:
        chunk = ser.read(ser.in_waiting)
        all_output += chunk
        try:
            print(chunk.decode('utf-8', errors='ignore'), end='')
        except:
            print(repr(chunk))
    time.sleep(0.05)

ser.close()

print(f"\n\nTotal bytes captured: {len(all_output)}")
print("Complete output:")
print(repr(all_output.decode('utf-8', errors='ignore')))

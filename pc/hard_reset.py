import serial
import time

print("Connecting to COM4...")
ser = serial.Serial('COM4', 115200, timeout=1)
time.sleep(0.5)

print("Sending multiple break signals...")
for i in range(5):
    ser.send_break()
    time.sleep(0.2)
    ser.write(b'\x03')  # Ctrl+C
    time.sleep(0.2)

print("Waiting for Pico to settle...")
time.sleep(2)

ser.close()
print("Connection closed")
print("Wait 2 seconds before attempting upload...")

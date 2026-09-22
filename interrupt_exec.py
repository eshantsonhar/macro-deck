import serial
import time

ser = serial.Serial('COM4', 115200, timeout=1)
ser.write(b'\x03')
time.sleep(0.5)
if ser.in_waiting > 0:
    print(ser.read(ser.in_waiting).decode('utf-8', errors='ignore'))
ser.close()

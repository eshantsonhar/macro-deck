import serial
import time

ser = serial.Serial('COM4', 115200, timeout=5)
ser.write(b'\x04')
time.sleep(4)
available = ser.in_waiting
print('Bytes available:', available)
if available > 0:
    result = ser.read(available)
    print('Boot output:', repr(result.decode('utf-8', errors='ignore')))
ser.close()

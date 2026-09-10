import serial
import time

print("Aggressive reset of Pico via serial...")
ser = serial.Serial('COM4', 1200, timeout=1)  # 1200 baud triggers bootloader
time.sleep(0.5)
ser.close()

print("Wait 2 seconds for Pico to reboot...")
time.sleep(2)

print("Pico should now be in bootloader mode or fresh reset")
print("Attempting to connect at 115200 baud...")
try:
    ser = serial.Serial('COM4', 115200, timeout=2)
    time.sleep(1)
    print("Connected at 115200 baud")
    ser.close()
except Exception as e:
    print(f"Connection failed: {e}")

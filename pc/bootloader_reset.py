import serial
import time

print("Triggering Pico bootloader mode via 1200 baud reset...")
ser = serial.Serial('COM4', 1200, timeout=1)
ser.setDTR(False)
time.sleep(0.1)
ser.setDTR(True)
time.sleep(0.1)
ser.close()

print("Wait 3 seconds for Pico to enter bootloader...")
time.sleep(3)

print("Pico should now be in bootloader mode")
print("You can now use mpremote to upload")

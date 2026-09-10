import serial
import time

print("Attempting to force Pico into bootloader mode...")

# Try multiple methods
methods = [
    ("1200 baud reset", 1200),
    ("9600 baud reset", 9600),
]

for name, baud in methods:
    print(f"\nTrying {name}...")
    try:
        ser = serial.Serial('COM4', baud, timeout=1)
        time.sleep(0.5)
        ser.setDTR(False)
        time.sleep(0.1)
        ser.setDTR(True)
        time.sleep(0.1)
        ser.setDTR(False)
        time.sleep(0.5)
        ser.close()
        print(f"  {name} sent")
        time.sleep(2)
    except Exception as e:
        print(f"  {name} failed: {e}")

print("\nWait 5 seconds for Pico to settle...")
time.sleep(5)

print("Check if RPI-RP2 drive appears...")

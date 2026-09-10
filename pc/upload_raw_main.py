import serial
import time

print("Uploading main.py to Pico via raw serial...")

# Read the main.py file
with open(r"C:\Eshant_Sonhar\misc coding projects\diy_macro_deck\main.py", "r") as f:
    code = f.read()

# Connect to Pico
ser = serial.Serial('COM4', 115200, timeout=2)
time.sleep(1)

# Enter raw REPL
ser.write(b'\r\n')
time.sleep(0.2)
ser.write(b'\x03')  # Ctrl+C
time.sleep(0.2)
ser.write(b'\x01')  # Ctrl+A (enter raw REPL)
time.sleep(0.5)

# Send the code
ser.write(code.encode('utf-8'))
time.sleep(0.5)

# Exit raw REPL
ser.write(b'\x04')  # Ctrl+D (execute)
time.sleep(0.5)

# Soft reset
ser.write(b'\x04')  # Ctrl+D (soft reset)
time.sleep(0.5)

ser.close()
print("Upload complete!")
print("The Pico should now be running the new main.py")

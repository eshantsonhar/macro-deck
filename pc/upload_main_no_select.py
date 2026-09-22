"""
Upload main.py to Pico filesystem using raw REPL - without select
"""

import serial
import time

print("Uploading main.py to Pico filesystem...")

# Read the main.py file
with open(r"C:\Eshant_Sonhar\misc coding projects\diy_macro_deck\main.py", "r") as f:
    content = f.read()

# Connect to Pico
ser = serial.Serial('COM4', 115200, timeout=2)
time.sleep(1)

# Interrupt any running program
ser.write(b'\x03')
time.sleep(0.2)
ser.write(b'\x03')
time.sleep(0.2)

# Enter raw REPL
ser.write(b'\x01')
time.sleep(0.5)

# Create the file using write() with escaped content
upload_script = f'''
f = open("main.py", "w")
f.write({repr(content)})
f.close()
print("File written")
'''

ser.write(upload_script.encode('utf-8'))
time.sleep(0.5)

# Execute the script
ser.write(b'\x04')
time.sleep(1)

# Exit raw REPL
ser.write(b'\x02')
time.sleep(0.5)

# Check response
if ser.in_waiting > 0:
    response = ser.read(ser.in_waiting)
    print(f"Response: {repr(response)}")

ser.close()
print("Upload complete!")

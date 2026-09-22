"""
Send TRACK message and then try to read response
"""

import serial
import time

print("Testing TRACK send and read...")
try:
    ser = serial.Serial("COM4", 115200, timeout=2)
    print(f"SUCCESS: COM4 opened")
    
    # Send TRACK message
    payload = b"TRACK|TestSong|TestArtist|TestApp\n"
    print(f"Sending: {repr(payload)}")
    ser.write(payload)
    print("Write completed")
    
    # Wait and read
    time.sleep(1)
    
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"Response: {repr(response)}")
    else:
        print("No response")
    
    ser.close()
    print("SUCCESS: COM4 closed")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

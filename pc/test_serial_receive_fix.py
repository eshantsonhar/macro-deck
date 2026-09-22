"""
Test serial receive fix - send TRACK message and check if Pico responds
"""

import serial
import time

print("Test: Opening COM4 and sending TRACK message")
try:
    ser = serial.Serial("COM4", 115200, timeout=2)
    print(f"SUCCESS: COM4 opened")
    
    # Send a test TRACK message
    payload = b"TRACK|TestSong|TestArtist|TestApp\n"
    print(f"Sending: {repr(payload)}")
    ser.write(payload)
    print("Write completed")
    
    # Wait for response
    time.sleep(1)
    
    # Check for any response
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"Response from Pico: {repr(response)}")
    else:
        print("No response from Pico (may be normal if no output)")
    
    time.sleep(0.5)
    ser.close()
    print("SUCCESS: COM4 closed")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

"""
Try to interrupt MicroPython using pyserial break signal
"""

import serial
import time

print("Test: Opening COM4 and sending break signal")
try:
    ser = serial.Serial("COM4", 115200, timeout=1)
    print(f"SUCCESS: COM4 opened")
    
    # Send break signal (equivalent to Ctrl+C in many terminals)
    print("Sending break signal...")
    ser.send_break(duration=0.25)
    time.sleep(0.5)
    
    # Try to send Ctrl+C explicitly
    print("Sending Ctrl+C...")
    ser.write(b'\x03')
    time.sleep(0.5)
    
    # Try to read response
    print("Checking for response...")
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"Response: {repr(response)}")
    else:
        print("No response")
    
    ser.close()
    print("SUCCESS: COM4 closed")
    
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

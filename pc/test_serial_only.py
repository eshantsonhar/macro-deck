"""
Test if serial connection is the issue
"""

import serial

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

print("Testing serial connection...")
print()

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
    
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    print("Buffers reset")
    
    ser.write(b"TRACK|Test|Artist|App\n")
    print("Sent test message")
    
    ser.close()
    print("Closed successfully")
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

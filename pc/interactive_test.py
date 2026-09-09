"""
Interactive test - send data and check for response
"""

import serial
import time

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
    print(f"Connected to {SERIAL_PORT}")
    
    # Clear buffers
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    # Send test data
    test_message = "TRACK|Test Song|Test Artist\n"
    print(f"Sending: {test_message.strip()}")
    ser.write(test_message.encode('utf-8'))
    
    # Wait for response
    time.sleep(1)
    
    # Read response
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting)
        print(f"Response from Pico: {response.decode('utf-8', errors='ignore')}")
    else:
        print("No response from Pico")
    
    ser.close()
    print("Connection closed")
    
except Exception as e:
    print(f"Error: {e}")

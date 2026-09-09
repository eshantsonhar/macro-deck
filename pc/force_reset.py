"""
Force reset Pico by sending break signal
"""
import serial
import time

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {SERIAL_PORT}")
    
    # Send break signal to interrupt running program
    ser.send_break()
    time.sleep(0.5)
    
    # Send Ctrl+C
    ser.write(b'\x03')
    time.sleep(0.5)
    
    print("Sent break signal and Ctrl+C")
    ser.close()
    print("Connection closed")
    
except Exception as e:
    print(f"Error: {e}")

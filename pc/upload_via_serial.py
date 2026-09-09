"""
Upload main.py to Pico via direct serial communication
"""

import serial
import time

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

def send_file_via_serial(ser, file_path):
    """Send a Python file to Pico over serial"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Send Ctrl+C to stop any running program
    ser.write(b'\x03')
    time.sleep(0.5)
    
    # Send Ctrl+D to enter paste mode
    ser.write(b'\x04')
    time.sleep(0.5)
    
    # Send the file content
    ser.write(content.encode('utf-8'))
    time.sleep(0.5)
    
    # Send Ctrl+D to execute
    ser.write(b'\x04')
    time.sleep(0.5)
    
    print(f"File {file_path} sent to Pico")

def main():
    print(f"Connecting to {SERIAL_PORT}...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print("Connected!")
        
        # Read main.py
        main_py_path = r"C:\Users\eshan\Documents\PicoW-Controller\main.py"
        
        # Stop any running program
        print("Stopping any running program...")
        ser.write(b'\x03')
        time.sleep(1)
        
        # Clear buffer
        ser.reset_input_buffer()
        
        # Send file upload command using mpremote approach
        print("Attempting to upload file...")
        
        # First try to enter raw REPL
        ser.write(b'\r\n')
        time.sleep(0.5)
        
        # Send Ctrl+C to interrupt
        for _ in range(3):
            ser.write(b'\x03')
            time.sleep(0.2)
        
        # Send Ctrl+B to enter raw REPL
        ser.write(b'\x02')
        time.sleep(0.5)
        
        # Try to send the file content as a series of exec commands
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Break into chunks and send
        chunk_size = 1000
        for i in range(0, len(content), chunk_size):
            chunk = content[i:i+chunk_size]
            ser.write(chunk.encode('utf-8'))
            time.sleep(0.1)
        
        print("File content sent")
        
        ser.close()
        print("Connection closed")
        
    except Exception as e:
        print(f"Error: {e}")
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()

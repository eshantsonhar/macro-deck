"""
Upload main.py to Pico using raw serial commands (no mpremote)
"""

import serial
import time

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

def upload_via_raw_serial():
    """Upload main.py by sending it directly to Pico"""
    
    print(f"Connecting to {SERIAL_PORT}...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        print("Connected!")
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Send multiple Ctrl+C to stop any running program
        print("Stopping any running program...")
        for _ in range(10):
            ser.write(b'\x03')
            time.sleep(0.1)
        
        # Send break signal
        ser.send_break()
        time.sleep(1)
        
        # Clear buffers again
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Try to get to a clean prompt
        ser.write(b'\r\n')
        time.sleep(0.5)
        
        # Read any response
        response = ser.read(ser.in_waiting)
        if response:
            print(f"Got response: {response}")
        
        # Send the new main.py content as a file write operation
        print("Uploading main.py...")
        
        with open(r"C:\Users\eshan\Documents\PicoW-Controller\main.py", 'r') as f:
            content = f.read()
        
        # Send the file write command
        # This writes the content to main.py on the Pico
        command = f"""
with open('main.py', 'w') as f:
    f.write('''{content}''')
print('File written')
"""
        
        # Send the command in chunks
        chunk_size = 500
        for i in range(0, len(command), chunk_size):
            chunk = command[i:i+chunk_size]
            ser.write(chunk.encode('utf-8'))
            time.sleep(0.05)
        
        time.sleep(1)
        
        # Send Ctrl+D to execute
        ser.write(b'\x04')
        time.sleep(2)
        
        # Read response
        response = ser.read(ser.in_waiting)
        if response:
            print(f"Response: {response.decode('utf-8', errors='ignore')}")
        
        ser.close()
        print("Upload complete!")
        print("Please reset the Pico to run the new main.py")
        
    except Exception as e:
        print(f"Error: {e}")
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    upload_via_raw_serial()

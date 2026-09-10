"""
Simple listener to see what Pico is sending
"""

import serial
import time

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

def main():
    print(f"Listening to {SERIAL_PORT} at {BAUD_RATE} baud...")
    print("Rotate encoder or press button to see what Pico sends")
    print("Press Ctrl+C to stop\n")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected!")
        
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        while True:
            try:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    text = data.decode('utf-8', errors='ignore')
                    print(f"Received: {repr(text)}")
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(0.1)
                
    except serial.SerialException as e:
        print(f"Failed to connect: {e}")
    finally:
        if 'ser' in locals():
            ser.close()
            print("Connection closed")

if __name__ == "__main__":
    main()

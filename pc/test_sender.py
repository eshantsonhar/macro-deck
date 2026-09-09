"""
Simple test sender for Pico W Controller
Sends test track data to Pico over serial
"""

import serial
import time

# Serial configuration
SERIAL_PORT = "COM4"
BAUD_RATE = 115200

def main():
    print("Test Sender for Pico W Controller")
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected to Pico!")
        
        # Send test data
        test_tracks = [
            ("Bohemian Rhapsody", "Queen"),
            ("Stairway to Heaven", "Led Zeppelin"),
            ("Hotel California", "Eagles"),
            ("Sweet Child O' Mine", "Guns N' Roses"),
            ("Smells Like Teen Spirit", "Nirvana"),
        ]
        
        print("Sending test tracks...")
        
        for track, artist in test_tracks:
            message = f"TRACK|{track}|{artist}\n"
            ser.write(message.encode('utf-8'))
            print(f"Sent: {message.strip()}")
            time.sleep(3)  # Wait 3 seconds between tracks
        
        # Send "no track" message
        message = "TRACK|No Track|Playing\n"
        ser.write(message.encode('utf-8'))
        print(f"Sent: {message.strip()}")
        
        print("Test complete!")
        
    except serial.SerialException as e:
        print(f"Failed to connect to serial port: {e}")
        print("Make sure Pico is connected and the port is correct.")
    finally:
        if 'ser' in locals():
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()

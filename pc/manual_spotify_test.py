"""
Manual Spotify bridge test - simulates Spotify track changes
"""

import serial
import time

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

def send_to_pico(ser, track, artist, app_name=""):
    """Send track info to Pico over serial"""
    if track and artist:
        message = f"TRACK|{track}|{artist}|{app_name}\n"
        ser.write(message.encode('utf-8'))
        print(f"Sent: {message.strip()}")
    else:
        message = "TRACK|No Track|Playing|\n"
        ser.write(message.encode('utf-8'))
        print("Sent: No track playing")

def format_for_oled(text, max_length=21):
    """Format text for OLED display"""
    if not text:
        return ""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text

def main():
    print("Manual Spotify Bridge Test")
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected to Pico!")

        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Test tracks
        test_tracks = [
            ("Bohemian Rhapsody", "Queen"),
            ("Stairway to Heaven", "Led Zeppelin"),
            ("Hotel California", "Eagles"),
            ("Sweet Child O' Mine", "Guns N' Roses"),
            ("Smells Like Teen Spirit", "Nirvana"),
        ]

        print("Sending test tracks...")
        print("Watch the OLED display for changes!")
        print()

        for track, artist in test_tracks:
            formatted_track = format_for_oled(track)
            formatted_artist = format_for_oled(artist)
            send_to_pico(ser, formatted_track, formatted_artist, "Test")
            time.sleep(3)  # Wait 3 seconds between tracks

        # Send "no track" message
        send_to_pico(ser, "No Track", "Playing")

        print()
        print("Test complete!")
        print("The OLED should now show 'No Track - Playing'")

    except serial.SerialException as e:
        print(f"Failed to connect to serial port: {e}")
    finally:
        if 'ser' in locals():
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()

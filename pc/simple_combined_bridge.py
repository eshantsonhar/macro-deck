"""
Simple Combined Bridge for Pico W Controller
Handles both media display and volume control
Uses non-blocking I/O for bidirectional communication
"""

import serial
import time
import subprocess
import sys
import re
import string

SERIAL_PORT = "COM4"
BAUD_RATE = 115200
POLL_INTERVAL = 2
VOLUME_STEP = 2


def get_media_from_browsers():
    """Get currently playing media from browser tabs"""
    try:
        ps_command = """
        Get-Process | Where-Object {$_.MainWindowTitle -ne ""} |
        Select-Object ProcessName, MainWindowTitle
        """

        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=5
        )

        lines = result.stdout.strip().split('\n')

        browser_patterns = {
            'vivaldi': 'Vivaldi',
            'chrome': 'Chrome',
            'msedge': 'Edge',
            'firefox': 'Firefox',
            'brave': 'Brave',
            'opera': 'Opera'
        }

        for line in lines:
            line = line.strip()
            if not line or 'ProcessName' in line or '---' in line:
                continue

            parts = line.split(None, 1)
            if len(parts) < 2:
                continue

            process_name = parts[0].lower().strip()
            window_title = parts[1].strip()

            for browser, display_name in browser_patterns.items():
                if browser in process_name:
                    skip_keywords = ['start page', 'new tab', 'settings', 'google.com', 'bing.com', 'github.com', 'stackoverflow.com', 'reddit.com', 'twitter.com', 'facebook.com', 'instagram.com', 'linkedin.com', 'devin', 'quota', 'troubleshooting']
                    if any(skip in window_title.lower() for skip in skip_keywords):
                        continue

                    # Handle different separators including special characters
                    allowed_chars = set(string.ascii_letters + string.digits + ' -.,\'')
                    special_chars = [c for c in window_title if c not in allowed_chars and c != ' ']

                    if special_chars:
                        sep = special_chars[0]
                        parts = window_title.split(sep)
                        if len(parts) >= 2:
                            track = parts[0].strip()
                            if len(parts) > 2:
                                artist = sep.join(parts[1:-1]).strip()
                            else:
                                artist = parts[1].strip()
                            for browser_name in ['Vivaldi', 'Chrome', 'Edge', 'Firefox', 'Brave', 'Opera']:
                                artist = artist.replace(browser_name, '').strip()
                            artist = artist.rstrip('-').strip()
                            return track, artist, display_name
                    elif ' - ' in window_title:
                        title_parts = window_title.split(' - ')
                        if len(title_parts) >= 2:
                            track = title_parts[0].strip()
                            artist = title_parts[1].strip()
                            for service in ['YouTube', 'Spotify', 'Music']:
                                artist = artist.replace(service, '').strip()
                            return track, artist, display_name
                    else:
                        parts = window_title.split()
                        if len(parts) >= 2:
                            track = parts[0]
                            artist = ' '.join(parts[1:])
                            artist = ''.join(c for c in artist if c.isprintable())
                            return track, artist, display_name

        return None, None, None

    except Exception as e:
        print(f"Error getting browser media: {e}")
        return None, None, None


def format_for_oled(text, max_length=21):
    if not text:
        return ""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text


def change_volume(direction):
    """Change system volume using keybd_event method"""
    try:
        import ctypes
        import time

        # Send one volume key press per encoder event
        if direction == "UP":
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # VK_VOLUME_UP
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)  # KEYEVENTF_KEYUP
        else:
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # VK_VOLUME_DOWN
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)  # KEYEVENTF_KEYUP
    except Exception as e:
        print(f"[ERROR] Volume control failed: {e}")


def toggle_mute():
    """Toggle system mute using keybd_event"""
    try:
        import ctypes
        import time

        # Send mute key press
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # VK_VOLUME_MUTE
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)  # KEYEVENTF_KEYUP
    except Exception as e:
        print(f"[ERROR] Mute toggle failed: {e}")


def handle_encoder_event(event):
    """Handle encoder event from Pico"""
    if event == "ENCODER_CW":
        change_volume("UP")
    elif event == "ENCODER_CCW":
        change_volume("DOWN")
    elif event == "ENCODER_SW":
        toggle_mute()


def main():
    print("Simple Combined Bridge for Pico W Controller")
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)  # Non-blocking
        print("Connected to Pico!")

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        last_track = None
        last_artist = None
        last_app = None

        print("Monitoring media and volume... (Ctrl+C to stop)")
        print("Encoder: Volume control | Press: Mute toggle")

        # Send initial "No Track" message
        ser.write(b"TRACK|No Track|Playing|\n")

        last_media_check = 0

        while True:
            try:
                # Check for encoder events from Pico
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        handle_encoder_event(line)

                # Check for media changes periodically
                current_time = time.time()
                if current_time - last_media_check >= POLL_INTERVAL:
                    track, artist, app_name = get_media_from_browsers()

                    if track != last_track or artist != last_artist or app_name != last_app:
                        if track and artist:
                            formatted_track = format_for_oled(track)
                            formatted_artist = format_for_oled(artist)
                            formatted_app = format_for_oled(app_name) if app_name else ""
                            message = f"TRACK|{formatted_track}|{formatted_artist}|{formatted_app}\n"
                            ser.write(message.encode('utf-8'))
                            last_track = track
                            last_artist = artist
                            last_app = app_name
                        else:
                            if last_track is not None:
                                ser.write(b"TRACK|No Track|Playing|\n")
                                last_track = None
                                last_artist = None
                                last_app = None

                    last_media_check = current_time

                time.sleep(0.05)  # Small sleep to prevent CPU hogging

            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(0.1)

    except serial.SerialException as e:
        print(f"Failed to connect to serial port: {e}")
        sys.exit(1)
    finally:
        if 'ser' in locals():
            ser.close()
            print("Serial connection closed.")


if __name__ == "__main__":
    main()

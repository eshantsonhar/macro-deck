"""
Browser-Focused Media Bridge for Pico W Controller
Prioritizes browser tabs over mini-player windows
"""

import serial
import time
import subprocess
import sys
import re
import string

# Serial configuration
SERIAL_PORT = "COM4"
BAUD_RATE = 115200

# Polling interval (seconds)
POLL_INTERVAL = 2


def get_media_from_browsers():
    """
    Get currently playing media from browser tabs only.
    Prioritizes browsers to avoid mini-player windows.
    """
    try:
        # Get all window titles from processes
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

        # Browser patterns - prioritize these
        browser_patterns = {
            'vivaldi': 'Vivaldi',
            'chrome': 'Chrome',
            'msedge': 'Edge',
            'firefox': 'Firefox',
            'brave': 'Brave',
            'opera': 'Opera'
        }

        # Look for browser windows first
        for line in lines:
            line = line.strip()
            if not line or 'ProcessName' in line or '---' in line:
                continue

            parts = line.split(None, 1)
            if len(parts) < 2:
                continue

            process_name = parts[0].lower().strip()
            window_title = parts[1].strip()

            # Check if this is a browser
            for browser, display_name in browser_patterns.items():
                if browser in process_name:
                    # Filter out non-media pages
                    skip_keywords = ['start page', 'new tab', 'settings', 'google', 'bing', 'github', 'stackoverflow', 'reddit', 'twitter', 'facebook', 'instagram', 'linkedin', 'devin', 'quota', 'troubleshooting', 'vivaldi', 'chrome', 'edge', 'firefox']
                    if any(skip in window_title.lower() for skip in skip_keywords):
                        continue

                    # Try to extract track/artist from title
                    # Handle different separators including special characters
                    # Look for characters that are not letters, numbers, or common punctuation
                    allowed_chars = set(string.ascii_letters + string.digits + ' -.,\'')
                    special_chars = [c for c in window_title if c not in allowed_chars and c != ' ']

                    if special_chars:
                        # Use the first special character as separator
                        sep = special_chars[0]
                        parts = window_title.split(sep)
                        if len(parts) >= 2:
                            track = parts[0].strip()
                            # The last part is likely the browser name
                            # Everything in between is the artist
                            if len(parts) > 2:
                                artist = sep.join(parts[1:-1]).strip()
                            else:
                                artist = parts[1].strip()

                            # Clean up browser name and trailing dashes from artist
                            for browser_name in ['Vivaldi', 'Chrome', 'Edge', 'Firefox', 'Brave', 'Opera']:
                                artist = artist.replace(browser_name, '').strip()
                            artist = artist.rstrip('-').strip()

                            return track, artist, display_name
                    elif ' - ' in window_title:
                        title_parts = window_title.split(' - ')
                        if len(title_parts) >= 2:
                            track = title_parts[0].strip()
                            artist = title_parts[1].strip()
                            # Remove service names
                            for service in ['YouTube', 'Spotify', 'Music']:
                                artist = artist.replace(service, '').strip()
                            return track, artist, display_name
                    else:
                        # Try space-separated format
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
    """Format text for OLED display"""
    if not text:
        return ""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text


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


def main():
    print("Browser-Focused Media Bridge for Pico W Controller")
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected to Pico!")

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        last_track = None
        last_artist = None
        last_app = None

        print("Monitoring browser tabs... (Ctrl+C to stop)")
        print("Prioritizes browser tabs over mini-player windows")

        send_to_pico(ser, "No Track", "Playing", "")

        while True:
            try:
                track, artist, app_name = get_media_from_browsers()

                if track != last_track or artist != last_artist or app_name != last_app:
                    if track and artist:
                        formatted_track = format_for_oled(track)
                        formatted_artist = format_for_oled(artist)
                        formatted_app = format_for_oled(app_name) if app_name else ""
                        send_to_pico(ser, formatted_track, formatted_artist, formatted_app)
                        last_track = track
                        last_artist = artist
                        last_app = app_name
                    else:
                        if last_track is not None:
                            send_to_pico(ser, "No Track", "Playing", "")
                            last_track = None
                            last_artist = None
                            last_app = None

                time.sleep(POLL_INTERVAL)

            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error in loop: {e}")
                time.sleep(POLL_INTERVAL)

    except serial.SerialException as e:
        print(f"Failed to connect to serial port: {e}")
        sys.exit(1)
    finally:
        if 'ser' in locals():
            ser.close()
            print("Serial connection closed.")


if __name__ == "__main__":
    main()

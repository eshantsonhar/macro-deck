"""
Combined Bridge for Pico W Controller
Handles both media display and volume control
Bidirectional communication with Pico
"""

import serial
import time
import subprocess
import sys
import re
import string
import threading

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
    """Change system volume"""
    try:
        current_result = subprocess.run(
            ["powershell", "-Command", "(Get-AudioDevice -RenderingControl).Volume"],
            capture_output=True,
            text=True,
            timeout=5
        )
        current = int(current_result.stdout.strip()) if current_result.stdout.strip() else 50

        if direction == "UP":
            new_volume = current + VOLUME_STEP
        else:
            new_volume = current - VOLUME_STEP

        new_volume = max(0, min(100, new_volume))
        subprocess.run(
            ["powershell", "-Command", f"Set-AudioDevice -RenderingVolume {new_volume}"],
            capture_output=True,
            timeout=5
        )
        print(f"Volume: {new_volume}%")
    except Exception as e:
        print(f"Error changing volume: {e}")


def toggle_mute():
    """Toggle system mute"""
    try:
        subprocess.run(
            ["powershell", "-Command", "$m = Get-AudioDevice -RenderingMute; Set-AudioDevice -RenderingMute (-not $m)"],
            capture_output=True,
            timeout=5
        )
        print("Mute toggled")
    except Exception as e:
        print(f"Error toggling mute: {e}")


def handle_volume_command(line):
    """Handle volume command from Pico"""
    if line == "VOLUME|UP":
        change_volume("UP")
    elif line == "VOLUME|DOWN":
        change_volume("DOWN")
    elif line == "VOLUME|MUTE":
        toggle_mute()


def volume_listener(ser):
    """Thread to listen for volume commands from Pico"""
    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    handle_volume_command(line)
            time.sleep(0.05)  # Slightly longer sleep to reduce CPU usage
        except Exception as e:
            print(f"Volume listener error: {e}")
            break


def main():
    print("Combined Bridge for Pico W Controller")
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected to Pico!")

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Start volume listener thread
        volume_thread = threading.Thread(target=volume_listener, args=(ser,), daemon=True)
        volume_thread.start()

        last_track = None
        last_artist = None
        last_app = None

        print("Monitoring media and volume... (Ctrl+C to stop)")
        print("Encoder: Volume control | Press: Mute toggle")

        # Send initial "No Track" message
        ser.write(b"TRACK|No Track|Playing|\n")

        while True:
            try:
                track, artist, app_name = get_media_from_browsers()

                if track != last_track or artist != last_artist or app_name != last_app:
                    if track and artist:
                        formatted_track = format_for_oled(track)
                        formatted_artist = format_for_oled(artist)
                        formatted_app = format_for_oled(app_name) if app_name else ""
                        message = f"TRACK|{formatted_track}|{formatted_artist}|{formatted_app}\n"
                        ser.write(message.encode('utf-8'))
                        print(f"Media: {formatted_track} - {formatted_artist} [{formatted_app}]")
                        last_track = track
                        last_artist = artist
                        last_app = app_name
                    else:
                        if last_track is not None:
                            ser.write(b"TRACK|No Track|Playing|\n")
                            print("Media: No Track - Playing")
                            last_track = None
                            last_artist = None
                            last_app = None

                time.sleep(POLL_INTERVAL)

            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error in media loop: {e}")
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

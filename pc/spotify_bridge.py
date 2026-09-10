"""
Media Bridge for Pico W Controller
Gets currently playing media from any player and sends to Pico over serial
Supports: Spotify, Windows Media Player, VLC, YouTube, and more
"""

import serial
import time
import subprocess
import sys
import re

# Serial configuration
SERIAL_PORT = "COM4"
BAUD_RATE = 115200

# Polling interval (seconds)
POLL_INTERVAL = 2


def get_media_from_window_title():
    """
    Get currently playing media from window titles across multiple players.
    Supports Spotify, Windows Media Player, VLC, YouTube (browser), etc.
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

        # Media player patterns and their name extraction logic
        # Browsers are prioritized to avoid mini-player windows
        media_patterns = {
            'vivaldi': {
                'pattern': r'(.+)',  # Match any content in Vivaldi
                'app_name': 'Browser',
                'priority': 10  # Highest priority for browsers
            },
            'chrome': {
                'pattern': r'(.+)',  # Match any content in Chrome
                'app_name': 'Browser',
                'priority': 10
            },
            'msedge': {
                'pattern': r'(.+)',  # Match any content in Edge
                'app_name': 'Browser',
                'priority': 10
            },
            'firefox': {
                'pattern': r'(.+)',  # Match any content in Firefox
                'app_name': 'Browser',
                'priority': 10
            },
            'brave': {
                'pattern': r'(.+)',  # Match any content in Brave
                'app_name': 'Browser',
                'priority': 10
            },
            'opera': {
                'pattern': r'(.+)',  # Match any content in Opera
                'app_name': 'Browser',
                'priority': 10
            },
            'spotify': {
                'pattern': r'(.+?)\s*-\s*(.+?)(?:\s*-\s*Spotify)?$',
                'app_name': 'Spotify',
                'priority': 5  # Lower priority to avoid mini-player
            },
            'vlc': {
                'pattern': r'(.+?)\s*-\s*VLC',
                'app_name': 'VLC',
                'priority': 5
            },
            'wmplayer': {
                'pattern': r'(.+?)\s*-\s*Windows Media Player',
                'app_name': 'WMP',
                'priority': 5
            },
            'mpc': {
                'pattern': r'(.+?)\s*-\s*MPC',
                'app_name': 'MPC',
                'priority': 5
            },
            'potplayer': {
                'pattern': r'(.+?)\s*-\s*PotPlayer',
                'app_name': 'PotPlayer',
                'priority': 5
            }
        }

        # Collect all potential media windows with their priorities
        potential_media = []

        for line in lines:
            line = line.strip()
            if not line or 'ProcessName' in line or '---' in line:
                continue

            # Extract process name and window title
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue

            process_name = parts[0].lower().strip()
            window_title = parts[1].strip()

            # Check if this is a known media player
            for player, config in media_patterns.items():
                if player in process_name:
                    match = re.search(config['pattern'], window_title, re.IGNORECASE)
                    if match:
                        track = match.group(1).strip()
                        # For browser media, try to extract artist from the title
                        if config['app_name'] == 'Browser':
                            # Filter out common non-media browser pages
                            skip_keywords = ['start page', 'new tab', 'settings', 'google', 'bing', 'github', 'stackoverflow', 'reddit', 'twitter', 'facebook', 'instagram', 'linkedin', 'devin', 'quota', 'troubleshooting']
                            if any(skip in window_title.lower() for skip in skip_keywords):
                                continue

                            # Look for patterns like "Song - Artist - YouTube" or "Song - Artist - Spotify"
                            if ' - ' in window_title:
                                parts = window_title.split(' - ')
                                if len(parts) >= 2:
                                    track = parts[0].strip()
                                    artist = parts[1].strip()
                                    # Remove service name from artist if present
                                    for service in ['YouTube', 'Spotify', 'Music']:
                                        artist = artist.replace(service, '').strip()
                            else:
                                # Try to parse "Song Artist" format (space separated)
                                parts = window_title.split()
                                if len(parts) >= 2:
                                    # Assume first part is track, rest is artist
                                    track = parts[0]
                                    artist = ' '.join(parts[1:])
                                    # Clean up weird characters
                                    artist = ''.join(c for c in artist if c.isprintable())
                                else:
                                    artist = config['app_name']
                        else:
                            artist = match.group(2).strip() if len(match.groups()) > 1 else config['app_name']

                        # Add to potential media with priority
                        potential_media.append({
                            'track': track,
                            'artist': artist,
                            'app': config['app_name'],
                            'priority': config['priority'],
                            'window_title': window_title
                        })

        # Sort by priority (highest first) and return the best match
        if potential_media:
            potential_media.sort(key=lambda x: x['priority'], reverse=True)
            best_match = potential_media[0]
            return best_match['track'], best_match['artist'], best_match['app']

            # Generic pattern for any window with " - " separator
            if ' - ' in window_title and len(window_title) < 100:  # Reasonable length
                parts = window_title.split(' - ')
                if len(parts) >= 2:
                    track = parts[0].strip()
                    artist = parts[1].strip()
                    # Filter out common non-media windows
                    skip_keywords = ['microsoft', 'visual studio', 'explorer', 'desktop', 'devin', 'notepad', 'code', 'terminal', 'powershell', 'command prompt', 'vivaldi', 'chrome', 'firefox', 'edge', 'brave', 'opera', 'gemini', 'google', 'bing', 'settings', 'outlook', 'inbox', 'mail', 'calendar', 'teams', 'word', 'excel', 'powerpoint', 'onedrive', 'sharepoint']
                    if not any(skip in window_title.lower() for skip in skip_keywords):
                        return track, artist, "Media"

        return None, None, None

    except Exception as e:
        print(f"Error getting media window: {e}")
        return None, None, None


def format_for_oled(text, max_length=21):
    """
    Format text for OLED display (21 chars max per line for 128x64 with default font)
    """
    if not text:
        return ""

    # Truncate if too long
    if len(text) > max_length:
        return text[:max_length-3] + "..."

    return text


def send_to_pico(ser, track, artist, app_name=""):
    """
    Send track info to Pico over serial
    Format: TRACK|song name|artist name|app name
    """
    if track and artist:
        message = f"TRACK|{track}|{artist}|{app_name}\n"
        ser.write(message.encode('utf-8'))
        print(f"Sent: {message.strip()}")
    else:
        # Send "No track playing" message
        message = "TRACK|No Track|Playing|\n"
        ser.write(message.encode('utf-8'))
        print("Sent: No track playing")


def main():
    print("Media Bridge for Pico W Controller")
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected to Pico!")

        # Clear any existing data
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        last_track = None
        last_artist = None
        last_app = None

        print("Monitoring media players... (Ctrl+C to stop)")
        print("Supports: Spotify, VLC, Windows Media Player, YouTube, and more")

        # Send initial "No Track" message
        send_to_pico(ser, "No Track", "Playing", "")

        while True:
            try:
                track, artist, app_name = get_media_from_window_title()

                # Only send if track changed
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
                        # No track playing
                        if last_track is not None:  # Only send if we previously had a track
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
        print("Make sure Pico is connected and the port is correct.")
        sys.exit(1)
    finally:
        if 'ser' in locals():
            ser.close()
            print("Serial connection closed.")


if __name__ == "__main__":
    main()

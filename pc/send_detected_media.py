"""
Detect current media and send once to Pico
"""

import serial
import subprocess
import re
import string

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

def get_media_from_window_title():
    """Get currently playing media from window titles"""
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

        media_patterns = {
            'spotify': {'pattern': r'(.+?)\s*-\s*(.+?)(?:\s*-\s*Spotify)?$', 'app_name': 'Spotify'},
            'vlc': {'pattern': r'(.+?)\s*-\s*VLC', 'app_name': 'VLC'},
            'wmplayer': {'pattern': r'(.+?)\s*-\s*Windows Media Player', 'app_name': 'WMP'},
            'chrome': {'pattern': r'(.+)', 'app_name': 'Browser'},
            'msedge': {'pattern': r'(.+)', 'app_name': 'Browser'},
            'firefox': {'pattern': r'(.+)', 'app_name': 'Browser'},
            'vivaldi': {'pattern': r'(.+)', 'app_name': 'Browser'},
            'brave': {'pattern': r'(.+)', 'app_name': 'Browser'},
            'opera': {'pattern': r'(.+)', 'app_name': 'Browser'},
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

            for player, config in media_patterns.items():
                if player in process_name:
                    match = re.search(config['pattern'], window_title, re.IGNORECASE)
                    if match:
                        track = match.group(1).strip()
                        if config['app_name'] == 'Browser':
                            skip_keywords = ['start page', 'new tab', 'settings', 'google', 'bing', 'github', 'stackoverflow', 'reddit', 'twitter', 'facebook', 'instagram', 'linkedin', 'devin', 'quota', 'troubleshooting']
                            if any(skip in window_title.lower() for skip in skip_keywords):
                                continue

                            # Handle different separators including special characters
                            allowed_chars = set(string.ascii_letters + string.digits + ' -.,\'')
                            special_chars = [c for c in window_title if c not in allowed_chars and c != ' ']

                            if special_chars:
                                # Use the first special character as separator
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
                            elif ' - ' in window_title:
                                parts = window_title.split(' - ')
                                if len(parts) >= 2:
                                    track = parts[0].strip()
                                    artist = parts[1].strip()
                                    for service in ['YouTube', 'Spotify', 'Music']:
                                        artist = artist.replace(service, '').strip()
                            else:
                                parts = window_title.split()
                                if len(parts) >= 2:
                                    track = parts[0]
                                    artist = ' '.join(parts[1:])
                                    artist = ''.join(c for c in artist if c.isprintable())
                                else:
                                    artist = config['app_name']
                        else:
                            artist = match.group(2).strip() if len(match.groups()) > 1 else config['app_name']
                        return track, artist, config['app_name']

        return None, None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

def format_for_oled(text, max_length=21):
    if not text:
        return ""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text

def main():
    print("Detecting current media...")
    track, artist, app = get_media_from_window_title()

    if track and artist:
        print(f"Found: {track} by {artist} from {app}")

        formatted_track = format_for_oled(track)
        formatted_artist = format_for_oled(artist)
        formatted_app = format_for_oled(app) if app else ""

        print(f"Sending to Pico: {formatted_track} - {formatted_artist} [{formatted_app}]")

        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            message = f"TRACK|{formatted_track}|{formatted_artist}|{formatted_app}\n"
            ser.write(message.encode('utf-8'))
            print("Sent successfully!")
            ser.close()
        except Exception as e:
            print(f"Error sending to Pico: {e}")
    else:
        print("No media detected")
        print("Make sure a media player is running with content playing")

if __name__ == "__main__":
    main()

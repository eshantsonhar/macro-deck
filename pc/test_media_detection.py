"""
Test media detection from various players
"""

import subprocess
import re

def get_media_from_window_title():
    """
    Get currently playing media from window titles across multiple players.
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
        media_patterns = {
            'spotify': {
                'pattern': r'(.+?)\s*-\s*(.+?)(?:\s*-\s*Spotify)?$',
                'app_name': 'Spotify'
            },
            'vlc': {
                'pattern': r'(.+?)\s*-\s*VLC',
                'app_name': 'VLC'
            },
            'wmplayer': {
                'pattern': r'(.+?)\s*-\s*Windows Media Player',
                'app_name': 'WMP'
            },
            'chrome': {
                'pattern': r'(.+?)\s*-\s*YouTube',
                'app_name': 'YouTube'
            },
            'msedge': {
                'pattern': r'(.+?)\s*-\s*YouTube',
                'app_name': 'YouTube'
            },
            'firefox': {
                'pattern': r'(.+?)\s*-\s*YouTube',
                'app_name': 'YouTube'
            },
            'mpc': {
                'pattern': r'(.+?)\s*-\s*MPC',
                'app_name': 'MPC'
            },
            'potplayer': {
                'pattern': r'(.+?)\s*-\s*PotPlayer',
                'app_name': 'PotPlayer'
            }
        }

        print("Detected windows:")
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

            print(f"  {process_name}: {window_title}")

            # Check if this is a known media player
            for player, config in media_patterns.items():
                if player in process_name:
                    match = re.search(config['pattern'], window_title, re.IGNORECASE)
                    if match:
                        track = match.group(1).strip()
                        artist = match.group(2).strip() if len(match.groups()) > 1 else config['app_name']
                        print(f"\n[+] Found media: {track} by {artist} from {config['app_name']}")
                        return track, artist, config['app_name']

            # Generic pattern for any window with " - " separator
            if ' - ' in window_title and len(window_title) < 100:  # Reasonable length
                parts = window_title.split(' - ')
                if len(parts) >= 2:
                    track = parts[0].strip()
                    artist = parts[1].strip()
                    # Filter out common non-media windows
                    skip_keywords = ['microsoft', 'visual studio', 'explorer', 'desktop', 'devin', 'notepad', 'code', 'terminal', 'powershell', 'command prompt', 'vivaldi', 'chrome', 'firefox', 'edge', 'brave', 'opera', 'gemini', 'google', 'bing', 'settings']
                    if not any(skip in window_title.lower() for skip in skip_keywords):
                        print(f"\n[+] Found generic media: {track} by {artist}")
                        return track, artist, "Media"

        print("\n[-] No media detected")
        return None, None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

if __name__ == "__main__":
    print("Testing media detection...")
    print("Make sure a media player is running with content playing\n")

    track, artist, app = get_media_from_window_title()

    if track and artist:
        print(f"\nFinal result: {track} by {artist} from {app}")
    else:
        print("\nNo media detected. Try opening Spotify, VLC, or YouTube with content playing.")

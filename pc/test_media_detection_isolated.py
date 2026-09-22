"""
Isolated media detection test - does NOT open COM4
Tests get_media_from_window_title() function directly
"""

import subprocess
import re

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
                'pattern': r'(.+)',
                'app_name': 'Browser',
                'priority': 10
            },
            'chrome': {
                'pattern': r'(.+)',
                'app_name': 'Browser',
                'priority': 10
            },
            'msedge': {
                'pattern': r'(.+)',
                'app_name': 'Browser',
                'priority': 10
            },
            'firefox': {
                'pattern': r'(.+)',
                'app_name': 'Browser',
                'priority': 10
            },
            'brave': {
                'pattern': r'(.+)',
                'app_name': 'Browser',
                'priority': 10
            },
            'opera': {
                'pattern': r'(.+)',
                'app_name': 'Browser',
                'priority': 10
            },
            'spotify': {
                'pattern': r'(.+?)\s*-\s*(.+?)(?:\s*-\s*Spotify)?$',
                'app_name': 'Spotify',
                'priority': 5
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


print("=== Isolated Media Detection Test ===")
print()

# First, inspect what Vivaldi windows are actually visible
print("Step 1: Inspecting Vivaldi window titles...")
ps_command = """
Get-Process | Where-Object {$_.MainWindowTitle -ne "" -and $_.ProcessName -like "*vivaldi*"} |
Select-Object ProcessName, MainWindowTitle
"""
result = subprocess.run(
    ["powershell", "-Command", ps_command],
    capture_output=True,
    text=True,
    timeout=5
)
print("Vivaldi windows found:")
print(result.stdout if result.stdout else "None")
print()

# Now test the actual detection function
print("Step 2: Testing get_media_from_window_title()...")
track, artist, app_name = get_media_from_window_title()
print(f"Detection result:")
print(f"  Track: {track}")
print(f"  Artist: {artist}")
print(f"  App: {app_name}")
print()

# If detection failed, show all window titles for debugging
if not track:
    print("Step 3: Showing all window titles for debugging...")
    ps_command_all = """
    Get-Process | Where-Object {$_.MainWindowTitle -ne ""} |
    Select-Object ProcessName, MainWindowTitle
    """
    result_all = subprocess.run(
        ["powershell", "-Command", ps_command_all],
        capture_output=True,
        text=True,
        timeout=5
    )
    lines = result_all.stdout.strip().split('\n')
    print("All window titles (filtered for relevant apps):")
    for line in lines:
        line = line.strip()
        if not line or 'ProcessName' in line or '---' in line:
            continue
        if any(app in line.lower() for app in ['vivaldi', 'chrome', 'edge', 'firefox', 'spotify', 'vlc', 'youtube']):
            print(f"  {line}")

print()
print("=== Test Complete ===")

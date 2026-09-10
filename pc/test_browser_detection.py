"""
Test browser-focused media detection
"""

import subprocess
import re
import string

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

        print("Detected browser windows:")

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
                    print(f"  {display_name}: {window_title}")

                    # Filter out non-media pages
                    skip_keywords = ['start page', 'new tab', 'settings', 'google.com', 'bing.com', 'github.com', 'stackoverflow.com', 'reddit.com', 'twitter.com', 'facebook.com', 'instagram.com', 'linkedin.com', 'devin', 'quota', 'troubleshooting']
                    if any(skip in window_title.lower() for skip in skip_keywords):
                        print(f"    -> Skipped (non-media page)")
                        continue

                    # Try to extract track/artist from title
                    # Handle different separators: " • " (Vivaldi), " - " (others), etc.
                    print(f"    Parsing: '{window_title}'")
                    print(f"    Character codes: {[hex(ord(c)) for c in window_title[:20]]}")

                    # Try to find any special separator character
                    # Look for characters that are not letters, numbers, or common punctuation
                    import string
                    allowed_chars = set(string.ascii_letters + string.digits + ' -.,\'')
                    special_chars = [c for c in window_title if c not in allowed_chars and c != ' ']
                    print(f"    Special characters found: {special_chars}")

                    if special_chars:
                        # Use the first special character as separator
                        sep = special_chars[0]
                        print(f"    Using separator: '{sep}' (code: {hex(ord(sep))})")
                        parts = window_title.split(sep)
                        print(f"    Split: {parts}")
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
                            # Remove trailing dash and spaces
                            artist = artist.rstrip('-').strip()

                            print(f"    Final: track='{track}', artist='{artist}'")
                            print(f"\n[+] Found media: {track} by {artist} from {display_name}")
                            return track, artist, display_name
                    elif ' - ' in window_title:
                        title_parts = window_title.split(' - ')
                        if len(title_parts) >= 2:
                            track = title_parts[0].strip()
                            artist = title_parts[1].strip()
                            # Remove service names
                            for service in ['YouTube', 'Spotify', 'Music']:
                                artist = artist.replace(service, '').strip()
                            print(f"\n[+] Found media: {track} by {artist} from {display_name}")
                            return track, artist, display_name
                    else:
                        # Try space-separated format
                        parts = window_title.split()
                        if len(parts) >= 2:
                            track = parts[0]
                            artist = ' '.join(parts[1:])
                            artist = ''.join(c for c in artist if c.isprintable())
                            print(f"\n[+] Found media: {track} by {artist} from {display_name}")
                            return track, artist, display_name

        print("\n[-] No media found in browser tabs")
        return None, None, None

    except Exception as e:
        print(f"Error: {e}")
        return None, None, None

if __name__ == "__main__":
    print("Testing browser-focused media detection...")
    print("Make sure Spotify is playing in a browser tab\n")

    track, artist, app = get_media_from_browsers()

    if track and artist:
        print(f"\nFinal result: {track} by {artist} from {app}")
    else:
        print("\nNo media detected in browser tabs")

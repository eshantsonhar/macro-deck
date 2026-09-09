"""
Test Spotify window detection
"""

import subprocess
import time

def get_spotify_track_window_title():
    """
    Get currently playing track from Spotify window title.
    """
    try:
        # Use PowerShell to get window titles
        ps_command = """
        Get-Process | Where-Object {$_.MainWindowTitle -like "*Spotify*"} | 
        Select-Object -ExpandProperty MainWindowTitle
        """
        
        result = subprocess.run(
            ["powershell", "-Command", ps_command],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        window_title = result.stdout.strip()
        
        print(f"Raw window title: '{window_title}'")
        print(f"Stderr: {result.stderr}")
        
        if window_title and "Spotify" in window_title:
            # Extract track info from window title
            title = window_title.replace(" - Spotify", "").replace("Spotify", "")
            
            if " - " in title:
                parts = title.split(" - ")
                if len(parts) >= 2:
                    track = parts[0].strip()
                    artist = parts[1].strip()
                    return track, artist
            
            return title, "Unknown"
        
        return None, None
        
    except Exception as e:
        print(f"Error getting Spotify window: {e}")
        return None, None

if __name__ == "__main__":
    print("Testing Spotify detection...")
    track, artist = get_spotify_track_window_title()
    
    if track and artist:
        print(f"Found track: {track} by {artist}")
    else:
        print("No Spotify track found")
        print("Make sure Spotify is running and playing music")

"""
Test media bridge with Pico - sends detected media to OLED
"""

import serial
import time
import subprocess
import re

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
                            
                            if ' - ' in window_title:
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
    print("Media Bridge Test")
    print(f"Connecting to {SERIAL_PORT}...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected to Pico!")
        
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        last_track = None
        last_artist = None
        last_app = None
        
        print("Monitoring media... (Ctrl+C to stop)")
        print("Current media:")
        
        while True:
            try:
                track, artist, app = get_media_from_window_title()
                
                if track != last_track or artist != last_artist or app != last_app:
                    if track and artist:
                        formatted_track = format_for_oled(track)
                        formatted_artist = format_for_oled(artist)
                        formatted_app = format_for_oled(app) if app else ""
                        message = f"TRACK|{formatted_track}|{formatted_artist}|{formatted_app}\n"
                        ser.write(message.encode('utf-8'))
                        print(f"Sent: {formatted_track} - {formatted_artist} [{formatted_app}]")
                        last_track = track
                        last_artist = artist
                        last_app = app
                    else:
                        if last_track is not None:
                            message = "TRACK|No Track|Playing|\n"
                            ser.write(message.encode('utf-8'))
                            print("Sent: No Track - Playing")
                            last_track = None
                            last_artist = None
                            last_app = None
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(2)
                
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        if 'ser' in locals():
            ser.close()
            print("Connection closed")

if __name__ == "__main__":
    main()

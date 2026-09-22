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
import asyncio
from volume_controller import volume_up, volume_down, volume_mute
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager

SERIAL_PORT = "COM4"
BAUD_RATE = 115200
POLL_INTERVAL = 2
VOLUME_STEP = 2


async def get_media_from_smtc_async():
    """
    Get currently playing media from Windows Global System Media Transport Controls.
    This works for background tabs in browsers like Vivaldi.
    """
    try:
        manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
        sessions = manager.get_sessions()

        # Prefer Vivaldi session
        vivaldi_aumid = "Vivaldi.Z5DLQOUXBXTNP4UT4UK7IYQSGM"
        vivaldi_session = None

        for session in sessions:
            if session.source_app_user_model_id == vivaldi_aumid:
                vivaldi_session = session
                break

        # If Vivaldi found, use it; otherwise use current session
        target_session = vivaldi_session if vivaldi_session else manager.get_current_session()

        if target_session:
            # Check playback status
            playback_info = target_session.get_playback_info()
            if playback_info.playback_status == 4:  # Playing
                # Get media properties
                props = await target_session.try_get_media_properties_async()
                if props and props.title and props.artist:
                    return props.title, props.artist, "Vivaldi"

        return None, None, None
    except Exception as e:
        print(f"[ERROR] SMTC async: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        return None, None, None


def get_media_from_smtc():
    """
    Synchronous wrapper for SMTC media detection.
    """
    try:
        return asyncio.run(get_media_from_smtc_async())
    except Exception as e:
        print(f"[ERROR] SMTC wrapper: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        return None, None, None


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
        volume_up()
    elif line == "VOLUME|DOWN":
        volume_down()
    elif line == "VOLUME|MUTE":
        volume_mute()
    elif line.startswith("Encoder CW"):
        volume_up()
    elif line.startswith("Encoder CCW"):
        volume_down()
    elif line == "Encoder switch pressed":
        volume_mute()


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
            print(f"[ERROR] Volume listener: {type(e).__name__}: {e}", flush=True)
            traceback.print_exc()
            break


def main():
    print("[MAIN] entering main", flush=True)
    print("Combined Bridge for Pico W Controller")
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")

    try:
        print("[MAIN] before Serial()", flush=True)
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1, write_timeout=2)
        print("[MAIN] after Serial()", flush=True)
        print("Connected to Pico!")

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        print("[MAIN] before starting volume listener", flush=True)
        # Start volume listener thread
        volume_thread = threading.Thread(target=volume_listener, args=(ser,), daemon=True)
        volume_thread.start()
        print("[MAIN] after starting volume listener", flush=True)

        last_track = None
        last_artist = None
        last_app = None

        print("Monitoring media and volume... (Ctrl+C to stop)")
        print("Supports: Spotify, VLC, Windows Media Player, YouTube, and more")
        print("Encoder: Volume control | Press: Mute toggle")

        print("[MAIN] before initial TRACK write", flush=True)
        # Send initial "No Track" message
        ser.write(b"TRACK|No Track|Playing|\n")
        print("[MAIN] after initial TRACK write", flush=True)

        print("[MAIN] entering main loop", flush=True)
        while True:
            try:
                print("[MAIN] before get_media_from_smtc()", flush=True)
                track, artist, app_name = get_media_from_smtc()
                print(f"[MAIN] after get_media_from_smtc()", flush=True)
                print(f"[MAIN] media result: track={repr(track)} artist={repr(artist)} app={repr(app_name)}", flush=True)

                print("[MAIN] before media comparison", flush=True)
                if track != last_track or artist != last_artist or app_name != last_app:
                    print("[MAIN] after media comparison (changed)", flush=True)
                    if track and artist:
                        formatted_track = format_for_oled(track)
                        formatted_artist = format_for_oled(artist)
                        formatted_app = format_for_oled(app_name) if app_name else ""
                        message = f"TRACK|{formatted_track}|{formatted_artist}|{formatted_app}\n"

                        print("[MAIN] before TRACK write", flush=True)
                        print(f"[MAIN] TRACK message: {repr(message)}", flush=True)
                        ser.write(message.encode('utf-8'))
                        print("[MAIN] after TRACK write", flush=True)
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
                else:
                    print("[MAIN] after media comparison (unchanged)", flush=True)

                print("[MAIN] before sleep", flush=True)
                time.sleep(POLL_INTERVAL)
                print("[MAIN] after sleep", flush=True)

            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"[ERROR] Media loop: {type(e).__name__}: {e}", flush=True)
                traceback.print_exc()
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

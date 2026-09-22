"""
Diagnostic version of combined_bridge with print statements
Temporary diagnostic only - NOT for production
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
        print(f"Error getting media from SMTC: {e}")
        return None, None, None


def get_media_from_smtc():
    """
    Synchronous wrapper for SMTC media detection.
    """
    try:
        return asyncio.run(get_media_from_smtc_async())
    except Exception as e:
        print(f"Error in SMTC async wrapper: {e}")
        return None, None, None


def format_for_oled(text, max_length=21):
    if not text:
        return ""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text


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
                    print(f"[VOLUME] Received: {repr(line)}")
                    handle_volume_command(line)
            time.sleep(0.05)
        except Exception as e:
            print(f"Volume listener error: {e}")
            break


def main():
    print("Combined Bridge for Pico W Controller (DIAGNOSTIC)")
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
        print("Supports: Spotify, VLC, Windows Media Player, YouTube, and more")
        print("Encoder: Volume control | Press: Mute toggle")

        # Send initial "No Track" message
        ser.write(b"TRACK|No Track|Playing|\n")
        print("[SERIAL] Sent: TRACK|No Track|Playing|")

        iteration = 0
        while True:
            iteration += 1
            try:
                print(f"\n=== Iteration {iteration} ===")
                track, artist, app_name = get_media_from_smtc()
                print(f"[SMTC] Detected: track={repr(track)}, artist={repr(artist)}, app={repr(app_name)}")
                print(f"[CACHE] Previous: track={repr(last_track)}, artist={repr(last_artist)}, app={repr(last_app)}")

                if track != last_track or artist != last_artist or app_name != last_app:
                    print(f"[DECISION] Media changed - will send")
                    
                    if track and artist:
                        formatted_track = format_for_oled(track)
                        formatted_artist = format_for_oled(artist)
                        formatted_app = format_for_oled(app_name) if app_name else ""
                        message = f"TRACK|{formatted_track}|{formatted_artist}|{formatted_app}\n"
                        
                        print(f"[SERIAL] Sending: {repr(message)}")
                        ser.write(message.encode('utf-8'))
                        print(f"[SERIAL] Sent successfully")
                        print(f"[MEDIA] Display: {formatted_track} - {formatted_artist} [{formatted_app}]")
                        
                        last_track = track
                        last_artist = artist
                        last_app = app_name
                    else:
                        print(f"[DECISION] No valid track/artist - sending No Track")
                        if last_track is not None:
                            ser.write(b"TRACK|No Track|Playing|\n")
                            print(f"[SERIAL] Sent: TRACK|No Track|Playing|")
                            last_track = None
                            last_artist = None
                            last_app = None
                else:
                    print(f"[DECISION] Media unchanged - no send")

                time.sleep(POLL_INTERVAL)

            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error in media loop: {e}")
                import traceback
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

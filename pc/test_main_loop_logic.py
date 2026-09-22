"""
Trace the main-loop decision logic WITHOUT COM4
Reproduce the exact logic from combined_bridge.py main loop
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from combined_bridge import get_media_from_smtc, format_for_oled

print("=== Tracing Main-Loop Decision Logic ===")
print()

# Simulate the main loop state
last_track = None
last_artist = None
last_app = None

# Get current media
track, artist, app_name = get_media_from_smtc()

print(f"Current detected media:")
print(f"  track: {repr(track)}")
print(f"  artist: {repr(artist)}")
print(f"  app_name: {repr(app_name)}")
print()

print(f"Previous cached media:")
print(f"  last_track: {repr(last_track)}")
print(f"  last_artist: {repr(last_artist)}")
print(f"  last_app: {repr(last_app)}")
print()

# Main loop decision logic
print(f"Decision check: track != last_track or artist != last_artist or app_name != last_app")
print(f"  {repr(track)} != {repr(last_track)}: {track != last_track}")
print(f"  {repr(artist)} != {repr(last_artist)}: {artist != last_artist}")
print(f"  {repr(app_name)} != {repr(last_app)}: {app_name != last_app}")
print(f"  Overall: {track != last_track or artist != last_artist or app_name != last_app}")
print()

if track != last_track or artist != last_artist or app_name != last_app:
    print("Decision: SEND TRACK (media changed)")
    print()
    
    if track and artist:
        print("Validation: track and artist are truthy - will format and send")
        print()
        
        formatted_track = format_for_oled(track)
        formatted_artist = format_for_oled(artist)
        formatted_app = format_for_oled(app_name) if app_name else ""
        message = f"TRACK|{formatted_track}|{formatted_artist}|{formatted_app}\n"
        
        print(f"Formatted values:")
        print(f"  formatted_track: {repr(formatted_track)}")
        print(f"  formatted_artist: {repr(formatted_artist)}")
        print(f"  formatted_app: {repr(formatted_app)}")
        print()
        
        print(f"EXACT TRACK string that would be sent:")
        print(f"  {repr(message)}")
        print()
        
        print(f"Encoded bytes:")
        print(f"  {message.encode('utf-8')}")
    else:
        print("Validation: track or artist is falsy - would send 'No Track'")
        if not track:
            print(f"  Reason: track is {repr(track)}")
        if not artist:
            print(f"  Reason: artist is {repr(artist)}")
else:
    print("Decision: DO NOT SEND (media unchanged)")

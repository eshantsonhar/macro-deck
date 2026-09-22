"""
Test the exact main loop logic with print statements
This will show if SMTC is working in the loop context
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from combined_bridge import get_media_from_smtc, format_for_oled

print("=== Testing Main Loop Logic with SMTC ===")
print()

# Simulate main loop state
last_track = None
last_artist = None
last_app = None

print("Starting simulated main loop (5 iterations)...")
print()

for i in range(5):
    print(f"--- Iteration {i+1} ---")
    
    # This is the EXACT call from the main loop
    print("Calling get_media_from_smtc()...")
    track, artist, app_name = get_media_from_smtc()
    print(f"Result: track={repr(track)}, artist={repr(artist)}, app={repr(app_name)}")
    
    # This is the EXACT decision logic
    if track != last_track or artist != last_artist or app_name != last_app:
        print("Decision: Media changed")
        
        if track and artist:
            formatted_track = format_for_oled(track)
            formatted_artist = format_for_oled(artist)
            formatted_app = format_for_oled(app_name) if app_name else ""
            message = f"TRACK|{formatted_track}|{formatted_artist}|{formatted_app}\n"
            
            print(f"Would send: {repr(message)}")
            
            # Update cache
            last_track = track
            last_artist = artist
            last_app = app_name
        else:
            print("Would send: TRACK|No Track|Playing|")
            last_track = None
            last_artist = None
            last_app = None
    else:
        print("Decision: Media unchanged - no send")
    
    print()
    time.sleep(2)  # Actual POLL_INTERVAL

print("=== Test Complete ===")

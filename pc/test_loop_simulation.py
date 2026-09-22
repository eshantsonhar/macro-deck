"""
Test to simulate what happens when the main loop runs
This will help identify if there's an issue with the async/asyncio.run blocking
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from combined_bridge import get_media_from_smtc, format_for_oled

print("=== Simulating Main Loop Behavior ===")
print()

# Simulate the exact main loop state
last_track = None
last_artist = None
last_app = None

print("Starting simulated main loop (3 iterations)...")
print()

for i in range(3):
    print(f"Iteration {i+1}:")
    
    # This is the exact call from the main loop
    track, artist, app_name = get_media_from_smtc()
    
    print(f"  Detected: track={repr(track)}, artist={repr(artist)}, app={repr(app_name)}")
    print(f"  Cached: last_track={repr(last_track)}, last_artist={repr(last_artist)}, last_app={repr(last_app)}")
    
    # This is the exact decision logic
    if track != last_track or artist != last_artist or app_name != last_app:
        print(f"  Decision: Media changed")
        
        if track and artist:
            formatted_track = format_for_oled(track)
            formatted_artist = format_for_oled(artist)
            formatted_app = format_for_oled(app_name) if app_name else ""
            message = f"TRACK|{formatted_track}|{formatted_artist}|{formatted_app}\n"
            
            print(f"  Would send: {repr(message)}")
            
            # Update cache
            last_track = track
            last_artist = artist
            last_app = app_name
        else:
            print(f"  Would send: TRACK|No Track|Playing|\\n")
            last_track = None
            last_artist = None
            last_app = None
    else:
        print(f"  Decision: Media unchanged - no send")
    
    print()
    
    # Simulate the sleep
    time.sleep(0.1)  # Shorter for testing

print("=== Simulation Complete ===")

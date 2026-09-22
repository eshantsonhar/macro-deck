"""
Test the actual get_media_from_smtc() from combined_bridge.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from combined_bridge import get_media_from_smtc

print("=== Testing Actual combined_bridge.get_media_from_smtc() ===")
print()

track, artist, app_name = get_media_from_smtc()

print(f"Result:")
print(f"  track: {repr(track)}")
print(f"  artist: {repr(artist)}")
print(f"  app_name: {repr(app_name)}")
print()

print(f"Type check:")
print(f"  track type: {type(track)}")
print(f"  artist type: {type(artist)}")
print(f"  app_name type: {type(app_name)}")
print()

if track and artist:
    print("Would send TRACK message (both track and artist are truthy)")
else:
    print("Would NOT send TRACK message (missing track or artist)")
    if not track:
        print(f"  Reason: track is {repr(track)}")
    if not artist:
        print(f"  Reason: artist is {repr(artist)}")

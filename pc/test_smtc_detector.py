"""
Isolated SMTC detector test - does NOT open COM4
Tests the new get_media_from_smtc() function
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from combined_bridge import get_media_from_smtc

print("=== Isolated SMTC Detector Test ===")
print()

track, artist, app_name = get_media_from_smtc()

print(f"Detection result:")
print(f"  Track: {track}")
print(f"  Artist: {artist}")
print(f"  App: {app_name}")
print()

if track and artist:
    print("SUCCESS: SMTC detector returned valid media metadata")
else:
    print("INFO: No media detected or playback stopped")

print()
print("=== Test Complete ===")

"""
Single volume_mute() test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from volume_controller import volume_mute

print("=== Single volume_mute() Test ===")
print()

print("Calling volume_mute() exactly once...")
try:
    volume_mute()
    print("volume_mute() completed without exception")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print()
print("=== Results ===")
print("Check: Windows mute state should have toggled")

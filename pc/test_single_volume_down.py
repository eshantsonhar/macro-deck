"""
Single volume_down() test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from volume_controller import volume_down

print("=== Single volume_down() Test ===")
print()

print("Calling volume_down() exactly once...")
try:
    volume_down()
    print("volume_down() completed without exception")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

print()
print("=== Results ===")
print("Check: Windows volume should have decreased by one step")

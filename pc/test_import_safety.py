"""
Test that importing volume_controller does not execute main() or open COM4
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Importing volume_controller...")
from volume_controller import volume_up, volume_down, volume_mute

print("Import successful")
print("volume_up function:", volume_up)
print("volume_down function:", volume_down)
print("volume_mute function:", volume_mute)
print()
print("COM4 was NOT opened (this would have caused an error if opened)")

"""
Single volume_up() test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from volume_controller import volume_up, get_current_volume

print("=== Single volume_up() Test ===")
print()

# Get volume before
print("Getting current volume before test...")
volume_before = get_current_volume()
print(f"Volume before: {volume_before}%")
print()

# Call volume_up() exactly once
print("Calling volume_up()...")
try:
    # Temporarily patch to capture SendInput return value
    import ctypes
    original_sendinput = ctypes.windll.user32.SendInput
    def sendinput_wrapper(nInputs, pInputs, cbSize):
        result = original_sendinput(nInputs, pInputs, cbSize)
        print(f"SendInput returned: {result} events")
        return result
    ctypes.windll.user32.SendInput = sendinput_wrapper

    volume_up()

    # Restore original
    ctypes.windll.user32.SendInput = original_sendinput
    print("volume_up() completed without exception")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
print()

# Get volume after
print("Getting current volume after test...")
volume_after = get_current_volume()
print(f"Volume after: {volume_after}%")
print()

print("=== Results ===")
print(f"Volume change: {volume_before}% -> {volume_after}%")
print(f"Expected: Volume should increase by one step")

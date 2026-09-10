"""
Simple Windows volume control test - no user input required
"""

import ctypes
import time

print("=== Windows Volume Control Test ===")
print("Testing keybd_event method for volume control")
print()

# Test 1: Volume UP
print("Test 1: Sending Volume UP event...")
try:
    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # VK_VOLUME_UP
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)  # KEYEVENTF_KEYUP
    print("[OK] Volume UP event sent")
    print("  (Your system volume should have increased)")
except Exception as e:
    print(f"[ERROR] Volume UP failed: {e}")

time.sleep(1)

# Test 2: Volume DOWN
print("\nTest 2: Sending Volume DOWN event...")
try:
    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # VK_VOLUME_DOWN
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)  # KEYEVENTF_KEYUP
    print("[OK] Volume DOWN event sent")
    print("  (Your system volume should have decreased)")
except Exception as e:
    print(f"[ERROR] Volume DOWN failed: {e}")

time.sleep(1)

# Test 3: Mute toggle
print("\nTest 3: Sending Mute toggle event...")
try:
    ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # VK_VOLUME_MUTE
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)  # KEYEVENTF_KEYUP
    print("[OK] Mute toggle event sent")
    print("  (Your system mute should have toggled)")
except Exception as e:
    print(f"[ERROR] Mute toggle failed: {e}")

print("\n=== Test Complete ===")
print("Check if your Windows volume actually changed")
print("If it did, the keybd_event method is working correctly")

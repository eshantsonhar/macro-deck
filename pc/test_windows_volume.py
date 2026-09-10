"""
Test Windows volume control using keybd_event method
This is TEST 3 from the debugging order
"""

import ctypes
import time

def test_volume_up():
    """Test single volume up"""
    print("Test 1: Volume UP")
    print("Current system volume should increase by ~2%")
    print("Press any key to continue...")
    input()
    
    try:
        ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # VK_VOLUME_UP
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)  # KEYEVENTF_KEYUP
        print("Volume UP key event sent")
        print("Did your system volume increase? (y/n)")
        return input().strip().lower() == 'y'
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_volume_down():
    """Test single volume down"""
    print("\nTest 2: Volume DOWN")
    print("Current system volume should decrease by ~2%")
    print("Press any key to continue...")
    input()
    
    try:
        ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # VK_VOLUME_DOWN
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)  # KEYEVENTF_KEYUP
        print("Volume DOWN key event sent")
        print("Did your system volume decrease? (y/n)")
        return input().strip().lower() == 'y'
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_mute():
    """Test mute toggle"""
    print("\nTest 3: Mute toggle")
    print("System mute should toggle")
    print("Press any key to continue...")
    input()
    
    try:
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # VK_VOLUME_MUTE
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)  # KEYEVENTF_KEYUP
        print("Mute key event sent")
        print("Did your system mute toggle? (y/n)")
        return input().strip().lower() == 'y'
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=== Windows Volume Control Test ===")
    print("This test verifies the keybd_event method actually changes system volume")
    print()
    
    results = []
    
    results.append(("Volume UP", test_volume_up()))
    results.append(("Volume DOWN", test_volume_down()))
    results.append(("Mute Toggle", test_mute()))
    
    print("\n=== Test Results ===")
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name}: {status}")
    
    if all(r[1] for r in results):
        print("\n✓ All tests passed - Windows volume control is working")
    else:
        print("\n✗ Some tests failed - Windows volume control needs investigation")

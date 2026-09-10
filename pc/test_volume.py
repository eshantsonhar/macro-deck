"""
Test volume control commands using keybd_event method
"""

import ctypes
import time

def test_volume_up():
    """Test volume up"""
    try:
        print("Testing volume up...")
        for _ in range(2):
            ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)  # VK_VOLUME_UP
            time.sleep(0.03)
            ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)  # KEYEVENTF_KEYUP
            time.sleep(0.03)
        print("Volume up sent (should increase by ~4%)")
    except Exception as e:
        print(f"Error: {e}")

def test_volume_down():
    """Test volume down"""
    try:
        print("Testing volume down...")
        for _ in range(2):
            ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)  # VK_VOLUME_DOWN
            time.sleep(0.03)
            ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)  # KEYEVENTF_KEYUP
            time.sleep(0.03)
        print("Volume down sent (should decrease by ~4%)")
    except Exception as e:
        print(f"Error: {e}")

def test_mute():
    """Test mute toggle"""
    try:
        print("Testing mute toggle...")
        ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)  # VK_VOLUME_MUTE
        time.sleep(0.05)
        ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)  # KEYEVENTF_KEYUP
        time.sleep(0.05)
        print("Mute toggle sent")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing volume control with keybd_event...")
    print("1. Test volume up")
    test_volume_up()
    print()
    print("2. Test volume down")
    test_volume_down()
    print()
    print("3. Test mute toggle")
    test_mute()
    print()
    print("Check if your system volume changed!")

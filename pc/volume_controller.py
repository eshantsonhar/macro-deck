"""
Volume Controller for Pico W Controller
Receives volume commands from Pico and adjusts system volume
"""

import serial
import time
import subprocess
import sys
import ctypes
from ctypes import wintypes

# ULONG_PTR is not in wintypes, define it based on architecture
ULONG_PTR = ctypes.c_uint64 if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_uint32

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

VOLUME_STEP = 2  # Volume percentage per encoder click

# Win32 Virtual-Key Codes
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF

# Win32 SendInput structures
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.WORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("ki", KEYBDINPUT),
        ("mi", MOUSEINPUT),
        ("hi", HARDWAREINPUT),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", INPUT_UNION),
    ]

# Win32 constants
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

# Load user32
user32 = ctypes.windll.user32

# SendInput function prototype
user32.SendInput.argtypes = [ctypes.c_uint, ctypes.POINTER(INPUT), ctypes.c_int]
user32.SendInput.restype = ctypes.c_uint


def validate_structures():
    """
    Non-destructive validation of INPUT/KEYBDINPUT structures.
    Does NOT call SendInput or send any Windows input.
    Verifies structure layout and array construction.
    """
    print("=== Structure Validation ===")

    # Check sizes
    keybdinput_size = ctypes.sizeof(KEYBDINPUT)
    input_size = ctypes.sizeof(INPUT)
    print(f"KEYBDINPUT size: {keybdinput_size} bytes")
    print(f"INPUT size: {input_size} bytes")

    # Check offsets
    input_type_offset = INPUT.type.offset
    print(f"INPUT.type offset: {input_type_offset}")

    # Test array construction
    try:
        inputs = (INPUT * 2)()
        print(f"INPUT array construction: SUCCESS (2 elements)")
    except Exception as e:
        print(f"INPUT array construction: FAILED - {e}")
        return False

    # Test field access
    try:
        inputs[0].type = INPUT_KEYBOARD
        inputs[0].u.ki.wVk = VK_VOLUME_UP
        inputs[0].u.ki.dwFlags = 0
        inputs[1].type = INPUT_KEYBOARD
        inputs[1].u.ki.wVk = VK_VOLUME_UP
        inputs[1].u.ki.dwFlags = KEYEVENTF_KEYUP
        print(f"Field access: SUCCESS")
        print(f"  inputs[0].type = {inputs[0].type}")
        print(f"  inputs[0].u.ki.wVk = {inputs[0].u.ki.wVk}")
        print(f"  inputs[0].u.ki.dwFlags = {inputs[0].u.ki.dwFlags}")
    except Exception as e:
        print(f"Field access: FAILED - {e}")
        return False

    # Expected sizes for 64-bit Windows
    # KEYBDINPUT: 2 + 2 + 4 + 4 + 8 = 20 bytes (may be padded to 24)
    # INPUT: 4 (type) + max(KEYBDINPUT, MOUSEINPUT, HARDWAREINPUT) = 4 + 24 = 28 (may be padded)
    # Actual sizes may differ due to compiler padding
    expected_keybdinput = 24  # Allow for padding
    expected_input = 72  # Allow for alignment

    if keybdinput_size != expected_keybdinput:
        print(f"WARNING: KEYBDINPUT size mismatch")
        print(f"  Expected: {expected_keybdinput}, Got: {keybdinput_size}")

    if input_size != expected_input:
        print(f"WARNING: INPUT size mismatch")
        print(f"  Expected: {expected_input}, Got: {input_size}")

    print("=== Validation Complete ===")
    return True


def volume_up():
    """
    Send Windows volume up key press using SendInput
    Uses VK_VOLUME_UP (0xAF)
    """
    inputs = (INPUT * 2)()

    # Key down
    inputs[0].type = INPUT_KEYBOARD
    inputs[0].u.ki.wVk = VK_VOLUME_UP
    inputs[0].u.ki.dwFlags = 0

    # Key up
    inputs[1].type = INPUT_KEYBOARD
    inputs[1].u.ki.wVk = VK_VOLUME_UP
    inputs[1].u.ki.dwFlags = KEYEVENTF_KEYUP

    events_sent = user32.SendInput(2, inputs, ctypes.sizeof(INPUT))
    if events_sent != 2:
        raise RuntimeError(f"SendInput failed: expected 2 events, got {events_sent}")


def volume_down():
    """
    Send Windows volume down key press using SendInput
    Uses VK_VOLUME_DOWN (0xAE)
    """
    inputs = (INPUT * 2)()

    # Key down
    inputs[0].type = INPUT_KEYBOARD
    inputs[0].u.ki.wVk = VK_VOLUME_DOWN
    inputs[0].u.ki.dwFlags = 0

    # Key up
    inputs[1].type = INPUT_KEYBOARD
    inputs[1].u.ki.wVk = VK_VOLUME_DOWN
    inputs[1].u.ki.dwFlags = KEYEVENTF_KEYUP

    events_sent = user32.SendInput(2, inputs, ctypes.sizeof(INPUT))
    if events_sent != 2:
        raise RuntimeError(f"SendInput failed: expected 2 events, got {events_sent}")


def volume_mute():
    """
    Send Windows volume mute key press using SendInput
    Uses VK_VOLUME_MUTE (0xAD)
    """
    inputs = (INPUT * 2)()

    # Key down
    inputs[0].type = INPUT_KEYBOARD
    inputs[0].u.ki.wVk = VK_VOLUME_MUTE
    inputs[0].u.ki.dwFlags = 0

    # Key up
    inputs[1].type = INPUT_KEYBOARD
    inputs[1].u.ki.wVk = VK_VOLUME_MUTE
    inputs[1].u.ki.dwFlags = KEYEVENTF_KEYUP

    events_sent = user32.SendInput(2, inputs, ctypes.sizeof(INPUT))
    if events_sent != 2:
        raise RuntimeError(f"SendInput failed: expected 2 events, got {events_sent}")


def get_current_volume():
    """Get current system volume (0-100)"""
    try:
        result = subprocess.run(
            ["powershell", "-Command",
             "(Get-AudioDevice -RenderingControl).Volume"],
            capture_output=True,
            text=True,
            timeout=5
        )
        volume = int(result.stdout.strip())
        return volume
    except:
        return 50  # Default to 50% if we can't get volume


def set_volume(volume):
    """Set system volume (0-100)"""
    volume = max(0, min(100, volume))
    try:
        subprocess.run(
            ["powershell", "-Command",
             f"Set-AudioDevice -RenderingVolume {volume}"],
            capture_output=True,
            timeout=5
        )
        return True
    except:
        return False


def toggle_mute():
    """Toggle system mute"""
    try:
        subprocess.run(
            ["powershell", "-Command",
             "$m = Get-AudioDevice -RenderingMute; Set-AudioDevice -RenderingMute (-not $m)"],
            capture_output=True,
            timeout=5
        )
        return True
    except:
        return False


def change_volume(direction):
    """Change volume up or down"""
    current = get_current_volume()
    if direction == "UP":
        new_volume = current + VOLUME_STEP
    else:
        new_volume = current - VOLUME_STEP

    new_volume = max(0, min(100, new_volume))
    if set_volume(new_volume):
        print(f"Volume: {new_volume}%")
        return new_volume
    return current


def handle_volume_command(command):
    """Handle volume command from Pico"""
    if command == "VOLUME|UP":
        change_volume("UP")
    elif command == "VOLUME|DOWN":
        change_volume("DOWN")
    elif command == "VOLUME|MUTE":
        toggle_mute()
        print("Mute toggled")


def main():
    print("Volume Controller for Pico W Controller")
    print(f"Connecting to {SERIAL_PORT} at {BAUD_RATE} baud...")

    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connected to Pico!")

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        print("Monitoring volume commands... (Ctrl+C to stop)")
        print("Use rotary encoder to adjust volume, press to mute/unmute")

        while True:
            try:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        print(f"Received: {line}")
                        handle_volume_command(line)

                time.sleep(0.01)

            except KeyboardInterrupt:
                print("\nStopping...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(0.1)

    except serial.SerialException as e:
        print(f"Failed to connect to serial port: {e}")
        sys.exit(1)
    finally:
        if 'ser' in locals():
            ser.close()
            print("Serial connection closed.")


if __name__ == "__main__":
    main()

"""
Test script for volume functions
Tests volume_up(), volume_down(), volume_mute() without connecting to Pico
"""

import sys
import os

# Add parent directory to path to import volume_controller
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from volume_controller import volume_up, volume_down, volume_mute, validate_structures

print("Volume Functions Test")
print("=" * 40)
print()

# First run structural validation (non-destructive)
print("Running structural validation...")
validate_structures()
print()

print("Available commands:")
print("  v - Run validation again")
print("  1 - volume_up() [CHANGES VOLUME]")
print("  2 - volume_down() [CHANGES VOLUME]")
print("  3 - volume_mute() [CHANGES VOLUME]")
print("  q - quit")
print()
print("WARNING: Commands 1, 2, 3 will change your Windows volume!")
print("         Do not run if you cannot tolerate volume changes.")
print()

while True:
    try:
        cmd = input("Enter command (v/1/2/3/q): ").strip().lower()

        if cmd == 'v':
            print("Running structural validation...")
            validate_structures()
        elif cmd == '1':
            print("Calling volume_up()...")
            volume_up()
            print("Volume up sent successfully")
        elif cmd == '2':
            print("Calling volume_down()...")
            volume_down()
            print("Volume down sent successfully")
        elif cmd == '3':
            print("Calling volume_mute()...")
            volume_mute()
            print("Volume mute sent successfully")
        elif cmd == 'q':
            print("Exiting...")
            break
        else:
            print("Invalid command. Use v, 1, 2, 3, or q")

        print()

    except KeyboardInterrupt:
        print("\nExiting...")
        break
    except Exception as e:
        print(f"Error: {e}")
        print()

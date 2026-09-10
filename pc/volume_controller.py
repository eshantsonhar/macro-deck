"""
Volume Controller for Pico W Controller
Receives volume commands from Pico and adjusts system volume
"""

import serial
import time
import subprocess
import sys

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

VOLUME_STEP = 2  # Volume percentage per encoder click


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

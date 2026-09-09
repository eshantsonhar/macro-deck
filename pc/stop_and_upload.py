"""
Stop Pico program and upload new main.py
"""

import serial
import time
import subprocess
import sys

SERIAL_PORT = "COM4"
BAUD_RATE = 115200

def stop_pico_program():
    """Stop any running program on Pico"""
    print("Stopping Pico program...")
    
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        
        # Send multiple Ctrl+C to ensure program stops
        for _ in range(5):
            ser.write(b'\x03')
            time.sleep(0.2)
        
        # Send break signal
        ser.send_break()
        time.sleep(0.5)
        
        ser.close()
        print("Program stopped")
        return True
        
    except Exception as e:
        print(f"Error stopping program: {e}")
        return False

def upload_with_mpremote():
    """Upload using mpremote after stopping"""
    print("Waiting for Pico to settle...")
    time.sleep(2)
    
    print("Uploading main.py with mpremote...")
    result = subprocess.run(
        ["py", "-m", "mpremote", "connect", SERIAL_PORT, "fs", "cp", 
         r"C:\Users\eshan\Documents\PicoW-Controller\main.py", ":main.py"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
    
    return result.returncode == 0

def reset_pico():
    """Reset Pico to run new main.py"""
    print("Resetting Pico...")
    time.sleep(1)
    
    result = subprocess.run(
        ["py", "-m", "mpremote", "connect", SERIAL_PORT, "reset"],
        capture_output=True,
        text=True,
        timeout=15
    )
    
    print("Reset result:", result.returncode == 0)
    return result.returncode == 0

def main():
    print("=== Stop and Upload ===")
    print()
    
    # Step 1: Stop program
    if not stop_pico_program():
        print("Failed to stop program, continuing anyway...")
    
    # Step 2: Upload
    if not upload_with_mpremote():
        print("Upload failed!")
        sys.exit(1)
    
    print("Upload successful!")
    
    # Step 3: Reset
    if not reset_pico():
        print("Reset failed, but upload may have succeeded")
    else:
        print("Reset successful!")
    
    print()
    print("=== Done ===")
    print("Pico should now be running the updated main.py")

if __name__ == "__main__":
    main()

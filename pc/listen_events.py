import serial
import time

print("=== Pico Event Listener ===")
print("Opening COM4...")
ser = serial.Serial('COM4', 115200, timeout=1)
print("Connected to COM4")
print("Listening for encoder events...")
print("Rotate the encoder or press the switch now")
print("Press Ctrl+C to stop")
print("")

try:
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[RX] {line}")
        time.sleep(0.01)
except KeyboardInterrupt:
    print("\nStopping...")
finally:
    ser.close()
    print("Connection closed")

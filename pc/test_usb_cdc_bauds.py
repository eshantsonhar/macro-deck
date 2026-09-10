import serial
import time

# Test various common USB CDC baud rates
baud_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]

print("=== Testing COM4 at multiple baud rates ===")

for baud in baud_rates:
    print(f"\nTrying {baud} baud...")
    try:
        ser = serial.Serial('COM4', baud, timeout=2)
        time.sleep(1)

        # Try to get any banner
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            print(f"  Spontaneous data: {repr(data)}")
            print(f"  Text: {data.decode('utf-8', errors='ignore')}")
        else:
            # Send Ctrl+C multiple times
            for _ in range(3):
                ser.write(b'\x03')
                time.sleep(0.2)

            # Send Enter
            ser.write(b'\r\n')
            time.sleep(0.5)

            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                print(f"  Response: {repr(data)}")
                print(f"  Text: {data.decode('utf-8', errors='ignore')}")
            else:
                print(f"  No response")

        ser.close()
    except Exception as e:
        print(f"  Error: {e}")

print("\nDone")

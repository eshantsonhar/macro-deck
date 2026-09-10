import serial
import time

baud_rates = [9600, 115200, 57600, 38400, 19200]

print("=== Testing COM4 at different baud rates ===")

for baud in baud_rates:
    print(f"\nTrying {baud} baud...")
    try:
        ser = serial.Serial('COM4', baud, timeout=1)
        time.sleep(0.5)

        # Send Ctrl+C
        ser.write(b'\x03')
        time.sleep(0.3)

        # Send Enter
        ser.write(b'\r\n')
        time.sleep(0.3)

        # Read response
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            print(f"  Received {len(data)} bytes: {repr(data)}")
            if data:
                print(f"  Text: {data.decode('utf-8', errors='ignore')}")
        else:
            print(f"  No response")

        ser.close()
    except Exception as e:
        print(f"  Error: {e}")

print("\nDone")

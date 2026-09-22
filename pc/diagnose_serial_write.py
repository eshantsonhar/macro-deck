"""
Diagnostic to test bounded serial write to COM4
"""

import serial
import time
import traceback

print("=== SERIAL WRITE DIAGNOSTIC ===")
print()

try:
    print("[TEST] BEFORE Serial()", flush=True)
    ser = serial.Serial("COM4", 115200, timeout=1, write_timeout=2)
    print("[TEST] AFTER Serial()", flush=True)

    # Test 1: TRACK message
    print("\n=== TEST 1: TRACK MESSAGE ===", flush=True)
    payload = b"TRACK|No Track|Playing|\n"
    print(f"[TEST] BEFORE write", flush=True)
    print(f"[TEST] payload length: {len(payload)}", flush=True)
    print(f"[TEST] payload repr: {repr(payload)}", flush=True)

    try:
        ser.write(payload)
        print("[TEST] AFTER write - TRACK message succeeded", flush=True)
    except Exception as exc:
        print(f"[TEST] WRITE ERROR: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()

    time.sleep(0.5)

    # Test 2: One byte
    print("\n=== TEST 2: ONE BYTE ===", flush=True)
    payload = b"\n"
    print(f"[TEST] BEFORE write", flush=True)
    print(f"[TEST] payload length: {len(payload)}", flush=True)
    print(f"[TEST] payload repr: {repr(payload)}", flush=True)

    try:
        ser.write(payload)
        print("[TEST] AFTER write - one byte succeeded", flush=True)
    except Exception as exc:
        print(f"[TEST] WRITE ERROR: {type(exc).__name__}: {exc}", flush=True)
        traceback.print_exc()

    ser.close()
    print("\n[TEST] Serial closed", flush=True)

except Exception as exc:
    print(f"[TEST] ERROR: {type(exc).__name__}: {exc}", flush=True)
    traceback.print_exc()

print("\n=== DIAGNOSTIC COMPLETE ===")

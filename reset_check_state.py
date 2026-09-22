import subprocess
import time
from subprocess import TimeoutExpired

print("=== RESET + STATE CHECK ===")
print()

# Reset
print("1. Hard reset...")
result = subprocess.run(
    ["py", "-m", "mpremote", "connect", "COM4", "reset"],
    capture_output=True,
    text=True
)
print(f"   Reset: {result.stdout if result.stdout else 'OK'}")

# Wait
print("2. Waiting 1 second...")
time.sleep(1)

# Check if we can execute a command immediately
print("3. Testing REPL availability...")
try:
    result = subprocess.run(
        ["py", "-m", "mpremote", "connect", "COM4", "exec", "print('POST_RESET_TEST')"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"   Result: {result.stdout}")
    print(f"   Stderr: {result.stderr if result.stderr else 'None'}")
except TimeoutExpired:
    print("   TIMEOUT - REPL not responsive")

# Check globals
print("4. Checking globals...")
try:
    result = subprocess.run(
        ["py", "-m", "mpremote", "connect", "COM4", "exec", "print('DT in globals:', 'DT' in globals())"],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"   Result: {result.stdout}")
except TimeoutExpired:
    print("   TIMEOUT - REPL not responsive")

print("\n=== COMPLETE ===")

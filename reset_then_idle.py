import subprocess
import time
from subprocess import TimeoutExpired

print("=== HARD RESET + WAIT + PROBE ===")
print()

# Reset
print("1. Hard reset...")
subprocess.run(
    ["py", "-m", "mpremote", "connect", "COM4", "reset"],
    capture_output=True
)

# Wait 5 seconds to allow main.py to start
print("2. Waiting 5 seconds for main.py to start...")
time.sleep(5)

# Try to execute a command - if main.py is running, this should fail or timeout
print("3. Attempting to execute command (will fail if main.py is running)...")
try:
    result = subprocess.run(
        ["py", "-m", "mpremote", "connect", "COM4", "exec", "print('TEST')"],
        capture_output=True,
        text=True,
        timeout=3
    )
    print(f"   Command succeeded: {result.stdout}")
    print("   => REPL is available, main.py is NOT running")
except TimeoutExpired:
    print("   Command timed out")
    print("   => main.py may be running and blocking REPL access")

print("\n=== COMPLETE ===")

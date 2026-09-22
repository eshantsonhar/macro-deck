"""
Test if the actual SMTC call can fail or hang
"""

import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from combined_bridge import get_media_from_smtc

print("=== Testing SMTC Call with Timing ===")
print()

for i in range(5):
    start = time.time()
    print(f"Call {i+1} starting at {start:.1f}s")
    
    try:
        track, artist, app_name = get_media_from_smtc()
        elapsed = time.time() - start
        print(f"  Result: track={repr(track)}, artist={repr(artist)}, app={repr(app_name)}")
        print(f"  Time: {elapsed:.3f}s")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ERROR: {type(e).__name__}: {e}")
        print(f"  Time: {elapsed:.3f}s")
    
    print()

print("=== Test Complete ===")

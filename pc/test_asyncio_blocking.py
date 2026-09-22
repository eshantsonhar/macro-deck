"""
Test if asyncio.run() blocks or causes issues in a loop
"""

import asyncio
import time

async def get_media():
    await asyncio.sleep(0.1)
    return "Track", "Artist", "App"

def get_sync():
    return asyncio.run(get_media())

print("Testing asyncio.run() in a loop...")
print()

start = time.time()
for i in range(5):
    print(f"Iteration {i+1} at {time.time() - start:.1f}s")
    result = get_sync()
    print(f"  Result: {result}")
    time.sleep(0.5)

print(f"Total time: {time.time() - start:.1f}s")
print()
print("If asyncio.run() works correctly, each iteration should take ~0.6s")

"""
Test if asyncio.run() can be called multiple times
"""

import asyncio

async def simple_async():
    await asyncio.sleep(0.1)
    return "result"

def call_once():
    return asyncio.run(simple_async())

print("Test 1: First call")
result1 = call_once()
print(f"Result: {result1}")

print("\nTest 2: Second call")
result2 = call_once()
print(f"Result: {result2}")

print("\nTest 3: Third call")
result3 = call_once()
print(f"Result: {result3}")

print("\nAll tests passed")

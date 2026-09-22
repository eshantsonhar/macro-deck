"""
ABI verification script - does NOT call SendInput
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from volume_controller import (
    KEYBDINPUT, MOUSEINPUT, HARDWAREINPUT,
    INPUT_UNION, INPUT, ULONG_PTR
)

print("=== ABI Verification ===")
print()

print("ULONG_PTR type:", ULONG_PTR)
print("sizeof(ctypes.c_void_p):", __import__('ctypes').sizeof(__import__('ctypes').c_void_p))
print()

print("KEYBDINPUT:")
print("  sizeof:", __import__('ctypes').sizeof(KEYBDINPUT))
print("  wVk.offset:", KEYBDINPUT.wVk.offset)
print("  wScan.offset:", KEYBDINPUT.wScan.offset)
print("  dwFlags.offset:", KEYBDINPUT.dwFlags.offset)
print("  time.offset:", KEYBDINPUT.time.offset)
print("  dwExtraInfo.offset:", KEYBDINPUT.dwExtraInfo.offset)
print()

print("MOUSEINPUT:")
print("  sizeof:", __import__('ctypes').sizeof(MOUSEINPUT))
print()

print("HARDWAREINPUT:")
print("  sizeof:", __import__('ctypes').sizeof(HARDWAREINPUT))
print()

print("INPUT_UNION:")
print("  sizeof:", __import__('ctypes').sizeof(INPUT_UNION))
print("  ki.offset:", INPUT_UNION.ki.offset)
print("  mi.offset:", INPUT_UNION.mi.offset)
print("  hi.offset:", INPUT_UNION.hi.offset)
print()

print("INPUT:")
print("  sizeof:", __import__('ctypes').sizeof(INPUT))
print("  type.offset:", INPUT.type.offset)
print("  u.offset:", INPUT.u.offset)
print()

print("=== Layout Checks ===")
ctypes = __import__('ctypes')

print("sizeof(INPUT_UNION) == sizeof(KEYBDINPUT):", ctypes.sizeof(INPUT_UNION) == ctypes.sizeof(KEYBDINPUT))
print("sizeof(INPUT) == INPUT.u.offset + sizeof(INPUT_UNION):", ctypes.sizeof(INPUT) == INPUT.u.offset + ctypes.sizeof(INPUT_UNION))
print()

print("=== dwExtraInfo Type ===")
print("KEYBDINPUT.dwExtraInfo type:", KEYBDINPUT.dwExtraInfo)
print("ULONG_PTR defined as:", ULONG_PTR)
print("sizeof(ULONG_PTR):", ctypes.sizeof(ULONG_PTR))
print("sizeof(ctypes.c_void_p):", ctypes.sizeof(ctypes.c_void_p))
print("Are they the same size:", ctypes.sizeof(ULONG_PTR) == ctypes.sizeof(ctypes.c_void_p))

"""
Run structure validation only - no volume events sent
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from volume_controller import validate_structures

print("Running structure validation (non-destructive)...")
print()
validate_structures()
